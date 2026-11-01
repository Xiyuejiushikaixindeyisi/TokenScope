# Token 异常后端独立复审交接

2026-11-01 最新用户已明确授权启动、按归口修复及复测。完整prompt已通过工具实际发送给审查session `01a1800e-80b4-7400-a78b-a84f5b6e888d`，工具成功返回同一threadId；当前状态是已发起，待审查方实际报告，不能称已通过。下方“仅准备/未发送”是原交接阶段记录，已被本条覆盖；不打包部署或Git发布。公共依赖已进展至arpc-local-4及其独立复审报告，审查应登记相对快照的真实漂移。

2026-11-01。候选 `token-review-20261101-1`，提供方 session `01a18fcd-0464-7cf1-b435-4f394bd33e66`。本文件是复审输入，**不是独立复审结论、用户视觉批准或发布授权**。本轮只整理交接及核对身份，未运行新的业务测试。

[可直接复制的完整 prompt](../../../prompts/sessions/TOKEN_CONTENT_BACKEND_INDEPENDENT_REVIEW.md) · [当前候选身份](INDEPENDENT_REVIEW_IDENTITY_20261101.json)

## 1. 范围、身份与维护边界

- 当前职责仅 T2–T4：T2 工具返回内容投影/截取；T3 完整重复载荷引用或授权普通消息删除；T4 保留与替换历史工具结果。新任务不输出 T1，历史 token-content-1/T1 报告仍可读取。
- 工具定义属于低命中现有一致性/漂移职责，不新增长度精简；Token 只读工具定义用于身份、参数schema及引用协议约束。
- Token 唯一维护 `src/tokenscope/token_content`、`tests/unit/token_content`、`tests/integration/token_content` 及本线文档。公共维护分析任务/归组/计量与回放封装/证据/状态发布/API；前端维护展示和只读交互。参数错配仍是独立研究，自进化Agent未启动。
- 当前私有源码 17 个 Python 文件、测试/基准辅助 19 个 Python 文件，逐文件 SHA256 见候选身份。整体私有源码+测试摘要为 `31fd67c2e7432baf24daf6ed8b43cf024a4ebc22824f689ec8f833e56ae0b564`，计算方式是身份文件中两个map以sort_keys、紧凑JSON序列化后SHA256。
- 观察到的分支 `main`，HEAD=`5d824b506d9e055bcf397c3846dafc450fcf02e5`。**Token源码和测试目录仍为未跟踪文件，HEAD不包含该候选**；独立复审必须按工作树文件摘要取证，不用git diff为空证明没有改动，不遗漏untracked文件。
- 身份文件另外登记33个公共/API依赖、14个契约JSON和前端交接输入，只作集成依赖观察，不将它们登记为Token维护范围。
- 本轮核对 arta-local-1 23/23、ART4 7/7、公共AR-L5 files 5/5一致。旧身份/封存报告未覆盖。前端验收文档和结果清单的当前字节也已记录；这不代替前端独立验收。

## 2. 对齐的公共层与前端入口

| 入口 | 使用方式 |
| --- | --- |
| [公共机器契约](../../contracts/analysis-recommendations-1/README.md) | analysis-recommendations-1、token-auto-proposals-1；internal/wire/public-views及其manifest，以实际机器契约为准 |
| [Token适配器交接](AUTO_ADAPTER_HANDOFF.md)与[私有配置Schema](AUTO_RECIPE_SCHEMA.json) | selector/generator DSL由Token维护；公共JSON外壳不能替代validate_bundle跨字段/依据校验 |
| [公共AR-L3完整交接](../prefix-analysis/FRONTEND_REWORK_IMPLEMENTATION_HANDOFF_ARL3.md) | 推荐/差异/局部证据/只读GET、完整性、默认报告和发布机制 |
| [公共AR-L4局部证据修复](../prefix-analysis/FRONTEND_READABILITY_HANDOFF_ARL4.md) | 内嵌与删除位置、缺依据建议的原始证据等后续修复，不以旧样例代表新定位行为 |
| [公共AR-L5文案修复](../prefix-analysis/FRONTEND_COPY_HANDOFF_ARL5.md) | 当前公共身份arpc-local-3，接续AR-L3/4，Schema不变 |
| [公共整体验证](../analysis/batches/ARPC006/RESULT.md) | 历史公共/监控兼容结果；不能拿Token私有复测代签公共整体 |
| [Token中文实际样例](FRONTEND_READABILITY_ART4.md) | 当前可读业务演示、真实封存state、实际GET及构造引用映射 |
| [前端UI-04工程验收](../viewer/analysis/ACCEPTANCE_UI04.md) | viewer-analysis-ui04-local-1、实际页面和浏览器/窄屏证据；用户功能/视觉验收及独立复审仍待进行 |
| [审查会话入口](../delivery/ENTRY.md)与[统一协作流程](../../architecture/TASK_SESSION_WORKFLOW.md) | 只登记已有复审角色，不自动新建/唤醒会话；打包须另获授权 |

