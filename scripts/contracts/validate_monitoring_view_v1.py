"""Validate frozen design fixtures, not live service or browser behavior."""

import csv
import hashlib
import io
import json
import platform
from datetime import UTC, datetime
from importlib.metadata import version
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[2]
C = ROOT / "docs/contracts"
EX = C / "examples/monitoring-view-s0"
REPORT = ROOT / "artifacts/validation/monitoring/B005.1/S0/contract-check.json"
schema = json.loads((C / "schemas/monitoring-view-v1.schema.json").read_text())
oas = json.loads((C / "schemas/monitoring-view-v1.design.openapi.json").read_text())
cases = json.loads((EX / "cases.json").read_text())["cases"]
checks = []


def check(name, function):
    try:
        detail = function()
        checks.append(dict(name=name, passed=True, detail=detail))
    except Exception as exc:
        checks.append(dict(name=name, passed=False, error=str(exc)))


def validate(typ, data):
    Draft202012Validator(
        {"$ref": "#/$defs/" + typ, "$defs": schema["$defs"]},
        format_checker=FormatChecker(),
    ).validate(data)


def load(name):
    return json.loads((EX / (name + ".json")).read_text())


check("json-schema-meta-schema", lambda: Draft202012Validator.check_schema(schema))
for case in cases:
    check(
        "example:" + case["name"],
        lambda case=case: validate(case["schema"], json.loads((C / case["path"]).read_text())),
    )


def references(doc):
    count = 0

    def walk(x):
        nonlocal count
        if isinstance(x, dict):
            if "$ref" in x:
                assert x["$ref"].startswith("#/"), "External schema reference"
                target = doc
                for part in x["$ref"][2:].split("/"):
                    target = target[part.replace("~1", "/").replace("~0", "~")]
                count += 1
            for v in x.values():
                walk(v)
        elif isinstance(x, list):
            for v in x:
                walk(v)

    walk(doc)
    return count


check("schema-refs", lambda: references(schema))
check("openapi-refs", lambda: references(oas))


def api_surface():
    seen = set()
    for path, methods in oas["paths"].items():
        for op in methods.values():
            assert op["operationId"] not in seen
            seen.add(op["operationId"])
            pars = op["parameters"]
            assert len(pars) == len({(p["name"], p["in"]) for p in pars})
            for p in pars:
                if p["in"] == "path":
                    assert p["required"] and "{" + p["name"] + "}" in path
                if "default" in p["schema"]:
                    Draft202012Validator(p["schema"]).validate(p["schema"]["default"])
            assert any(k.startswith("2") for k in op["responses"])
            assert all(k in op["responses"] for k in ("404", "409", "422", "503"))
    assert oas["x-runtime-implemented"] is False
    return dict(paths=len(oas["paths"]), operations=len(seen))


check("intended-openapi-surface", api_surface)


def snapshots():
    n = 0
    for c in cases:
        if c["schema"] != "ViewSnapshot":
            continue
        v = json.loads((C / c["path"]).read_text())
        g, identity = v["metrics"], v["identity"]
        t = {k: int(x) for k, x in g["totals"].items()}
        assert (
            t["prompt_tokens"] == t["ideal_cached_input_tokens"] + t["ideal_compute_input_tokens"]
        )
        assert int(g["json_to_prompt_delta"]) == t["prompt_tokens"] - t["json_tokens"]
        assert g["ideal_hit_rate"] == (
            t["ideal_cached_input_tokens"] / t["prompt_tokens"] if t["prompt_tokens"] else None
        )
        assert g["model_id"] == identity["model_id"] == v["provenance"]["settings"]["model_id"]
        assert g["appid"] == identity["appid"]
        count = int(g["request_count"])
        bins = 0
        for metric, widths in v["distributions"].items():
            for width, h in widths.items():
                w = int(width)
                assert h["bin_width"] == w and len(h["bins"]) == 200000 // w + 1
                assert int(h["sample_count"]) == count
                assert sum(int(b["count"]) for b in h["bins"]) == count
                assert h["quantiles"] == g["quantiles"][metric]
                assert h["bins"][-1]["upper"] is None
                for i, b in enumerate(h["bins"]):
                    assert int(b["lower"]) == i * w
                    assert b["upper"] == (str((i + 1) * w) if i < len(h["bins"]) - 1 else None)
                    assert b["share"] == int(b["count"]) / count
                maximum = max(int(b["count"]) for b in h["bins"])
                assert h["summary"]["mode_bin_indices"] == [
                    str(i) for i, b in enumerate(h["bins"]) if int(b["count"]) == maximum
                ]
                assert int(h["summary"]["mode_count"]) == maximum
                bins += len(h["bins"])
        assert bins == 1029
        q = v["quality"]["file_quality"]
        assert int(q["records_read"]) == int(q["valid_requests"]) + int(q["skipped_rows"])
        n += 1
    return dict(snapshots=n, bins_per_snapshot=1029)


check("snapshot-cross-field-invariants", snapshots)


def reject(name, typ, data):
    def run():
        try:
            validate(typ, data)
        except Exception:
            return "rejected"
        raise AssertionError("Invalid fixture unexpectedly accepted")

    check("negative:" + name, run)


