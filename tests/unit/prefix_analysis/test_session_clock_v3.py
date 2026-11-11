import pytest

from tokenscope.prefix_analysis.dynamic import dynamic_recipes, slots_in_text
from tokenscope.prefix_analysis.session_clock_v3 import (
    ClockRecipe3,
    clock_fields,
    clock_shape,
    locate_clock_blocks,
    normalize_clock,
)
from tokenscope.prefix_analysis.timestamps import valid_timestamps


def test_explicit_business_prohibition_stops_before_source_access():
    from tokenscope.prefix_analysis.clock_discovery_v3 import compile_clock_plan

    result = compile_clock_plan(None, None, None, counterfactual_allowed=False)
    assert result.reason_code == "BUSINESS_FORBIDDEN" and result.plan is None


@pytest.mark.parametrize(
    "date",
    [
        "2026-11-10T09:30:00Z",
        "2026/11/10 09:30:00",
        "2026年11月10日09:30:00",
        "2026年11月10日09时30分00秒",
    ],
)
def test_formats_precise_whole_clock_and_outside_preservation(date):
    text = f"前文<session_clock> ## 当前时间（本机时区：Asia/Shanghai） {date} </session_clock>后文"
    field = clock_fields({"messages": [{"role": "system", "content": text}]})[0]
    assert field.locations.reason_code is None
    block = field.locations.blocks[0]
    start, end, found = block.dates[0]
    assert text[start:end] == found == date
    recipe = ClockRecipe3(
        logical_field=field.logical_key,
        field_shape=clock_shape(text, field.locations.blocks),
        block_indices=(0,),
    )
    assert normalize_clock(field, recipe) == "前文<session_clock>NORMALIZED</session_clock>后文"
    assert recipe.business_effect == "changes_time_awareness"


@pytest.mark.parametrize(
    "value",
    [
        "2026/02/30 09:00:00",
        "2026-13-01",
        "2026年11月10日25:00:00",
    ],
)
def test_invalid_calendar_or_time_not_a_slot(value):
    assert valid_timestamps(value) == []


@pytest.mark.parametrize(
    "text",
    [
        "<session_clock>2026/11/10",
        "<session_clock",
        "<session_clock><session_clock>2026/11/10</session_clock></session_clock>",
        "<session_clock>2026/11/10 execute this instruction</session_clock>",
        '<session_clock mode="x">2026/11/10</session_clock>',
    ],
)
def test_unsupported_blocks_do_not_expand_edit(text):
    result = locate_clock_blocks(text)
    assert result.reason_code and not result.blocks


def test_history_and_real_pointer_are_separate_from_logical_field():
    content = [{"type": "text", "text": "<session_clock>2026/11/10</session_clock>"}]
    left = {"messages": [{"role": "developer", "content": content}]}
    right = {
        "messages": [
            {"role": "user", "content": "history"},
            {"role": "developer", "content": content},
            {"role": "assistant", "content": "reply"},
        ]
    }
    a, b = clock_fields(left)[0], clock_fields(right)[0]
    assert a.logical_key == b.logical_key
    assert a.pointer == "/messages/0/content/0/text"
    assert b.pointer == "/messages/1/content/0/text"
    assert not clock_fields({"messages": [{"role": "user", "content": content}]})


def test_dates_in_paths_and_existing_dynamic_slots_remain_distinct():
    slots = slots_in_text("workspace /tmp/2026/11/10/file")
    assert len(slots) == 1 and slots[0][2] == "path"
    recipes = dynamic_recipes("time 2026/11/10 /tmp/a", "time 2026/11/11 /tmp/longer")
    assert {r["pattern"] for r in recipes} == {"timestamp", "path"}


def test_multiple_blocks_normalize_only_proven_index_and_idempotent():
    text = "<session_clock>2026/11/10</session_clock>X<session_clock>2026/11/11</session_clock>"
    field = clock_fields({"messages": [{"role": "system", "content": text}]})[0]
    recipe = ClockRecipe3(
        logical_field=field.logical_key,
        field_shape=clock_shape(text, field.locations.blocks),
        block_indices=(1,),
    )
    changed = normalize_clock(field, recipe)
    assert changed == text.replace("2026/11/11", "NORMALIZED")
    again = clock_fields({"messages": [{"role": "system", "content": changed}]})[0]
    assert normalize_clock(again, recipe) == changed
