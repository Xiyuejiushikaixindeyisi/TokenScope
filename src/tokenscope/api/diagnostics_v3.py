"""V3 preparation registration. Execution is connected only after runtime gates."""

import json
from typing import Any

from fastapi import APIRouter, Depends, Header, Query
from pydantic import BaseModel, ConfigDict, Field

from tokenscope.analysis_common.contracts_v3 import (
    PreparationReceipt3,
    PreparationRequest3,
    SampleManifest3,
)
from tokenscope.analysis_common.diagnostic_store_v3 import DiagnosticStore3
from tokenscope.analysis_common.execution_v3 import Execution3
from tokenscope.analysis_common.preparation_store import PreparationStore
from tokenscope.analysis_common.report_v3 import SampleReport3
from tokenscope.analysis_common.wire_v3 import from_wire, to_wire, wire_schema
from tokenscope.errors import TokenScopeError


class Retry3(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    submission_key: str = Field(min_length=1, max_length=128)


class DiagnosisRequest3(Retry3):
    preparation_id: str = Field(pattern=r"^prep-[0-9a-f]{32}$")


def router(
    store: PreparationStore, instance_id: str, *, preparation_enabled: bool = False
) -> APIRouter:
    diagnoses = DiagnosticStore3(store)
    root = APIRouter(prefix="/diagnostics/v3")

    def identity(x_tokenscope_service_instance: str = Header()) -> None:
        if x_tokenscope_service_instance != instance_id:
            raise TokenScopeError("SERVICE_INSTANCE_MISMATCH", "Diagnostic instance differs", 409)

    api = APIRouter(dependencies=[Depends(identity)])

    @root.get("/capabilities")
    def capabilities() -> dict[str, Any]:
        return {
            "version": "diagnostics-sampling-3",
            "service_instance_id": instance_id,
            "directions": ["low_hit"],
            "discovery_mode": "automatic",
            "execution_enabled": preparation_enabled,
            "preparation_enabled": preparation_enabled,
            "submission_url": "/diagnostics/v3/source-preparations",
            "schemas": {
                "request": wire_schema(PreparationRequest3),
                "receipt": wire_schema(PreparationReceipt3),
                "sample": wire_schema(SampleManifest3),
                "report": wire_schema(SampleReport3),
                "execution": wire_schema(Execution3),
            },
        }

    @api.post("/source-preparations", status_code=202)
    def submit(payload: dict[str, Any]) -> dict[str, Any]:
        try:
            request = from_wire(PreparationRequest3, payload)
        except ValueError as exc:
            raise TokenScopeError("INVALID_ARGUMENT", "Invalid preparation input", 422) from exc
        return to_wire(store.submit(request))

    @api.get("/source-preparations/{preparation_id}")
    def receipt(preparation_id: str) -> dict[str, Any]:
        return to_wire(store.receipt(preparation_id))

    @api.get("/source-preparations/{preparation_id}/execution")
    def execution(preparation_id: str) -> dict[str, Any]:
        return to_wire(store.execution(preparation_id))

    @api.post("/source-preparations/{preparation_id}/cancel")
    def cancel(preparation_id: str) -> dict[str, Any]:
        return to_wire(store.cancel(preparation_id))

    @api.post("/source-preparations/{preparation_id}/retry", status_code=202)
    def retry(preparation_id: str, request: Retry3) -> dict[str, Any]:
        return to_wire(store.retry(preparation_id, request.submission_key))

    @api.get("/tasks")
    def tasks(
        offset: int = Query(0, ge=0), limit: int = Query(100, ge=1, le=100)
    ) -> dict[str, Any]:
        page = diagnoses.catalog(offset, limit)
        return {
            "items": [
                {
                    "execution": to_wire(item["execution"]),
                    "source": to_wire(item["source"]),
                    "preparation_id": item["preparation_id"],
                }
                for item in page["items"]
            ],
            "next_offset": page["next_offset"],
            "service_instance_id": instance_id,
        }

    @api.post("/tasks", status_code=202)
    def diagnose(request: DiagnosisRequest3) -> dict[str, Any]:
        return to_wire(diagnoses.submit(request.preparation_id, request.submission_key))

    @api.get("/tasks/{task_id}")
    def diagnosis(task_id: str) -> dict[str, Any]:
        return to_wire(diagnoses.execution(task_id))

    @api.post("/tasks/{task_id}/cancel")
    def cancel_diagnosis(task_id: str) -> dict[str, Any]:
        return to_wire(diagnoses.cancel(task_id))

    @api.get("/tasks/{task_id}/report")
    def report(task_id: str) -> dict[str, Any]:
        return to_wire(SampleReport3.model_validate_json(json.dumps(diagnoses.report(task_id))))

    root.include_router(api)
    return root
