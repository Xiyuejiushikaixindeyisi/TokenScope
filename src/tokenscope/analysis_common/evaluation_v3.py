"""Complete-window counterfactuals; no pilot/full promotion or gain filter."""

from dataclasses import dataclass, field
from fractions import Fraction
from pathlib import Path
from typing import Any, Literal, Self

from pydantic import Field, model_validator

from tokenscope.analysis_common.contracts import Contract, RequestKey
from tokenscope.analysis_common.encoding import EncodingContext
from tokenscope.analysis_common.modifications import apply_mutations, value_digest
from tokenscope.analysis_common.runtime_v3 import BudgetLedger, TaskStopped
from tokenscope.analysis_common.sample_source import SampleResolvedSource
from tokenscope.analysis_common.supervisor_v3 import atomic_json
from tokenscope.domain import ModelSettings
from tokenscope.encoding.batch import EncodedRequest
from tokenscope.errors import TokenScopeError
from tokenscope.monitoring.simulation import PrefixLedger, make_strategy
from tokenscope.prefix_analysis.clock_discovery_v3 import ClockFinding3, compile_clock_plan
from tokenscope.prefix_analysis.prefix_findings_v3 import PrefixFinding3, compile_prefix_plan


class Rational3(Contract):
    numerator: int
    denominator: int = Field(gt=0)


EvaluationStatus3 = Literal[
    "positive",
    "zero",
    "negative",
    "no_targets",
    "no_op",
    "unavailable",
    "budget_exhausted",
    "cancelled",
    "failed",
    "not_evaluated",
]


class WindowEvaluation3(Contract):
    role: Literal["discovery", "review"]
    status: EvaluationStatus3
    transformation_digest: str
    reason_code: str | None = None
    complete: bool = False
    n: int = 0
    matched: int = 0
    modified: int = 0
    before: dict[str, int] | None = None
    after: dict[str, int] | None = None
    improvement_pp: Rational3 | None = None
    rows_ref: str | None = None
    plan_ref: str | None = None

    @model_validator(mode="after")
    def complete_metrics(self) -> Self:
        if self.complete:
            if self.before is None or self.after is None or self.n <= 0:
                raise ValueError("Complete window requires both totals")
            for values in (self.before, self.after):
                if (
                    set(values) != {"p", "h", "c"}
                    or min(values.values()) < 0
                    or values["p"] != values["h"] + values["c"]
                ):
                    raise ValueError("Invalid conserved metrics")
            if not 0 <= self.modified <= self.matched <= self.n:
                raise ValueError("Invalid target counts")
            pp = improvement(self.before, self.after)
            expected = (
                "unavailable"
                if pp is None
                else (
                    "positive" if pp.numerator > 0 else "negative" if pp.numerator < 0 else "zero"
                )
            )
            if self.status != expected:
                raise ValueError("Status differs from exact gain")
            if self.improvement_pp != pp:
                raise ValueError("Improvement must equal exact window rates")
        elif self.before is not None or self.after is not None or self.improvement_pp is not None:
            raise ValueError("Incomplete window cannot publish full totals")
        return self


def improvement(before: dict[str, int], after: dict[str, int]) -> Rational3 | None:
    if not before["p"] or not after["p"]:
        return None
    value = 100 * (Fraction(after["h"], after["p"]) - Fraction(before["h"], before["p"]))
    return Rational3(numerator=value.numerator, denominator=value.denominator)


def stopped_status(code: str) -> EvaluationStatus3:
    if code == "USER_CANCELLED":
        return "cancelled"
    if code.startswith("BUDGET_") or code in (
        "DEADLINE_EXHAUSTED",
        "PHASE_DEADLINE_EXHAUSTED",
        "MEMORY_PRESSURE",
    ):
        return "budget_exhausted"
    return "failed"


@dataclass
class SampleBaseline3:
    """One verified replay per immutable sample; retains small metrics, never token arrays."""

    source: SampleResolvedSource
    control: BudgetLedger
    context: EncodingContext = field(init=False)
    rows: dict[RequestKey, dict[str, Any]] = field(default_factory=dict)
    totals: dict[str, int] = field(default_factory=lambda: dict(p=0, h=0, c=0))

    def __post_init__(self) -> None:
        self.context = EncodingContext(self.source, cpu_budget=self.control.profile.cpu_budget)

    def prepare(self, directory: Path) -> None:
        directory.mkdir(parents=True, exist_ok=False)
        settings = ModelSettings.model_validate_json(self.source.scope.source.settings_json)
        ledger = PrefixLedger(directory / "baseline.sqlite3")
        try:
            strategy = make_strategy(settings, self.source.scope.source.asset_identity, ledger)
            for request in self.source.iter_requests():
                self.control.reserve_many(
                    {"encoding_calls": 1, "encoding_input_bytes": len(request.raw_body.encode())}
                )
                encoded = self.context.verify_baseline(request)
                self.control.reserve("encoding_output_tokens", encoded.prompt_tokens)
                metrics = strategy.process(self.source.scope.appid, encoded.prompt_ids)
                values = dict(
                    p=encoded.prompt_tokens, h=metrics.hit_tokens, c=metrics.compute_tokens
                )
                self.rows[request.request_key] = values | {"ids_sha256": encoded.prompt_digest}
                for key, value in values.items():
                    self.totals[key] += value
            self.source.verify()
            if len(self.rows) != self.source.scope.request_count:
                raise TokenScopeError("SCOPE_CHANGED", "Incomplete baseline", 409)
            atomic_json(directory / "totals.json", self.totals)
        finally:
            ledger.close()

    def original(self, request: Any) -> EncodedRequest:
        row = self.rows[request.request_key]
        ids = self.source.read_ids(request)
        return EncodedRequest(
            request.baseline_metrics.j, ids, row["ids_sha256"], request.encoder_identity, {}
        )


