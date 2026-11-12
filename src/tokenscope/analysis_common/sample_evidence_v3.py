"""Seal small exact examples during execution. Reads never rerun transformations."""

import hashlib
import json
from pathlib import Path
from typing import Any

from tokenscope.analysis_common.contracts import (
    Contract,
    Location,
    ModificationPlan,
    RequestKey,
    stable_id,
)
from tokenscope.analysis_common.modifications import apply_mutations
from tokenscope.analysis_common.recommendation_evidence import focus_pair
from tokenscope.analysis_common.recommendations import RecommendationBudget, RecommendationExample
from tokenscope.analysis_common.sample_source import SampleResolvedSource
from tokenscope.domain import ModelSettings


class EvidenceBundle3(Contract):
    task_id: str
    sample_id: str
    owner_id: str
    examples: tuple[RecommendationExample, ...]


def example_for(
    source: SampleResolvedSource, owner: dict[str, Any], task_id: str, plan_path: Path | None = None
) -> RecommendationExample:
    pair = owner["comparison"]
    left = source.read_request(RequestKey.model_validate_json(json.dumps(pair["left"])))
    right = source.read_request(RequestKey.model_validate_json(json.dumps(pair["right"])))
    if left.raw_sha256 != pair["left_raw_sha256"] or right.raw_sha256 != pair["right_raw_sha256"]:
        raise ValueError("EVIDENCE_SOURCE_DIGEST_MISMATCH")
    pointer = pair["difference_pointers"][0]
    a = Location(
        request_key=left.request_key,
        raw_sha256=left.raw_sha256,
        source_pointer=owner.get("left_locations", [{"source_pointer": pointer}])[0][
            "source_pointer"
        ],
    )
    b = Location(
        request_key=right.request_key,
        raw_sha256=right.raw_sha256,
        source_pointer=owner.get("right_locations", [{"source_pointer": pointer}])[0][
            "source_pointer"
        ],
    )
    budget = RecommendationBudget(
        max_examples_per_group=3, max_excerpt_codepoints=1000, max_context_codepoints=120
    )
    after = None
    if plan_path is not None:
        plan = ModificationPlan.model_validate_json(plan_path.read_bytes())
        ops = tuple(
            op for op in plan.operations if op.target.location.request_key == left.request_key
        )
        if not ops:
            left, right, a, b = right, left, b, a
            ops = tuple(
                op for op in plan.operations if op.target.location.request_key == left.request_key
            )
        if ops:
            raw, _ = apply_mutations(
                left, ops, ModelSettings.model_validate_json(source.scope.source.settings_json)
            )
            changed_location = a.model_copy(
                update={"raw_sha256": hashlib.sha256(raw.encode()).hexdigest()}
            )
            _, after = focus_pair(left.raw_body, a, raw, changed_location, budget)
    before, comparison = focus_pair(left.raw_body, a, right.raw_body, b, budget)
    owner_id = str(owner.get("finding_id", owner.get("group_id")))
    return RecommendationExample(
        example_id=stable_id("example", [task_id, owner_id]),
        task_id=task_id,
        scope_id=source.scope.scope_id,
        owner_id=owner_id,
        before=before,
        comparison=comparison,
        after=after,
    )
