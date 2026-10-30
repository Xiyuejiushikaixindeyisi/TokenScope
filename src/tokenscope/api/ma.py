"""MA-specific routes, separate from the frozen V1 presentation contract."""

from fastapi import APIRouter, Depends, Request, Response

from tokenscope.monitoring.ma.contracts import (
    Catalog,
    ErrorEnvelope,
    QualityPage,
    Receipt,
    Snapshot,
    Submit,
)
from tokenscope.monitoring.ma.service import MaService
from tokenscope.monitoring.view_models import QueryDecimal


def router(service: MaService) -> APIRouter:
    def guard(request: Request, response: Response) -> None:
        service.base.views.guard(request.headers.get("x-tokenscope-instance-id"))
        response.headers["Cache-Control"] = "no-store"
        response.headers["X-TokenScope-Instance-Id"] = service.service_id

    api = APIRouter(
        prefix="/monitoring/ma",
        dependencies=[Depends(guard)],
        responses={code: {"model": ErrorEnvelope} for code in (404, 409, 422, 503)},
    )

    @api.post("/runs", response_model=Receipt, status_code=202)
    def submit(body: Submit) -> Receipt:
        return service.submit(body)

    @api.get("/runs/{ma_run_id}", response_model=Receipt)
    def receipt(ma_run_id: str) -> Receipt:
        return service.store.receipt(ma_run_id)

    @api.get("/submissions/{submission_key}", response_model=Receipt)
    def submission(submission_key: str) -> Receipt:
        return service.submission(submission_key)

    @api.get("/catalog", response_model=Catalog)
    def catalog(
        model_standard_name: str | None = None,
        offset: QueryDecimal = 0,
        limit: int = 100,
        catalog_revision: QueryDecimal | None = None,
    ) -> Catalog:
        return service.catalog(model_standard_name, offset, limit, catalog_revision)

    @api.get("/runs/{ma_run_id}/instances/{instance_uuid}", response_model=Snapshot)
    def snapshot(ma_run_id: str, instance_uuid: str) -> Snapshot:
        return service.snapshot(ma_run_id, instance_uuid)

    @api.get("/runs/{ma_run_id}/quality", response_model=QualityPage)
    def quality(ma_run_id: str, offset: QueryDecimal = 0, limit: int = 100) -> QualityPage:
        return service.quality(ma_run_id, offset, limit)

    return api
