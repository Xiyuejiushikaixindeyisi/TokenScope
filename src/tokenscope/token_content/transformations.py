"""Explicit, guarded content edits compiled to public atomic primitives."""

import copy
import json
import re
from typing import Literal

from tokenscope.analysis_common.contracts import (
    Location,
    ModificationCandidate,
    PreparedMutation,
    RequestView,
    TargetLocation,
    stable_id,
)
from tokenscope.analysis_common.modifications import value_digest
from tokenscope.analysis_common.plugins import MutationPreparation
from tokenscope.token_content.json_values import (
    PARSER_VERSION,
    ContentError,
    Number,
    Value,
    digest,
    dumps,
    loads,
    pointer_child,
    resolve,
)

HANDLER_VERSION = "1"
HANDLERS = (
    "replace_tool_description",
    "project_result_fields",
    "select_result_items",
    "select_result_lines",
    "replace_payload_with_reference",
    "remove_authorized_duplicate_message",
    "apply_retention_replacements",
)
# Compile has no RunControl argument in H0: explicit hard ceilings bound this pure operation.
COMPILE_MAX_BYTES = 8 * 1024 * 1024
COMPILE_MAX_DEPTH = 64
COMPILE_MAX_TARGETS = 1000


def kind(value: Value) -> Literal["object", "array", "string", "number", "boolean", "null"]:
    if isinstance(value, dict):
        return "object"
    if isinstance(value, list):
        return "array"
    if isinstance(value, str):
        return "string"
    if isinstance(value, Number):
        return "number"
    if isinstance(value, bool):
        return "boolean"
    return "null"


def edit(
    value: Value, pointer: str, replacement: Value, *, remove: bool = False, add: bool = False
) -> Value:
    if not pointer:
        if remove:
            raise ContentError("ROOT_REMOVAL_FORBIDDEN")
        return replacement
    parent_pointer, _, encoded = pointer.rpartition("/")
    parent = resolve(value, parent_pointer)
    key = encoded.replace("~1", "/").replace("~0", "~")
    if isinstance(parent, dict):
        if add and key in parent or not add and key not in parent:
            raise ContentError("TARGET_CONFLICT")
        if remove:
            del parent[key]
        else:
            parent[key] = replacement
    elif isinstance(parent, list) and not add:
        resolve(value, pointer)  # canonical index and bounds
        index = int(key)
        if remove:
            del parent[index]
        else:
            parent[index] = replacement
    else:
        raise ContentError("INVALID_TARGET_CONTAINER")
    return value


def exact_int(parameters: dict[str, Value], key: str) -> int:
    value = parameters.get(key)
    if not isinstance(value, Number) or not re.fullmatch(r"0|[1-9][0-9]*", value.lexeme):
        raise ContentError("EXPLICIT_NONNEGATIVE_INTEGER_REQUIRED")
    return int(value.lexeme)


def replacement(parameters: dict[str, Value]) -> Value:
    raw = parameters.get("replacement_json")
    if not isinstance(raw, str):
        raise ContentError("REPLACEMENT_REQUIRED")
    return loads(raw, max_depth=COMPILE_MAX_DEPTH)


def transform(value: Value, handler: str, parameters: dict[str, Value]) -> Value:
    if handler in ("replace_tool_description", "apply_retention_replacements"):
        result = replacement(parameters)
        if handler == "replace_tool_description" and not isinstance(result, str):
            raise ContentError("DESCRIPTION_MUST_BE_STRING")
        return result
    if handler == "project_result_fields":
        fields = parameters.get("fields")
        if not isinstance(fields, list) or not all(isinstance(f, str) for f in fields):
            raise ContentError("EXPLICIT_FIELDS_REQUIRED")
        level = parameters.get("field_level")
        rows = (
            [value]
            if level == "object"
            else value
            if level == "array_items" and isinstance(value, list)
            else None
        )
        if rows is None or not all(isinstance(row, dict) for row in rows):
            raise ContentError("INVALID_PROJECTION_SHAPE")
        projected: list[Value] = [
            {key: item for key, item in row.items() if key in fields}
            for row in rows
            if isinstance(row, dict)
        ]
        return projected[0] if level == "object" else projected
    if handler in ("select_result_items", "select_result_lines"):
        start, end = exact_int(parameters, "start"), exact_int(parameters, "end")
        if handler == "select_result_items" and isinstance(value, list):
            if start > end or end > len(value):
                raise ContentError("INVALID_RANGE")
            return value[start:end]
        if handler == "select_result_lines" and isinstance(value, str):
            lines = value.splitlines(keepends=True)
            if start > end or end > len(lines):
                raise ContentError("INVALID_RANGE")
            return "".join(lines[start:end])
        raise ContentError("INCOMPATIBLE_OPERATION")
    raise ContentError("UNSUPPORTED_HANDLER")


