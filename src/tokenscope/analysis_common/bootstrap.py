"""Only explicit app/worker registration enables diagnostic task processing."""

import os
from pathlib import Path

from tokenscope.analysis_common.plugins import PluginRegistry
from tokenscope.analysis_common.proposal_plugins import ProposalRegistry
from tokenscope.analysis_common.recommendation_runtime import RecommendationSettings
from tokenscope.analysis_common.recommendations import RecipeBundle
from tokenscope.analysis_common.service import DiagnosticService
from tokenscope.analysis_common.source import SourceResolver
from tokenscope.monitoring.service import MonitoringService
from tokenscope.token_content.auto_proposals import TokenProposalAdapter
from tokenscope.token_content.current_plugin import CurrentTokenContentPlugin
from tokenscope.user_monitoring.service import UserRunService


def build_diagnostics(base: MonitoringService, user: UserRunService) -> DiagnosticService:
    registry = PluginRegistry()
    registry.register(CurrentTokenContentPlugin())
    proposals = ProposalRegistry()
    proposals.register(TokenProposalAdapter())
    path = os.environ.get("TOKENSCOPE_RECOMMENDATION_BUNDLE")
    bundle: RecipeBundle | Path = (
        Path(path)
        if path
        else RecipeBundle(bundle_id="no-business-recipes-configured", revision="1", recipes=())
    )
    return DiagnosticService(
        SourceResolver(base, user), registry, RecommendationSettings(proposals, bundle)
    )
