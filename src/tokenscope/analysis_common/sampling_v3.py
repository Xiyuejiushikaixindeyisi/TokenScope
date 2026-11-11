"""Streaming, metadata-only selection of two bounded contiguous windows.

A is the first admissible prefix of a segment; B is the latest admissible suffix
after A. Rejected records break segments. No body, token IDs or gain enters this
algorithm. Costs are bounds on materialized samples, not on the parent dataset.
"""

import hashlib
from collections import Counter, deque
from collections.abc import Iterable
from itertools import pairwise
from typing import Literal, Self

from pydantic import Field, model_validator

from tokenscope.analysis_common.contracts import Contract, Digest, RequestKey, canonical_metadata


class SampleLimits(Contract):
    """Internal positive limits; deployment profile selection belongs to runtime v3."""

    max_requests: int = Field(gt=0, le=100000)
    max_raw_bytes: int = Field(gt=0)
    max_prompt_tokens: int = Field(gt=0)
    max_record_bytes: int = Field(gt=0)
    max_record_tokens: int = Field(gt=0)
    max_metadata_bytes: int = Field(gt=0)
    max_snapshot_bytes: int = Field(gt=0)
    max_exclusion_examples: int = Field(ge=0, le=1000)
    review_requested: bool = True

    @property
    def digest(self) -> str:
        return hashlib.sha256(canonical_metadata(self)).hexdigest()


class SampleMetadata(Contract):
    key: RequestKey
    time_ns: int
    raw_bytes: int = Field(ge=0)
    prompt_tokens: int | None = Field(default=None, ge=0)

    @property
    def order(self) -> tuple[int, int]:
        return self.time_ns, self.key.source_record_index


class ExcludedRecord(Contract):
    key: RequestKey
    reason: str


class SampleWindow(Contract):
    role: Literal["discovery", "review"]
    members: tuple[SampleMetadata, ...]
    keys_digest: Digest
    raw_bytes: int = Field(ge=0)
    prompt_tokens: int = Field(ge=0)
    contiguous: Literal[True] = True

    @model_validator(mode="after")
    def consistent(self) -> Self:
        if not self.members:
            raise ValueError("Empty windows must be omitted")
        if any(a.order >= b.order for a, b in pairwise(self.members)):
            raise ValueError("Window is not strictly ordered")
        if len({m.key for m in self.members}) != len(self.members):
            raise ValueError("Duplicate window member")
        if any(m.prompt_tokens is None for m in self.members):
            raise ValueError("Unencoded member")
        if self.raw_bytes != sum(m.raw_bytes for m in self.members):
            raise ValueError("Window byte count differs")
        if self.prompt_tokens != sum(m.prompt_tokens or 0 for m in self.members):
            raise ValueError("Window token count differs")
        if self.keys_digest != keys_digest(m.key for m in self.members):
            raise ValueError("Window key digest differs")
        return self


class SamplingDecision(Contract):
    algorithm: Literal["first-prefix-last-suffix-1"] = "first-prefix-last-suffix-1"
    parent_count: int = Field(ge=0)
    parent_keys_digest: Digest
    admitted_count: int = Field(ge=0)
    excluded_count: int = Field(ge=0)
    exclusion_counts: dict[str, int]
    exclusion_examples: tuple[ExcludedRecord, ...]
    windows: tuple[SampleWindow, ...]
    limits: SampleLimits

    @model_validator(mode="after")
    def consistent(self) -> Self:
        if self.parent_count != self.admitted_count + self.excluded_count:
            raise ValueError("Metadata counts do not conserve")
        if any(n < 0 for n in self.exclusion_counts.values()):
            raise ValueError("Negative exclusion count")
        if sum(self.exclusion_counts.values()) != self.excluded_count:
            raise ValueError("Exclusion counts differ")
        if len(self.exclusion_examples) > self.limits.max_exclusion_examples:
            raise ValueError("Too many exclusion examples")
        roles = [w.role for w in self.windows]
        if roles not in ([], ["discovery"], ["discovery", "review"]):
            raise ValueError("Invalid window roles")
        members = [m for w in self.windows for m in w.members]
        if len({m.key for m in members}) != len(members):
            raise ValueError("Discovery and review overlap")
        if any(a.order >= b.order for a, b in pairwise(members)):
            raise ValueError("Window order differs")
        if len(members) > min(self.admitted_count, self.limits.max_requests):
            raise ValueError("Too many selected members")
        if sum(m.raw_bytes for m in members) > self.limits.max_raw_bytes:
            raise ValueError("Selected bytes exceed budget")
        if sum(m.prompt_tokens or 0 for m in members) > self.limits.max_prompt_tokens:
            raise ValueError("Selected tokens exceed budget")
        if any(
            m.raw_bytes > self.limits.max_record_bytes
            or (m.prompt_tokens or 0) > self.limits.max_record_tokens
            for m in members
        ):
            raise ValueError("Selected record exceeds limit")
        return self


