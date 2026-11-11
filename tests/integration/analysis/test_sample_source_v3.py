import json
from pathlib import Path

import pytest
from conftest import csv_bytes, valid_row

from tokenscope.analysis_common.contracts import SourceSelection
from tokenscope.analysis_common.sample_source import open_sample_window
from tokenscope.analysis_common.sampling_v3 import SampleLimits
from tokenscope.analysis_common.source import SourceResolver
from tokenscope.analysis_common.source_preparation import PreparationIO, prepare_snapshot
from tokenscope.domain import RunSubmission
from tokenscope.errors import TokenScopeError
from tokenscope.monitoring.pipeline import file_digest
from tokenscope.user_monitoring.contracts import Bind
from tokenscope.user_monitoring.service import UserRunService


def limits(**changes):
    data = dict(
        max_requests=4,
        max_raw_bytes=100000,
        max_prompt_tokens=100000,
        max_record_bytes=40000,
        max_record_tokens=20000,
        max_metadata_bytes=1000000,
        max_snapshot_bytes=2000000,
        max_exclusion_examples=4,
    )
    data.update(changes)
    return SampleLimits(**data)


def source(service):
    rows = []
    for i in range(9):
        body = json.dumps(
            {"messages": [{"role": "user", "content": f"request {i} " + "shared " * 30}]}
        )
        rows.append(
            valid_row(
                appid="other" if i == 2 else "a",
                hash_id="same-hash",
                request_input=body,
                model_handle_start_time=f"2026-10-27T00:00:0{i // 2}Z",
            )
        )
    (service.inputs.root / "sample.csv").write_bytes(csv_bytes(rows))
    run = service.submit(RunSubmission(file_ref="sample.csv", model_id="GLM-5.2"))
    assert service.processor.process_next().status == "completed"
    return SourceSelection(source_kind="base", base_run_id=run.run_id, appid="a")


def test_real_seal_exact_members_and_sample_only_reads(service, tmp_path, monkeypatch):
    selection = source(service)
    resolver = SourceResolver(service)
    original = resolver.resolve_scope(selection)
    original_digest = file_digest(original.directory / "requests.sqlite3")
    target = tmp_path / "snapshots" / "one"
    import tokenscope.analysis_common.source_preparation as preparation

    materialized = []
    original_view = preparation.selected_view

    def track(resolved, db, member, budget):
        materialized.append(member.key.source_record_index)
        return original_view(resolved, db, member, budget)

    monkeypatch.setattr(preparation, "selected_view", track)
    manifest = prepare_snapshot(resolver, selection, limits(), target)
    assert materialized == [1, 2, 8, 9]
    assert manifest.parent_scope.request_count == 8
    assert [[m.key.source_record_index for m in w.members] for w in manifest.decision.windows] == [
        [1, 2],
        [8, 9],
    ]
    assert manifest.verification_bytes > manifest.selected_raw_bytes
    assert file_digest(original.directory / "requests.sqlite3") == original_digest
    digest = file_digest(target / "manifest.json")
    a = open_sample_window(service, target, digest, "discovery", metadata_limit=1000000)
    b = open_sample_window(service, target, digest, "review", metadata_limit=1000000)
    expected = [(r.raw_body, original.read_ids(r)) for r in original.iter_requests()][:2]

    real_open = Path.open

    def protected(path, *args, **kwargs):
        assert not path.is_relative_to(original.directory)
        assert not path.is_relative_to(target / "review")
        return real_open(path, *args, **kwargs)

    monkeypatch.setattr(Path, "open", protected)
    actual = list(a.iter_requests())
    assert [(r.raw_body, a.read_ids(r)) for r in actual] == expected
    assert len({r.request_key for r in actual}) == 2
    assert actual[0].hash_id == actual[1].hash_id
    with pytest.raises(TokenScopeError, match="outside"):
        a.read_request(manifest.decision.windows[1].members[0].key)
    with pytest.raises(TokenScopeError, match="exact sample"):
        a._rows()
    assert a.scope.scope_id != b.scope.scope_id


