"""Versioned decimal-integer wire transport, separate from embedded payload JSON."""

import copy
import json
import re
from typing import Any, TypeVar

from tokenscope.analysis_common.contracts import Contract, metadata_wire

Model = TypeVar("Model", bound=Contract)


def to_wire(model: Contract) -> dict[str, Any]:
    result: dict[str, Any] = metadata_wire(model)
    return result


def from_wire(model: type[Model], payload: dict[str, Any]) -> Model:
    schema = model.model_json_schema()

    def restore(value: Any, node: dict[str, Any]) -> Any:
        if "$ref" in node:
            return restore(value, schema["$defs"][node["$ref"].split("/")[-1]])
        if "anyOf" in node:
            if value is None:
                return None
            errors = []
            for branch in node["anyOf"]:
                if branch.get("type") == "null":
                    continue
                try:
                    return restore(value, branch)
                except ValueError as exc:
                    errors.append(exc)
            raise ValueError("No valid wire alternative") from (errors[0] if errors else None)
        if node.get("type") == "integer":
            if not isinstance(value, str) or not re.fullmatch(r"0|-?[1-9][0-9]*", value):
                raise ValueError("Integer wire field requires canonical decimal string")
            return int(value)
        if node.get("type") == "object" and isinstance(value, dict):
            return {
                key: restore(item, node.get("properties", {}).get(key, {}))
                for key, item in value.items()
            }
        if node.get("type") == "array" and isinstance(value, list):
            prefixes = node.get("prefixItems")
            return [
                restore(
                    item, prefixes[i] if prefixes and i < len(prefixes) else node.get("items", {})
                )
                for i, item in enumerate(value)
            ]
        return value

    return model.model_validate_json(json.dumps(restore(payload, schema), allow_nan=False))


def wire_schema(model: type[Contract]) -> dict[str, Any]:
    schema = copy.deepcopy(model.model_json_schema())

    def visit(node: Any) -> None:
        if isinstance(node, dict):
            if node.get("type") == "integer":
                node["type"] = "string"
                node["pattern"] = r"^(0|-?[1-9][0-9]*)$"
                for key in ("minimum", "maximum", "exclusiveMinimum", "exclusiveMaximum"):
                    if key in node:
                        node["x-integer-" + key] = str(node.pop(key))
                if "default" in node:
                    node["default"] = str(node["default"])
            for item in node.values():
                visit(item)
        elif isinstance(node, list):
            for item in node:
                visit(item)

    visit(schema)
    return schema
