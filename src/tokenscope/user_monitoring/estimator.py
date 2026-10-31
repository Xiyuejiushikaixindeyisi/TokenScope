"""P90-length reference calculator, not a production or aggregate hit-rate guarantee."""

import json
from fractions import Fraction
from typing import Any
from uuid import uuid4

from tokenscope.errors import TokenScopeError
from tokenscope.user_monitoring.contracts import (
    SCENARIO_ADAPTER,
    BatchScenario,
    Evaluation,
    EvaluationRequest,
    Scenario,
    ScenarioPayload,
)
from tokenscope.user_monitoring.service import UserRunService
from tokenscope.user_monitoring.storage import canonical

LIMITATIONS = [
    "P90-length reference only; not an aggregate ideal-hit-rate pass/fail threshold.",
    "Fixed waiting/chunk assumptions; waiting/computation percentiles do not add.",
    "GB service flow is hypothetical for this deployment, not a production instance replay.",
    "Workload, thinking mode and measurement boundary require operator confirmation.",
    "Full-block/MTP and cache-read overhead may make the reference unattainable.",
]


def calculate(
    request: EvaluationRequest,
    scenario: ScenarioPayload,
    *,
    count: int,
    prompt_p90: int | None,
    service_id: str,
    evaluation_id: str,
) -> Evaluation:
    payload: dict[str, Any] = dict(
        evaluation_id=evaluation_id,
        service_instance_id=service_id,
        request=request.model_dump(mode="json"),
        scenario=scenario.model_dump(mode="json"),
        status="unavailable",
        reason=None,
        request_count=str(count),
        prompt_p90=str(prompt_p90) if prompt_p90 is not None else None,
        allowed_chunks=None,
        computable_tokens=None,
        required_hit_fraction=None,
        required_hit_rate=None,
        limitations=list(LIMITATIONS),
    )
    payload["limitations"].append(
        "User assumption; not calibrated performance evidence."
        if scenario.source == "user_assumption"
        else "Measurement applicability is limited to the supplied evidence."
    )
    if isinstance(scenario, BatchScenario):
        # Legacy messages remain unchanged for legacy calculations. Optional
        # validation materials must not read as prerequisites in the new model.
        payload["limitations"] = payload["limitations"][:3] + payload["limitations"][5:]
        payload["limitations"].extend(
            [
                "W covers all non-compute time from GF dispatch to first token; no separate O.",
                "Whole-batch token budget is assumed to be per-request progress, not measured.",
                "Batch timing alone does not validate end-to-end reference accuracy.",
                "Full-block/MTP restrictions or inaccurate W may make the reference unattainable.",
                "Detailed workload and thinking-mode evidence is optional "
                "for assumption scenarios.",
            ]
        )
        if scenario.min_prompt_tokens is None:
            payload["limitations"].append("Prompt-length applicability range is unverified.")
    if not count or prompt_p90 is None or prompt_p90 == 0:
        payload["reason"] = "NO_POSITIVE_P90"
    elif (
        scenario.min_prompt_tokens is not None
        and scenario.max_prompt_tokens is not None
        and not int(scenario.min_prompt_tokens) <= prompt_p90 <= int(scenario.max_prompt_tokens)
    ):
        payload.update(status="out_of_scope", reason="P90_OUTSIDE_CALIBRATION_RANGE")
    else:
        budget = Fraction(request.target_seconds) - Fraction(request.waiting_seconds)
        if isinstance(scenario, Scenario):
            budget -= Fraction(scenario.overhead_seconds)
        if budget < 0 or (budget == 0 and request.comparator == "lt"):
            payload.update(
                status="no_budget",
                reason=(
                    "WAIT_AND_OVERHEAD_EXHAUST_TARGET"
                    if isinstance(scenario, Scenario)
                    else "NONCOMPUTE_BUDGET_EXHAUSTS_TARGET"
                ),
            )
        else:
            steps = budget / Fraction(scenario.chunk_seconds)
            n = (
                steps.numerator // steps.denominator
                if request.comparator == "le"
                else (steps.numerator + steps.denominator - 1) // steps.denominator - 1
            )
            computable = min(prompt_p90, n * int(scenario.chunk_tokens))
            required = Fraction(prompt_p90 - computable, prompt_p90)
            payload.update(
                status="reference_with_limit" if n == 0 else "reference",
                reason="FULL_REUSE_FEASIBILITY_UNPROVEN" if n == 0 else None,
                allowed_chunks=str(n),
                computable_tokens=str(computable),
                required_hit_fraction=dict(
                    numerator=str(required.numerator), denominator=str(required.denominator)
                ),
                required_hit_rate=float(required),
            )
    return Evaluation.model_validate(payload)


