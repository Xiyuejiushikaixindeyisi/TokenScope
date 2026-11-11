> V2历史材料，仅供追溯，不是当前启动/修复/打包指令。[原始字节](../../../originals/prompts/sessions/TOKEN_ANOMALY_BACKEND_FORK_START.md) · [当前会话登记](../../../../../../memory/SESSIONS.md)。下文仅迁移导航链接，历史决定和结果未更新。

# Token异常分析后端设计与开发：fork启动prompt

你在TokenScope项目的fork会话中工作，根目录/home/zhangxiyue/TokenScope（Windows为同目录WSL UNC）。用户已批准异常分析产品v0.4，并指定当前主会话负责低命中后端、你负责Token异常分析后端设计和开发。此prompt仅在用户明确允许且fork成功后发送执行；文档存在不等于已经创建会话。

首先核实自己的真实session/thread ID并登记memory/SESSIONS.md、docs/tasks/length-analysis/ENTRY.md、memory/tasks/length-analysis.md。父会话ID为01a18be2-7112-7aa2-919b-5137d1f1b1ad，绝不能用作自己的ID。若工具/环境身份不一致或仍未知，如实记录并核对，不臆造。继承历史仅用于理解，不接管母会话全部任务。

阅读顺序：
1. AGENTS.md、memory/CURRENT.md、memory/SESSIONS.md、docs/README.md。
2. docs/tasks/length-analysis/ENTRY.md、memory/tasks/length-analysis.md。
3. docs/tasks/analysis/BACKEND_SPLIT_HANDOFF.md、PRODUCT_PROPOSAL.md、TOKEN_CONTENT_DETECTORS.md、PHASE1_PLAN.md、RESULT_FIELDS_DRAFT.md；DISPLAY_EXAMPLES.md重点读T1–T4及边界状态。
4. 按ENTRY核对监控已有原文、字段映射、统一编码与实际接口。只读取本线所需源码/资料，不全量重读母会话研究。

职责仅为首期T1工具定义负担、T2大工具返回注入、T3同一载荷重复搬运、T4历史工具结果负担，含具体判据、证据、内容修改方案、离线评估接入、测试和后端交接。目录length-analysis是兼容路径，不等于只做长度阈值，也不代表获得Loop/执行过程分析授权。

产品v0.4已批准，不再重复产品审批。启动先完成本线技术设计、能力/数据缺口核对、接口需求及开发/验证计划，再按项目工作流进入实现；尚未形成的技术方案/契约不写成已批准。不要实施新trace采集、模型摘要、工具搜索/上下文管理架构、前端、部署或打包。

共享接口：原监控拥有Tokenizer/Template/J/P/H/C和缓存算法；主会话低命中线维护两线公共分析结果、范围/证据引用、离线评估封装与集成。你提供本线输入/输出要求，复用固定版本，不复制公共回放/存储、不改L1–L5。共同契约未固定可先做本线设计和明确标注的样例，不冒充联调通过。共享源码、API/CLI/worker、索引和配置修改前登记唯一维护方与范围；不要直接覆盖主会话文件。

必须保持：
- 只评估目标appid/服务/窗口，子窗口重算基线与源监控值分开。
- 内容负担、优化机会、超出业务约定分开；没有业务上限/策略不发明阈值。
- 字节和字段Token归属分开，ΔP不是精确字段贡献；正常跨请求历史携带不判重复浪费。
- 请求快照不等于真实工具事件；无可靠关联不判Loop/失败重试或执行次数。
- 具体修改只在原结构副本完成，再复用统一计量；只给真实完成的离线结果，负收益/零收益保留，组合不能求和。
- 已知cch/排序修复语义沿已批产品，不重开无损争论；它们由主会话低命中线实现。
- 页面只读已保存结果；PrefixLens仅参考，构造样例不当作测试结果。

本线维护docs/tasks/length-analysis/{ENTRY,DESIGN,CODEMAP}.md及后续计划/验证文件、memory/tasks/length-analysis.md、自身SESSIONS行。共同产品语义变化先列差异，不整份重写analysis、CURRENT或SESSIONS。开始时说明身份/角色/阶段/优先级/依赖，然后推进本线能力核对和详细设计；每轮记录真实完成和未决事项。
