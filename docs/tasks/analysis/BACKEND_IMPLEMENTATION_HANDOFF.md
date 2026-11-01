# 两类异常分析后端实施接口交接

当前ARPC实现保存点：[进度与未完成项](ARPC_PROGRESS_20261031.md)、[T2–T4范围回执](../prefix-analysis/SCOPE_T234_ACK.md)。公共基础已有实现，机器Schema仍为范围修订前工作稿，不可正式消费；等待统一阶段答复，未接入新自动链/HTTP。

2026-10-31 AR-C1推荐扩展设计对齐：[公共工程基线](RECOMMENDATION_CONTRACT_ALIGNMENT_AR1.md)、[ARTA000公共方签收](../prefix-analysis/ARTA000_PUBLIC_ACK.md)、[ARPC000–006分批验收](RECOMMENDATION_IMPLEMENTATION_PLAN_AR1.md)。对外统一analysis-recommendations-1，Token静态适配token-auto-proposals-1；旧冻结协议不变。仅文档语义对齐完成，机器Schema/API/自动链路未交付，不把历史H0–H4验收当新能力测试。

FE-N1公共增补已实现：[通知/目录/时间协议](../prefix-analysis/NOTIFICATION_HANDOFF.md)。独立diagnostics-discovery-1，冻结H0/HTTP及Token插件不变；包含评估/授权无报告终态恢复与父证据关联，Token/combined零负值展示不变。用户确认partial/empty保留旧默认、整体ready更新已包含方向；本线提供方测试不代签前端/Token消费者新验收。

前端接入统一阅读入口：[公共与低命中前端交接](../prefix-analysis/FRONTEND_HANDOFF.md) → [Token交接](../length-analysis/BACKEND_HANDOFF.md) / [Token参数API](../length-analysis/IMPLEMENTED_API.md)。用户已认可低命中完整自审；接入prompt已更新，未创建/启动前端会话，不代签接收。

2026-10-31公共方自审补充：low-hit-backend-local-2 修复取消与发布事务边界、末条回放复核和预算证据保留；低命中 Plan 字节预算与 Token 统一为完整序列化 Plan。H0/HTTP 冻结摘要一致，Token 私有代码未改；公共/低命中/Token 联合193项、额外计数边界2项及监控兼容300项通过。experiment 新增 pilot_scope/reason_codes/confidence_basis，不改变 EvaluationResult 或 Token 的报告门槛。详见 [自审验收与字段说明](../prefix-analysis/SELF_REVIEW_20261031.md)。这是公共方的实际消费者回归记录，不代签 Token 会话新增验收。

2026-10-31实施交接更新：用户已授权两线逐批开发，H0–H3b提供与消费验收完成，H4本地交接收口；不是早期planned状态。公共analysis-common-1.0及HTTP diagnostics-http-1分别冻结，主线low-hit-backend-local-1工作树身份见LH009；Token TA005/TA006已由其本线验收closed。实际入口为[公共/低命中API](../prefix-analysis/IMPLEMENTED_API.md)、[公共验收](../prefix-analysis/batches/LH009/RESULT.md)、[Token交接](../length-analysis/BACKEND_HANDOFF.md)。无打包部署。

## 1. 身份与责任

| 维护方 | 实际session ID | 唯一维护范围 |
| --- | --- | --- |
| 低命中/公共层 | 01a18be2-7112-7aa2-919b-5137d1f1b1ad | analysis_common、prefix_analysis、诊断API/任务/存储装配及公共契约 |
| Token内容 | 01a18fcd-0464-7cf1-b435-4f394bd33e66 | token_content、T1–T4及其纯变换处理器、本线测试与文档 |

Tokenizer/Template/缓存算法复用现有监控；不由两线复制。app.py/cli.py及配置修改由公共维护方在实际接入前登记窗口；本文件不预占当前监控联合审查的共享代码。Token不实现独立Dispatcher、数据库或编码器，不写公共源码。

## 2. 本次读取身份

本轮工作树HEAD读取为5c619f80631dbd0efdcbadffa7eedbf314bb678e，仅表明读取时版本；未重新审查全部源码或运行功能。以下摘要绑定实际设计文档字节，不表示工作树洁净或接口已冻结。

| 来源 | 版本 | 本轮读取SHA256 |
| --- | --- | --- |
| [公共契约](BACKEND_COMMON_CONTRACT_DRAFT.md) | analysis-common-draft-2 | 87163e5a5b173cf72ec397b707c318580cae6cd9eb20c505a2be4024129ce865 |
| [低命中修订](../prefix-analysis/DESIGN_REVISION_20261031.md) | prefix-design-0.2，用户已认可 | 8ba209ddc654914e50054df61ceb29d7615fc364135024fca084b0e0941a4af8 |
| [Token对齐](../length-analysis/COMMON_INTERFACE_ALIGNMENT.md) | TA-C0.2 | 1c38da909c56629f726260a7ce93e61d27c6e4245aafd7415f42d798286c9892 |
| [Token计划](../length-analysis/BATCH_PLAN.md) | TA-B0.1，读取时planned | c63921584da8d53aa7d0b402c9e8734dabdce2234c94b65357d1d63d9c1a6d01 |

公共draft-2已由主会话接纳TA-C0.2的受保护外层替换、三层证据身份和静态插件方案。正式Schema/摘要及消费者确认在H0登记；不能沿用TA文档记录的旧draft-1摘要当成draft-2签收。

## 3. 交接里程碑与接收清单

