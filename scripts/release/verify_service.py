"""Explicit synthetic-only smoke acceptance; resume is read-only. Python stdlib only."""

import argparse
import csv
import hashlib
import io
import json
import time
import uuid
from pathlib import Path
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", required=True)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--submit-synthetic", type=Path, help="Explicit generated input manifest")
    parser.add_argument("--resume", type=Path, help="Verify prior runs after container restart")
    args = parser.parse_args()
    if bool(args.submit_synthetic) == bool(args.resume):
        parser.error("Choose exactly one of --submit-synthetic or --resume")
    base = args.url.rstrip("/")

    def read(path, data=None, headers=None):
        req = Request(
            base + path,
            data=json.dumps(data).encode() if data is not None else None,
            headers={"Content-Type": "application/json", **(headers or {})},
        )
        with urlopen(req, timeout=60) as response:
            return response.read(), dict(response.headers)

    def get(path):
        return json.loads(read(path)[0])

    assert get("/healthz")["status"] == "alive"
    html = read("/")[0].decode()
    assert '<div id="root">' in html
    import re

    for asset in re.findall(r'(?:src|href)="([^"]+)"', html):
        assert not asset.startswith(("http:", "https:", "//"))
        assert read("/" + asset.lstrip("./"))[0]
    catalog = get("/monitoring/catalog")
    instance = catalog["service_instance_id"]
    headers = {"X-TokenScope-Instance-Id": instance}
    if args.submit_synthetic:
        manifest = json.loads(args.submit_synthetic.read_text())
        assert manifest["kind"] == "synthetic_not_production"
        runs = []
        for item in manifest["files"]:
            path = args.submit_synthetic.parent / Path(item["file_ref"]).name
            assert hashlib.sha256(path.read_bytes()).hexdigest() == item["sha256"]
            key = "release-smoke-" + str(uuid.uuid4())
            payload = {"file_ref": path.name, "model_id": item["model_id"], "submission_key": key}
            run = json.loads(read("/analysis-runs", payload, headers)[0])
            started = time.monotonic()
            while True:
                status = get("/analysis-runs/" + run["run_id"])
                if status["status"] not in ("queued", "running"):
                    break
                if time.monotonic() - started > 7200:
                    raise TimeoutError("Synthetic run exceeded 7200 seconds")
                time.sleep(1)
            assert status["status"] == "completed", status
            duplicate = json.loads(read("/analysis-runs", payload, headers)[0])
            assert duplicate["run_id"] == run["run_id"]
            runs.append(
                {
                    "run_id": run["run_id"],
                    "submission_key": key,
                    "model_id": item["model_id"],
                    "seconds": time.monotonic() - started,
                }
            )
    else:
        prior = json.loads(args.resume.read_text())
        assert prior["service_instance_id"] == instance
        runs = prior["runs"]
    scopes = []
    for run in runs:
        receipt = json.loads(
            read("/analysis-submissions/" + run["submission_key"], headers=headers)[0]
        )
        assert receipt["run_id"] == run["run_id"] and receipt["status"] == "completed"
        prefix = "/analysis-runs/" + run["run_id"]
        metrics = get(prefix + "/metrics")["groups"]
        assert len(metrics) == 5
        for group in metrics:
            appid = group["appid"]
            raw, snapshot_headers = read(prefix + "/view-snapshot?" + urlencode({"appid": appid}))
            snapshot = json.loads(raw)
            totals = snapshot["metrics"]["totals"]
            assert int(totals["prompt_tokens"]) == int(totals["ideal_cached_input_tokens"]) + int(
                totals["ideal_compute_input_tokens"]
            )
            assert totals == {k: str(v) for k, v in group["totals"].items()}
            assert snapshot["identity"]["run_id"] == run["run_id"]
            assert snapshot["identity"]["appid"] == appid
            assert (
                sum(
                    len(h["bins"])
                    for metric in snapshot["distributions"].values()
                    for h in metric.values()
                )
                == 1029
            )
            etag = '"' + hashlib.sha256(raw).hexdigest() + '"'
            assert snapshot_headers.get("ETag", snapshot_headers.get("etag")) == etag
            try:
                read(
                    prefix + "/view-snapshot?" + urlencode({"appid": appid}),
                    headers={"If-None-Match": etag},
                )
                raise AssertionError("Expected 304")
            except HTTPError as exc:
                assert exc.code == 304
            request_page = get(prefix + "/requests?" + urlencode({"appid": appid, "limit": 50}))
            assert request_page["items"]
            digest = hashlib.sha256()
            export, export_headers = read(
                prefix + "/requests/export?" + urlencode({"appid": appid, "format": "ndjson"})
            )
            lines = export.splitlines(keepends=True)
            assert json.loads(lines[0])["type"] == "metadata"
            for line in lines[1:-1]:
                assert line.endswith(b"\n") and json.loads(line)["type"] == "request"
                digest.update(line)
            summary = json.loads(lines[-1])
            count = len(lines) - 2
            assert summary["type"] == "summary"
            assert summary["request_lines_sha256"] == digest.hexdigest()
            assert int(summary["actual_rows"]) == count == group["request_count"]
            csv_body, _ = read(
                prefix + "/requests/export?" + urlencode({"appid": appid, "format": "csv"})
            )
            rows = list(csv.reader(io.StringIO(csv_body.decode())))
            assert len(rows) - 1 == count and all(len(row) == 14 for row in rows)
            scopes.append(
                {
                    "run_id": run["run_id"],
                    "appid": appid,
                    "rows": count,
                    "snapshot_sha256": hashlib.sha256(raw).hexdigest(),
                    "ndjson_sha256": hashlib.sha256(export).hexdigest(),
                    "csv_sha256": hashlib.sha256(csv_body).hexdigest(),
                }
            )
    with urlopen(
        base + "/monitoring/events?" + urlencode({"after": instance + ":0"}), timeout=30
    ) as response:
        while True:
            line = response.readline()
            if line.startswith(b"data: "):
                event = json.loads(line[6:])
                if event.get("run_id") in {r["run_id"] for r in runs}:
                    assert event["status"] == "completed"
                    break
            if not line:
                raise AssertionError("SSE ended without persistent terminal event")
    if args.resume:
        assert scopes == prior["scopes"], "Published result bytes changed after restart"
    report = {
        "kind": "synthetic_container_acceptance_not_production",
        "url": base,
        "service_instance_id": instance,
        "runs": runs,
        "scopes": scopes,
        "restart_verified": bool(args.resume),
        "passed": True,
    }
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2) + "\n")
    print(
        json.dumps({"passed": True, "scopes": len(scopes), "restart_verified": bool(args.resume)})
    )


if __name__ == "__main__":
    main()
