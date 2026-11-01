"""Strict JSON values preserving number lexemes and source object order."""

import hashlib
import json
import re
from dataclasses import dataclass
from typing import TypeAlias

PARSER_VERSION = "json-exact-1"


class ContentError(ValueError):
    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


@dataclass(frozen=True)
class Number:
    lexeme: str


Value: TypeAlias = "None | bool | str | Number | list[Value] | dict[str, Value]"


def loads(raw: str, *, max_depth: int) -> Value:
    """Bound nesting before invoking the noninterruptible stdlib parser."""
    depth = 0
    quoted = escaped = False
    for char in raw:
        if quoted:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                quoted = False
        elif char == '"':
            quoted = True
        elif char in "[{":
            depth += 1
            if depth > max_depth:
                raise ContentError("ANALYSIS_BUDGET_EXHAUSTED")
        elif char in "]}":
            depth -= 1

    def pairs(items: list[tuple[str, Value]]) -> dict[str, Value]:
        result: dict[str, Value] = {}
        for key, value in items:
            if key in result:
                raise ContentError("INVALID_JSON")
            result[key] = value
        return result

    def constant(_: str) -> None:
        raise ContentError("INVALID_JSON")

    try:
        value: Value = json.loads(
            raw,
            parse_int=Number,
            parse_float=Number,
            parse_constant=constant,
            object_pairs_hook=pairs,
        )
        # Checks escaped surrogate values and keys as well as the raw input.
        dumps(value).encode("utf-8")
        return value
    except RecursionError as exc:
        raise ContentError("ANALYSIS_BUDGET_EXHAUSTED") from exc
    except (ValueError, UnicodeError) as exc:
        if isinstance(exc, ContentError):
            raise
        raise ContentError("INVALID_JSON") from exc


def dumps(value: Value, *, sort_keys: bool = False) -> str:
    if isinstance(value, Number):
        return value.lexeme
    if isinstance(value, str):
        value.encode("utf-8")
        return json.dumps(value, ensure_ascii=False)
    if isinstance(value, list):
        return "[" + ",".join(dumps(v, sort_keys=sort_keys) for v in value) + "]"
    if isinstance(value, dict):
        keys = sorted(value) if sort_keys else value.keys()
        return (
            "{"
            + ",".join(dumps(k) + ":" + dumps(value[k], sort_keys=sort_keys) for k in keys)
            + "}"
        )
    return json.dumps(value, allow_nan=False)


def digest(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def pointer_child(parent: str, key: str | int) -> str:
    return parent + "/" + str(key).replace("~", "~0").replace("/", "~1")


def resolve(value: Value, pointer: str) -> Value:
    if not pointer:
        return value
    if not pointer.startswith("/"):
        raise ContentError("TARGET_NOT_FOUND")
    for encoded in pointer[1:].split("/"):
        if re.search(r"~(?![01])", encoded):
            raise ContentError("TARGET_NOT_FOUND")
        key = encoded.replace("~1", "/").replace("~0", "~")
        if isinstance(value, dict) and key in value:
            value = value[key]
        elif isinstance(value, list) and key.isascii() and key.isdecimal():
            if str(int(key)) != key or int(key) >= len(value):
                raise ContentError("TARGET_NOT_FOUND")
            value = value[int(key)]
        else:
            raise ContentError("TARGET_NOT_FOUND")
    return value
