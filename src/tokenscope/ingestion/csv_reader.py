"""Bounded batch ingestion; record errors and file errors have distinct semantics."""

import csv
import io
import json
import math
import re
from collections.abc import Iterator
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Any, BinaryIO

from tokenscope.domain import ModelSettings
from tokenscope.errors import TokenScopeError

REQUIRED_COLUMNS = (
    "hash_id",
    "appid",
    "model_handle_start_time",
    "completion_tokens",
    "request_input",
)
TIME_PATTERN = re.compile(
    r"^(\d{4}-\d{2}-\d{2})[T ](\d{2}:\d{2}:\d{2})(?:\.(\d{1,9}))?"
    r"(Z|[+-]\d{2}:\d{2})?$"
)
EPOCH = datetime(1970, 1, 1, tzinfo=UTC)


class InvalidRow(ValueError):
    def __init__(self, code: str, field: str) -> None:
        self.code = code
        self.field = field
        super().__init__(code)


@dataclass(frozen=True)
class RowIssue:
    source_record_index: int
    physical_line_start: int
    physical_line_end: int
    code: str
    field: str


@dataclass(frozen=True)
class RequestRecord:
    source_record_index: int
    physical_line_start: int
    physical_line_end: int
    hash_id: str
    appid: str
    time_ns: int
    time_utc: str
    completion_tokens: int
    request_input: str


def parse_utc(
    value: str, *, source_timezone: str = "UTC", field: str = "model_handle_start_time"
) -> tuple[int, str]:
    """Accept ISO calendar time, assuming UTC when no suffix; retain nanoseconds."""
    if source_timezone != "UTC":
        raise InvalidRow("UNSUPPORTED_SOURCE_TIMEZONE", field)
    normalized = value.strip()
    day_first = re.fullmatch(
        r"(\d{2})/(\d{2})/(\d{4}) (\d{2}:\d{2}:\d{2}(?:\.\d{1,9})?)", normalized
    )
    if day_first:
        day, month, year, clock_text = day_first.groups()
        normalized = f"{year}-{month}-{day} {clock_text}"
    matched = TIME_PATTERN.fullmatch(normalized)
    if matched is None:
        raise InvalidRow("INVALID_TIMESTAMP", field)
    date, clock, fraction, offset = matched.groups()
    try:
        base = datetime.fromisoformat(f"{date}T{clock}").replace(tzinfo=UTC)
        if offset and offset != "Z":
            hours, minutes = int(offset[1:3]), int(offset[4:6])
            if hours > 23 or minutes > 59:
                raise ValueError("invalid offset")
            delta = timedelta(hours=hours, minutes=minutes)
            base += -delta if offset[0] == "+" else delta
        elapsed = base - EPOCH
        nanos = int((fraction or "").ljust(9, "0"))
        ns = (elapsed.days * 86400 + elapsed.seconds) * 1_000_000_000 + nanos
        if not -(2**63) <= ns <= 2**63 - 1:
            raise ValueError("timestamp outside SQLite nanosecond range")
    except (ValueError, OverflowError) as exc:
        raise InvalidRow("INVALID_TIMESTAMP", field) from exc
    return ns, base.strftime("%Y-%m-%dT%H:%M:%S") + f".{nanos:09d}Z"


def reject_constant(value: str) -> None:
    raise ValueError("Nonfinite JSON value")


def unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate JSON key")
        result[key] = value
    return result


def validate_request(raw: str, settings: ModelSettings) -> None:
    try:
        request = json.loads(raw, parse_constant=reject_constant, object_pairs_hook=unique_object)
        # SQLite UTF-8 and Rust encoders reject lone surrogate code points.
        raw.encode("utf-8")
    except (ValueError, UnicodeError, RecursionError) as exc:
        raise InvalidRow("INVALID_JSON", "request_input") from exc
    if not isinstance(request, dict):
        raise InvalidRow("INVALID_REQUEST", "request_input")
    if "model" in request and request["model"] not in (settings.model_id, *settings.model_aliases):
        raise InvalidRow("MODEL_MISMATCH", "request_input.model")
    messages = request.get("messages")
    if not isinstance(messages, list) or not messages:
        raise InvalidRow("INVALID_MESSAGES", "request_input.messages")
    for message in messages:
        if not isinstance(message, dict) or message.get("role") not in (
            "system",
            "developer",
            "user",
            "assistant",
            "tool",
            "function",
        ):
            raise InvalidRow("INVALID_MESSAGE", "request_input.messages")
        content = message.get("content")
        calls = message.get("tool_calls")
        legacy_call = message.get("function_call")
        if isinstance(content, list):
            for part in content:
                if not isinstance(part, dict) or part.get("type") not in ("text", "input_text"):
                    raise InvalidRow("NON_TEXT_CONTENT", "request_input.messages.content")
                if not isinstance(part.get("text"), str):
                    raise InvalidRow("INVALID_CONTENT", "request_input.messages.content")
        elif not isinstance(content, str):
            if content is not None or not (calls or legacy_call):
                raise InvalidRow("INVALID_CONTENT", "request_input.messages.content")
        if calls is not None:
            if not isinstance(calls, list) or not calls:
                raise InvalidRow("INVALID_TOOL_CALL", "request_input.messages.tool_calls")
            for call in calls:
                if (
                    not isinstance(call, dict)
                    or call.get("type") != "function"
                    or not isinstance(call.get("id"), str)
                    or not call["id"]
                ):
                    raise InvalidRow("INVALID_TOOL_CALL", "request_input.messages.tool_calls")
                validate_function(call.get("function"), calling=True)
        if legacy_call is not None:
            validate_function(legacy_call, calling=True)
        if message["role"] == "tool" and (
            not isinstance(message.get("tool_call_id"), str) or not message["tool_call_id"]
        ):
            raise InvalidRow("INVALID_TOOL_RETURN", "request_input.messages.tool_call_id")
    if "tools" in request:
        if not isinstance(request["tools"], list):
            raise InvalidRow("INVALID_TOOLS", "request_input.tools")
        for tool in request["tools"]:
            if not isinstance(tool, dict) or tool.get("type") != "function":
                raise InvalidRow("INVALID_TOOLS", "request_input.tools")
            validate_function(tool.get("function"), calling=False)
    if "functions" in request:
        if not isinstance(request["functions"], list):
            raise InvalidRow("INVALID_TOOLS", "request_input.functions")
        for function in request["functions"]:
            validate_function(function, calling=False)
    # Escaped JSON surrogates can survive raw.encode; check all decoded strings too.
    stack: list[Any] = [request]
    while stack:
        value = stack.pop()
        if isinstance(value, str):
            try:
                value.encode("utf-8")
            except UnicodeError as exc:
                raise InvalidRow("INVALID_JSON", "request_input") from exc
        elif isinstance(value, dict):
            stack.extend(value.keys())
            stack.extend(value.values())
        elif isinstance(value, list):
            stack.extend(value)
        elif isinstance(value, float) and not math.isfinite(value):
            raise InvalidRow("INVALID_JSON", "request_input")


