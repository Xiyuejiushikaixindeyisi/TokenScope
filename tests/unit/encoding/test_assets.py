import hashlib
import json

import pytest

from tokenscope.encoding.assets import AssetRegistry
from tokenscope.errors import TokenScopeError


def fixture_assets(tmp_path):
    files = []
    for name in ("tokenizer.json", "tokenizer_config.json", "chat_template.jinja"):
        path = tmp_path / name
        path.write_bytes(b"synthetic validation fixture, not a tokenizer")
        files.append(
            {
                "path": name,
                "role": name,
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                "source_url": "https://example.invalid/synthetic",
            }
        )
    lock = {
        "schema_version": 1,
        "models": [
            {
                "model_id": "GLM-5.2",
                "source": "synthetic",
                "revision": "a" * 40,
                "license": "test",
                "files": files,
            }
        ],
    }
    target = tmp_path / "lock.json"
    target.write_text(json.dumps(lock))
    return lock, target


def test_verified_bytes_do_not_change_after_load(tmp_path):
    _, path = fixture_assets(tmp_path)
    registry = AssetRegistry(tmp_path, path)
    loaded = registry.load("GLM-5.2")
    (tmp_path / "tokenizer.json").write_bytes(b"modified")
    assert loaded.contents["tokenizer.json"] == b"synthetic validation fixture, not a tokenizer"
    with pytest.raises(TokenScopeError) as error:
        registry.load("GLM-5.2")
    assert error.value.code == "ASSET_DIGEST_MISMATCH"


@pytest.mark.parametrize(
    "change,code",
    [
        ("missing", "ASSET_MISSING"),
        ("escape", "INVALID_ASSET_PATH"),
        ("duplicate", "INVALID_ASSET_LOCK"),
        ("schema", "INVALID_ASSET_LOCK"),
    ],
)
def test_invalid_assets_fail_closed(tmp_path, change, code):
    lock, target = fixture_assets(tmp_path)
    if change == "missing":
        (tmp_path / "tokenizer.json").unlink()
    elif change == "escape":
        lock["models"][0]["files"][0]["path"] = "../tokenizer.json"
    elif change == "duplicate":
        lock["models"].append(lock["models"][0])
    elif change == "schema":
        lock["schema_version"] = 999
    target.write_text(json.dumps(lock))
    with pytest.raises(TokenScopeError) as error:
        AssetRegistry(tmp_path, target).load("GLM-5.2")
    assert error.value.code == code


def test_missing_model_does_not_choose_another(tmp_path):
    _, target = fixture_assets(tmp_path)
    with pytest.raises(TokenScopeError) as error:
        AssetRegistry(tmp_path, target).load("Qwen3.6-27B")
    assert error.value.code == "ASSETS_NOT_FOUND"
