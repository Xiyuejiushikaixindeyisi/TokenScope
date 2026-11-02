# HTML视觉基线与用户认可

2026-11-01最新用户认可：“这版L4/L5展示我认可。”认可对象为RV2正式页面的L4/L5各一张卡、每类最多3个代表例子；没有生成或替换原HTML。用户同时授权统一审查、修复复验通过后的打包交付，见[执行记录](../../analysis/UNIFIED_REVIEW_DELIVERY_EXECUTION_20261101.md)。

2026-11-01补充产品决定：L4/L5分别只显示一张卡片，每类详情最多3个代表例子，覆盖旧实现的逐差异组造卡。正式实现仍沿UI-04颜色/布局；[RV2当前验收](../../analysis/JOINT_VALIDATION_RV2_20261101.md)。本轮没有新HTML，也没有代签用户对正式页面的视觉认可。

## 当前基线：analysis-ui04（2026-10-31已认可）

2026-10-31：两后端 AR-L2/AR-T2 完成回传后生成 [7 张代表卡片](prototypes/analysis-ui04/tokenscope-analysis-ui04.html)，沿用 UI-03 的全部 CSS 基础。新信息结构强调影响请求、预期变化、局部证据与具体改法；L4/L5 无收益门槛，详情最多 3 例。

SHA256：`779e6665985fe02e6df9e7d0483ef8111a16a49c2b61fdb27aacbef58d624f5f`。实际版本/源样例身份与验证见 [manifest](prototypes/analysis-ui04/manifest.json)、[AR-02](REWORK_COORDINATION_AR02.md)。用户已认可 UI-04 信息结构并要求记录为新视觉基线。原HTML及摘要保留；随后用户明确移除Token T1，Token范围仅T2–T4，工具说明精简暂缓，因此原HTML里的T1卡片不是当前开发范围。当前信息结构/配色布局依UI-04，规则范围依[AR-03](REWORK_COORDINATION_AR03.md)。UI-03保留历史。本轮已补做 UI-03 桌面参考截图和 UI-04 桌面/窄屏视觉检查，下文“截图待补”为历史阶段记录。

## 历史基线：analysis-ui03（2026-10-31已认可）

用户原话：“这版只读 DEMO 和轻量缓存、历史切换、详情返回方案我认可。把这些决定更新到文档，记录新版 HTML 为视觉基线，并梳理进入开发方案设计前还需要后端补齐或确认的事项，暂不改正式代码。”

- 文件：[tokenscope-analysis-ui03.html](prototypes/analysis-ui03/tokenscope-analysis-ui03.html)。项目路径：docs/tasks/viewer/analysis/prototypes/analysis-ui03/tokenscope-analysis-ui03.html。
- SHA256：`e6fa9f96c946e066f2ed52a439b07350cb07d78a290427c6a1670f4662b56869`，本轮再次核验一致，HTML未修改。
- [manifest](prototypes/analysis-ui03/manifest.json)记录用户认可；旧UI-01/UI-02/UI-02-r1保留，不覆盖历史身份。
- 只读问题/证据、修改建议和后端已有预期提升；无单项评估表单/授权/提交/结果选择。当前正式实现视觉规格以UI-03为准。
- 轻量缓存、紧凑历史选择、详情返回原位置亦获确认，详见交互文档；工程容量/精确组件方案尚未批准，不推导为代码开发授权。
- 既有UI-03 DOM检查通过；本轮不重跑业务或浏览器测试。桌面/窄屏截图仍待补，用户实际认可与截图证据分别记录，不代填截图。

## 历史基线：analysis-ui02-r1

日期：2026-10-31。用户原话：“这版 DEMO 我认可，但是需要删除”这是支持的检查范围，不代表每次均已完整执行。“”。并要求记录版本、路径与摘要后开始交互讨论，暂不代码开发。

- 认可来源：本聊天用户实际反馈；非agent代签。
- 当时基线版本：analysis-ui02-r1（已由UI-03替代）。
- 文件：[tokenscope-analysis-ui02-r1.html](prototypes/analysis-ui02-r1/tokenscope-analysis-ui02-r1.html)。项目相对路径：docs/tasks/viewer/analysis/prototypes/analysis-ui02-r1/tokenscope-analysis-ui02-r1.html。
- SHA256：`1c3f5011717f48e1a2d93ce65853cbb380c90dab0c6ff6ecde2cf6bbf119bf81`。
- [manifest](prototypes/analysis-ui02-r1/manifest.json)记录批准文字、前版身份和修订范围。
- 唯一修订：删除指定句子及包裹它的p标签，其他字节保持不变。删除说明不改变partial/未检查结果必须如实表达的契约语义。
- 原analysis-ui02及UI-01保持原位，未覆盖；UI-02摘要e7256e18960f21114126bfa032be2382a8e91054e32a651dc57bb1c50121f6db。
- 原UI-02的DOM检查属于原版证据，本轮仅核验精确文案删除与文件摘要，未冒称重新执行完整浏览器测试。
- 桌面/窄屏截图尚未采集：工具浏览器先前受阻。用户认可已记录，截图待工具可用时补充，不伪造截图或将其作为重复请求同稿批准的理由。

批准适用于展示配色、布局、卡片/详情和已讨论内容；不扩大为未讨论任务管理、缓存、交互协议或代码开发授权。后续正式实现以该HTML为视觉规格，交互讨论见[讨论稿](INTERACTION_DRAFT.md)。
