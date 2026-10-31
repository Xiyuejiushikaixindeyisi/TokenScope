import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from tokenscope.user_monitoring.contracts import SCENARIO_ADAPTER, BatchScenario, Scenario


def minimal(**updates):
    value = dict(
        timing_model="batch_reference_total_noncompute_v1",
        scenario_id="minimal",
        revision="1",
        model_id="GLM-5.2",
        common_name="GLM-V5.2",
        deployment="fixed synthetic configuration",
        source="user_assumption",
        source_description="batch time assumed for arithmetic, not calibrated",
        chunk_tokens="8192",
        chunk_seconds="1",
    )
    value.update(updates)
    return value


def test_minimal_and_optional_evidence():
    value = SCENARIO_ADAPTER.validate_python(minimal())
    assert isinstance(value, BatchScenario)
    assert value.min_prompt_tokens is None
    assert value.measurement_boundary == "GF dispatch to first token"
    assert "overhead_seconds" not in value.model_dump()
    assert SCENARIO_ADAPTER.validate_json(value.model_dump_json()) == value
    measured_tau = SCENARIO_ADAPTER.validate_python(
        minimal(evidence_sha256="a" * 64, sample_count="10")
    )
    assert measured_tau.source == "user_assumption"


@pytest.mark.parametrize(
    "field",
    [
        "timing_model",
        "model_id",
        "common_name",
        "deployment",
        "source",
        "source_description",
        "chunk_tokens",
        "chunk_seconds",
    ],
)
@pytest.mark.parametrize("missing", ["absent", "null", "blank"])
def test_required_not_defaulted(field, missing):
    value = minimal()
    if missing == "absent":
        del value[field]
    else:
        value[field] = None if missing == "null" else ""
    with pytest.raises(ValidationError):
        SCENARIO_ADAPTER.validate_python(value)


@pytest.mark.parametrize(
    "updates",
    [
        {"timing_model": "unknown"},
        {"overhead_seconds": "0"},
        {"chunk_tokens": "0"},
        {"chunk_tokens": 8192},
        {"chunk_seconds": "0"},
        {"chunk_seconds": "NaN"},
        {"chunk_seconds": "Infinity"},
        {"chunk_seconds": "-1"},
        {"chunk_seconds": "1" * 129},
        {"min_prompt_tokens": "1"},
        {"max_prompt_tokens": "100"},
        {"min_prompt_tokens": "100", "max_prompt_tokens": "1"},
        {"measurement_boundary": "GB receive"},
        {"source": "verified_measurement"},
        {"source": "verified_measurement", "evidence_sha256": "a" * 64, "sample_count": "10"},
    ],
)
def test_invalid_new_scenarios(updates):
    with pytest.raises(ValidationError):
        SCENARIO_ADAPTER.validate_python(minimal(**updates))


def test_legacy_examples_roundtrip_without_new_fields():
    examples = json.loads(Path("docs/contracts/user-monitoring-v2/examples.json").read_text())
    for example in examples:
        if example["model"] != "Scenario":
            continue
        if example["valid"]:
            result = SCENARIO_ADAPTER.validate_python(example["value"])
            assert isinstance(result, Scenario)
            assert result.model_dump(mode="json") == example["value"]
        else:
            with pytest.raises(ValidationError):
                SCENARIO_ADAPTER.validate_python(example["value"])
