# F007 上下文：审批 DEMO 视觉还原

日期：2026-10-27。状态：用户随后批准开发；F007实现已完成，2026-10-28人工验收通过并closed。

用户已批准恢复 DEMO 页面骨架和样式，要求本次作为独立 batch，包含编码、验证、测试、视觉一致性单独验收、问题与闭环记录、增量记忆。本轮请求是生成最终修改方案，不执行代码修改。后端在 Docker 构建和镜像打包前统一阅读代码、闭环和设计文档进行验收；打包仍需用户另行同意。

## 权威与固定输入

1. 当前用户决定及本批 [PLAN](PLAN.md)：本批范围和实施顺序。
2. [前端交互设计](../../../../../../../docs/tasks/viewer/MONITORING_INTERACTION_V1.md)：数据交互与不变语义；本批覆盖其中仅将 HTML 视为“视觉起点”的宽泛表述。
3. 审批原型：`artifacts/prototypes/monitoring-v1/tokenscope-monitoring-demo.html`，SHA256 `ef7bb11c8d5450e41826a10c39230167b6a5bb22198416fff0c93c282ea5fdc5`。本批唯一视觉基准，保留原件，不改写为匹配实现。
4. 后端 [S0](../../../../../../../docs/tasks/monitoring/batches/B005.1/S0_CONTRACT.md) 和 [联合结果](../../../../../../../docs/tasks/monitoring/JOINT_RESULT_V1.md)：固定业务契约、已有联合证据；联合通过不代表当前 UI 获得视觉通过。
5. 工作区 HEAD `f92fc2870406ba6617a13066cd73f7420b8007c2`；实际前端会话 `01a17811-4c9a-7513-befc-b35723aec96e`，本轮由 CODEX_THREAD_ID 核实。

## 当前事实

当前页面已经具备真实数据交互，但横向导航、七卡四列布局及大块“当前完整结果”偏离审批原型。原型为左侧导航、紧凑筛选及元信息条、六卡三列、Token 去向条、三图并列。不得只修改配色后宣称还原。

8000 是用户人工验收完整服务；4175 可能是旧预览。实施与验收记录实际 URL、构建身份，不以旧标签页代表新版本。不得擅自停掉共享服务。

开始前工作区已有他人改动：.gitignore、README.md、docs/tasks/monitoring/ENTRY.md、memory/CURRENT.md、memory/SESSIONS.md、memory/tasks/monitoring.md、src/tokenscope/paths.py、tests/unit/test_paths.py；保留，不纳入本批实现或回退。编码前重新核对 HEAD/差异及原型/S0摘要，记录实际起点。

后续用户授权已进入编码；初始“本轮仅方案”的描述保留为起点历史。当前事实以RESULT为准。
