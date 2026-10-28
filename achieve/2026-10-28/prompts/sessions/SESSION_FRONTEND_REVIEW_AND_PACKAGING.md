# 新session：TokenScope打包前统一审查与后续交付

你负责TokenScope的打包前统一审查，并在用户明确授权后承担Docker构建、镜像打包和代码交付包。本项目根目录/home/zhangxiyue/TokenScope，Windows对应WSL UNC路径。不要创建额外session或自动发消息。

先读AGENTS.md、memory/CURRENT.md、docs/README.md、memory/SESSIONS.md，登记从环境获取的实际session ID；获取不到写未知，不沿用前端/后端ID。仅更新自己的协作状态，保留其他session工作。

优先阅读：
1. docs/tasks/viewer/ENTRY.md及batches/F007/{CONTEXT,PLAN,ISSUES,TESTS,VISUAL_ACCEPTANCE,RESULT}.md。
2. docs/tasks/viewer/MONITORING_INTERACTION_V1.md（含F007补充）。
3. docs/tasks/monitoring/ENTRY.md、batches/B005.1/{PLAN,S0_CONTRACT,TESTS,RESULT}.md、JOINT_RESULT_V1.md；再沿当前入口进入B006，避免使用已归档的仅后端打包计划。
4. docs/architecture/TASK_SESSION_WORKFLOW.md、docs/operations/GIT_WORKFLOW.md和README运行入口。按引用阅读V100环境报告、构建资产与现场约束，不全量读项目或参考源码。

已知背景：原联合验证已完成，之后F007修复正式前端偏离审批HTML的问题。F007是纯展示修复：侧栏/筛选/元信息、六卡与Token去向、直方图与表单样式；后端契约、缓存、SSE、回执、导出校验未改。实现版本0.1.0-f007，用户验收链接http://127.0.0.1:8000/#/overview。该地址仅当本机服务仍运行时有效，重启按README，不假定旧4175就是当前版本。

F007已于2026-10-28获得用户明确回复“F007 通过”，已closed；审批记录见F007 RESULT/VISUAL_ACCEPTANCE。请核对该审批对应版本及当前工作树，之后仍需你完成打包前统一审查。人工通过与Docker/镜像/代码包授权是两件事；只有当前用户明确授权打包时才能执行打包，不把本prompt的职责说明当作打包批准。

审查要求：
- 用当前工作树和artifacts/validation/viewer/F007/source-manifest.json核对身份。F007基线HEAD为f92fc2870406ba6617a13066cd73f7420b8007c2，生成prompt时F007尚未提交；不能仅拉取main就声称拿到F007，不能清理或覆盖共享未提交修改。
- 阅读实际源码及差异，核查设计、闭环、测试、人工结论一致；重点确认展示精度、空值、范围、固定版本、缓存/事件生命周期、导出取消和校验未被破坏，业务GET不触发计算。
- F007前端回归与视觉证据独立于旧联合证据。纯展示修复不重复整套联合review；如审查发现实质数据/行为变化或证据缺口，说明具体问题和必要复测，不降低门槛或擅改契约。
- backend-owned joint*.spec.ts有旧UI选择器（“当前范围”、七卡等）；如需复测，可将定位改到metadata详情/精确Token总量，保留原身份、数值、缓存、恢复和导出断言。不能把选择器失效当后端功能失败，也不能删除断言换通过。
- 固定审查源码/资源/锁文件/S0/模型资产摘要，记录问题、修复、复测和最终结论，增量更新自己的记忆。未通过的问题按范围与用户讨论，不替用户签字。

审查通过且获明确打包授权后，按当前B006和交付约定统一构建前后端镜像、验证compose启动与必要容器测试、形成代码包/镜像包/部署执行prompt及版本配置摘要。CPU/驱动/Docker/Compose等按实际V100环境报告核对，不假定现场可用；本机通过不冒称现场通过。镜像包和代码包不上传GitHub，不用Docker反复代替日常开发测试。交付前列未决项和回退方式，给出实际文件路径和校验值。
