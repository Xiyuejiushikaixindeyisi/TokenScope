import json

from tokenscope.prefix_analysis.detection import pair_dynamics
from tokenscope.prefix_analysis.dynamic import (
    apply_recipe,
    dynamic_recipe,
    dynamic_recipes,
    locate_recipe,
)


def test_multiple_dynamic_slots_remain_individually_actionable():
    left = "Time: 2026-10-30 09:00:00 workspace: /tmp/one\nStable"
    right = "Time: 2026-10-31 09:00:00 workspace: /tmp/two\nStable"
    recipes = dynamic_recipes(left, right)
    assert len(recipes) == 2
    assert "/tmp/two" in apply_recipe(right, recipes[0])
    assert "2026-10-31" in apply_recipe(right, recipes[1])


def test_cch_known_header_not_arbitrary_name():
    left = "x-anthropic-billing-header: cc_version=1; cch=one;\nStable prompt"
    right = left.replace("one", "two")
    recipe = dynamic_recipe(left, right)
    assert recipe["pattern"] == "billing_header"
    assert apply_recipe(right, recipe) == "Stable prompt"
    assert dynamic_recipe("Business cch=one", "Business cch=two") is None


def test_business_time_removal_is_an_experiment():
    left = "Time: 2026-10-30 09:00:00\nStable"
    right = "Time: 2026-10-31 09:00:00\nStable"
    recipe = dynamic_recipe(left, right)
    assert apply_recipe(right, recipe) == "Time: \nStable"
    assert apply_recipe("Time: business decision\nStable", recipe) is None
    assert dynamic_recipe(left, "different prompt") is None


def test_tool_path_and_real_source_pointer():
    def body(path):
        return {
            "tools": [
                {
                    "type": "function",
                    "function": {"name": "read", "description": "read file; workspace: " + path},
                }
            ],
            "messages": [],
        }

    before, after = body("/tmp/job-a"), body("/tmp/job-b")
    matches = pair_dynamics(before, after)
    recipe = json.loads(next(item[2] for item in matches if item[2]))
    pointer, old, new = locate_recipe(after, recipe)
    assert pointer == "/tools/0/function/description"
    assert old.endswith("job-b") and new == "read file; workspace: "
    assert any(rule == "L3" and recipe is None for rule, _, recipe in matches)
    assert pair_dynamics({"messages": []}, after) == [("L3", "/tools", None)]
    assert pair_dynamics(before, {"messages": [], "tools": []}) == [("L3", "/tools", None)]
