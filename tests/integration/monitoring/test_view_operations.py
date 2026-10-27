import csv
import hashlib
import io
import json
import os
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from conftest import csv_bytes, request_json, valid_row
from fastapi.testclient import TestClient

from tokenscope.api.app import create_app
from tokenscope.domain import RunSubmission
from tokenscope.monitoring.events import PublicationEventReader
from tokenscope.monitoring.view_export import COLUMNS


def capture(name, value):
    if os.environ.get("TOKENSCOPE_OPERATIONS_CAPTURE"):
        root = Path(os.environ["TOKENSCOPE_OPERATIONS_CAPTURE"])
        root.mkdir(exist_ok=True, parents=True)
        (root / (name + ".json")).write_text(json.dumps(value, ensure_ascii=False))


def test_submission_concurrency_recovery_and_instance_guard(service, monkeypatch):
    (service.inputs.root / "input.csv").write_bytes(csv_bytes([valid_row()]))
    submission = RunSubmission(file_ref="input.csv", model_id="GLM-5.2", submission_key="same-key")
    with ThreadPoolExecutor(4) as pool:
        runs = list(pool.map(service.submit, [submission] * 8))
    assert len({r.run_id for r in runs}) == 1
    run_id = runs[0].run_id
    service.control.claim_next()
    service.control.fail(run_id, "SYNTHETIC_FAILURE")
    PublicationEventReader(service.control).prune(days=0)
    (service.inputs.root / "input.csv").unlink()

    def forbidden(*args, **kwargs):
        raise AssertionError("Idempotent replay must skip asset/file validation")

    monkeypatch.setattr(service.assets, "load", forbidden)
    with TestClient(create_app(service, start_worker=False)) as client:
        instance = client.get("/monitoring/catalog").json()["service_instance_id"]
        replay = client.post("/analysis-runs", json=submission.model_dump())
        assert replay.status_code == 202 and replay.json()["run_id"] == run_id
        assert replay.headers["x-tokenscope-instance-id"] == instance
        receipt = client.get("/analysis-submissions/same-key")
        assert receipt.status_code == 200 and receipt.json()["status"] == "failed"
        assert receipt.headers["cache-control"] == "no-store"
        capture("Receipt", receipt.json())
        mismatch = client.post(
            "/analysis-runs", json={**submission.model_dump(), "file_ref": "other.csv"}
        )
        assert (
            mismatch.status_code == 409
            and mismatch.json()["error"]["code"] == "SUBMISSION_KEY_CONFLICT"
        )
        for path in ("/analysis-submissions/same-key", f"/analysis-runs/{run_id}"):
            assert client.get(path, headers={"X-TokenScope-Instance-Id": "old"}).status_code == 409
        assert (
            client.post(
                "/analysis-runs",
                json=submission.model_dump(),
                headers={"X-TokenScope-Instance-Id": "old"},
            ).status_code
            == 409
        )
        assert client.get("/analysis-submissions/absent").status_code == 404


