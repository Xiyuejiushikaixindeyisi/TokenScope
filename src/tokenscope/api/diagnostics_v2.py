"""Additive explicit-direction endpoints; attach alongside diagnostics v1."""

from typing import Any

from fastapi import APIRouter, Depends, Header

from tokenscope.analysis_common.discovery_v2 import DiscoveryV2
from tokenscope.analysis_common.execution_v2 import CatalogV2, ExecutionViewV2, SubmissionV2
from tokenscope.analysis_common.service import DiagnosticService
from tokenscope.analysis_common.wire import from_wire, to_wire, wire_schema
from tokenscope.errors import TokenScopeError


def router(
    service: DiagnosticService, instance_id: str, *, legacy_execution: bool = True
) -> APIRouter:
    root = APIRouter(prefix="/diagnostics")

    def identity(x_tokenscope_service_instance: str = Header()) -> None:
        if x_tokenscope_service_instance != instance_id:
            raise TokenScopeError("SERVICE_INSTANCE_MISMATCH", "Diagnostic instance differs", 409)

    api = APIRouter(dependencies=[Depends(identity)])

    def parse(model: Any, payload: dict[str, Any]) -> Any:
        try:
            return from_wire(model, payload)
        except ValueError as exc:
            raise TokenScopeError("INVALID_ARGUMENT", "Invalid diagnostic v2 input", 422) from exc

    @root.get("/v2/capabilities")
    def capabilities_v2() -> dict[str, Any]:
        return {
            "service_instance_id": instance_id,
            "version": "diagnostics-execution-2",
            "directions": ["low_hit", "token_content"] if legacy_execution else [],
            "execution_enabled": legacy_execution,
            "minimum_selected_directions": "1",
            "submission_url": "/diagnostics/v2/tasks",
            "catalog_url": "/diagnostics/v2/catalog",
            "discovery_version": "diagnostics-discovery-2",
            "legacy_read_compatible": True,
            "schemas": {
                "submission": wire_schema(SubmissionV2),
                "catalog": wire_schema(CatalogV2),
                "execution": wire_schema(ExecutionViewV2),
            },
            "budget_semantics": "direction_isolated_compute_rule_reserved_retention",
            "partial_policy": "ready_preferred_published_partial_fallback",
        }

    @api.post("/v2/tasks", status_code=202)
    def submit_v2(payload: dict[str, Any]) -> dict[str, Any]:
        body = parse(SubmissionV2, payload)
        try:
            return to_wire(service.submit(body.request, body.options))
        except ValueError as exc:
            raise TokenScopeError(
                "INVALID_ARGUMENT", "Invalid diagnostic v2 selection", 422
            ) from exc

    @api.get("/v2/catalog")
    def catalog_v2(
        snapshot: str | None = None, after: str = "0", limit: int = 50
    ) -> dict[str, Any]:
        return DiscoveryV2(service.store, instance_id).catalog_v2(snapshot, after, limit)

    @api.get("/v2/tasks/{task_id}/execution")
    def execution_v2(task_id: str) -> dict[str, Any]:
        report = service.report(task_id)
        return {
            "version": "diagnostics-execution-2",
            "task_id": task_id,
            "scope_id": report["scope_id"],
            "status": service.receipt(task_id).status,
            "availability": "computed" if "telemetry" in report else "not_computed",
            "selected_directions": report.get("selected_directions"),
            "stages": report.get("stages", []),
            "telemetry": report.get("telemetry"),
        }

    root.include_router(api)
    return root
