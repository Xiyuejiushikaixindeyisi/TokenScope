"""T3 exact complete payloads within one request, with explicit overlap exclusion."""

from tokenscope.analysis_common.contracts import Coverage, RuleResult
from tokenscope.analysis_common.plugins import RunControl
from tokenscope.token_content.extraction import Entry, Inventory
from tokenscope.token_content.json_values import digest, dumps
from tokenscope.token_content.rules import RuleOutput, observation
from tokenscope.token_content.stops import consume


def candidate(entry: Entry) -> bool:
    value = entry.value
    if not isinstance(value, (str, list, dict)) or not value:
        return False
    facets = entry.unit.facets
    if "argument_payload" in facets:
        return True
    if "tool_result" not in facets and "message_payload" not in facets:
        return False
    if isinstance(value, str):
        return entry.location.embedded is None
    # Multimodal protocol blocks are containers, not copied business documents.
    if isinstance(value, list) and any(isinstance(v, dict) and "type" in v for v in value):
        return False
    return True


def run_duplicates(inventory: Inventory, control: RunControl) -> RuleOutput:
    entries = [e for e in inventory.entries if candidate(e)]
    # Hash bucket then exact typed canonical value verification, including collisions.
    buckets: dict[tuple[str, int, str], dict[str, list[Entry]]] = {}
    for entry in entries:
        control.checkpoint()
        canonical = dumps(entry.value, sort_keys=True)
        encoded_size = len(canonical.encode("utf-8"))
        consume(control, "max_comparison_bytes", encoded_size, entry.location.location_id)
        key = (entry.unit.representation, encoded_size, digest(canonical))
        buckets.setdefault(key, {}).setdefault(canonical, []).append(entry)
    parents = {e.unit.unit_id: e.unit.parent_unit_id for e in inventory.entries}

    def ancestors(unit_id: str) -> set[str]:
        found = {unit_id}
        parent = parents.get(unit_id)
        while parent is not None:
            found.add(parent)
            parent = parents.get(parent)
        return found

    groups = [
        group
        for bucket in buckets.values()
        for group in bucket.values()
        if len(group) > 1 and any("tool_result" in e.unit.facets for e in group)
    ]
    groups.sort(key=lambda group: (-group[0].unit.measured_value, group[0].unit.unit_id))
    used: set[str] = set()
    used_ancestors: set[str] = set()
    observations = []
    for group in groups:
        control.checkpoint()
        selected: list[Entry] = []
        local_used: set[str] = set()
        local_ancestors: set[str] = set()
        for entry in group:
            identity = entry.unit.unit_id
            chain = ancestors(identity)
            if (
                chain.intersection(used)
                or chain.intersection(local_used)
                or identity in used_ancestors
                or identity in local_ancestors
            ):
                continue
            selected.append(entry)
            local_used.add(identity)
            local_ancestors.update(chain)
        if len(selected) < 2 or not any("tool_result" in e.unit.facets for e in selected):
            continue
        control.consume("max_candidates", 1)
        used.update(local_used)
        used_ancestors.update(local_ancestors)
        text_equal = isinstance(selected[0].value, str)
        observations.append(
            observation(
                "T3",
                selected,
                "exact_payload_repetition",
                "met",
                {
                    "occurrences": len(selected),
                    "comparison": "exact_text_bytes"
                    if text_equal
                    else "typed_structure_number_lexemes",
                    "repeated_utf8_bytes": (len(selected) - 1) * selected[0].measures["utf8_bytes"]
                    if text_equal
                    else None,
                    "occurrence_measures": [e.measures for e in selected],
                    "saved_tokens": None,
                    "deletion_safe": None,
                    "execution_count": None,
                    "scope": "single_request",
                    "aggregation": "nonoverlapping_groups",
                },
            )
        )
    return RuleOutput(
        tuple(observations),
        (),
        RuleResult(
            rule_id="T3",
            status="completed",
            condition="met" if observations else "not_met",
            coverage=Coverage(checked=len(entries), eligible=len(entries), complete=True),
        ),
    )
