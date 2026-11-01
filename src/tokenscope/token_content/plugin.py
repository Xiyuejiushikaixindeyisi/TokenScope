"""Static Token content plugin for analysis-common-1.0."""

import json
from typing import Literal, cast

from tokenscope.analysis_common.contracts import (
    AnalysisFragment,
    Coverage,
    FindingCandidate,
    ModificationCandidate,
    Observation,
    RequestView,
    RuleResult,
)
from tokenscope.analysis_common.plugins import (
    EvidenceCapabilities,
    ExecutionStopped,
    MutationPreparation,
    PluginDescriptor,
    PluginSelection,
    RunControl,
    VersionedName,
)
from tokenscope.token_content.candidates import pending_candidates
from tokenscope.token_content.duplicates import run_duplicates
from tokenscope.token_content.extraction import extract
from tokenscope.token_content.json_values import PARSER_VERSION, ContentError
from tokenscope.token_content.measurements import MEASUREMENT_VERSION
from tokenscope.token_content.policies import parse_policies
from tokenscope.token_content.rules import RULE_VERSION, RuleOutput, run_inventory_rule
from tokenscope.token_content.transformations import HANDLER_VERSION, HANDLERS, prepare

PLUGIN_VERSION = "token-content-1"


class TokenContentPlugin:
    def describe(self) -> PluginDescriptor:
        return PluginDescriptor(
            plugin_id="token_content",
            version=PLUGIN_VERSION,
            parser_version=PARSER_VERSION,
            measurement_version=MEASUREMENT_VERSION,
            rule_versions=tuple(
                VersionedName(name=rule, version=RULE_VERSION) for rule in ("T1", "T2", "T3", "T4")
            ),
            policy_schema_version="token-policy-1",
            handlers=tuple(
                VersionedName(name=handler, version=HANDLER_VERSION) for handler in HANDLERS
            ),
        )

    def validate_selection(self, selection: PluginSelection) -> PluginSelection:
        if not selection.rule_ids or len(set(selection.rule_ids)) != len(selection.rule_ids):
            raise ValueError("Unique nonempty rule selection required")
        if set(selection.rule_ids) - {"T1", "T2", "T3", "T4"}:
            raise ValueError("Unsupported Token rule")
        policies = parse_policies(selection.policies_json)
        if any(policy.rule_id not in selection.rule_ids for policy in policies):
            raise ValueError("Policy references unselected rule")
        return selection

    def analyze_request(
        self,
        request: RequestView,
        selection: PluginSelection,
        evidence: EvidenceCapabilities,
        control: RunControl,
    ) -> AnalysisFragment:
        self.validate_selection(selection)
        try:
            required = set(self.describe().required_capabilities)
            if not required.issubset(evidence.available):
                raise ContentError("MISSING_REQUIRED_CAPABILITY")
            inventory = extract(request, evidence, control)
        except (ContentError, ExecutionStopped) as exc:
            coverage = Coverage(
                checked=0,
                eligible=None,
                complete=False,
                reasons=(exc.code,),
                stop_location=getattr(exc, "stop_location", ""),
            )
            return AnalysisFragment(
                request_key=request.request_key,
                raw_sha256=request.raw_sha256,
                plugin_id="token_content",
                plugin_version=self.describe().version,
                coverage=coverage,
                reason_codes=(exc.code,),
                rule_results=tuple(
                    RuleResult(
                        rule_id=rule,
                        status="not_checked",
                        condition="unknown",
                        coverage=coverage,
                        reason_codes=(exc.code,),
                    )
                    for rule in selection.rule_ids
                ),
            )
        policies = parse_policies(selection.policies_json)
        outputs: list[RuleOutput] = []
        results: list[RuleResult] = []
        reasons: list[str] = []
        stopped = False
        for rule in selection.rule_ids:
            if stopped:
                results.append(
                    RuleResult(
                        rule_id=rule,
                        status="not_checked",
                        condition="unknown",
                        coverage=Coverage(
                            checked=0,
                            eligible=None,
                            complete=False,
                            reasons=("PREVIOUS_RULE_STOPPED",),
                        ),
                    )
                )
                continue
            try:
                control.checkpoint()
                if rule == "T3":
                    output = run_duplicates(inventory, control)
                elif rule in ("T1", "T2", "T4"):
                    output = run_inventory_rule(
                        cast(Literal["T1", "T2", "T4"], rule),
                        inventory,
                        policies,
                        control,
                        capture_truncation=request.capture_truncation,
                        message_count=inventory.message_count,
                    )
                else:
                    raise ValueError("Unsupported rule")
                outputs.append(output)
                results.append(output.result)
            except ExecutionStopped as exc:
                stopped = True
                reasons.append(exc.code)
                results.append(
                    RuleResult(
                        rule_id=rule,
                        status="partial",
                        condition="unknown",
                        coverage=Coverage(
                            checked=0,
                            eligible=None,
                            complete=False,
                            reasons=(exc.code,),
                            stop_location=getattr(exc, "stop_location", rule),
                        ),
                        reason_codes=(exc.code,),
                    )
                )
        if inventory.local_errors:
            reasons.append("LOCAL_EXTRACTION_INCOMPLETE")
            results = [
                r.model_copy(
                    update={
                        "status": "partial",
                        "condition": "unknown",
                        "reason_codes": r.reason_codes + ("LOCAL_EXTRACTION_INCOMPLETE",),
                        "coverage": Coverage(
                            checked=r.coverage.checked,
                            eligible=None,
                            complete=False,
                            reasons=("LOCAL_EXTRACTION_INCOMPLETE",),
                        ),
                    }
                )
                if r.status == "completed"
                else r
                for r in results
            ]
        observations = tuple(o for output in outputs for o in output.observations)
        if inventory.local_errors:
            observations += tuple(
                Observation(
                    rule_id=selection.rule_ids[0],
                    rule_version=RULE_VERSION,
                    unit_ids=tuple(
                        e.unit.unit_id
                        for e in inventory.entries
                        if e.location.source_pointer == pointer and e.location.embedded is None
                    ),
                    predicate="local_parse_incomplete:" + pointer,
                    method=PARSER_VERSION,
                    condition="unknown",
                    details_json=json.dumps({"source_pointer": pointer, "reason": reason}),
                )
                for pointer, reason in inventory.local_errors
            )
        extra_findings: tuple[FindingCandidate, ...] = ()
        candidates: tuple[ModificationCandidate, ...] = ()
        if not reasons:
            try:
                extra_findings, candidates = pending_candidates(
                    inventory, observations, selection.rule_ids, control
                )
            except ExecutionStopped as exc:
                reasons.append(exc.code)
        return AnalysisFragment(
            request_key=request.request_key,
            raw_sha256=request.raw_sha256,
            plugin_id="token_content",
            plugin_version=self.describe().version,
            locations=tuple(e.location for e in inventory.entries),
            units=tuple(e.unit for e in inventory.entries),
            observations=observations,
            finding_candidates=tuple(f for output in outputs for f in output.findings)
            + extra_findings,
            modification_candidates=candidates,
            rule_results=tuple(results),
            coverage=Coverage(
                checked=0 if reasons else 1,
                eligible=1,
                complete=not reasons,
                reasons=tuple(reasons),
            ),
            reason_codes=tuple(reasons),
        )

    def prepare_mutation(
        self,
        request: RequestView,
        candidate: ModificationCandidate,
        parameters_json: str,
        business_basis_ref: str | None,
    ) -> MutationPreparation:
        return prepare(request, candidate, parameters_json, business_basis_ref)