def reference_edit(
    root: Value, inner: Value, location: Location, parameters: dict[str, Value]
) -> tuple[Value, str]:
    """Conservative v1: top-level string document_ref accepted by current tool Schema."""
    match = re.fullmatch(
        r"/messages/(0|[1-9][0-9]*)/tool_calls/(0|[1-9][0-9]*)/function/arguments",
        location.source_pointer,
    )
    if match is None or location.embedded is None or not isinstance(inner, dict):
        raise ContentError("REFERENCE_TARGET_UNSUPPORTED")
    key_pointer = location.embedded.pointer
    if not re.fullmatch(r"/[^/]+", key_pointer):
        raise ContentError("REFERENCE_TARGET_UNSUPPORTED")
    ref_key, ref_value = parameters.get("reference_key"), parameters.get("reference_value")
    if (
        not isinstance(ref_key, str)
        or not ref_key
        or not isinstance(ref_value, str)
        or not ref_value
    ):
        raise ContentError("REAL_REFERENCE_REQUIRED")
    if not isinstance(parameters.get("protocol_ref"), str) or not parameters["protocol_ref"]:
        raise ContentError("REFERENCE_PROTOCOL_REQUIRED")
    call = resolve(root, f"/messages/{match[1]}/tool_calls/{match[2]}/function")
    assert isinstance(root, dict)
    tools = root.get("tools")
    if not isinstance(call, dict) or not isinstance(tools, list):
        raise ContentError("REFERENCE_SCHEMA_UNPROVEN")
    matches: list[dict[str, Value]] = []
    for tool in tools:
        function = tool.get("function") if isinstance(tool, dict) else None
        if (
            isinstance(tool, dict)
            and isinstance(function, dict)
            and function.get("name") == call.get("name")
        ):
            matches.append(tool)
    if len(matches) != 1:
        raise ContentError("REFERENCE_SCHEMA_UNPROVEN")
    definition = matches[0]
    if parameters.get("tool_identity") != digest(dumps(definition, sort_keys=True)):
        raise ContentError("REFERENCE_SCHEMA_UNPROVEN")
    assert isinstance(definition, dict) and isinstance(definition["function"], dict)
    schema = definition["function"].get("parameters")
    old_key = key_pointer[1:].replace("~1", "/").replace("~0", "~")
    if not isinstance(schema, dict) or schema.get("type") != "object":
        raise ContentError("REFERENCE_SCHEMA_UNPROVEN")
    properties = schema.get("properties")
    required = schema.get("required", [])
    if not isinstance(properties, dict) or not isinstance(required, list) or old_key in required:
        raise ContentError("REFERENCE_SCHEMA_UNPROVEN")
    # Only the explicitly supported unconstrained string schema is validated in v1.
    ref_schema = properties.get(ref_key)
    if (
        not isinstance(ref_schema, dict)
        or ref_schema.get("type") != "string"
        or set(ref_schema) - {"type", "description", "title"}
    ):
        raise ContentError("REFERENCE_SCHEMA_UNSUPPORTED")
    if set(schema) - {
        "type",
        "properties",
        "required",
        "additionalProperties",
        "description",
        "title",
    }:
        raise ContentError("REFERENCE_SCHEMA_UNSUPPORTED")
    new_pointer = pointer_child("", ref_key)
    working = edit(copy.deepcopy(inner), key_pointer, None, remove=True)
    working = edit(working, new_pointer, ref_value, add=True)
    assert isinstance(working, dict)
    if not all(isinstance(key, str) and key in working for key in required):
        raise ContentError("REFERENCE_SCHEMA_UNPROVEN")
    if schema.get("additionalProperties") is False and set(working) - set(properties):
        raise ContentError("REFERENCE_SCHEMA_UNPROVEN")
    return working, new_pointer


def prepare(
    request: RequestView,
    candidate: ModificationCandidate,
    parameters_json: str,
    business_basis_ref: str | None,
) -> MutationPreparation:
    try:
        return _prepare(request, candidate, parameters_json, business_basis_ref)
    except (
        ContentError,
        ValueError,
        TypeError,
        KeyError,
        IndexError,
        OverflowError,
        RecursionError,
    ) as exc:
        return MutationPreparation(
            status="blocked",
            reason_codes=(
                exc.code if isinstance(exc, ContentError) else "INVALID_MODIFICATION_INPUT",
            ),
        )


