"""Pre-optimization full fragment identities for bounded synthetic structures."""

import hashlib

import pytest
from profile_hv2 import bodies
from test_extraction import control, view

from tokenscope.analysis_common.plugins import EvidenceCapabilities, PluginSelection
from tokenscope.token_content.current_plugin import CurrentTokenContentPlugin

GOLDEN = {
    "messages": "9c0da0f651eb1bb4d8a0f24493f22702f805d859fe634c10c306f0ef4302da2a",
    "schema": "f91bda86493a9b50c6091a29d13b031e0c4d6f8cd30927ed7cde7bbb44bdd712",
    "wide": "ca7d6046048f2fded4792ab6590a3021dec3cc190e6bab5a6d46008d21aad921",
    "deep": "e7608a040c70e26c70865d7569c071ce32530cb432b928ca61f089467caa4d95",
    "chain": "52351ab82802d30c64330b718c3202f0fdf4a0b5e8d8d26dcadb7f60c09f22e3",
}


@pytest.mark.parametrize("name", GOLDEN)
def test_preoptimization_fragment_identity(name):
    ctl = control(max_units=3000)
    result = CurrentTokenContentPlugin().analyze_request(
        view(bodies()[name]),
        PluginSelection(rule_ids=("T2", "T3", "T4"), budget=ctl.budget),
        EvidenceCapabilities(),
        ctl,
    )
    assert hashlib.sha256(result.model_dump_json().encode()).hexdigest() == GOLDEN[name]
    if name == "messages":
        assert not [o for o in result.observations if o.rule_id == "T3" and o.condition == "met"]
