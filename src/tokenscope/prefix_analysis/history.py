"""History and structured representation differences, without invented chain identity."""

import json
from typing import Any

from tokenscope.analysis_common.contracts import checked_json
from tokenscope.prefix_analysis.dynamic import field_differences


def structured_json(value: str) -> Any:
    checked_json(value)
    return json.loads(
        value, parse_int=lambda text: ("number", text), parse_float=lambda text: ("number", text)
    )


def history_differences(left: dict[str, Any], right: dict[str, Any]) -> list[str]:
    before, after = left.get("messages", []), right.get("messages", [])
    output: list[str] = []
    for i in range(min(len(before), len(after))):
        output.extend(field_differences(before[i], after[i], f"/messages/{i}"))
    if len(after) < len(before):
        output.extend(f"/messages/{i}" for i in range(len(after), len(before)))
    return output


def representation_differences(left: dict[str, Any], right: dict[str, Any]) -> list[str]:
    output = []
    for i, (a, b) in enumerate(
        zip(left.get("messages", []), right.get("messages", []), strict=False)
    ):
        if a.get("role") != "tool" or b.get("role") != "tool":
            continue
        x, y = a.get("content"), b.get("content")
        if not isinstance(x, str) or not isinstance(y, str) or x == y:
            continue
        try:
            xv, yv = structured_json(x), structured_json(y)
        except (ValueError, UnicodeError, RecursionError):
            continue
        if isinstance(xv, (dict, list)) and type(xv) is type(yv) and xv == yv:
            output.append(f"/messages/{i}/content")
    return output
