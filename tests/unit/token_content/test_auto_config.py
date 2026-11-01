"""Synthetic policies validate engineering behavior, not production authorization."""

import json

import pytest

from tokenscope.token_content.auto_config import (
    RetentionGenerator,
    parameters_for,
    parse_config,
    retention_indices,
)
from tokenscope.token_content.json_values import ContentError, dumps, loads
from tokenscope.token_content.transformations import transform


def config(kind="project_fields", **updates):
    selector = {
        "version": "token-result-selector-1",
        "appid": "synthetic-app",
        "tool_name": "synthetic-search",
        "tool_identity": "a" * 64,
        "representation": "structural_json",
        "embedded_pointer": "",
    }
    generator = {
        "version": "token-result-generator-1",
        "kind": kind,
        "omission_permitted": True,
    }
    if kind == "project_fields":
        generator.update(fields=["id"], field_level="object")
    elif kind == "retain_last":
        generator.update(keep_last=1, replacement_json='{"omitted":true}')
    else:
        generator.update(side="first", count=2)
    if kind == "select_lines":
        selector.update(representation="text", embedded_pointer=None)
    generator.update(updates)
    handler = {
        "project_fields": "project_result_fields",
        "select_items": "select_result_items",
        "select_lines": "select_result_lines",
        "retain_last": "apply_retention_replacements",
    }[kind]
    return [
        json.dumps(selector),
        json.dumps(generator),
        "T4" if kind == "retain_last" else "T2",
        handler,
        "1",
    ]


@pytest.mark.parametrize(
    "kind,raw,expected",
    [
        ("project_fields", '{"id":9007199254740993,"extra":1}', '{"id":9007199254740993}'),
        ("select_items", "[1e2,-0,3]", "[1e2,-0]"),
        ("select_lines", '"a\\r\\nb\\nc"', '"a\\r\\nb\\n"'),
        ("retain_last", '{"old":1}', '{"omitted":true}'),
    ],
)
def test_parameters_execute_existing_handlers(kind, raw, expected):
    args = config(kind)
    _, generator = parse_config(*args)
    value = loads(raw, max_depth=32)
    parameters = loads(parameters_for(generator, value), max_depth=32)
    assert isinstance(parameters, dict)
    assert dumps(transform(value, args[3], parameters)) == expected


@pytest.mark.parametrize(
    "updates",
    [
        {"omission_permitted": False},
        {"omission_permitted": 1},
        {"omission_permitted": "true"},
        {"fields": ["id", "id"]},
        {"fields": []},
        {"unknown": 1},
        {"version": "future"},
        {"kind": "replace_tool_description"},
    ],
)
def test_bad_config_rejected(updates):
    args = config()
    generator = json.loads(args[1])
    generator.update(updates)
    args[1] = json.dumps(generator)
    with pytest.raises(ValueError):
        parse_config(*args)


@pytest.mark.parametrize("index,value", [(2, "T1"), (2, "T3"), (3, "other"), (4, "2")])
def test_rule_handler_version_is_bound(index, value):
    args = config()
    args[index] = value
    with pytest.raises(ValueError):
        parse_config(*args)


def test_duplicate_keys_and_unbounded_configuration_rejected():
    args = config()
    args[1] = args[1][:-1] + ',"kind":"select_items"}'
    with pytest.raises(ContentError):
        parse_config(*args)
    args = config()
    args[0] = " " * 262145
    with pytest.raises(ContentError):
        parse_config(*args)


@pytest.mark.parametrize("count", [-1, True, "2", 2.5])
def test_counts_are_exact_nonnegative_integers(count):
    with pytest.raises(ValueError):
        parse_config(*config("select_items", count=count))


@pytest.mark.parametrize(
    "side,count,expected",
    [
        ("first", 0, (0, 0)),
        ("last", 0, (3, 3)),
        ("last", 1, (2, 3)),
        ("first", 99, (0, 3)),
        ("last", 99, (0, 3)),
    ],
)
def test_ranges_are_bounded(side, count, expected):
    _, generator = parse_config(*config("select_items", side=side, count=count))
    assert json.loads(parameters_for(generator, [None] * 3)) == dict(
        zip(("start", "end"), expected, strict=True)
    )


def test_retention_zero_keeps_none_and_large_k_keeps_all():
    for keep, expected in [(0, [0, 1, 2]), (1, [0, 1]), (5, [])]:
        _, generator = parse_config(*config("retain_last", keep_last=keep))
        assert isinstance(generator, RetentionGenerator)
        assert list(retention_indices(3, generator)) == expected


def test_retention_requires_complete_container_and_typed_replacement():
    args = config("retain_last")
    selector = json.loads(args[0])
    selector["embedded_pointer"] = "/inner"
    args[0] = json.dumps(selector)
    with pytest.raises(ValueError):
        parse_config(*args)
    selector.update(representation="text", embedded_pointer=None)
    args[0] = json.dumps(selector)
    with pytest.raises(ValueError):
        parse_config(*args)


def test_projection_never_silently_drops_nonobject_rows():
    _, generator = parse_config(*config(field_level="array_items"))
    with pytest.raises(ContentError):
        parameters_for(generator, [{"id": None}, None])
