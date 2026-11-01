"""Manual diagnostics: frozen source, low-hit experiments, then original Token content."""

import hashlib
import json
import sqlite3
from dataclasses import asdict
from itertools import combinations
from pathlib import Path
from typing import Any
from uuid import uuid4

from tokenscope.analysis_common.contracts import (
    AnalysisFragment,
    AnalysisScope,
    DiagnosticRequest,
    ModificationCandidate,
    ModificationPlan,
    TaskReceipt,
    canonical_metadata,
    metadata_wire,
)
from tokenscope.analysis_common.evaluation import evaluate_plan
from tokenscope.analysis_common.plugins import (
    EvidenceCapabilities,
    ExecutionStopped,
    PluginRegistry,
    RunControl,
)
from tokenscope.analysis_common.presentation import evaluation_view
from tokenscope.analysis_common.recommendation_pipeline import run_extension
from tokenscope.analysis_common.recommendation_runtime import RecommendationSettings
from tokenscope.analysis_common.runtime import RuntimeOptions, TaskControl
from tokenscope.analysis_common.source import ResolvedSource, SourceResolver
from tokenscope.analysis_common.storage import DiagnosticStore, ResultWriter, read_items
from tokenscope.analysis_common.wire import from_wire, to_wire
from tokenscope.errors import TokenScopeError
from tokenscope.prefix_analysis.comparison import read_comparison
from tokenscope.prefix_analysis.detection import collect_dynamics
from tokenscope.prefix_analysis.experiments import compile_combination, run_experiment
from tokenscope.prefix_analysis.service import PrefixFinding, collect_l2


