"""Statically registered proposal adapter, separate from the immutable H0 protocol."""

from typing import Literal, Protocol

from tokenscope.analysis_common.contracts import AnalysisFragment, Contract, Name, RequestView
from tokenscope.analysis_common.plugins import EvidenceCapabilities, MutationPreparation, RunControl
from tokenscope.analysis_common.recommendations import Basis, Proposal, RecipeBundle


class ProposalDescriptor(Contract):
    version: Literal["token-auto-proposals-1"] = "token-auto-proposals-1"
    generator_identity: Name
    rule_ids: tuple[Literal["T2", "T3", "T4"], ...]
    basis_kinds: tuple[
        Literal["business_policy", "explicit_authorization", "offline_hypothesis"], ...
    ]


class ProposalAdapter(Protocol):
    def describe(self) -> ProposalDescriptor: ...

    def validate_bundle(self, bundle: RecipeBundle) -> RecipeBundle: ...

    def propose(
        self,
        task_id: str,
        scope_id: str,
        request: RequestView,
        fragment_id: str,
        fragment: AnalysisFragment,
        bundle_snapshot: RecipeBundle,
        capabilities: EvidenceCapabilities,
        control: RunControl,
    ) -> tuple[Proposal, ...]: ...

    def prepare_proposal(
        self, request: RequestView, proposal: Proposal, basis_snapshot: Basis
    ) -> MutationPreparation: ...


class ProposalRegistry:
    def __init__(self) -> None:
        self._adapter: ProposalAdapter | None = None

    def register(self, adapter: ProposalAdapter) -> None:
        if self._adapter is not None:
            raise ValueError("Duplicate proposal adapter")
        ProposalDescriptor.model_validate(adapter.describe())
        self._adapter = adapter

    def get(self) -> ProposalAdapter | None:
        return self._adapter

    def capabilities(self) -> tuple[ProposalDescriptor, ...]:
        return () if self._adapter is None else (self._adapter.describe(),)


def validate_support(
    proposal: Proposal, task_id: str, scope_id: str, fragment_id: str, fragment: AnalysisFragment
) -> None:
    """Validate against actual fragment relations, not only untrusted identifiers."""
    observations = {o.observation_id: o for o in fragment.observations}
    units = {u.unit_id: u for u in fragment.units}
    findings = {f.finding_id: f for f in fragment.finding_candidates}
    locations = {loc.location_id: loc for loc in fragment.locations}
    for support in proposal.support_refs:
        if (
            support.kind != "token_observation"
            or (support.task_id, support.scope_id, support.fragment_id)
            != (task_id, scope_id, fragment_id)
            or (support.request_key, support.raw_sha256)
            != (fragment.request_key, fragment.raw_sha256)
        ):
            raise ValueError("Foreign fragment support")
        if not set(support.observation_ids) <= observations.keys():
            raise ValueError("Unknown observation")
        related_units = {u for o in support.observation_ids for u in observations[o].unit_ids}
        if not set(support.unit_ids) <= related_units:
            raise ValueError("Unrelated unit")
        related_locations = {units[u].location_id for u in related_units}
        if not set(support.location_ids) <= related_locations:
            raise ValueError("Unrelated location")
        if not set(support.finding_ids) <= findings.keys():
            raise ValueError("Unknown finding")
        for finding_id in support.finding_ids:
            if not set(findings[finding_id].observation_ids) & set(support.observation_ids):
                raise ValueError("Unrelated finding")
    for target in proposal.request_targets:
        if locations.get(target.location.location_id) != target.location:
            raise ValueError("Target absent from fragment")
