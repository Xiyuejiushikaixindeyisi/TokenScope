"""Export deterministic schemas for the shared internal and decimal-wire models."""

import json
import sys
from pathlib import Path

from tokenscope.analysis_common import contracts, plugins
from tokenscope.analysis_common.contracts import CONTRACT_VERSION, Contract
from tokenscope.analysis_common.wire import wire_schema


def export(directory: Path) -> None:
    directory.mkdir(parents=True, exist_ok=True)
    models = {
        name: value
        for module in (contracts, plugins)
        for name, value in vars(module).items()
        if isinstance(value, type) and issubclass(value, Contract) and value is not Contract
    }
    for kind in ("internal", "wire"):
        payload = {
            "version": CONTRACT_VERSION,
            "models": {
                name: (model.model_json_schema() if kind == "internal" else wire_schema(model))
                for name, model in sorted(models.items())
            },
        }
        (directory / f"{kind}.json").write_text(
            json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
            encoding="utf-8",
        )


if __name__ == "__main__":
    export(Path(sys.argv[1]))