旧 `docs/tasks/viewer/analysis/PROMPT_INDEPENDENT_REVIEW.md` 仍描述UI-03、AF006及“自动收益留V3”，是过期前端复审输入，**不能覆盖当前UI-04/T2–T4自动链路范围**。本线不代改前端归口文件。当前Token新插件为 `CurrentTokenContentPlugin/token-content-2`；历史类仍是 `TokenContentPlugin/token-content-1`。提案适配器为 `TokenProposalAdapter`，generator_identity=`token-content-recipes-1`，协议=`token-auto-proposals-1`。

## 3. 已有验证证据及未证明的事项

| 验证 | 实际记录与边界 |
| --- | --- |
| 原TA000–006及ARTA新增 | [ARTA004 RESULT](batches/ARTA004/RESULT.md)：162项完整回归/64.33s；另补缓存块边界1项/5.59s，去重163项。17个私有源码mypy、ruff通过。不是同一次163项全量命令 |
| 中文具体方案补充 | [ART4](FRONTEND_READABILITY_ART4.md)：新增定向1项/10.77s，ruff通过；未因只新增fixture重复整套回归。不能声称做过单次164项全量测试 |
| 实际接口样例 | [ARTA实际样例](batches/ARTA004/ACTUAL_API_EXAMPLES.json)与[ART4样例](FRONTEND_READABILITY_ART4_EXAMPLES.json)：真实worker/Tokenizer/完整原scope回放/create_app GET，不是手写收益 |
| 公共整体 | 提供方历史记录294项分析、300项监控兼容；AR-L4/5另有增量。分析测试与Token测试重叠，**不可把这些计数相加**；本次未重跑或代签 |
| 前端接收 | 原23/23、ART4 7/7摘要匹配；前端报告四卡、8例、浏览器及窄屏通过。不是本线重新运行浏览器或用户视觉批准 |

已有结果包含：仅appid原scope；N按完整回放raw实际改变计，不按Finding/样例/Token差计；noop N=0；缺依据N/收益未知；不同依据各自prepare、相同操作共享evaluation；负收益保留；P1026→1022而C642→766仍可见；T3三模型真实编码回放、无Finding的Observation支持；新T1禁用/历史T1兼容；只读GET；预算partial不替换ready默认。

测试数据、业务策略和引用地址均为构造配置。真实的是固定Tokenizer/Chat Template资产、程序链路和离线测量；不是生产请求分布、策略批准、外部引用服务可用性、业务质量或性能收益。没有Agent重新执行，也没有输出质量/TTFT/SLA/费用的实测结论。`authority.status=verified`来自受控后台配置，**不是系统完成了生产业务审批或远程引用可达性验证**。T3本地fixture映射被读回核对，只证明该构造映射内容一致。

生产策略缺失时，默认空recipe bundle，不让前端填写参数/授权，不自行把测试bundle设成全局默认。hypothesis首批禁用；检测阈值不等于删除许可。

## 4. 独立审查及复测重点

| 重点 | 必须核对的结果/失败边界 | 主要位置 |
| --- | --- | --- |
| 范围与旧报告 | 当前插件只T2–T4；旧T1读取不回填/重算，新任务无工具定义精简；默认空bundle不冒充全部无异常 | current_plugin.py、plugin.py；公共bootstrap/summary |
| 配置与依据 | 未知版本/字段/handler拒绝；bool不能当整数，omission_permitted须真布尔；完整scope匹配、精确工具身份；缺依据与坏配置不同 | auto_config.py、auto_duplicates.py、auto_proposals.py |
| T2 | appid/工具身份/内嵌pointer匹配；投影保持行序和条数，不静默丢非对象行；截取范围有界；不把模型未证明参与当作精确Token贡献 | auto_targets.py、transformations.py |
| T4 | 同身份、源顺序最后K；K=0和缺配置分开；完整结果或明确text_part；不误删调用关系，不对截断/不完整历史宣称完整保留语义 | auto_config.py、auto_targets.py |
| T3 | 精确完整载荷及非重叠证据，可Observation无Finding；引用真实映射、参数schema、必需字段、工具摘要；普通副本删除必须角色/完整消息匹配，不删tool/call-bearing消息 | duplicates.py、authorizations.py、auto_duplicates.py |
| 修改保护 | 原文hash/RequestKey/scope、basis快照、目标和参数重新推导；大整数/负零/指数词法、JSON内嵌转义、重复key；失败不得产生部分修改/原文写回 | json_values.py、transformations.py、prepare_proposal |
| 归组与离线收益 | 跨规则共享证据不双算；不同依据不误合；独立Plan与复用执行引用均正确；M原scope，N完整raw变化；P/C分别计，零/负/P降C升不套低命中>1pp门槛 | 公共grouping/engine/evaluation，Token实际集成测试 |
| 资源与发布 | 配置/请求/单元/比较/候选/编码/Plan/例子预算；取消、源变化、失败、重试固定快照；partial/empty不覆盖ready；不缩scope伪称全量 | 本线控制点与公共runtime/service/pipeline/discovery |
| 前端证据与只读 | 真实局部位置与owner，最多3例不代替N；raw/decoded Unicode码点，无法定位有reason；缺依据保留before不伪造after；GET不调用分析/准备/编码，实例/task/scope隔离 | 公共AR-L4及API；UI-04验收与实际GET |