def test_multicolumn_details_evidence_exports_and_settings(service, monkeypatch):
    raw = request_json(messages=[dict(role="user", content="中文" * 25000)])
    rows = [
        valid_row(hash_id="dup", completion_tokens="4"),
        valid_row(hash_id="dup", completion_tokens="9007199254740993", request_input=raw),
        valid_row(hash_id="@formula,\n中文", completion_tokens="3"),
        valid_row(hash_id="100%_literal", completion_tokens="1"),
    ]
    (service.inputs.root / "input.csv").write_bytes(csv_bytes(rows))
    run = service.submit(RunSubmission(file_ref="input.csv", model_id="GLM-5.2"))
    assert service.processor.process_next().status == "completed"
    import tokenscope.monitoring.pipeline as pipeline
    from tokenscope.encoding.batch import EncodingBatchService
    from tokenscope.encoding.models import ModelEncoder

    def forbidden(*args, **kwargs):
        raise AssertionError("Presentation GET called an analysis operation")

    for name in ("aggregate", "replay", "encode_input"):
        monkeypatch.setattr(pipeline, name, forbidden)
    monkeypatch.setattr(ModelEncoder, "render", forbidden)
    monkeypatch.setattr(EncodingBatchService, "encode_batch", forbidden)
    monkeypatch.setattr(service, "explain_encoding", forbidden)
    artifacts = list((service.state_root / "runs" / run.run_id).rglob("*"))
    before = {
        p: (p.stat().st_mtime_ns, hashlib.sha256(p.read_bytes()).hexdigest())
        for p in artifacts
        if p.is_file()
    }
    base = f"/analysis-runs/{run.run_id}"
    with TestClient(create_app(service, start_worker=False)) as c:
        query = dict(appid="tenant", sort_by="completion_tokens", sort_order="desc", limit=1)
        first = c.get(base + "/requests", params=query)
        assert first.status_code == 200, first.text
        first = first.json()
        assert first["items"][0]["completion_tokens"] == "9007199254740993"
        assert first["items"][0]["request_ref"]["source_record_index"] == "2"
        second = c.get(base + "/requests", params={**query, "offset": "1"}).json()
        assert (
            second["items"][0]["completion_tokens"] == "4" and second["items"][0]["position"] == "2"
        )
        capture("RequestsPage", first)
        filtered = c.get(
            base + "/requests", params=dict(appid="tenant", hash_id="100%_", hash_match="prefix")
        ).json()
        assert filtered["total"] == "1"
        assert (
            c.get(base + "/requests", params=dict(appid="tenant", lower=str(2**80))).json()["total"]
            == "0"
        )
        detail = c.get(base + "/requests/2", params=dict(appid="tenant"))
        assert detail.status_code == 200, detail.text
        detail = detail.json()
        assert detail["body_preview"]["truncated"]
        assert int(detail["body_preview"]["preview_utf8_bytes"]) <= 65536
        assert c.get(detail["links"]["body"]).content == raw.encode()
        assert c.get(base + "/requests/2", params=dict(appid="other")).status_code == 404
        capture("RequestDetail", detail)
        for section in ("source_fields", "special_ranges"):
            response = c.get(
                detail["links"]["evidence"], params=dict(appid="tenant", section=section, limit=1)
            )
            assert response.status_code == 200, response.text
            capture("EvidencePage-" + section, response.json())
        signals = c.get(base + "/view-signals", params=dict(appid="tenant")).json()
        assert signals["total"] == "0"
        capture("SignalsPage", signals)
        exported = c.get(base + "/requests/export", params=dict(appid="tenant", format="ndjson"))
        assert exported.status_code == 200, exported.text
        lines = exported.content.splitlines(keepends=True)
        assert all(x.endswith(b"\n") for x in lines)
        values = [json.loads(x) for x in lines]
        assert (
            values[0]["expected_rows"]
            == values[-1]["actual_rows"]
            == exported.headers["x-export-row-count"]
            == "4"
        )
        assert (
            hashlib.sha256(b"".join(lines[1:-1])).hexdigest() == values[-1]["request_lines_sha256"]
        )
        for name, value in zip(
            ("ExportMetadata", "ExportRequest", "ExportSummary"),
            (values[0], values[1], values[-1]),
            strict=True,
        ):
            capture(name, value)
        csv_response = c.get(base + "/requests/export", params=dict(appid="tenant", format="csv"))
        parsed = list(csv.reader(io.StringIO(csv_response.text, newline="")))
        assert parsed[0] == list(COLUMNS) and len(parsed) == 5
        assert any(row[7] == "'@formula,\n中文" for row in parsed[1:])
        empty = c.get(
            base + "/requests/export",
            params=dict(appid="tenant", format="ndjson", lower=str(2**80)),
        )
        assert len(empty.content.splitlines()) == 2
        assert (
            c.get(base + "/requests/export", params=dict(appid="tenant", limit=1)).status_code
            == 422
        )
        settings = c.get("/monitoring/models/GLM-5.2/settings").json()
        assert settings["settings"]["block_size"] == "128"
        capture("ModelSettingsResponse", settings)
        assert (
            c.put(
                "/monitoring/models/GLM-5.2/settings",
                json=dict(expected_revision="1", changes=dict(block_size=64)),
            ).status_code
            == 422
        )
        changed = c.put(
            "/monitoring/models/GLM-5.2/settings",
            json=dict(expected_revision="1", changes=dict(block_size="64")),
        )
        assert changed.status_code == 200, changed.text
        assert c.get("/models/GLM-5.2/settings").json()["settings"]["block_size"] == 64
        rules = c.get("/monitoring/threshold-rules").json()
        capture("RulesPage", rules)
        rule = dict(
            appid="tenant",
            model_id="GLM-5.2",
            rule_id="r",
            expected_revision="0",
            metric="request_count",
            comparator="gt",
            threshold="9007199254740993",
            value_kind="integer",
            enabled=True,
            route=None,
            measurement_signature="a" * 64,
        )
        updated = c.put("/monitoring/threshold-rules", json=rule)
        assert updated.status_code == 200, updated.text
        capture("RuleResponse", updated.json())
        assert updated.json()["rule"]["threshold"] == "9007199254740993"
        assert c.get("/monitoring/threshold-rules?rules_revision=0").status_code == 409
    assert before == {
        p: (p.stat().st_mtime_ns, hashlib.sha256(p.read_bytes()).hexdigest()) for p in before
    }


def test_signals_shared_outbox_and_failed_validation_no_receipt(service):
    from tokenscope.monitoring.rules import RuleUpdate

    (service.inputs.root / "input.csv").write_bytes(csv_bytes([valid_row()]))
    initial = service.submit(RunSubmission(file_ref="input.csv", model_id="GLM-5.2"))
    service.processor.process_next()
    signature = service.metrics(initial.run_id)["groups"][0]["measurement_signatures"][
        "request_count"
    ]
    service.control.update_rule(
        RuleUpdate(
            appid="tenant",
            model_id="GLM-5.2",
            rule_id="threshold",
            expected_revision=0,
            metric="request_count",
            comparator="gt",
            threshold=0.5,
            measurement_signature=signature,
        )
    )
    ids = []
    for _ in range(2):
        run = service.submit(RunSubmission(file_ref="input.csv", model_id="GLM-5.2"))
        service.processor.process_next()
        signal = service.views.signals(run.run_id, "tenant", 0, 100)["items"][0]
        assert signal["run_id"] == run.run_id and signal["observed_value"] == "1"
        assert signal["value_kind"] == "number" and signal["threshold"] == 0.5
        ids.append(signal["event_id"])
        capture("SignalsPage-nonempty", service.views.signals(run.run_id, "tenant", 0, 100))
    assert ids[0] == ids[1]
    with TestClient(create_app(service, start_worker=False)) as c:
        payload = dict(
            file_ref="missing.csv", model_id="GLM-5.2", submission_key="validation-fails"
        )
        assert c.post("/analysis-runs", json=payload).status_code != 202
        assert c.get("/analysis-submissions/validation-fails").status_code == 404
        payload["file_ref"] = "input.csv"
        assert c.post("/analysis-runs", json=payload).status_code == 202
