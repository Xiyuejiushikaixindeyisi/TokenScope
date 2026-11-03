"""Summarize preserved profile evidence; never edits raw runs."""

import json
import statistics
from pathlib import Path

ROOT = Path("artifacts/reviews/hv2-lowhit-20261103")


def read(name):
    return json.loads((ROOT / name / "result.json").read_bytes())


def normalize(value):
    if isinstance(value, dict):
        return {
            k: normalize(v)
            for k, v in value.items()
            if k not in ("scope_id", "finding_id", "base_run_id")
        }
    if isinstance(value, list):
        return [normalize(v) for v in value]
    return value


def main():
    rows = []
    for run in json.loads((ROOT / "profile-runs.json").read_bytes()):
        name = run["name"]
        if not name.endswith("detect"):
            continue
        old, new = read(name), read(name + "-after")
        a, b = old["result"], new["result"]
        assert old["input_sha256"] == new["input_sha256"]
        for field in (
            "reports",
            "detected",
            "retained",
            "retained_bytes",
            "retention_complete",
            "encoding_calls",
        ):
            assert normalize(a[field]) == normalize(b[field]), (name, field)
        assert a["telemetry"]["counts"] == b["telemetry"]["counts"], name
        rows.append(
            {
                "case": new["case"],
                "n": new["n"],
                "k": new["candidate_limit"],
                "wall_before": old["analysis_wall_seconds"],
                "wall_after": new["analysis_wall_seconds"],
                "cpu_after": new["analysis_cpu_seconds"],
                "rss_kib_after": new["process_peak_rss_kib"],
                "comparisons": [r["candidate_comparisons"] for r in b["reports"]],
                "source_raw_bytes_read": b["telemetry"]["counts"]["source.raw_bytes_read"],
                "token_ids_read": b["telemetry"]["counts"].get("source.token_ids_read", "0"),
                "encoding_calls": b["encoding_calls"],
                "detected": b["detected"],
                "retained": b["retained"],
                "exact_evidence_match": True,
            }
        )
    repeats = {}
    for case in ["schema", "mixed"]:
        before = [
            read(f"{case}-16-4-detect"),
            *(read(f"{case}-16-4-before-repeat{i}") for i in [2, 3]),
        ]
        after = [
            read(f"{case}-16-4-detect-after"),
            *(read(f"{case}-16-4-after-repeat{i}") for i in [2, 3]),
        ]
        repeats[case] = {
            phase: {
                field: {
                    "median": statistics.median(j[field] for j in runs),
                    "min": min(j[field] for j in runs),
                    "max": max(j[field] for j in runs),
                }
                for field in [
                    "analysis_wall_seconds",
                    "analysis_cpu_seconds",
                    "process_peak_rss_kib",
                ]
            }
            for phase, runs in [("before", before), ("after", after)]
        }
    full = []
    for case in ["mixed", "order"]:
        j = read(f"{case}-8-16-full-after")
        full.append(
            {
                "case": case,
                "wall": j["analysis_wall_seconds"],
                "cpu": j["analysis_cpu_seconds"],
                "rss_kib": j["process_peak_rss_kib"],
                "status": j["result"]["receipt_status"],
                "encoding_calls": j["result"]["report"]["encoding_calls"],
                "phase_costs": j["evaluation_phase_costs"],
                "telemetry": j["result"]["telemetry"],
                "experiments": [e["data"]["status"] for e in j["result"]["experiments"]],
            }
        )
    output = {
        "synthetic": True,
        "profile_instrumented": True,
        "isolated_process_per_case": True,
        "system_exclusive": False,
        "rows": rows,
        "repeat_comparisons": repeats,
        "full": full,
    }
    (ROOT / "profile-summary.json").write_text(json.dumps(output, indent=2))
    lines = [
        "# HV2-R2 low-hit 合成profile实测",
        "",
        "全部固定GLM-5.2、seed=20261103、user_v2独立小来源；每例独立进程。cProfile与其它session并行会影响耗时，RSS含模型初始化，不能外推生产SLA。24检测例前后输入及规范化证据（仅去本次run/scope/finding身份）逐项相同，读取/编码/发现/保留计数完全相同。原证据不改。",
        "",
        "| 场景 | N | K | 比较L2/dynamic | 实际原文字节读取 | 编码调用 | "
        "wall前→后(s) | CPU后(s) | RSS后(KiB) |",
        "|---|---:|---:|---|---:|---:|---|---:|---:|",
    ]
    for r in rows:
        lines.append(
            f"| {r['case']} | {r['n']} | {r['k']} | {r['comparisons']} | "
            f"{r['source_raw_bytes_read']} | {r['encoding_calls']} | "
            f"{r['wall_before']:.4f}→{r['wall_after']:.4f} | "
            f"{r['cpu_after']:.4f} | {r['rss_kib_after']} |"
        )
    lines += [
        "",
        "schema/mixed各3次重复的min/median/max与pilot/full实测见同目录profile-summary.json。普通检测编码=0仍有读取、解析、正则、哈希、对比、序列化和存储成本。full-case的partial由保留/实验上限如实产生，不转成ready。阶段计时为嵌套累计，不能相加成总耗时。",
    ]
    (ROOT / "PROFILE_RESULTS.md").write_text("\n".join(lines) + "\n")
    print(json.dumps({"matched_cases": len(rows), "repeats": repeats, "full": full}, indent=2))


if __name__ == "__main__":
    main()
