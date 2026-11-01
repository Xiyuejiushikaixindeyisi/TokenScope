"""Versioned private recipe configuration; no public recommendation draft dependency."""

from typing import Annotated, Literal, Self

from pydantic import Field, RootModel, field_validator, model_validator

from tokenscope.analysis_common.contracts import Contract, Digest, Name, Pointer
from tokenscope.token_content.json_values import ContentError, Number, Value, dumps, loads

CONFIG_MAX_BYTES = 256 * 1024


class ResultSelector(Contract):
    version: Literal["token-result-selector-1"]
    appid: Name
    tool_name: Name
    tool_identity: Digest
    representation: Literal["text", "structural_json"]
    embedded_pointer: Pointer | None
    retention_unit: Literal["result_container", "text_part"] = "result_container"

    @model_validator(mode="after")
    def coherent(self) -> Self:
        if (self.representation == "text") != (self.embedded_pointer is None):
            raise ValueError("Text requires no embedded pointer; JSON requires an explicit pointer")
        if self.retention_unit == "text_part" and self.representation != "text":
            raise ValueError("Text-part selector must select text")
        return self


class OmissionPermission(Contract):
    omission_permitted: Literal[True]

    @field_validator("omission_permitted", mode="before")
    @classmethod
    def exact_permission(cls, value: object) -> object:
        if value is not True:
            raise ValueError("Explicit boolean omission permission required")
        return value


class ProjectionGenerator(OmissionPermission):
    version: Literal["token-result-generator-1"]
    kind: Literal["project_fields"]
    fields: tuple[Name, ...] = Field(min_length=1)
    field_level: Literal["object", "array_items"]

    @model_validator(mode="after")
    def unique_fields(self) -> Self:
        if len(set(self.fields)) != len(self.fields):
            raise ValueError("Duplicate projection field")
        return self


class SliceGenerator(OmissionPermission):
    version: Literal["token-result-generator-1"]
    kind: Literal["select_items", "select_lines"]
    side: Literal["first", "last"]
    count: int = Field(ge=0)


class RetentionGenerator(OmissionPermission):
    version: Literal["token-result-generator-1"]
    kind: Literal["retain_last"]
    keep_last: int = Field(ge=0)
    replacement_json: str

    @model_validator(mode="after")
    def valid_replacement(self) -> Self:
        checked_raw(self.replacement_json)
        return self


Generator = Annotated[
    ProjectionGenerator | SliceGenerator | RetentionGenerator, Field(discriminator="kind")
]


class GeneratorConfig(RootModel[Generator]):
    pass


def checked_raw(raw: str) -> None:
    if len(raw.encode("utf-8")) > CONFIG_MAX_BYTES:
        raise ContentError("RECIPE_BUNDLE_INVALID")
    loads(raw, max_depth=32)  # Reject duplicate keys, nonfinite numbers and invalid Unicode.


def parse_config(
    selector_json: str, generator_json: str, rule: str, handler: str, handler_version: str
) -> tuple[ResultSelector, Generator]:
    checked_raw(selector_json)
    checked_raw(generator_json)
    selector = ResultSelector.model_validate_json(selector_json)
    generator = GeneratorConfig.model_validate_json(generator_json).root
    expected = {
        "project_fields": ("T2", "project_result_fields"),
        "select_items": ("T2", "select_result_items"),
        "select_lines": ("T2", "select_result_lines"),
        "retain_last": ("T4", "apply_retention_replacements"),
    }
    if expected[generator.kind] != (rule, handler) or handler_version != "1":
        raise ValueError("Recipe rule/handler/version mismatch")
    if isinstance(generator, ProjectionGenerator) or generator.kind == "select_items":
        if selector.representation != "structural_json":
            raise ValueError("Projection/items require structural JSON")
    if generator.kind == "select_lines" and selector.representation != "text":
        raise ValueError("Lines require text")
    if isinstance(generator, RetentionGenerator):
        # Retention replaces the complete selected result, never an arbitrary inner field.
        if selector.embedded_pointer not in (None, ""):
            raise ValueError("Retention requires a complete result")
        replacement = loads(generator.replacement_json, max_depth=32)
        if selector.representation == "text" and not isinstance(replacement, str):
            raise ValueError("Text retention requires a string replacement")
    return selector, generator


def parameters_for(generator: Generator, value: Value) -> str:
    """Produce exact handler parameters; this is not authorization or evidence matching."""
    parameters: dict[str, Value]
    if isinstance(generator, ProjectionGenerator):
        rows = [value] if generator.field_level == "object" else value
        if not isinstance(rows, list) or not all(isinstance(row, dict) for row in rows):
            raise ContentError("INVALID_PROJECTION_SHAPE")
        parameters = {"fields": list(generator.fields), "field_level": generator.field_level}
    elif isinstance(generator, SliceGenerator):
        if generator.kind == "select_items" and isinstance(value, list):
            size = len(value)
        elif generator.kind == "select_lines" and isinstance(value, str):
            size = len(value.splitlines(keepends=True))
        else:
            raise ContentError("INCOMPATIBLE_OPERATION")
        count = min(size, generator.count)
        start, end = (0, count) if generator.side == "first" else (size - count, size)
        parameters = {"start": Number(str(start)), "end": Number(str(end))}
    else:
        parameters = {"replacement_json": generator.replacement_json}
    return dumps(parameters)


def retention_indices(size: int, generator: RetentionGenerator) -> range:
    """Indices of old members in an already identity-filtered, source-ordered group."""
    if size < 0:
        raise ValueError("Negative group size")
    return range(max(0, size - generator.keep_last))
