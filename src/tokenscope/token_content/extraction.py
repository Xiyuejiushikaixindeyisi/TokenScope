"""Single-request content inventory. No inference of execution or usefulness."""

from dataclasses import dataclass

from tokenscope.analysis_common.contracts import (
    ContentUnit,
    EmbeddedLocation,
    Location,
    Participation,
    RequestView,
)
from tokenscope.analysis_common.plugins import EvidenceCapabilities, RunControl
from tokenscope.token_content.json_values import (
    PARSER_VERSION,
    ContentError,
    Value,
    digest,
    dumps,
    loads,
    pointer_child,
)
from tokenscope.token_content.measurements import MEASUREMENT_VERSION, measure
from tokenscope.token_content.stops import consume


@dataclass(frozen=True)
class Entry:
    location: Location
    unit: ContentUnit
    value: Value
    measures: dict[str, int]
    message_index: int | None = None
    tool_name: str | None = None
    tool_identity: str | None = None
    identity_status: str = "not_applicable"


@dataclass(frozen=True)
class Inventory:
    entries: tuple[Entry, ...]
    local_errors: tuple[tuple[str, str], ...]
    source_fields: tuple[str, ...]
    message_count: int


def extract(request: RequestView, evidence: EvidenceCapabilities, control: RunControl) -> Inventory:
    """Raise on incomplete source or budget stop; never silently truncate inventory."""
    control.checkpoint()
    if not request.raw_body_complete:
        raise ContentError("INCOMPLETE_BODY")
    if len(request.raw_body.encode("utf-8")) > control.budget.max_request_bytes:
        raise ContentError("ANALYSIS_BUDGET_EXHAUSTED")
    root = loads(request.raw_body, max_depth=control.budget.max_depth)
    if not isinstance(root, dict):
        raise ContentError("INVALID_REQUEST_SHAPE")
    entries: list[Entry] = []
    errors: list[tuple[str, str]] = []
    participation = dict(evidence.participation)
    definitions: dict[str, set[str]] = {}

    def add(
        value: Value,
        pointer: str,
        facets: tuple[str, ...],
        *,
        parent: Entry | None = None,
        embedded: str | None = None,
        message_index: int | None = None,
        tool_name: str | None = None,
        identity_status: str = "not_applicable",
        tool_identity: str | None = None,
    ) -> Entry:
        consume(control, "max_units", 1, pointer)
        location = Location(
            request_key=request.request_key,
            raw_sha256=request.raw_sha256,
            source_pointer=pointer,
            embedded=None
            if embedded is None
            else EmbeddedLocation(parser_version=PARSER_VERSION, pointer=embedded),
        )
        if isinstance(value, str):
            metrics = measure(value)
            canonical = dumps(value, sort_keys=True)
        else:
            canonical = dumps(value, sort_keys=True)
            metrics = measure(value, canonical_json=canonical)
        metric = "utf8_bytes" if isinstance(value, str) else "display_json_utf8_bytes"
        part = participation.get(pointer, Participation()) if embedded is None else Participation()
        if part.encoding_identity != request.encoder_identity:
            part = Participation()
        unit = ContentUnit(
            location_id=location.location_id,
            representation="text" if isinstance(value, str) else "structural_json",
            measurement_version=MEASUREMENT_VERSION,
            content_sha256=digest(canonical),
            facets=facets,
            measurement_unit=metric,
            measured_value=metrics[metric],
            parent_unit_id=parent.unit.unit_id if parent else None,
            container_unit_id=(parent.unit.container_unit_id or parent.unit.unit_id)
            if parent
            else None,
            overlap_relation="contained" if parent else "none",
            participation=part,
        )
        entry = Entry(
            location, unit, value, metrics, message_index, tool_name, tool_identity, identity_status
        )
        entries.append(entry)
        return entry

    def children(
        value: Value,
        pointer: str,
        facets: tuple[str, ...],
        parent: Entry,
        embedded: str | None = None,
    ) -> None:
        items = (
            value.items()
            if isinstance(value, dict)
            else enumerate(value)
            if isinstance(value, list)
            else ()
        )
        for key, child in items:
            child_pointer = pointer_child(pointer, key) if embedded is None else pointer
            inner = pointer_child(embedded, key) if embedded is not None else None
            entry = add(
                child,
                child_pointer,
                facets,
                parent=parent,
                embedded=inner,
                message_index=parent.message_index,
                tool_name=parent.tool_name,
                identity_status=parent.identity_status,
                tool_identity=parent.tool_identity,
            )
            children(child, child_pointer, facets, entry, inner)

    def embedded_json(entry: Entry, required: bool = False) -> None:
        value = entry.value
        if not isinstance(value, str) or not (required or value.lstrip().startswith(("{", "["))):
            return
        try:
            parsed = loads(value, max_depth=control.budget.max_depth)
        except ContentError as exc:
            if exc.code == "ANALYSIS_BUDGET_EXHAUSTED":
                raise
            errors.append((entry.location.source_pointer, "INVALID_EMBEDDED_JSON"))
            return
        parsed_entry = add(
            parsed,
            entry.location.source_pointer,
            entry.unit.facets,
            parent=entry,
            embedded="",
            message_index=entry.message_index,
            tool_name=entry.tool_name,
            identity_status=entry.identity_status,
            tool_identity=entry.tool_identity,
        )
        children(parsed, entry.location.source_pointer, entry.unit.facets, parsed_entry, "")

    for field in ("tools", "functions"):
        tools = root.get(field, [])
        if not isinstance(tools, list):
            errors.append(("/" + field, "INVALID_TOOL_DEFINITIONS"))
            continue
        for index, definition in enumerate(tools):
            pointer = f"/{field}/{index}"
            function = (
                definition.get("function")
                if field == "tools" and isinstance(definition, dict)
                else definition
            )
            if not isinstance(function, dict) or not isinstance(function.get("name"), str):
                errors.append((pointer, "UNSUPPORTED_TOOL_DEFINITION"))
                continue
            name = str(function["name"])
            definition_identity = digest(dumps(definition, sort_keys=True))
            definitions.setdefault(name, set()).add(definition_identity)
            entry = add(
                definition,
                pointer,
                ("tool_definition",),
                tool_name=name,
                tool_identity=definition_identity,
                identity_status="resolved",
            )
            # Definition children are evidence, not additional total burden.
            children(definition, pointer, ("tool_definition_field",), entry)

    messages = root.get("messages", [])
    if not isinstance(messages, list):
        raise ContentError("INVALID_REQUEST_SHAPE")
    calls: dict[str, list[str | None]] = {}
    for index, message in enumerate(messages):
        control.checkpoint()
        if not isinstance(message, dict):
            errors.append((f"/messages/{index}", "INVALID_MESSAGE"))
            continue
        role = message.get("role")
        pointer = f"/messages/{index}"
        tool_name: str | None = None
        identity: str | None = None
        status = "not_applicable"
        if role in ("tool", "function"):
            status = "missing"
            if role == "function" and isinstance(message.get("name"), str):
                tool_name = str(message["name"])
            elif isinstance(message.get("tool_call_id"), str):
                matches = calls.get(str(message["tool_call_id"]), [])
                if len(matches) == 1:
                    tool_name = matches[0]
                elif len(matches) > 1:
                    status = "ambiguous"
            if tool_name is not None:
                identities = definitions.get(tool_name, set())
                status = (
                    "resolved" if len(identities) == 1 else "ambiguous" if identities else "missing"
                )
                identity = next(iter(identities)) if len(identities) == 1 else None
        if "content" in message and role in ("tool", "function", "user", "assistant"):
            content = message["content"]
            facets = (
                ("tool_result", "history_tool_result")
                if role in ("tool", "function")
                else ("message_payload",)
            )
            entry = add(
                content,
                pointer + "/content",
                facets,
                message_index=index,
                tool_name=tool_name,
                tool_identity=identity,
                identity_status=status,
            )
            embedded_json(entry)
            if isinstance(content, list):
                for part_index, part in enumerate(content):
                    if (
                        isinstance(part, dict)
                        and part.get("type") in ("text", "input_text", "output_text")
                        and isinstance(part.get("text"), str)
                    ):
                        child = add(
                            part["text"],
                            f"{pointer}/content/{part_index}/text",
                            facets + ("text_part",),
                            parent=entry,
                            message_index=index,
                            tool_name=tool_name,
                            tool_identity=identity,
                            identity_status=status,
                        )
                        embedded_json(child)
        if role != "assistant":
            continue
        raw_calls = message.get("tool_calls", [])
        if not isinstance(raw_calls, list):
            errors.append((pointer + "/tool_calls", "INVALID_TOOL_CALLS"))
            raw_calls = []
        for call_index, call in enumerate(raw_calls):
            if not isinstance(call, dict):
                continue
            function = call.get("function")
            if not isinstance(function, dict):
                continue
            call_name = function.get("name")
            if isinstance(call.get("id"), str):
                calls.setdefault(str(call["id"]), []).append(
                    call_name if isinstance(call_name, str) else None
                )
            if "arguments" in function:
                entry = add(
                    function["arguments"],
                    f"{pointer}/tool_calls/{call_index}/function/arguments",
                    ("argument_payload",),
                    message_index=index,
                )
                embedded_json(entry, required=True)
        legacy = message.get("function_call")
        if isinstance(legacy, dict) and "arguments" in legacy:
            entry = add(
                legacy["arguments"],
                pointer + "/function_call/arguments",
                ("argument_payload",),
                message_index=index,
            )
            embedded_json(entry, required=True)
    return Inventory(tuple(entries), tuple(errors), tuple(root), len(messages))
