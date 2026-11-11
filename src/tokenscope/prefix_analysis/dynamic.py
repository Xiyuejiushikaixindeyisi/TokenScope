"""Precisely located dynamic slots; syntax retrieves candidates, pairs prove changes."""

import json
import re
from typing import Any

from tokenscope.prefix_analysis.structure import tool_map
from tokenscope.prefix_analysis.timestamps import valid_timestamps

PATTERNS = {
    "timestamp": r"\b\d{4}-\d{2}-\d{2}(?:[T ]\d{2}:\d{2}:\d{2}(?:\.\d+)?Z?)?\b",
    "path": r"(?:[A-Za-z]:\\|/)(?:[^\s\"<>，。；]+)",
}
HEADER = re.compile(r"(?m)^x-anthropic-billing-header:[^\r\n]*\bcch\s*=[^\r\n]*(?:\r?\n|$)")


def strings(value: Any, path: str = "") -> list[tuple[str, str]]:
    output = []
    if isinstance(value, str):
        output.append((path, value))
    elif isinstance(value, dict):
        for key, child in value.items():
            output.extend(strings(child, path + "/" + key.replace("~", "~0").replace("/", "~1")))
    elif isinstance(value, list):
        for i, child in enumerate(value):
            output.extend(strings(child, path + "/" + str(i)))
    return output


def slots_in_text(value: str) -> list[tuple[int, int, str, str]]:
    candidates = [(m.start(), m.end(), "billing_header", m.group()) for m in HEADER.finditer(value)]
    candidates.extend((a, b, "timestamp", text) for a, b, text in valid_timestamps(value))
    for name, pattern in PATTERNS.items():
        if name == "timestamp":
            continue
        candidates.extend(
            (m.start(), m.end(), name, m.group()) for m in re.finditer(pattern, value)
        )
    selected: list[tuple[int, int, str, str]] = []
    for match in sorted(candidates, key=lambda item: (item[0], -(item[1] - item[0]))):
        if not selected or match[0] >= selected[-1][1]:
            selected.append(match)
    return selected


def text_shape(value: str, slots: list[tuple[int, int, str, str]]) -> list[str]:
    shape: list[str] = []
    start = 0
    for left, right, kind, _ in slots:
        shape.extend((value[start:left], kind))
        start = right
    shape.append(value[start:])
    return shape


def dynamic_recipes(left: str, right: str) -> list[dict[str, Any]]:
    if left == right:
        return []
    before, after = slots_in_text(left), slots_in_text(right)
    shape = text_shape(right, after)
    if len(before) != len(after) or text_shape(left, before) != shape:
        return []
    return [
        {"kind": "dynamic_remove", "pattern": b[2], "slot_index": i, "shape": shape}
        for i, (a, b) in enumerate(zip(before, after, strict=True))
        if a[3] != b[3]
    ]


def dynamic_recipe(left: str, right: str) -> dict[str, Any] | None:
    recipes = dynamic_recipes(left, right)
    return recipes[0] if recipes else None


def apply_recipe(value: str, recipe: dict[str, Any]) -> str | None:
    slots = slots_in_text(value)
    if text_shape(value, slots) != recipe["shape"]:
        return None
    index = recipe["slot_index"]
    if type(index) is not int or not 0 <= index < len(slots):
        return None
    left, right, kind, _ = slots[index]
    if kind != recipe["pattern"]:
        return None
    return value[:left] + value[right:]


def comparable_slots(body: dict[str, Any]) -> dict[str, tuple[str, str]]:
    """Logical tool names permit order changes; source paths retain actual indices."""
    slots = {}
    for i, message in enumerate(body.get("messages", [])):
        if message.get("role") in ("system", "developer"):
            for path, text in strings(message.get("content"), f"/messages/{i}/content"):
                slots["L1:" + path] = (path, text)
    mapping = tool_map(body)
    if mapping is not None:
        for i, tool in enumerate(body["tools"]):
            name = tool["function"]["name"]
            for path, text in strings(tool, f"/tools/{i}"):
                # Names/types/actual enum constraints are not silently treated as prose.
                if path.endswith("/description"):
                    relative = "/".join(path.split("/")[3:])
                    slots["L3:" + json.dumps([name, relative])] = (path, text)
    return slots


def locate_recipe(body: dict[str, Any], recipe: dict[str, Any]) -> tuple[str, str, str] | None:
    slots = comparable_slots(body)
    target = slots.get(recipe["slot_key"])
    if target is None:
        return None
    path, value = target
    changed = apply_recipe(value, recipe)
    return (path, value, changed) if changed is not None else None


def field_differences(left: Any, right: Any, path: str = "") -> list[str]:
    output: list[str] = []
    if type(left) is not type(right):
        return [path]
    if isinstance(left, dict):
        output = []
        for key in sorted(set(left) | set(right)):
            pointer = path + "/" + key.replace("~", "~0").replace("/", "~1")
            output.extend(
                [pointer]
                if key not in left or key not in right
                else field_differences(left[key], right[key], pointer)
            )
        return output
    if isinstance(left, list):
        output = []
        for i in range(max(len(left), len(right))):
            pointer = path + "/" + str(i)
            output.extend(
                [pointer]
                if i >= len(left) or i >= len(right)
                else field_differences(left[i], right[i], pointer)
            )
        return output
    return [] if left == right else [path]
