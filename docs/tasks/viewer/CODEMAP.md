# 当前前端源码地图（2026-10-28，0.1.0-f007）

apps/viewer为正式实现，旧HTML为视觉参考。设计及验收入口见ENTRY。

| 模块 | 固定入口 | 相关测试 |
| --- | --- | --- |
| DTO/边界/整数/时间 | scripts/generate-contract.mjs；src/api/{client,validate,generated}、src/domain/{identity,integer,time} | contract/client/domain.test.ts |
| 通知/目录/完整切换 | src/state/{publication-client,catalog,snapshot-coordinator,view-store} | publication/coordinator.test.ts；full-journey.spec.ts |
| 内存/持久快照 | src/storage/{db,snapshot-cache}；src/api/query-cache；components/useRead | cache.spec.ts、coordinator.test.ts |
| 概览/直方图/明细/历史/信号 | src/features/{overview,distributions,requests,signals}；components/History；src/app.tsx | monitoring组件与browser、performance、integration |
| 回执/提交/设置/规则 | src/state/{receipt-store,submission-coordinator}；features/{submissions,settings} | receipts.test.ts、operations.spec.ts、integration |
| 导出 | features/exports/{Exports,export-controller}；domain/export-protocol；workers/export-validator | export.test.ts；export/export-fixture.spec.ts |
| 统一验证/恢复 | tests/browser；scripts/check-build.mjs；F006/rollback | F006 TESTS及source-manifest |

下方历史条目用于追溯，不再描述当前实现状态。

---

# 前端展示代码地图

当前没有本任务运行实现或固定源码接入。不要把预留目录视为已有能力。

任务开展后登记直接相关的源码路径、关键符号、配置、测试、共享依赖及版本，形成具体阅读范围。外部源码须指向固定身份，不能列“阅读整个仓库”。维护范围和资料入口见 [ENTRY](ENTRY.md)。


## 监控设计评审 DEMO（2026-10-26）

由用户明确要求提前提供，用于检查监控 v1.0-rc2；不是正式 apps/viewer 实现。所有产物均在项目内。

| 入口 | 用途 |
| --- | --- |
| [tokenscope-monitoring-demo.html](../../../artifacts/prototypes/monitoring-v1/tokenscope-monitoring-demo.html) | 自包含离线成品；三模型默认 128/1536/32，模型/租户筛选、指标、长度直方图（含箱内请求）及辅助降序曲线、请求详情、下次配置、阈值和触发示例 |
| [冻结基线](../../../artifacts/prototypes/monitoring-v1/tokenscope-monitoring-baseline-v1.html) / [清单](../../../artifacts/prototypes/monitoring-v1/baseline-manifest.json) | 用户指定的前端设计起点，保存版本与 SHA256；全套前端设计尚未完成 |
| [monitoring-demo.template.html](../../../artifacts/prototypes/monitoring-v1/monitoring-demo.template.html) | 可维护界面源码；render/drawChart、openSettings、openThreshold、openImport；不执行真实编码/缓存仿真 |
| [build_demo.py](../../../artifacts/prototypes/monitoring-v1/build_demo.py) | 固定随机种子生成单峰/双峰/长尾合成计数、预计算分箱/统计和完整 HTML；不是生产计算实现 |
| [demo-fixtures.json](../../../artifacts/prototypes/monitoring-v1/demo-fixtures.json) | 三模型，每模型 540 条有效请求、三个示例租户；所有值人工合成 |
| [check_demo.cjs](../../../artifacts/prototypes/monitoring-v1/check_demo.cjs) | 使用已有 Edge/Playwright 检查筛选、曲线、请求、参数不可追改、阈值、导入预览、导出和移动布局 |
| [ui-validation.json](../../../artifacts/prototypes/monitoring-v1/ui-validation.json) / [fixture-validation.json](../../../artifacts/prototypes/monitoring-v1/fixture-validation.json) | 浏览器交互通过，无 JS 错误/外部网络请求；1620 条合成记录、81 组三宽度直方图的算术/排名/分位数、尾部覆盖和众数通过；不构成真实编码/缓存/性能验证 |

