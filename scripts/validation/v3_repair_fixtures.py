"""Deterministic synthetic Huawei-shaped requests; never imports onsite raw data."""

import argparse
import csv
import hashlib
import json
from pathlib import Path

from tokenscope.ingestion.csv_reader import REQUIRED_COLUMNS

GROUPS = (
    ("BUS01", "S00000000000000000000000000000773", "DeepSeek-V4-Flash-0731", 27469, 24156, 44),
    ("BUS02", "S010320", "DeepSeek-V4-Flash-0731", 23268, 16063, 40),
    ("BUS03", "com.huawei.mbs.ilegal.ioc", "DeepSeek-V4-Flash-0731", 37222, 22348, 40),
    ("BUS04", "com.huawei.newalliance", "DeepSeek-V4-Flash-0731", 18892, 14645, 40),
    ("BUS05", "com.huawei.aidp_dg06", "Qwen3.6-27B", 17982, 14883, 40),
)
FILL = "合成验证规则：准确阅读输入，保持工具参数类型，不传播个人信息。 "


def fill(length):
    assert length >= 0
    return (FILL * (length // len(FILL) + 1))[:length]


def make_request(group, index):
    name, _, model, length, offset, tool_count = group
    if index >= 12:
        # BUS03's independent short system path family, no clock or env.
        length = 4567 if index % 2 == 0 else 4572
        tail = "/workspace/USER0001/" + ("alpha" if index % 2 == 0 else "bravo-long")
        system = fill(4567 - len("/workspace/USER0001/alpha")) + tail
        tool_count = 25
    else:
        prefix = "SYNTHETIC_VALIDATION_ONLY " + name + "\n"
        prefix += fill(1045 - len(prefix)) + "model=" + model + "\n"
        prefix += (
            fill(1400 - len(prefix))
            + "<env>date=Tue Oct 20 2026; workspace=/workspace/USER0001/stable</env>\n"
        )
        prefix += fill(offset - len(prefix))
        second = index if index < 4 else 4 if index < 6 else index
        clock = (
            "<session_clock> ## 当前时间（本机时区：Asia/Shanghai） "
            f"2026/10/20 09:00:{second:02d} </session_clock>"
        )
        if index >= 8:
            clock = "无动态时间字段，以下为稳定合成内容。"
        system = prefix + clock + fill(length - len(prefix) - len(clock))
    assert len(system) == length
    tools = []
    for n in range(tool_count):
        description = f"合成工具 {n}，读取指定对象。"
        if index in (8, 9) and name != "BUS04" and n == 0:
            description += " workspace=/workspace/USER0001/" + ("alpha" if index == 8 else "bravo")
        tools.append(
            {
                "type": "function",
                "function": {
                    "name": f"synthetic_tool_{n:02d}",
                    "description": description,
                    "parameters": {
                        "type": "object",
                        "properties": {"query": {"type": "string"}},
                        "required": ["query"],
                    },
                },
            }
        )
    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": "请读取合成对象。"},
    ]
    if index in (6, 7):
        for turn in range(index - 5):
            ident = f"call_{turn}"
            messages.extend(
                [
                    {
                        "role": "assistant",
                        "content": "",
                        "tool_calls": [
                            {
                                "id": ident,
                                "type": "function",
                                "function": {
                                    "name": "synthetic_tool_00",
                                    "arguments": '{"query":"synthetic"}',
                                },
                            }
                        ],
                    },
                    {"role": "tool", "tool_call_id": ident, "content": '{"ok":true}'},
                    {"role": "assistant", "content": "已读取。"},
                    {"role": "user", "content": f"继续第{turn}轮。"},
                ]
            )
    return {"messages": messages, "tools": tools, "tokenscope_synthetic_fixture": "huawei-shape-1"}


def generate(output):
    output = Path(output)
    output.mkdir(parents=True, exist_ok=False)
    manifest = {"version": "synthetic-huawei-shape-1", "synthetic": True, "groups": []}
    for group in GROUPS:
        name, appid, model, *_ = group
        count = 16 if name == "BUS03" else 12
        path = output / (name + ".csv")
        entries = []
        with path.open("x", encoding="utf-8", newline="") as stream:
            writer = csv.writer(stream)
            writer.writerow(REQUIRED_COLUMNS)
            for index in range(count):
                body = make_request(group, index)
                raw = json.dumps(body, ensure_ascii=False, separators=(",", ":"))
                system = body["messages"][0]["content"]
                start = system.find("<session_clock>")
                end = (
                    system.find("</session_clock>") + len("</session_clock>")
                    if start >= 0
                    else None
                )
                writer.writerow(
                    [
                        f"synthetic-{name}-{index + 1:04d}",
                        appid,
                        f"2026-11-11T00:00:{index:02d}Z",
                        12,
                        raw,
                    ]
                )
                entries.append(
                    {
                        "index": index + 1,
                        "sha256": hashlib.sha256(raw.encode()).hexdigest(),
                        "bytes": len(raw.encode()),
                        "system_chars": len(system),
                        "tools": len(body["tools"]),
                        "clock_range": [start, end] if start >= 0 else None,
                    }
                )
        manifest["groups"].append(
            {
                "group": name,
                "appid": appid,
                "model": model,
                "file": path.name,
                "count": count,
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                "requests": entries,
            }
        )
    (output / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2))
    return manifest


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("output", type=Path)
    generate(parser.parse_args().output)
