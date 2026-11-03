import json
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from test_diagnostic_tasks import options, setup

from tokenscope.analysis_common.execution_v2 import RequestV2, RuntimeV2, SelectionV2, SubmissionV2
from tokenscope.analysis_common.proposal_plugins import ProposalRegistry
from tokenscope.analysis_common.recommendation_runtime import RecommendationSettings
from tokenscope.analysis_common.recommendations import RecipeBundle
from tokenscope.analysis_common.service import DiagnosticService
from tokenscope.analysis_common.source import SourceResolver
from tokenscope.analysis_common.wire import to_wire
from tokenscope.api.app import create_app
from tokenscope.token_content.auto_proposals import TokenProposalAdapter


def configured(service, low=True, token=True, **kw):
    old, req = setup(service, low_hit=True)
    adapters = ProposalRegistry()
    adapters.register(TokenProposalAdapter())
    d = DiagnosticService(
        SourceResolver(service),
        old.registry,
        RecommendationSettings(adapters, RecipeBundle(bundle_id="empty", revision="1", recipes=())),
    )
    request = RequestV2(
        source=req.source,
        selection=SelectionV2(
            reason_codes=("low_hit",), enable_low_hit=low, enable_token_content=token
        ),
        submission_key="v2",
    )
    opts = options(candidate_limit=16, max_findings=5, max_encoding_calls=1000).model_dump()
    opts.update(version="diagnostics-runtime-2", **kw)
    return d, request, RuntimeV2(**opts)


def bomb(*a, **kw):
    raise AssertionError("Disabled direction was called")


def test_low_only_never_resolves_plugin_adapter_or_recipe(service):
    d, req, opts = configured(service, token=False)
    with (
        patch.object(d.registry, "get", bomb),
        patch.object(d.recommendations.registry, "get", bomb),
    ):
        receipt = d.submit(req, opts)
        result = d.process_next()
    assert result.status in ("ready", "partial")
    report = d.report(receipt.task_id)
    assert report["selected_directions"] == ["low_hit"]
    assert all(s["direction"] == "low_hit" for s in report["stages"])
    assert d.items(receipt.task_id, "fragment") == []
    assert d.items(receipt.task_id, "difference_group")
    assert (
        "TOKEN_DIRECTION_DISABLED"
        in d.items(receipt.task_id, "recommendation_summary")[0]["data"]["reason_codes"]
    )
    assert d.retry(receipt.task_id, "retry").status == "queued"
    assert (
        json.loads(d.store.row(receipt.task_id)["intent"])["request"]["selection"][
            "enable_token_content"
        ]
        is False
    )


def test_token_only_empty_recipe_never_proposes_or_low_hit(service):
    d, req, opts = configured(service, low=False)
    with patch.object(d, "_low_hit", bomb), patch.object(TokenProposalAdapter, "propose", bomb):
        receipt = d.submit(req, opts)
        result = d.process_next()
    assert result.status == "ready"
    assert len(d.items(receipt.task_id, "fragment")) == 6
    report = d.report(receipt.task_id)
    assert report["selected_directions"] == ["token_content"]
    summary = d.items(receipt.task_id, "recommendation_summary")[0]["data"]
    assert summary["proposal_coverage"]["checked"] == "0"
    assert summary["proposal_coverage"]["eligible"] == "0"
    assert summary["reason_codes"] == ["NO_CONFIGURED_RECIPES"]


def test_retention_truncation_does_not_stop_following_direction(service):
    d, req, opts = configured(service)
    receipt = d.submit(req, opts)
    result = d.process_next()
    assert result.status == "partial"
    report = d.report(receipt.task_id)
    low, token = report["stages"][:2]
    assert low["checked_requests"] == "6" and low["scan_complete"]
    assert low["comparison_complete"] and not low["retention_complete"]
    assert "FINDING_RETENTION_TRUNCATED" in low["reason_codes"]
    assert token["checked_requests"] == "6" and token["fragments_complete"]
    assert len(d.items(receipt.task_id, "finding")) <= 5
    assert len(d.items(receipt.task_id, "fragment")) == 6
    assert report["telemetry"]["clock"] == "perf_counter_ns"
    assert int(report["telemetry"]["elapsed_ns"]["source_preflight"]) > 0


