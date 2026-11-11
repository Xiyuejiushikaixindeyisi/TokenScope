> V2历史材料，仅供追溯，不是当前启动/修复/打包指令。[原始字节](../../../originals/prompts/sessions/LOW_HIT_BACKEND_START.md) · [当前会话登记](../../../../../../memory/SESSIONS.md)。下文仅迁移导航链接，历史决定和结果未更新。

# 低命中率分析后端设计与开发：主会话恢复prompt

在TokenScope项目中继续工作，根目录/home/zhangxiyue/TokenScope（Windows为同目录WSL UNC）。你是当前主会话，实际ID应自行核实；登记身份为01a18be2-7112-7aa2-919b-5137d1f1b1ad，原角色为异常分析产品母会话，现由用户指定继续负责低命中率分析后端设计和开发。

产品v0.4已经用户审批通过，不重复申请产品审批。当前启动先做本线技术设计与已有能力核对，形成接入契约、实现/测试计划，再按项目工作流推进开发；不要把未编写的技术方案当已批准。此prompt不授权打包、部署或新增范围。若仍在fork准备轮，先完成材料和询问，不提前执行fork或编码。

按顺序阅读：
1. AGENTS.md、memory/CURRENT.md、memory/SESSIONS.md、docs/README.md。
2. docs/tasks/prefix-analysis/ENTRY.md、memory/tasks/prefix-analysis.md。
3. docs/tasks/analysis/BACKEND_SPLIT_HANDOFF.md、PRODUCT_PROPOSAL.md、LOW_HIT_DETECTORS.md、PHASE1_PLAN.md、RESULT_FIELDS_DRAFT.md；DISPLAY_EXAMPLES.md只重点读L1–L5及边界状态。
4. 按ENTRY读取现有监控API、编码/缓存计量与资产能力。只查直接相关源码，不全量读取上游或历史。

你的范围：L1动态元数据、L2工具排列、L3工具定义/集合漂移、L4历史改写、L5序列化不确定；包括证据、修改建议、目标appid窗口离线评估和后端验证。T1–T4由Token异常fork会话负责，不代写其业务逻辑。

你还作为两线公共分析结果模型、范围/证据引用、离线评估封装的唯一设计/集成维护方；这是复用监控统一能力的封装，不是重写Tokenizer/Template/缓存算法。先形成最小公共约定并登记路径/版本，供Token线接入；公共API/CLI/worker改动须先核对其他会话窗口，不同时覆盖共享文件。

产品约束：仅目标appid窗口；内部配置校验不作业务探测；无固定探测优先级；已知误注入cch清理按业务信息无损、同集合固定排序按稳定化修复；LCP不等于H，对照不等于真实缓存来源；修改原结构再编码；保留零/负收益；组合实际评估；GET只读；Loop和其他过程分析不实现。

将技术设计、代码地图、后续计划/验证分别维护到docs/tasks/prefix-analysis，长期记忆写memory/tasks/prefix-analysis.md；共同产品交接留analysis。每轮更新实际状态及必要交接，不把“有文件”写成“已实现/已验证”。源码/契约事实与产品批准分开。

开始时简述实际身份、当前阶段、范围和直接依赖，随后进行本线核对/设计。Token fork若尚未获准或尚未创建，按BACKEND_SPLIT_HANDOFF保留未知身份，不擅自创建或用父ID代填。
