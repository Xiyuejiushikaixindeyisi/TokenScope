"""User V2 namespace. All reads are side-effect-free."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query, Request, Response
from fastapi.routing import APIRoute

from tokenscope.errors import TokenScopeError
from tokenscope.user_monitoring.contracts import (
    Bind,
    ErrorEnvelope,
    Evaluation,
    EvaluationRequest,
    Modes,
    Ranking,
    Receipt,
    ScenarioPayload,
    Submit,
)
from tokenscope.user_monitoring.defaults import DefaultEstimator
from tokenscope.user_monitoring.discovery import Discovery
from tokenscope.user_monitoring.discovery_contracts import (
    AutoEvaluation,
    AutoEvaluationRequest,
    DefaultConfig,
    DefaultPage,
    DefaultQuery,
    DefaultUpdate,
    DiscoveryPage,
    DiscoveryQuery,
)
from tokenscope.user_monitoring.estimator import EstimatorService
from tokenscope.user_monitoring.ranking import ModeQuery, RankingService, RankQuery
from tokenscope.user_monitoring.service import UserRunService


def router(service: UserRunService) -> APIRouter:
    def guard(request: Request, response: Response) -> None:
        if request.headers.get("x-tokenscope-instance-id") != service.service_id:
            raise TokenScopeError("INSTANCE_MISMATCH", "Expected service instance identity", 409)
        response.headers["Cache-Control"] = "no-store"
        response.headers["X-TokenScope-Instance-Id"] = service.service_id

    api = APIRouter(
        prefix="/monitoring/user-v2",
        dependencies=[Depends(guard)],
        responses={code: {"model": ErrorEnvelope} for code in (404, 409, 422, 503)},
    )
    ranking = RankingService(service)
    estimator = EstimatorService(service)
    discovery = Discovery(service)
    defaults = DefaultEstimator(service)

    @api.get("/runs", response_model=DiscoveryPage)
    def runs(query: Annotated[DiscoveryQuery, Query()]) -> DiscoveryPage:
        return discovery.catalog(query)

    @api.get("/ttft/defaults", response_model=DefaultPage)
    def default_configs(query: Annotated[DefaultQuery, Query()]) -> DefaultPage:
        return defaults.get(query)

    @api.post("/ttft/defaults", response_model=DefaultConfig, status_code=201)
    def update_defaults(body: DefaultUpdate) -> DefaultConfig:
        return defaults.update(body)

    @api.post("/ttft/evaluations", response_model=AutoEvaluation, status_code=201)
    def auto_evaluate(body: AutoEvaluationRequest) -> AutoEvaluation:
        return defaults.evaluate(body)

    @api.get("/ttft/evaluations/{evaluation_id}", response_model=AutoEvaluation)
    def auto_evaluation(evaluation_id: str) -> AutoEvaluation:
        return defaults.evaluation(evaluation_id)

    @api.post("/runs", response_model=Receipt, status_code=202)
    def submit(body: Submit) -> Receipt:
        return service.submit(body)

    @api.post("/bindings", response_model=Receipt, status_code=202)
    def bind(body: Bind) -> Receipt:
        return service.submit(body)

    @api.get("/runs/{user_run_id}", response_model=Receipt)
    def receipt(user_run_id: str) -> Receipt:
        return service.receipt(user_run_id)

    @api.get("/runs/{user_run_id}/rankings", response_model=Ranking)
    def rankings(user_run_id: str, query: Annotated[RankQuery, Query()]) -> Ranking:
        return ranking.rankings(user_run_id, query)

    @api.get("/runs/{user_run_id}/modes", response_model=Modes)
    def modes(user_run_id: str, query: Annotated[ModeQuery, Query()]) -> Modes:
        return ranking.modes(user_run_id, query)

    @api.post("/scenarios", response_model=ScenarioPayload, status_code=201)
    def put_scenario(body: ScenarioPayload) -> ScenarioPayload:
        return estimator.put_scenario(body)

    @api.get("/scenarios/{scenario_id}/{revision}", response_model=ScenarioPayload)
    def scenario(scenario_id: str, revision: str) -> ScenarioPayload:
        return estimator.scenario(scenario_id, revision)

    @api.post("/evaluations", response_model=Evaluation, status_code=201)
    def evaluate(body: EvaluationRequest) -> Evaluation:
        return estimator.evaluate(body)

    @api.get("/evaluations/{evaluation_id}", response_model=Evaluation)
    def evaluation(evaluation_id: str) -> Evaluation:
        return estimator.evaluation(evaluation_id)

    for route in api.routes:
        if isinstance(route, APIRoute):
            route.openapi_extra = {
                "parameters": [
                    {
                        "name": "X-TokenScope-Instance-Id",
                        "in": "header",
                        "required": True,
                        "schema": {"type": "string", "minLength": 1},
                    }
                ],
                "x-runtime-implemented": True,
                "x-user-contract-version": "2.1.0",
            }
    return api