def test_real_comparison_budget_is_partial_not_retention(service):
    d, req, opts = configured(service, max_comparisons=1)
    receipt = d.submit(req, opts)
    assert d.process_next().status == "partial"
    low = d.report(receipt.task_id)["stages"][0]
    assert "COMPARISON_COUNT_BUDGET_EXHAUSTED" in low["reason_codes"]
    assert not low["comparison_complete"]
    assert d.report(receipt.task_id)["stages"][1]["checked_requests"] == "6"


def test_fragment_retention_does_not_falsify_fragment_scan(service):
    d, req, opts = configured(service, low=False, max_fragment_bytes=1)
    receipt = d.submit(req, opts)
    assert d.process_next().status == "partial"
    token = d.report(receipt.task_id)["stages"][0]
    assert token["checked_requests"] == "6" and token["fragments_complete"]
    assert not token["retention_complete"] and token["retained_requests"] == "0"
    assert d.items(receipt.task_id, "fragment") == []


def test_v2_http_and_readonly_legacy(service, tmp_path):
    d, req, opts = configured(service, token=False)
    app = create_app(service, start_worker=False)
    with TestClient(app) as client:
        cap = client.get("/diagnostics/v2/capabilities").json()
        client.headers["x-tokenscope-service-instance"] = cap["service_instance_id"]
        response = client.post(
            "/diagnostics/v2/tasks", json=to_wire(SubmissionV2(request=req, options=opts))
        )
        assert response.status_code == 202, response.text
        task = response.json()["task_id"]
        assert client.app.state.diagnostics.process_next().status == "partial"
        with (
            patch.object(DiagnosticService, "submit", bomb),
            patch.object(DiagnosticService, "process_next", bomb),
        ):
            catalog = client.get("/diagnostics/v2/catalog").json()
            assert not catalog["defaults"] and catalog["selected_reports"][0]["task_id"] == task
            assert (
                client.get("/diagnostics/v2/tasks/" + task + "/execution").json()["availability"]
                == "computed"
            )
            assert client.get("/diagnostics/tasks/" + task + "/report").status_code == 200
        assert (
            client.get(
                "/diagnostics/v2/catalog", headers={"x-tokenscope-service-instance": "wrong"}
            ).status_code
            == 409
        )
        assert client.get("/diagnostics/v2/catalog?limit=101").status_code == 422
        import hashlib

        from tokenscope.analysis_common.execution_v2 import CatalogV2, ExecutionViewV2
        from tokenscope.analysis_common.wire import from_wire

        execution = client.get("/diagnostics/v2/tasks/" + task + "/execution").json()
        from_wire(CatalogV2, catalog)
        from_wire(ExecutionViewV2, execution)

        def routes(items):
            for route in items:
                if hasattr(route, "original_router"):
                    yield from routes(route.original_router.routes)
                else:
                    yield route

        assert sum(getattr(route, "path", None) == "/v2/tasks" for route in routes(app.routes)) == 1
        before = {
            str(p): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in app.state.diagnostics.store.root.rglob("*")
            if p.is_file()
        }
        with (
            patch.object(DiagnosticService, "submit", bomb),
            patch.object(DiagnosticService, "process_next", bomb),
        ):
            assert client.get("/diagnostics/v2/catalog").json() == catalog
            assert client.get("/diagnostics/v2/tasks/" + task + "/execution").json() == execution
        assert before == {
            str(p): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in app.state.diagnostics.store.root.rglob("*")
            if p.is_file()
        }
        (tmp_path / "v2-actual.json").write_text(
            json.dumps(
                {
                    "submission": to_wire(SubmissionV2(request=req, options=opts)),
                    "catalog": catalog,
                    "execution": execution,
                },
                ensure_ascii=False,
                indent=2,
            )
        )


@pytest.mark.parametrize("empty", [True, False])
def test_incomplete_fragment_independent_of_recipe_absence(service, empty):
    from test_recommendation_engine import configured as with_recipe

    d, req = with_recipe(service)
    if empty:
        d.recommendations.bundle = RecipeBundle(bundle_id="none", revision="1", recipes=())
    request = RequestV2(**req.model_dump())
    opts = options(candidate_limit=16).model_dump()
    opts["version"] = "diagnostics-runtime-2"
    opts["token_selection"]["budget"]["max_units"] = 1
    receipt = d.submit(request, RuntimeV2(**opts))
    assert d.process_next().status == "partial"
    report = d.report(receipt.task_id)
    assert not report["stages"][0]["fragments_complete"]
    summary = d.items(receipt.task_id, "recommendation_summary")[0]["data"]
    if empty:
        assert summary["reason_codes"] == ["NO_CONFIGURED_RECIPES"]
        assert summary["proposal_coverage"]["eligible"] == "0"
    else:
        assert "TOKEN_FRAGMENT_INCOMPLETE" in summary["reason_codes"]
        assert "NO_CONFIGURED_RECIPES" not in summary["reason_codes"]


