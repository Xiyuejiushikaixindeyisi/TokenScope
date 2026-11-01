"""Independent guarded preparation, then canonical execution reuse within one task."""

from collections.abc import Iterable

from tokenscope.analysis_common.contracts import PreparedMutation, RequestKey, canonical_metadata
from tokenscope.analysis_common.modifications import pointer_parts


def canonical_operations(operations: Iterable[PreparedMutation]) -> bytes:
    normalized = {}
    targets: list[tuple[RequestKey, tuple[str, ...]]] = []
    for op in operations:
        target = op.target.location
        if target.source_pointer == "/tools" or target.source_pointer.startswith("/tools/"):
            raise ValueError("TOKEN_TOOL_DEFINITION_MUTATION_FORBIDDEN")
        payload = op.model_dump(exclude={"operation_id", "business_basis_ref"})
        key = canonical_metadata(payload)
        if key in normalized:
            continue
        parts = pointer_parts(target.source_pointer)
        for request, prior in targets:
            if request == target.request_key and (
                parts[: len(prior)] == prior or prior[: len(parts)] == parts
            ):
                raise ValueError("PLAN_OPERATION_CONFLICT")
        targets.append((target.request_key, parts))
        normalized[key] = payload
    return canonical_metadata([normalized[k] for k in sorted(normalized)])