def evaluate_window(
    source: SampleResolvedSource,
    finding: ClockFinding3 | PrefixFinding3,
    directory: Path,
    control: BudgetLedger,
    baseline: SampleBaseline3 | None = None,
) -> WindowEvaluation3:
    digest = value_digest(finding.recipe.model_dump(mode="json"))
    base: dict[str, Any] = {"role": source.role, "transformation_digest": digest}
    ledgers: list[PrefixLedger] = []
    try:
        directory.mkdir(parents=True, exist_ok=False)
        compiled = (
            compile_clock_plan(source, finding, control)
            if isinstance(finding, ClockFinding3)
            else compile_prefix_plan(source, finding, control)
        )
        if compiled.plan is None:
            return WindowEvaluation3(
                **base,
                status="no_op" if compiled.matched else "no_targets",
                reason_code=compiled.reason_code,
                matched=len(set(compiled.matched)),
            )
        if baseline is None:
            baseline = SampleBaseline3(source, control)
            baseline.prepare(directory / "baseline")
        if (
            baseline.source.scope.scope_id != source.scope.scope_id
            or baseline.source.manifest_sha256 != source.manifest_sha256
        ):
            raise TokenScopeError("BASELINE_MISMATCH", "Baseline identity differs", 409)
        context = baseline.context
        settings = ModelSettings.model_validate_json(source.scope.source.settings_json)
        operations: dict[RequestKey, list[Any]] = {}
        for operation in compiled.plan.operations:
            operations.setdefault(operation.target.location.request_key, []).append(operation)
        ledgers = [PrefixLedger(directory / "after.sqlite3")]
        strategies = [
            make_strategy(settings, source.scope.source.asset_identity, ledger)
            for ledger in ledgers
        ]
        totals = [dict(baseline.totals), dict(p=0, h=0, c=0)]
        rows: list[dict[str, Any]] = []
        for request in source.iter_requests():
            raw, changes = apply_mutations(
                request, tuple(operations.pop(request.request_key, ())), settings
            )
            changed = raw != request.raw_body
            if changed:
                control.reserve_many(
                    {"encoding_calls": 1, "encoding_input_bytes": len(raw.encode())}
                )
                after = context.encode(request, raw)
                control.reserve("encoding_output_tokens", after.prompt_tokens)
            else:
                after = baseline.original(request)
            row: dict[str, Any] = {
                "request_key": request.request_key.model_dump(mode="json"),
                "sequence": len(rows),
                "mutations": changes,
            }
            row["before"] = baseline.rows[request.request_key]
            metrics = strategies[0].process(source.scope.appid, after.prompt_ids)
            values = dict(p=after.prompt_tokens, h=metrics.hit_tokens, c=metrics.compute_tokens)
            if values["p"] != values["h"] + values["c"]:
                raise TokenScopeError("METRIC_CONSERVATION", "Invalid replay metrics", 409)
            for key, value in values.items():
                totals[1][key] += value
            row["after"] = values | {"ids_sha256": after.prompt_digest}
            import json

            control.reserve("result_bytes", len(json.dumps(row).encode()))
            rows.append(row)
        if operations or len(rows) != source.scope.request_count:
            raise TokenScopeError("SCOPE_CHANGED", "Incomplete sample replay", 409)
        source.verify()
        control.checkpoint()
        pp = improvement(*totals)
        status: EvaluationStatus3 = (
            "unavailable"
            if pp is None
            else ("positive" if pp.numerator > 0 else "negative" if pp.numerator < 0 else "zero")
        )
        atomic_json(directory / "rows.json", rows)
        atomic_json(directory / "plan.json", compiled.plan.model_dump(mode="json"))
        return WindowEvaluation3(
            **base,
            status=status,
            complete=True,
            n=len(rows),
            matched=len(set(compiled.matched)),
            modified=len(set(compiled.modified)),
            before=totals[0],
            after=totals[1],
            improvement_pp=pp,
            reason_code="ZERO_DENOMINATOR" if pp is None else None,
            rows_ref="rows.json",
            plan_ref="plan.json",
        )
    except (TaskStopped, TokenScopeError) as exc:
        return WindowEvaluation3(**base, status=stopped_status(exc.code), reason_code=exc.code)
    finally:
        for ledger in ledgers:
            ledger.close()