导入操作只预览文件名与提交信息，不读取或上传 CSV。配置/规则只保存在本页内存，刷新恢复默认。页面只展示预计算合成结果；阈值比较是明确标记的交互预览。实际后端接入和前端开发 batch 另行设计。

2026-10-26 分布澄清修订：默认长度直方图，新增 [distribution-charts.js](../../../artifacts/prototypes/monitoring-v1/distribution-charts.js) 渲染预计算分箱：默认 5K，可选 1K/2K；0–200K 有限箱加 ≥200K 开放尾桶，所有并列众数高亮并显示各箱数量/占比；P50/P80/P90 只在图外显示数值。条数/占比可切换，原降序图作为辅助。合成 demo-rag 的 GLM 模板后输入集中约 66K；不把合成形状归因为真实 Agent 行为。

## 分析报告展示参考（2026-10-26）

[用户投递 prefixlens_demo.html](../../../evidence/source_drops/prefixlens-ui-demo/prefixlens_demo.html)：15,018 字节，SHA256 `324f2bc93880e77bb6fb6bb159be2478bcc0995d69a250272047b79182487284`。诊断结构位于开头至第 106 行附近；后半 Traffic Replay 不在本次范围。文件为无配套 CSS/JS 的页面片段；仅读取，原件未改，不作为分析后端已实现或交互已验证的证据。采用提案见 DESIGN 的“分析报告展示 v0.1”。

## 当前业务报告 HTML（report-ui-v2-business）

| 文件 | 职责 |
| --- | --- |
| [report-ui.js](../../../artifacts/prototypes/monitoring-v1/report-ui.js) | appid/model 范围、类别路由、sortedFindings 排序、renderReports/renderSolutionCards 展示 |
| [report-evidence.js](../../../artifacts/prototypes/monitoring-v1/report-evidence.js) | findingHtml 渲染断点/来源/事件/对比、建议与收益 |
| [report-ui.css](../../../artifacts/prototypes/monitoring-v1/report-ui.css) | 业务卡片、证据和移动布局 |
| [report-fixtures.json](../../../artifacts/prototypes/monitoring-v1/report-fixtures.json) | 两个 appid 的独立构造建议，不是生产 Schema |
| [check_business_reports.cjs](../../../artifacts/prototypes/monitoring-v1/check_business_reports.cjs) / [验证](../../../artifacts/prototypes/monitoring-v1/report-v2-validation.json) | 范围隔离、排序、详情、移动端、路由、原监控导航及离线检查 |
| [v2 冻结 HTML](../../../artifacts/prototypes/monitoring-v1/tokenscope-monitoring-with-reports-v2.html) / [清单](../../../artifacts/prototypes/monitoring-v1/report-v2-manifest.json) | 本轮结果与摘要 |
| [v1 冻结 HTML](../../../artifacts/prototypes/monitoring-v1/tokenscope-monitoring-with-reports-v1.html) / [清单](../../../artifacts/prototypes/monitoring-v1/report-v1-manifest.json) | 历史报告列表；check_reports.cjs 和 report-ui-validation.json 仅对应此旧版 |

build_demo.py 将报告源码和样例内联进 HTML，无外部资源依赖。正式实现未迁移至 apps/viewer；下一阶段先共同设计前后端交互。原始证据和冻结监控基线未改。

## 监控交互设计 v0.1（2026-10-27）

[方案](MONITORING_INTERACTION_V1.md)、[后端需求差异](BACKEND_REQUIREMENTS_V1.md)、[合成通知样例](examples/monitoring-publication.example.json)、[源码读取摘要](../../../artifacts/reviews/viewer-interaction-v1/source-observations.json)。对照 src/tokenscope/api/app.py 的现有路由、MonitoringService.metrics/histograms/lengths、ControlStore.complete、statistics.aggregate 和 pipeline 封存流程；本轮只读，未执行后端测试。

