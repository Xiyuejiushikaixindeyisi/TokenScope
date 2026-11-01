import json

import pytest

from tokenscope.analysis_common.source import SourceResolver


@pytest.mark.parametrize("candidate_limit,expected", [(1, "partial"), (16, "ready")])
def test_member_coverage_separate_from_full_evaluation(
    service, tmp_path, candidate_limit, expected
):
    from test_diagnostic_tasks import options, setup

    from tokenscope.analysis_common.plugins import PluginRegistry
    from tokenscope.analysis_common.proposal_plugins import ProposalRegistry
    from tokenscope.analysis_common.recommendation_runtime import RecommendationSettings
    from tokenscope.analysis_common.recommendations import RecipeBundle
    from tokenscope.analysis_common.service import DiagnosticService
    from tokenscope.token_content.auto_proposals import TokenProposalAdapter
    from tokenscope.token_content.current_plugin import CurrentTokenContentPlugin

    _, request = setup(service, low_hit=True)
    plugins = PluginRegistry()
    plugins.register(CurrentTokenContentPlugin())
    proposals = ProposalRegistry()
    proposals.register(TokenProposalAdapter())
    d = DiagnosticService(
        SourceResolver(service),
        plugins,
        RecommendationSettings(
            proposals, RecipeBundle(bundle_id="review-empty", revision="1", recipes=())
        ),
    )
    task = d.submit(request, options(candidate_limit=candidate_limit, max_encoding_calls=500))
    assert d.process_next().status == expected
    report = d.report(task.task_id)
    recs = [
        x["data"]
        for x in d.items(task.task_id, "recommendation")
        if x["data"]["direction"] == "low_hit"
    ]
    (tmp_path / "partial.json").write_text(
        json.dumps({"report": report, "recommendations": recs}, ensure_ascii=False, indent=2)
    )
    assert recs
    assert all(r["members_complete"] == (expected == "ready") for r in recs)
    assert all(r["impact"]["evaluation_complete"] for r in recs)
    assert all(r["impact"]["total_requests"] == "6" for r in recs)
    assert all(r["impact"]["modified_requests"] == "6" for r in recs)
