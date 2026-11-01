"""Deterministic recipe grouping; business JSON strings retain their exact spelling."""

import hashlib
from collections import defaultdict
from collections.abc import Iterable
from dataclasses import dataclass

from tokenscope.analysis_common.contracts import canonical_metadata, stable_id
from tokenscope.analysis_common.recommendations import Proposal, ProposalTarget, Recipe, SupportRef


@dataclass(frozen=True)
class ProposalGroup:
    recommendation_id: str
    recipe_key: str
    recipe: Recipe
    support_refs: tuple[SupportRef, ...]
    targets: tuple[ProposalTarget, ...]
    support_set_digest: str
    matched_set_digest: str


def digest(value: object) -> str:
    return hashlib.sha256(canonical_metadata(value)).hexdigest()


def group_proposals(
    proposals: Iterable[Proposal],
    *,
    task_id: str,
    scope_id: str,
    generator_identity: str,
    bundle_digest: str,
) -> tuple[ProposalGroup, ...]:
    groups: dict[bytes, list[Proposal]] = defaultdict(list)
    for proposal in proposals:
        proposal = Proposal.model_validate_json(proposal.model_dump_json())
        if any((s.task_id, s.scope_id) != (task_id, scope_id) for s in proposal.support_refs):
            raise ValueError("Foreign proposal")
        groups[canonical_metadata(proposal.recipe)].append(proposal)
    result = []
    for recipe_bytes, members in sorted(groups.items()):
        recipe = members[0].recipe
        key = "recipe:" + hashlib.sha256(recipe_bytes).hexdigest()
        supports = {
            canonical_metadata(s.model_dump(exclude={"task_id"})): s
            for member in members
            for s in member.support_refs
        }
        targets = {canonical_metadata(t): t for member in members for t in member.request_targets}
        support_digest = hashlib.sha256(b"[" + b",".join(sorted(supports)) + b"]").hexdigest()
        request_keys = {canonical_metadata(s.request_key): s.request_key for s in supports.values()}
        matched_digest = digest([request_keys[k] for k in sorted(request_keys)])
        ident = stable_id(
            "rec",
            [scope_id, "token_content", generator_identity, key, support_digest, bundle_digest],
        )
        result.append(
            ProposalGroup(
                ident,
                key,
                recipe,
                tuple(supports[k] for k in sorted(supports)),
                tuple(targets[k] for k in sorted(targets)),
                support_digest,
                matched_digest,
            )
        )
    return tuple(sorted(result, key=lambda g: (g.recipe.primary_rule, g.recipe_key)))
