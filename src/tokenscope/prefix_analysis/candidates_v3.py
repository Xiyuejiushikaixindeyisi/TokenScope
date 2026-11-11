"""Bounded, deterministic channel/bucket/time interleaving over sealed A only."""

from collections import deque
from collections.abc import Iterator
from dataclasses import dataclass
from typing import Any

from tokenscope.analysis_common.contracts import RequestView, stable_id
from tokenscope.prefix_analysis.dynamic import slots_in_text, text_shape
from tokenscope.prefix_analysis.prefix_findings_v3 import dynamic_fields
from tokenscope.prefix_analysis.session_clock_v3 import clock_fields, clock_shape
from tokenscope.prefix_analysis.structure import tool_map, tool_set_fingerprint


def feature_keys(request: RequestView, body: dict[str, Any]) -> list[tuple[str, str]]:
    identity = [request.encoder_identity, request.effective_options_json]
    keys = []
    for field in clock_fields(body):
        if not field.locations.reason_code:
            keys.append(
                (
                    "L1",
                    stable_id(
                        "bucket",
                        [
                            identity,
                            field.logical_key,
                            clock_shape(field.text, field.locations.blocks),
                        ],
                    ),
                )
            )
    for logical, (_, text) in dynamic_fields(body).items():
        slots = slots_in_text(text)
        if slots:
            keys.append(
                (logical[:2], stable_id("bucket", [identity, logical, text_shape(text, slots)]))
            )
    # A common bounded fallback also compares empty/disjoint valid tool sets.
    if body.get("tools") in (None, []) or tool_map(body) is not None:
        keys.append(("L3", stable_id("tool-presence", identity)))
    mapping = tool_map(body)
    if mapping:
        keys.append(("L2", stable_id("bucket", [identity, tool_set_fingerprint(body)])))
        for name in mapping:
            keys.append(("L3", stable_id("bucket", [identity, name])))
    # These are evidence-only fallbacks, never inferred conversation identity.
    for channel in ("L4", "L5"):
        keys.append((channel, stable_id("bucket", identity)))
    return list(dict.fromkeys(keys))


def time_order(size: int) -> Iterator[int]:
    """Endpoints then breadth-first time subdivisions, O(n), no pair matrix."""
    if size <= 0:
        return
    yield 0
    if size == 1:
        return
    yield size - 1
    pending = deque([(1, size - 2)])
    while pending:
        lo, hi = pending.popleft()
        if lo > hi:
            continue
        mid = (lo + hi) // 2
        yield mid
        pending.extend(((lo, mid - 1), (mid + 1, hi)))


def bucket_pairs(indices: list[int], limit: int) -> Iterator[tuple[int, int]]:
    for position in time_order(len(indices)):
        # Select at most K indices without enumerating all preceding pairs.
        for count, prior in enumerate(time_order(position)):
            if count >= limit:
                break
            yield indices[prior], indices[position]


@dataclass
class CandidateSchedule:
    buckets: dict[tuple[str, str], list[int]]
    candidate_limit: int = 16

    def __post_init__(self) -> None:
        if not 1 <= self.candidate_limit <= 128:
            raise ValueError("Per-request predecessor limit must be in [1,128]")

    def pairs(self) -> Iterator[tuple[str, int, int]]:
        channels: dict[str, deque[Iterator[tuple[int, int]]]] = {}
        for (channel, _), indices in sorted(self.buckets.items()):
            if len(indices) > 1:
                channels.setdefault(channel, deque()).append(
                    bucket_pairs(indices, self.candidate_limit)
                )
        active = deque(channels)
        # K is task-wide per right request, not multiplied by channels/buckets.
        predecessors: dict[int, set[int]] = {}
        while active:
            channel = active.popleft()
            queue = channels[channel]
            iterator = queue.popleft()
            pair = next(iterator, None)
            if pair is not None:
                queue.append(iterator)
                left, right = pair
                selected = predecessors.setdefault(right, set())
                if left in selected or len(selected) < self.candidate_limit:
                    selected.add(left)
                    yield channel, left, right
            if queue:
                active.append(channel)