上述是独立复审应检查的矩阵，不表示本次已逐项重测。发现公共或前端问题交对应维护方，不能用“Token测试通过”关闭跨层缺陷。

## 5. 可执行复测与证据保护

在WSL `/home/zhangxiyue/TokenScope` 下使用已有 `.venv`，不安装/升级依赖，不构建镜像。先核对身份JSON里的各map；有漂移就记录文件、旧新SHA和影响，不覆盖旧manifest。使用全新basetemp：**pytest会清空指定basetemp，绝不能复用已有前端展示state或此前证据目录**。

```bash
# 先确认该路径不存在；存在就换新的后缀，不删除已有证据。
test ! -e artifacts/validation/token-independent-review-20261101-01
.venv/bin/python -m pytest tests/unit/token_content tests/integration/token_content --basetemp=artifacts/validation/token-independent-review-20261101-01 -q
.venv/bin/mypy src/tokenscope/token_content
.venv/bin/ruff check src/tokenscope/token_content tests/unit/token_content tests/integration/token_content
```

首行检查失败必须停止后续命令并换新路径。本线集成已包含真实自动链/HTTP/三模型/块边界/中文样例。按发现扩展公共测试，建议具体入口：`tests/unit/analysis_common/test_recommendations.py`、`test_recommendation_freeze.py`、`test_recommendation_runtime.py`，以及 `tests/integration/analysis/test_recommendation_engine.py`、`test_recommendation_publication.py`、`test_recommendation_http.py`、`test_recommendation_frontend_reports.py`；用另一个未存在的basetemp。只在跨层变更/问题需要时跑公共维护方定义的监控兼容集，不无依据堆叠重复全量测试。

保留实际命令、退出码、通过/失败数、耗时、工具版本、stdout/stderr路径和运行身份；不能仅引用本线历史通过数作为独立结论。当前已知Starlette/httpx弃用warning应记录，不为消除warning擅自升级依赖。缺模型资产或环境失败应明确区分测试未执行与业务失败。

可直接读取的ART4旧state：

- 根目录 `artifacts/validation/art4-readable-20261031-01/test_chinese_recipes_actual_se0`，内含inputs/state/synthetic-recipes.json/synthetic-reference-map.json。
- task `716967b3-3e69-4f58-82e8-37f5e7715b8d`，instance `2fceceeb-ea9d-4d67-9c63-da25cca35c1e`；服务当前实例仍须GET capabilities核对。
- 每项N/M=2/2；T2输入4144→2388；T3引用4144→3224、普通副本删除4144→3206；T4保留最近1份4144→3240。不是四项可以相加的收益。
- 本地服务恢复命令及端口见ART4文档、前端ACCEPTANCE_UI04；端口可能已有其他会话服务，先检查、不重复启动或终止他人服务。只读GET不需要重新提交分析任务，不设置生产recipe环境变量。

## 6. 复审输出和授权边界

复审报告应包含：实际复审session ID与角色；候选/依赖摘要及漂移；逐项范围与证据；按严重度列问题、文件/行、复现/影响、归口；实际运行结果；阻断与非阻断项；环境/生产数据限制；明确通过、有条件通过或不通过。问题转Token/公共/前端归口修复并以新身份复测，不私自改源码或契约来凑通过。

当前用户只授权整理复审交接，**本文件就绪不等于已经启动或发送复审**。后续在复审会话收到执行指令后，可按本prompt进行源码核对与本机隔离测试；不自动创建/唤醒会话。本轮及该prompt不授权构建临时测试镜像、前端发布包、Docker镜像、代码交付包、部署、远端操作、Git提交/合并/push；此前其他阶段的临时镜像/收口设想不迁移到本次。“审查会话”的角色名称不是打包授权。用户视觉批准、独立复审、生产策略批准和发布授权分开记录。
