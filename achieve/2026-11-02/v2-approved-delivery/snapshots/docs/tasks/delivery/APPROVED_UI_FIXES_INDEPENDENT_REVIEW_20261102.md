# UIR修复候选c2独立复审：鼠标读数仍待修复

2026-11-02。审查角色：镜像打包与审查／完整服务总负责；本轮环境实际ID `01a1800e-80b4-7400-a78b-a84f5b6e888d`。承接[前轮两项问题](APPROVED_UI_INDEPENDENT_REVIEW_20261102.md)与[前端补充交接](../viewer/monitoring-v2/APPROVED_UI_REVIEW_FIX_HANDOFF_20261102.md)。

**候选整体未通过。UIR-02“跳至内容”及附带排行恢复路由修复通过；UIR-01坐标、颜色、键盘精确读数和分段显示已补齐，但宽窗口鼠标会选错请求，不能关闭。** 本线没有修改业务源码，未提交、合并、push、Docker构建或交付打包，不代签用户视觉认可。

## 1. 当前候选和独立环境

- 候选：`viewer-approved-ui-review-fixes-20261102-c2`。HEAD `9f2a3e60394327e4e6bdc41bd688497ddef21dd7` 加原c5及本轮6文件未提交增量，不能由HEAD单独代表。
- 交接 SHA256：`816173b4720b918adfc178522f0ee3a2c12f20dd0e4eb0d5a55f37d022c48ae9`。前端manifest SHA256：`839f185872c5f2437a7a9a68e82e8da8d6de40b2bfb436e4bb7f89b298238a77`。
- 主清单1343条：1340条与清单一致，3份前端入口／记忆在清单生成后更新，已逐项匹配前端 `final-verification.json` 的收尾摘要。差异为 `docs/tasks/viewer/analysis/ENTRY.md`、`docs/tasks/viewer/monitoring-v2/ENTRY.md`、`memory/tasks/viewer-analysis.md`；不是业务源码漂移。分别保存[原始差异](../../../artifacts/reviews/approved-ui-fixes-independent-20261102/manifest-initial-differences.json)和[本线开始身份](../../../artifacts/reviews/approved-ui-fixes-independent-20261102/identity-start.json)，不笼统宣称1343条全匹配原manifest。
- 本轮6文件增量：Distributions.tsx、Requests.tsx、UserMonitor.tsx、AppShell.tsx、ui-review-fixes.spec.ts、ui-review-fixes.test.tsx，逐一匹配交接SHA。核对当前源码及差异，并保存本线源码快照；后端、契约、锁和模型资产没有因本线审查更改。
- 核实前端候选PID2899497完整argv/cwd，TERM正常退出；WSL及Windows相关端口释放后再启动独立环境。未保留旧候选另换端口并行验收。
- 本线证据根：`artifacts/reviews/approved-ui-fixes-independent-20261102`。新空state、独立inputs/config、真实worker新生成结果；WSL Node22.22.2独立build，Windows Chrome新context。新实例 `fe254e4a-b6f6-4796-82e7-0f9e244b84ad`，同源4191，原始PID2909528；没有复用前端state。
- 真实后端合成覆盖三模型15基础范围、29APP搜索、ready/history/partial诊断、用户来源和1005条分段运行。模型模式设置仅针对本线合成数据，不代表生产配置批准。
- 同版本重启前PID2909528正常退出且4191释放；新PID2958013恢复同一state完成检查后也正常退出。结束时Windows/WSL4191、4193、8016、4175及本项目验收端口关闭，无保留预览；state/输入/日志仍在。

独立build、前端交回及实际HTTP四资源完全一致：

| 文件 | SHA256 |
| --- | --- |
| index.html | `9515e3cf640e96d63aa4664625d29f36c4b8457e6428e4a82328362bc9489942` |
| assets/index-CHXcFvtG.js | `bc9852a916576059fde7a4d04dee187d0f9430319e31551b676437c0316f623d` |
| assets/export-validator-rZ4O78aZ.js | `e52838c80a214d465b29b1e6049fabe887e80d8077fc5ce121061c8f109e9d41` |
| assets/index-BxqENh7v.css | `7de15a1ce92dc92d4d93a96c70425c1ea22663c5c4653c98cb4d9122ef0254a5` |

