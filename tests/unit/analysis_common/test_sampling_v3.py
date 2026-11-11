import pytest
from pydantic import ValidationError

from tokenscope.analysis_common.contracts import RequestKey
from tokenscope.analysis_common.sampling_v3 import SampleLimits, SampleMetadata, select_windows
from tokenscope.analysis_common.wire_v3 import from_wire, to_wire


def limits(**changes):
    values = dict(
        max_requests=6,
        max_raw_bytes=60,
        max_prompt_tokens=60,
        max_record_bytes=10,
        max_record_tokens=10,
        max_metadata_bytes=10000,
        max_snapshot_bytes=100000,
        max_exclusion_examples=2,
    )
    values.update(changes)
    return SampleLimits(**values)


def rows(count, *, bad=()):
    for index in range(count):
        yield SampleMetadata(
            key=RequestKey(base_run_id="run", source_record_index=index),
            time_ns=index // 2,
            raw_bytes=11 if index in bad else 10,
            prompt_tokens=10,
        )


def indices(window):
    return [r.key.source_record_index for r in window.members]


def test_first_prefix_latest_suffix_with_exact_tied_timestamp_members():
    result = select_windows(rows(10), limits())
    assert [indices(w) for w in result.windows] == [[0, 1, 2], [7, 8, 9]]
    assert result.parent_count == result.admitted_count == 10
    assert result.excluded_count == 0
    assert sum(w.raw_bytes for w in result.windows) == 60
    assert result == select_windows(rows(10), limits())


def test_rejection_breaks_contiguity_and_trailing_bad_record_keeps_last_valid_segment():
    result = select_windows(rows(11, bad=(1, 5, 9, 10)), limits())
    assert [indices(w) for w in result.windows] == [[0], [6, 7, 8]]
    assert result.excluded_count == 4
    assert result.exclusion_counts == {"RECORD_BYTE_LIMIT": 4}
    assert len(result.exclusion_examples) == 2


@pytest.mark.parametrize("size,excluded", [(9, 0), (10, 0), (11, 1)])
def test_byte_boundary_before_body_access(size, excluded):
    row = SampleMetadata(
        key=RequestKey(base_run_id="run", source_record_index=1),
        time_ns=0,
        raw_bytes=size,
        prompt_tokens=5,
    )
    result = select_windows([row], limits())
    assert result.excluded_count == excluded


def test_empty_whole_scope_and_no_review():
    assert select_windows([], limits()).windows == ()
    whole = select_windows(rows(2), limits())
    assert [indices(w) for w in whole.windows] == [[0, 1]]
    one = select_windows(rows(10), limits(max_requests=1))
    assert [indices(w) for w in one.windows] == [[0]]
    original = limits(review_requested=False)
    assert [indices(w) for w in select_windows(rows(10), original).windows] == [list(range(6))]


def test_unencoded_record_is_not_spliced_into_a_contiguous_window():
    source = list(rows(5))
    source[2] = source[2].model_copy(update={"prompt_tokens": None})
    result = select_windows(source, limits())
    assert [indices(w) for w in result.windows] == [[0, 1], [3, 4]]
    assert result.parent_count == result.admitted_count + result.excluded_count == 5
    assert result.exclusion_counts == {"UNENCODED_RECORD": 1}


def test_invalid_order_overlap_and_budget_are_rejected():
    with pytest.raises(ValueError, match="ordered"):
        select_windows(reversed(list(rows(3))), limits())
    result = select_windows(rows(8), limits())
    data = result.model_dump()
    data["windows"] = (data["windows"][0], data["windows"][0] | {"role": "review"})
    with pytest.raises(ValidationError, match="overlap"):
        type(result).model_validate(data)
    with pytest.raises(ValidationError):
        limits(max_requests=0)


def test_large_parent_does_not_expand_member_or_exclusion_lists():
    result = select_windows(rows(100000), limits())
    assert result.parent_count == 100000
    assert sum(len(w.members) for w in result.windows) == 6
    assert indices(result.windows[1]) == [99997, 99998, 99999]


def test_wire_roundtrip_preserves_exclusion_counts_and_rejects_numeric_wire_values():
    decision = select_windows(rows(8, bad=(3,)), limits())
    wire = to_wire(decision)
    assert wire["exclusion_counts"]["RECORD_BYTE_LIMIT"] == "1"
    assert from_wire(type(decision), wire) == decision
    wire["exclusion_counts"]["RECORD_BYTE_LIMIT"] = 1
    with pytest.raises(ValueError, match="canonical decimal"):
        from_wire(type(decision), wire)