class EstimatorService:
    def __init__(self, user: UserRunService) -> None:
        self.user = user

    def put_scenario(self, scenario: ScenarioPayload) -> ScenarioPayload:
        self.user.validate_name(scenario.common_name, scenario.model_id)
        payload = canonical(scenario.model_dump(mode="json"))
        with self.user.store.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            prior = db.execute(
                "SELECT payload FROM scenarios WHERE id=? AND revision=?",
                (scenario.scenario_id, scenario.revision),
            ).fetchone()
            if prior:
                if prior[0] != payload:
                    raise TokenScopeError("SCENARIO_CONFLICT", "Immutable scenario differs", 409)
            else:
                db.execute(
                    "INSERT INTO scenarios VALUES(?,?,?)",
                    (scenario.scenario_id, scenario.revision, payload),
                )
        return scenario

    def scenario(self, scenario_id: str, revision: str) -> ScenarioPayload:
        with self.user.store.connect(readonly=True) as db:
            row = db.execute(
                "SELECT payload FROM scenarios WHERE id=? AND revision=?", (scenario_id, revision)
            ).fetchone()
        if row is None:
            raise TokenScopeError("RESOURCE_NOT_FOUND", "Unknown scenario revision", 404)
        return SCENARIO_ADAPTER.validate_json(row[0])

    def evaluate(self, request: EvaluationRequest) -> Evaluation:
        intent = canonical(request.model_dump(mode="json"))
        with self.user.store.connect(readonly=True) as db:
            prior = db.execute(
                "SELECT intent,payload FROM evaluations WHERE submission_key=?",
                (request.submission_key,),
            ).fetchone()
        if prior:
            if prior[0] != intent:
                raise TokenScopeError("SUBMISSION_KEY_CONFLICT", "Evaluation input differs", 409)
            return Evaluation.model_validate_json(prior[1])
        scenario = self.scenario(request.scenario_id, request.scenario_revision)
        receipt = self.user.receipt(request.user_run_id)
        if receipt.model_id != scenario.model_id or receipt.common_name != scenario.common_name:
            raise TokenScopeError("MODEL_MISMATCH", "Scenario and user service differ", 422)
        with self.user.index(request.user_run_id) as db:
            group = db.execute(
                "SELECT payload FROM groups WHERE appid=? AND width=5000", (request.appid,)
            ).fetchone()
        values = json.loads(group[0]) if group else None
        result = calculate(
            request,
            scenario,
            count=int(values["request_count"]) if values else 0,
            prompt_p90=int(values["prompt_p90"]) if values else None,
            service_id=self.user.service_id,
            evaluation_id="ue-" + uuid4().hex,
        )
        with self.user.store.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            prior = db.execute(
                "SELECT intent,payload FROM evaluations WHERE submission_key=?",
                (request.submission_key,),
            ).fetchone()
            if prior:
                if prior[0] != intent:
                    raise TokenScopeError(
                        "SUBMISSION_KEY_CONFLICT", "Evaluation input differs", 409
                    )
                return Evaluation.model_validate_json(prior[1])
            db.execute(
                "INSERT INTO evaluations VALUES(?,?,?,?)",
                (result.evaluation_id, request.submission_key, intent, result.model_dump_json()),
            )
        return result

    def evaluation(self, evaluation_id: str) -> Evaluation:
        with self.user.store.connect(readonly=True) as db:
            row = db.execute(
                "SELECT payload FROM evaluations WHERE id=?", (evaluation_id,)
            ).fetchone()
        if row is None:
            raise TokenScopeError("RESOURCE_NOT_FOUND", "Unknown evaluation", 404)
        return Evaluation.model_validate_json(row[0])
