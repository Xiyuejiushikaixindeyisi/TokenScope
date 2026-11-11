> 2026-10-31：内容已整合到[唯一完整启动prompt](ANOMALY_ANALYSIS_FRONTEND_START.md)。本文件仅作Token接入历史参考，不再单独复制启动会话。

# 启动增量：异常分析前端接入Token内容后端

你负责统一异常分析前端，同时承接低命中率和Token内容分析。本prompt是已有ANOMALY_ANALYSIS_FRONTEND_START的后端接入增量，不创建第二个前端会话，不接管监控V2、公共后端或探测算法。

项目为/home/zhangxiyue/TokenScope，Windows同目录为\\wsl.localhost\Ubuntu-22.04\home\zhangxiyue\TokenScope。先读AGENTS.md、memory/CURRENT.md、memory/SESSIONS.md，再由docs/README.md进入docs/tasks/viewer/ENTRY.md。登记本会话实际ID、角色、阶段、优先级、维护范围与依赖；ID未知如实写未知，不复制后端ID。不要创建/唤醒其他会话、发消息或委派子Agent。

接着按顺序只读：

1. prompts/sessions/ANOMALY_ANALYSIS_FRONTEND_START.md及docs/tasks/prefix-analysis/FRONTEND_HANDOFF.md：统一启动与公共接入主入口，沿用已有视觉及审批约定。
2. docs/tasks/length-analysis/FRONTEND_HANDOFF.md（TA-FE1）：Token增量；已与低命中交接结构对齐，明确状态、字段、门槛、完整请求样例及验收清单。
3. docs/tasks/prefix-analysis/IMPLEMENTED_API.md和SELF_REVIEW_20261031.md：公共/低命中local-2实际协议、pilot_scope与confidence_basis；不要从Token类推L类卡片。
4. docs/tasks/analysis/BACKEND_IMPLEMENTATION_HANDOFF.md及docs/contracts/analysis-common-1.0、diagnostics-http-1的README/wire.json：H0–H4、冻结Schema与维护分工。
5. docs/tasks/length-analysis/IMPLEMENTED_API.md、BACKEND_HANDOFF.md；按问题查对应真实集成测试，不全量阅读研究/算法源码。

当前两线后端本机已闭环，HTTP diagnostics-http-1、公共analysis-common-1.0可接入；Token最终112项本线测试通过，公共后续自审结果独立记录。后端通过不等于前端已验收或本prompt授权立即编码。已有前端阶段授权若存在继续遵循；尚未批准前端方案时先做职责/就绪核对和接入设计，按用户审批推进，不重问已批事项。本次绝不打包部署。

必须保持的接入语义：

- capabilities取得实例；其余请求带x-tokenscope-service-instance。源为封存base/user_v2的appid及窗口，不接MA请求库；缓存按实例/task/scope隔离。
- 页面访问不创建分析任务。显式提交后仅跟踪对应receipt，终态停止；Token排在低命中阶段之后且始终使用原scope，不能把等待写成无异常。
- 当前没有服务器按appid列出/查最新报告的端点，也没有receipt创建/完成时间；保存已知task_id和父子任务引用，不虚构历史发现API或用读取时间当分析时间。分页恰满页继续请求，所有ID独立编码，切换实例隔离旧响应。
- Token发现取fragment.finding_candidates；T3可能只有observation；不要从items/finding或optimization找Token结果。用fragment_index映射location/unit/observation身份，不自行重写哈希。
- 元数据整数wire是字符串；嵌套JSON文本保持原数字词法。证据用完整requests/{fragment_id}，>64KiB不能用预览代替；同请求多位置不伪造第二请求。captured未知与raw完整分开。
- 任务状态、规则状态与condition、评估状态分开；失败/未查/不适用/unknown不等于正常。任务状态放任务区，业务卡片只展示已有事实/建议。
- 严格>1pp仅作用低命中优化卡片。Token/combined的gate_passed=null、display_eligible=false不能隐藏结果；零负/P下降C增加完整显示。compute_tokens_delta=after.c-before.c，子集和全范围不能相加。
- T1–T4无业务策略不报超限，不猜Loop、输出浪费、参数错配、费用或质量。候选待参数不自动裁剪；引用/删除须显式授权和真实协议/引用值。
- 授权与普通评估返回新task；从其plan/evaluation/authorization及evaluations/{id}/rows读实际证据。组合只引用同scope已存Plan独立评估，不相加收益，冲突无after。

先形成自己的docs/tasks/viewer/analysis/BACKEND_ALIGNMENT.md，分别登记公共/低命中/Token版本、已接收能力、实际缺口与展示映射；维护自身入口和memory/tasks/viewer-analysis.md。需要新字段记具体需求交对应后端，不改两线契约/源码，不在前端实现替代诊断。原型视觉沿用已批UI-01及用户后续决定，不从零另造风格；不覆盖监控V2页面或原型。

首轮向用户说明当前授权下的阶段、接入范围、两个方向不同门槛以及尚待前端确认的布局/交互。后续验收至少包括：状态与历史报告、源/实例隔离、Token事实与策略区分、T3多位置、全文/内嵌定位、零负效果、授权/参数缺失、组合冲突、GET不计算、终态停轮询。后端合成样例不能代替浏览器/视觉验收。参数错配仍独立研究，暂不打包或部署。
