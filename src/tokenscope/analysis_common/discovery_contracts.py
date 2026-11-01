"""Wire schemas for the additive discovery protocol; not a change to H0."""

from typing import Any, Literal

from pydantic import Field

from tokenscope.analysis_common.contracts import AnalysisScope, Contract
from tokenscope.analysis_common.wire import wire_schema


class Binding(Contract):
    appid: str
    model_id: str
    common_name: str | None
    source_kind: Literal["base", "user_v2"]


class PlanRef(Contract):
    task_id: str
    plan_id: str


class TerminalMetadata(Contract):
    task_id: str
    task_kind: Literal[
        "analysis", "low_hit_evaluation", "token_evaluation", "token_authorization", "combination"
    ]
    parent_task_id: str | None
    plan_refs: list[PlanRef]
    status: Literal["ready", "partial", "empty", "failed", "interrupted"]
    error_code: str | None
    report_published: bool
    report_ref: str | None
    report_digest: str | None
    scope_id: str
    binding: Binding
    binding_id: str
    directions: list[Literal["low_hit", "token_content"]]
    sequence: str = Field(pattern=r"^[1-9][0-9]*$")
    terminal_at: str | None
    published_at: str | None
    analysis_completed_at: str | None
    legacy: bool
    default_eligible: bool


class CatalogEntry(TerminalMetadata):
    scope: AnalysisScope


class DefaultReference(Contract):
    binding_id: str
    direction: Literal["low_hit", "token_content"]
    task_id: str
    sequence: str


class Envelope(Contract):
    version: Literal["diagnostics-discovery-1"]
    service_instance_id: str


class Catalog(Envelope):
    snapshot: str
    event_cursor: str
    items: list[CatalogEntry]
    defaults: list[DefaultReference]
    next_after: str | None


class Terminal(Envelope):
    terminal: CatalogEntry | None


class TerminalEvent(TerminalMetadata, Envelope):
    event_id: str


class Reset(Envelope):
    reason: str
    catalog_url: Literal["/diagnostics/discovery/catalog"]


class ErrorDetail(Contract):
    code: str
    message: str


class Error(Contract):
    error: ErrorDetail


def schemas() -> dict[str, Any]:
    return {
        name: wire_schema(model)
        for name, model in (
            ("catalog", Catalog),
            ("terminal", Terminal),
            ("terminal_event", TerminalEvent),
            ("reset", Reset),
            ("error", Error),
        )
    }
