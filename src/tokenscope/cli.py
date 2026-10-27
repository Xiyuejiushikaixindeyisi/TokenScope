"""CLI uses the same service as HTTP; validate-input is explicitly not analysis."""

import argparse
import json
import sqlite3
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from tokenscope.api.app import create_app
from tokenscope.domain import RunSubmission, SettingsUpdate
from tokenscope.errors import TokenScopeError
from tokenscope.monitoring.rules import RuleUpdate
from tokenscope.monitoring.service import MonitoringService
from tokenscope.resources import configure_process


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="tokenscope")
    parser.add_argument("--input-root", type=Path, required=True)
    parser.add_argument("--state-root", type=Path, required=True)
    parser.add_argument("--asset-root", type=Path)
    parser.add_argument("--cpu-budget", type=int, default=8)
    subcommands = parser.add_subparsers(dest="command", required=True)
    for name in ("version", "models", "ready", "schema", "work-once"):
        subcommands.add_parser(name)
    settings = subcommands.add_parser("settings")
    settings.add_argument("model_id")
    settings.add_argument(
        "--update-json", help="SettingsUpdate JSON (expected_revision and changes)"
    )
    for name in ("validate-input", "submit"):
        command = subcommands.add_parser(name)
        command.add_argument("file_ref")
        command.add_argument("--model", required=True)
    run = subcommands.add_parser("run")
    run.add_argument("run_id")
    rules = subcommands.add_parser("rules")
    rules.add_argument("--update-json")
    for name in ("metrics", "histograms", "lengths", "signals", "explain"):
        command = subcommands.add_parser(name)
        command.add_argument("run_id")
        if name in ("metrics", "histograms", "lengths"):
            command.add_argument("--appid", required=name != "metrics")
        if name in ("metrics", "lengths"):
            command.add_argument("--offset", type=int, default=0)
            command.add_argument("--limit", type=int, default=100)
        if name == "histograms":
            command.add_argument("--bin-width", type=int, default=5000)
        if name == "lengths":
            command.add_argument("--metric", default="prompt_tokens")
            command.add_argument("--lower", type=int, default=0)
            command.add_argument("--upper", type=int)
        if name == "explain":
            command.add_argument("--record", type=int, required=True)
    serve = subcommands.add_parser("serve")
    serve.add_argument("--host", default="127.0.0.1")
    serve.add_argument("--port", type=int, default=8000)
    serve.add_argument("--viewer-root", type=Path, help="Built viewer dist for same-origin UI")
    args = parser.parse_args(argv)
    try:
        service = MonitoringService(
            args.input_root, args.state_root, args.asset_root, args.cpu_budget
        )
        result: Any
        if args.command == "version":
            result = service.version()
        elif args.command == "models":
            result = service.models()
        elif args.command == "ready":
            result = service.readiness()
        elif args.command == "schema":
            result = create_app(service).openapi()
        elif args.command == "settings":
            if args.update_json:
                result = service.update_settings(
                    args.model_id, SettingsUpdate.model_validate_json(args.update_json)
                )
            else:
                result = service.model(args.model_id)
        elif args.command in ("validate-input", "submit"):
            submission = RunSubmission.model_validate(
                {"file_ref": args.file_ref, "model_id": args.model}
            )
            result = (
                service.validate_input(submission)
                if args.command == "validate-input"
                else service.submit(submission).model_dump(mode="json")
            )
        elif args.command == "run":
            result = service.control.run(args.run_id).model_dump(mode="json")
        elif args.command == "work-once":
            processed = service.processor.process_next()
            result = processed.model_dump(mode="json") if processed else None
        elif args.command == "metrics":
            result = service.metrics(args.run_id, args.appid, args.offset, args.limit)
        elif args.command == "histograms":
            result = service.histograms(args.run_id, args.appid, args.bin_width)
        elif args.command == "lengths":
            result = service.lengths(
                args.run_id,
                args.appid,
                args.metric,
                args.lower,
                args.upper,
                args.offset,
                args.limit,
            )
        elif args.command == "signals":
            result = service.control.signals(args.run_id)
        elif args.command == "explain":
            result = service.explain_encoding(args.run_id, args.record)
        elif args.command == "rules":
            result = (
                service.control.update_rule(RuleUpdate.model_validate_json(args.update_json))
                if args.update_json
                else service.control.rules()
            )
        elif args.command == "serve":
            import uvicorn

            uvicorn.run(
                create_app(service, viewer_root=args.viewer_root), host=args.host, port=args.port
            )
            return 0
        else:
            raise AssertionError("Unrecognized parsed command")
        print(json.dumps(result, ensure_ascii=False, sort_keys=True))
        return 3 if args.command == "ready" and not result["ready"] else 0
    except TokenScopeError as exc:
        print(json.dumps({"error": exc.as_dict()}, ensure_ascii=False))
        return 2
    except ValidationError:
        print(json.dumps({"error": {"code": "INVALID_REQUEST", "message": "Invalid CLI input"}}))
        return 2
    except (sqlite3.Error, OSError):
        print(
            json.dumps(
                {
                    "error": {
                        "code": "STORAGE_UNAVAILABLE",
                        "message": "Local storage operation failed",
                    }
                }
            )
        )
        return 2


def entrypoint() -> int:
    # The dedicated OS process is constrained; programmatic main() does not alter its host.
    resource_parser = argparse.ArgumentParser(add_help=False)
    resource_parser.add_argument("--cpu-budget", type=int, default=8)
    args, _ = resource_parser.parse_known_args()
    try:
        configure_process(args.cpu_budget)
    except TokenScopeError as exc:
        print(json.dumps({"error": exc.as_dict()}))
        return 2
    return main()


if __name__ == "__main__":
    raise SystemExit(entrypoint())
