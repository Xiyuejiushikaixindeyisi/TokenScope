import importlib.util
from pathlib import Path

import pytest

from tokenscope.domain import RunSubmission


def fixtures():
    spec = importlib.util.spec_from_file_location(
        "fixtures", Path("scripts/validation/v3_repair_fixtures.py")
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize("group_index", range(5))
def test_long_business_fixture_encodes_with_actual_model(service, group_index):
    module = fixtures()
    manifest = module.generate(service.inputs.root / "synthetic")
    group = manifest["groups"][group_index]
    run = service.submit(
        RunSubmission(file_ref="synthetic/" + group["file"], model_id=group["model"])
    )
    result = service.processor.process_next()
    assert result.status == "completed", result
    from tokenscope.analysis_common.contracts import SourceSelection
    from tokenscope.analysis_common.source import SourceResolver
    from tokenscope.user_monitoring.service import UserRunService

    source = SourceResolver(service, UserRunService(service)).resolve_scope(
        SourceSelection(source_kind="base", base_run_id=run.run_id, appid=group["appid"])
    )
    requests = list(source.iter_requests())
    assert len(requests) == group["count"]
    assert all(r.baseline_metrics.p > 1000 for r in requests)
    assert all(r.encoder_identity == source.scope.source.encoder_identity for r in requests)


@pytest.mark.parametrize("group_index", range(5))
def test_five_long_groups_automatic_sample_clock_replay(service, group_index):
    import json
    from fractions import Fraction

    from tokenscope.analysis_common.contracts import SourceSelection
    from tokenscope.analysis_common.contracts_v3 import PreparationRequest3
    from tokenscope.analysis_common.service_v3 import PreparationService
    from tokenscope.user_monitoring.service import UserRunService

    module = fixtures()
    group = module.generate(service.inputs.root / "synthetic")["groups"][group_index]
    run = service.submit(
        RunSubmission(file_ref="synthetic/" + group["file"], model_id=group["model"])
    )
    assert service.processor.process_next().status == "completed"
    preparation = PreparationService(service, UserRunService(service))
    receipt = preparation.store.submit(
        PreparationRequest3(
            submission_key="synthetic",
            source=SourceSelection(
                source_kind="base", base_run_id=run.run_id, appid=group["appid"]
            ),
        )
    )
    assert preparation.process_next().state == "completed"
    task = preparation.diagnoses.submit(receipt.preparation_id, "synthetic-diagnosis")
    execution = preparation.process_next()
    report = preparation.diagnoses.report(task.task_id)
    assert execution.state == "completed", (execution, report["discovery"]["reason_codes"])
    assert report["discovery"]["complete"]
    assert len(report["sample"]["decision"]["windows"]) == 1
    assert len(report["sample"]["decision"]["windows"][0]["members"]) == group["count"]
    clock = [r for r in report["recommendations"] if r["finding"]["rule_version"] == "clock-3.1"]
    assert clock
    rules = {r["finding"]["rule_id"] for r in report["recommendations"]}
    if group_index != 3:
        assert "L3" in rules
    if group_index == 2:
        assert any(
            r["finding"]["rule_id"] == "L1" and r["finding"]["rule_version"] == "prefix-3.2"
            for r in report["recommendations"]
        )
    root = preparation.store.root / "jobs" / task.task_id
    for recommendation in report["recommendations"]:
        assert len(recommendation["windows"]) == 1
        window = recommendation["windows"][0]
        assert window["complete"], window
        rows = json.loads((root / window["rows_ref"]).read_text())
        for side in ("before", "after"):
            assert window[side]["p"] == window[side]["h"] + window[side]["c"]
            for metric in ("p", "h", "c"):
                assert window[side][metric] == sum(r[side][metric] for r in rows)
        before, after = window["before"], window["after"]
        expected = 100 * (Fraction(after["h"], after["p"]) - Fraction(before["h"], before["p"]))
        assert expected == Fraction(**window["improvement_pp"])
    assert not execution.forced_termination
    # Exactly one baseline encode per request, plus modified variants only.
    modified = sum(r["windows"][0]["modified"] for r in report["recommendations"])
    assert (
        execution.telemetry["telemetry"]["consumed"]["encoding_calls"] == group["count"] + modified
    )

    from tokenscope.analysis_common.contracts import ModificationPlan
    from tokenscope.analysis_common.modifications import apply_mutations
    from tokenscope.analysis_common.sample_source import open_sample_window
    from tokenscope.domain import ModelSettings

    prep_execution = preparation.store.execution(receipt.preparation_id)
    sample_path = (
        preparation.store.root
        / "jobs"
        / receipt.preparation_id
        / prep_execution.telemetry["manifest_path"]
    )
    sample = open_sample_window(
        service,
        sample_path.parent,
        preparation.store.receipt(receipt.preparation_id).manifest_sha256,
        "discovery",
        metadata_limit=8 * 1024 * 1024,
    )
    for rec in clock:
        plan = ModificationPlan.model_validate_json(
            (root / rec["windows"][0]["plan_ref"]).read_bytes()
        )
        for op in plan.operations:
            request = sample.read_request(op.target.location.request_key)
            raw, _ = apply_mutations(
                request, (op,), ModelSettings.model_validate_json(sample.scope.source.settings_json)
            )
            original, changed = json.loads(request.raw_body), json.loads(raw)
            old, new = original["messages"][0]["content"], changed["messages"][0]["content"]
            start = old.index("<session_clock>") + len("<session_clock>")
            end = old.index("</session_clock>")
            assert new == old[:start] + "NORMALIZED" + old[end:]
            changed["messages"][0]["content"] = old
            assert changed == original
        evidence = preparation.diagnoses.evidence(task.task_id, rec["finding"]["finding_id"])
        ex = evidence["examples"][0]
        assert ex["after"] is not None and ex["comparison"] is not None
        assert "NORMALIZED" in ex["after"]["excerpt"]
    from fastapi.testclient import TestClient

    from tokenscope.api.app import create_app

    client = TestClient(create_app(service, start_worker=False))
    instance = client.get("/diagnostics/v3/capabilities").json()["service_instance_id"]
    headers = {"x-tokenscope-service-instance": instance}
    owner = clock[0]["finding"]["finding_id"]
    url = f"/diagnostics/v3/tasks/{task.task_id}/evidence/{owner}"
    assert client.get(url, headers=headers).status_code == 200
    assert client.get(url, headers={"x-tokenscope-service-instance": "other"}).status_code == 409
    assert (
        client.get(
            f"/diagnostics/v3/tasks/{task.task_id}/evidence/unknown", headers=headers
        ).status_code
        == 404
    )
    assert preparation.process_next() is None
    # Damage only this test's new sealed evidence; it must never be served as valid.
    (root / report["evidence_refs"][owner]).write_text("corrupt")
    assert client.get(url, headers=headers).status_code in (404, 409)
