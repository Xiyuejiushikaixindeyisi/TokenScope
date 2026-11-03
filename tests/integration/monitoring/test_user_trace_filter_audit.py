"""Regression evidence for actual Trace filtering, not a reconstruction of the 622 rows."""

import json

from conftest import csv_bytes, valid_row
from fastapi.testclient import TestClient

from tokenscope.analysis_common.contracts import SourceSelection
from tokenscope.analysis_common.source import SourceResolver
from tokenscope.api.app import create_app


def test_real_trace_filters_preserve_duplicate_hash_and_late_time(service):
    raw = json.dumps({"messages": [{"role": "user", "content": "valid missing model"}]})
    rows = [
        valid_row(hash_id="h", request_input=raw, model_handle_start_time="2026-10-20T07:00:00Z"),
        valid_row(hash_id="h", request_input=raw, model_handle_start_time="2026-10-20T09:18:57Z"),
        valid_row(hash_id="h", request_input=raw, model_handle_start_time="2026-10-20T09:18:57Z"),
        valid_row(request_input='{"model":"GLM-V5.2","messages":[]}'),
        valid_row(request_input='{"model":"GLM-V5.2","model":"GLM-V5.2","messages":[]}'),
        valid_row(
            request_input='{"model":"GLM-V5.2","messages":[{"role":"user","content":".5"}],"t":.5}'
        ),
        valid_row(
            request_input=json.dumps(
                {"model": "wrong", "messages": [{"role": "user", "content": "text"}]}
            )
        ),
        valid_row(completion_tokens="-1", request_input=raw),
    ]
    path = service.inputs.root / "audit.csv"
    path.write_bytes(csv_bytes(rows))
    original = path.read_bytes()
    app = create_app(service, start_worker=False)
    user = app.state.user
    headers = {"X-TokenScope-Instance-Id": user.service_id}
    with TestClient(app) as client:
        receipt = client.post(
            "/monitoring/user-v2/runs",
            json=dict(
                submission_key="audit",
                file_ref="audit.csv",
                common_name="GLM-V5.2",
                model_id="GLM-5.2",
            ),
            headers=headers,
        ).json()
        user.process_next()
        base = service.processor.process_next()
        assert base.status == "completed"
        ready = user.process_next()
        assert ready.state == "ready"
        summary = service.control.result(base.run_id)
        assert summary["quality"]["valid_requests"] == 3
        with service.result_db(base.run_id) as db:
            assert db.execute("SELECT count(*) FROM facts").fetchone()[0] == 3
            assert db.execute("SELECT count(DISTINCT hash_id) FROM facts").fetchone()[0] == 1
            codes = dict(db.execute("SELECT code,count(*) FROM row_errors GROUP BY code"))
            assert codes == {
                "INVALID_JSON": 2,
                "INVALID_MESSAGES": 1,
                "MODEL_MISMATCH": 1,
                "INVALID_COMPLETION_TOKENS": 1,
            }
        with user.index(ready.user_run_id) as db:
            group = json.loads(
                db.execute(
                    "SELECT payload FROM groups WHERE width=5000 AND appid='tenant'"
                ).fetchone()[0]
            )
            assert group["request_count"] == "3"
        catalog = client.get("/monitoring/user-v2/runs", headers=headers).json()
        item = catalog["entries"][0]
        assert item["source"]["user_run_id"] == receipt["user_run_id"]
        assert item["source"]["base_run_id"] == base.run_id
        assert item["request_count"] == "3"
        # Existing analysis common contract accepts this exact user Trace selection.
        selected = SourceSelection(
            source_kind="user_v2",
            user_run_id=ready.user_run_id,
            expected_index_revision=item["source"]["index_revision"],
            appid=item["appid"],
            window=None,
        )
        resolved = SourceResolver(service, user).resolve_scope(selected)
        assert resolved.scope.request_count == 3
        assert resolved.scope.source.manifest_sha256 == item["source"]["manifest_sha256"]
        assert resolved.scope.source.model_id == item["source"]["model_id"]
        assert path.read_bytes() == original
