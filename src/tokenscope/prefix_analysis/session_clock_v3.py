"""V3 clock grammar and precise field-local normalization, no business equivalence claim."""

import json
import re
from dataclasses import dataclass
from typing import Any, Literal

from pydantic import Field

from tokenscope.analysis_common.contracts import Contract, TextRange
from tokenscope.prefix_analysis.timestamps import valid_timestamps

OPEN, CLOSE, NORMALIZED = "<session_clock>", "</session_clock>", "NORMALIZED"
TAGS = re.compile(r"</?session_clock\b[^>]*>", re.IGNORECASE)
LABEL = re.compile(
    r"Asia/Shanghai|UTC(?:[+-]\d{1,2}(?::\d{2})?)?|GMT(?:[+-]\d{1,2})?|CST"
    r"|北京时间|当前时间|当前日期|本机时区|当前时区|时区|日期|时间"
    r"|星期[一二三四五六日天]|周[一二三四五六日天]"
    r"|\b(?:current|date|time|timezone|now|local|Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)\b",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class ClockBlock:
    start: int
    inner_start: int
    inner_end: int
    end: int
    dates: tuple[tuple[int, int, str], ...]


@dataclass(frozen=True)
class ClockLocations:
    blocks: tuple[ClockBlock, ...]
    reason_code: str | None = None


def locate_clock_blocks(text: str) -> ClockLocations:
    tags = list(TAGS.finditer(text))
    if not tags:
        malformed = "<session_clock" in text.lower() or "</session_clock" in text.lower()
        return ClockLocations(
            (), "CLOCK_STRUCTURE_UNSUPPORTED" if malformed else "CLOCK_NOT_PRESENT"
        )
    if len(tags) % 2:
        return ClockLocations((), "CLOCK_STRUCTURE_UNSUPPORTED")
    blocks = []
    for left, right in zip(tags[::2], tags[1::2], strict=True):
        if left.group() != OPEN or right.group() != CLOSE:
            return ClockLocations((), "CLOCK_STRUCTURE_UNSUPPORTED")
        inner = text[left.end() : right.start()]
        if "<" in inner or ">" in inner:
            return ClockLocations((), "CLOCK_STRUCTURE_UNSUPPORTED")
        dates = valid_timestamps(inner)
        if inner == NORMALIZED:
            dates = []
        elif not dates:
            return ClockLocations((), "CLOCK_TIME_UNSUPPORTED")
        else:
            remaining, cursor = [], 0
            for start, end, _ in dates:
                remaining.append(inner[cursor:start])
                cursor = end
            remaining.append(inner[cursor:])
            residue = LABEL.sub("", "".join(remaining))
            if re.sub(r"[\s#：:()（）,，.。\[\]{}\-–—]+", "", residue):
                return ClockLocations((), "CLOCK_EXTRA_CONTENT_REQUIRES_REVIEW")
        blocks.append(
            ClockBlock(
                left.start(),
                left.end(),
                right.start(),
                right.end(),
                tuple((a + left.end(), b + left.end(), v) for a, b, v in dates),
            )
        )
    return ClockLocations(tuple(blocks))


def clock_shape(text: str, blocks: tuple[ClockBlock, ...]) -> tuple[str, ...]:
    parts, cursor = [], 0
    for block in blocks:
        parts.append(text[cursor : block.inner_start])
        cursor = block.inner_end
    parts.append(text[cursor:])
    return tuple(parts)


@dataclass(frozen=True)
class ClockField:
    logical_key: str
    pointer: str
    text: str
    locations: ClockLocations


def clock_fields(body: dict[str, Any]) -> tuple[ClockField, ...]:
    fields = []
    ordinals: dict[str, int] = {}
    for index, message in enumerate(body.get("messages", [])):
        if not isinstance(message, dict) or message.get("role") not in ("system", "developer"):
            continue
        role = message["role"]
        ordinal = ordinals.get(role, 0)
        ordinals[role] = ordinal + 1
        content = message.get("content")
        texts = (
            [("", content)]
            if isinstance(content, str)
            else [
                (f"/{i}/text", part["text"])
                for i, part in enumerate(content or [])
                if isinstance(part, dict)
                and part.get("type") == "text"
                and isinstance(part.get("text"), str)
            ]
            if isinstance(content, list)
            else []
        )
        for relative, text in texts:
            key = json.dumps([role, ordinal, relative], separators=(",", ":"))
            fields.append(
                ClockField(
                    key, f"/messages/{index}/content" + relative, text, locate_clock_blocks(text)
                )
            )
    return tuple(fields)


class ClockRecipe3(Contract):
    version: Literal["session-clock-normalize-3.1"] = "session-clock-normalize-3.1"
    discovery: Literal["automatic_l1"] = "automatic_l1"
    logical_field: str
    field_shape: tuple[str, ...]
    block_indices: tuple[int, ...] = Field(min_length=1)
    constant: Literal["NORMALIZED"] = "NORMALIZED"
    business_effect: Literal["changes_time_awareness"] = "changes_time_awareness"


def normalize_clock(field: ClockField, recipe: ClockRecipe3) -> str | None:
    blocks = field.locations.blocks
    if field.logical_key != recipe.logical_field or field.locations.reason_code is not None:
        return None
    if clock_shape(field.text, blocks) != recipe.field_shape:
        return None
    if len(set(recipe.block_indices)) != len(recipe.block_indices) or any(
        i < 0 or i >= len(blocks) for i in recipe.block_indices
    ):
        return None
    result = field.text
    for index in sorted(recipe.block_indices, reverse=True):
        block = blocks[index]
        result = result[: block.inner_start] + NORMALIZED + result[block.inner_end :]
    return result


def date_ranges(block: ClockBlock) -> tuple[TextRange, ...]:
    return tuple(TextRange(start=a, end=b) for a, b, _ in block.dates)
