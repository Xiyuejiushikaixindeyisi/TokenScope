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


def test_identical_and_changed_text_fast_path_matches_original():
    import random

    from tokenscope.prefix_analysis.dynamic import dynamic_recipes, slots_in_text, text_shape

    def original(left, right):
        before, after = slots_in_text(left), slots_in_text(right)
        shape = text_shape(right, after)
        if len(before) != len(after) or text_shape(left, before) != shape:
            return []
        return [
            {"kind": "dynamic_remove", "pattern": b[2], "slot_index": i, "shape": shape}
            for i, (a, b) in enumerate(zip(before, after, strict=True))
            if a[3] != b[3]
        ]

    values = [
        "",
        "中文 😀",
        "same schema " * 100,
        "2026-11-03",
        "/tmp/job-1",
        "x-anthropic-billing-header: cc_version=1; cch=abc;\n",
        "escaped \\ path",
        "2026-11-03 /tmp/a",
    ]
    rng = random.Random(20261103)
    values += [
        f"prefix {rng.randrange(10)} /tmp/job-{rng.randrange(10)} "
        f"2026-11-{rng.randrange(1, 29):02d}"
        for _ in range(24)
    ]
    for left in values:
        for right in values:
            assert dynamic_recipes(left, right) == original(left, right)
