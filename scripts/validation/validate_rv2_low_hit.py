"""RV2-L acceptance against a fresh copy of frozen RV1; run from project root."""

import argparse
import hashlib
import json
import shutil
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient

from tokenscope.analysis_common.encoding import EncodingContext
from tokenscope.analysis_common.service import DiagnosticService
from tokenscope.api.app import create_app
from tokenscope.monitoring.service import MonitoringService
from tokenscope.token_content.current_plugin import CurrentTokenContentPlugin

parser = argparse.ArgumentParser(
    description="Read-only RV1 aggregation acceptance; never generate reports"
)
parser.add_argument("--output", type=Path, required=True)
args = parser.parse_args()
out = args.output.resolve()
out.mkdir(parents=True, exist_ok=False)
original = Path("artifacts/validation/unified-rv1-20261101-01").resolve()


def hashes(p):
    return {
        str(f.relative_to(p)): hashlib.sha256(f.read_bytes()).hexdigest()
        for f in p.rglob("*")
        if f.is_file()
    }


before = hashes(original)
copy = out / "rv1-copy"
assert not copy.exists()
shutil.copytree(original, copy)
prior = json.loads((original / "actual-unified-rv1.json").read_text())
service = MonitoringService(copy / "inputs", copy / "state")
responses = {}
aggregates = []


def forbidden(*a, **k):
    raise AssertionError("GET triggered analysis/write")


with (
    patch.object(DiagnosticService, "submit", forbidden),
    patch.object(DiagnosticService, "process_next", forbidden),
    patch.object(EncodingContext, "encode", forbidden),
    patch.object(CurrentTokenContentPlugin, "analyze_request", forbidden),
    TestClient(create_app(service, start_worker=False)) as c,
):
    cap = c.get("/diagnostics/recommendations/capabilities").json()
    assert cap["service_instance_id"] == prior["service_instance_id"]
    c.headers["x-tokenscope-service-instance"] = cap["service_instance_id"]

    def get(url, expected=200):
        v = c.get(url)
        assert v.status_code == expected, (url, v.status_code, v.text)
        responses[url] = v.json()
        return v.json()

    catalog = get("/diagnostics/discovery/catalog")
    assert catalog["defaults"] == prior["catalog"]["defaults"]
    for t in prior["tasks"]:
        base = "/diagnostics/tasks/" + t["task_id"]
        s = get(base + "/recommendation-summary")
        assert s == t["summary"]
        assert get("/diagnostics/discovery/tasks/" + t["task_id"] + "/terminal") == t["terminal"]
        for kind, field in [
            ("recommendations", "recommendations"),
            ("difference-groups", "difference_groups"),
        ]:
            allitems = get(base + "/" + kind)["items"]
            assert allitems == t[field]["items"]
            paged = []
            offset = "0"
            while offset is not None:
                page = get(base + "/" + kind + "?limit=1&offset=" + offset)
                paged += page["items"]
                offset = page["next_offset"]
            assert paged == allitems
            for item in allitems:
                url = base + "/" + kind + "/" + item["id"] + "/examples"
                assert get(url) == t["examples"][url]
        groups = get(base + "/difference-groups")["items"]
        rule_results = {}
        for rule in ("L4", "L5"):
            selected = [i["data"] for i in groups if i["data"]["rule_id"] == rule]
            keys = {json.dumps(k, sort_keys=True) for g in selected for k in g["member_requests"]}
            assert len(keys) == 6
            samples = []
            seen = set()
            example_reads = 0
            for g in [g for g in selected if g["example_refs"]][:3]:
                example_reads += 1
                page = get(base + "/difference-groups/" + g["group_id"] + "/examples")
                for item in page["items"]:
                    e = item["data"]
                    assert e["owner_id"] == g["group_id"]
                    sides = [e["before"]["source"], e["comparison"]["source"]]
                    signature = tuple(sorted(json.dumps(x, sort_keys=True) for x in sides))
                    if signature in seen:
                        continue
                    seen.add(signature)
                    samples.append(
                        {
                            "owner_id": e["owner_id"],
                            "example_id": e["example_id"],
                            "before": e["before"],
                            "comparison": e["comparison"],
                        }
                    )
                    break
            assert len(samples) <= 3 and example_reads <= 3
            assert all(g["members_complete"] for g in selected)
            rule_results[rule] = {
                "group_count": len(selected),
                "unique_requests": len(keys),
                "summed_group_members": sum(len(g["member_requests"]) for g in selected),
                "members_complete": all(g["members_complete"] for g in selected),
                "request_keys": [json.loads(k) for k in sorted(keys)],
                "reason_codes": sorted({c for g in selected for c in g["reason_codes"]}),
                "example_reads": example_reads,
                "representatives": samples,
            }
        assert rule_results["L4"]["group_count"] == 20 and rule_results["L5"]["group_count"] == 9
        assert int(t["summary"]["difference_group_count"]) == 29
        aggregates.append({"task_id": t["task_id"], "label": t["label"], "rules": rule_results})
        get(base + "/recommendations?offset=01", 422)
        get(base + "/recommendations?limit=101", 422)
        v = c.get(base + "/recommendations", headers={"x-tokenscope-service-instance": "wrong"})
        assert v.status_code == 409
    (out / "rv1-final-responses.json").write_text(
        json.dumps(responses, ensure_ascii=False, indent=2)
    )
assert hashes(original) == before
(out / "aggregation.json").write_text(json.dumps(aggregates, ensure_ascii=False, indent=2))
(out / "rv1-final-readonly.json").write_text(
    json.dumps(
        {
            "result": "pass",
            "get_routes": len(responses),
            "original_files_unchanged": len(before),
            "instance": prior["service_instance_id"],
            "copied_state": str(copy),
            "guarded": ["submit", "process_next", "encode", "analyze_request"],
            "defaults_same": True,
        },
        indent=2,
    )
)
print((out / "rv1-final-readonly.json").read_text())