def validate_function(function: Any, *, calling: bool) -> None:
    if not isinstance(function, dict) or not isinstance(function.get("name"), str):
        raise InvalidRow("INVALID_FUNCTION", "request_input")
    if not function["name"].strip():
        raise InvalidRow("INVALID_FUNCTION", "request_input")
    if calling and not isinstance(function.get("arguments"), str):
        raise InvalidRow("INVALID_FUNCTION_ARGUMENTS", "request_input")
    if not calling and "parameters" in function and not isinstance(function["parameters"], dict):
        raise InvalidRow("INVALID_FUNCTION_PARAMETERS", "request_input")


class CsvBatchReader:
    def __init__(
        self, settings: ModelSettings, batch_rows: int = 256, batch_bytes: int = 16 * 1024 * 1024
    ) -> None:
        if batch_rows <= 0 or batch_bytes <= 0:
            raise ValueError("Batch limits must be positive")
        self.settings = settings
        self.batch_rows = batch_rows
        self.batch_bytes = batch_bytes

    def records(self, stream: BinaryIO) -> Iterator[RequestRecord | RowIssue]:
        # csv's default 128 KiB limit is too small for long context requests.
        csv.field_size_limit(2**31 - 1)
        wrapper = io.TextIOWrapper(stream, encoding="utf-8-sig", newline="", errors="strict")
        reader = csv.reader(wrapper, strict=True)
        try:
            header = next(reader, None)
            if (
                not header
                or len(set(header)) != len(header)
                or not set(REQUIRED_COLUMNS) <= set(header)
            ):
                raise TokenScopeError("INVALID_CSV_HEADER", "Missing or duplicate CSV columns")
            index = 0
            while True:
                start = reader.line_num + 1
                cells = next(reader, None)
                if cells is None:
                    break
                index += 1
                try:
                    if len(cells) != len(header):
                        raise InvalidRow("COLUMN_COUNT", "csv")
                    values = dict(zip(header, cells, strict=True))
                    for name in ("hash_id", "appid"):
                        if not values[name].strip() or "\x00" in values[name]:
                            raise InvalidRow("INVALID_ID", name)
                    completion = values["completion_tokens"].strip()
                    if re.fullmatch(r"[0-9]+", completion):
                        completion = completion.lstrip("0") or "0"
                    if not re.fullmatch(r"[0-9]+", completion) or len(completion) > 19:
                        raise InvalidRow("INVALID_COMPLETION_TOKENS", "completion_tokens")
                    output_tokens = int(completion)
                    if output_tokens > 2**63 - 1:
                        raise InvalidRow("INVALID_COMPLETION_TOKENS", "completion_tokens")
                    time_ns, time_utc = parse_utc(values["model_handle_start_time"])
                    validate_request(values["request_input"], self.settings)
                    yield RequestRecord(
                        index,
                        start,
                        reader.line_num,
                        values["hash_id"],
                        values["appid"],
                        time_ns,
                        time_utc,
                        output_tokens,
                        values["request_input"],
                    )
                except InvalidRow as exc:
                    yield RowIssue(index, start, reader.line_num, exc.code, exc.field)
        except (csv.Error, UnicodeError) as exc:
            raise TokenScopeError("UNREADABLE_CSV", "CSV encoding or quoting is invalid") from exc
        finally:
            wrapper.detach()

    def batches(self, stream: BinaryIO) -> Iterator[list[RequestRecord | RowIssue]]:
        batch: list[RequestRecord | RowIssue] = []
        size = 0
        for record in self.records(stream):
            count = (
                len(record.request_input.encode("utf-8"))
                if isinstance(record, RequestRecord)
                else 0
            )
            if batch and (len(batch) >= self.batch_rows or size + count > self.batch_bytes):
                yield batch
                batch, size = [], 0
            batch.append(record)
            size += count
        if batch:
            yield batch
