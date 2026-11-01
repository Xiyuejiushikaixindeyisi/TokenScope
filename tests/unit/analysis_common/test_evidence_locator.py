import hashlib
import json

import pytest

from tokenscope.analysis_common.contracts import EmbeddedLocation, Location, RequestKey
from tokenscope.analysis_common.evidence_locator import locate
from tokenscope.analysis_common.recommendations import RecommendationBudget


def location(raw, pointer, **kwargs):
    return Location(
        request_key=RequestKey(base_run_id="r", source_record_index=0),
        raw_sha256=hashlib.sha256(raw.encode()).hexdigest(),
        source_pointer=pointer,
        **kwargs,
    )


@pytest.mark.parametrize(
    "raw,pointer,text",
    [
        ('{"a":"same","b":"same"}', "/b", '"same"'),
        ('{"n":900719925474099312345}', "/n", "900719925474099312345"),
        ('{"😀":"x\\ny"}', "/😀", '"x\\ny"'),
        ("[null,false,0]", "/0", "null"),
        ("{}", "", "{}"),
    ],
)
def test_exact_lexical_slice(raw, pointer, text):
    result = locate(raw, location(raw, pointer), RecommendationBudget())
    assert result.excerpt == text
    assert result.raw_span is not None
    assert raw[result.raw_span.start : result.raw_span.end] == text
    if pointer == "/b":
        assert result.raw_span.start == raw.rindex('"same"')


def test_duplicate_key_and_missing_never_fake_highlight():
    for raw, pointer in [(' {"x":1,"x":2}', "/x"), ("{}", "/missing")]:
        result = locate(raw, location(raw, pointer), RecommendationBudget())
        assert result.raw_span is None and result.reason_codes


def test_embedded_surrogate_mapping_and_long_content():
    raw = json.dumps({"x": json.dumps({"emoji": "😀", "n": 900719925474099312345})})
    loc = location(raw, "/x", embedded=EmbeddedLocation(parser_version="exact-1", pointer="/n"))
    result = locate(raw, loc, RecommendationBudget())
    assert result.excerpt == "900719925474099312345"
    raw = json.dumps({"content": "x" * 65536})
    result = locate(raw, location(raw, "/content"), RecommendationBudget())
    assert len(result.excerpt) == 1024 and result.omitted_after
    with pytest.raises(ValueError, match="DIGEST"):
        locate(raw + " ", location(raw, "/content"), RecommendationBudget())


def test_decoded_range_and_escape_safe_truncation():
    from tokenscope.analysis_common.contracts import TextRange

    raw = '{"x":"a\\ud83d\\ude00b\\nc"}'
    loc = location(raw, "/x", text_range=TextRange(start=1, end=2))
    result = locate(raw, loc, RecommendationBudget())
    assert result.excerpt == "\\ud83d\\ude00"
    assert result.decoded_span.start == 1 and result.decoded_span.end == 2
    result = locate(raw, loc, RecommendationBudget(max_excerpt_codepoints=6))
    assert result.excerpt == "" and result.omitted_after
    assert result.decoded_span is None
    bad = location(raw, "/x", text_range=TextRange(start=1, end=100))
    assert locate(raw, bad, RecommendationBudget()).reason_codes


@pytest.mark.parametrize(
    "left,right",
    [
        ("stable " * 400 + "2026-10-30 tail", "stable " * 400 + "2026-10-31 tail"),
        ("same " * 400 + "😀\nold tail", "same " * 400 + "😀\nnew tail"),
        ("same " * 400 + "remove tail", "same " * 400 + " tail"),
    ],
)
def test_focus_pair_uses_exact_late_difference(left, right):
    from tokenscope.analysis_common.recommendation_evidence import focus_pair

    a, b = json.dumps({"x": left}), json.dumps({"x": right})
    first, second = focus_pair(a, location(a, "/x"), b, location(b, "/x"), RecommendationBudget())
    assert first.source.text_range.start > 1000
    assert second.source.text_range.start == first.source.text_range.start
    for raw, evidence in [(a, first), (b, second)]:
        assert len(evidence.excerpt) < 50
        assert raw[evidence.raw_span.start : evidence.raw_span.end] == evidence.excerpt
        assert evidence.context_before


def test_focus_pair_does_not_guess_duplicate_key():
    from tokenscope.analysis_common.recommendation_evidence import focus_pair

    a, b = '{"x":"one","x":"two"}', '{"x":"one","x":"three"}'
    first, second = focus_pair(a, location(a, "/x"), b, location(b, "/x"), RecommendationBudget())
    assert first.raw_span is None and second.raw_span is None
    assert first.reason_codes == ("EVIDENCE_LOCATION_AMBIGUOUS",)


@pytest.mark.parametrize(
    "reverse_current,reverse_other", [(False, False), (False, True), (True, False)]
)
def test_dynamic_counterpart_tracks_logical_tool(reverse_current, reverse_other):
    from tokenscope.analysis_common.contracts import RequestComparison
    from tokenscope.analysis_common.recommendation_evidence import counterpart_pointer
    from tokenscope.prefix_analysis.dynamic import comparable_slots, dynamic_recipes
    from tokenscope.prefix_analysis.service import PrefixFinding

    a = {"type": "function", "function": {"name": "a", "description": "workspace /tmp/a"}}
    b = {"type": "function", "function": {"name": "b", "description": "unrelated"}}
    current = {"tools": [b, a] if reverse_current else [a, b]}
    other_a = {"type": "function", "function": {"name": "a", "description": "workspace /tmp/b"}}
    other = {"tools": [b, other_a] if reverse_other else [other_a, b]}
    slot = next(k for k, v in comparable_slots(current).items() if v[1] == "workspace /tmp/a")
    recipe = dynamic_recipes("workspace /tmp/a", "workspace /tmp/b")[0]
    recipe["slot_key"] = slot
    current_pointer = comparable_slots(current)[slot][0]
    other_pointer = comparable_slots(other)[slot][0]
    key = RequestKey(base_run_id="r", source_record_index=0)
    finding = PrefixFinding(
        finding_id="f",
        rule_id="L3",
        source_pointer=other_pointer,
        recipe_json=json.dumps(recipe),
        advice="",
        evidence_status="observed",
        comparison=RequestComparison(
            left=key,
            right=key,
            left_raw_sha256="a" * 64,
            right_raw_sha256="b" * 64,
            difference_pointers=(current_pointer, other_pointer),
        ),
    )
    assert (
        counterpart_pointer(finding, json.dumps(current), json.dumps(other), current_pointer)
        == other_pointer
    )
    assert (
        counterpart_pointer(
            finding, json.dumps(current), json.dumps({"tools": [b]}), current_pointer
        )
        is None
    )
    assert (
        counterpart_pointer(
            finding, json.dumps(current), json.dumps(other), "/tools/9/function/description"
        )
        is None
    )