[冷启动身份](../../../artifacts/reviews/approved-ui-fixes-independent-20261102/cold-identity.json) · [停止前序候选](../../../artifacts/reviews/approved-ui-fixes-independent-20261102/old-candidate-stopped.json) · [最终清理](../../../artifacts/reviews/approved-ui-fixes-independent-20261102/cleanup-final.json)。

## 2. 唯一未关闭项：UIR-01宽窗口鼠标读数错位（P2）

### 用户主页面直接复现

同候选环境下，用1920×1080 viewport打开：

`/#/users?run=ur-37edc04cc5ab4d648b839fabc148c78b&appid=synthetic-app-1`

选择“降序明细 · 辅助视图”，把鼠标移到“输入重算长度”的第一个真实圆点。

| 对象 | 应显示 | 实际显示 |
| --- | --- | --- |
| 选中请求 | 排名#1，synthetic-0，源记录1 | 排名#4，synthetic-3，源记录4 |
| 输入重算Token | 418 | **162** |
| 原始JSON／模板后输入 | 同样应为#1 | 同样错选#4；这两项值重复，单看Token数会漏报 |

[主页面JSON](../../../artifacts/reviews/approved-ui-fixes-independent-20261102/user-pointer-1920.json)保存URL、真实圆点的屏幕坐标／title与实际读数；[主页面截图](../../../artifacts/reviews/approved-ui-fixes-independent-20261102/user-pointer-1920.png)。没有拦截替换数据或修改DOM来制造失败。

![1920宽：指向第一点却选中第四条，重算418显示为162](../../../artifacts/reviews/approved-ui-fixes-independent-20261102/user-pointer-1920.png)

### 独立对照和源码原因

另对同一组件的有效S0分布深链验证：

`/#/distributions?run=c382d269-879a-4d04-837a-7c06680f9e8c&appid=synthetic-app-1&model=GLM-5.2`

首点220,072 Token被读成第二点200,072；末点92被读成倒数第二点535。[36项坐标探针](../../../artifacts/reviews/approved-ui-fixes-independent-20261102/pointer-regression.json)覆盖1440、390、1920宽、三指标首中尾点及请求明细辅助图：30项匹配，6项失败，失败均为1920宽三图首尾点；另有上面的用户主页面3图首点失败。无脚本错误或写请求。错误计数不混入“81业务用例通过”。