def test_changed_source_does_not_publish_snapshot(service, tmp_path, monkeypatch):
    selection = source(service)
    import tokenscope.analysis_common.source_preparation as module

    original = module.selected_view
    changed = False

    def mutate(resolved, db, member, budget):
        nonlocal changed
        result = original(resolved, db, member, budget)
        if not changed:
            path = resolved.directory / "manifest.json"
            path.write_text(path.read_text() + " ")
            changed = True
        return result

    monkeypatch.setattr(module, "selected_view", mutate)
    target = tmp_path / "changed"
    with pytest.raises(TokenScopeError, match="changed"):
        prepare_snapshot(SourceResolver(service), selection, limits(), target)
    assert not target.exists()
    assert target.with_name("changed.working").exists()


def test_cancellation_and_disk_budget_never_seal(service, tmp_path):
    selection = source(service)
    calls = 0

    def stop():
        nonlocal calls
        calls += 1
        if calls == 3:
            raise TokenScopeError("CANCELLED", "Cancelled", 409)

    target = tmp_path / "cancelled"
    with pytest.raises(TokenScopeError, match="Cancelled"):
        prepare_snapshot(
            SourceResolver(service),
            selection,
            limits(),
            target,
            io=PreparationIO(1000000, checkpoint=stop),
        )
    assert not target.exists()
    with pytest.raises(TokenScopeError, match="disk"):
        prepare_snapshot(
            SourceResolver(service), selection, limits(max_snapshot_bytes=1), tmp_path / "disk"
        )
    assert not (tmp_path / "disk").exists()


def test_byte_admission_precedes_selected_body_materialization(service, tmp_path, monkeypatch):
    selection = source(service)
    import tokenscope.analysis_common.source_preparation as module

    def forbidden(*args, **kwargs):
        raise AssertionError("No oversized body may be materialized")

    monkeypatch.setattr(module, "selected_view", forbidden)
    with pytest.raises(TokenScopeError, match="No complete request"):
        prepare_snapshot(
            SourceResolver(service), selection, limits(max_record_bytes=1), tmp_path / "small"
        )
    assert not (tmp_path / "small").exists()


@pytest.mark.parametrize("damage", ["sha", "count", "path", "missing"])
def test_invalid_token_slice_never_publishes(service, tmp_path, monkeypatch, damage):
    selection = source(service)
    import tokenscope.analysis_common.source_preparation as module

    original = module.selected_view

    def corrupt(resolved, db, member, budget):
        data = original(resolved, db, member, budget)
        ref = json.loads(data["token_slice_json"])
        if damage == "sha":
            ref["sha256"] = "0" * 64
        elif damage == "count":
            ref["token_count"] += 1
        elif damage == "path":
            ref["shard"] = "../outside.bin"
        else:
            ref["shard"] = "tokens-999999.bin"
        data["token_slice_json"] = json.dumps(ref)
        return data

    monkeypatch.setattr(module, "selected_view", corrupt)
    target = tmp_path / "invalid"
    with pytest.raises((TokenScopeError, FileNotFoundError)):
        prepare_snapshot(SourceResolver(service), selection, limits(), target)
    assert not target.exists()


def test_user_index_revision_is_pinned_in_sample(service, tmp_path):
    selection = source(service)
    user = UserRunService(service)
    receipt = user.submit(
        Bind(submission_key="user", base_run_id=selection.base_run_id, common_name="GLM-5.2")
    )
    user.process_next()
    current = user.receipt(receipt.user_run_id)
    selected = SourceSelection(source_kind="user_v2", user_run_id=receipt.user_run_id, appid="a")
    result = prepare_snapshot(SourceResolver(service, user), selected, limits(), tmp_path / "user")
    assert result.source_index_revision == current.index_revision
    assert result.source_selection.expected_index_revision == current.index_revision
    with pytest.raises(TokenScopeError, match="revision"):
        prepare_snapshot(
            SourceResolver(service, user),
            selected.model_copy(update={"expected_index_revision": "stale"}),
            limits(),
            tmp_path / "stale",
        )
