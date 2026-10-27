"""Attach the frozen presentation schemas to the actual registered routes."""

import json
from importlib.resources import files
from typing import Any

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi


def install(app: FastAPI) -> None:
    def schema() -> dict[str, Any]:
        if app.openapi_schema:
            return app.openapi_schema
        result = get_openapi(title=app.title, version=app.version, routes=app.routes)
        contract = json.loads(
            files("tokenscope.api").joinpath("monitoring_view_openapi.json").read_text()
        )
        # Namespace the frozen DTOs so legacy model names retain their original meaning.
        contract = json.loads(
            json.dumps(contract).replace(
                "#/components/schemas/", "#/components/schemas/ViewContract"
            )
        )
        for name, value in contract["components"]["schemas"].items():
            result["components"]["schemas"]["ViewContract" + name] = value
        for path, operations in contract["paths"].items():
            for method, operation in operations.items():
                if path not in result["paths"] or method not in result["paths"][path]:
                    raise RuntimeError("Frozen presentation route is not implemented")
                # Keep real operation IDs and document the fixed wire contract.
                current = result["paths"][path][method]
                current.update({k: v for k, v in operation.items() if k != "operationId"})
                current["x-runtime-implemented"] = True
        # Preserve the shared legacy request type name while adding the approved optional key.
        result["components"]["schemas"]["RunSubmission"] = contract["components"]["schemas"][
            "Submission"
        ]
        result["paths"]["/analysis-runs"]["post"]["requestBody"]["content"]["application/json"][
            "schema"
        ] = {"$ref": "#/components/schemas/RunSubmission"}
        app.openapi_schema = result
        return result

    app.openapi = schema  # type: ignore[method-assign]