class DiagnosticService:
    def __init__(
        self,
        resolver: SourceResolver,
        registry: PluginRegistry,
        recommendations: RecommendationSettings | None = None,
    ) -> None:
        self.resolver = resolver
        self.base = resolver.base
        self.registry = registry
        self.recommendations = recommendations
        self.store = DiagnosticStore(self.base.state_root / "diagnostics")

    def submit(self, request: DiagnosticRequest, options: RuntimeOptions) -> TaskReceipt:
        if self.recommendations is not None:
            # T1 stays readable in historical tasks, but is deliberately disabled in new profiles.
            selection = options.token_selection.model_copy(
                update={"rule_ids": tuple(r for r in options.token_selection.rule_ids if r != "T1")}
            )
            options = options.model_copy(update={"token_selection": selection})
        try:
            plugin = self.registry.get("token_content")
        except ExecutionStopped:
            plugin = None  # Capability absence is an explicit stage outcome, not empty success.
        if plugin:
            plugin.validate_selection(options.token_selection)
        source = self.resolver.resolve_scope(request.source)
        intent = {
            "kind": "analysis",
            "request": request.model_dump(exclude={"submission_key"}),
            "plugin": plugin.describe().model_dump() if plugin else None,
        }
        if self.recommendations is not None:
            with self.store.connect(True) as db:
                prior = db.execute(
                    "SELECT intent FROM tasks WHERE submission_key=?", (request.submission_key,)
                ).fetchone()
            if prior:
                frozen = json.loads(prior["intent"]).get("recommendations")
                if frozen is not None:
                    intent["recommendations"] = frozen
            else:
                try:
                    intent["recommendations"] = self.recommendations.snapshot()
                except (ValueError, OSError) as exc:
                    raise TokenScopeError(
                        "RECIPE_BUNDLE_INVALID", "Invalid recommendation configuration", 422
                    ) from exc
        return self.store.submit(
            request.submission_key,
            json.dumps(intent, sort_keys=True),
            source.scope.model_dump_json(),
            options.model_dump_json(),
        )

    def receipt(self, task_id: str) -> TaskReceipt:
        return self.store.receipt(task_id)

    def retry(self, task_id: str, submission_key: str) -> TaskReceipt:
        row = self.store.row(task_id)
        if row["status"] in ("queued", "running"):
            raise TokenScopeError("TASK_ACTIVE", "Active task cannot retry", 409)
        return self.store.submit(
            submission_key, row["intent"], row["scope"], row["options"], row["attempt"] + 1
        )

    def cancel(self, task_id: str) -> TaskReceipt:
        return self.store.cancel(task_id)

    def report(self, task_id: str) -> dict[str, Any]:
        result: dict[str, Any] = json.loads(
            (self.store.result_directory(task_id) / "report.json").read_bytes()
        )
        return result

    def items(
        self, task_id: str, kind: str, key: str | None = None, offset: int = 0, limit: int = 100
    ) -> list[dict[str, Any]]:
        return read_items(self.store.result_directory(task_id), kind, key, offset, limit)

    def item(self, task_id: str, kind: str, key: str) -> dict[str, Any]:
        items = self.items(task_id, kind, key)
        if not items:
            raise TokenScopeError("EVIDENCE_NOT_FOUND", "Unknown report evidence", 404)
        result: dict[str, Any] = items[0]["data"]
        return result

    def source(self, row: dict[str, Any]) -> ResolvedSource:
        scope = AnalysisScope.model_validate_json(row["scope"])
        source = ResolvedSource(
            self.base, scope, self.base.state_root / "runs" / scope.source.base_run_id
        )
        source.verify()
        return source

    def evaluation_rows(
        self, task_id: str, evaluation_id: str, offset: int = 0, limit: int = 100
    ) -> list[dict[str, Any]]:
        if offset < 0 or not 1 <= limit <= 100:
            raise TokenScopeError("INVALID_ARGUMENT", "Invalid page", 422)
        directory = self.store.result_directory(task_id)
        items = read_items(directory, "evaluation", evaluation_id, 0, 1)
        if not items:
            raise TokenScopeError("EVIDENCE_NOT_FOUND", "Unknown evaluation", 404)
        evaluation = items[0]["data"]
        if evaluation["status"] != "available" or evaluation["manifest_ref"] is None:
            raise TokenScopeError("EVALUATION_INCOMPLETE", "No complete row evidence", 409)
        path = (directory / evaluation["manifest_ref"]).resolve()
        if directory.resolve() not in path.parents:
            raise TokenScopeError("REPORT_DIGEST_MISMATCH", "Invalid evidence path", 409)
        db = sqlite3.connect(path.as_uri() + "?mode=ro", uri=True)
        try:
            return [
                {"source_record_index": str(index), "evidence": metadata_wire(json.loads(raw))}
                for index, raw in db.execute(
                    "SELECT request_index,evidence_json FROM rows "
                    "ORDER BY json_extract(evidence_json,'$.sequence'),request_index "
                    "LIMIT ? OFFSET ?",
                    (limit, offset),
                )
            ]
        finally:
            db.close()

    def comparison(self, task_id: str, finding_id: str) -> dict[str, Any]:
        finding = from_wire(PrefixFinding, self.item(task_id, "finding", finding_id))
        source = self.source(self.store.row(task_id))
        left, right = read_comparison(source, finding.comparison)
        return {
            "comparison": to_wire(finding.comparison),
            "left_raw_body": left,
            "right_raw_body": right,
            "raw_body_complete": True,
        }

    def request_body(self, task_id: str, fragment_id: str) -> dict[str, Any]:
        fragment = from_wire(AnalysisFragment, self.item(task_id, "fragment", fragment_id))
        source = self.source(self.store.row(task_id))
        request = source.read_request(fragment.request_key)
        if request.raw_sha256 != fragment.raw_sha256:
            raise TokenScopeError("SOURCE_DIGEST_MISMATCH", "Evidence source differs", 409)
        return {
            "request_key": to_wire(request.request_key),
            "raw_body": request.raw_body,
            "raw_sha256": request.raw_sha256,
            "raw_body_complete": request.raw_body_complete,
            "scope_id": request.scope_id,
            "capture_truncation": request.capture_truncation,
        }

    def submit_token_evaluation(
        self,
        task_id: str,
        fragment_id: str,
        candidate_id: str,
        parameters_json: str,
        business_basis_ref: str | None,
        submission_key: str,
    ) -> TaskReceipt:
        # Membership checked before queueing; compile against sealed evidence in the worker.
        fragment = from_wire(AnalysisFragment, self.item(task_id, "fragment", fragment_id))
        if candidate_id not in {c.candidate_id for c in fragment.modification_candidates}:
            raise TokenScopeError("CANDIDATE_NOT_FOUND", "Unknown candidate in report", 404)
        row = self.store.row(task_id)
        intent = {
            "kind": "token_evaluation",
            "parent": task_id,
            "fragment_id": fragment_id,
            "candidate_id": candidate_id,
            "parameters_json": parameters_json,
            "business_basis_ref": business_basis_ref,
            "plugin": json.loads(row["intent"])["plugin"],
        }
        return self.store.submit(
            submission_key, json.dumps(intent, sort_keys=True), row["scope"], row["options"]
        )

    def process_next(self) -> TaskReceipt | None:
        import fcntl

        with (self.base.state_root / "worker.lock").open("a") as lock:
            try:
                fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError:
                return None
            self.store.recover()
            task_id = self.store.claim_next()
            if task_id is None:
                return None
            row = self.store.row(task_id)
            workspace = self.store.root / (task_id + ".working-" + str(uuid4()))
            writer: ResultWriter | None = None
            closed = False
            try:
                workspace.mkdir()
                writer = ResultWriter(workspace)
                source = self.source(row)
                options = RuntimeOptions.model_validate_json(row["options"])
                control = TaskControl(options, lambda: bool(self.store.row(task_id)["cancel"]))
                self._preflight(source, control)
                intent = json.loads(row["intent"])
                plan: ModificationPlan | None
                if intent["kind"] == "analysis":
                    report = self._analyze(
                        task_id, source, intent, options, control, writer, workspace
                    )
                elif intent["kind"] in ("token_evaluation", "token_authorization"):
                    report = self._token_evaluate(source, intent, control, writer, workspace)
                elif intent["kind"] == "combination":
                    plans = self._referenced_plans(source.scope, intent["plan_refs"])
                    operations = tuple(operation for plan in plans for operation in plan.operations)
                    plan = ModificationPlan(
                        plan_id=str(uuid4()),
                        version="1",
                        source_scope_id=source.scope.scope_id,
                        transformation_digest=hashlib.sha256(
                            canonical_metadata(operations)
                        ).hexdigest(),
                        direction="low_hit"
                        if all(p.direction == "low_hit" for p in plans)
                        else "combined",
                        action_class="hypothetical_content_removal",
                        finding_refs=tuple(dict.fromkeys(f for p in plans for f in p.finding_refs)),
                        operations=operations,
                        combination_refs=tuple(p.plan_id for p in plans),
                    )
                    control.plan(len(plan.model_dump_json().encode()))
                    writer.add("plan", plan.plan_id, to_wire(plan))
                    result = evaluate_plan(source, plan, workspace / "evaluation", control=control)
                    if result.manifest_ref:
                        result = result.model_copy(
                            update={"manifest_ref": "evaluation/rows.sqlite3"}
                        )
                    writer.add("evaluation", result.evaluation_id, evaluation_view(result))
                    if result.display_eligible:
                        writer.add("optimization", result.evaluation_id, evaluation_view(result))
                    report = {
                        "status": "ready" if result.status == "available" else "partial",
                        "stages": [],
                        "evaluation_id": result.evaluation_id,
                        "combination_refs": intent["plan_refs"],
                    }
                else:
                    findings = tuple(
                        from_wire(PrefixFinding, self.item(intent["parent"], "finding", key))
                        for key in intent["finding_ids"]
                    )
                    plan = compile_combination(source, findings, control)
                    if plan is None:
                        report = {
                            "status": "partial",
                            "reason_codes": ["NO_APPLICABLE_TARGETS"],
                            "stages": [],
                        }
                    else:
                        writer.add("plan", plan.plan_id, to_wire(plan))
                        result = evaluate_plan(
                            source, plan, workspace / "evaluation", control=control
                        )
                        if result.manifest_ref:
                            result = result.model_copy(
                                update={"manifest_ref": "evaluation/rows.sqlite3"}
                            )
                        writer.add("evaluation", result.evaluation_id, evaluation_view(result))
                        if result.display_eligible:
                            writer.add(
                                "optimization", result.evaluation_id, evaluation_view(result)
                            )
                        report = {
                            "status": "ready" if result.status == "available" else "partial",
                            "stages": [],
                            "evaluation_id": result.evaluation_id,
                            "pilot_bypassed_by_explicit_request": True,
                        }
                control.checkpoint()
                source.verify()
                report.update(
                    scope=to_wire(source.scope),
                    scope_id=source.scope.scope_id,
                    runtime_options=to_wire(options),
                    encoding_calls=str(control.encoding_calls),
                )
                writer.close()
                closed = True
                status = "empty" if source.scope.request_count == 0 else report["status"]
                self.store.publish(task_id, workspace, report, status)
            except Exception as exc:
                # The worker boundary must record unexpected plugin failures without leaking bodies.
                code = getattr(exc, "code", "DIAGNOSTIC_EXECUTION_FAILED")
                self.store.update(
                    task_id,
                    status="interrupted" if code == "ANALYSIS_INTERRUPTED" else "failed",
                    active=None,
                    error=code,
                )
            finally:
                if not closed and writer is not None:
                    try:
                        writer.close()
                    except (OSError, sqlite3.Error):
                        self.store.update(
                            task_id, status="failed", active=None, error="STORAGE_UNAVAILABLE"
                        )
            return self.receipt(task_id)

    @staticmethod
    def _preflight(source: ResolvedSource, control: TaskControl) -> None:
        if source.scope.request_count > control.options.max_source_requests:
            raise ExecutionStopped("SOURCE_REQUEST_BUDGET_EXHAUSTED")
        total = 0
        # Bound raw bytes before recursive parsing or plan expansion; no body corpus is retained.
        for row in source._rows():
            control.checkpoint()
            length = len(row["request_input"].encode("utf-8"))
            if length > control.options.token_selection.budget.max_request_bytes:
                raise ExecutionStopped("REQUEST_BYTES_EXHAUSTED")
            total += length
            if total > control.options.max_source_bytes:
                raise ExecutionStopped("SOURCE_BYTES_EXHAUSTED")
            depth = 0
            quoted = escaped = False
            for char in row["request_input"]:
                if quoted:
                    if escaped:
                        escaped = False
                    elif char == "\\":
                        escaped = True
                    elif char == '"':
                        quoted = False
                elif char == '"':
                    quoted = True
                elif char in "[{":
                    depth += 1
                    if depth > control.options.token_selection.budget.max_depth:
                        raise ExecutionStopped("SOURCE_DEPTH_EXHAUSTED")
                elif char in "]}":
                    depth -= 1

    def _analyze(
        self,
        task_id: str,
        source: ResolvedSource,
        intent: dict[str, Any],
        options: RuntimeOptions,
        control: TaskControl,
        writer: ResultWriter,
        workspace: Path,
    ) -> dict[str, Any]:
        selection = intent["request"]["selection"]
        stages: list[dict[str, Any]] = []
        if selection["enable_low_hit"]:
            self.store.update(task_id, active="low_hit")
            try:
                stage = self._low_hit(
                    source,
                    options,
                    control,
                    writer,
                    workspace,
                    automatic_combinations="recommendations" not in intent,
                )
                stages.append(stage)
            except (
                ExecutionStopped,
                ValueError,
                RuntimeError,
                KeyError,
                IndexError,
                TypeError,
            ) as exc:
                if getattr(exc, "code", "") == "ANALYSIS_INTERRUPTED":
                    raise
                stages.append(
                    {
                        "direction": "low_hit",
                        "status": "partial",
                        "reason": getattr(exc, "code", "LOW_HIT_FAILED"),
                    }
                )
        control.checkpoint()
        source.verify()  # Shared corruption must not continue into the next direction.
        self.store.update(task_id, active="token_content")
        try:
            plugin = self.registry.get("token_content")
            if json.loads(plugin.describe().model_dump_json()) != intent["plugin"]:
                raise ExecutionStopped("PLUGIN_IDENTITY_CHANGED")
            checked, complete = 0, True
            for request in source.iter_requests():
                control.request(request)
                fragment = plugin.analyze_request(
                    request,
                    options.token_selection,
                    EvidenceCapabilities(),
                    RunControl(options.token_selection.budget, control.cancelled),
                )
                fragment = AnalysisFragment.model_validate_json(fragment.model_dump_json())
                location_ids = {item.location_id for item in fragment.locations}
                finding_ids = {item.finding_id for item in fragment.finding_candidates}
                if any(
                    not set(candidate.finding_refs) <= finding_ids
                    or any(
                        location.location_id not in location_ids for location in candidate.locations
                    )
                    for candidate in fragment.modification_candidates
                ):
                    raise ValueError("Plugin candidate has foreign references")
                if (
                    fragment.request_key != request.request_key
                    or fragment.raw_sha256 != request.raw_sha256
                ):
                    raise ValueError("Plugin returned foreign evidence")
                writer.add(
                    "fragment", str(request.request_key.source_record_index), to_wire(fragment)
                )
                writer.add(
                    "fragment_index",
                    str(request.request_key.source_record_index),
                    {
                        "location_ids": [item.location_id for item in fragment.locations],
                        "unit_ids": [item.unit_id for item in fragment.units],
                        "observation_ids": [item.observation_id for item in fragment.observations],
                    },
                )
                checked += 1
                complete &= fragment.coverage.complete
                control.checkpoint()
            stages.append(
                {
                    "direction": "token_content",
                    "status": "completed" if complete else "partial",
                    "checked_requests": str(checked),
                }
            )
        except (ExecutionStopped, ValueError, RuntimeError, KeyError, IndexError, TypeError) as exc:
            if getattr(exc, "code", "") == "ANALYSIS_INTERRUPTED":
                raise
            stages.append(
                {
                    "direction": "token_content",
                    "status": "partial",
                    "reason": getattr(exc, "code", "TOKEN_PLUGIN_FAILED"),
                }
            )
        if "recommendations" in intent:
            extension_complete = run_extension(
                source,
                writer,
                workspace,
                task_id,
                intent["recommendations"],
                self.recommendations,
                control,
                all(s["status"] == "completed" for s in stages if s["direction"] == "low_hit"),
            )
            if not extension_complete:
                stages.append(
                    {"direction": "token_content", "stage": "recommendations", "status": "partial"}
                )
        return {
            "status": "ready" if all(s["status"] == "completed" for s in stages) else "partial",
            "stages": stages,
            "version": "diagnostics-report-1",
        }

    @staticmethod
    def _low_hit(
        source: ResolvedSource,
        options: RuntimeOptions,
        control: TaskControl,
        writer: ResultWriter,
        workspace: Path,
        automatic_combinations: bool = True,
    ) -> dict[str, Any]:
        reports = [
            collect_l2(
                source, workspace / "l2", candidate_limit=options.candidate_limit, control=control
            ),
            collect_dynamics(
                source,
                workspace / "dynamics",
                candidate_limit=options.candidate_limit,
                include_history=True,
                control=control,
            ),
        ]
        recipes: dict[str, PrefixFinding] = {}
        for report in reports:
            writer.add(
                "rule_coverage",
                str(len(recipes))
                + "-"
                + str(report.candidate_comparisons)
                + "-"
                + ("l2" if report is reports[0] else "dynamic"),
                {
                    "checked_requests": str(report.checked_requests),
                    "candidate_comparisons": str(report.candidate_comparisons),
                    "partial": report.candidate_coverage_partial,
                    "reason_codes": list(report.reason_codes),
                },
            )
            for finding in report.findings:
                writer.add("finding", finding.finding_id, to_wire(finding))
                if finding.recipe_json:
                    recipes.setdefault(finding.recipe_json, finding)
        groups: list[tuple[PrefixFinding, ...]] = [(f,) for f in recipes.values()]
        dynamic = [f for f in recipes.values() if f.rule_id in ("L1", "L3")]
        for i, pair in enumerate(combinations(dynamic, 2) if automatic_combinations else ()):
            if i >= options.max_combinations:
                break
            groups.append(pair)
        partial = (
            any(r.candidate_coverage_partial for r in reports)
            or len(groups) > options.max_experiments
            or (
                automatic_combinations
                and len(dynamic) * (len(dynamic) - 1) // 2 > options.max_combinations
            )
        )
        stop_reason: str | None = None
        for i, findings in enumerate(groups):
            control.checkpoint()
            if i >= options.max_experiments or stop_reason:
                writer.add(
                    "experiment",
                    str(i),
                    {
                        "status": "not_run",
                        "reason": stop_reason or "EXPERIMENT_BUDGET_EXHAUSTED",
                        "finding_ids": [f.finding_id for f in findings],
                    },
                )
                continue
            directory = workspace / "experiments" / str(i)
            result = run_experiment(
                source, findings, directory, pilot_limit=options.pilot_limit, control=control
            )
            payload = metadata_wire(asdict(result))
            payload["confidence_basis"] = (
                "pilot_gain_gt_1pp"
                if result.pilot and result.pilot.gate_passed
                else "not_established"
            )
            if "ENCODING_BUDGET_EXHAUSTED" in result.reason_codes:
                stop_reason = "ENCODING_BUDGET_EXHAUSTED"
            writer.add("experiment", str(i), payload)
            for evaluation in (result.pilot, result.full):
                if evaluation:
                    data = evaluation_view(evaluation)
                    if evaluation.manifest_ref:
                        data["manifest_ref"] = (
                            (directory / evaluation.stage / "rows.sqlite3")
                            .relative_to(workspace)
                            .as_posix()
                        )
                    writer.add("evaluation", evaluation.evaluation_id, data)
                    if evaluation.display_eligible:
                        writer.add("optimization", evaluation.evaluation_id, data)
            for name in ("pilot-plan.json", "full-plan.json"):
                if (directory / name).exists():
                    plan = ModificationPlan.model_validate_json((directory / name).read_bytes())
                    writer.add("plan", plan.plan_id, to_wire(plan))
            if result.status not in (
                "full_qualified",
                "full_below_gate",
                "pilot_below_gate",
                "no_applicable_targets",
            ):
                partial = True
        return {
            "direction": "low_hit",
            "ruleset_version": "prefix-detectors-1",
            "status": "partial" if partial else "completed",
            "checked_requests": str(min(r.checked_requests for r in reports)),
            "candidate_coverage_partial": partial,
            "rule_scope": "dates_paths_known_billing_header_tools_history_json_representation",
        }

    def _token_evaluate(
        self,
        source: ResolvedSource,
        intent: dict[str, Any],
        control: TaskControl,
        writer: ResultWriter,
        workspace: Path,
    ) -> dict[str, Any]:
        plugin = self.registry.get("token_content")
        if json.loads(plugin.describe().model_dump_json()) != intent["plugin"]:
            raise ExecutionStopped("PLUGIN_IDENTITY_CHANGED")
        fragment = from_wire(
            AnalysisFragment, self.item(intent["parent"], "fragment", intent["fragment_id"])
        )
        if intent["kind"] == "token_authorization":
            candidate = self._authorize(fragment, intent)
            if candidate.model_dump_json() != intent["authorized_candidate"]:
                raise ExecutionStopped("AUTHORIZATION_IDENTITY_CHANGED")
            writer.add(
                "authorization",
                candidate.candidate_id,
                {"input": intent["authorization"], "candidate": to_wire(candidate)},
            )
        else:
            candidate = next(
                c
                for c in fragment.modification_candidates
                if c.candidate_id == intent["candidate_id"]
            )
        request = source.read_request(fragment.request_key)
        prepared = plugin.prepare_mutation(
            request, candidate, intent["parameters_json"], intent["business_basis_ref"]
        )
        if prepared.status != "prepared":
            return {"status": "partial", "reason_codes": list(prepared.reason_codes), "stages": []}
        plan = ModificationPlan(
            plan_id=str(uuid4()),
            version="1",
            source_scope_id=source.scope.scope_id,
            transformation_digest=hashlib.sha256(canonical_metadata(prepared)).hexdigest(),
            direction="token_content",
            action_class=candidate.action_class,
            finding_refs=candidate.finding_refs,
            operations=prepared.operations,
        )
        control.plan(len(plan.model_dump_json().encode()))
        writer.add("plan", plan.plan_id, to_wire(plan))
        result = evaluate_plan(source, plan, workspace / "evaluation", control=control)
        if result.manifest_ref:
            result = result.model_copy(update={"manifest_ref": "evaluation/rows.sqlite3"})
        writer.add("evaluation", result.evaluation_id, evaluation_view(result))
        return {
            "status": "ready" if result.status == "available" else "partial",
            "stages": [],
            "evaluation_id": result.evaluation_id,
        }

    def submit_low_hit_evaluation(
        self, task_id: str, finding_ids: tuple[str, ...], submission_key: str
    ) -> TaskReceipt:
        if not finding_ids or len(set(finding_ids)) != len(finding_ids) or len(finding_ids) > 2:
            raise TokenScopeError("INVALID_ARGUMENT", "Select one or two distinct findings", 422)
        findings = [
            from_wire(PrefixFinding, self.item(task_id, "finding", key)) for key in finding_ids
        ]
        if any(f.recipe_json is None for f in findings) or (
            len(findings) > 1 and any(f.rule_id == "L2" for f in findings)
        ):
            raise TokenScopeError("PLAN_UNSUPPORTED", "No compatible concrete transformation", 422)
        row = self.store.row(task_id)
        intent = {"kind": "low_hit_evaluation", "parent": task_id, "finding_ids": finding_ids}
        return self.store.submit(
            submission_key, json.dumps(intent, sort_keys=True), row["scope"], row["options"]
        )

    def _referenced_plans(
        self, scope: AnalysisScope, refs: list[dict[str, str]]
    ) -> list[ModificationPlan]:
        if not 2 <= len(refs) <= 8 or len({(r["task_id"], r["plan_id"]) for r in refs}) != len(
            refs
        ):
            raise TokenScopeError("INVALID_ARGUMENT", "Select two to eight distinct plans", 422)
        plans = []
        for ref in refs:
            row = self.store.row(ref["task_id"])
            if AnalysisScope.model_validate_json(row["scope"]) != scope:
                raise TokenScopeError("PLAN_SCOPE_MISMATCH", "Combination scopes differ", 409)
            plan = from_wire(ModificationPlan, self.item(ref["task_id"], "plan", ref["plan_id"]))
            if plan.source_scope_id != scope.scope_id:
                raise TokenScopeError(
                    "PLAN_SCOPE_MISMATCH", "Pilot plan cannot be used as full-scope plan", 409
                )
            plans.append(plan)
        return plans

    def submit_combination(
        self, task_id: str, plan_refs: list[dict[str, str]], submission_key: str
    ) -> TaskReceipt:
        row = self.store.row(task_id)
        self._referenced_plans(AnalysisScope.model_validate_json(row["scope"]), plan_refs)
        intent = {"kind": "combination", "plan_refs": plan_refs}
        return self.store.submit(
            submission_key, json.dumps(intent, sort_keys=True), row["scope"], row["options"]
        )

    @staticmethod
    def _authorize(fragment: AnalysisFragment, intent: dict[str, Any]) -> ModificationCandidate:
        from tokenscope.token_content.authorizations import authorize_candidate

        return authorize_candidate(fragment, **intent["authorization"])

    def submit_token_authorization(
        self, task_id: str, fragment_id: str, authorization: dict[str, str], submission_key: str
    ) -> TaskReceipt:
        fragment = from_wire(AnalysisFragment, self.item(task_id, "fragment", fragment_id))
        intent: dict[str, Any] = {
            "kind": "token_authorization",
            "parent": task_id,
            "fragment_id": fragment_id,
            "authorization": authorization,
            "parameters_json": authorization["parameters_json"],
            "business_basis_ref": authorization["business_basis_ref"],
        }
        try:
            candidate = self._authorize(fragment, intent)
        except ValueError as exc:
            raise TokenScopeError(
                "INVALID_AUTHORIZATION", "Authorization does not match saved evidence", 422
            ) from exc
        row = self.store.row(task_id)
        intent.update(
            authorized_candidate=candidate.model_dump_json(),
            plugin=json.loads(row["intent"])["plugin"],
        )
        return self.store.submit(
            submission_key, json.dumps(intent, sort_keys=True), row["scope"], row["options"]
        )
