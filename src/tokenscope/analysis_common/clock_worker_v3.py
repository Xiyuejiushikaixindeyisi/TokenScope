"""Automatic discovery, frozen A/B replay and checkpointed sample reports."""

import json
from pathlib import Path
from typing import Any, Literal

from tokenscope.analysis_common.evaluation_v3 import (
    SampleBaseline3,
    WindowEvaluation3,
    evaluate_window,
    stopped_status,
)
from tokenscope.analysis_common.execution_v3 import WorkerSpec3
from tokenscope.analysis_common.modifications import value_digest
from tokenscope.analysis_common.preparation_store import PreparationStore
from tokenscope.analysis_common.runtime_v3 import BudgetLedger, CheckpointJournal
from tokenscope.analysis_common.sample_evidence_v3 import example_for
from tokenscope.analysis_common.sample_source import open_sample_window
from tokenscope.analysis_common.supervisor_v3 import atomic_json
from tokenscope.errors import TokenScopeError
from tokenscope.monitoring.service import MonitoringService
from tokenscope.prefix_analysis.clock_discovery_v3 import collect_clock


def diagnose_clock(spec: WorkerSpec3, control: BudgetLedger) -> dict[str, Any]:
    if spec.sample_preparation_id is None:
        raise TokenScopeError("SAMPLE_REFERENCE_REQUIRED", "Completed preparation required", 422)
    store = PreparationStore(Path(spec.state_root) / "diagnostics-v3")
    receipt = store.receipt(spec.sample_preparation_id)
    if receipt.state != "completed" or receipt.manifest_sha256 is None:
        raise TokenScopeError("SAMPLE_NOT_READY", "Preparation is incomplete", 409)
    if store.request(receipt.preparation_id).intent_digest != spec.request.intent_digest:
        raise TokenScopeError("SAMPLE_INTENT_MISMATCH", "Sample belongs to another intent", 409)
    execution = store.execution(receipt.preparation_id)
    parent = (store.root / "jobs" / receipt.preparation_id).resolve(strict=True)
    manifest = (parent / execution.telemetry["manifest_path"]).resolve(strict=True)
    if not manifest.is_relative_to(parent) or manifest.name != "manifest.json":
        raise TokenScopeError("INVALID_ARTIFACT", "Sample reference escapes task", 409)
    base = MonitoringService(
        Path(spec.input_root), Path(spec.state_root), Path(spec.asset_root), spec.profile.cpu_budget
    )
    source = open_sample_window(
        base,
        manifest.parent,
        receipt.manifest_sha256,
        "discovery",
        metadata_limit=spec.profile.sample.max_metadata_bytes,
        control=control,
    )
    root = Path(spec.job_root)
    journal = CheckpointJournal(
        root,
        max_entries=spec.profile.budgets["checkpoints"],
        max_bytes=spec.profile.max_file_bytes,
    )
    # Reserve bounded finalization before entering cancellable computation.
    control.reserve_many(
        {"checkpoints": 2, "result_bytes": 2 * spec.profile.sample.max_metadata_bytes}
    )
    control.enter("selection")
    atomic_json(root / "phase.json", {"phase": "selection"})
    discovery = collect_clock(source, control)
    data = discovery.model_dump(mode="json")
    if len(json.dumps(data, ensure_ascii=False).encode()) > spec.profile.sample.max_metadata_bytes:
        raise TokenScopeError("RESULT_BYTE_LIMIT", "Discovery artifact exceeds limit", 409)
    atomic_json(root / "findings.json", data)
    journal.commit("findings", "findings.json")
    report: dict[str, Any] = {
        "version": "diagnostics-report-3",
        "task_id": spec.job_id,
        "sample_id": receipt.sample_id,
        "manifest_sha256": receipt.manifest_sha256,
        "sample": source.manifest.model_dump(mode="json"),
        "discovery": data,
        "recommendations": [
            {
                "finding": f.model_dump(mode="json"),
                "transformation_digest": value_digest(f.recipe.model_dump(mode="json")),
                "windows": [],
            }
            for f in discovery.findings
        ],
        "business_note": (
            "所有改法仅在样本副本实算；删除动态内容或固定session_clock"
            "可能改变业务信息/时间感知，需业务确认。"
        ),
        "automatic_full": False,
        "evidence_mode": "sealed_examples",
        "evidence_refs": {},
    }

    def publish(number: int) -> None:
        filename = f"report-{number:04d}.json"
        payload = json.dumps(report, ensure_ascii=False).encode()
        if len(payload) > spec.profile.sample.max_metadata_bytes:
            raise TokenScopeError("RESULT_BYTE_LIMIT", "Report artifact exceeds limit", 409)
        atomic_json(root / filename, report)
        journal.commit("report", filename)

    def save_example(owner: dict[str, Any], plan: Path | None = None) -> None:
        example = example_for(source, owner, spec.job_id, plan)
        filename = f"evidence-{journal.sequence + 1:06d}.json"
        payload = {
            "task_id": spec.job_id,
            "sample_id": receipt.sample_id,
            "owner_id": example.owner_id,
            "examples": [example.model_dump(mode="json")],
        }
        if (
            len(json.dumps(payload, ensure_ascii=False).encode())
            > spec.profile.sample.max_metadata_bytes
        ):
            raise TokenScopeError("RESULT_BYTE_LIMIT", "Evidence exceeds limit", 409)
        atomic_json(root / filename, payload)
        journal.commit("window_evaluation", filename)
        report["evidence_refs"][example.owner_id] = filename

    for rule in ("L4", "L5"):
        groups = [g for g in discovery.cause_groups if g.rule_id == rule and g.comparison]
        for group in groups[:3]:
            save_example(group.model_dump(mode="json"))
    for finding in discovery.findings:
        save_example(finding.model_dump(mode="json"))
    publish(0)
    if not discovery.findings:
        return {
            "state": "completed" if discovery.complete else "stopped",
            "phase": "prefix_discovery",
            "finding_count": 0,
            "reason_code": "NO_EXECUTABLE_CHANGE_EVIDENCE"
            if discovery.complete
            else discovery.reason_codes[-1],
            "report_available": True,
        }
    control.enter("model")
    atomic_json(root / "phase.json", {"phase": "model"})
    # Admission follows the finite discovered work, not arbitrary 32-plan caps.
    # Memory and per-artifact byte limits stay fixed; each plan releases its arrays.
    roles: tuple[Literal["discovery", "review"], ...] = tuple(
        window.role for window in source.manifest.decision.windows
    )
    count = len(discovery.findings) * len(roles)
    sample = source.manifest.decision.limits
    budgets = dict(control.profile.budgets)
    for name, limit in {
        "requests": sample.max_requests * (8 + count * 4),
        "raw_read_bytes": sample.max_raw_bytes * (8 + count * 4),
        "token_read_bytes": sample.max_prompt_tokens * 4 * (4 + count * 2),
        "verification_bytes": sample.max_snapshot_bytes * (16 + count * 12),
        "encoding_calls": sample.max_requests * (len(roles) + count),
        "encoding_input_bytes": sample.max_raw_bytes * (len(roles) + count),
        "encoding_output_tokens": sample.max_prompt_tokens * (len(roles) + count) * 2,
        "plans": max(1, count),
        "plan_bytes": spec.profile.max_file_bytes * max(1, count),
        "result_bytes": sample.max_metadata_bytes * (4 + count),
    }.items():
        budgets[name] = control.consumed.get(name, 0) + limit
    control.profile = control.profile.model_copy(update={"budgets": budgets})
    baselines: dict[str, SampleBaseline3] = {}
    for number, finding in enumerate(discovery.findings, 1):
        # Freeze A's recipe before opening B. Each window has separate ledgers,
        # exact key/order conservation and no tuning from review observations.
        control.reserve("checkpoints", 8)
        item = report["recommendations"][number - 1]
        for role_index, role in enumerate(roles):
            folder = root / f"evaluation-{number:04d}" / role
            try:
                window = (
                    source
                    if role == "discovery"
                    else open_sample_window(
                        base,
                        manifest.parent,
                        receipt.manifest_sha256,
                        "review",
                        metadata_limit=spec.profile.sample.max_metadata_bytes,
                        control=control,
                    )
                )
                if role not in baselines:
                    baseline = SampleBaseline3(window, control)
                    baseline.prepare(root / ("baseline-" + role))
                    baselines[role] = baseline
                result = evaluate_window(window, finding, folder, control, baselines[role])
            except TokenScopeError as exc:
                result = WindowEvaluation3(
                    role=role,
                    status="unavailable"
                    if exc.code == "REVIEW_UNAVAILABLE"
                    else stopped_status(exc.code),
                    transformation_digest=item["transformation_digest"],
                    reason_code=exc.code,
                )
            entry = result.model_dump(mode="json")
            for key in ("rows_ref", "plan_ref"):
                if entry[key]:
                    path = folder / entry[key]
                    entry[key] = str(path.relative_to(root))
                    journal.commit("window_evaluation", entry[key])
            item["windows"].append(entry)
            if role == "discovery":
                save_example(
                    item["finding"], root / entry["plan_ref"] if entry["plan_ref"] else None
                )
            # A's complete result survives B failures and parent/child crashes.
            atomic_json(root / f"window-{number:04d}-{role}.json", entry)
            journal.commit("window_evaluation", f"window-{number:04d}-{role}.json")
            publish(number * 2 + role_index)
    incomplete = [
        w
        for item in report["recommendations"]
        for w in item["windows"]
        if not w["complete"] and w["status"] not in ("no_targets", "no_op")
    ]
    return {
        "state": "stopped" if incomplete or not discovery.complete else "completed",
        "reason_code": (
            incomplete[0]["reason_code"]
            if incomplete
            else discovery.reason_codes[-1]
            if not discovery.complete
            else None
        ),
        "phase": "sample_evaluation",
        "finding_count": len(discovery.findings),
        "plan_count": len(report["recommendations"]),
        "report_available": True,
    }
