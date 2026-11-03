"""Bounded synthetic profile; run directly, never starts services."""

import cProfile
import hashlib
import json
import pstats
import subprocess
import sys
import time
import tracemalloc
from pathlib import Path

from test_auto_proposals import fixture, propose
from test_extraction import control, view

from tokenscope.analysis_common.plugins import EvidenceCapabilities, PluginSelection
from tokenscope.analysis_common.storage import ResultWriter
from tokenscope.token_content.auto_proposals import TokenProposalAdapter
from tokenscope.token_content.current_plugin import CurrentTokenContentPlugin


def bodies():
    payload = json.dumps([{f"k{k}": "value" * 8 for k in range(8)} for _ in range(8)])
    deep = {"leaf": -0.0}
    for _ in range(12):
        deep = {"child": deep}
    return {
        "messages": {"messages": [{"role": "user", "content": "necessary quote"}] * 8},
        "schema": {
            "tools": [
                {
                    "type": "function",
                    "function": {
                        "name": "f",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                f"p{i}": {"type": "string", "description": "required " * 8}
                                for i in range(64)
                            },
                        },
                    },
                }
            ],
            "messages": [{"role": "user", "content": "task"}],
        },
        "wide": {
            "messages": [
                {"role": "tool", "content": payload},
                {"role": "user", "content": payload},
                {"role": "user", "content": payload + "!"},
            ]
        },
        "deep": {"messages": [{"role": "tool", "content": json.dumps(deep)}]},
        "chain": {"messages": [{"role": "tool", "content": f"result-{i}"} for i in range(24)]},
    }


def main():
    out = Path(sys.argv[1])
    out.mkdir(parents=True, exist_ok=False)
    if "--baseline" in sys.argv:
        import tokenscope.token_content.auto_duplicates as ad
        import tokenscope.token_content.auto_proposals as ap
        import tokenscope.token_content.extraction as ex
        import tokenscope.token_content.measurements as me
        import tokenscope.token_content.plugin as pl

        for module, name in [(me, "measurements"), (ex, "extraction")]:
            source = subprocess.check_output(
                [
                    "git",
                    "show",
                    "7cbe28621f4e46083bf47f9aa14b011b3cb250c4:src/tokenscope/token_content/"
                    + name
                    + ".py",
                ]
            )
            exec(compile(source, module.__file__, "exec"), module.__dict__)
        pl.extract = ap.extract = ad.extract = ex.extract
        fixture.__globals__["extract"] = ex.extract
    results = {}
    plugin = CurrentTokenContentPlugin()
    for name, body in bodies().items():
        request = view(body)

        def analyze(request=request):
            ctl = control(max_units=3000)
            fragment = plugin.analyze_request(
                request,
                PluginSelection(rule_ids=("T2", "T3", "T4"), budget=ctl.budget),
                EvidenceCapabilities(),
                ctl,
            )
            return fragment, ctl

        results[name] = run_phase(out, name, analyze)
        fragment, ctl = analyze()
        raw = fragment.model_dump_json()
        results[name].update(
            raw_bytes=len(request.raw_body.encode()),
            fragment_bytes=len(raw.encode()),
            fragment_sha256=hashlib.sha256(raw.encode()).hexdigest(),
            units=len(fragment.units),
            consumed=ctl.consumed,
            encoding_calls=ctl.consumed.get("max_encoding_calls", 0),
            coverage=fragment.coverage.model_dump(),
            rules=[r.model_dump() for r in fragment.rule_results],
            budget=ctl.budget.model_dump(),
        )
        (out / (name + "-fragment.json")).write_text(raw)
        results[name + "_serialize"] = run_phase(
            out, name + "_serialize", lambda fragment=fragment: fragment.model_dump_json()
        )
        write_number = 0

        def write(name=name, fragment=fragment):
            nonlocal write_number
            dest = out / f"{name}-sqlite-{write_number}"
            dest.mkdir()
            write_number += 1
            writer = ResultWriter(dest)
            writer.add("fragment", "0", fragment.model_dump(mode="json"))
            writer.close()

        results[name + "_write"] = run_phase(out, name + "_write", write)
    request, fragment, bundle = fixture()
    adapter = TokenProposalAdapter()
    results["proposal"] = run_phase(out, "proposal", lambda: propose(request, fragment, bundle))
    proposal = propose(request, fragment, bundle)[0]
    results["prepare"] = run_phase(
        out, "prepare", lambda: adapter.prepare_proposal(request, proposal, bundle.recipes[0].basis)
    )
    (out / "results.json").write_text(json.dumps(results, indent=2))
    print(json.dumps({k: v["wall_ns"] for k, v in results.items()}))


def run_phase(out, name, fn):
    wall, cpu = [], []
    for _ in range(5):
        start = time.perf_counter_ns()
        process = time.process_time_ns()
        fn()
        wall.append(time.perf_counter_ns() - start)
        cpu.append(time.process_time_ns() - process)
    tracemalloc.start()
    fn()
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    profiler = cProfile.Profile()
    profiler.enable()
    fn()
    profiler.disable()
    profiler.dump_stats(str(out / (name + ".prof")))
    stats = pstats.Stats(profiler)
    calls = [
        {
            "file": f,
            "line": line,
            "function": fun,
            "primitive": value[0],
            "calls": value[1],
            "self_seconds": value[2],
            "inclusive_seconds": value[3],
        }
        for (f, line, fun), value in stats.stats.items()
        if any(x in f for x in ("token_content", "json_values"))
    ]
    byte_counters = {}

    def observe(frame, event, arg):
        if "token_content" not in frame.f_code.co_filename:
            return
        function = frame.f_code.co_name
        if event == "return" and function == "dumps" and isinstance(arg, str):
            byte_counters["dumps_return_utf8_bytes_including_recursive"] = byte_counters.get(
                "dumps_return_utf8_bytes_including_recursive", 0
            ) + len(arg.encode())
        if event == "call" and function in ("loads", "digest"):
            value = frame.f_locals.get("raw" if function == "loads" else "text")
            if isinstance(value, str):
                key = function + "_input_utf8_bytes"
                byte_counters[key] = byte_counters.get(key, 0) + len(value.encode())

    sys.setprofile(observe)
    try:
        fn()
    finally:
        sys.setprofile(None)
    return {
        "instrumented_bytes_separate_from_timing": byte_counters,
        "wall_ns": wall,
        "cpu_ns": cpu,
        "peak_tracemalloc_bytes": peak,
        "profile_calls": calls,
        "profile_separate_from_timing": True,
    }


if __name__ == "__main__":
    main()
