"""Exact tool identity and structural comparisons, no semantic equivalence guesses."""

from typing import Any

from tokenscope.analysis_common.modifications import value_digest


def tool_map(body: dict[str, Any]) -> dict[str, Any] | None:
    tools = body.get("tools")
    if not isinstance(tools, list) or not tools:
        return None
    result = {}
    for tool in tools:
        if not isinstance(tool, dict) or tool.get("type") != "function":
            return None
        function = tool.get("function")
        if not isinstance(function, dict) or not isinstance(function.get("name"), str):
            return None
        identity = "function:" + function["name"]
        if identity in result:
            return None
        result[identity] = tool
    return result


def tool_set_fingerprint(body: dict[str, Any]) -> str | None:
    mapping = tool_map(body)
    return value_digest(mapping) if mapping is not None else None


def sorted_tools(body: dict[str, Any]) -> list[Any] | None:
    mapping = tool_map(body)
    if mapping is None:
        return None
    return [mapping[key] for key in sorted(mapping, key=lambda key: key.encode("utf-8"))]


def common_prefix(left: list[int], right: list[int]) -> int:
    for i, (a, b) in enumerate(zip(left, right, strict=False)):
        if a != b:
            return i
    return min(len(left), len(right))