根因在 [Requests.tsx第49行](../../../apps/viewer/src/features/requests/Requests.tsx#L49) 新增 `onPointerMove`：

```tsx
(event.clientX - bounds.left) * 400 / bounds.width
```

代码把整个SVG元素边框当成400宽viewBox。现有CSS固定图高220px，而1920宽下每图SVG元素为504×220，viewBox为400×220，默认等比居中渲染产生左右各52px留白。实际绘图坐标包含这段平移，鼠标换算却没有。

实际观测：SVG左边258、宽504，绘图坐标原点屏幕x=310，第一点viewBox x=51对应屏幕361。当前算法将其换成约81.75，12点时选为第二条、30点时选为第四条。由此可以解释错误，不归因于后端、缓存或整数精度。1440/390宽的该探针匹配，不能证明所有正常桌面宽度都正确。该问题来自本轮尚未提交的鼠标读取实现，没有对应新Git提交。

**必要修复：** 将客户端指针转换到SVG实际用户坐标系，再定位本段最近点；可用实际screen CTM逆变换或等价方案。处理缩放、留白、滚动、resize及转换不可用边界。不能通过固定偏移、拉伸图形、限制窗口宽度或移除鼠标能力绕过问题，也不改批准布局。

**必要复测：** 三指标首／中／尾点；1440/390/1920宽及resize后；1005条首段／次段和请求明细辅助图。期望应来自实际渲染圆点对应的API行，必须同时比较排名、hash、源记录与精确Token，不能只比可能相等的数值，也不能复用实现坐标公式生成测试期望。现有键盘、分段、空/0/单点/大整数/503重读、取消和导出断言保留。

可直接交前端的[本项修复prompt](../../../prompts/sessions/FRONTEND_UIR01_POINTER_FIX_20261102.md)已整理；本线未代改源码。

## 3. 已通过的修复与18项保持

| 范围 | 本线结论与证据 |
| --- | --- |
| UIR-01原轴说明／绘图 | Token纵轴、请求排名横轴、网格／刻度、灰蓝／蓝／青恢复；直方图／降序文案正确切换。1440与390图表已人工查看，不再虚称“下表” |
| UIR-01键盘／分页 | 三指标真实API排序与左右键精确值匹配；1005条首段1–1000、次段1001–1005及返回通过；0/空/单点、大整数、错误重读通过。当前鼠标失败不否定上述已验证范围 |
| UIR-02 | 公共skip阻止默认hash跳转，主内容获焦点，URL/history长度与报告卡片保持；用户、排行、MA、分析、设置、overview、requests两宽度测试通过，可关闭 |
| 附带排行恢复 | `UserMonitor.follow` 按当前实际hash保留users/ranking，设置／MA等进入排行及前进后退通过；run/appid恢复未被改写。不是仅展示变化，已做行为回归 |
| A01–A04、D04 | 同一四入口、顺序／激活态、SVG／208px／分组、设置兼容流程及窄屏完整入口保持；skip修复补齐键盘路径 |
| U01/U02/U04 | 六卡、Token去向、TTFT缺参/情景、三图、真实运行/历史/已知ID、信号/导出/明细保持；15范围精确数值、分位数、1029箱以及导出取消和校验通过 |
| U03 | **仅鼠标读数仍未闭环**；其他图表恢复如上 |
| R01/R02 | 20条排行、300ms防抖、字面量/大小写/上下界、固定revision与显式范围保持，真实搜索和历史恢复通过 |
| M01–M04 | 本轮未改MA源码；全部UUID、三摘要、配对条、真实规格/质量入口、蓝青趋势、刻度/均值/12桶/0与null、页签/分布保持，MA回归与对照截图通过 |
| D01–D03 | 本轮未改Reports/Evidence；UI-04、通知/cache/固定历史/partial保护、L4/L5各一卡≤3例与去重返回、T2–T4保持；不恢复T1。来源FS-01精确run通过 |

[40组视觉捕获索引](../../../artifacts/reviews/approved-ui-fixes-independent-20261102/visual-final/summary.json)：同Chrome1440×1000／390×844，另有三图局部、实际次段及1920问题截图。无pageerror、横向溢出或非GET写请求。数据、合法历史状态与批准静态样例不同，不机械比较整图像素或数字相等；部分分析卡片截图保留既有懒加载提示，证据展开由浏览器用例另测。

[1440三图](../../../artifacts/reviews/approved-ui-fixes-independent-20261102/visual-final/rank-detail-1440.png) · [390三图](../../../artifacts/reviews/approved-ui-fixes-independent-20261102/visual-final/rank-detail-390.png) · [L5窄屏](../../../artifacts/reviews/approved-ui-fixes-independent-20261102/visual-final/candidate-L5-390.png) · [设置四入口](../../../artifacts/reviews/approved-ui-fixes-independent-20261102/visual-final/candidate-settings-1440.png)。这些是工程复审观察，不是用户视觉签字。

## 4. 本线实际测试记录

| 检查 | 结果 | 原始记录 |
| --- | --- | --- |
| typecheck／lint／WSL build | 全部退出0，4资源与HTTP一致 | [checks-linux.json](../../../artifacts/reviews/approved-ui-fixes-independent-20261102/checks-linux.json)、[build.log](../../../artifacts/reviews/approved-ui-fixes-independent-20261102/build.log) |
| 单元／组件 | 25文件222项通过 | [unit-linux.log](../../../artifacts/reviews/approved-ui-fixes-independent-20261102/unit-linux.log) |
| 监控／分析／来源／联合 | 42＋18＋3＋8通过 | [monitoring.log](../../../artifacts/reviews/approved-ui-fixes-independent-20261102/monitoring.log)、[analysis.log](../../../artifacts/reviews/approved-ui-fixes-independent-20261102/analysis.log)、[source.log](../../../artifacts/reviews/approved-ui-fixes-independent-20261102/source.log)、[joint.log](../../../artifacts/reviews/approved-ui-fixes-independent-20261102/joint.log) |
| 新增UIR用例 | 10通过，合计81个不同浏览器用例 | [fixes.log](../../../artifacts/reviews/approved-ui-fixes-independent-20261102/fixes.log) |
| 独立鼠标回归 | 36检查中6失败；主页面另3失败 | 第2节JSON、截图、脚本；不关闭问题 |
| 真实API数据 | 15范围、29APP搜索、重新生成诊断、1005请求 | [base-acceptance.json](../../../artifacts/reviews/approved-ui-fixes-independent-20261102/base-acceptance.json)、[搜索oracle](../../../artifacts/reviews/approved-ui-fixes-independent-20261102/search/real-search-api.json)、[诊断](../../../artifacts/reviews/approved-ui-fixes-independent-20261102/fixture-config/actual-http.json)、[1005运行](../../../artifacts/reviews/approved-ui-fixes-independent-20261102/rank-segment-fixture.json) |
| c5固定历史run竞争保持 | 真实snapshot延迟1200ms，4次目录回调后及刷新仍保持旧run；无写请求 | [history-race.json](../../../artifacts/reviews/approved-ui-fixes-independent-20261102/history-race.json) |
| 同版本重启 | 120地址SHA一致，实例不变；四个控制库业务表记录/摘要保持，GET未新增业务 | [restart-result.json](../../../artifacts/reviews/approved-ui-fixes-independent-20261102/restart-result.json) |
| 重启后新context | 来源3＋键盘/排行/1005分段4通过，共7项重复验证，不累计到81 | [restart-source.log](../../../artifacts/reviews/approved-ui-fixes-independent-20261102/restart-source.log)、[restart-fixes.log](../../../artifacts/reviews/approved-ui-fixes-independent-20261102/restart-fixes.log) |

负向、网络异常和大整数用例包含受控客户端响应注入，真实基础数据／诊断／1005分段及鼠标问题不依赖网络替身；分别记录，不能统称所有用例均无替身。没有把业务表不变写成整个SQLite字节恒定，也不代表15万规模性能、生产TTFT校准、Docker或华为现场通过。

本轮设置错误保留：初次身份检查发现上述3份文档收尾差异后另核对；旧c5的488清单不包含当时未跟踪AppShell，分别对其原文快照及当前6项增量核对；浏览器测试副本初次少改一层docs import导致发现阶段失败，无业务断言执行，保留 `monitoring-import-setup-failure.*`，修正本线artifact路径后42项通过；旧group链接已在执行前改为本线新生成task/group，原行与适配说明保留。没有删用例、跳过断言或更改业务代码换通过。既有大chunk构建警告保留。

## 5. 保全与后续

当前源码／锁／契约／模型、6项增量、两批准HTML、两份前端交接、15个WSL冻结交付文件及其他session原有未提交修改均保留；HEAD不变。只新增本线复审证据/本文/单项prompt并更新自己的入口、协作状态和记忆。最终[保全记录](../../../artifacts/reviews/approved-ui-fixes-independent-20261102/preservation-final.json)与[证据清单](../../../artifacts/reviews/approved-ui-fixes-independent-20261102/evidence-manifest.json)为恢复入口，原审计/c5/c2失败与自测证据不覆盖。

下一步按单项prompt修复鼠标坐标换算，再交新候选独立复审。不得再设计页面，已关闭的UIR-02与其他业务保持。前端和审查线每轮都执行先停旧服务、确认退出/端口释放、新空state/new dist/新浏览器冷启动。只在明确复现同版本问题时依 `server-restarted.json` 的argv/env/cwd使用本线保留state；当前服务已关闭，不直接照抄旧PID进行停止操作。

**本轮不通过整体候选，不提交／push／打包，不代用户签字。** 修复后的工程通过也不自动取得Git发布、镜像或交付打包授权。