| 里程碑 | 提供时点 | 提供方必须交付 | Token侧对应工作 | 当前状态 |
| --- | --- | --- | --- | --- |
| H0 公共逻辑契约 | LH000 | 版本化Schema/类型边界；wire/ID编码样例；状态/错误；Plan及插件接口；正反例；相对TA-C0.2差异 | TA000记录实际版本/摘要和接收/差异；TA001–003可做独立规则 | H0已交付，TA000实际签收 |
| H1 真实请求输入 | LH001 | resolve_scope/RequestView/IDs/编码桥接；源及资产身份；能力矩阵；完整原文、unknown映射样例与实际检查结果 | TA001–003通过公共输入读数据，不自行开源DB | H1提供、TA001–003实际消费 |
| H2 原子变换与评估内核 | LH002 | PreparedMutation静态registry、Plan应用/manifest、单次scope回放；失败原子性、真实编码及策略验证 | TA004提供本线handler，验证内嵌JSON等实际变换 | H2提供、TA004三模型实际消费 |
| H3a 真实公共任务服务 | LH007 | 公共service/storage/processor；报告持久化；scope/插件隔离；生命周期、retry和RunControl | TA005准备真实服务接入 | 提供且TA005真实服务签收 |
| H3b 实际HTTP提供方就绪 | LH008前半 | API/实例/错误/分页/完整JSON读取协议及实测；明确已实现与待联合项 | TA005与LH008共同完成真实插件/两方向流程 | 提供且TA005真实HTTP签收，G1–G3关闭 |
| H4 联合交接 | LH008联合项、LH009与TA006 | 双方实际源码/契约/模型身份、样例报告和评估、联合结果、预算、限制、回退 | 两线各自记录负责项及联合接收结果 | 两线本地结果交接；现场/前端/容器未执行 |

H3b允许Token进入真实API联调，不等于LH008退出；LH008关闭要求真实Token插件通过，避免“双方等待对方整批完成”的循环依赖。真实Token尚未就绪时公共层可以完成自身子项，不能以合成插件代签联合完成。

## 4. 公共调用面与数据交接

| 层 | 公共提供 | Token返回/使用 | 关键不变量 |
| --- | --- | --- | --- |
| 输入 | RequestView、AnalysisScope、原文lazy reader、EvidenceCapabilities | 消费不可变对象 | 相同冻结源scope；不把低命中优化副本当作Token原始输入；RequestKey不以hash_id替代 |
| 插件注册 | 版本化静态registry、RunControl | describe / validate_selection / analyze_request | 一个token_content插件，内部T1–T4；客户端不能指定模块路径；缺可选映射不阻断内容事实 |
| 规则结果 | 公共验证、归组、保存纯fragment | locations/units/observations/findings/candidates、coverage与状态 | location/unit不含rule_id；T2/T4共享事实；原文完整读取与采集截断未知分开 |
| 变换 | Plan冻结及原子应用、原值校验、统一编码 | prepare_mutation返回PreparedMutation | 内嵌JSON由Token解析编译，公共应用外层替换；同外层多操作一次编译，不自动重定位冲突 |
| 评估 | evaluate_plan及公共manifest、逐请求和全scope/修改子集指标 | 引用实际evaluation_id | 同appid/窗口/身份，失败不丢行；O仅背景；零负结果保存 |
| 调度与读取 | 后台任务、结果库、HTTP、封存/恢复 | 本线只返回结果，不写数据库 | GET只读；公共层负责原因开关/阶段顺序，不向每个规则注册worker |

## 5. 必须交给Token线核对的最新编排语义

以下来自用户已认可的低命中修订，属于公共调度/展示职责，不要求Token重新实现门槛：

1. 手动low_hit原因开启两方向，低命中探测及其已调度两阶段评估结束后再执行Token；仅长度/QPS原因直接Token。没有自动告警或32k/70%启动规则。
2. Token使用同一原始冻结范围，不隐式接受L类删除后的请求；跨方向组合需显式组合计划独立评估。
3. 小范围/全范围严格>1pp的高置信度与卡片门槛只作用于低命中优化；Token内容事实/业务策略结果及显式内容修改评估不套此门槛。
4. L4/L5两份完整JSON是独立差异证据。通用Evidence可引用完整源请求，但不能用预览进行检测，也不能把完整读取等同于采集无截断。
5. 无低命中发现或规则局部失败仍可继续Token；源身份/完整性失败阻断共用范围，中断停止后续；预算耗尽如实标未查，不把未运行Token写成无问题。

状态：已按用户授权使用真实会话工具逐项发送H0/H1/H2/H3a/H3b及G1–G3回复；Token实际消费者记录已核实，不代签其职责。公共方未修改Token私有源码或记忆；其TA005与TA006结果由其维护。

## 6. 交接完成与差异处理

每次实际交接记录提供方batch、源码HEAD/必要工作树摘要、契约版本/摘要、模型/profile身份、已实现能力、验证命令/结果、消费者接收状态/差异与对应版本。契约文件一旦冻结不静默改写；影响消费者的修订应另存版本并列兼容/迁移。

纯规则可用标记清楚的fixture推进，真实源/编码/服务/HTTP能力必须有各自验证，不能互相代替。相同实际检查结果可双方引用，不机械重复运行；对改动或未解决失败再针对验证。

联调最低集合：同appid隔离；同位置跨规则共享不重复计数；内嵌JSON/数组冲突；准确guard失败无收益；真实Token单独路径及低命中后Token；低命中筛选不屏蔽Token；中断/失败/重试及只读GET；真实统一编码计量。产品前端验收、现场数据验证、容器及交付另列，不在本轮自动启动。