## 前端v1.0待审批工程方案

[最终设计](MONITORING_INTERACTION_V1.md)第3节规定apps/viewer内api/domain/state/storage/features/workers及tests；目前这些是拟建入口，apps/viewer尚无业务实现。精确路径和符号随各batch闭环登记。[F001–F006](batches/README.md)均有五份计划/记录入口，[统一验收](ACCEPTANCE_V1.md)按V01–V15映射后端A/J。

## F001 实现入口（未闭环，2026-10-27）

- apps/viewer/package.json、package-lock.json、vite.config.ts、tsconfig.json：固定本地工程与根路径代理。
- scripts/generate-contract.mjs → src/api/generated/{types.ts,schema.json}、src/api/contract-lock.json：验证S0摘要，生成67个DTO。
- src/api/{types,validate,client}.ts：Schema校验、scope校验、UTF8/错误/根URL封装；cursor语义待I03修复。
- src/domain/{integer,time,identity}.ts：BigInt精确值、UTC原串/北京时间、范围键。
- src/{app,main}.tsx、src/styles/base.css：无模拟指标的hash路由工程壳。
- tests/unit、tests/component、tests/browser：F001计划内边界与工程检查；当前100通过1失败，浏览器尚未执行。

实际命令和失败证据见batches/F001/TESTS.md与ISSUES.md。后续缓存/SSE/图表/配置/导出尚未实现。

2026-10-27 F001闭环更新：cursor语义已修复；102项单元组件、类型/lint/构建、check-build.mjs与真实Edge浏览器全部通过；生成原Schema不变。具体源码摘要/版本/浏览器差异见F001 RESULT。后续业务尚未实现。

2026-10-27：F002已closed（115项单元组件+4项真实浏览器缓存检查、类型/lint/build）；自动进入F003监控展示。F002代码入口src/state/{publication-client,catalog,snapshot-coordinator,view-store}、src/storage/{db,snapshot-cache}、src/api/query-cache；证据与限制见F002 RESULT/TESTS。

2026-10-27：F003 closed，120项回归与真实Edge合成展示检查通过；代码features/{overview,distributions,requests,signals}、components/{useRead,History}。源摘要/失败修复/视觉/网络见F003 RESULT。已自主进入F004提交恢复与配置；后端契约未变。

2026-10-27：F004 closed，128项回归+真实Edge2条恢复/CAS综合流程通过。代码state/{receipt-store,submission-coordinator}、features/{submissions,settings}；固定S0不变。进入F005有界导出；完整前端完成后才提交用户审批。

## F007计划入口（尚未编码）

审批原型固定为artifacts/prototypes/monitoring-v1/tokenscope-monitoring-demo.html；从配色参考升级为视觉规格。计划修改现有app.tsx、styles/base.css、components/History.tsx、features内展示组件，逐文件范围见[batches/F007/PLAN.md](../../../achieve/2026-10-28/docs/tasks/viewer/batches/F007/PLAN.md)。测试复用现有component/browser框架；实际新增/修改符号和证据待实施登记，不提前声称已实现。

## F007实际代码（0.1.0-f007）

app.tsx：sidebar/topbar/filter-meta/标题导出菜单；Overview.tsx：compact、六卡、精确值与去向条；Distributions.tsx：图表坐标/网格/分位值/众数位置；styles/base.css：审批原型CSS与React适配。未新建业务组件/类，数据层未变。测试：component/monitoring、browser/{monitoring,full-journey,visual}.spec.ts。视觉/真实只读核对使用visual.spec.ts，具体命令和证据见F007 TESTS。生成审查prompt在prompts/sessions/SESSION_FRONTEND_REVIEW_AND_PACKAGING.md。
