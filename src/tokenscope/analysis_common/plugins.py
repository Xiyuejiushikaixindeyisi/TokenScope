"""Static plugin protocol and cooperative, explicitly configured execution budgets."""

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Literal, Protocol, Self

from pydantic import Field, model_validator

from tokenscope.analysis_common.contracts import (
    CONTRACT_VERSION,
    AnalysisFragment,
    Contract,
    JsonText,
    ModificationCandidate,
    Name,
    Nonnegative,
    Participation,
    PreparedMutation,
    RequestView,
)


class BudgetSpec(Contract):
    max_request_bytes: int = Field(gt=0)
    max_units: int = Field(gt=0)
    max_comparison_bytes: int = Field(gt=0)
    max_depth: int = Field(gt=0)
    max_candidates: int = Field(gt=0)
    max_encoding_calls: int = Field(gt=0)


class VersionedName(Contract):
    name: Name
    version: Name


class PluginDescriptor(Contract):
    plugin_id: Literal["low_hit", "token_content"]
    version: Name
    contract_version: Literal["analysis-common-1.0"] = CONTRACT_VERSION
    parser_version: Name
    measurement_version: Name
    rule_versions: tuple[VersionedName, ...]
    policy_schema_version: Name
    handlers: tuple[VersionedName, ...]
    required_capabilities: tuple[str, ...] = ("complete_body", "scope_identity")
    optional_capabilities: tuple[str, ...] = ("participation", "exact_spans")


class PluginSelection(Contract):
    rule_ids: tuple[str, ...]
    policies_json: JsonText = "[]"
    budget: BudgetSpec


class EvidenceCapabilities(Contract):
    available: tuple[str, ...] = ("complete_body", "scope_identity")
    # Pointer paired with its evidence; tuple representation remains deeply immutable.
    participation: tuple[tuple[str, Participation], ...] = ()


class MutationPreparation(Contract):
    status: Literal["prepared", "blocked"]
    operations: tuple[PreparedMutation, ...] = ()
    reason_codes: tuple[str, ...] = ()

    @model_validator(mode="after")
    def valid_preparation(self) -> Self:
        if self.status == "prepared" and not self.operations:
            raise ValueError("Prepared mutation needs operations")
        if self.status == "blocked" and self.operations:
            raise ValueError("Blocked preparation cannot publish operations")
        return self


class ExecutionStopped(Exception):
    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


@dataclass
class RunControl:
    budget: BudgetSpec
    cancelled: Callable[[], bool] = lambda: False
    consumed: dict[str, int] = field(default_factory=dict)

    def checkpoint(self) -> None:
        if self.cancelled():
            raise ExecutionStopped("ANALYSIS_INTERRUPTED")

    def consume(self, resource: str, amount: int) -> None:
        self.checkpoint()
        if type(amount) is not int or amount < 0:
            raise ValueError("Budget amount must be a nonnegative integer")
        limits = self.budget.model_dump()
        if resource not in limits:
            raise ValueError("Unknown budget resource")
        total = self.consumed.get(resource, 0) + amount
        if total > limits[resource]:
            raise ExecutionStopped("ANALYSIS_BUDGET_EXHAUSTED")
        self.consumed[resource] = total


class AnalysisPlugin(Protocol):
    def describe(self) -> PluginDescriptor: ...

    def validate_selection(self, selection: PluginSelection) -> PluginSelection: ...

    def analyze_request(
        self,
        request: RequestView,
        selection: PluginSelection,
        evidence: EvidenceCapabilities,
        control: RunControl,
    ) -> AnalysisFragment: ...

    def prepare_mutation(
        self,
        request: RequestView,
        candidate: ModificationCandidate,
        parameters_json: str,
        business_basis_ref: str | None,
    ) -> MutationPreparation: ...


class PluginRegistry:
    def __init__(self) -> None:
        self._plugins: dict[str, AnalysisPlugin] = {}
        self._handlers: set[tuple[str, str]] = set()

    def register(self, plugin: AnalysisPlugin) -> None:
        descriptor = plugin.describe()
        handlers = {(item.name, item.version) for item in descriptor.handlers}
        if descriptor.plugin_id in self._plugins:
            raise ValueError("Duplicate plugin")
        if len(handlers) != len(descriptor.handlers) or handlers & self._handlers:
            raise ValueError("Duplicate handler")
        self._plugins[descriptor.plugin_id] = plugin
        self._handlers.update(handlers)

    def get(self, plugin_id: str) -> AnalysisPlugin:
        if plugin_id not in self._plugins:
            raise ExecutionStopped("PLUGIN_UNAVAILABLE")
        return self._plugins[plugin_id]


class DirectionState(Contract):
    direction: Literal["low_hit", "token_content"]
    status: Literal["not_started", "running", "completed", "partial", "failed", "interrupted"]
    checked_requests: Nonnegative = 0
