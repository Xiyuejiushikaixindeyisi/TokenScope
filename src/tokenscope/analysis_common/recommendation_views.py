"""Read-only business metadata projection, excluding private recipe configuration."""

import copy
from fractions import Fraction
from typing import Any

from tokenscope.analysis_common.contracts import gain_percentage_points
from tokenscope.analysis_common.recommendation_grouping import digest
from tokenscope.analysis_common.recommendations import Recommendation
from tokenscope.analysis_common.wire import from_wire, wire_schema


def rational(value: Fraction | None) -> dict[str, str] | None:
    return (
        None
        if value is None
        else {"numerator": str(value.numerator), "denominator": str(value.denominator)}
    )


def public_recommendation(payload: dict[str, Any]) -> dict[str, Any]:
    rec = from_wire(Recommendation, payload)
    view = copy.deepcopy(payload)
    recipe = view["recipe"]
    for name in ("selector_json", "parameter_generator_json"):
        recipe[name + "_digest"] = digest(recipe.pop(name))
    if recipe["basis"]:
        recipe["basis"]["scope_selector_digest"] = digest(recipe["basis"].pop("scope_selector"))
    ev = rec.evaluation
    view["metrics"] = None
    if ev and ev.status == "available" and ev.before and ev.after:
        view["metrics"] = {
            "gain_percentage_points": rational(gain_percentage_points(ev.before, ev.after)),
            "input_tokens_delta": str(ev.after.p - ev.before.p),
            "input_tokens_ratio": rational(
                Fraction(ev.after.p - ev.before.p, ev.before.p) if ev.before.p else None
            ),
            "compute_tokens_delta": str(ev.after.c - ev.before.c),
            "compute_tokens_ratio": rational(
                Fraction(ev.after.c - ev.before.c, ev.before.c) if ev.before.c else None
            ),
        }
    return view


def recommendation_view_schema() -> dict[str, Any]:
    schema = wire_schema(Recommendation)
    for model, fields in [
        ("Recipe", ("selector_json", "parameter_generator_json")),
        ("Basis", ("scope_selector",)),
    ]:
        definition = schema["$defs"][model]
        for field in fields:
            definition["properties"].pop(field)
            definition["properties"][field + "_digest"] = {
                "type": "string",
                "pattern": "^[0-9a-f]{64}$",
            }
            definition["required"].remove(field)
            definition["required"].append(field + "_digest")
    fraction = {
        "anyOf": [
            {"type": "null"},
            {
                "type": "object",
                "additionalProperties": False,
                "required": ["numerator", "denominator"],
                "properties": {
                    "numerator": {"type": "string", "pattern": "^(0|-?[1-9][0-9]*)$"},
                    "denominator": {"type": "string", "pattern": "^[1-9][0-9]*$"},
                },
            },
        ]
    }
    delta = {"type": "string", "pattern": "^(0|-?[1-9][0-9]*)$"}
    schema["properties"]["metrics"] = {
        "anyOf": [
            {"type": "null"},
            {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "gain_percentage_points": fraction,
                    "input_tokens_delta": delta,
                    "input_tokens_ratio": fraction,
                    "compute_tokens_delta": delta,
                    "compute_tokens_ratio": fraction,
                },
                "required": [
                    "gain_percentage_points",
                    "input_tokens_delta",
                    "input_tokens_ratio",
                    "compute_tokens_delta",
                    "compute_tokens_ratio",
                ],
            },
        ]
    }
    schema["required"].append("metrics")
    return schema