def _prepare(
    request: RequestView,
    candidate: ModificationCandidate,
    parameters_json: str,
    business_basis_ref: str | None,
) -> MutationPreparation:
    handler = candidate.handler_id
    if handler not in HANDLERS or candidate.handler_version != HANDLER_VERSION:
        raise ContentError("UNSUPPORTED_HANDLER_VERSION")
    if not request.raw_body_complete:
        raise ContentError("INCOMPLETE_BODY")
    if not business_basis_ref:
        raise ContentError("BUSINESS_BASIS_REQUIRED")
    if (
        len(request.raw_body.encode()) + len(parameters_json.encode()) > COMPILE_MAX_BYTES
        or len(candidate.locations) > COMPILE_MAX_TARGETS
    ):
        raise ContentError("COMPILE_BUDGET_EXHAUSTED")
    if not candidate.locations:
        raise ContentError("TARGETS_REQUIRED")
    root = loads(request.raw_body, max_depth=COMPILE_MAX_DEPTH)
    parameters = loads(parameters_json, max_depth=COMPILE_MAX_DEPTH)
    if not isinstance(root, dict) or not isinstance(parameters, dict):
        raise ContentError("INVALID_MODIFICATION_INPUT")
    allowed = {
        "replace_tool_description": {"replacement_json"},
        "apply_retention_replacements": {"replacement_json"},
        "project_result_fields": {"fields", "field_level"},
        "select_result_items": {"start", "end"},
        "select_result_lines": {"start", "end"},
        "replace_payload_with_reference": {
            "reference_key",
            "reference_value",
            "protocol_ref",
            "tool_identity",
        },
        "remove_authorized_duplicate_message": {"authorized"},
    }
    if set(parameters) - allowed[handler]:
        raise ContentError("UNKNOWN_MODIFICATION_PARAMETER")
    # H2 currently serializes outer numbers through stdlib. Refuse unsafe lexemes.
    public_root = json.loads(request.raw_body)
    public_serialized = json.dumps(
        public_root, ensure_ascii=False, allow_nan=False, separators=(",", ":")
    )
    if root != loads(public_serialized, max_depth=COMPILE_MAX_DEPTH):
        raise ContentError("PUBLIC_NUMBER_LEXEME_UNSAFE")
    grouped: dict[str, list[Location]] = {}
    for location in candidate.locations:
        if location.request_key != request.request_key or location.raw_sha256 != request.raw_sha256:
            raise ContentError("MODIFICATION_GUARD_FAILED")
        if location.text_range is not None:
            raise ContentError("TEXT_RANGE_UNSUPPORTED")
        grouped.setdefault(location.source_pointer, []).append(location)
    operations: list[PreparedMutation] = []
    pointers = list(grouped)
    for index, pointer in enumerate(pointers):
        if any(
            pointer.startswith(other + "/") or other.startswith(pointer + "/")
            for other in pointers[:index]
        ):
            raise ContentError("PLAN_OPERATION_CONFLICT")
        locations = grouped[pointer]
        outer = resolve(root, pointer)
        first = locations[0]
        is_embedded = first.embedded is not None
        if any((loc.embedded is not None) != is_embedded for loc in locations):
            raise ContentError("PLAN_OPERATION_CONFLICT")
        if not is_embedded and len(locations) != 1:
            raise ContentError("PLAN_OPERATION_CONFLICT")
        if is_embedded and not isinstance(outer, str):
            raise ContentError("EMBEDDED_STRING_REQUIRED")
        inner = (
            loads(outer, max_depth=COMPILE_MAX_DEPTH)
            if isinstance(outer, str) and is_embedded
            else outer
        )
        working = copy.deepcopy(inner)
        paths: list[str] = []
        source_operations: list[dict[str, object]] = []
        primitive: Literal["replace_value", "remove_value"] = "replace_value"
        for location in locations:
            if location.embedded is not None and location.embedded.parser_version != PARSER_VERSION:
                raise ContentError("PARSER_VERSION_MISMATCH")
            inner_pointer = location.embedded.pointer if location.embedded else ""
            if any(
                inner_pointer == p
                or inner_pointer.startswith(p + "/")
                or p.startswith(inner_pointer + "/")
                for p in paths
            ):
                raise ContentError("PLAN_OPERATION_CONFLICT")
            paths.append(inner_pointer)
            original = resolve(inner, inner_pointer)
            if handler == "remove_authorized_duplicate_message":
                if is_embedded or re.fullmatch(r"/messages/(0|[1-9][0-9]*)", pointer) is None:
                    raise ContentError("MESSAGE_TARGET_REQUIRED")
                if (
                    not isinstance(outer, dict)
                    or outer.get("role") not in ("user", "assistant")
                    or "tool_calls" in outer
                    or "function_call" in outer
                ):
                    raise ContentError("CALL_BEARING_MESSAGE_FORBIDDEN")
                if parameters.get("authorized") is not True:
                    raise ContentError("EXPLICIT_MESSAGE_REMOVAL_REQUIRED")
                content = outer.get("content")
                messages = root.get("messages")
                if (
                    not isinstance(content, str)
                    or not content
                    or not isinstance(messages, list)
                    or not any(
                        isinstance(message, dict)
                        and message.get("role") in ("tool", "function")
                        and message.get("content") == content
                        for message in messages
                    )
                ):
                    raise ContentError("DUPLICATE_MESSAGE_UNPROVEN")
                primitive = "remove_value"
            elif handler == "replace_tool_description":
                if (
                    is_embedded
                    or re.fullmatch(
                        r"/(tools/(0|[1-9][0-9]*)/function|functions/(0|[1-9][0-9]*))/description",
                        pointer,
                    )
                    is None
                    or not isinstance(original, str)
                ):
                    raise ContentError("DESCRIPTION_TARGET_REQUIRED")
                working = transform(original, handler, parameters)
            elif handler == "replace_payload_with_reference":
                if len(locations) != 1:
                    raise ContentError("REFERENCE_SINGLE_REWRITE_REQUIRED")
                working, added = reference_edit(root, inner, location, parameters)
                source_operations.append(
                    {"operation": "add", "pointer": added, "value_guard": "absent"}
                )
            else:
                match = re.fullmatch(
                    r"/messages/(0|[1-9][0-9]*)/content(?:/(0|[1-9][0-9]*)/text)?", pointer
                )
                if match is None:
                    raise ContentError("TOOL_RESULT_TARGET_REQUIRED")
                message = resolve(root, f"/messages/{match[1]}")
                if not isinstance(message, dict) or message.get("role") not in ("tool", "function"):
                    raise ContentError("TOOL_RESULT_TARGET_REQUIRED")
                working = edit(working, inner_pointer, transform(original, handler, parameters))
            source_operations.append(
                {
                    "operation": handler,
                    "pointer": inner_pointer,
                    "original_value_digest": digest(dumps(original, sort_keys=True)),
                }
            )
        new_value: Value = dumps(working) if is_embedded else working
        replacement_json = dumps(new_value) if primitive == "replace_value" else None
        if not is_embedded and replacement_json is not None:
            normalized = json.dumps(
                json.loads(replacement_json),
                allow_nan=False,
                ensure_ascii=False,
                separators=(",", ":"),
            )
            if loads(normalized, max_depth=COMPILE_MAX_DEPTH) != new_value:
                raise ContentError("PUBLIC_NUMBER_LEXEME_UNSAFE")
        target = TargetLocation(
            location=first,
            original_type=kind(resolve(inner, first.embedded.pointer) if first.embedded else outer),
            value_guard=digest(dumps(resolve(inner, first.embedded.pointer), sort_keys=True))
            if first.embedded
            else value_digest(json.loads(dumps(outer))),
            outer_string_guard=digest(outer) if isinstance(outer, str) and is_embedded else None,
        )
        operations.append(
            PreparedMutation(
                operation_id=stable_id(
                    "operation",
                    {
                        "location": first.location_id,
                        "handler": handler,
                        "version": HANDLER_VERSION,
                        "parameters": parameters_json,
                        "basis": business_basis_ref,
                        "source_operations": source_operations,
                    },
                ),
                handler_id=handler,
                handler_version=HANDLER_VERSION,
                target=target,
                public_primitive=primitive,
                replacement_json=replacement_json,
                source_operations_json=json.dumps(source_operations, ensure_ascii=False),
                business_basis_ref=business_basis_ref,
                invariants_json='{"protocol_fields_preserved":true,"source_immutable":true}',
                manifest_fragment_json=json.dumps(
                    {
                        "embedded_reserialized": is_embedded,
                        "numeric_lexemes_preserved": True,
                        "quality_verified": False,
                    }
                ),
            )
        )
    return MutationPreparation(status="prepared", operations=tuple(operations))