v = load("requests-normal")
v["total"] = 1
reject("numeric-count", "RequestsPage", v)
v = load("requests-normal")
del v["items"][0]["completion_tokens"]
reject("missing-required-column", "RequestsPage", v)
v = load("requests-normal")
v["unknown_field"] = True
reject("unknown-field", "RequestsPage", v)
v = load("requests-normal")
v["total"] = "01"
reject("noncanonical-decimal", "RequestsPage", v)
v = load("requests-normal")
v["total"] = "1\n"
reject("decimal-with-newline", "RequestsPage", v)
v = load("snapshot-normal")
v["metrics"]["ideal_hit_rate"] = 1.1
reject("rate-outside-domain", "ViewSnapshot", v)
v = load("receipt-completed")
v["finished_at"] = None
reject("terminal-without-time", "Receipt", v)
v = load("receipt-failed")
v["error_code"] = None
reject("failure-without-code", "Receipt", v)
v = load("settings-glm")
v["settings"]["cache_mode"] = "qwen_hybrid"
reject("wrong-model-mode", "ModelSettingsResponse", v)
v = load("rule-ratio")
v["threshold"] = "0.25"
reject("ratio-as-string", "Rule", v)
v = load("rule-update")
v["threshold"] = 90
reject("integer-threshold-as-number", "RuleUpdate", v)


def sse():
    result = []
    for name in ("replay.sse", "reset.sse"):
        raw = (EX / name).read_bytes()
        assert raw.endswith(b"\n\n")
        for frame in raw.decode().split("\n\n"):
            fields = dict(
                line.split(": ", 1)
                for line in frame.splitlines()
                if ": " in line and not line.startswith(":")
            )
            if "event" not in fields:
                assert "id" not in fields
                continue
            payload = json.loads(fields["data"])
            kind = fields["event"]
            validate(
                {
                    "result_published": "ResultPublishedEvent",
                    "run_terminal": "RunTerminalEvent",
                    "reset": "ResetEvent",
                }[kind],
                payload,
            )
            if kind == "reset":
                assert "id" not in fields
            else:
                assert (
                    fields["id"]
                    == payload["service_instance_id"]
                    + ":"
                    + payload["publish_seq" if kind == "result_published" else "event_seq"]
                )
            result.append(kind)
    return result


check("sse-byte-frames", sse)


def ndjson(raw):
    assert raw.endswith(b"\n") and not raw.startswith(b"\xef\xbb\xbf") and b"\r" not in raw
    lines = raw.splitlines(keepends=True)
    values = [json.loads(line.decode("utf-8")) for line in lines]
    validate("ExportMetadata", values[0])
    validate("ExportSummary", values[-1])
    for v in values[1:-1]:
        validate("ExportRequest", v)
    assert int(values[0]["expected_rows"]) == int(values[-1]["actual_rows"]) == len(values) - 2
    assert hashlib.sha256(b"".join(lines[1:-1])).hexdigest() == values[-1]["request_lines_sha256"]
    return len(values) - 2


def exports():
    base = C / "examples/monitoring-view-v0.2"
    manifest = json.loads((base / "manifest.json").read_text())
    result = []
    for item in manifest["fixtures"]:
        for fmt in ("ndjson", "csv"):
            e = item[fmt]
            raw = (base / e["path"]).read_bytes()
            assert hashlib.sha256(raw).hexdigest() == e["file_sha256"]
            if fmt == "ndjson":
                n = ndjson(raw)
            else:
                records = list(
                    csv.reader(io.StringIO(raw.decode("utf-8"), newline=""), strict=True)
                )
                assert len(records[0]) == 14 and all(len(r) == 14 for r in records)
                n = len(records) - 1
            assert n == item["rows"] == int(e["headers"]["X-Export-Row-Count"])
            result.append(dict(name=item["name"], format=fmt, rows=n, bytes=len(raw)))
    raw = (base / "normal.ndjson").read_bytes()
    mutations = [
        raw[:-1],
        b"".join(raw.splitlines(keepends=True)[:-1]),
        raw + b"{}\n",
        raw.replace(b'"actual_rows":"4"', b'"actual_rows":"5"'),
    ]
    for bad in mutations:
        assert bad != raw
        try:
            ndjson(bad)
        except Exception:
            continue
        raise AssertionError("Corrupt NDJSON accepted")
    return dict(fixtures=result, rejected_mutations=len(mutations))


check("export-bytes-and-corruption", exports)


def size_boundary():
    request = json.loads(
        (C / "examples/monitoring-view-v0.2/normal.ndjson").read_bytes().splitlines()[1]
    )
    request["hash_id"] = ""

    def encode(v):
        return (
            json.dumps(v, sort_keys=True, ensure_ascii=False, separators=(",", ":")) + "\n"
        ).encode()

    extra = 1048576 - len(encode(request))
    request["hash_id"] = "x" * extra
    validate("ExportRequest", request)
    exact = len(encode(request))
    request["hash_id"] += "x"
    validate("ExportRequest", request)
    over = len(encode(request))
    assert exact == 1048576 and over == 1048577
    return dict(
        equal_limit_bytes=exact,
        above_limit_bytes=over,
        scope="serialized NDJSON fixture only; UI rejection not tested",
    )


check("r2-record-size-fixture", size_boundary)
report = dict(
    contract_version="1.0.0",
    validated_at_utc=datetime.now(UTC).isoformat(),
    scope="schema/examples/document protocol only; no API/browser/runtime tests",
    python=platform.python_version(),
    validator={
        n: version(n)
        for n in ("jsonschema", "attrs", "referencing", "jsonschema-specifications", "rpds-py")
    },
    runtime_or_docker_started=False,
    checks=checks,
    passed=all(c["passed"] for c in checks),
)
REPORT.parent.mkdir(parents=True, exist_ok=True)
REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
print(
    json.dumps(
        dict(
            passed=report["passed"],
            checks=len(checks),
            failures=[c for c in checks if not c["passed"]],
            report=str(REPORT.relative_to(ROOT)),
        ),
        ensure_ascii=False,
    )
)
raise SystemExit(0 if report["passed"] else 1)
