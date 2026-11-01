"""Streaming single-scope counterfactual replay using the monitoring strategy."""

import json
import sqlite3
from collections import defaultdict
from pathlib import Path
from typing import Any, Literal
from uuid import uuid4

from tokenscope.analysis_common.contracts import (
    AggregateMetrics,
    Coverage,
    EvaluationResult,
    ModificationPlan,
    PreparedMutation,
)
from tokenscope.analysis_common.encoding import EncodingContext
from tokenscope.analysis_common.modifications import apply_mutations
from tokenscope.analysis_common.plugins import ExecutionStopped
from tokenscope.analysis_common.runtime import TaskControl
from tokenscope.analysis_common.source import ResolvedSource
from tokenscope.domain import ModelSettings
from tokenscope.errors import TokenScopeError
from tokenscope.ingestion.csv_reader import InvalidRow
from tokenscope.monitoring.simulation import PrefixLedger, make_strategy


def evaluate_plan(
    source: ResolvedSource,
    plan: ModificationPlan,
    directory: Path,
    *,
    stage: Literal["pilot", "full", "direct_full"] = "direct_full",
    control: TaskControl | None = None,
) -> EvaluationResult:
    """Directory must be fresh. Task publication/attempt sealing belongs to the service."""
    directory.mkdir(parents=True, exist_ok=False)
    evaluation_id = str(uuid4())
    base: dict[str, Any] = dict(
        evaluation_id=evaluation_id,
        plan_id=plan.plan_id,
        scope_id=source.scope.scope_id,
        stage=stage,
        direction=plan.direction,
        baseline_origin=source.scope.baseline_origin,
    )
    before = dict(n=0, j=0, p=0, h=0, c=0)
    after = dict(before)
    modified_before, modified_after = dict(before), dict(before)
    count = 0
    ledgers: list[PrefixLedger] = []
    db: sqlite3.Connection | None = None
    try:
        if plan.source_scope_id != source.scope.scope_id:
            raise TokenScopeError("PLAN_SCOPE_MISMATCH", "Plan scope differs", 409)
        operations: dict[int, list[PreparedMutation]] = defaultdict(list)
        for operation in plan.operations:
            request_key = operation.target.location.request_key
            source.read_request(request_key)
            operations[request_key.source_record_index].append(operation)
        context = EncodingContext(source)
        settings = ModelSettings.model_validate_json(source.scope.source.settings_json)
        for name in ("before.sqlite3", "after.sqlite3"):
            ledgers.append(PrefixLedger(directory / name))
        strategies = [
            make_strategy(settings, source.scope.source.asset_identity, ledger)
            for ledger in ledgers
        ]
        db = sqlite3.connect(directory / "rows.sqlite3")
        db.execute("CREATE TABLE rows (request_index INTEGER PRIMARY KEY, evidence_json TEXT)")
        for request in source.iter_requests():
            if control:
                control.request(request)
                control.encode()
            encoded_before = context.verify_baseline(request)
            ops = tuple(operations.pop(request.request_key.source_record_index, ()))
            raw, changes = apply_mutations(request, ops, settings)
            changed = raw != request.raw_body
            if changed and control:
                control.encode()
            encoded_after = context.encode(request, raw) if changed else encoded_before
            b = strategies[0].process(source.scope.appid, encoded_before.prompt_ids)
            a = strategies[1].process(source.scope.appid, encoded_after.prompt_ids)
            if source.scope.baseline_origin == "original_run_window" and (
                b.hit_tokens != request.baseline_metrics.h
                or b.compute_tokens != request.baseline_metrics.c
            ):
                raise TokenScopeError("BASELINE_MISMATCH", "Original cache metrics differ", 409)
            for totals, subset, encoded, result in (
                (before, modified_before, encoded_before, b),
                (after, modified_after, encoded_after, a),
            ):
                values = dict(
                    n=1,
                    j=encoded.json_tokens,
                    p=encoded.prompt_tokens,
                    h=result.hit_tokens,
                    c=result.compute_tokens,
                )
                for key, value in values.items():
                    totals[key] += value
                    if changed:
                        subset[key] += value
            db.execute(
                "INSERT INTO rows VALUES (?,?)",
                (
                    request.request_key.source_record_index,
                    json.dumps(
                        {
                            "sequence": count,
                            "before_j": encoded_before.json_tokens,
                            "after_j": encoded_after.json_tokens,
                            "before_ids": encoded_before.prompt_digest,
                            "after_ids": encoded_after.prompt_digest,
                            "before_p": encoded_before.prompt_tokens,
                            "after_p": encoded_after.prompt_tokens,
                            "before_h": b.hit_tokens,
                            "after_h": a.hit_tokens,
                            "before_c": b.compute_tokens,
                            "after_c": a.compute_tokens,
                            "changes": changes,
                            "after_raw": raw if ops else None,
                        },
                        ensure_ascii=False,
                    ),
                ),
            )
            count += 1
        if operations or count != source.scope.request_count:
            raise TokenScopeError("SCOPE_CHANGED", "Evaluation target count differs", 409)
        source.verify()
        if control:
            control.checkpoint()
        db.commit()
        return EvaluationResult(
            **base,
            status="available",
            coverage=Coverage(checked=count, eligible=count, complete=True),
            before=AggregateMetrics(**before),
            after=AggregateMetrics(**after),
            modified_before=AggregateMetrics(**modified_before),
            modified_after=AggregateMetrics(**modified_after),
            manifest_ref="rows.sqlite3",
        )
    except (TokenScopeError, InvalidRow, ValueError, KeyError, IndexError, ExecutionStopped) as exc:
        code = getattr(exc, "code", "MODIFICATION_INVALID")
        return EvaluationResult(
            **base,
            status="interrupted" if code == "ANALYSIS_INTERRUPTED" else "blocked",
            coverage=Coverage(checked=count, eligible=source.scope.request_count, complete=False),
            reason_codes=(code,),
        )
    finally:
        if db is not None:
            db.close()
        for ledger in ledgers:
            ledger.close()
