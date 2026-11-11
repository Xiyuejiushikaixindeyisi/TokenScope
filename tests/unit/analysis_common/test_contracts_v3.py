import hashlib
import json
from pathlib import Path

import pytest
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient
from pydantic import ValidationError

from tokenscope.analysis_common.contracts import SourceSelection
from tokenscope.analysis_common.contracts_v3 import (
    PreparationReceipt3,
    PreparationRequest3,
    SampleManifest3,
)
from tokenscope.analysis_common.preparation_store import PreparationStore
from tokenscope.analysis_common.wire_v3 import from_wire, to_wire
from tokenscope.api.diagnostics_v3 import router
from tokenscope.errors import TokenScopeError


def request(**changes):
    data = dict(
        submission_key="one",
        source=SourceSelection(source_kind="base", base_run_id="large-source", appid="a"),
    )
    data.update(changes)
    return PreparationRequest3(**data)


def test_automatic_request_only_and_strict_wire():
    value = request()
    assert from_wire(PreparationRequest3, to_wire(value)) == value
    for invalid in (
        {"direction": "token_content"},
        {"discovery_mode": "manual_counterfactual"},
        {"recipe": {"clock": "injected"}},
    ):
        with pytest.raises(ValidationError):
            request(**invalid)
    with pytest.raises(ValidationError):
        PreparationReceipt3(
            preparation_id="prep-" + "0" * 32, intent_digest="intent:x", state="completed"
        )


def test_receipt_registration_does_not_resolve_source_or_load_assets(tmp_path):
    # No monitoring service or source resolver exists in this app.
    store = PreparationStore(tmp_path / "store")
    app = FastAPI()

    @app.exception_handler(TokenScopeError)
    async def error(req: Request, exc: TokenScopeError):
        return JSONResponse({"error": exc.as_dict()}, status_code=exc.http_status)

    app.include_router(router(store, "instance"))
    client = TestClient(app)
    cap = client.get("/diagnostics/v3/capabilities").json()
    assert cap["execution_enabled"] is False
    headers = {"X-TokenScope-Service-Instance": "instance"}
    payload = to_wire(request())
    first = client.post("/diagnostics/v3/source-preparations", json=payload, headers=headers)
    assert first.status_code == 202
    assert first.json()["state"] == "queued"
    assert (
        client.post("/diagnostics/v3/source-preparations", json=payload, headers=headers).json()
        == first.json()
    )
    payload["source"]["appid"] = "other"
    assert (
        client.post(
            "/diagnostics/v3/source-preparations", json=payload, headers=headers
        ).status_code
        == 409
    )
    assert (
        client.post(
            "/diagnostics/v3/source-preparations",
            json=payload,
            headers={"X-TokenScope-Service-Instance": "stale"},
        ).status_code
        == 409
    )
    receipt_id = first.json()["preparation_id"]
    assert (
        client.get(f"/diagnostics/v3/source-preparations/{receipt_id}", headers=headers).json()
        == first.json()
    )
    assert store.request(receipt_id) == request()


def test_frozen_sampling_examples_and_reference_guards():
    root = Path(__file__).resolve().parents[3] / "docs/contracts/diagnostics-sampling-3"
    manifest = json.loads((root / "manifest.json").read_text())
    for name, digest in manifest["files"].items():
        assert hashlib.sha256((root / name).read_bytes()).hexdigest() == digest
    examples = json.loads((root / "examples.json").read_text())
    sample = from_wire(SampleManifest3, examples["sample"])
    assert to_wire(sample) == examples["sample"]
    for mutated in (
        sample.model_dump() | {"selected_raw_bytes": 12345},
        sample.model_dump() | {"files": sample.files[:-1]},
        sample.model_dump() | {"source_selection": request().source},
    ):
        with pytest.raises(ValidationError):
            SampleManifest3.model_validate(mutated)
