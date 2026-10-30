"""Streaming MA ingestion with independent field eligibility and durable provenance."""

import csv
import re
import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

from tokenscope.domain import ModelSettings
from tokenscope.errors import TokenScopeError
from tokenscope.ingestion.csv_reader import InvalidRow, parse_utc, validate_request
from tokenscope.monitoring.ma.contracts import Submit

COLUMNS = (
    "instance_uuid",
    "hash_id",
    "appid",
    "request_time",
    "model_handle_start_time",
    "prompt_tokens",
    "cached_tokens",
    "completion_tokens",
    "request_input",
)


@contextmanager
def connect(path: Path, *, readonly: bool = False) -> Iterator[sqlite3.Connection]:
    db = (
        sqlite3.connect(path.as_uri() + "?mode=ro", uri=True) if readonly else sqlite3.connect(path)
    )
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA cache_size=-8192")
    db.execute("PRAGMA temp_store=FILE")
    try:
        with db:
            yield db
    finally:
        db.close()


def initialize(path: Path) -> None:
    with connect(path) as db:
        db.executescript("""
        CREATE TABLE records (
          id INTEGER PRIMARY KEY, role TEXT NOT NULL, source_record_index INTEGER NOT NULL,
          line_start INTEGER NOT NULL, line_end INTEGER NOT NULL,
          instance_uuid TEXT, hash_id TEXT, appid TEXT, request_ns INTEGER, handle_ns INTEGER,
          request_input TEXT, prompt_tokens INTEGER, cached_tokens INTEGER,
          completion_tokens INTEGER, assigned INTEGER NOT NULL, candidate INTEGER NOT NULL,
          local_prompt INTEGER, ideal_hit INTEGER, token_slice TEXT, evidence TEXT,
          UNIQUE(role,source_record_index));
        CREATE TABLE issues (role TEXT, source_record_index INTEGER, line_start INTEGER,
                             line_end INTEGER, field TEXT, code TEXT);
        CREATE INDEX scope_order ON records(instance_uuid,role,handle_ns,source_record_index);
        CREATE INDEX quality_order ON issues(role,source_record_index,field,code);
        CREATE TABLE scopes (instance_uuid TEXT PRIMARY KEY,status TEXT NOT NULL);
        CREATE TABLE projections (instance_uuid TEXT PRIMARY KEY,snapshot TEXT NOT NULL);
        """)


def token_cell(text: str) -> int:
    value = text.strip()
    if not value:
        raise ValueError("MISSING_TOKEN_VALUE")
    if not re.fullmatch(r"[0-9]+", value):
        raise ValueError("INVALID_TOKEN_INTEGER")
    value = value.lstrip("0") or "0"
    if len(value) > 19 or int(value) > 2**63 - 1:
        raise ValueError("TOKEN_OVERFLOW")
    return int(value)


def ingest(path: Path, source: Path, role: str, binding: Submit, settings: ModelSettings) -> None:
    start = parse_utc(binding.pre_start if role == "pre" else binding.now_start)[0]
    end = parse_utc(binding.now_start if role == "pre" else binding.now_end)[0]
    csv.field_size_limit(2**31 - 1)
    with connect(path) as db, source.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.reader(stream, strict=True)
        try:
            header = next(reader, None)
            if not header or len(set(header)) != len(header) or not set(COLUMNS) <= set(header):
                raise TokenScopeError("MISSING_COLUMNS", "Missing or duplicate MA CSV columns", 422)
            index = 0
            while True:
                line_start = reader.line_num + 1
                cells = next(reader, None)
                if cells is None:
                    break
                index += 1
                errors: list[tuple[str, str]] = []
                values = dict(zip(header, cells, strict=True)) if len(cells) == len(header) else {}
                if not values:
                    errors.append(("csv", "COLUMN_COUNT"))
                uuid = values.get("instance_uuid", "")
                valid_uuid = bool(uuid.strip()) and "\x00" not in uuid and len(uuid) <= 512
                if not valid_uuid:
                    errors.append(("instance_uuid", "INVALID_ID"))
                spec_ok = True
                if "model_standard_name" in values:
                    spec = values["model_standard_name"]
                    if spec and spec != binding.model_standard_name:
                        raise TokenScopeError(
                            "MIXED_SPEC", f"Mixed specification at {role}:{index}", 422
                        )
                    if not spec:
                        spec_ok = False
                        errors.append(("model_standard_name", "MISSING_SPEC"))
                times: dict[str, int | None] = {}
                for field in ("request_time", "model_handle_start_time"):
                    try:
                        times[field] = parse_utc(values.get(field, ""))[0]
                    except InvalidRow as exc:
                        times[field] = None
                        errors.append((field, exc.code))
                request_ns = times["request_time"]
                if request_ns is not None and not start <= request_ns < end:
                    raise TokenScopeError(
                        "OUTSIDE_WINDOW", f"Window violation at {role}:{index}", 422
                    )
                tokens: dict[str, int | None] = {}
                for field in ("prompt_tokens", "cached_tokens", "completion_tokens"):
                    try:
                        tokens[field] = token_cell(values.get(field, ""))
                    except ValueError as exc:
                        tokens[field] = None
                        errors.append((field, str(exc)))
                p, h = tokens["prompt_tokens"], tokens["cached_tokens"]
                if p is not None and h is not None and h > p:
                    tokens["cached_tokens"] = None
                    errors.append(("cached_tokens", "CACHE_EXCEEDS_INPUT"))
                ids_ok = True
                for field in ("hash_id", "appid"):
                    if not values.get(field, "").strip() or "\x00" in values.get(field, ""):
                        ids_ok = False
                        errors.append((field, "INVALID_ID"))
                raw = values.get("request_input", "")
                raw_ok = True
                try:
                    validate_request(raw, settings)
                except InvalidRow as exc:
                    raw_ok = False
                    errors.append((exc.field, exc.code))
                assigned = valid_uuid and spec_ok and request_ns is not None
                candidate = (
                    assigned and ids_ok and raw_ok and times["model_handle_start_time"] is not None
                )
                db.execute(
                    """INSERT INTO records(role,source_record_index,line_start,line_end,
                    instance_uuid,hash_id,appid,request_ns,handle_ns,request_input,prompt_tokens,
                    cached_tokens,completion_tokens,assigned,candidate)
                    VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                    (
                        role,
                        index,
                        line_start,
                        reader.line_num,
                        uuid,
                        values.get("hash_id"),
                        values.get("appid"),
                        request_ns,
                        times["model_handle_start_time"],
                        raw,
                        tokens["prompt_tokens"],
                        tokens["cached_tokens"],
                        tokens["completion_tokens"],
                        int(assigned),
                        int(candidate),
                    ),
                )
                db.executemany(
                    "INSERT INTO issues VALUES (?,?,?,?,?,?)",
                    [
                        (role, index, line_start, reader.line_num, field, code)
                        for field, code in errors
                    ],
                )
                if index % 256 == 0:
                    db.commit()
        except (csv.Error, UnicodeError) as exc:
            raise TokenScopeError(
                "MALFORMED_CSV", "MA CSV encoding or quoting invalid", 422
            ) from exc
