import io
import json

import pytest
from conftest import csv_bytes, request_json, valid_row

from tokenscope.domain import DEFAULT_SETTINGS
from tokenscope.errors import TokenScopeError
from tokenscope.ingestion.csv_reader import (
    CsvBatchReader,
    InvalidRow,
    RequestRecord,
    RowIssue,
    parse_utc,
)


def test_multiline_bom_preserves_json_and_physical_lines(reader):
    raw = (
        ' {\n "messages": [{"role":"user", "content":"comma, and \\"quote\\""}],'
        ' "temperature": 0.2\n} '
    )
    records = list(reader.records(io.BytesIO(csv_bytes([valid_row(request_input=raw)], bom=True))))
    assert len(records) == 1
    assert isinstance(records[0], RequestRecord)
    assert records[0].request_input == raw
    assert records[0].physical_line_start == 2
    assert records[0].physical_line_end == 4


def test_long_field_bounded_batches_and_no_truncation():
    reader = CsvBatchReader(DEFAULT_SETTINGS["GLM-5.2"], batch_rows=3, batch_bytes=100)
    large = request_json(messages=[{"role": "user", "content": "x" * 300_000}])
    batches = list(
        reader.batches(
            io.BytesIO(csv_bytes([valid_row(request_input=large), valid_row(), valid_row()]))
        )
    )
    assert [len(batch) for batch in batches] == [1, 1, 1]
    assert batches[0][0].request_input == large


@pytest.mark.parametrize(
    "value,code",
    [
        ("[]", "INVALID_REQUEST"),
        ("{", "INVALID_JSON"),
        ('{"messages": [], "x":NaN}', "INVALID_JSON"),
        (request_json(temperature=float("inf")).replace("Infinity", "1e999"), "INVALID_JSON"),
        ('{"messages": [], "messages": []}', "INVALID_JSON"),
        ('{"messages":[{"role":"user","content":"\\ud800"}]}', "INVALID_JSON"),
        (request_json(messages=[]), "INVALID_MESSAGES"),
        (request_json(model="another-deployment"), "MODEL_MISMATCH"),
        (
            request_json(messages=[{"role": "user", "content": [{"type": "image_url"}]}]),
            "NON_TEXT_CONTENT",
        ),
        (request_json(messages=[{"role": "user", "content": None}]), "INVALID_CONTENT"),
        (request_json(messages=[{"role": "tool", "content": "answer"}]), "INVALID_TOOL_RETURN"),
        (request_json(tools={}), "INVALID_TOOLS"),
    ],
)
def test_invalid_request_row_skips_and_continues(reader, value, code):
    records = list(
        reader.records(
            io.BytesIO(csv_bytes([valid_row(request_input=value), valid_row(hash_id="h2")]))
        )
    )
    assert isinstance(records[0], RowIssue)
    assert records[0].code == code
    assert isinstance(records[1], RequestRecord)
    assert records[1].source_record_index == 2
    assert "request_input" not in records[0].__dict__


def test_text_tools_and_parts_supported(reader):
    request = request_json(
        model="glm-5.2",
        tools=[
            {"type": "function", "function": {"name": "lookup", "parameters": {"type": "object"}}}
        ],
        messages=[
            {"role": "user", "content": [{"type": "text", "text": "hello"}]},
            {
                "role": "assistant",
                "content": None,
                "tool_calls": [
                    {
                        "id": "call1",
                        "type": "function",
                        "function": {"name": "lookup", "arguments": "{}"},
                    }
                ],
            },
            {"role": "tool", "tool_call_id": "call1", "content": "result"},
        ],
    )
    [record] = list(reader.records(io.BytesIO(csv_bytes([valid_row(request_input=request)]))))
    assert isinstance(record, RequestRecord)
    assert json.loads(record.request_input)["model"] == "glm-5.2"


@pytest.mark.parametrize(
    "change,code",
    [
        ({"completion_tokens": "-1"}, "INVALID_COMPLETION_TOKENS"),
        ({"completion_tokens": "1.0"}, "INVALID_COMPLETION_TOKENS"),
        ({"completion_tokens": str(2**63)}, "INVALID_COMPLETION_TOKENS"),
        ({"hash_id": " "}, "INVALID_ID"),
        ({"appid": "\x00"}, "INVALID_ID"),
        ({"model_handle_start_time": "1761000000000"}, "INVALID_TIMESTAMP"),
    ],
)
def test_invalid_scalar(reader, change, code):
    [record] = list(reader.records(io.BytesIO(csv_bytes([valid_row(**change)]))))
    assert record.code == code


@pytest.mark.parametrize(
    "value",
    [
        "2026-02-29T00:00:00Z",
        "2026-10-27T24:00:00Z",
        "2026-10-27T00:00:00+00:60",
        "1500-01-01T00:00:00Z",
    ],
)
def test_invalid_time(value):
    with pytest.raises(InvalidRow):
        parse_utc(value)


def test_nanosecond_utc_and_offsets():
    expected = parse_utc("2026-10-27T00:00:00.123456789Z")
    assert parse_utc("2026-10-27 00:00:00.123456789") == expected
    assert parse_utc("2026-10-27T08:00:00.123456789+08:00") == expected
    assert parse_utc("2026-10-27T00:00:00.123456790Z")[0] == expected[0] + 1
    assert parse_utc("1969-12-31T23:59:59.999999999Z")[0] == -1


@pytest.mark.parametrize(
    "data,code",
    [
        (b"", "INVALID_CSV_HEADER"),
        (b"hash_id,hash_id\na,b\n", "INVALID_CSV_HEADER"),
        (csv_bytes([]) + b'"unclosed', "UNREADABLE_CSV"),
        (csv_bytes([]) + b"\xff", "UNREADABLE_CSV"),
    ],
)
def test_file_errors_are_not_silent_bad_rows(reader, data, code):
    with pytest.raises(TokenScopeError) as error:
        list(reader.records(io.BytesIO(data)))
    assert error.value.code == code


def test_wrong_width_and_blank_records_count(reader):
    records = list(reader.records(io.BytesIO(csv_bytes([["one"], [], valid_row()]))))
    assert [record.source_record_index for record in records] == [1, 2, 3]
    assert [record.code for record in records[:2]] == ["COLUMN_COUNT", "COLUMN_COUNT"]
