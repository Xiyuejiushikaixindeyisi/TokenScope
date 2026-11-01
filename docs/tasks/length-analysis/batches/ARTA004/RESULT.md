# ARTA004 — 只读接入、历史兼容及最终验证

2026-10-31，本线实现与消费者验收闭环；前端接收/正式视觉验收单独跟踪。身份 arta-local-1（工作树快照，不是发布或Git提交）。

## 实际验证

- 命令：`.venv/bin/python -m pytest tests/unit/token_content tests/integration/token_content --basetemp=artifacts/validation/arta-final-20261031-01 -q`。
- **162 passed / 64.33s，另1项边界增量 passed / 5.59s，共163项通过**：原112项 + 新增46项unit + 4项实际自动集成。一个既有 Starlette/httpx 弃用warning，无失败。17个Token源码mypy及本线ruff通过。
- 当前真实应用 create_app 已消费公共 bootstrap 的 CurrentTokenContentPlugin/token-content-2 和 TokenProposalAdapter/token-content-recipes-1。未修改公共文件，装配由公共会话完成。
- 实际 GET capabilities/推荐分页/单项/局部例子/summary；实例错配409。GET过程中禁止调用分析和编码仍可读取，前端只读成立。
- 旧 token-content-1 报告仍读取T1；新推荐summary标 not_computed，不回填/重算历史。新任务不生成T1。
- 预算耗尽任务partial、blocked推荐N=null，discovery仍选此前ready；terminal可读。单请求取消/预算在本线unit验证；公共完整任务恢复/其他资源矩阵由其审查另行覆盖。
- 局部例子最多3条，位置/owner/报告引用正确。示例JSON为真实HTTP返回，数字保留wire十进制字符串。

## 实际构造结果

GLM构造scope M=2：T2 P=1322→1318、N=2；noop 1322→1322、N=0；T4 1322→1318、N=2；负收益1322→1916仍展示；缺依据不填0收益。T3三模型引用与删除两方案分别评估，通过且N=2。

输入、策略、引用地址都是明确构造配置，不能推导生产收益/质量等价。没有Agent重跑、参数错配研究实施、正式前端修改、打包或部署。

[实际HTTP样例](ACTUAL_API_EXAMPLES.json) · [源码/样例摘要](CODE_IDENTITY.json) · [适配器交接](../../AUTO_ADAPTER_HANDOFF.md)。本地原始测试产物位于 artifacts/validation/arta-final-20261031-01；产物不进入Git。

## 追加 P下降/C上升边界验收

同一固定GLM配置，构造输入寻找有效全块/MTP边界，未修改模型设置。P=1026→1022，H=384→256，C=642→766，N/M=2/2，仍标 token_evaluated。单独命令 `pytest tests/integration/token_content/test_auto_recommendations.py::test_less_input_can_increase_full_block_compute --basetemp=artifacts/validation/arta-boundary-20261031-02 -q`：1 passed/5.59s。初次fixture错误选到整块边界且未考虑末token/MTP保留，修正为实际策略有效边界后通过；不是生产算法改动。最后仅补测试，未再修改业务源码，因此不重复整套回归。

## 前端接收回执

2026-10-31，异常分析前端 session `01a19111-344a-75c1-84e0-14db8be08f4f` 已实际回执：读取交接/结果/实际HTTP样例，CODE_IDENTITY 23/23摘要匹配。接收依据见[AR-03前端记录](../../../viewer/analysis/REWORK_COORDINATION_AR03.md)。这是交接接收及身份核对，不是正式界面/端到端验收；前端继续等待公共ARPC005/006最终冻结。未因此重新测试、修改源码、打包或部署。