def keys_digest(keys: Iterable[RequestKey]) -> str:
    digest = hashlib.sha256()
    for key in keys:
        digest.update(canonical_metadata(key) + b"\n")
    return digest.hexdigest()


def select_windows(rows: Iterable[SampleMetadata], limits: SampleLimits) -> SamplingDecision:
    split = 2 if limits.review_requested and limits.max_requests > 1 else 1
    count_limit = max(1, limits.max_requests // split)
    byte_limit = limits.max_raw_bytes // split
    token_limit = limits.max_prompt_tokens // split
    first: list[SampleMetadata] = []
    tail: deque[SampleMetadata] = deque()
    prior_tail: tuple[SampleMetadata, ...] = ()
    first_bytes = first_tokens = tail_bytes = tail_tokens = 0
    fixed = False
    previous: tuple[int, int] | None = None
    run_id: str | None = None
    digest = hashlib.sha256()
    total = 0
    excluded: Counter[str] = Counter()
    examples: list[ExcludedRecord] = []
    for row in rows:
        if previous is not None and row.order <= previous:
            raise ValueError("Metadata must be strictly ordered")
        if run_id is not None and row.key.base_run_id != run_id:
            raise ValueError("Mixed metadata sources")
        previous, run_id = row.order, row.key.base_run_id
        total += 1
        digest.update(canonical_metadata(row.key) + b"\n")
        reason = None
        if row.prompt_tokens is None:
            reason = "UNENCODED_RECORD"
        elif row.raw_bytes > min(limits.max_record_bytes, byte_limit):
            reason = "RECORD_BYTE_LIMIT"
        elif row.prompt_tokens > min(limits.max_record_tokens, token_limit):
            reason = "RECORD_TOKEN_LIMIT"
        if reason is not None:
            excluded[reason] += 1
            if len(examples) < limits.max_exclusion_examples:
                examples.append(ExcludedRecord(key=row.key, reason=reason))
            if first:
                fixed = True
            if tail:
                prior_tail = tuple(tail)
            tail.clear()
            tail_bytes = tail_tokens = 0
            continue
        tokens = row.prompt_tokens or 0
        if not fixed and (
            len(first) < count_limit
            and first_bytes + row.raw_bytes <= byte_limit
            and first_tokens + tokens <= token_limit
        ):
            first.append(row)
            first_bytes += row.raw_bytes
            first_tokens += tokens
            continue
        fixed = True
        if split == 1:
            continue
        tail.append(row)
        tail_bytes += row.raw_bytes
        tail_tokens += tokens
        while len(tail) > count_limit or tail_bytes > byte_limit or tail_tokens > token_limit:
            removed = tail.popleft()
            tail_bytes -= removed.raw_bytes
            tail_tokens -= removed.prompt_tokens or 0

    windows: list[SampleWindow] = []
    for role, members in (("discovery", tuple(first)), ("review", tuple(tail) or prior_tail)):
        if members:
            windows.append(
                SampleWindow(
                    role=role,  # type: ignore[arg-type]
                    members=members,
                    keys_digest=keys_digest(m.key for m in members),
                    raw_bytes=sum(m.raw_bytes for m in members),
                    prompt_tokens=sum(m.prompt_tokens or 0 for m in members),
                )
            )
    return SamplingDecision(
        parent_count=total,
        parent_keys_digest=digest.hexdigest(),
        admitted_count=total - sum(excluded.values()),
        excluded_count=sum(excluded.values()),
        exclusion_counts=dict(excluded),
        exclusion_examples=tuple(examples),
        windows=tuple(windows),
        limits=limits,
    )
