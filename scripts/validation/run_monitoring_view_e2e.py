"""Real-network presentation checks invoked by the full synthetic pipeline runner."""

import hashlib
import json
import math
import time
from urllib.parse import quote

import httpx


def check_views(base, run_id, metrics):
    checks = []
    with httpx.Client(base_url=base, timeout=60) as client:
        catalog = client.get("/monitoring/catalog").raise_for_status().json()
        assert any(x["active_run_id"] == run_id for x in catalog["items"])
        for group in metrics["groups"]:
            appid = group["appid"]
            path = f"/analysis-runs/{run_id}"
            snapshot = client.get(
                path + "/view-snapshot", params=dict(appid=appid)
            ).raise_for_status()
            value = snapshot.json()
            assert value["metrics"]["request_count"] == str(group["request_count"])
            assert value["metrics"]["ideal_hit_rate"] == group["ideal_hit_rate"]
            for name, total in group["totals"].items():
                assert value["metrics"]["totals"][name] == str(total)
            assert (
                client.get(
                    path + "/view-snapshot",
                    params=dict(appid=appid),
                    headers={"If-None-Match": snapshot.headers["etag"]},
                ).status_code
                == 304
            )
            endpoint = path + "/requests?appid=" + quote(appid) + "&limit=50"
            latencies = {}
            for name, url in (
                ("catalog", "/monitoring/catalog?limit=100"),
                ("snapshot", path + "/view-snapshot?appid=" + quote(appid)),
                ("requests", endpoint),
            ):
                times = []
                for _ in range(30):
                    started = time.perf_counter()
                    client.get(url).raise_for_status()
                    times.append((time.perf_counter() - started) * 1000)
                latencies[name] = sorted(times)[math.ceil(0.95 * len(times)) - 1]
                assert latencies[name] <= (300 if name == "catalog" else 500), latencies
            digest = hashlib.sha256()
            rows = 0
            with client.stream(
                "GET", path + "/requests/export", params=dict(appid=appid, format="ndjson")
            ) as response:
                response.raise_for_status()
                for raw in response.iter_lines():
                    item = json.loads(raw)
                    if item["type"] == "request":
                        digest.update(raw.encode() + b"\n")
                        rows += 1
                    elif item["type"] == "summary":
                        assert item["actual_rows"] == str(rows)
                        assert item["request_lines_sha256"] == digest.hexdigest()
                assert rows == group["request_count"] == int(response.headers["X-Export-Row-Count"])
            checks.append(
                dict(
                    appid=appid,
                    p95_ms=latencies,
                    snapshot_bytes=len(snapshot.content),
                    export_rows=rows,
                )
            )
        with client.stream(
            "GET", "/monitoring/events", params=dict(after=catalog["service_instance_id"] + ":0")
        ) as response:
            response.raise_for_status()
            seen = []
            for line in response.iter_lines():
                if line.startswith("data: "):
                    event = json.loads(line[6:])
                    seen.append(event)
                    if event.get("run_id") == run_id:
                        assert event["status"] == "completed"
                        break
            assert seen
    return checks
