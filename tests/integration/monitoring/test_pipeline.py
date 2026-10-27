import json

import pytest
from conftest import csv_bytes, valid_row
from fastapi.testclient import TestClient

from tokenscope.api.app import create_app
from tokenscope.domain import DEFAULT_SETTINGS, RunSubmission, SettingsUpdate
from tokenscope.errors import TokenScopeError
from tokenscope.monitoring.pipeline import verify_seal
from tokenscope.monitoring.rules import RuleUpdate


def prepare(service, model="GLM-5.2"):
    raw = json.dumps(
        {
            "messages": [{"role": "user", "content": "prefix shared " * 4000}],
            "enable_thinking": False,
        },
        ensure_ascii=False,
    )
    rows = [
        valid_row(
            hash_id="dup",
            appid=tenant,
            request_input=raw,
            model_handle_start_time=f"2026-10-27T00:00:0{second}Z",
        )
        for tenant, second in [("a", 2), ("b", 1), ("a", 1), ("a", 3)]
    ]
    rows.append(valid_row(completion_tokens="invalid"))
    (service.inputs.root / "sample.csv").write_bytes(csv_bytes(rows))
    return service.submit(RunSubmission(file_ref="sample.csv", model_id=model))


@pytest.mark.parametrize("model", list(DEFAULT_SETTINGS))
def test_complete_real_encoding_pipeline_and_readonly_api(service, model):
    run = prepare(service, model)
    client = TestClient(create_app(service, start_worker=False))
    assert client.get(f"/analysis-runs/{run.run_id}/metrics").status_code == 409
    completed = service.processor.process_next()
    assert completed.status == "completed", completed
    result = service.control.result(run.run_id)
    assert result["quality"] == dict(
        records_read=5, valid_requests=4, skipped_rows=1, duplicate_hash_id_rows=3
    )
    groups = service.metrics(run.run_id)["groups"]
    assert len(groups) == 2
    assert groups[0]["totals"]["ideal_cached_input_tokens"] > 0
    assert groups[1]["totals"]["ideal_cached_input_tokens"] == 0
    with service.result_db(run.run_id) as db:
        facts = {r["source_record_index"]: dict(r) for r in db.execute("SELECT * FROM facts")}
    assert facts[3]["ideal_cached_input_tokens"] == 0
    assert facts[1]["ideal_cached_input_tokens"] > 0
    for group in groups:
        totals = group["totals"]
        assert (
            totals["prompt_tokens"]
            == totals["ideal_cached_input_tokens"] + totals["ideal_compute_input_tokens"]
        )
        assert (
            group["ideal_hit_rate"] == totals["ideal_cached_input_tokens"] / totals["prompt_tokens"]
        )
        assert group["threshold_states"] == [{"status": "unconfigured"}]
        hist = service.histograms(run.run_id, group["appid"])
        assert all(
            sum(b["count"] for b in h["bins"]) == group["request_count"]
            for h in hist["metrics"].values()
        )
    ids = service.explain_encoding(run.run_id, 1)["ids"]
    assert len(ids) == facts[1]["prompt_tokens"]
    directory = service.state_root / "runs" / run.run_id
    before = {str(p): p.stat().st_mtime_ns for p in directory.rglob("*") if p.is_file()}
    for suffix in ["metrics", "length-histograms?appid=a", "lengths?appid=a&limit=1", "signals"]:
        assert client.get(f"/analysis-runs/{run.run_id}/{suffix}").status_code == 200
    assert before == {str(p): p.stat().st_mtime_ns for p in directory.rglob("*") if p.is_file()}
    assert len(service.lengths(run.run_id, "a", limit=1)["points"]) == 1
    assert service.lengths(run.run_id, "a", lower=200000)["total"] == 0
    assert verify_seal(directory, run.run_id)["summary"]["quality"] == result["quality"]


def test_rules_outbox_idempotence_and_cached_settings(service):
    run = prepare(service)
    service.processor.process_next()
    signature = service.control.result(run.run_id)["measurement_signatures"]["request_count"]
    service.control.update_rule(
        RuleUpdate(
            appid="a",
            model_id="GLM-5.2",
            rule_id="count",
            expected_revision=0,
            metric="request_count",
            comparator="gt",
            threshold=0,
            measurement_signature=signature,
        )
    )
    repeated = []
    for _ in range(2):
        item = service.submit(RunSubmission(file_ref="sample.csv", model_id="GLM-5.2"))
        service.processor.process_next()
        repeated.append(service.control.signals(item.run_id))
    assert repeated[0] == repeated[1]
    assert repeated[0][0]["status"] == "pending_consumer"
    with service.control.connect() as db:
        assert db.execute("SELECT count(*) FROM outbox").fetchone()[0] == 1
    queued = service.submit(RunSubmission(file_ref="sample.csv", model_id="GLM-5.2"))
    service.update_settings(
        "GLM-5.2", SettingsUpdate(expected_revision=1, changes={"prefix_cache_enabled": False})
    )
    service.processor.process_next()
    assert service.control.run(queued.run_id).settings.revision == 2
    assert service.metrics(queued.run_id)["groups"][0]["totals"]["ideal_cached_input_tokens"] == 0
    assert service.control.run(run.run_id).settings.revision == 1


def test_pending_deepseek_no_valid_and_interrupted(service):
    raw = json.dumps({"messages": [{"role": "user", "content": "pending"}]})
    (service.inputs.root / "pending.csv").write_bytes(csv_bytes([valid_row(request_input=raw)]))
    run = service.submit(RunSubmission(file_ref="pending.csv", model_id="DeepSeek-V4-Flash-0731"))
    service.processor.process_next()
    assert service.control.run(run.run_id).error_code == "ENCODING_DEFAULT_UNRESOLVED"
    with pytest.raises(TokenScopeError):
        service.metrics(run.run_id)
    (service.inputs.root / "empty.csv").write_bytes(csv_bytes([valid_row(completion_tokens="bad")]))
    run = service.submit(RunSubmission(file_ref="empty.csv", model_id="GLM-5.2"))
    assert service.processor.process_next().status == "no_valid_rows"
    assert service.metrics(run.run_id)["groups"] == []
    run = service.submit(RunSubmission(file_ref="empty.csv", model_id="GLM-5.2"))
    service.control.claim_next()
    service.processor.process_next()
    assert service.control.run(run.run_id).status == "interrupted"


def test_sealed_transaction_failure_recovers(service, monkeypatch):
    run = prepare(service)
    original = service.control.complete

    def fail(*args):
        raise OSError("injected after seal")

    monkeypatch.setattr(service.control, "complete", fail)
    assert service.processor.process_next().status == "running"
    with pytest.raises(TokenScopeError):
        service.metrics(run.run_id)
    monkeypatch.setattr(service.control, "complete", original)
    assert service.processor.process_next() is None
    assert service.control.run(run.run_id).status == "completed"
    assert service.metrics(run.run_id)["total_groups"] == 2
