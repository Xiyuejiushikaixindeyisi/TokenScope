# V2 用户监控后端功能入口

2026-11-03总设计师阶段同步：五项后端已独立验收冻结，两前端接入及HV2-AF-01/MF-02修复完成；根339项前端、88项最终浏览器通过（原失败与测试修正分别保留）。本线窗口关闭，统一版本与容器交付由V2总设计师继续；华为真实数据仍待验。[实际独立验收](../../delivery/HV2_INDEPENDENT_ACCEPTANCE_20261103.md)。下方旧阶段按历史阅读。

2026-11-03当前HV2-R1-USER：已实现只读多模型发布目录、用户提供TTFT默认参数持久化及自动计算候选；[本轮后端交接](HV2_USER_BACKEND_HANDOFF_20261103.md)和[2.1.0候选契约](../../../contracts/user-monitoring-v2/2.1.0/README.md)优先。待总设计师独立验收/冻结后才交前端；旧U008仅作历史。参数Qwen1/GLM2.7/DeepSeek2.6秒、K8192是用户提供参考，真实性能校准仍待完成。后续恢复只按prompts/sessions/hv2-repair-20261103/USER_BACKEND.md及当前执行板，不重复执行历史提交指令。


2026-11-02统一交付同步：V2已完成WSL打包、桌面全文件SHA核对，华为真实数据待验；用户认可V2可交付，UIR-03暂不修、留V3，不作V2阻断。本角色职责/休眠状态不变；当前发布与实际结果见[交付记录](../../delivery/V2_APPROVED_DELIVERY_20261102.md)。现场只用真实Trace3/MA18 CSV，先用户监控（搜索/P90 TTFT）和MA，第一次用户验收并指定appid后才两类异常；SSH18002，唯一Markdown嵌关键源码/证据。[当前prompt](../../../../prompts/delivery/HUAWEI_V2_REAL_DATA_20261102.md) · [固定规则](../../../operations/DELIVERY_ACCEPTANCE_RULES.md)。下方旧开发/交接状态按历史阅读，不覆盖本决定。

当前TTFT状态：**代码完成，性能校准待完成**。新最小模型已实现：W覆盖全部非计算耗时、不单列O；证据材料选填，缺必要参数不出比例、W不默认0。当前用户契约2.0.0，旧1.0.1历史兼容；[前端接入](TTFT_FRONTEND_HANDOFF.md)尚待前端实施/验收。
2026-10-30：用户已认可最终设计并授权连续开发。**U000–U005 closed，本地用户后端统一验收完成**；289全量回归及最终增量15项恢复测试通过，真实MA联合通过。未部署、打包或修改V1运行配置；前端、真实TTFT校准及现场仍pending。

## 优先阅读

P0：AGENTS → CURRENT → SESSIONS → docs/README → 本入口。
P1：[TTFT增量验收](batches/U008/RESULT.md) → [TTFT前端交接](TTFT_FRONTEND_HANDOFF.md) → [既有最终报告](batches/U005/RESULT.md) → [已实现API](IMPLEMENTED_API.md) → [分层验收](batches/U005/VALIDATION_SUMMARY.md) → [设计符合性](batches/U005/DESIGN_CONFORMANCE.md) → [版本](VERSIONS.md)。
需要修改时再读[当前设计v1.1（最小产品方案获认可，后端适配已实现）](DESIGN.md)、[批次计划](BATCH_PLAN.md)、[交叉检查](CROSSCHECK_MA_20261030.md)及相关batch四文档。设计目标与实际验证分别以设计/最终报告为准，不用旧“未实现”描述覆盖现状。
P2：按问题读[V1实际API](../../../contracts/MONITORING_IMPLEMENTED_API.md)、[S0](../batches/B005.1/S0_CONTRACT.md)、[现场验收](../../../huawei/MONITORING_V1_ACCEPTANCE_20261030.md)、[MaaS](../../../architecture/MAAS_REFERENCE.md)、[MA设计](../v2-ma/DESIGN.md)及[UI-01](../../viewer/PROTOTYPE_V2_UI_01.md)。

## 范围与接入

- GB appid×common_name独立、每CSV空缓存；原JSON先tokenization得到J，P套模板，C=P−H；排行基于C众数箱内均值，最低并列箱为排序代表。
- V1 UTC日期/模型别名/DeepSeek现场模式兼容已修复；旧default不静默覆盖。生产缺省、GF资产/GLM CP限制保留。
- TTFT为P90长度固定chunk情景参考；等待参数化，无队列模型、总体命中达标保证或实测准确性承诺。
- 用户router/控制库/索引独立；HTTP worker及CLI work-once通过Dispatcher.register接入，与MA/V1共用同state_root/worker.lock。共享app/CLI编辑窗口已释放，接入方先读最新文件。
- 不负责MA编排、异常分析、前端、hybrid、自动采集或生产路由切换。内网开放仍由审查打包会话另行授权。

[契约2.0.0](../../../contracts/user-monitoring-v2/2.0.0/README.md) · [本线记忆](../../../../memory/tasks/monitoring-v2-user.md) · [角色登记](../../../../memory/SESSIONS.md)

## 源码/前端交接
本轮用户授权提交并push。前端首先阅读[用户后端交接](FRONTEND_HANDOFF.md)，提交边界见[Git交接检查点](GIT_HANDOFF_20261030.md)。本会话转为前端接入支持/后端维护，未部署打包。

## U006–U008提交交接（2026-10-31）
本轮用户授权提交/push，范围与实际Git身份见[U008 Git检查点](GIT_HANDOFF_U008_20261031.md)。优先采用[TTFT前端交接](TTFT_FRONTEND_HANDOFF.md)及契约2.0.0；前端接入支持/后端维护，性能校准待完成，不部署打包。

## 2026-11-03最新：HV2用户后端已独立验收并冻结

总设计师已确认用户监控发现与自动TTFT 2.1.0独立验收通过，权威[冻结清单](../../delivery/HV2_USER_FREEZE_20261103.json)，identity为4d9e2e5d6c7031ff0aaa266114b92dbcb8684b9a80d722d2cfae9de8ad1d7dc0。上方“候选/待独立验收”保留为此前状态，当前以本节及冻结清单为准。监控前端正式接入已派发，后端源码窗口关闭；本线等待总设计师归口后续问题，不自行修改、复测、提交/push或监听。

冻结仅覆盖清单列出的源码/测试、2.1.0与旧2.0.0契约及相关锁/S0身份，不代表前端验收或现场性能校准通过。现场622条数差、真实性能准确性及大历史目录规模仍未决。前端按[本轮交接](HV2_USER_BACKEND_HANDOFF_20261103.md)接入；不恢复旧U008工作。
