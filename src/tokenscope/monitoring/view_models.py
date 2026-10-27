"""Exact view wire primitives. The frozen S0 schema is tested independently."""

import hashlib
import json
import re
from datetime import UTC, datetime, timedelta
from typing import Annotated, Any, Literal

from pydantic import BeforeValidator, Field, WithJsonSchema, model_validator

from tokenscope.domain import CacheMode, ModelId, SettingsUpdate, StrictModel
from tokenscope.errors import TokenScopeError
from tokenscope.monitoring.rules import METRICS, RuleUpdate

SCHEMA = "1"


def canonical(value: Any) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode()


def sha(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def wire(value: Any, key: str = "") -> Any:
    if isinstance(value, bool) or value is None:
        return value
    if isinstance(value, int):
        return value if key in ("bin_width", "limit") else str(value)
    if isinstance(value, dict):
        return {k: wire(v, k) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [wire(v) for v in value]
    return value


def utc_ns(ns: int | None) -> str | None:
    if ns is None:
        return None
    sec, nano = divmod(ns, 1000000000)
    return (datetime(1970, 1, 1, tzinfo=UTC) + timedelta(seconds=sec)).strftime(
        "%Y-%m-%dT%H:%M:%S"
    ) + f".{nano:09d}Z"


def data_range(low: int | None, high: int | None) -> dict[str, Any]:
    return dict(start=utc_ns(low), end=utc_ns(high))


def rule_wire(rule: dict[str, Any]) -> dict[str, Any]:
    result = wire(rule)
    if rule["metric"] == "ideal_hit_rate":
        result.update(value_kind="ratio", threshold=float(rule["threshold"]))
    elif isinstance(rule["threshold"], int):
        result["value_kind"] = "integer"
    else:
        result["value_kind"] = "number"
    return dict(result)


def page(offset: int, limit: int, total: int) -> dict[str, Any]:
    if offset < 0 or not 1 <= limit <= 1000:
        raise TokenScopeError("INVALID_PAGINATION", "Invalid page bounds", 422)
    return dict(
        offset=str(offset),
        limit=limit,
        total=str(total),
        next_offset=str(offset + limit) if offset + limit < total else None,
    )


Decimal = Annotated[str, Field(strict=True, pattern=r"^(0|[1-9][0-9]*)$")]
PositiveDecimal = Annotated[str, Field(strict=True, pattern=r"^[1-9][0-9]*$")]
SignedDecimal = Annotated[str, Field(strict=True, pattern=r"^(0|-?[1-9][0-9]*)$")]
StrictBool = Annotated[bool, Field(strict=True)]


class ViewSettingsChanges(StrictModel):
    block_size: PositiveDecimal | None = None
    cp_world_size: PositiveDecimal | None = None
    mtp: StrictBool | None = None
    prefix_cache_enabled: StrictBool | None = None
    hybrid_enabled: StrictBool | None = None
    cache_mode: CacheMode | None = None
    model_aliases: list[Annotated[str, Field(min_length=1)]] | None = None
    encoding_profile: Literal["default", "thinking_enabled", "thinking_disabled"] | None = None

    @model_validator(mode="after")
    def nonempty(self) -> "ViewSettingsChanges":
        values = self.model_dump(exclude_unset=True)
        if not values or any(v is None for v in values.values()):
            raise ValueError("Changes must be nonempty and nonnull")
        if self.model_aliases and len(set(self.model_aliases)) != len(self.model_aliases):
            raise ValueError("Aliases must be unique")
        return self


class ViewSettingsUpdate(StrictModel):
    expected_revision: PositiveDecimal
    changes: ViewSettingsChanges

    def domain(self) -> SettingsUpdate:
        values = self.changes.model_dump(exclude_unset=True)
        for key in ("block_size", "cp_world_size"):
            if key in values:
                values[key] = int(values[key])
        return SettingsUpdate.model_validate(
            dict(expected_revision=int(self.expected_revision), changes=values)
        )


class ViewRuleUpdate(StrictModel):
    appid: str = Field(min_length=1)
    model_id: ModelId
    rule_id: str = Field(min_length=1)
    expected_revision: Decimal
    metric: str
    comparator: Literal["lt", "le", "gt", "ge"]
    threshold: (
        SignedDecimal
        | Annotated[int, Field(strict=True)]
        | Annotated[float, Field(strict=True, allow_inf_nan=False)]
    )
    value_kind: Literal["integer", "ratio", "number"]
    enabled: StrictBool
    route: Literal["prefix_analysis", "length_analysis", "signal_only"] | None
    measurement_signature: str = Field(pattern=r"^[0-9a-f]{64}$")

    @model_validator(mode="after")
    def valid_kind(self) -> "ViewRuleUpdate":
        if self.metric not in METRICS or (
            (self.metric == "ideal_hit_rate") != (self.value_kind == "ratio")
        ):
            raise ValueError("Metric or value kind mismatch")
        if (self.value_kind == "integer") != isinstance(self.threshold, str):
            raise ValueError("Threshold wire type mismatch")
        return self

    def domain(self) -> RuleUpdate:
        values = self.model_dump(exclude={"value_kind"})
        values["expected_revision"] = int(self.expected_revision)
        values["threshold"] = (
            int(self.threshold) if self.value_kind == "integer" else float(self.threshold)
        )
        return RuleUpdate.model_validate(values)


def query_decimal(value: Any) -> int:
    if isinstance(value, int) and not isinstance(value, bool) and value >= 0:
        return value
    if not isinstance(value, str) or re.fullmatch(r"0|[1-9][0-9]*", value) is None:
        raise ValueError("Expected canonical nonnegative decimal")
    return int(value)


QueryDecimal = Annotated[
    int,
    BeforeValidator(query_decimal),
    WithJsonSchema({"type": "string", "pattern": "^(0|[1-9][0-9]*)$"}),
]


Nonempty = Annotated[str, Field(min_length=1)]
QueryPositive = Annotated[
    QueryDecimal, Field(gt=0), WithJsonSchema({"type": "string", "pattern": "^[1-9][0-9]*$"})
]
