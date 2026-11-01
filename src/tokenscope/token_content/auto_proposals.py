"""T2/T4 static proposal adapter for token-auto-proposals-1."""

from tokenscope.analysis_common.contracts import (
    AnalysisFragment,
    ModificationCandidate,
    PreparedMutation,
    RequestView,
    stable_id,
)
from tokenscope.analysis_common.plugins import (
    BudgetSpec,
    EvidenceCapabilities,
    ExecutionStopped,
    MutationPreparation,
    RunControl,
)
from tokenscope.analysis_common.proposal_plugins import ProposalDescriptor, validate_support
from tokenscope.analysis_common.recommendations import (
    Basis,
    Proposal,
    ProposalTarget,
    Recipe,
    RecipeBundle,
    SupportRef,
)
from tokenscope.token_content.authorizations import authorize_candidate
from tokenscope.token_content.auto_config import ResultSelector, parse_config
from tokenscope.token_content.auto_duplicates import (
    duplicate_config,
    duplicate_proposal,
    fresh_duplicate_fragment,
)
from tokenscope.token_content.auto_targets import ResultTarget, select_targets
from tokenscope.token_content.extraction import extract
from tokenscope.token_content.json_values import ContentError, digest
from tokenscope.token_content.transformations import prepare


def validate_recipe(recipe: Recipe) -> None:
    if recipe.primary_rule == "T3":
        duplicate_config(recipe)
        return
    selector, _ = parse_config(
        recipe.selector_json,
        recipe.parameter_generator_json,
        recipe.primary_rule,
        recipe.handler_id,
        recipe.handler_version,
    )
    if any(rule not in ("T2", "T4") for rule in recipe.category_rules):
        raise ValueError("Unsupported recipe category")
    if recipe.basis is not None:
        if recipe.basis.kind != "business_policy" or recipe.basis.authority.status != "verified":
            raise ContentError("BASIS_INVALID")
        # This first version requires exact authorization scope, not an implicit wildcard.
        if ResultSelector.model_validate_json(recipe.basis.scope_selector) != selector:
            raise ContentError("AUTHORIZATION_SCOPE_MISMATCH")


