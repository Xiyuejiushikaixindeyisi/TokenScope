"""Versioned per-tenant rules, metric-specific semantics and idempotent signal identities."""

import hashlib
import json
import operator
from typing import Annotated, Any, Literal

from pydantic import Field, model_validator

from tokenscope import ALGORITHM_VERSION
from tokenscope.domain import ModelId, ModelSettings, NonnegativeInt, StrictModel
from tokenscope.monitoring.statistics import LENGTHS, TOTALS

METRICS = (
    "request_count",
    "ideal_hit_rate",
    *(f"totals.{m}" for m in TOTALS),
    *(f"quantiles.{m}.{q}" for m in LENGTHS for q in ("p50", "p80", "p90")),
)


def digest(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(
            value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False
        ).encode()
    ).hexdigest()


class RuleUpdate(StrictModel):
    appid: str = Field(min_length=1)
    model_id: ModelId
    rule_id: str = Field(min_length=1)
    expected_revision: NonnegativeInt
    metric: str
    comparator: Literal["lt", "le", "gt", "ge"]
    threshold: (
        Annotated[int, Field(strict=True)]
        | Annotated[float, Field(strict=True, allow_inf_nan=False)]
    )
    enabled: bool = Field(strict=True, default=True)
    route: Literal["prefix_analysis", "length_analysis", "signal_only"] | None = None
    measurement_signature: str = Field(pattern=r"^[0-9a-f]{64}$")

    @model_validator(mode="after")
    def supported_metric(self) -> "RuleUpdate":
        if self.metric not in METRICS:
            raise ValueError("Unsupported metric")
        return self


def signatures(
    settings: ModelSettings, encoder_identity: str, asset_identity: str
) -> dict[str, str]:
    common = dict(
        model=settings.model_id,
        aliases=sorted(settings.model_aliases),
        valid_set_policy="csv-and-encoding-valid-v1",
    )
    cache = dict(
        block=settings.block_size,
        cp=settings.cp_world_size,
        mtp=settings.mtp,
        prefix=settings.prefix_cache_enabled,
        mode=settings.cache_mode,
        hybrid=settings.hybrid_enabled,
        algorithm=ALGORITHM_VERSION,
    )
    result = {}
    for metric in METRICS:
        identity: dict[str, Any] = dict(common, metric=metric)
        if "ideal_" in metric:
            identity.update(encoder=encoder_identity, cache=cache)
        elif "prompt_tokens" in metric:
            identity.update(encoder=encoder_identity)
        elif "json_tokens" in metric:
            identity.update(asset=asset_identity, plain_encoding="raw-json-v1")
        result[metric] = digest(identity)
    return result


def evaluate(
    metrics: dict[str, Any],
    rules: list[dict[str, Any]],
    measurement_signatures: dict[str, str],
    input_sha256: str,
    model_id: str,
    run_id: str,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    states, signals = [], []
    matching = [r for r in rules if r["appid"] == metrics["appid"] and r["enabled"]]
    for rule in matching:
        metric = rule["metric"]
        value: Any = metrics
        for key in metric.split("."):
            value = value.get(key) if isinstance(value, dict) else None
        status = "clear"
        if rule["measurement_signature"] != measurement_signatures[metric]:
            status = "needs_review"
        elif value is None:
            status = "metric_unavailable"
        elif getattr(operator, rule["comparator"])(value, rule["threshold"]):
            status = "triggered"
            identity = dict(
                input_sha256=input_sha256,
                model_id=model_id,
                appid=rule["appid"],
                rule_id=rule["rule_id"],
                revision=rule["revision"],
                metric=metric,
                measurement_signature=measurement_signatures[metric],
            )
            route = rule["route"] or (
                "prefix_analysis"
                if metric == "ideal_hit_rate"
                else "length_analysis"
                if metric.startswith("quantiles.")
                else "signal_only"
            )
            signals.append(
                dict(
                    identity,
                    event_id=digest(identity),
                    observed_value=value,
                    threshold=rule["threshold"],
                    comparator=rule["comparator"],
                    route=route,
                    status="pending_consumer",
                    result_ref={"run_id": run_id},
                )
            )
        states.append(dict(rule_id=rule["rule_id"], revision=rule["revision"], status=status))
    return states or [{"status": "unconfigured"}], signals
