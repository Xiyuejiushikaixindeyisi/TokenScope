# Token T2–T4 独立复审实际报告

2026-11-01（Asia/Shanghai）。审查会话：`01a1800e-80b4-7400-a78b-a84f5b6e888d`，环境 `CODEX_THREAD_ID` 实际核实。角色为独立审查及授权后交付。本次按用户经 Token 维护方转交的启动授权执行；不承担业务源码修复、生产策略批准或用户视觉签字。

## 结论

**通过本次 Token 私有 T2–T4 后端及其与 arpc-local-4 组合的独立复审，保留下列明确能力边界。未发现需要归口修复的阻断缺陷。** 本结论基于实际源码检查、新运行的 164 项本线测试、12 项独立边界探针及 ART4 封存数据副本的只读验证，不以此前公共层报告替代 Token 私有验证。

本轮没有修改业务源码、测试目录或契约，没有构建、打包或部署；没有提交当前分析工作树。监控V2旧归档提交的核对属于此前独立任务，不是本报告候选的 Git 发布。异常分析 Git 收口由用户指定的总负责会话统一处理。

[机器结果与逐文件身份](INDEPENDENT_REVIEW_RESULT_20261101.json) · [原始候选](INDEPENDENT_REVIEW_IDENTITY_20261101.json) · [交接输入](INDEPENDENT_REVIEW_HANDOFF.md) · [公共层实际复审](../prefix-analysis/INDEPENDENT_REVIEW_RESULT_20261101.md)

## 实际候选与漂移

- 当前工作树私有候选 `token-review-20261101-1`，17 个源码文件及 19 个测试/辅助文件全部与交接摘要一致。私有整体摘要 `31fd67c2e7432baf24daf6ed8b43cf024a4ebc22824f689ec8f833e56ae0b564`。本报告仍使用交接定义的两个 map 紧凑排序 JSON 摘要口径。
- HEAD 为 `5d824b506d9e055bcf397c3846dafc450fcf02e5`，不是此候选：Token 源码和测试仍未跟踪。没有仅凭 main 或空 diff 判断候选身份。
- 相对交接 88 个身份条目，发现 4 项漂移：公共 `recommendation_evidence.py`、`recommendation_publication.py`、`recommendations.py` 已更新为 arpc-local-4；前端 `ACCEPTANCE_UI04.md` 补了 RV1 新入口。公共漂移和相应完整 7 文件修复集均匹配[维护方修复身份](../prefix-analysis/INDEPENDENT_REVIEW_FIX_IDENTITY_20261101.json)，不是未经解释的 Token 改动。
- 复审起止的 65 个 Token/公共源码和 Token 测试文件完全一致。候选中的源码、公共/API依赖及 14 个契约文件也复核未在测试期间漂移；最终额外固定公共修复集、Token 配置 Schema 与 S0 文档，共 89 个文件身份见机器结果。旧 manifest 不改写。
- WSL Python 3.11.16，pytest 9.1.1、pydantic 2.14.1、fastapi 0.162.0、tokenizers 0.23.2、transformers 5.21.0、mypy 1.20.2、ruff 0.17.3。5 个依赖/来源锁文件及三模型 8 个 Tokenizer/Template 资产文件实际重新计算摘要并匹配；没有安装或升级依赖。模型 revision 与逐文件摘要见 evidence 下 `environment.json`。

## 源码与行为矩阵

| 范围 | 独立核查与实际结果 |
| --- | --- |
| 当前范围与历史兼容 | `CurrentTokenContentPlugin` 只接受 T2–T4，新链路不能产生工具定义精简；旧插件/T1读取兼容由本线集成测试覆盖，未把历史 handler 的存在当作新功能开放。 |
| 策略和授权 | `auto_config`、`auto_duplicates`、`auto_proposals` 对版本、handler、严格布尔/整数、重复 key、scope/appid、工具摘要及 basis 快照进行校验；缺依据/映射仅 advice，不给可执行目标。构造 verified 配置不等于生产批准。 |
| T2 投影/截取 | 明确内嵌路径与结构级别，保持行序、不吞掉混合数组中的非对象行；范围有界。独立探针从提案到公共 apply 验证内嵌 `-0`、`1e+02` 词法仍保留；混合数组导致整次失败，不输出部分方案。 |
| T3 重复依据 | 完整载荷 hash 后仍作精确内容比较，排除子串/语义近似和重叠单位；Observation 足以支持，不强制先制造 Finding。授权选择必须重新从当前 raw 推导，旧 raw hash、目标、basis、参数不能复用篡改。 |
| T3 引用 | 只允许支持的顶层参数引用；调用所用工具摘要、必需字段和引用参数 Schema 再校验。独立探针重新绑定变更后的工具身份，仍确认必需原字段或受约束引用字段会阻止修改；没有把“身份不匹配”误作 Schema 验证的唯一证据。 |
| T3 删除 | 完整普通 user/assistant 消息及明确角色授权；不删除 tool 或带调用字段的消息。独立相邻双副本删除只删授权副本，保留原工具结果、近似文本及最后指令；公共 apply 原文 guard 后按倒序删除，原始 RequestView 不变。 |
| T4 保留 | 同 appid、同工具摘要、源顺序最后 K；交错其他工具不参加本策略计数，K=0 与无配置不同，K超大无目标。另独立验证显式 `text_part` 按文本片段计数且只替换旧片段，不把它冒称整结果容器保留。 |
| 原子修改 | `transformations` 与公共 `apply_mutations` 的 RequestKey/raw/字段或外层字符串保护、重叠冲突拒绝、数值词法保护和协议校验一致；失败不回写原请求。 |
| 真实回放与计数 | 新跑本线集成覆盖三模型真实编码、原 appid 完整 scope 回放、noop N=0、缺参数/授权未知收益、不同依据/共享执行、零负收益及 P下降而C上升。N按完整 raw 实际变化，M是原scope；四个独立方案不能收益相加。 |
| 取消、预算、恢复 | 本线源码和新运行的资源、提案、恢复测试覆盖单元/比较/候选等边界、取消与新重试独立、源摘要变化阻断、原封存报告不被覆盖；公共发布/default 的独立全范围结论另见 arpc-local-4 报告，不把本轮当作又跑了一次公共全量。 |
| 只读展示接口 | ART4原目录复制后读取四建议八例、分页、错误参数、错误实例；禁止 submit/process_next/analyze/propose/prepare/encode，仍与原保存响应完全一致。原35文件 hash不变；未启动/终止其他会话服务。 |

