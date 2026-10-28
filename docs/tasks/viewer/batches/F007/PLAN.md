# F007 最终代码修改方案：恢复审批 DEMO 的页面骨架与样式

日期：2026-10-27。状态：closed / 2026-10-28用户回复“F007 通过”，人工验收完成。打包前统一审查独立待执行。

主入口：[CONTEXT](CONTEXT.md)；执行记录：[ISSUES](ISSUES.md)、[TESTS](TESTS.md)、[VISUAL_ACCEPTANCE](VISUAL_ACCEPTANCE.md)、[RESULT](RESULT.md)。用户已批准修复方向，本批不另起 UI 设计。

## 1. 目标与边界

以冻结 HTML 为视觉规格，将正式 React 页面还原为审批的布局、信息层级、尺寸、字体、颜色、边框、图表和交互控件样式；接入当前真实数据和现有业务处理函数。

不改后端契约/算法、API字段、SSE、缓存和完整快照切换、运行身份、分页、CAS、幂等回执、导出校验与内存门槛。不引入 UI 框架、依赖、数据服务、新业务组件或类。使用现有组件和原生 HTML 控件，必要展示代码在现有模块内整理。不得复制原型的合成数据、模拟导出、假设置、诊断报告或分析触发逻辑到正式服务。

## 2. 编码范围与顺序

| 步骤 | 现有源码入口（apps/viewer 下） | 修改内容与约束 |
| --- | --- | --- |
| C1 壳与样式 | src/app.tsx、src/styles/base.css | 移植 DEMO 的 sidebar/workspace/topbar/main 布局、CSS 变量、字体、按钮、边框、间距、断点；保留 React 状态生命周期、跳至内容、语义导航和现有 hash 路由，不重建数据协调器 |
| C2 筛选与元信息 | src/app.tsx、src/components/History.tsx、src/features/overview/Overview.tsx | 恢复模型 tabs、appid、结果选择的紧凑一行和底部细信息条。按目录中已有 appid×模型组合选择，不发明无数据组合。历史选择/返回最新继续调用原处理函数；保留新版本待切换和编辑冻结机制 |
| C3 指标与去向 | src/features/overview/Overview.tsx、src/styles/base.css | 六卡三列两行：命中率、请求数、原JSON、模板后、输入重算、输出；H转入Token去向条，与C并列。数字展示紧凑，精确值可查看/复制，不用Number转换完整大整数。null、零分母按原语义处理，不伪造0 |
| C4 移除大面板 | Overview.tsx、app.tsx、src/features/exports/Exports.tsx | 删除独立“当前完整结果”大面板；窗口放结果选择处，文件/质量/配置放底部细信息条，生成时间紧凑显示；组/文件完整范围、run/revision等在详情中可查。导出移至标题操作区，继续复用现有控制器，限制在操作附近说明 |
| C5 图表和辅助页面 | src/features/distributions/Distributions.tsx、src/features/{requests,signals,settings,submissions}/*.tsx、base.css | 恢复三直方图卡片、标题/分位值/众数/工具栏样式；表格、信号、设置及提交的按钮/面板统一到原型样式。保留现有分页、过滤、表单校验、错误恢复和写操作确认，不重写业务逻辑 |
| C6 对照与修复 | tests/component/{app,monitoring}.test.tsx、tests/browser/{shell,monitoring,full-journey,operations}.spec.ts | 更新确因布局变化失效的定位，优先role/label；保留原行为断言。使用现有Playwright截图，不引入截图服务或新测试框架 |

布局变化不成为修改取数策略的理由：保留现有功能路由和按需读取，不为模仿原型长页面而一次性挂载所有表单/请求列表或触发额外请求。导航、页面外观和关联入口按原型还原，已有直接链接继续有效。原型独有的辅助排名视图/诊断样例不借本批新增；缺少后端能力的项不得用假数据填充。

原型控件的“导出样例/演示完成态/新建分析”等文案替换为真实功能语义；提交任务继续遵循现有file_ref方式。新增真实运行状态、网络故障和导出提示使用原型已有的信息条、徽标和详情样式，错误不能为美观而隐藏。以上是数据/功能适配差异，不是重新设计布局。

## 3. “当前完整结果”的处理

默认页面不再有同名独立大面板。时间窗口与生成时间不混淆；组实际范围与整文件实际范围在详情中分别标注，UTC转换北京时间，不补齐虚构两小时整点。run UUID、配置版本、运行参数、文件级质量详细项转入详情入口；简短配置仍区分当前冻结值与下次生效值。质量异常保留可见提示，不能把文件坏行分摊到当前appid。

导出入口位置改变，不改变NDJSON/CSV的作用范围、快照绑定、流式处理、完整性验证及取消行为；浏览器能力限制在打开导出入口或执行操作时可见。

## 4. 验证、门槛和推进

执行 [TESTS](TESTS.md) 的前端回归，再执行 [VISUAL_ACCEPTANCE](VISUAL_ACCEPTANCE.md) 的独立视觉对照。视觉通过不能抵消功能失败，功能通过也不能代替视觉通过。普通缺陷自主修复和复测；涉及契约、业务行为、未约定组件或类、总方案变化或无法解决问题时暂停讨论。

阶段状态：planned → implementing → frontend_verified → awaiting_user_visual_acceptance → closed。closed须代码/前端测试/独立视觉核对通过，且用户明确人工验收通过；尚未通过必须写pending。闭环同时记录后端打包前统一审查pending，不冒称release_ready。

此次纯展示修复不主动重复整套前后端联合review/压力验收。使用真实服务进行只读UI核对是前端验证，不重新命名为联合验收。后端打包前仍统一检查代码、设计和闭环，必要复测由其决定；Docker/镜像/交付包仍需用户单独同意。

## 5. 证据与交接

证据放 `artifacts/validation/viewer/F007/`，按 baseline、functional、visual/reference、visual/actual、visual/comparison 组织；截图/日志不混入源码。记录代码commit或逐文件SHA、原型和S0摘要、依赖锁、构建资源摘要、测试命令、浏览器/viewport/DPR/字体环境、样例身份、实际URL。不得覆盖F006或联合证据。

RESULT提供实际文件清单、设计逐项对照、测试与视觉证据、用户验收原话/日期、未决问题、回退步骤。后端只需从RESULT追到PLAN/TESTS/VISUAL_ACCEPTANCE及源码差异；本轮不自动发送会话消息。

## 6. 回退

编码开始固定前端源码/构建身份和实际工作区差异，沿现有Git约定留可恢复检查点。仅撤销F007自有展示改动及其测试适配，恢复对应前端资源；不重置整个仓库、不覆盖联合修复或他人工作。无缓存schema/API变化，不清空真实缓存、回执或运行数据。若需变更共享服务静态资源，先确认后端服务读取方式与正在使用的版本，保留旧资源并在切换后核对版本；不得用旧4175预览替代8000验收结论。

## 实施增量（2026-10-27）

用户批准进入代码开发，并要求提供HTTP人工验收链接；验收后由后端或用户另建session统一审查与打包。实际结果和身份见RESULT；新session prompt见prompts/sessions/SESSION_FRONTEND_REVIEW_AND_PACKAGING.md。未创建会话或打包。
