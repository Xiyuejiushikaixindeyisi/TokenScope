"""Lossless JSON pointer spans in Unicode code points, with escaped-string maps."""

import hashlib
import json
import re
from dataclasses import dataclass, field

from tokenscope.analysis_common.contracts import Location
from tokenscope.analysis_common.modifications import pointer_parts
from tokenscope.analysis_common.recommendations import (
    EvidenceSpan,
    LocalEvidence,
    RecommendationBudget,
)


@dataclass
class Node:
    start: int
    end: int
    kind: str
    children: dict[str, "Node"] = field(default_factory=dict)


def parse_spans(raw: str, max_depth: int = 128) -> Node:
    decoder = json.JSONDecoder()

    def skip(i: int) -> int:
        while i < len(raw) and raw[i] in " \r\n\t":
            i += 1
        return i

    def parse(i: int, depth: int) -> Node:
        if depth > max_depth:
            raise ValueError("EVIDENCE_DEPTH_EXHAUSTED")
        i = skip(i)
        start = i
        c = raw[i]
        if c in "[{":
            closing = "}" if c == "{" else "]"
            children: dict[str, Node] = {}
            i = skip(i + 1)
            if raw[i] == closing:
                return Node(start, i + 1, "object" if c == "{" else "array", children)
            while True:
                if c == "{":
                    if raw[i] != '"':
                        raise ValueError("Invalid object key")
                    key, i = decoder.raw_decode(raw, i)
                    i = skip(i)
                    if raw[i] != ":":
                        raise ValueError("Missing colon")
                    i += 1
                else:
                    key = str(len(children))
                if key in children:
                    raise ValueError("EVIDENCE_LOCATION_AMBIGUOUS")
                child = parse(i, depth + 1)
                children[key] = child
                i = skip(child.end)
                if raw[i] == closing:
                    return Node(start, i + 1, "object" if c == "{" else "array", children)
                if raw[i] != ",":
                    raise ValueError("Missing comma")
                i = skip(i + 1)
        if c == '"':
            _, end = decoder.raw_decode(raw, i)
            return Node(start, end, "string")
        match = re.match(
            r"(?:true|false|null|-?(?:0|[1-9][0-9]*)(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?)", raw[i:]
        )
        if not match:
            raise ValueError("Invalid scalar")
        return Node(start, i + len(match[0]), "scalar")

    result = parse(0, 0)
    if skip(result.end) != len(raw):
        raise ValueError("Trailing JSON input")
    return result


def at_pointer(root: Node, pointer: str) -> Node:
    for part in pointer_parts(pointer):
        if root.kind == "array" and not re.fullmatch(r"0|[1-9][0-9]*", part):
            raise ValueError("Invalid array pointer")
        root = root.children[part]
    return root


def decoded_offsets(raw: str, node: Node) -> tuple[str, list[int]]:
    """Map decoded boundaries to original quoted-string content boundaries."""
    if node.kind != "string":
        raise ValueError("Expected JSON string")
    i = node.start + 1
    offsets = [i]
    chunks = []
    while i < node.end - 1:
        end = i + 1
        if raw[i] == "\\":
            end = i + (6 if raw[i + 1] == "u" else 2)
            if raw[i + 1] == "u" and 0xD800 <= int(raw[i + 2 : end], 16) <= 0xDBFF:
                if (
                    raw[end : end + 2] == "\\u"
                    and 0xDC00 <= int(raw[end + 2 : end + 6], 16) <= 0xDFFF
                ):
                    end += 6
        value = json.loads('"' + raw[i:end] + '"')
        if len(value) != 1:
            raise ValueError("Ambiguous decoded mapping")
        chunks.append(value)
        offsets.append(end)
        i = end
    return "".join(chunks), offsets


def locate(raw: str, location: Location, budget: RecommendationBudget) -> LocalEvidence:
    if hashlib.sha256(raw.encode()).hexdigest() != location.raw_sha256:
        raise ValueError("EVIDENCE_SOURCE_DIGEST_MISMATCH")
    try:
        node = at_pointer(parse_spans(raw), location.source_pointer)
        start, end = node.start, node.end
        decoded_span = None
        boundaries: list[int] | None = None
        if location.embedded is not None:
            decoded, offsets = decoded_offsets(raw, node)
            inner = at_pointer(parse_spans(decoded), location.embedded.pointer)
            start, end = offsets[inner.start], offsets[inner.end]
            decoded_span = EvidenceSpan(start=inner.start, end=inner.end)
            boundaries = offsets[inner.start : inner.end + 1]
            if location.text_range is not None:
                text, inner_offsets = decoded_offsets(decoded, inner)
                a, b = location.text_range.start, location.text_range.end
                if b > len(text):
                    raise ValueError("Text range outside decoded value")
                boundaries = [offsets[i] for i in inner_offsets[a : b + 1]]
                start, end = boundaries[0], boundaries[-1]
                decoded_span = EvidenceSpan(start=a, end=b)
        elif node.kind == "string":
            decoded, offsets = decoded_offsets(raw, node)
            boundaries = [node.start, *offsets, node.end]
            if location.text_range is not None:
                a, b = location.text_range.start, location.text_range.end
                if b > len(decoded):
                    raise ValueError("Text range outside decoded value")
                boundaries = offsets[a : b + 1]
                start, end = boundaries[0], boundaries[-1]
                decoded_span = EvidenceSpan(start=a, end=b)
        elif location.text_range is not None:
            raise ValueError("Text range requires string")
        limit = budget.max_excerpt_codepoints
        stop = min(end, start + limit)
        if boundaries is not None:
            stop = max(i for i in boundaries if i <= stop)
        if stop < end:
            # The span describes the displayed raw slice; no full decoded extent on a partial slice.
            decoded_span = None
        context = budget.max_context_codepoints
        return LocalEvidence(
            source=location,
            raw_span=EvidenceSpan(start=start, end=stop),
            decoded_span=decoded_span,
            excerpt=raw[start:stop],
            context_before=raw[max(0, start - context) : start],
            context_after=raw[end : end + context],
            omitted_before=start > context,
            omitted_after=stop < end or end + context < len(raw),
        )
    except (ValueError, KeyError, IndexError, RecursionError) as exc:
        code = (
            "EVIDENCE_LOCATION_AMBIGUOUS"
            if str(exc) == "EVIDENCE_LOCATION_AMBIGUOUS"
            else "EVIDENCE_LOCATION_UNAVAILABLE"
        )
        if str(exc) == "EVIDENCE_DEPTH_EXHAUSTED":
            raise
        return LocalEvidence(source=location, raw_span=None, excerpt="", reason_codes=(code,))
