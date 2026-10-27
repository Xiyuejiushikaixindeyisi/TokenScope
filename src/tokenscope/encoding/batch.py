"""Batch fast paths and an on-demand detailed path with identical-ID verification."""

import hashlib
from array import array
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any

from tokenscope.encoding.models import ModelEncoder, RenderedInput
from tokenscope.errors import TokenScopeError
from tokenscope.ingestion.csv_reader import InvalidRow


def ids_bytes(ids: list[int]) -> bytes:
    import sys

    values = array("I", ids)
    if values.itemsize != 4:
        raise RuntimeError("uint32 encoding is unavailable")
    if sys.byteorder != "little":
        values.byteswap()
    return values.tobytes()


def ids_digest(ids: list[int]) -> str:
    return hashlib.sha256(ids_bytes(ids)).hexdigest()


def utf8_ranges(text: str, ranges: Sequence[tuple[int, int]]) -> list[tuple[int, int]]:
    """SDK Python offsets are code points; the public contract uses UTF-8 bytes."""
    positions = sorted({point for pair in ranges for point in pair})
    byte_positions: dict[int, int] = {}
    previous = byte_offset = 0
    for position in positions:
        if position < 0 or position > len(text):
            raise TokenScopeError("INVALID_ENCODING_OFFSET", "Encoder offset is out of bounds", 500)
        byte_offset += len(text[previous:position].encode("utf-8"))
        byte_positions[position] = byte_offset
        previous = position
    return [(byte_positions[start], byte_positions[end]) for start, end in ranges]


@dataclass(frozen=True)
class EncodedRequest:
    json_tokens: int
    prompt_ids: list[int]
    prompt_digest: str
    encoder_identity: str
    light_evidence: dict[str, Any]

    @property
    def prompt_tokens(self) -> int:
        return len(self.prompt_ids)


@dataclass(frozen=True)
class EncodingFailure:
    code: str
    field: str


class EncodingBatchService:
    def __init__(self, encoder: ModelEncoder) -> None:
        self.encoder = encoder

    @staticmethod
    def segments(rendered: RenderedInput) -> list[tuple[str, int, int, bool]]:
        pieces = []
        start = 0
        for left, right in rendered.special_ranges:
            if left < start or right <= left or right > len(rendered.text):
                raise TokenScopeError(
                    "INVALID_SPECIAL_RANGE", "Invalid template control boundary", 500
                )
            pieces.append((rendered.text[start:left], start, left, False))
            pieces.append((rendered.text[left:right], left, right, True))
            start = right
        pieces.append((rendered.text[start:], start, len(rendered.text), False))
        return pieces

    def encode_batch(self, raw_requests: list[str]) -> list[EncodedRequest | EncodingFailure]:
        rendered: list[RenderedInput] = []
        good_indices: list[int] = []
        output: list[EncodedRequest | EncodingFailure] = []
        for index, raw in enumerate(raw_requests):
            try:
                rendered.append(self.encoder.render(raw))
                good_indices.append(index)
                output.append(EncodingFailure("PENDING", "internal"))
            except InvalidRow as exc:
                output.append(EncodingFailure(exc.code, exc.field))
        if not rendered:
            return output
        json_encodings = self.encoder.plain.encode_batch_fast(
            [raw_requests[index] for index in good_indices], add_special_tokens=False
        )
        if self.encoder.recipe is None:
            prompts = self.encoder.full.encode_batch_fast(
                [item.text for item in rendered], add_special_tokens=False
            )
            prompt_ids = [list(item.ids) for item in prompts]
        else:
            # Recipe supplies the actual control boundaries; do not regex-match user literals.
            all_segments = [self.segments(item) for item in rendered]
            plain_texts = [
                text for pieces in all_segments for text, _, _, special in pieces if not special
            ]
            plain_encodings = iter(
                self.encoder.plain.encode_batch_fast(plain_texts, add_special_tokens=False)
            )
            prompt_ids = []
            for pieces in all_segments:
                ids: list[int] = []
                for text, _, _, special in pieces:
                    if special:
                        if text not in self.encoder.added_ids:
                            raise TokenScopeError(
                                "MISSING_SPECIAL_TOKEN",
                                "Template token missing from vocabulary",
                                503,
                            )
                        ids.append(self.encoder.added_ids[text])
                    else:
                        ids.extend(next(plain_encodings).ids)
                prompt_ids.append(ids)
        for position, index in enumerate(good_indices):
            item, ids = rendered[position], prompt_ids[position]
            light = {
                "raw_json_sha256": hashlib.sha256(raw_requests[index].encode()).hexdigest(),
                "rendered_sha256": hashlib.sha256(item.text.encode()).hexdigest(),
                "rendered_characters": len(item.text),
                "rendered_utf8_bytes": len(item.text.encode()),
                "special_ranges": utf8_ranges(item.text, item.special_ranges),
                "special_ranges_unit": "utf8_bytes_half_open",
                "special_ranges_semantics": item.special_ranges_semantics,
                "source_fields": item.source_fields,
                "effective_options": item.effective_options,
                "source_attribution": "references_only_not_additive_token_contributions",
                "source_attribution_status": "partial",
            }
            output[index] = EncodedRequest(
                len(json_encodings[position].ids),
                ids,
                ids_digest(ids),
                self.encoder.identity,
                light,
            )
        return output

    def explain(self, raw: str, expected_digest: str) -> dict[str, Any]:
        rendered = self.encoder.render(raw)
        if self.encoder.recipe is None:
            encoding = self.encoder.full.encode(rendered.text, add_special_tokens=False)
            ids = list(encoding.ids)
            offsets = list(encoding.offsets)
        else:
            ids, offsets = [], []
            for text, left, right, special in self.segments(rendered):
                if special:
                    ids.append(self.encoder.added_ids[text])
                    offsets.append((left, right))
                else:
                    encoding = self.encoder.plain.encode(text, add_special_tokens=False)
                    ids.extend(encoding.ids)
                    offsets.extend((left + begin, left + end) for begin, end in encoding.offsets)
        digest = ids_digest(ids)
        if digest != expected_digest:
            raise TokenScopeError(
                "ENCODING_REPLAY_MISMATCH", "Detailed encoding differs from stored IDs", 409
            )
        return {
            "encoder_identity": self.encoder.identity,
            "ids_digest": digest,
            "ids": ids,
            "prompt_offsets": utf8_ranges(rendered.text, offsets),
            "offset_unit": "utf8_bytes_half_open",
            "special_ranges": utf8_ranges(rendered.text, rendered.special_ranges),
            "source_fields": rendered.source_fields,
            "source_attribution": "unassigned; offsets locate rendered prompt, not raw JSON fields",
            "source_attribution_status": "unknown",
        }
