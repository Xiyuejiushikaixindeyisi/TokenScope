"""Deterministic T2/T4 target selection over bounded, trusted extraction results."""

from dataclasses import dataclass

from tokenscope.analysis_common.contracts import RequestView
from tokenscope.analysis_common.plugins import RunControl
from tokenscope.token_content.auto_config import (
    Generator,
    ResultSelector,
    RetentionGenerator,
    parameters_for,
    retention_indices,
)
from tokenscope.token_content.extraction import Entry, Inventory
from tokenscope.token_content.json_values import ContentError


@dataclass(frozen=True)
class ResultTarget:
    entry: Entry
    parameters_json: str


def select_targets(
    request: RequestView,
    inventory: Inventory,
    selector: ResultSelector,
    generator: Generator,
    control: RunControl,
) -> tuple[ResultTarget, ...]:
    """No authorization implied: caller must validate typed basis before preparing edits."""
    if request.appid != selector.appid:
        return ()
    # A partial history cannot establish the last K matching results.
    if not request.raw_body_complete or inventory.local_errors:
        raise ContentError("EVIDENCE_LOCATION_UNAVAILABLE")
    entries: list[Entry] = []
    for entry in inventory.entries:
        control.checkpoint()
        if "tool_result" not in entry.unit.facets:
            continue
        if entry.tool_name is None and entry.identity_status in ("missing", "ambiguous"):
            raise ContentError("EVIDENCE_LOCATION_AMBIGUOUS")
        if entry.tool_name != selector.tool_name:
            continue
        if entry.identity_status != "resolved":
            raise ContentError("EVIDENCE_LOCATION_AMBIGUOUS")
        if entry.tool_identity != selector.tool_identity:
            continue
        if entry.unit.representation != selector.representation:
            continue
        inner = entry.location.embedded
        if (inner.pointer if inner else None) != selector.embedded_pointer:
            continue
        is_part = "text_part" in entry.unit.facets
        if is_part != (selector.retention_unit == "text_part"):
            continue
        # Exclude non-container outer descendants; JSON inner path is explicit.
        if inner is None and not is_part and entry.unit.parent_unit_id is not None:
            continue
        if (entry.location.request_key, entry.location.raw_sha256) != (
            request.request_key,
            request.raw_sha256,
        ):
            raise ContentError("EVIDENCE_LOCATION_UNAVAILABLE")
        entries.append(entry)
    if isinstance(generator, RetentionGenerator):
        entries = [entries[i] for i in retention_indices(len(entries), generator)]
    targets = []
    for entry in entries:
        control.consume("max_candidates", 1)
        targets.append(ResultTarget(entry, parameters_for(generator, entry.value)))
    return tuple(targets)
