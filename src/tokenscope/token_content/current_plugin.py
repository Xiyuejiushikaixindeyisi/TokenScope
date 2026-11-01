"""Current T2-T4 plugin; token-content-1 remains available for historical execution."""

from tokenscope.analysis_common.contracts import ModificationCandidate, RequestView
from tokenscope.analysis_common.plugins import (
    MutationPreparation,
    PluginDescriptor,
    PluginSelection,
)
from tokenscope.token_content.plugin import TokenContentPlugin


class CurrentTokenContentPlugin(TokenContentPlugin):
    def describe(self) -> PluginDescriptor:
        legacy = super().describe()
        return legacy.model_copy(
            update={
                "version": "token-content-2",
                "rule_versions": tuple(r for r in legacy.rule_versions if r.name != "T1"),
                "handlers": tuple(
                    h for h in legacy.handlers if h.name != "replace_tool_description"
                ),
            }
        )

    def validate_selection(self, selection: PluginSelection) -> PluginSelection:
        if "T1" in selection.rule_ids:
            raise ValueError("T1 is historical only")
        return super().validate_selection(selection)

    def prepare_mutation(
        self,
        request: RequestView,
        candidate: ModificationCandidate,
        parameters_json: str,
        business_basis_ref: str | None,
    ) -> MutationPreparation:
        if candidate.handler_id == "replace_tool_description":
            return MutationPreparation(status="blocked", reason_codes=("RECIPE_RULE_OUT_OF_SCOPE",))
        return super().prepare_mutation(request, candidate, parameters_json, business_basis_ref)