def test_v2_idempotency_conflict_and_disabled_retry_recovery(service):
    from tokenscope.errors import TokenScopeError

    d, req, opts = configured(service, token=False)
    first = d.submit(req, opts)
    assert d.submit(req, opts).task_id == first.task_id
    changed = req.model_copy(
        update={
            "selection": SelectionV2(
                reason_codes=("low_hit",), enable_low_hit=False, enable_token_content=True
            )
        }
    )
    with pytest.raises(TokenScopeError, match="Submission intent"):
        d.submit(changed, opts)
    assert d.store.claim_next() == first.task_id
    d.store.recover()
    assert d.receipt(first.task_id).status == "interrupted"
    retried = d.retry(first.task_id, "after-recovery")
    with (
        patch.object(d.registry, "get", bomb),
        patch.object(d.recommendations.registry, "get", bomb),
    ):
        assert d.process_next().status == "partial"
    assert d.report(retried.task_id)["selected_directions"] == ["low_hit"]


def test_plugin_failure_is_not_fragment_incomplete(service):
    d, req, opts = configured(service, low=False)
    receipt = d.submit(req, opts)
    plugin = d.registry.get("token_content")
    with patch.object(type(plugin), "analyze_request", side_effect=ValueError("synthetic failure")):
        assert d.process_next().status == "partial"
    stage = d.report(receipt.task_id)["stages"][0]
    assert stage["reason"] == "TOKEN_PLUGIN_FAILED"
    assert "TOKEN_FRAGMENT_INCOMPLETE" not in stage["reason_codes"]
    assert stage["checked_requests"] == "0" and not stage["scan_complete"]


def test_legacy_execution_uncomputed_and_invalid_v2_selection(service):
    d, req = setup(service, low_hit=False)
    receipt = d.submit(req, options())
    assert d.process_next().status == "ready"
    app = create_app(service, start_worker=False)
    with TestClient(app) as client:
        cap = client.get("/diagnostics/v2/capabilities").json()
        client.headers["x-tokenscope-service-instance"] = cap["service_instance_id"]
        view = client.get("/diagnostics/v2/tasks/" + receipt.task_id + "/execution").json()
        from tokenscope.analysis_common.execution_v2 import ExecutionViewV2
        from tokenscope.analysis_common.wire import from_wire

        from_wire(ExecutionViewV2, view)
        assert view["availability"] == "not_computed" and view["telemetry"] is None
        _, req2, opts = configured(service)
        payload = to_wire(SubmissionV2(request=req2, options=opts))
        payload["request"]["selection"].update(enable_low_hit=False, enable_token_content=False)
        assert client.post("/diagnostics/v2/tasks", json=payload).status_code == 422
        payload["request"]["selection"]["enable_token_content"] = True
        payload["options"]["token_selection"]["rule_ids"] = ["unknown"]
        assert client.post("/diagnostics/v2/tasks", json=payload).status_code == 422


def test_empty_execution_uses_published_terminal_status(service):
    d, req, opts = configured(service, low=False)
    req = req.model_copy(update={"source": req.source.model_copy(update={"appid": "absent"})})
    receipt = d.submit(req, opts)
    assert d.process_next().status == "empty"
    app = create_app(service, start_worker=False)
    with TestClient(app) as client:
        cap = client.get("/diagnostics/v2/capabilities").json()
        client.headers["x-tokenscope-service-instance"] = cap["service_instance_id"]
        response = client.get("/diagnostics/v2/tasks/" + receipt.task_id + "/execution")
        assert response.status_code == 200
        assert response.json()["status"] == "empty"
        assert client.get("/diagnostics/v2/catalog").json()["selected_reports"] == []


def test_disabled_token_ignores_unreadable_recipe_file(service, tmp_path):
    d, req, opts = configured(service, token=False)
    d.recommendations.bundle = tmp_path / "not-present.json"
    with (
        patch.object(d.registry, "get", bomb),
        patch.object(d.recommendations.registry, "get", bomb),
    ):
        receipt = d.submit(req, opts)
        assert d.process_next().status == "partial"
    assert d.report(receipt.task_id)["selected_directions"] == ["low_hit"]
