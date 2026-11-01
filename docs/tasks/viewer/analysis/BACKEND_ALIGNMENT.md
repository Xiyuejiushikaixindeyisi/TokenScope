# 异常分析前端接收记录

2026-10-31；接收session `01a19111-344a-75c1-84e0-14db8be08f4f`。仅静态检查，未启动服务/任务或运行后端回归。提供方历史测试不作为本轮前端复测。

## 三方记录

| 维护方 | 权威路径、版本 | 批准/冻结依据、后端已有测试 | 本次检查、结论 |
| --- | --- | --- | --- |
| 公共（低命中维护方） | [职责交接](../../analysis/BACKEND_IMPLEMENTATION_HANDOFF.md)；[analysis-common-1.0](../../../contracts/analysis-common-1.0/README.md)、[diagnostics-http-1](../../../contracts/diagnostics-http-1/README.md)各自wire.json/manifest.json；runtime/report各为1 | README/manifest冻结；H0–H4交接与local-2自审；用户认可自审由交接材料记载 | manifest共8条全部匹配；读取wire字段和六种POST模型。静态接收；运行时capabilities/实例待验证 |
| 低命中 | [前端交接](../../prefix-analysis/FRONTEND_HANDOFF.md)、[API](../../prefix-analysis/IMPLEMENTED_API.md)、[自审](../../prefix-analysis/SELF_REVIEW_20261031.md)及SELF_REVIEW_CODE_IDENTITY.json；low-hit-backend-local-2 | prefix-design-0.2、LH000–009和完整自审已获认可；提供方193联合、2边界、300监控兼容通过，集合不相加 | 清单41/41匹配；接收L1–L5、实验/证据和门槛；无本轮前端业务测试结论 |
| Token | [TA-FE1](../../length-analysis/FRONTEND_HANDOFF.md)、[后端交接](../../length-analysis/BACKEND_HANDOFF.md)、[API参数](../../length-analysis/IMPLEMENTED_API.md)、[TA006结果](../../length-analysis/batches/TA006/RESULT.md)及CODE_IDENTITY.json；token-content-1、T1–T4@1、七handler@1、token-policy-1、token-authorization-1 | TA-D0.3/TA-B0.2已批范围，TA000–006本地闭环；提供方112项、ruff/mypy、三模型handler和GLM HTTP验证 | 43条中40匹配，3个公共文件与旧快照不同；Token私有文件匹配。静态接收Token接口/私有身份，旧公共快照不作为当前联合身份 |

观察HEAD `5d824b506d9e055bcf397c3846dafc450fcf02e5`；共享工作区有其他会话修改及未跟踪后端文件，HEAD不能证明这些内容已提交/发布。未暂存或Git收口。入口/manifest摘要及逐文件expected/actual见[机器记录](RECEIPT_IDENTITY_20261031.json)。

核心wire摘要：公共 `0ca27b5fe84048364ae15e471e78e2b835314265fd93b330283699462b7d1dcc`；HTTP `943a88daa45f6f3de18547bda28f260836d340f8180e03322afa525596161064`。

## TA006公共快照差异

| 文件 | TA006历史SHA256 | 当前SHA256（匹配local-2） |
| --- | --- | --- |
| src/tokenscope/analysis_common/evaluation.py | 9d7a10978693f76d6c630428f343a3bbde8b0aa4306b90f026e04aa1fc5e231a | 0028dfaa07b2ca674967afca276fedf48e3917a452d158245d32cdda534688ec |
| src/tokenscope/analysis_common/service.py | 8e43966c68366c283da9739ebca624d02c8dd694c93743d14620bd3f2b3d1ba6 | 5930837fc4b53f74ab8ed7686be91ac5ea4f7427afa71770a7fbb3dff326ce55 |
| src/tokenscope/analysis_common/storage.py | 2264b7e58181f51077b1ca7833ec01686a2af737f7028127d9d90144d256d24c | b78c89e1b2be2d792bd7deb53f4bede8e1a306cac4e7860a9ea359a6f568f237 |

local-2自审记录取消/发布事务、末条回放复核、预算证据保留等后续修复及联合回归。这解释版本先后，但本轮未重跑，也未取得Token消费者对新公共身份的新签署。保留差异，不更新历史/冻结摘要；公共维护方与Token消费者在真实联合前复核当前候选。此项不阻止文档/展示讨论。

## 接收边界

