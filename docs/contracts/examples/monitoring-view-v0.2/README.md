# v0.2完整回执与导出协议夹具

**synthetic / protocol_fixture / 非服务输出**。对应[契约v0.2第7–8节](../../MONITORING_VIEW_V1_DRAFT.md)，用于前端F001协议核对和后续自动化断言；不能作为A/J/R业务验收。正常导出4条请求，含重复hash、Unicode、双引号、逗号、字段内LF/CR及公式前缀。

- [receipts.json](receipts.json)：6种完整状态响应、404未确认、跨实例409。所有时间/ID人工构造，不指向实际任务。
- [normal.ndjson](normal.ndjson) / [normal.csv](normal.csv)：同一组4条事实；NDJSON不改hash，CSV按声明加公式安全前缀。
- [empty.ndjson](empty.ndjson) / [empty.csv](empty.csv)：筛选空集；前者metadata+summary，后者只有表头，预计数0。
- [manifest.json](manifest.json)：响应头、文件SHA/字节、NDJSON请求字节摘要、CSV解析记录数、UTF8切点和故障变换建议。
- [facts.synthetic.json](facts.synthetic.json)：人工已有事实的来源夹具；metadata.input_sha256对应此文件而非真实摄入CSV，settings_sha256也是示意身份。未运行Tokenizer或DES。

normal的NDJSON request行摘要为
`e836c082faadda85bbe9c6bba3895956a8c6cbaffb3ccc4f254046c72d6fad26`。
normal.csv解析为**4条数据记录**，物理LF为7个，不能按换行计数。CSV文件SHA用于验证本夹具身份，不代表CSV客户端提供内容哈希保证。

独立复核（在本目录，Python标准库；不导入TokenScope）：

```python
import csv, hashlib, io, json
from pathlib import Path

manifest = json.loads(Path("manifest.json").read_text())
for case in manifest["fixtures"]:
    raw = Path(case["ndjson"]["path"]).read_bytes()
    lines = raw.splitlines(keepends=True)
    assert all(x.endswith(b"\n") and not x.endswith(b"\r\n") for x in lines)
    records = [json.loads(x) for x in lines]
    assert records[0]["type"] == "metadata"
    assert records[-1]["type"] == "summary"
    assert all(x["type"] == "request" for x in records[1:-1])
    actual = hashlib.sha256(b"".join(lines[1:-1])).hexdigest()
    assert actual == records[-1]["request_lines_sha256"]
    assert actual == case["ndjson"]["request_lines_sha256"]
    assert int(records[0]["expected_rows"]) == len(lines) - 2
    assert int(records[-1]["actual_rows"]) == len(lines) - 2
    raw_csv = Path(case["csv"]["path"]).read_bytes()
    parsed = list(csv.reader(io.StringIO(raw_csv.decode("utf-8"), newline=""), strict=True))
    assert len(parsed) - 1 == case["csv"]["parsed_data_records"]
    assert all(len(row) == len(parsed[0]) for row in parsed)
```

上述简短脚本只校验本目录已知良好小夹具；生产浏览器必须执行契约规定的所有身份/头/EOF/增量资源检查，不能用它代替完整校验器。当前没有完整catalog/snapshot DTO与生成OpenAPI，F001的全量输入仍待S0固定；本目录的“完整”仅指回执和两种导出各自协议。

≥256MiB、1MiB单记录及16MiB备用边界的生成和真实浏览器测试仍为实施计划，本轮未执行或生成大文件。
