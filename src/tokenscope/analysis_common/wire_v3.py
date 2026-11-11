"""V3 typed-map decoding extension; the frozen H0 transport stays byte-identical."""

import json
import re
from typing import Any, TypeVar

from tokenscope.analysis_common.contracts import Contract
from tokenscope.analysis_common.wire import to_wire as to_wire
from tokenscope.analysis_common.wire import wire_schema as wire_schema

Model = TypeVar("Model", bound=Contract)


def from_wire(model: type[Model], payload: dict[str, Any]) -> Model:
    schema = model.model_json_schema()

    def restore(value: Any, node: dict[str, Any]) -> Any:
        if "$ref" in node:
            return restore(value, schema["$defs"][node["$ref"].split("/")[-1]])
        if "const" in node and value != node["const"]:
            raise ValueError("Wire constant differs")
        if "enum" in node and value not in node["enum"]:
            raise ValueError("Wire enum differs")
        if node.get("type") == "object" and isinstance(value, dict):
            if any(key not in value for key in node.get("required", ())):
                raise ValueError("Required wire field missing")
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
            extra_schema = node.get("additionalProperties", {})
            if not isinstance(extra_schema, dict):
                extra_schema = {}
            return {
                key: restore(item, node.get("properties", {}).get(key, extra_schema))
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

