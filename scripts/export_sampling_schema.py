"""Export/check only the new sampling contract; never rewrites v1/v2 files."""

import argparse
import hashlib
import json
from pathlib import Path

from tokenscope.analysis_common.contracts import (
    AnalysisScope,
    RequestKey,
    SourceIdentity,
    SourceSelection,
)
from tokenscope.analysis_common.contracts_v3 import (
    PreparationReceipt3,
    PreparationRequest3,
    SampleManifest3,
    SnapshotFile3,
)
from tokenscope.analysis_common.sampling_v3 import SampleLimits, SampleMetadata, select_windows
from tokenscope.analysis_common.wire_v3 import to_wire, wire_schema


def document(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")


def export_values():
    selection = SourceSelection(source_kind="base", base_run_id="example-run", appid="example-app")
    request = PreparationRequest3(submission_key="example-submission", source=selection)
    receipt = PreparationReceipt3(
        preparation_id="prep-" + "1" * 32,
        state="queued",
        intent_digest=request.intent_digest,
    )
    limits = SampleLimits(
        max_requests=2,
        max_raw_bytes=100,
        max_prompt_tokens=100,
        max_record_bytes=50,
        max_record_tokens=50,
        max_metadata_bytes=100000,
        max_snapshot_bytes=200000,
        max_exclusion_examples=2,
    )
    decision = select_windows(
        [
            SampleMetadata(
                key=RequestKey(base_run_id="example-run", source_record_index=n),
                time_ns=n,
                raw_bytes=2,
                prompt_tokens=0,
            )
            for n in (1, 2)
        ],
        limits,
    )
    identity = SourceIdentity(
        base_run_id="example-run",
        model_id="GLM-5.2",
        manifest_sha256="0" * 64,
        asset_identity="example-asset",
        encoder_identity="example-encoder",
        profile_json="{}",
        settings_json="{}",
        algorithm_version="example-algorithm",
    )
    sample = SampleManifest3(
        parent_scope=AnalysisScope(
            source=identity,
            appid=selection.appid,
            window=None,
            request_count=decision.parent_count,
            request_keys_digest=decision.parent_keys_digest,
            baseline_origin="original_run_window",
        ),
        source_selection=selection,
        decision=decision,
        files=tuple(
            SnapshotFile3(
                path=f"{w.role}/{m.key.source_record_index}.{ext}",
                size=size,
                sha256="0" * 64,
            )
            for w in decision.windows
            for m in w.members
            for ext, size in (("raw", 2), ("view", 1024), ("tokens", 0))
        ),
        verification_bytes=1234,
        selected_raw_bytes=4,
        selected_token_bytes=0,
    )
    return {
        "wire.json": document(
            {
                name: wire_schema(model)
                for name, model in (
                    ("request", PreparationRequest3),
                    ("receipt", PreparationReceipt3),
                    ("sample", SampleManifest3),
                )
            }
        ),
        "examples.json": document(
            {
                "request": to_wire(request),
                "queued": to_wire(receipt),
                "sample": to_wire(sample),
                "note": "Synthetic schema examples; no real source or validation result.",
            }
        ),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1] / "docs/contracts/diagnostics-sampling-3"
    files = export_values()
    files["manifest.json"] = document(
        {
            "version": "diagnostics-sampling-3",
            "files": {name: hashlib.sha256(data).hexdigest() for name, data in files.items()},
        }
    )
    if args.check:
        for name, data in files.items():
            if (root / name).read_bytes() != data:
                raise SystemExit(f"Sampling contract differs: {name}")
        print("Sampling contract matches models and examples")
    else:
        root.mkdir(parents=True, exist_ok=True)
        for name, data in files.items():
            (root / name).write_bytes(data)


if __name__ == "__main__":
    main()
