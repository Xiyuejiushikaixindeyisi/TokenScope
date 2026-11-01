"""Additive sealed-report GET endpoints. Never submit, prepare, replay, or backfill."""

import json
import re
import sqlite3
from typing import Any

from fastapi import APIRouter, Depends, Header

from tokenscope.analysis_common.recommendation_store import EXTENSION_MODELS
from tokenscope.analysis_common.recommendation_views import (
    public_recommendation,
    recommendation_view_schema,
)
from tokenscope.analysis_common.recommendations import VERSION, RecommendationSummary
from tokenscope.analysis_common.service import DiagnosticService
from tokenscope.analysis_common.wire import from_wire, to_wire, wire_schema
from tokenscope.errors import TokenScopeError


def router(service: DiagnosticService, instance_id: str) -> APIRouter:
    root = APIRouter(prefix="/diagnostics")

    def validate(kind: str, payload: dict[str, Any]) -> None:
        try:
            from_wire(EXTENSION_MODELS[kind], payload)
        except ValueError as exc:
            raise TokenScopeError(
                "RECOMMENDATION_CONTRACT_MISMATCH",
                "Unsupported or invalid recommendation contract",
                409,
            ) from exc

    @root.get("/recommendations/capabilities")
    def capabilities() -> dict[str, Any]:
        return {
            "version": VERSION,
            "service_instance_id": instance_id,
            "read_only": True,
            "token_rule_ids": ["T2", "T3", "T4"],
            "adapters": [to_wire(d) for d in service.recommendations.registry.capabilities()]
            if service.recommendations
            else [],
            "schemas": {
                **{name: wire_schema(model) for name, model in EXTENSION_MODELS.items()},
                "recommendation": recommendation_view_schema(),
            },
            "legacy_policy": "not_computed_no_backfill",
            "pagination": {"default_limit": "50", "max_limit": "100", "end_cursor": None},
        }

    def identity(x_tokenscope_service_instance: str = Header()) -> None:
        if x_tokenscope_service_instance != instance_id:
            raise TokenScopeError("SERVICE_INSTANCE_MISMATCH", "Diagnostic instance differs", 409)

    api = APIRouter(dependencies=[Depends(identity)])

    def sealed(task_id: str) -> tuple[Any, dict[str, Any], bool]:
        directory = service.store.result_directory(task_id)
        report = json.loads((directory / "report.json").read_bytes())
        with sqlite3.connect((directory / "items.sqlite3").as_uri() + "?mode=ro", uri=True) as db:
            present = db.execute(
                "SELECT payload FROM items WHERE kind='recommendation_summary'"
            ).fetchone()
        if present:
            validate("recommendation_summary", json.loads(present[0]))
        return directory, report, bool(present)

    def page(
        task_id: str, kind: str, offset: str, limit: str, direction: str | None = None
    ) -> dict[str, Any]:
        if not re.fullmatch(r"0|[1-9][0-9]*", offset) or not re.fullmatch(r"[1-9][0-9]*", limit):
            raise TokenScopeError("INVALID_ARGUMENT", "Invalid pagination", 422)
        if (
            len(offset) > 18
            or len(limit) > 3
            or not 1 <= int(limit) <= 100
            or direction not in (None, "low_hit", "token_content")
        ):
            raise TokenScopeError("INVALID_ARGUMENT", "Invalid pagination or direction", 422)
        directory, report, present = sealed(task_id)
        rows = []
        if present:
            with sqlite3.connect(
                (directory / "items.sqlite3").as_uri() + "?mode=ro", uri=True
            ) as db:
                rows = db.execute(
                    "SELECT id,payload FROM items WHERE kind=?"
                    + (" AND json_extract(payload,'$.direction')=?" if direction else "")
                    + " ORDER BY CAST(json_extract(payload,'$.display_order') AS INTEGER),id"
                    + " LIMIT ? OFFSET ?",
                    (kind, *((direction,) if direction else ()), int(limit) + 1, int(offset)),
                ).fetchall()
        items = []
        for ident, raw in rows[: int(limit)]:
            value = json.loads(raw)
            validate(kind, value)
            if (value["task_id"], value["scope_id"]) != (task_id, report["scope_id"]):
                raise TokenScopeError("REPORT_DIGEST_MISMATCH", "Foreign report object", 409)
            items.append(
                {
                    "id": ident,
                    "data": public_recommendation(value) if kind == "recommendation" else value,
                }
            )
        return {
            "version": VERSION,
            "task_id": task_id,
            "scope_id": report["scope_id"],
            "availability": "computed" if present else "not_computed",
            "items": items,
            "offset": offset,
            "next_offset": str(int(offset) + int(limit)) if len(rows) > int(limit) else None,
        }

    def item(task_id: str, kind: str, ident: str) -> dict[str, Any]:
        _, report, present = sealed(task_id)
        rows = service.items(task_id, kind, ident) if present else []
        if not rows:
            raise TokenScopeError("RECOMMENDATION_NOT_FOUND", "Unknown recommendation object", 404)
        value = rows[0]["data"]
        validate(kind, value)
        if (value["task_id"], value["scope_id"]) != (task_id, report["scope_id"]):
            raise TokenScopeError("REPORT_DIGEST_MISMATCH", "Foreign report object", 409)
        return public_recommendation(value) if kind == "recommendation" else value

    @api.get("/tasks/{task_id}/recommendation-summary")
    def summary(task_id: str) -> dict[str, Any]:
        _, report, present = sealed(task_id)
        if present:
            return item(task_id, "recommendation_summary", task_id)
        return to_wire(
            RecommendationSummary(
                task_id=task_id,
                scope_id=report["scope_id"],
                availability="not_computed",
                configured_recipe_count=None,
                recommendation_count=0,
                difference_group_count=0,
                proposal_coverage=None,
                evaluation_coverage=None,
                budget=None,
                budget_digest=None,
                consumed=None,
            )
        )

    @api.get("/tasks/{task_id}/recommendations")
    def recommendations(
        task_id: str, offset: str = "0", limit: str = "50", direction: str | None = None
    ) -> dict[str, Any]:
        return page(task_id, "recommendation", offset, limit, direction)

    @api.get("/tasks/{task_id}/recommendations/{recommendation_id}")
    def recommendation(task_id: str, recommendation_id: str) -> dict[str, Any]:
        return item(task_id, "recommendation", recommendation_id)

    def examples(task_id: str, kind: str, owner_id: str) -> dict[str, Any]:
        owner = item(task_id, kind, owner_id)
        rows = [
            {"id": ref["id"], "data": item(task_id, "recommendation_example", ref["id"])}
            for ref in owner["example_refs"]
        ]
        if any(row["data"]["owner_id"] != owner_id for row in rows):
            raise TokenScopeError("REPORT_DIGEST_MISMATCH", "Foreign example owner", 409)
        return {
            "version": VERSION,
            "task_id": task_id,
            "scope_id": owner["scope_id"],
            "items": rows,
            "next_offset": None,
        }

    @api.get("/tasks/{task_id}/recommendations/{recommendation_id}/examples")
    def recommendation_examples(task_id: str, recommendation_id: str) -> dict[str, Any]:
        return examples(task_id, "recommendation", recommendation_id)

    @api.get("/tasks/{task_id}/difference-groups")
    def differences(task_id: str, offset: str = "0", limit: str = "50") -> dict[str, Any]:
        return page(task_id, "difference_group", offset, limit)

    @api.get("/tasks/{task_id}/difference-groups/{group_id}/examples")
    def difference_examples(task_id: str, group_id: str) -> dict[str, Any]:
        return examples(task_id, "difference_group", group_id)

    root.include_router(api)
    return root
