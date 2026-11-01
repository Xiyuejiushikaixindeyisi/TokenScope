from test_diagnostic_tasks import options, setup

from tokenscope.analysis_common.recommendation_publication import publish_low_hit
from tokenscope.analysis_common.recommendations import RecommendationBudget
from tokenscope.analysis_common.storage import ResultWriter, read_items


def test_existing_real_replay_projects_one_recipe_and_local_examples(service, tmp_path):
    diagnostics, request = setup(service, low_hit=True)
    task = diagnostics.submit(request, options(max_encoding_calls=500))
    result = diagnostics.process_next()
    assert result is not None and result.status in ("ready", "partial")
    source = diagnostics.source(diagnostics.store.row(task.task_id))
    workspace = tmp_path / "projection"
    workspace.mkdir()
    writer = ResultWriter(workspace)
    for kind in ("finding", "plan", "evaluation"):
        for item in diagnostics.items(task.task_id, kind):
            writer.add(kind, item["id"], item["data"])
    n, d = publish_low_hit(source, writer, task.task_id, RecommendationBudget(), True)
    writer.close()
    assert n >= 1
    recs = read_items(workspace, "recommendation", None, 0, 100)
    assert len(recs) == n
    cards = [
        r["data"] for r in recs if r["data"]["display_qualification"] == "low_hit_optimization"
    ]
    assert cards
    for card in cards:
        assert card["impact"]["total_requests"] == "6"
        assert card["impact"]["modified_requests"] == card["evaluation"]["modified_after"]["n"]
        assert len(card["example_refs"]) <= 3
    examples = read_items(workspace, "recommendation_example", None, 0, 100)
    assert examples
    for item in examples:
        assert len(item["data"]["before"]["excerpt"]) <= 1024
        assert "raw_body" not in item["data"]
