"""Export independent recommendation schemas without rewriting H0/HTTP manifests."""

import hashlib
import json
from pathlib import Path

from recommendation_contract_examples import examples

from tokenscope.analysis_common import proposal_plugins, recommendations
from tokenscope.analysis_common.contracts import Contract
from tokenscope.analysis_common.wire import wire_schema


def export(directory: Path) -> None:
    directory.mkdir(parents=True, exist_ok=True)
    models = {
        name: model
        for module in (recommendations, proposal_plugins)
        for name, model in vars(module).items()
        if isinstance(model, type)
        and issubclass(model, Contract)
        and model is not Contract
        and model.__module__ == module.__name__
    }
    manifest = {}
    for kind in ("internal", "wire"):
        payload = {
            "version": recommendations.VERSION,
            "models": {
                name: model.model_json_schema() if kind == "internal" else wire_schema(model)
                for name, model in sorted(models.items())
            },
        }
        data = (json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode()
        (directory / f"{kind}.json").write_bytes(data)
        manifest[f"{kind}.json"] = hashlib.sha256(data).hexdigest()
    data = (json.dumps(examples(), ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode()
    (directory / "examples.json").write_bytes(data)
    manifest["examples.json"] = hashlib.sha256(data).hexdigest()
    (directory / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")


if __name__ == "__main__":
    export(Path("docs/contracts/analysis-recommendations-1"))
