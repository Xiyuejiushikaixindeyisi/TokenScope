# B002 实际验证记录

2026-10-27 / 本机 WSL / CPython 3.11.16 / 代码 **0.1.0.dev2**。三模型使用 [实际资产锁](../../../../../../../env/encoding-assets.lock.json)，源/测试身份见 [manifest](../../../../../../../artifacts/validation/monitoring/B002/source-manifest.json)。全部输入为合成测试请求，不是用户生产 CSV。

最终全套 **94 passed，1 条既有 TestClient 弃用 warning**；mypy 检查 17 个源码文件，ruff/format 均通过。B001 66 例包含在本次回归内，新增资产/分片 9 例、编码集成 19 例。

| 检查 | 退出码 | 证据 |
| --- | --- | --- |
| pytest-final | 0 | [日志](../../../../../../../artifacts/validation/monitoring/B002/20261027T025329Z-pytest-final.log) |
| ruff-final | 0 | [日志](../../../../../../../artifacts/validation/monitoring/B002/20261027T025329Z-ruff-final.log) |
| format-final | 0 | [日志](../../../../../../../artifacts/validation/monitoring/B002/20261027T025329Z-format-final.log) |
| mypy-final | 0 | [日志](../../../../../../../artifacts/validation/monitoring/B002/20261027T025329Z-mypy-final.log) |

[机器可读报告](../../../../../../../artifacts/validation/monitoring/B002/20261027T025329Z-final-checks.json)。复现：`.venv/bin/pytest -q`；`.venv/bin/ruff check src tests`；`.venv/bin/ruff format --check src tests`；`.venv/bin/mypy`。

## 验证内容

- 固定 Qwen/GLM 真实 tokenizer/template 与独立 AutoTokenizer 参考 IDs 对齐，覆盖文本、多轮、工具、中文/emoji/特殊 Token 字面量；默认模板与明确关闭思考的区别有测试。
- DeepSeek 显式模式通过 Recipe 官方绑定直接 encode 与本批分段批量编码对齐；特殊 Token 在用户正文内按普通字面文本编码。**测试指定 True/False 不等于选定生产默认**。
- 单条/批量、1/4 线程结果与编码身份一致；长文本无隐式截断；详细重编码 IDs 摘要一致，错误摘要拒绝；所有对外区间为 UTF-8 byte 左闭右开。
- J 按完整 JSON 普通文本计量；不把 added vocabulary 字面量当控制符。轻量源字段 reference 和详细 prompt offsets 有边界说明，缺失精确原字段归因标 partial/unknown。
- 资产缺失/越界/重复/摘要改变拒绝；uint32 LE 分片、旋转、超大单条、截断/损坏及防覆盖。
- 单个编码坏行不吞掉同批其他请求；DeepSeek 缺省未确认时明确 ENCODING_DEFAULT_UNRESOLVED，显式请求仍能编码。

## 失败与修复（保留日志）

1. [初始机制测试](../../../../../../../artifacts/validation/monitoring/B002/mechanism-tests-initial.log) 9 passed；[初轮静态](../../../../../../../artifacts/validation/monitoring/B002/ruff-initial.log) 28 格式项；[mypy](../../../../../../../artifacts/validation/monitoring/B002/mypy-initial.log) 当时缺尚未安装依赖。
2. uv 的 numpy 下载重试后完成（16m21s preparation，非运行性能）；额外下载尝试在主安装成功后中断，没有代替锁版本。[安装日志](../../../../../../../artifacts/validation/monitoring/B002/environment-setup.log)。
3. [首轮真实编码](../../../../../../../artifacts/validation/monitoring/B002/real-encoding-initial.log)：11 failed / 2 passed / 4 errors，缺 Jinja2 与 Qwen 重复 chat_template 参数；[复测1](../../../../../../../artifacts/validation/monitoring/B002/real-encoding-retest-1.log)：3 failed / 10 passed / 4 errors，Qwen AddedToken 转换与参考返回类型；[复测2](../../../../../../../artifacts/validation/monitoring/B002/real-encoding-retest-2.log)：17 passed。问题及修复见 ISSUES。
4. 源码复核修正区间单位为契约的 UTF-8 byte，补显式思考/缺省 pending 和来源字段回归。最终 94 项统一重跑及静态检查全部通过。

未验证：部署词表相同、华为 GF 0.30.0rc2 默认模式、现场 Transformers 5.5.4 的等价性、CSV 全流水线、目标机容量/两小时性能。因此本批仍 verifying，不以测试子集通过替代整体关闭。

## 落盘收口复测

新增 stage 两例。首次95通过/1失败（SQLite database locked），切换WAL后96通过；ruff/format/mypy退出码均0。报告：`artifacts/validation/monitoring/B002/20261027T031422Z-report.json`。失败历史保留。源码清单和快照已刷新。