## 实际运行记录

工作目录 `/home/zhangxiyue/TokenScope`；全部新证据位于 `artifacts/reviews/token-independent-20261101/`。pytest 全量使用此前不存在的独立 `pytest-main`，不清空任何旧验证目录。

| 实际执行 | 结果 | 证据 |
| --- | --- | --- |
| `.venv/bin/python -m pytest tests/unit/token_content tests/integration/token_content --basetemp=artifacts/reviews/token-independent-20261101/pytest-main -q` | 164 passed，86.05s，退出0 | `checks.json`、`check-0.log` |
| `.venv/bin/mypy src/tokenscope/token_content` | 17文件，退出0 | `check-1.log` |
| `.venv/bin/ruff check src/tokenscope/token_content tests/unit/token_content tests/integration/token_content` | 退出0 | `check-2.log` |
| `PYTHONPATH=tests:tests/unit/token_content .venv/bin/python -m pytest artifacts/reviews/token-independent-20261101/test_review_edges.py -q` | 最终12 passed，0.26s，退出0 | `test_review_edges.py`、`edge-complete.log` |
| `.venv/bin/python artifacts/reviews/token-independent-20261101/art4.py` | 14个不同GET URL响应核验通过，另核对capabilities及错误实例409；4建议/8例；35原文件未变；退出0 | `art4.log`、`art4-readonly.json`、`art4-responses.json` |

164项本线测试与12项新增探针分别列出，不加上公共报告的146/6等数字冒充本轮执行量。唯一全量 warning 是已知 Starlette/httpx TestClient 弃用提示，没有为消警告更换依赖。

独立探针过程原样保留：首轮8通过/1失败，原因是审查构造的 `tool_calls: []` 被合法性校验拒绝；第二轮9通过/1失败，原因是 `tool_calls: null` 触发保守的局部提取不完整。随后把合法调用消息保护、无效空数组拒绝、null保守拒绝分开表达，11项通过，再补 text_part 项形成最终12项。没有删业务断言、改源码或覆盖失败日志换通过；各版探针及日志摘要见机器结果。

## 问题、未决事项与结论边界

没有确认的阻断缺陷，本轮无业务修复或待修复编号。以下是保留限制，不应被“通过”抹去：

1. `tool_calls: null` 当前会使 Token 提取为 partial，自动修改拒绝，尽管输入解析允许该空值。这是保守的支持边界，会减少可处理覆盖面，不会误删内容或伪造完整收益。已用独立探针记录；如生产数据大量采用显式null，应由Token维护方按数据事实决定是否另行扩展，不能靠本次测试假设已支持。
2. 测试请求、业务策略与引用地址均为构造输入。三模型 Tokenizer/Template 和离线程序链路是真实运行；远程引用解析、业务输出质量、生产删除许可、线上收益、TTFT/SLA、费用及华为现场均未验证。默认空 recipe 不得偷偷换成测试策略。
3. 本报告不代替异常分析前端用户功能/视觉验收，不评定本次之后的前端改动；不代表已具备交付批准。公共 arpc-local-4 的 PCR-01/02 已在其报告修复闭环，本轮没有再次发现同类 Token 阻断。
4. 当前候选是共享工作树，等待总负责会话统一收集稳定清单及获授权的 Git 收口；将来若私有/公共依赖/锁文件/契约/模型身份变化，应按变更影响重新核验，不能直接沿用本结论。

[ART4原始说明](FRONTEND_READABILITY_ART4.md)和原始state保持原位；本次只读副本为 evidence 下 `art4-copy`。本次无部署变更，因此无运行态回退操作。后续统一交付仍须等待异常分析前后端验收及用户明确安排。
