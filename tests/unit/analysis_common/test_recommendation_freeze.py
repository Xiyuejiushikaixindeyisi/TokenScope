import hashlib
import json
from pathlib import Path

import pytest

from tokenscope.analysis_common import proposal_plugins, recommendations
from tokenscope.analysis_common.contracts import Contract
from tokenscope.analysis_common.wire import from_wire, wire_schema


def test_schemas_and_examples_are_current():
    root = Path(__file__).resolve().parents[3] / "docs/contracts/analysis-recommendations-1"
    manifest = json.loads((root / "manifest.json").read_text())
    for name, digest in manifest.items():
        assert hashlib.sha256((root / name).read_bytes()).hexdigest() == digest
    internal = json.loads((root / "internal.json").read_text())["models"]
    wire = json.loads((root / "wire.json").read_text())["models"]
    models = {
        name: model
        for module in (recommendations, proposal_plugins)
        for name, model in vars(module).items()
        if isinstance(model, type)
        and issubclass(model, Contract)
        and model.__module__ == module.__name__
    }
    assert set(models) == set(internal) == set(wire)
    for name, model in models.items():
        assert internal[name] == model.model_json_schema()
        assert wire[name] == wire_schema(model)
    fixtures = json.loads((root / "examples.json").read_text())
    for item in fixtures["valid"]:
        from_wire(models[item["model"]], item["wire"])
    for item in fixtures["invalid"]:
        with pytest.raises(ValueError):
            from_wire(models[item["model"]], item["wire"])


def test_public_views_are_separate_from_private_recipe():
    from tokenscope.analysis_common.recommendation_views import recommendation_view_schema

    root = Path(__file__).resolve().parents[3] / "docs/contracts/analysis-recommendations-1"
    manifest = json.loads((root / "http-manifest.json").read_text())
    for name, digest in manifest["files"].items():
        assert hashlib.sha256((root / name).read_bytes()).hexdigest() == digest
    view = json.loads((root / "public-views.json").read_text())["models"]["recommendation"]
    assert view == recommendation_view_schema()
    assert "parameter_generator_json" not in view["$defs"]["Recipe"]["properties"]
