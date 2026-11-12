import importlib.util
from pathlib import Path


def test_deterministic_long_fixtures_and_exact_clock_ranges(tmp_path):
    spec = importlib.util.spec_from_file_location(
        "fixture", Path("scripts/validation/v3_repair_fixtures.py")
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    a, b = module.generate(tmp_path / "a"), module.generate(tmp_path / "b")
    assert a == b
    assert sum(g["count"] for g in a["groups"]) == 64
    for group, entry in zip(module.GROUPS, a["groups"], strict=True):
        for i, row in enumerate(entry["requests"]):
            body = module.make_request(group, i)
            system = body["messages"][0]["content"]
            if i < 8:
                start, end = row["clock_range"]
                assert start == group[4]
                assert system[start:end].startswith("<session_clock>")
                assert system[start:end].endswith("</session_clock>")
            else:
                assert row["clock_range"] is None
            assert len(body["tools"]) == (25 if i >= 12 else group[5])
            assert all(t["function"]["parameters"]["type"] == "object" for t in body["tools"])
    try:
        module.generate(tmp_path / "a")
        raise AssertionError("Historical output overwritten")
    except FileExistsError:
        pass
