"""Guarded, atomic in-memory mutations of copies, never of source evidence."""

import copy
import hashlib
import json
import re
from typing import Any

from tokenscope.analysis_common.contracts import PreparedMutation, RequestView, checked_json
from tokenscope.domain import ModelSettings
from tokenscope.errors import TokenScopeError
from tokenscope.ingestion.csv_reader import validate_request


def value_digest(value: Any) -> str:
    """Structural guard v1; types are preserved (unlike metadata integer wire encoding)."""
    raw = json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False
    )
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def pointer_parts(pointer: str) -> tuple[str, ...]:
    return (
        tuple(part.replace("~1", "/").replace("~0", "~") for part in pointer.split("/")[1:])
        if pointer
        else ()
    )


def at(value: Any, parts: tuple[str, ...]) -> Any:
    for part in parts:
        if isinstance(value, list):
            if not re.fullmatch(r"0|[1-9][0-9]*", part):
                raise ValueError("Invalid array index")
            value = value[int(part)]
        elif isinstance(value, dict):
            value = value[part]
        else:
            raise ValueError("Pointer does not address a container")
    return value


def apply_mutations(
    request: RequestView,
    operations: tuple[PreparedMutation, ...],
    settings: ModelSettings,
) -> tuple[str, list[dict[str, Any]]]:
    if not operations:
        return request.raw_body, []
    checked_json(request.raw_body)
    original = json.loads(request.raw_body)
    # Never change unrelated numeric lexemes as a side-effect of field serialization.
    lexical: dict[str, Any] = dict(
        parse_int=lambda text: ("number", text), parse_float=lambda text: ("number", text)
    )
    normalized = json.dumps(original, ensure_ascii=False, separators=(",", ":"), allow_nan=False)
    if json.loads(request.raw_body, **lexical) != json.loads(normalized, **lexical):
        raise TokenScopeError(
            "PUBLIC_NUMBER_LEXEME_UNSAFE", "Numeric serialization would change source", 422
        )
    working = copy.deepcopy(original)
    targets: list[tuple[tuple[str, ...], PreparedMutation]] = []
    seen: dict[tuple[str, ...], PreparedMutation] = {}
    for operation in operations:
        target = operation.target
        location = target.location
        if location.request_key != request.request_key or location.raw_sha256 != request.raw_sha256:
            raise TokenScopeError("MODIFICATION_GUARD_FAILED", "Source target differs", 409)
        parts = pointer_parts(location.source_pointer)
        if not parts:
            raise TokenScopeError(
                "UNSUPPORTED_OPERATION", "Whole request replacement is forbidden", 422
            )
        if location.text_range is not None:
            raise TokenScopeError(
                "UNCOMPILED_OPERATION", "Compile text range to guarded field", 422
            )
        if parts in seen:
            prior = seen[parts]
            if (prior.public_primitive, prior.replacement_json, prior.target) == (
                operation.public_primitive,
                operation.replacement_json,
                operation.target,
            ):
                continue
            raise TokenScopeError("PLAN_OPERATION_CONFLICT", "Same target conflicts", 409)
        if any(parts[: len(other)] == other or other[: len(parts)] == parts for other in seen):
            raise TokenScopeError("PLAN_OPERATION_CONFLICT", "Overlapping targets", 409)
        parent = at(original, parts[:-1])
        absent = isinstance(parent, dict) and parts[-1] not in parent
        value = None if absent else at(original, parts)
        if location.embedded is not None:
            if (
                not isinstance(value, str)
                or hashlib.sha256(value.encode("utf-8")).hexdigest() != target.outer_string_guard
                or operation.public_primitive != "replace_value"
                or not isinstance(json.loads(operation.replacement_json or "null"), str)
            ):
                raise TokenScopeError(
                    "MODIFICATION_GUARD_FAILED", "Embedded outer guard failed", 409
                )
        elif absent:
            if target.value_guard != "absent" or operation.public_primitive != "replace_value":
                raise TokenScopeError(
                    "MODIFICATION_GUARD_FAILED", "Absent target guard failed", 409
                )
        elif target.value_guard == "absent" or value_digest(value) != target.value_guard:
            raise TokenScopeError("MODIFICATION_GUARD_FAILED", "Original value guard failed", 409)
        if (
            operation.public_primitive == "remove_value"
            and len(parts) == 2
            and parts[0] == "messages"
        ):
            if (
                not isinstance(value, dict)
                or value.get("role") in ("tool", "function")
                or value.get("tool_calls")
                or value.get("function_call")
            ):
                raise TokenScopeError(
                    "UNSUPPORTED_OPERATION", "Cannot remove call-bearing message", 422
                )
        seen[parts] = operation
        targets.append((parts, operation))
    # All locations/guards resolved against original; replacements precede descending deletions.
    manifest: list[dict[str, Any]] = []
    for parts, operation in targets:
        if operation.public_primitive == "remove_value":
            continue
        value = json.loads(operation.replacement_json or "null")
        if json.loads(operation.replacement_json or "null", **lexical) != json.loads(
            json.dumps(value, ensure_ascii=False, allow_nan=False), **lexical
        ):
            raise TokenScopeError(
                "PUBLIC_NUMBER_LEXEME_UNSAFE", "Numeric replacement is not lossless", 422
            )
        parent = at(working, parts[:-1])
        if isinstance(parent, list):
            parent[int(parts[-1])] = value
        else:
            parent[parts[-1]] = value
    deletes = [(parts, op) for parts, op in targets if op.public_primitive == "remove_value"]
    deletes.sort(
        key=lambda pair: (
            pair[0][:-1],
            int(pair[0][-1]) if isinstance(at(original, pair[0][:-1]), list) else 0,
        ),
        reverse=True,
    )
    for parts, _ in deletes:
        parent = at(working, parts[:-1])
        del parent[int(parts[-1]) if isinstance(parent, list) else parts[-1]]
    for _parts, operation in targets:
        manifest.append(
            {
                "operation_id": operation.operation_id,
                "source_pointer": operation.target.location.source_pointer,
                "source_operations_json": operation.source_operations_json,
                "handler_id": operation.handler_id,
                "handler_version": operation.handler_version,
                "primitive": operation.public_primitive,
                "original_raw_sha256": request.raw_sha256,
                "target_guard": operation.target.value_guard,
                "outer_string_guard": operation.target.outer_string_guard,
                "invariants_json": operation.invariants_json,
                "manifest_fragment_json": operation.manifest_fragment_json,
            }
        )
    raw = json.dumps(working, ensure_ascii=False, separators=(",", ":"), allow_nan=False)
    if raw == json.dumps(original, ensure_ascii=False, separators=(",", ":"), allow_nan=False):
        return request.raw_body, []
    validate_request(raw, settings)
    for change in manifest:
        change["after_raw_sha256"] = hashlib.sha256(raw.encode("utf-8")).hexdigest()
        change["serialization_version"] = "json-preserve-order-1"
        change["protocol_validated"] = True
    return raw, manifest
