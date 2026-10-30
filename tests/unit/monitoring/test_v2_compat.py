import pytest

from tokenscope.domain import DEFAULT_SETTINGS, SettingsUpdate
from tokenscope.errors import TokenScopeError
from tokenscope.ingestion.csv_reader import InvalidRow, parse_utc, validate_request
from tokenscope.monitoring.storage import ControlStore


@pytest.mark.parametrize("fraction", ["", ".1", ".123456789"])
def test_day_first_exact_nanoseconds(fraction):
    assert parse_utc("20/10/2026 07:00:03" + fraction) == parse_utc(
        "2026-10-20T07:00:03" + fraction + "Z"
    )


@pytest.mark.parametrize(
    "bad",
    [
        "29/02/2025 00:00:00",
        "20/13/2026 07:00:00",
        "10/20/2026 07:00:00",
        "20/10/2026 07:00:00.1234567890",
        "1790000000",
    ],
)
def test_no_guessing_and_field(bad):
    with pytest.raises(InvalidRow) as e:
        parse_utc(bad, field="request_time")
    assert e.value.field == "request_time"


def test_utc_policy_and_offset():
    assert parse_utc("01/03/2024 00:00:00") == parse_utc("2024-03-01T08:00:00+08:00")
    assert parse_utc("29/02/2024 23:00:00") == parse_utc("2024-03-01T00:00:00+01:00")
    with pytest.raises(InvalidRow, match="UNSUPPORTED_SOURCE_TIMEZONE"):
        parse_utc("2026-01-01 00:00:00", source_timezone="unknown")


def test_all_registered_aliases_and_unknown():
    import json

    for settings in DEFAULT_SETTINGS.values():
        for alias in settings.model_aliases:
            validate_request(
                json.dumps({"model": alias, "messages": [{"role": "user", "content": "hello"}]}),
                settings,
            )
        with pytest.raises(InvalidRow, match="MODEL_MISMATCH"):
            validate_request(
                '{"model":"unknown","messages":[{"role":"user","content":"hello"}]}', settings
            )


def test_existing_settings_not_overwritten_and_conflict(tmp_path):
    path = tmp_path / "control.db"
    store = ControlStore(path)
    assert store.settings("DeepSeek-V4-Flash-0731").encoding_profile == "thinking_disabled"
    store.update_settings(
        "DeepSeek-V4-Flash-0731",
        SettingsUpdate.model_validate(
            {"expected_revision": 1, "changes": {"encoding_profile": "default"}}
        ),
    )
    assert ControlStore(path).settings("DeepSeek-V4-Flash-0731").encoding_profile == "default"
    with pytest.raises(TokenScopeError) as e:
        store.update_settings(
            "GLM-5.2",
            SettingsUpdate.model_validate(
                {"expected_revision": 1, "changes": {"model_aliases": ["Qwen-V3.6-27B"]}}
            ),
        )
    assert e.value.code == "MODEL_ALIAS_CONFLICT"
    assert store.settings("GLM-5.2").revision == 1
