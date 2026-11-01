"""Explicit business policies, independent of execution budgets."""

import hashlib
from typing import Literal, Self

from pydantic import Field, TypeAdapter, model_validator

from tokenscope.analysis_common.contracts import Contract, Pointer


class PolicySpec(Contract):
    policy_id: str = Field(min_length=1)
    revision: str = Field(min_length=1)
    source: str = Field(min_length=1)
    rule_id: Literal["T1", "T2", "T4"]
    kind: Literal["limit", "field_allowlist", "retain_last"]
    tool_name: str | None = None
    tool_identity: str | None = None
    source_pointer: Pointer | None = None
    embedded_pointer: Pointer | None = None
    representation: Literal["text", "structural_json"] | None = None
    basis: Literal["source_content", "model_input"] = "source_content"
    unit: str | None = None
    operator: Literal["gt", "ge"] = "gt"
    limit: int | None = Field(default=None, ge=0)
    allowed_fields: tuple[str, ...] | None = None
    field_level: Literal["object", "array_items"] | None = None
    keep_last: int | None = Field(default=None, ge=0)
    retention_unit: Literal["result_container", "text_part"] = "result_container"

    @model_validator(mode="after")
    def coherent(self) -> Self:
        if self.kind == "limit":
            if self.rule_id == "T4" or self.limit is None or not self.unit:
                raise ValueError("Limit policy needs T1/T2, explicit unit and limit")
            if self.allowed_fields is not None or self.keep_last is not None:
                raise ValueError("Unrelated policy parameters")
        elif self.kind == "field_allowlist":
            if self.rule_id != "T2" or self.allowed_fields is None or self.field_level is None:
                raise ValueError("Field policy needs T2 and explicit field level")
            if self.limit is not None or self.keep_last is not None:
                raise ValueError("Unrelated policy parameters")
        else:
            if self.rule_id != "T4" or self.keep_last is None:
                raise ValueError("Retention needs T4 and explicit K")
            if self.limit is not None or self.allowed_fields is not None:
                raise ValueError("Unrelated policy parameters")
        if self.tool_name is not None and self.tool_identity is None:
            raise ValueError("Tool policy requires exact definition identity")
        return self

    @property
    def digest(self) -> str:
        return hashlib.sha256(self.model_dump_json().encode()).hexdigest()


def parse_policies(raw: str) -> tuple[PolicySpec, ...]:
    policies = TypeAdapter(tuple[PolicySpec, ...]).validate_json(raw)
    keys = [(p.policy_id, p.revision) for p in policies]
    if len(keys) != len(set(keys)):
        raise ValueError("Duplicate policy identity")
    return policies
