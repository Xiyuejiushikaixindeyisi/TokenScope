"""Deterministic synthetic fixtures. Never reads or imitates confidential production CSVs."""

import argparse
import csv
import json
from datetime import UTC, datetime, timedelta
from pathlib import Path

import numpy as np

from tokenscope.domain import DEFAULT_SETTINGS
from tokenscope.ingestion.csv_reader import REQUIRED_COLUMNS
from tokenscope.monitoring.pipeline import file_digest


def generate(
    output: Path, seed: int = 271027, mean_requests: int = 2000, long_per_app: int = 15
) -> dict:
    output.mkdir(parents=True, exist_ok=False)
    rng = np.random.default_rng(seed)
    files = []
    for number, model in enumerate(DEFAULT_SETTINGS):
        path = output / f"model-{number + 1}.csv"
        count = invalid = duplicates = 0
        apps = []
        with path.open("w", newline="", encoding="utf-8") as stream:
            writer = csv.writer(stream)
            writer.writerow(REQUIRED_COLUMNS)
            for app in range(5):
                appid = f"synthetic-app-{app + 1}"
                regular = int(rng.poisson(mean_requests))
                sizes = [int(v) for v in rng.poisson(512, regular)]
                sizes.extend(int(v) for v in rng.poisson(66000, long_per_app))
                sizes.extend([0, 7999, 8000, 200000, 220000])
                rng.shuffle(sizes)
                for index, length in enumerate(sizes):
                    hash_id = f"app-{app}-req-{index}"
                    if index and index % 79 == 0:
                        hash_id = f"app-{app}-req-{index - 1}"
                        duplicates += 1
                    content = (" token" * length) + f"\nSYNTHETIC task {index % 7} 中文🙂"
                    messages = [
                        {"role": "system", "content": "SYNTHETIC ONLY. Tenant " + appid},
                        {"role": "user", "content": content},
                    ]
                    body = dict(model=model, messages=messages, stream=True, enable_thinking=False)
                    if index % 13 == 0:
                        body["tools"] = [
                            {
                                "type": "function",
                                "function": {
                                    "name": "lookup",
                                    "description": "Synthetic lookup",
                                    "parameters": {
                                        "type": "object",
                                        "properties": {"key": {"type": "string"}},
                                    },
                                },
                            }
                        ]
                        messages.extend(
                            [
                                {
                                    "role": "assistant",
                                    "content": None,
                                    "tool_calls": [
                                        {
                                            "id": "call_1",
                                            "type": "function",
                                            "function": {
                                                "name": "lookup",
                                                "arguments": '{"key":"demo"}',
                                            },
                                        }
                                    ],
                                },
                                {
                                    "role": "tool",
                                    "tool_call_id": "call_1",
                                    "content": "Synthetic tool result.",
                                },
                                {"role": "user", "content": "Continue the synthetic check."},
                            ]
                        )
                    raw = json.dumps(body, ensure_ascii=False, indent=2 if index % 3 == 0 else None)
                    # Out-of-order input and tied timestamps, within one two-hour UTC window.
                    at = datetime(2026, 10, 27, tzinfo=UTC) + timedelta(
                        seconds=int(rng.integers(0, 7200))
                    )
                    writer.writerow(
                        [
                            hash_id,
                            appid,
                            at.isoformat().replace("+00:00", "Z"),
                            int(rng.poisson(128)),
                            raw,
                        ]
                    )
                    count += 1
                    if index % 500 == 0:
                        writer.writerow(["invalid", appid, at.isoformat(), "NaN", "{bad-json"])
                        count += 1
                        invalid += 1
                apps.append(
                    dict(appid=appid, valid_requests=len(sizes), regular_poisson_count=regular)
                )
        files.append(
            dict(
                model_id=model,
                file_ref=path.name,
                sha256=file_digest(path),
                bytes=path.stat().st_size,
                records=count,
                invalid_rows=invalid,
                duplicate_hash_id_rows=duplicates,
                apps=apps,
            )
        )
    manifest = dict(
        kind="synthetic_not_production",
        seed=seed,
        numpy_version=np.__version__,
        appids_per_model=5,
        mean_requests_per_app=mean_requests,
        regular_length_units_poisson_lambda=512,
        long_length_units_poisson_lambda=66000,
        length_unit="repetition of text ` token`; actual model tokens measured by encoder",
        long_per_app=long_per_app,
        deepseek_thinking="explicit false in synthetic requests only",
        files=files,
    )
    (output / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")
    return manifest


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("output", type=Path)
    parser.add_argument("--seed", type=int, default=271027)
    parser.add_argument("--mean-requests", type=int, default=2000)
    parser.add_argument("--long-per-app", type=int, default=15)
    args = parser.parse_args()
    print(
        json.dumps(
            generate(args.output, args.seed, args.mean_requests, args.long_per_app), indent=2
        )
    )
