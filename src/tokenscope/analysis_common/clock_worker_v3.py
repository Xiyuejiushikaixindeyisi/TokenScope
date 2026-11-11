"""Automatic discovery, frozen A/B replay and checkpointed sample reports."""

import json
from pathlib import Path
from typing import Any, Literal

from tokenscope.analysis_common.evaluation_v3 import (
    WindowEvaluation3,
    evaluate_window,
    stopped_status,
)
from tokenscope.analysis_common.execution_v3 import WorkerSpec3
from tokenscope.analysis_common.modifications import value_digest
from tokenscope.analysis_common.preparation_store import PreparationStore
from tokenscope.analysis_common.runtime_v3 import BudgetLedger, CheckpointJournal
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
        max_bytes=spec.profile.sample.max_metadata_bytes,
    )
    # Reserve bounded finalization before entering cancellable computation.
    control.reserve_many(
        {"checkpoints": 2, "result_bytes": 2 * spec.profile.sample.max_metadata_bytes}
    )
    atomic_json(root / "phase.json", {"phase": "selection", "deadline": control.enter("selection")})
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
        "recommendations": [],
        "business_note": (
            "所有改法仅在样本副本实算；删除动态内容或固定session_clock"
            "可能改变业务信息/时间感知，需业务确认。"
        ),
        "automatic_full": False,
    }

    def publish(number: int) -> None:
        filename = f"report-{number:04d}.json"
        payload = json.dumps(report, ensure_ascii=False).encode()
        if len(payload) > spec.profile.sample.max_metadata_bytes:
            raise TokenScopeError("RESULT_BYTE_LIMIT", "Report artifact exceeds limit", 409)
        atomic_json(root / filename, report)
        journal.commit("report", filename)

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
    atomic_json(root / "phase.json", {"phase": "model", "deadline": control.enter("model")})
    for number, finding in enumerate(discovery.findings, 1):
        # Freeze A's recipe before opening B. Each window has separate ledgers,
        # exact key/order conservation and no tuning from review observations.
        control.reserve("checkpoints", 8)
        item: dict[str, Any] = {
            "finding": finding.model_dump(mode="json"),
            "transformation_digest": value_digest(finding.recipe.model_dump(mode="json")),
            "windows": [],
        }
        report["recommendations"].append(item)
        roles: tuple[Literal["discovery", "review"], ...] = ("discovery", "review")
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
                result = evaluate_window(window, finding, folder, control)
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
            # A's complete result survives B failures and parent/child crashes.
            atomic_json(root / f"window-{number:04d}-{role}.json", entry)
            journal.commit("window_evaluation", f"window-{number:04d}-{role}.json")
            publish(number * 2 + role_index)
    return {
        "state": "completed",
        "phase": "sample_evaluation",
        "finding_count": len(discovery.findings),
        "plan_count": len(report["recommendations"]),
        "report_available": True,
    }
