import pytest
from fastapi.testclient import TestClient

from tokenscope.api.app import create_app
from tokenscope.errors import TokenScopeError


def test_same_origin_static_does_not_shadow_api_or_expose_siblings(service, tmp_path):
    dist = tmp_path / "dist"
    dist.mkdir()
    (dist / "index.html").write_text("<html>viewer</html>")
    (dist / "app.js").write_text("console.log(1)")
    (tmp_path / "secret.txt").write_text("private")
    with TestClient(create_app(service, start_worker=False, viewer_root=dist)) as client:
        assert client.get("/").text == "<html>viewer</html>"
        assert client.get("/app.js").status_code == 200
        assert client.get("/healthz").json() == {"status": "alive"}
        assert client.get("/monitoring/catalog").status_code == 200
        assert client.get("/missing.js").status_code == 404
        assert client.get("/%2e%2e/secret.txt").status_code == 404
        assert client.post("/").status_code == 405
    with pytest.raises(TokenScopeError, match="index.html"):
        create_app(service, start_worker=False, viewer_root=tmp_path / "absent")


def test_stream_resumes_and_closes_on_different_workers(service):
    import hashlib
    import json
    from concurrent.futures import ThreadPoolExecutor

    from conftest import csv_bytes, valid_row

    from tokenscope.domain import RunSubmission
    from tokenscope.monitoring.view_export import ViewExport
    from tokenscope.monitoring.views import RequestQuery

    (service.inputs.root / "stream.csv").write_bytes(csv_bytes([valid_row()] * 4))
    run = service.submit(RunSubmission(file_ref="stream.csv", model_id="GLM-5.2"))
    service.processor.process_next()
    export = ViewExport(service.views, run.run_id, "tenant", RequestQuery())
    sentinel = object()
    with ThreadPoolExecutor(1) as a, ThreadPoolExecutor(1) as b:
        stream = export.stream("ndjson")
        chunks = []
        for i in range(20):
            chunk = (a if i % 2 else b).submit(next, stream, sentinel).result()
            if chunk is sentinel:
                break
            chunks.append(chunk)
        raw = b"".join(chunks).splitlines(keepends=True)
        assert json.loads(raw[-1])["actual_rows"] == "4"
        assert (
            json.loads(raw[-1])["request_lines_sha256"]
            == hashlib.sha256(b"".join(raw[1:-1])).hexdigest()
        )
        body = service.views.body(run.run_id, 1)
        assert a.submit(next, body).result()
        assert b.submit(next, body, sentinel).result() is sentinel
        partial = export.stream("csv")
        a.submit(next, partial).result()
        a.submit(next, partial).result()
        b.submit(partial.close).result()
