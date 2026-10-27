"""Pinned local assets are verified before any tokenizer or template is loaded."""

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path

from pydantic import Field, ValidationError

from tokenscope.domain import ModelId, StrictModel
from tokenscope.errors import TokenScopeError


class AssetFile(StrictModel):
    path: str
    role: str
    sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    source_url: str


class ModelAssetSpec(StrictModel):
    model_id: ModelId
    source: str
    revision: str = Field(pattern=r"^[0-9a-f]{40}$")
    license: str
    files: tuple[AssetFile, ...]


@dataclass(frozen=True)
class VerifiedAssets:
    spec: ModelAssetSpec
    identity: str
    contents: dict[str, bytes]


class AssetRegistry:
    def __init__(self, project_root: Path, lock_path: Path | None = None) -> None:
        self.root = project_root.resolve(strict=True)
        self.lock_path = lock_path or self.root / "env/encoding-assets.lock.json"

    def load(self, model_id: str) -> VerifiedAssets:
        try:
            data = json.loads(self.lock_path.read_text(encoding="utf-8"))
            if data["schema_version"] != 1:
                raise ValueError("Unknown asset schema")
            specs = [ModelAssetSpec.model_validate(item) for item in data["models"]]
            if len({s.model_id for s in specs}) != len(specs):
                raise ValueError("Duplicate model")
        except (OSError, ValueError, KeyError, TypeError, ValidationError) as exc:
            raise TokenScopeError(
                "INVALID_ASSET_LOCK", "Cannot read the encoding asset lock", 503
            ) from exc
        spec = next((item for item in specs if item.model_id == model_id), None)
        if spec is None:
            raise TokenScopeError("ASSETS_NOT_FOUND", "No pinned assets for this model", 503)
        contents: dict[str, bytes] = {}
        for item in spec.files:
            candidate = Path(item.path)
            if candidate.is_absolute() or ".." in candidate.parts:
                raise TokenScopeError(
                    "INVALID_ASSET_PATH", "Asset path must stay in the project", 503
                )
            try:
                path = (self.root / candidate).resolve(strict=True)
                if not path.is_relative_to(self.root) or not path.is_file():
                    raise TokenScopeError(
                        "INVALID_ASSET_PATH", "Asset path must stay in the project", 503
                    )
                content = path.read_bytes()
            except OSError as exc:
                raise TokenScopeError(
                    "ASSET_MISSING", "Pinned encoding asset is missing", 503
                ) from exc
            if hashlib.sha256(content).hexdigest() != item.sha256:
                raise TokenScopeError(
                    "ASSET_DIGEST_MISMATCH", "Encoding asset checksum mismatch", 503
                )
            if item.role in contents:
                raise TokenScopeError("INVALID_ASSET_LOCK", "Duplicate asset role", 503)
            contents[item.role] = content
        required = {"tokenizer.json", "tokenizer_config.json"}
        if model_id != "DeepSeek-V4-Flash-0731":
            required.add("chat_template.jinja")
        if not required <= contents.keys():
            raise TokenScopeError("ASSET_MISSING", "Required model encoding files are absent", 503)
        identity = hashlib.sha256(
            json.dumps(spec.model_dump(mode="json"), sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()
        return VerifiedAssets(spec, identity, contents)
