"""Separate V3 sample report; old full-report qualification is unchanged."""

from typing import Literal

from tokenscope.analysis_common.contracts import Contract, Digest
from tokenscope.analysis_common.contracts_v3 import SampleManifest3
from tokenscope.analysis_common.evaluation_v3 import WindowEvaluation3
from tokenscope.prefix_analysis.clock_discovery_v3 import ClockDiscovery3, ClockFinding3
from tokenscope.prefix_analysis.prefix_findings_v3 import PrefixFinding3


class Recommendation3(Contract):
    finding: ClockFinding3 | PrefixFinding3
    transformation_digest: Digest
    windows: tuple[WindowEvaluation3, ...]


class SampleReport3(Contract):
    version: Literal["diagnostics-report-3"] = "diagnostics-report-3"
    task_id: str
    sample_id: str
    manifest_sha256: Digest
    sample: SampleManifest3
    discovery: ClockDiscovery3
    recommendations: tuple[Recommendation3, ...]
    business_note: str
    automatic_full: Literal[False] = False