1. capabilities免实例头；其他诊断请求使用x-tokenscope-service-instance。POST按HTTP wire的request/options等模型，不套监控S0头。base/user_v2封存来源、手动appid/原因/可选半开窗口；MA仅线索。low_hit先低命中后原scope Token，长度/QPS只Token；页面访问/GET不提交分析。
2. TaskReceipt七状态与stage/RuleResult/EvaluationResult分别解析。仅跟踪中的queued/running查状态，终态停止，report_ref可用才读成果。partial保留证据与局限，empty不是正常，失败不覆盖旧报告。报告可stages=[]且准备阻断时无evaluation，只有reason_codes。
3. 无任务目录/latest报告/创建完成时间/进度百分比/SSE接口，不虚构。已知task_id按实例保存；分析时间未提供，不用浏览器读取时间替代。
4. items列表为{id,data}，单项GET直接data。分页只有items/offset，limit 1–100；满页继续、不足结束，无total/has_more。未加载完不能称全scope统计或全局排序。
5. 低命中finding/experiment/optimization独立于Token fragment。Token数据在fragment.data：request_key/raw_sha256/locations/units/observations/finding_candidates/modification_candidates/rule_results/coverage/reason_codes；T3没有Finding也保留Observation。
6. fragment_id取item.id，fragment_index的location_ids/unit_ids/observation_ids按数组同序关联，不自行hash造ID。子评估保留父task_id，回溯原finding/fragment。
7. L4/L5用comparisons/{finding_id}两份完整原文，工具漂移两端路径独立。Token用requests/{fragment_id}同请求多位置。raw_body_complete不证明采集未截断，capture_truncation unknown仍未知；64KiB预览不能替代全文。
8. source_pointer与embedded.pointer分开；embedded=null不同于内层根空串，展示parser版本。通常无raw offset，不用全局首次字符串匹配冒充定位。原文安全文本渲染，保留原始数字词法；格式化副本不覆盖原文。
9. 元数据整数为十进制字符串；JSON文本内部业务数字不转换。n/j/p/h/c及范围明确，P=H+C、R=H/P且P=0为null，J不是P。精确pp分数及服务派生资格只读，不用浮点重判；compute_tokens_delta正值表示计算Token增加。
10. 完整pilot严格>1pp才自动full；完整full/direct_full严格>1pp才低命中优化卡片。direct_full标明绕过pilot。L4/L5事实独立，Token/combined不套门槛，零负收益保留；available之外不补after，仅available读rows。
11. ContentUnit字节/字符/行等不是Token贡献；participation included/ignored/unknown原样表达。无policy展示事实/机会，inventory/met不是异常；父子/重复/共享unit不累加为浪费；coverage不是进度。
12. T3只证明同请求完整重复，不证明Loop/执行次数/可删除。授权必须基于已存Observation/selected_unit、支持handler、真实业务依据；候选评估需真实parameters_json/business_basis_ref。T4 keep_last缺失与0区分，later_message_count不是turn/时长，多文本块按容器关系。
13. Plan完整操作/guard、预算/runtime_options、scope、模型/资产/配置身份可追溯。组合仅2–8个同scope已存非pilot Plan，独立回放、冲突无after，收益不能相加；不推断输出Token、质量、费用或性能。

## 样例与缺口

两份FRONTEND_HANDOFF为构造样例和协议说明，不是现场成果；本轮未执行from_wire/后端回归。已有低命中完整>1pp、恰1pp、full超预算、L4/L5双全文；Token已有65536字节参与unknown无policy、同请求三位置未授权、P10000→8000而C2000→3000、零效果、阻断及等待保留旧报告。T4 keep_last=1已有说明，缺失/0成对用例需后续建立明确标记fixture。

| 缺口 | 处理/影响 | 负责方 |
| --- | --- | --- |
| 无运行时capabilities及真实浏览器HTTP验证 | 本轮未访问服务，不宣称联调；后续绑定实例、源码、资产 | 前端与两后端 |
| 无任务目录/latest/分析时间/百分比 | 使用已知task_id；跨浏览器恢复及文案待确认，新增API另协商 | 用户/前端；公共维护方 |
| 无生产预算/policy默认值 | 不把样例预算静默用于生产；确定配置责任与入口 | 用户与后端/前端 |
| 低命中无直接影响请求数/概率置信度字段 | 不复用DEMO合成值；排序回退/覆盖表达需讨论 | 前端/用户；必要聚合交后端 |
| 无完整静态封存响应fixture包 | 后续用隔离测试成果或明确标注构造fixture覆盖三层状态和边界 | 前端/后端 |
| TA006公共身份滞后 | 历史保留，真实联合前重新绑定并复核 | 公共方/Token消费者 |
| UI-01直接浏览受阻 | 当前仅核验摘要及设计说明；视觉/范围/详情检查待补 | 前端 |

结论：冻结契约路径明确且摘要一致，两类本地实现已有提供方验证依据，可以讨论接入方案；不等于前端设计、HTML、编码、真实联合或现场验收通过。

## diagnostics-discovery-1增量接收初核（2026-10-31）
已读公共后端NOTIFICATION_HANDOFF、FE-N1 RESULT、独立契约README/wire/manifest。5项摘要逐项一致，新增目录/通知/完成时间已提供；旧文无接口及首次partial/empty待明确的描述由新交接覆盖。提供方199/7/300测试未由本轮重跑；未调用服务或浏览器联调。当前storage为新discovery身份，不再以local-2旧文件摘要代表当前整合版本。详见[开发前核对](DEVELOPMENT_READINESS.md)。

## FE-R-L1 / FE-R-T1最终接收（2026-10-31）

按用户授权分别发送两个现有后端session并等待最终完成；已收到各自字段映射、身份清单、完整关联构造样例和监控边界。前端复核64项公共/低命中、28项Token摘要全部一致，样例JSON可解析。前文“无目录/通知/时间、缺样例、当前身份待补”已由新交付覆盖；只读展示不要求生产policy/授权输入。详细映射和仍有的能力边界见[开发前最终核对](DEVELOPMENT_READINESS.md)，过程与材料摘要见[协调记录](BACKEND_RECEIPT_COORDINATION.md)。可以进入开发方案设计，不等于正式编码获批或联调通过。
