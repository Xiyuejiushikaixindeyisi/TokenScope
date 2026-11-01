# ARTA000 公共方设计签收

TA-S1补充：本历史设计签收中的T1模板/四规则内容由[SCOPE_T234_ACK](SCOPE_T234_ACK.md)覆盖；当前只T2–T4，不新增长度精简职责。文档对齐不等于Token编码授权或机器冻结，当前阶段见回执。

2026-10-31。提供方：低命中/公共后端session `01a18be2-7112-7aa2-919b-5137d1f1b1ad`。核对Token session `01a18fcd-0464-7cf1-b435-4f394bd33e66`的[ARTA000对齐说明](../length-analysis/ARTA000_ALIGNMENT.md)，以其第8节最新收口覆盖前文提议。公共权威为[AR-C1契约设计](../analysis/RECOMMENDATION_CONTRACT_ALIGNMENT_AR1.md)。本签收只完成文档对齐，不代表机器Schema、路由、自动链路已交付或联合测试通过。

| 核对项 | 公共方结论 |
| --- | --- |
| 版本及职责 | 接受analysis-recommendations-1、recommendation-group-1、evidence-locator-1；适配器统一token-auto-proposals-1及四方法。公共维护Schema/ID/归组/回放/存储/router，Token维护recipe、typed basis验证与handler适配；不改冻结AnalysisPlugin |
| 支持关系及ID | 接受token_observation与observation_ids数组，T3允许finding_ids为空。公共验证同task/scope/fragment引用。recipe不含请求身份，target必须含；ID不含task但读取隔离绑定实例+task+scope+版本，不跨task复用执行 |
| 分组及评估复用 | 接受相同生成规则及依据才归组；不同依据分别保存推荐且独立validate/prepare通过后才可共享canonical执行。prepared/execution/evaluation三种引用分开；冲突操作不自动组合 |
| N/M与null | M为scope请求数；N为完整available回放的raw修改子集计数，不是匹配/位置/Token减少数。未完整评估N=null，noop为0，P不变仍可N>0；未完整匹配matched_requests=null。跨卡不累加 |
| 依据与状态 | 接受缺依据检查完整可advice_only/ready；invalid授权、技术缺失、预算中断与执行失败不能伪ready。有效依据不适用为not_applicable。空bundle与丢失/坏bundle区分。采用第8节公共reason命名，具体缺项通过结构化reason_details表达 |
| 预算 | 接受recommendation-budget-1服务端快照，具体默认见AR-C1第7节。受既有更严硬限制及全任务encoding_calls约束；新Token回放额度不等于新增编码许可；失败启动计数、复用不重复计数 |
| 分页与兼容 | 接受AR-C1第2节确切GET路径；limit默认50、1–100，offset非负十进制文本，next_offset=null终止。封存task不可变、稳定排序；同task分页不需要额外可变快照。旧报告not_computed，不GET补算。详情缺对象404、未封存409、非法参数422、存储错误503 |
| 发布 | 推荐、Plan、Evaluation、例子必须先完整封存并验证关联，再终态发布及通知；partial/empty保留旧默认，两方向整体ready才更新其包含方向，前端只读 |
| 业务策略 | 首批完整后台配置驱动；无依据T2/T4假设默认关闭，T3不绕过真实协议/删除约定。不将视觉示例、测试fixture或检测limit当授权 |

补充签名输入已明确scope_id、fragment_id、capabilities；来源记录放authority的source_kind/source_ref/source_digest，不再增加平行basis.source结构。缺项原因、范围不匹配与非法依据的区别已写入AR-C1第6节。

**公共方结论：ARTA000所需文档语义已签收，无待业务选择的工程分歧。** Token方自行记录本线ARTA000退出，本文件不代签其批次。实际业务配置尚未核实，运行时未实现；两者分别作为后续业务验收和工程批次依赖。分批执行与验收以[ARPC000–006计划](../analysis/RECOMMENDATION_IMPLEMENTATION_PLAN_AR1.md)为准。本轮未编码、改正式前端、启动任务、打包或部署。
