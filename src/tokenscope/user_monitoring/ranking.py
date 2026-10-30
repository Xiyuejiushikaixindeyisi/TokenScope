"""Exact rational filtering/sorting performed before bounded SQL pagination."""

import json
from fractions import Fraction
from typing import Annotated, Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from tokenscope.errors import TokenScopeError
from tokenscope.user_monitoring.contracts import Modes, Ranking
from tokenscope.user_monitoring.service import UserRunService

Decimal = Annotated[str, Field(pattern=r"^(0|[1-9][0-9]*)(\.[0-9]+)?$", max_length=128)]
Unsigned = Annotated[str, Field(pattern=r"^(0|[1-9][0-9]*)$", max_length=20)]
Count = Annotated[str, Field(pattern=r"^(0|[1-9][0-9]*)$", max_length=128)]
METRICS = (
    "request_count",
    "ideal_hit_rate",
    "total_ideal_compute_tokens",
    "typical_ideal_compute_tokens",
)


class PageQuery(BaseModel):
    model_config = ConfigDict(extra="forbid")
    bin_width: Literal[1000, 2000, 5000] = 5000
    index_revision: str | None = None
    offset: Unsigned = "0"
    limit: int = Field(default=100, ge=1, le=1000)

    @field_validator("bin_width", mode="before")
    @classmethod
    def parse_width(cls, value: Any) -> Any:
        return int(value) if value in ("1000", "2000", "5000") else value

    @model_validator(mode="after")
    def bounded_offset(self) -> "PageQuery":
        if int(self.offset) > 2**63 - 1:
            raise ValueError("Offset outside SQLite range")
        return self


class RankQuery(PageQuery):
    appid_contains: str | None = None
    sort: Literal[
        "request_count",
        "ideal_hit_rate",
        "total_ideal_compute_tokens",
        "typical_ideal_compute_tokens",
    ] = "request_count"
    direction: Literal["asc", "desc"] = "desc"
    request_count_min: Count | None = None
    request_count_max: Count | None = None
    ideal_hit_rate_min: Decimal | None = None
    ideal_hit_rate_max: Decimal | None = None
    total_ideal_compute_tokens_min: Count | None = None
    total_ideal_compute_tokens_max: Count | None = None
    typical_ideal_compute_tokens_min: Decimal | None = None
    typical_ideal_compute_tokens_max: Decimal | None = None

    @model_validator(mode="after")
    def bounds(self) -> "RankQuery":
        for name in METRICS:
            lo, hi = getattr(self, name + "_min"), getattr(self, name + "_max")
            if lo is not None and hi is not None and Fraction(lo) > Fraction(hi):
                raise ValueError("Inverted range")
            if name == "ideal_hit_rate" and any(Fraction(v) > 1 for v in (lo, hi) if v is not None):
                raise ValueError("Ratio outside 0..1")
        return self


class ModeQuery(PageQuery):
    appid: str = Field(min_length=1)


def compare(left: str, right: str) -> int:
    a, b = Fraction(left), Fraction(right)
    return (a > b) - (a < b)


class RankingService:
    def __init__(self, user: UserRunService) -> None:
        self.user = user

    def rankings(self, run_id: str, query: RankQuery) -> Ranking:
        if int(query.offset) and not query.index_revision:
            raise TokenScopeError(
                "INDEX_REVISION_CONFLICT", "Subsequent pages require revision", 409
            )
        receipt = self.user.receipt(run_id)
        with self.user.index(run_id, query.index_revision) as db:
            db.create_collation("EXACT", compare)
            where = ["width=?"]
            params: list[Any] = [query.bin_width]
            if query.appid_contains is not None:
                where.append("instr(appid,?)>0")
                params.append(query.appid_contains)
            for name in METRICS:
                for suffix, operator in (("min", ">="), ("max", "<=")):
                    bound = getattr(query, name + "_" + suffix)
                    if bound is not None:
                        where.append(f"{name} COLLATE EXACT {operator} ?")
                        params.append(bound)
            condition = " AND ".join(where)
            total = db.execute("SELECT count(*) FROM groups WHERE " + condition, params).fetchone()[
                0
            ]
            records = db.execute(
                "SELECT payload FROM groups WHERE "
                + condition
                + f" ORDER BY {query.sort} IS NULL, {query.sort} COLLATE EXACT "
                + query.direction
                + ",appid COLLATE BINARY LIMIT ? OFFSET ?",
                (*params, query.limit, int(query.offset)),
            )
            rows = [json.loads(r[0]) for r in records]
            meta = json.loads(db.execute("SELECT payload FROM metadata").fetchone()[0])
        end = int(query.offset) + len(rows)
        return Ranking.model_validate(
            dict(
                service_instance_id=self.user.service_id,
                user_run_id=run_id,
                common_name=receipt.common_name,
                index_revision=receipt.index_revision,
                bin_width=query.bin_width,
                total=str(total),
                next_offset=str(end) if end < total else None,
                file_quality=meta["file_quality"],
                rows=rows,
            )
        )

    def modes(self, run_id: str, query: ModeQuery) -> Modes:
        if int(query.offset) and not query.index_revision:
            raise TokenScopeError(
                "INDEX_REVISION_CONFLICT", "Subsequent pages require revision", 409
            )
        receipt = self.user.receipt(run_id)
        with self.user.index(run_id, query.index_revision) as db:
            db.create_collation("EXACT", compare)
            group = db.execute(
                "SELECT payload FROM groups WHERE appid=? AND width=?",
                (query.appid, query.bin_width),
            ).fetchone()
            if group is None:
                raise TokenScopeError("RESOURCE_NOT_FOUND", "Unknown user group", 404)
            row = json.loads(group[0])
            count = int(row["representative_bin"]["count"])
            total = int(row["tie_count"])
            records = db.execute(
                "SELECT payload FROM bins WHERE appid=? AND width=? AND count=? "
                "ORDER BY lower COLLATE EXACT LIMIT ? OFFSET ?",
                (query.appid, query.bin_width, count, query.limit, int(query.offset)),
            )
            bins = [json.loads(r[0]) for r in records]
        end = int(query.offset) + len(bins)
        return Modes.model_validate(
            dict(
                user_run_id=run_id,
                appid=query.appid,
                index_revision=receipt.index_revision,
                bin_width=query.bin_width,
                total=str(total),
                next_offset=str(end) if end < total else None,
                bins=bins,
            )
        )
