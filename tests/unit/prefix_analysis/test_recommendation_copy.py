import json

import pytest

from tokenscope.analysis_common.contracts import (
    Location,
    ModificationPlan,
    PreparedMutation,
    RequestComparison,
    RequestKey,
    TargetLocation,
)
from tokenscope.prefix_analysis.recommendation_projection import recipe_copy
from tokenscope.prefix_analysis.service import PrefixFinding


def inputs(rule, path, handler):
    key = RequestKey(base_run_id="r", source_record_index=0)
    finding = PrefixFinding(
        finding_id="f",
        rule_id=rule,
        comparison=RequestComparison(
            left=key,
            right=key,
            left_raw_sha256="a" * 64,
            right_raw_sha256="a" * 64,
            difference_pointers=(path,),
        ),
        source_pointer=path,
        advice="评估删除",
        evidence_status="observed",
        recipe_json=json.dumps({"pattern": "path" if rule == "L3" else "timestamp"}),
    )
    op = PreparedMutation(
        operation_id="o",
        handler_id=handler,
        handler_version="1",
        target=TargetLocation(
            location=Location(request_key=key, raw_sha256="a" * 64, source_pointer=path),
            original_type="string",
            value_guard="b" * 64,
        ),
        public_primitive="replace_value",
        replacement_json='"unchanged remainder"',
    )
    plan = ModificationPlan(
        plan_id="p",
        version="1",
        source_scope_id="s",
        transformation_digest="c" * 64,
        direction="low_hit",
        action_class="hypothetical_content_removal",
        finding_refs=("f",),
        operations=(op,),
    )
    return finding, plan


@pytest.mark.parametrize(
    "rule,path,handler,action",
    [
        ("L1", "/messages/0/content", "low_hit.dynamic_remove", "时间戳片段"),
        ("L2", "/tools", "low_hit.sort_tools", "按工具名称固定排序"),
        ("L3", "/tools/0/function/description", "low_hit.dynamic_remove", "路径片段"),
    ],
)
def test_copy_names_real_location_action_and_condition(rule, path, handler, action):
    finding, plan = inputs(rule, path, handler)
    title, summary = recipe_copy(finding, plan)
    assert "影响" in title and path in summary and action in summary
    assert "评估" not in summary
    assert "前提" in summary or "集合一致" in summary
    if rule == "L3":
        assert "保留其余工具定义" in summary


def test_missing_or_unrecognized_plan_does_not_invent_deletion():
    finding, plan = inputs("L1", "/messages/0/content", "other.handler")
    assert "删除" not in recipe_copy(finding, plan)[1]
    assert "尚无完整修改方案" in recipe_copy(finding, None)[1]
