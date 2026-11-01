from tokenscope.prefix_analysis.history import history_differences, representation_differences


def test_append_is_not_rewrite():
    first = {"messages": [{"role": "user", "content": "hello"}]}
    second = {"messages": [*first["messages"], {"role": "assistant", "content": "world"}]}
    assert history_differences(first, second) == []
    second["messages"][0] = {"role": "user", "content": "changed"}
    assert history_differences(first, second) == ["/messages/0/content"]


def test_exact_structured_representation():
    def body(text):
        return {"messages": [{"role": "tool", "tool_call_id": "c", "content": text}]}

    assert representation_differences(body('{"a":1,"b":2}'), body('{ "b":2, "a":1 }')) == [
        "/messages/0/content"
    ]
    for changed in [
        '{"a":true,"b":2}',
        '{"a":1.0,"b":2}',
        '{"a":1,"a":1,"b":2}',
        '{"a":NaN,"b":2}',
        "ordinary text",
    ]:
        assert representation_differences(body('{"a":1,"b":2}'), body(changed)) == []
    assert representation_differences(body("[1,2]"), body("[2,1]")) == []
