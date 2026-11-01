import hashlib
import json

import pytest

from tokenscope.analysis_common.contracts import (
    BaselineMetrics,
    Location,
    PreparedMutation,
    RequestKey,
    RequestView,
    TargetLocation,
)
from tokenscope.analysis_common.modifications import apply_mutations, value_digest
from tokenscope.domain import DEFAULT_SETTINGS
from tokenscope.errors import TokenScopeError


def request(body):
    raw = json.dumps(body, ensure_ascii=False, indent=2)
    return RequestView(
        request_key=RequestKey(base_run_id="r", source_record_index=1),
        scope_id="scope",
        appid="a",
        time_ns=1,
        hash_id="h",
        raw_body=raw,
        raw_sha256=hashlib.sha256(raw.encode()).hexdigest(),
        raw_body_complete=True,
        baseline_metrics=BaselineMetrics(j=0, p=0),
        encoder_identity="e",
        asset_identity="a",
        effective_options_json="{}",
    )


def operation(view, path, old, replacement=None, remove=False):
    kind = "object" if isinstance(old, dict) else "array" if isinstance(old, list) else "string"
    return PreparedMutation(
        operation_id=path,
        handler_id="test",
        handler_version="1",
        target=TargetLocation(
            location=Location(
                request_key=view.request_key, raw_sha256=view.raw_sha256, source_pointer=path
            ),
            original_type=kind,
            value_guard=value_digest(old),
        ),
        public_primitive="remove_value" if remove else "replace_value",
        replacement_json=None if remove else json.dumps(replacement),
    )


def test_unrelated_numeric_lexemes_are_never_silently_changed():
    view = request({"messages": [{"role": "user", "content": "old"}], "value": 10.0})
    raw = view.raw_body.replace("10.0", "1e1")
    view = view.model_copy(
        update={"raw_body": raw, "raw_sha256": hashlib.sha256(raw.encode()).hexdigest()}
    )
    op = operation(view, "/messages/0/content", "old", "new")
    with pytest.raises(TokenScopeError, match="Numeric serialization"):
        apply_mutations(view, (op,), DEFAULT_SETTINGS["GLM-5.2"])
    assert apply_mutations(view, (), DEFAULT_SETTINGS["GLM-5.2"])[0] == raw


def test_original_array_coordinates_and_no_source_change():
    messages = [{"role": "user", "content": str(i)} for i in range(5)]
    view = request({"messages": messages})
    ops = (
        operation(view, "/messages/1", messages[1], remove=True),
        operation(view, "/messages/3", messages[3], remove=True),
        operation(view, "/messages/4/content", "4", "last"),
    )
    raw, changes = apply_mutations(view, ops, DEFAULT_SETTINGS["GLM-5.2"])
    assert [m["content"] for m in json.loads(raw)["messages"]] == ["0", "2", "last"]
    assert len(changes) == 3
    assert json.loads(view.raw_body)["messages"] == messages


def test_parent_child_conflict_and_guard_are_atomic():
    messages = [{"role": "user", "content": "hello"}]
    view = request({"messages": messages})
    ops = (
        operation(view, "/messages", messages, []),
        operation(view, "/messages/0/content", "hello", "changed"),
    )
    with pytest.raises(TokenScopeError, match="Overlapping"):
        apply_mutations(view, ops, DEFAULT_SETTINGS["GLM-5.2"])
    with pytest.raises(TokenScopeError, match="guard"):
        apply_mutations(
            view,
            (operation(view, "/messages/0/content", "wrong", "changed"),),
            DEFAULT_SETTINGS["GLM-5.2"],
        )
    assert json.loads(view.raw_body)["messages"] == messages


def test_protocol_call_message_cannot_be_removed():
    messages = [
        {"role": "user", "content": "hello"},
        {"role": "tool", "tool_call_id": "call1", "content": "result"},
    ]
    view = request({"messages": messages})
    with pytest.raises(TokenScopeError, match="call-bearing"):
        apply_mutations(
            view,
            (operation(view, "/messages/1", messages[1], remove=True),),
            DEFAULT_SETTINGS["GLM-5.2"],
        )


def test_noop_preserves_original_bytes():
    view = request({"messages": [{"role": "user", "content": "你好"}]})
    raw, changes = apply_mutations(
        view, (operation(view, "/messages/0/content", "你好", "你好"),), DEFAULT_SETTINGS["GLM-5.2"]
    )
    assert raw == view.raw_body and changes == []
    assert value_digest(1) != value_digest("1") != value_digest(True)
