from tokenscope.analysis_common.contracts import RequestKey
from tokenscope.prefix_analysis.candidates import CandidateIndex
from tokenscope.prefix_analysis.structure import common_prefix, sorted_tools, tool_set_fingerprint


def tool(name, description="stable"):
    return {
        "type": "function",
        "function": {
            "name": name,
            "description": description,
            "parameters": {"type": "object", "properties": {}},
        },
    }


def test_sets_and_order():
    a, b = tool("a"), tool("b")
    assert tool_set_fingerprint({"tools": [a, b]}) == tool_set_fingerprint({"tools": [b, a]})
    assert sorted_tools({"tools": [b, a]}) == [a, b]
    assert tool_set_fingerprint({"tools": [a, tool("b", "changed")]}) != tool_set_fingerprint(
        {"tools": [a, b]}
    )
    assert sorted_tools({"tools": [a, a]}) is None
    assert common_prefix([1, 2], [1, 2, 3]) == 2
    assert common_prefix([1, 2], [1, 3]) == 1


def test_predecessors_and_explicit_partial(tmp_path):
    index = CandidateIndex(tmp_path / "index.sqlite3", "run", 1)
    assert index.lookup("tools", "set") == ((), False)
    first = RequestKey(base_run_id="run", source_record_index=9)
    second = RequestKey(base_run_id="run", source_record_index=1)
    index.insert(first, {"tools": "set"})
    assert index.lookup("tools", "set") == ((first,), False)
    index.insert(second, {"tools": "set"})
    assert index.lookup("tools", "set") == ((second,), True)
    index.close()