class TokenProposalAdapter:
    def describe(self) -> ProposalDescriptor:
        return ProposalDescriptor(
            generator_identity="token-content-recipes-1",
            rule_ids=("T2", "T3", "T4"),
            basis_kinds=("business_policy", "explicit_authorization"),
        )

    def validate_bundle(self, bundle: RecipeBundle) -> RecipeBundle:
        bundle = RecipeBundle.model_validate_json(bundle.model_dump_json())
        for recipe in bundle.recipes:
            validate_recipe(recipe)
        return bundle

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
    ) -> tuple[Proposal, ...]:
        bundle = self.validate_bundle(bundle_snapshot)
        if digest(request.raw_body) != request.raw_sha256:
            raise ContentError("EVIDENCE_LOCATION_UNAVAILABLE")
        if scope_id != request.scope_id or (fragment.request_key, fragment.raw_sha256) != (
            request.request_key,
            request.raw_sha256,
        ):
            raise ContentError("EVIDENCE_LOCATION_UNAVAILABLE")
        inventory = extract(request, capabilities, control)
        proposals: list[Proposal] = []
        units = {unit.unit_id: unit for unit in fragment.units}
        locations = {location.location_id: location for location in fragment.locations}
        for recipe in bundle.recipes:
            if recipe.primary_rule == "T3":
                duplicate = duplicate_proposal(
                    task_id, scope_id, request, fragment_id, fragment, recipe, control
                )
                if duplicate is not None:
                    validate_support(duplicate, task_id, scope_id, fragment_id, fragment)
                    proposals.append(duplicate)
                continue
            selector, generator = parse_config(
                recipe.selector_json,
                recipe.parameter_generator_json,
                recipe.primary_rule,
                recipe.handler_id,
                recipe.handler_version,
            )
            targets = select_targets(request, inventory, selector, generator, control)
            if not targets:
                continue
            evidence_units: set[str] = set()
            observation_ids: set[str] = set()
            for target in targets:
                entry = target.entry
                if locations.get(entry.location.location_id) != entry.location:
                    raise ContentError("EVIDENCE_LOCATION_UNAVAILABLE")
                ancestors = {entry.unit.unit_id}
                cursor = entry.unit
                while cursor.parent_unit_id is not None:
                    if cursor.parent_unit_id in ancestors or cursor.parent_unit_id not in units:
                        raise ContentError("EVIDENCE_LOCATION_UNAVAILABLE")
                    ancestors.add(cursor.parent_unit_id)
                    cursor = units[cursor.parent_unit_id]
                related = [
                    o
                    for o in fragment.observations
                    if o.rule_id == recipe.primary_rule
                    and o.condition == "met"
                    and set(o.unit_ids) & ancestors
                ]
                if not related:
                    raise ContentError("EVIDENCE_LOCATION_UNAVAILABLE")
                observation_ids.update(o.observation_id for o in related)
                evidence_units.update(u for o in related for u in o.unit_ids if u in ancestors)
            proposal = Proposal(
                recipe=recipe,
                support_refs=(
                    SupportRef(
                        kind="token_observation",
                        task_id=task_id,
                        scope_id=scope_id,
                        request_key=request.request_key,
                        raw_sha256=request.raw_sha256,
                        fragment_id=fragment_id,
                        observation_ids=tuple(sorted(observation_ids)),
                        unit_ids=tuple(sorted(evidence_units)),
                        location_ids=tuple(sorted({units[u].location_id for u in evidence_units})),
                    ),
                ),
                request_targets=tuple(
                    ProposalTarget(location=t.entry.location, parameters_json=t.parameters_json)
                    for t in targets
                )
                if recipe.basis
                else (),
                applicability="matched" if recipe.basis else "advice_only",
                reason_codes=() if recipe.basis else ("RECIPE_BASIS_MISSING",),
            )
            validate_support(proposal, task_id, scope_id, fragment_id, fragment)
            proposals.append(proposal)
        return tuple(proposals)

    def prepare_proposal(
        self, request: RequestView, proposal: Proposal, basis_snapshot: Basis
    ) -> MutationPreparation:
        try:
            return self._prepare(request, proposal, basis_snapshot)
        except (ValueError, ExecutionStopped) as exc:
            return MutationPreparation(
                status="blocked",
                reason_codes=(
                    exc.code
                    if isinstance(exc, (ContentError, ExecutionStopped))
                    else "PREPARATION_FAILED",
                ),
            )

    def _prepare(
        self, request: RequestView, proposal: Proposal, basis_snapshot: Basis
    ) -> MutationPreparation:
        proposal = Proposal.model_validate_json(proposal.model_dump_json())
        if digest(request.raw_body) != request.raw_sha256:
            raise ContentError("EVIDENCE_LOCATION_UNAVAILABLE")
        recipe = proposal.recipe
        validate_recipe(recipe)
        if recipe.basis != basis_snapshot or proposal.applicability != "matched":
            raise ContentError("BASIS_INVALID")
        for support in proposal.support_refs:
            if (support.scope_id, support.request_key, support.raw_sha256) != (
                request.scope_id,
                request.request_key,
                request.raw_sha256,
            ):
                raise ContentError("AUTHORIZATION_SCOPE_MISMATCH")
        control = RunControl(
            BudgetSpec(
                max_request_bytes=8 * 1024 * 1024,
                max_units=10000,
                max_comparison_bytes=8 * 1024 * 1024,
                max_depth=64,
                max_candidates=1000,
                max_encoding_calls=1,
            )
        )
        if recipe.primary_rule == "T3":
            fresh = fresh_duplicate_fragment(request, control)
            support = proposal.support_refs[0]
            rebuilt = duplicate_proposal(
                support.task_id,
                request.scope_id,
                request,
                support.fragment_id or "0",
                fresh,
                recipe,
                control,
            )
            if rebuilt is None or rebuilt.request_targets != proposal.request_targets:
                raise ContentError("AUTHORIZATION_SCOPE_MISMATCH")
            operations: list[PreparedMutation] = []
            for target, target_support in zip(
                rebuilt.request_targets, rebuilt.support_refs, strict=True
            ):
                candidate = authorize_candidate(
                    fresh,
                    target_support.observation_ids[0],
                    target_support.unit_ids[0],
                    recipe.handler_id,
                    recipe.handler_version,
                    target.parameters_json,
                    basis_snapshot.ref,
                )
                result = prepare(request, candidate, target.parameters_json, basis_snapshot.ref)
                if result.status != "prepared":
                    return result
                operations.extend(result.operations)
            return MutationPreparation(status="prepared", operations=tuple(operations))
        selector, generator = parse_config(
            recipe.selector_json,
            recipe.parameter_generator_json,
            recipe.primary_rule,
            recipe.handler_id,
            recipe.handler_version,
        )
        inventory = extract(request, EvidenceCapabilities(), control)
        expected: tuple[ResultTarget, ...] = select_targets(
            request, inventory, selector, generator, control
        )
        # Re-derive the whole selection and parameters; callers cannot widen targets or
        # change a projection/retention operation while reusing a valid basis reference.
        exact = tuple(
            ProposalTarget(location=t.entry.location, parameters_json=t.parameters_json)
            for t in expected
        )
        if not exact or proposal.request_targets != exact:
            raise ContentError("AUTHORIZATION_SCOPE_MISMATCH")
        operations = []
        for target in exact:
            candidate = ModificationCandidate(
                candidate_id=stable_id(
                    "auto_candidate",
                    {
                        "recipe": recipe.model_dump(),
                        "location": target.location.location_id,
                    },
                ),
                finding_refs=(),
                handler_id=recipe.handler_id,
                handler_version=recipe.handler_version,
                action_class="policy_based",
                locations=(target.location,),
                parameters_json=target.parameters_json,
            )
            result = prepare(request, candidate, target.parameters_json, basis_snapshot.ref)
            if result.status != "prepared":
                return result
            operations.extend(result.operations)
        return MutationPreparation(status="prepared", operations=tuple(operations))
