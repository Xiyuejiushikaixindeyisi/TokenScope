"""Manual diagnostic HTTP boundary. All GET handlers read sealed output only."""

from typing import Any, Literal

from fastapi import APIRouter, Depends, Header
from pydantic import ValidationError

from tokenscope.analysis_common.contracts import Contract, DiagnosticRequest, JsonText, Name
from tokenscope.analysis_common.runtime import RuntimeOptions
from tokenscope.analysis_common.service import DiagnosticService
from tokenscope.analysis_common.wire import from_wire, to_wire, wire_schema
from tokenscope.errors import TokenScopeError


class Submission(Contract):
    request: DiagnosticRequest
    options: RuntimeOptions


class Retry(Contract):
    submission_key: Name


class TokenEvaluation(Contract):
    fragment_id: Name
    candidate_id: Name
    parameters_json: JsonText
    business_basis_ref: str | None = None
    submission_key: Name


class LowHitEvaluation(Contract):
    finding_ids: tuple[Name, ...]
    submission_key: Name


class PlanReference(Contract):
    task_id: Name
    plan_id: Name


class Combination(Contract):
    plan_refs: tuple[PlanReference, ...]
    submission_key: Name


class Authorization(Contract):
    fragment_id: Name
    observation_id: Name
    selected_unit_id: Name
    handler_id: Literal["replace_payload_with_reference", "remove_authorized_duplicate_message"]
    handler_version: Name
    parameters_json: JsonText
    business_basis_ref: Name
    submission_key: Name


ItemKind = Literal[
    "authorization",
    "finding",
    "fragment",
    "fragment_index",
    "rule_coverage",
    "plan",
    "evaluation",
    "optimization",
    "experiment",
]


def router(service: DiagnosticService, instance_id: str) -> APIRouter:
    root = APIRouter(prefix="/diagnostics")

    def identity(x_tokenscope_service_instance: str = Header()) -> None:
        if x_tokenscope_service_instance != instance_id:
            raise TokenScopeError(
                "SERVICE_INSTANCE_MISMATCH", "Diagnostic service identity differs", 409
            )

    api = APIRouter(dependencies=[Depends(identity)])

    def parse(model: Any, payload: dict[str, Any]) -> Any:
        try:
            return from_wire(model, payload)
        except (ValueError, ValidationError) as exc:
            raise TokenScopeError("INVALID_ARGUMENT", "Invalid diagnostic input", 422) from exc

    @root.get("/capabilities")
    def capabilities() -> dict[str, Any]:
        return {
            "service_instance_id": instance_id,
            "contract_version": "analysis-common-1.0",
            "http_version": "diagnostics-http-1",
            "schemas": {
                "submission": wire_schema(Submission),
                "retry": wire_schema(Retry),
                "token_evaluation": wire_schema(TokenEvaluation),
                "low_hit_evaluation": wire_schema(LowHitEvaluation),
                "combination": wire_schema(Combination),
                "authorization": wire_schema(Authorization),
            },
        }

    @api.post("/tasks", status_code=202)
    def submit(payload: dict[str, Any]) -> dict[str, Any]:
        body = parse(Submission, payload)
        try:
            return to_wire(service.submit(body.request, body.options))
        except ValueError as exc:
            raise TokenScopeError("INVALID_ARGUMENT", "Invalid plugin options", 422) from exc

    @api.get("/tasks/{task_id}")
    def receipt(task_id: str) -> dict[str, Any]:
        return to_wire(service.receipt(task_id))

    @api.get("/tasks/{task_id}/report")
    def report(task_id: str) -> dict[str, Any]:
        return service.report(task_id)

    @api.get("/tasks/{task_id}/items/{kind}")
    def items(
        task_id: str,
        kind: ItemKind,
        offset: int = 0,
        limit: int = 100,
    ) -> dict[str, Any]:
        return {
            "items": service.items(task_id, kind, offset=offset, limit=limit),
            "offset": str(offset),
        }

    @api.get("/tasks/{task_id}/items/{kind}/{key}")
    def item(
        task_id: str,
        kind: ItemKind,
        key: str,
    ) -> dict[str, Any]:
        return service.item(task_id, kind, key)

    @api.get("/tasks/{task_id}/comparisons/{finding_id}")
    def comparison(task_id: str, finding_id: str) -> dict[str, Any]:
        return service.comparison(task_id, finding_id)

    @api.get("/tasks/{task_id}/requests/{fragment_id}")
    def request_body(task_id: str, fragment_id: str) -> dict[str, Any]:
        return service.request_body(task_id, fragment_id)

    @api.get("/tasks/{task_id}/evaluations/{evaluation_id}/rows")
    def evaluation_rows(
        task_id: str, evaluation_id: str, offset: int = 0, limit: int = 100
    ) -> dict[str, Any]:
        return {
            "items": service.evaluation_rows(task_id, evaluation_id, offset, limit),
            "offset": str(offset),
        }

    @api.post("/tasks/{task_id}/cancel")
    def cancel(task_id: str) -> dict[str, Any]:
        return to_wire(service.cancel(task_id))

    @api.post("/tasks/{task_id}/retry", status_code=202)
    def retry(task_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        body = parse(Retry, payload)
        return to_wire(service.retry(task_id, body.submission_key))

    @api.post("/tasks/{task_id}/token-evaluations", status_code=202)
    def token_evaluation(task_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        body = parse(TokenEvaluation, payload)
        return to_wire(
            service.submit_token_evaluation(
                task_id,
                body.fragment_id,
                body.candidate_id,
                body.parameters_json,
                body.business_basis_ref,
                body.submission_key,
            )
        )

    @api.post("/tasks/{task_id}/low-hit-evaluations", status_code=202)
    def low_hit_evaluation(task_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        body = parse(LowHitEvaluation, payload)
        return to_wire(
            service.submit_low_hit_evaluation(task_id, body.finding_ids, body.submission_key)
        )

    @api.post("/tasks/{task_id}/combination-evaluations", status_code=202)
    def combination(task_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        body = parse(Combination, payload)
        return to_wire(
            service.submit_combination(
                task_id, [p.model_dump() for p in body.plan_refs], body.submission_key
            )
        )

    @api.post("/tasks/{task_id}/token-authorizations", status_code=202)
    def authorization(task_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        body = parse(Authorization, payload)
        return to_wire(
            service.submit_token_authorization(
                task_id,
                body.fragment_id,
                body.model_dump(exclude={"fragment_id", "submission_key"}),
                body.submission_key,
            )
        )

    root.include_router(api)
    return root
