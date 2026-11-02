> 归档：本文件保存历史过程，不再是执行入口。2026-11-02用户认可V2可交付，UIR-03留V3、不作V2阻断。现场只用真实数据，分两次用户验收，单份Markdown回传。当前见[交付入口](../../../../../../../docs/tasks/delivery/ENTRY.md)；[逐字节原始快照](../../../../snapshots/docs/tasks/viewer/monitoring-v2/APPROVED_UI_RESTORATION_HANDOFF_20261102.md)。

# 已批准 UI 恢复：统一交接（2026-11-02）

本轮完成前端修复与自测，交回“镜像打包与审查”session `01a1800e-80b4-7400-a78b-a84f5b6e888d` 独立复审。**不是用户视觉验收通过，也不是发布版本。暂不提交、合并、push、构建 Docker 或生成交付包。**

执行 session：`01a19111-344a-75c1-84e0-14db8be08f4f`（环境实际 ID）。本轮职责为已授权的四入口/UI-02/UI-04恢复；优先级 P0。后端能力及契约不变。依据：[执行 prompt](../../../../prompts/sessions/FRONTEND_APPROVED_UI_RESTORATION_20261102.md)、[18项原审计](../../delivery/VISUAL_AUDIT_20261102.md)、[监控交互](../../../../../../../docs/tasks/viewer/monitoring-v2/INTERACTION_V2.md)、[分析视觉基线](../../../../../../../docs/tasks/viewer/analysis/VISUAL_BASELINE.md)。原审计证据未覆盖。

## 1. 候选与文件身份

- 候选：`viewer-approved-ui-restoration-20261102-c5`，基于 HEAD `9f2a3e60394327e4e6bdc41bd688497ddef21dd7` 加本交接所列未提交修改；不能以 package.json 的旧版本号识别候选。
- 唯一预览：[http://localhost:4191/#/users](http://localhost:4191/#/users)，四入口均在该同源；异常可选 synthetic-orders。当前 PID `2680003`，服务身份 `1f9e4b17-7676-41a2-8206-0e066e2e12f7`。
- 前端 `/home/zhangxiyue/TokenScope/artifacts/validation/viewer/approved-ui-restoration-20261102/dist-5`；后端为同工作区源码 CLI，独立 `state-5`。不是镜像、也没有旧镜像挂新 dist。
- 开工488项文件摘要、原 dirty 清单：[identity-start.json](../../../../../../../artifacts/validation/viewer/approved-ui-restoration-20261102/identity-start.json)。最终逐文件源码/样式/测试/锁/S0/模型摘要和实际HTTP资源：[identity-final.json](../../../../../../../artifacts/validation/viewer/approved-ui-restoration-20261102/identity-final.json)。本轮源码/测试22文件见下表。
- 后端、锁、契约和资产301项开工一致检查：[preservation-final.json](../../../../../../../artifacts/validation/viewer/approved-ui-restoration-20261102/preservation-final.json)；不修改算法、生成契约、SourceLink 或模型资产。别人原有未提交修改保留；SESSIONS 与 delivery 记忆被审查方并发更新，明确记为归口修改，不宣称字节未变。
- UI-02 SHA256 `799786cb3ee52e0931d2482211f82e594ab0f33ad57969232a7ea2ec06d2eaea`；UI-04 `779e6665985fe02e6df9e7d0483ef8111a16a49c2b61fdb27aacbef58d624f5f`，批准 HTML 未修改。

| 本轮文件 | SHA256 |
| --- | --- |
| [apps/viewer/src/app.tsx](../../../../../../../apps/viewer/src/app.tsx) | `82dbc7bb7470aba351e62544a4be061f5d96c786ceb47d1a6b48ff34d405b769` |
| [apps/viewer/src/features/analysis/AnalysisApp.tsx](../../../../../../../apps/viewer/src/features/analysis/AnalysisApp.tsx) | `4de7ac5ec1e5078f3654bfb14e87318598a1e017e6421116dbf15aaf74cab675` |
| [apps/viewer/src/features/distributions/Distributions.tsx](../../../../../../../apps/viewer/src/features/distributions/Distributions.tsx) | `616ad7ac0fe7f1155d2dac59fdb3d90bbd12cd9fd29c5ef28d57b9c0eefd8af8` |
| [apps/viewer/src/features/requests/Requests.tsx](../../../../../../../apps/viewer/src/features/requests/Requests.tsx) | `15e720bf2e34a193125b14ff67d3d75abe82770f405f4e609d104b9f424ddeee` |
| [apps/viewer/src/features/signals/Signals.tsx](../../../../../../../apps/viewer/src/features/signals/Signals.tsx) | `4ac68b84a53d05994b3bc4ed4f2df0d3a5e7ab94bea74161740c887c8f8cbaa8` |
| [apps/viewer/src/features/v2/MACharts.tsx](../../../../../../../apps/viewer/src/features/v2/MACharts.tsx) | `920fb06eae3075dd0f17fd6491d41270d4940a7a1ec2d40433f4594295108c86` |
| [apps/viewer/src/features/v2/MAMonitor.tsx](../../../../../../../apps/viewer/src/features/v2/MAMonitor.tsx) | `c6ae5ac1df69ee0c9387961c779067b6fe407976ed2a271637128ee364e97f05` |
| [apps/viewer/src/features/v2/UserMonitor.tsx](../../../../../../../apps/viewer/src/features/v2/UserMonitor.tsx) | `247d8eaa79d9875fde97b85987f03c7618a8bbdcf66ad4b5ef40a15cb190dfdf` |
| [apps/viewer/src/features/v2/V2App.tsx](../../../../../../../apps/viewer/src/features/v2/V2App.tsx) | `0441c0bf71939b5a1d72fe0af9ba11aa5b8b6e2635a98437e3a50a970df8b7da` |
| [apps/viewer/src/state/snapshot-coordinator.ts](../../../../../../../apps/viewer/src/state/snapshot-coordinator.ts) | `c12cfdfbcc74c9f6a3d8383f251653cb872eb65169993a0cb89e8527e9174087` |
| [apps/viewer/tests/browser/analysis.spec.ts](../../../../../../../apps/viewer/tests/browser/analysis.spec.ts) | `55e0c44cc5efbc83a0452a69e1e31aa6b73d166a9f6da9672bd9e8b60fdf74f1` |
| [apps/viewer/tests/browser/joint.spec.ts](../../../../../../../apps/viewer/tests/browser/joint.spec.ts) | `10dee7135dcfd7776bb2df89efd5078475b0e64b0fd915a030a51b8a11faad8f` |
| [apps/viewer/tests/browser/monitoring.spec.ts](../../../../../../../apps/viewer/tests/browser/monitoring.spec.ts) | `141e9b5457c720f2677ce11a45649859280fe08aeb4bb77711e1336f58c222a2` |
| [apps/viewer/tests/browser/v2-acceptance.spec.ts](../../../../../../../apps/viewer/tests/browser/v2-acceptance.spec.ts) | `875f08f0caaeb071a8bd8b165b863921c31b93e1c8760d88ce0b482666159d52` |
| [apps/viewer/tests/browser/v2-ma.spec.ts](../../../../../../../apps/viewer/tests/browser/v2-ma.spec.ts) | `27f87b5cc36d12b9c88df9c4a76b7f14cffd9024c36178a9f5cb7f392c1f4a02` |
| [apps/viewer/tests/browser/v2-review-fixes.spec.ts](../../../../../../../apps/viewer/tests/browser/v2-review-fixes.spec.ts) | `0488f39f8d5f12b335be75e8bedf9be07e32ad0a4c8134a7ecc5b9d26acb3df5` |
| [apps/viewer/tests/component/monitoring.test.tsx](../../../../../../../apps/viewer/tests/component/monitoring.test.tsx) | `138ac3efeccce4d438b84a4114a0f3b295445ec456cbda6c26207b332db49c0b` |
| [apps/viewer/tests/unit/coordinator.test.ts](../../../../../../../apps/viewer/tests/unit/coordinator.test.ts) | `45a9746f39767f046486181bdc6d3bd8e57371d1917df0f2b09ac97686df697d` |
| [apps/viewer/src/components/AppShell.tsx](../../../../../../../apps/viewer/src/components/AppShell.tsx) | `a536e9cc69d7b7733a81f7d58205a77e47781cc2ac199a9f12675ebe45268d47` |
| [apps/viewer/src/components/app-shell.css](../../../../../../../apps/viewer/src/components/app-shell.css) | `610f418857bd39783cb297cdfeb5f82595f1df1ee4485ec9bade534207583f20` |
| [apps/viewer/tests/browser/approved-ui-restoration.spec.ts](../../../../../../../apps/viewer/tests/browser/approved-ui-restoration.spec.ts) | `015871669f12d17e1a5f80749f74976998223e28c2e2653f2f019961af3ac87f` |
| [apps/viewer/tests/component/app-shell.test.tsx](../../../../../../../apps/viewer/tests/component/app-shell.test.tsx) | `415c13c7801c7b740ff7b0094029a1d1f99e8c21b20d54f88dec3d2075905577` |

| 实际 dist 与 HTTP 同摘要资源 | SHA256 |
| --- | --- |
| index.html | `2c41b7bff760f46d86c54ae57174d86068db4e34b45efba304ca7c555edfa0e4` |
| assets/index-CEgv_duI.js | `663658cdfbf37d0b877fbf444710c0e8bd3025b9240d4b9f1292ffb869287f19` |
| assets/export-validator-rZ4O78aZ.js | `e52838c80a214d465b29b1e6049fabe887e80d8077fc5ce121061c8f109e9d41` |
| assets/index-BxqENh7v.css | `7de15a1ce92dc92d4d93a96c70425c1ea22663c5c4653c98cb4d9122ef0254a5` |

## 2. 18项逐项处理

所有行均为本轮自测结论；未决列统一为“待独立复审及用户视觉判断”，没有自行豁免。文件链接带入口行号；长行组件的全部操作在对应文件内。证据文件名均相对本轮证据目录。

| 编号 | 处理 | 原问题 | 修复或保持依据 | 源码入口 | 复现/验证步骤 | 通过证据 |
| --- | --- | --- | --- | --- | --- | --- |
| A01 | 修复 | 设置落入整套 V1 | 统一 AppShell 包裹 S0 子流程；设置、请求、信号、提交和导出仍可用 | [src/app.tsx:35](../../../../../../../apps/viewer/src/app.tsx#L35) | users→运行设置→返回；旧 settings/requests/overview 深链 | candidate5.log；joint5.log |
| A02 | 修复 | 三套五/六项主导航 | 所有模块同一四入口及顺序；功能操作留在正文 | [src/components/AppShell.tsx:3](../../../../../../../apps/viewer/src/components/AppShell.tsx#L3) | 四业务页直接访问、互切、刷新、前后退 | candidate5.log；visual-checks-5.json |
| A03 | 修复 | 字符图标、间距和固定顶栏标题 | SVG、208px侧栏、分组与实际模块标题；桌面四入口几何与 UI-02 相同 | [src/components/app-shell.css:1](../../../../../../../apps/viewer/src/components/app-shell.css#L1) | 1440宽核对 x18、y111/159/207/306、172×43 | visual-checks-5.json |
| A04 | 修复 | 分析窄屏缺排行入口 | 统一窄屏四入口、顺序和激活态；沿既有移动导航方式 | [src/components/AppShell.tsx:10](../../../../../../../apps/viewer/src/components/AppShell.tsx#L10) | 390宽逐路由、刷新、返回；导航高度<100px | candidate5.log |
| U01 | 保持 | 主要结构已一致 | 六卡3×2、Token去向、TTFT三栏、三张分布保留；数据不改写 | [src/features/v2/UserMonitor.tsx:1](../../../../../../../apps/viewer/src/features/v2/UserMonitor.tsx#L1) | 真实15范围逐卡数值、1029箱和分位数 | joint5.log；base-acceptance-5.json |
| U02 | 保持并融入 | 真实运行操作比静态稿多 | 保留打开/新建、历史、已知ID、状态和TTFT情景；依据 INTERACTION_V2 §3 | [src/features/v2/UserMonitor.tsx:1](../../../../../../../apps/viewer/src/features/v2/UserMonitor.tsx#L1) | 新建运行、响应丢失恢复、历史与缺参评估 | candidate5.log；joint5.log |
| U03 | 修复 | 图表控件及众数摘要偏离 | 视图/箱宽/纵轴下拉；众数箱/请求数/占比摘要、刻度；排行视图读既有 requests | [src/features/distributions/Distributions.tsx:1](../../../../../../../apps/viewer/src/features/distributions/Distributions.tsx#L1) | 三图切换直方图/排行、箱宽/占比；数值对后端 | candidate5.log；joint5.log；visual-5-final/candidate-users-1440.png |
| U04 | 修复 | 信号、独立导出区使布局冗长 | 紧凑信号空态和阈值入口；导出移到顶部详情控件，保留明细筛选导出 | [src/features/signals/Signals.tsx:1](../../../../../../../apps/viewer/src/features/signals/Signals.tsx#L1) / [src/features/v2/UserMonitor.tsx:1](../../../../../../../apps/viewer/src/features/v2/UserMonitor.tsx#L1) | 顶部导出、明细导出、取消、完整性失败与空结果 | candidate5.log；joint5.log |
| R01 | 保持 | 主要筛选和表格已一致 | 保留筛选栏、精确整数、20条分页、300ms防抖；不用原型4条样例 | [src/features/v2/Ranking.tsx:1](../../../../../../../apps/viewer/src/features/v2/Ranking.tsx#L1) | 29 APPID真实搜索：正反向/字面量/大小写/上下界/分页 | joint5.log；search5/api.log |
| R02 | 保持 | 真实身份与静态范围不同 | 保留模型/run/revision、刷新与显式应用范围；依据固定版本读取要求 | [src/features/v2/Ranking.tsx:1](../../../../../../../apps/viewer/src/features/v2/Ranking.tsx#L1) | 切排序重置分页、范围跳转和历史恢复 | joint5.log；source-tests-5.log |
| M01 | 保持 | 主要结构已一致 | 三摘要、全部UUID、理想蓝/真实青配对条及双页签；不裁剪实例 | [src/features/v2/MAMonitor.tsx:1](../../../../../../../apps/viewer/src/features/v2/MAMonitor.tsx#L1) | 13 UUID、独立集合、零/null/覆盖与历史 | candidate5.log；visual-5-final/candidate-ma-1440.png |
| M02 | 修复并保留真实流程 | 规格下拉、质量入口位置、画像文案 | 真实目录横排规格、表头数据质量、展开详情；历史/任务/已知ID仍在 | [src/features/v2/MAMonitor.tsx:1](../../../../../../../apps/viewer/src/features/v2/MAMonitor.tsx#L1) | 真实规格切换、质量打开关闭、实例展开收起 | candidate5.log；visual-5-final/candidate-ma-quality-1440.png |
| M03 | 修复 | 双趋势同色且无Y刻度 | 请求蓝、重算青及同色均值线，恢复网格/刻度；亚单位范围按真实最大值缩放 | [src/features/v2/MACharts.tsx:1](../../../../../../../apps/viewer/src/features/v2/MACharts.tsx#L1) | 12桶、整小时后端均值、null断点、0值不插值 | candidate5.log；visual-5-final/candidate-ma-trend-1440.png |
| M04 | 修复 | 页签和分布样式简化 | 选中填充页签，分布刻度、众数数量占比；尾桶和独立分位数不改 | [src/components/app-shell.css:1](../../../../../../../apps/viewer/src/components/app-shell.css#L1) / [src/features/v2/MACharts.tsx:1](../../../../../../../apps/viewer/src/features/v2/MACharts.tsx#L1) | 切长度分布、箱宽/纵轴与200K尾桶 | candidate5.log；visual-5-final/candidate-ma-distribution-1440.png |
| D01 | 保持 | 主要信息结构已有认可 | UI-04卡片/详情/局部证据、通知与历史/cache维持；partial/失败保留旧报告 | [src/features/analysis/AnalysisApp.tsx:1](../../../../../../../apps/viewer/src/features/analysis/AnalysisApp.tsx#L1) | 两方向切换、固定历史、通知、重连，无状态轮询 | analysis5.log |
| D02 | 保持 | 最新L4/L5应保护 | 各一张卡、每类最多三例、跨组请求去重和返回位置；不恢复逐组卡片 | [src/features/analysis/Reports.tsx:1](../../../../../../../apps/viewer/src/features/analysis/Reports.tsx#L1) | L4/L5各一卡、详情三例；旧group链接归并返回 | analysis5.log；visual-checks-5.json |
| D03 | 保持 | 原HTML含已撤销T1 | 仅T2–T4；真实配方/收益来自后端，不复制旧稿T1或演示数值 | [src/features/analysis/Reports.tsx:1](../../../../../../../apps/viewer/src/features/analysis/Reports.tsx#L1) | Token卡片、局部证据、收益和历史/partial | analysis5.log；visual-5-final/candidate-token-1440.png |
| D04 | 修复 | 分析独立五入口/窄屏三入口 | 分析改用同一AppShell；两类来源保留精确run，FS-01源码未改 | [src/features/analysis/AnalysisApp.tsx:1](../../../../../../../apps/viewer/src/features/analysis/AnalysisApp.tsx#L1) | 分析→来源→用户/S0→刷新；另一最近运行不污染 | source-tests-5.log；analysis5.log |

补充发现并修复一个真实范围竞争：S0 固定历史 run 读取尚未完成时，目录重连可先选最新运行，覆盖 URL 的历史 run。[src/app.tsx:45](../../../../../../../apps/viewer/src/app.tsx#L45) 在每次目录回调读取当前 URL，[src/state/snapshot-coordinator.ts:27](../../../../../../../apps/viewer/src/state/snapshot-coordinator.ts#L27) 使用显式 appid/model/run 对齐。新增 coordinator 竞争回归；保留最新通知/待应用行为。失败在 joint2，c5 joint5 的15范围固定历史全部通过；不是通过修改数值或删除断言解决。

## 3. 视觉对照

同一 Windows Chrome、全新 context，1440×1000 与390×844。最终主捕获38组截图+DOM，另有2组批准 Token 页面，共40组。[visual-5-final/visual-summary.json](../../../../../../../artifacts/validation/viewer/approved-ui-restoration-20261102/visual-5-final/visual-summary.json) 与 [visual-checks-5.json](../../../../../../../artifacts/validation/viewer/approved-ui-restoration-20261102/visual-checks-5.json) 记录无 pageerror、无横向溢出；桌面导航几何与 UI-02 一致。人工查看六卡/三图/明细、MA和窄屏 L4，确认布局、配色、刻度和例子结构；不做不同真实数据的整图像素相等要求。下表两个宽度均有同名后缀文件。

| 页面 | 批准稿1440 | 候选1440 | 候选390 |
| --- | --- | --- | --- |
| users | [visual-5-final/approved-users-1440.png](../../../../../../../artifacts/validation/viewer/approved-ui-restoration-20261102/visual-5-final/approved-users-1440.png) | [visual-5-final/candidate-users-1440.png](../../../../../../../artifacts/validation/viewer/approved-ui-restoration-20261102/visual-5-final/candidate-users-1440.png) | [visual-5-final/candidate-users-390.png](../../../../../../../artifacts/validation/viewer/approved-ui-restoration-20261102/visual-5-final/candidate-users-390.png) |
| ranking | [visual-5-final/approved-ranking-1440.png](../../../../../../../artifacts/validation/viewer/approved-ui-restoration-20261102/visual-5-final/approved-ranking-1440.png) | [visual-5-final/candidate-ranking-1440.png](../../../../../../../artifacts/validation/viewer/approved-ui-restoration-20261102/visual-5-final/candidate-ranking-1440.png) | [visual-5-final/candidate-ranking-390.png](../../../../../../../artifacts/validation/viewer/approved-ui-restoration-20261102/visual-5-final/candidate-ranking-390.png) |
| ma-trend | [visual-5-final/approved-ma-trend-1440.png](../../../../../../../artifacts/validation/viewer/approved-ui-restoration-20261102/visual-5-final/approved-ma-trend-1440.png) | [visual-5-final/candidate-ma-trend-1440.png](../../../../../../../artifacts/validation/viewer/approved-ui-restoration-20261102/visual-5-final/candidate-ma-trend-1440.png) | [visual-5-final/candidate-ma-trend-390.png](../../../../../../../artifacts/validation/viewer/approved-ui-restoration-20261102/visual-5-final/candidate-ma-trend-390.png) |
| ma-distribution | [visual-5-final/approved-ma-distribution-1440.png](../../../../../../../artifacts/validation/viewer/approved-ui-restoration-20261102/visual-5-final/approved-ma-distribution-1440.png) | [visual-5-final/candidate-ma-distribution-1440.png](../../../../../../../artifacts/validation/viewer/approved-ui-restoration-20261102/visual-5-final/candidate-ma-distribution-1440.png) | [visual-5-final/candidate-ma-distribution-390.png](../../../../../../../artifacts/validation/viewer/approved-ui-restoration-20261102/visual-5-final/candidate-ma-distribution-390.png) |
| low | [visual-5-final/approved-analysis-1440.png](../../../../../../../artifacts/validation/viewer/approved-ui-restoration-20261102/visual-5-final/approved-analysis-1440.png) | [visual-5-final/candidate-low-1440.png](../../../../../../../artifacts/validation/viewer/approved-ui-restoration-20261102/visual-5-final/candidate-low-1440.png) | [visual-5-final/candidate-low-390.png](../../../../../../../artifacts/validation/viewer/approved-ui-restoration-20261102/visual-5-final/candidate-low-390.png) |
| token | [visual-5-final/approved-token-1440.png](../../../../../../../artifacts/validation/viewer/approved-ui-restoration-20261102/visual-5-final/approved-token-1440.png) | [visual-5-final/candidate-token-1440.png](../../../../../../../artifacts/validation/viewer/approved-ui-restoration-20261102/visual-5-final/candidate-token-1440.png) | [visual-5-final/candidate-token-390.png](../../../../../../../artifacts/validation/viewer/approved-ui-restoration-20261102/visual-5-final/candidate-token-390.png) |

设置及旧深链：[visual-5-final/candidate-settings-1440.png](../../../../../../../artifacts/validation/viewer/approved-ui-restoration-20261102/visual-5-final/candidate-settings-1440.png)、[visual-5-final/candidate-overview-390.png](../../../../../../../artifacts/validation/viewer/approved-ui-restoration-20261102/visual-5-final/candidate-overview-390.png)。L4/L5：[visual-5-final/candidate-L4-390.png](../../../../../../../artifacts/validation/viewer/approved-ui-restoration-20261102/visual-5-final/candidate-L4-390.png)、[visual-5-final/candidate-L5-1440.png](../../../../../../../artifacts/validation/viewer/approved-ui-restoration-20261102/visual-5-final/candidate-L5-1440.png)；两宽度各三例，卡片聚合不变。旧审计的 V1 设置导航不能满足新四入口断言（visual-checks 中记录原导航反例）。窄屏四入口是正式导航一致性修复，不声称原型本就包含该菜单。

UI-04原稿T1不恢复；L4/L5按后来认可聚合；真实运行/历史/任务和后端数值差异按18项矩阵明确保留。没有新增产品设计或单项评估流程。

## 4. 功能自测与失败复测

| 检查 | 本候选结果 | 原始记录 |
| --- | --- | --- |
| typecheck / lint / build | 通过，退出0 | [checks-7.log](../../../../../../../artifacts/validation/viewer/approved-ui-restoration-20261102/checks-7.log) |
| 单元/组件 | 24文件、215项通过 | 同上 |
| 监控V2、MA、TTFT、导出、统一外框 | 42项通过 | [candidate5.log](../../../../../../../artifacts/validation/viewer/approved-ui-restoration-20261102/candidate5.log)、[candidate5-result.json](../../../../../../../artifacts/validation/viewer/approved-ui-restoration-20261102/candidate5-result.json) |
| 异常分析缓存/SSE/历史/partial/卡片 | 18项通过 | [analysis5.log](../../../../../../../artifacts/validation/viewer/approved-ui-restoration-20261102/analysis5.log)、[analysis5-result.json](../../../../../../../artifacts/validation/viewer/approved-ui-restoration-20261102/analysis5-result.json) |
| FS-01两种来源及另一最近运行 | 3项通过 | [source-tests-5.log](../../../../../../../artifacts/validation/viewer/approved-ui-restoration-20261102/source-tests-5.log) |
| 真实搜索排行/明细/导出 + S0联合 | 8项通过 | [joint5.log](../../../../../../../artifacts/validation/viewer/approved-ui-restoration-20261102/joint5.log) |
| 合成数据真实后端基础验收 | 15范围通过 | [base-acceptance-5.json](../../../../../../../artifacts/validation/viewer/approved-ui-restoration-20261102/base-acceptance-5.json) |
| 搜索API | 通过 | [search5/api.log](../../../../../../../artifacts/validation/viewer/approved-ui-restoration-20261102/search5/api.log)、[search5/real-search-api.json](../../../../../../../artifacts/validation/viewer/approved-ui-restoration-20261102/search5/real-search-api.json) |
| 同候选服务重启 | 111地址逐字节SHA一致、service_instance不变 | [restart-result.json](../../../../../../../artifacts/validation/viewer/approved-ui-restoration-20261102/restart-result.json)、[restart-check.log](../../../../../../../artifacts/validation/viewer/approved-ui-restoration-20261102/restart-check.log) |
| 重启后新context | 来源3项 + 四入口2项通过（重复验证不累加） | [restart-browser.log](../../../../../../../artifacts/validation/viewer/approved-ui-restoration-20261102/restart-browser.log)、[restart-shell.log](../../../../../../../artifacts/validation/viewer/approved-ui-restoration-20261102/restart-shell.log) |

浏览器不同用例共71项，不将重启后的5项重复算入。restart-browser首轮因遗漏 REAL_BACKEND 环境变量跳过两项外框测试，已在 restart-shell 正确设置后2项通过，保留原skip记录。15范围/搜索/诊断都由本轮真实后端合成输入产生；异常错误与断网、导出损坏等边界用现有受控网络注入验证，不能称全部断言毫无网络替身。

原断言保留：joint 数值从旧7卡文本拆到六卡、精确总量和Token图例；metadata选择器替代旧identity；P50精确匹配；新SVG导航不计入分布rect。老4193重定向断言按本轮“旧服务必须停”改为连接失败，并保留同源双方向断言。没有删数值/身份/缓存/恢复/导出断言换通过。

失败与复测链（全部保留在证据目录）：
- checks-1：P50新说明导致定位歧义，等价精确标签修复；checks-7通过。
- v2-1：生产dist不能导入源码测试模块、错误合成文件不满足原30行断言。只在artifact测试副本提供当前client源码打包模块（client-test.mjs），接口仍真实；改用已有v2合成输入，不改后端或断言。candidate5 42通过。
- 早期窄屏分析导航继承宽度导致堆叠，限定公共移动样式并增加高度断言；c5通过。
- 诊断旧group链接fixture重复diff前缀、来源fixture错误模型alias属于测试设置问题；修正为当前真实ID/合法alias，analysis5/source-tests-5通过。
- joint1旧选择器和fixture范围问题等价修正；joint2暴露真实历史run竞争，修复代码后joint5全部通过。
- checks-6暴露严格可选类型和测试unknown类型错误，修复后checks-7通过。
- visual-5的MA桌面在加载未完成时取证，原证据保留；capture-5-final等待真实可展开后重拍，visual-5-final为最终对照。后续DOM脚本曾遗漏baseline active类，修正匹配nav-item类成员后重新检查（未改页面）。
- candidate1优雅停止后HTTP停但进程尚在，后续确认精确PID强停；没有把初次 exited:false 隐去。

构建存在既有大chunk警告（主JS约934KB、gzip193KB），不是编译失败；本轮没有以恢复任务扩展到拆包重构。合成自测不能代替15万规模性能、生产收益或华为现场验收。

## 5. 环境清理、冷启动与复现

开工清单 [processes-before.json](../../../../../../../artifacts/validation/viewer/approved-ui-restoration-20261102/processes-before.json)；原4191 Vite PID1648720、4193重定向1648721、8016旧后端1734153均核对命令/cwd后停止，[old-services-stopped.json](../../../../../../../artifacts/validation/viewer/approved-ui-restoration-20261102/old-services-stopped.json) 确认退出与释放。旧state/包/日志未删除。启动前无本项目测试容器/daemon；未停止共享Docker或其他项目。c1–c4各独立state/dist及退出记录保留；c5开始为空state，[cold-catalog-5.json](../../../../../../../artifacts/validation/viewer/approved-ui-restoration-20261102/cold-catalog-5.json)。Windows浏览器测试使用全新context，未删除用户个人浏览器数据。

当前唯一候选 PID2680003；[server-5-restarted.json](../../../../../../../artifacts/validation/viewer/approved-ui-restoration-20261102/server-5-restarted.json) 为精确argv/env/cwd；[cleanup-final.json](../../../../../../../artifacts/validation/viewer/approved-ui-restoration-20261102/cleanup-final.json) 为结束清单：4191提供候选，4193/8016/4175关闭；编辑器语言服务保留。原PID2645757已确认退出、4191释放后才重启。重启是明确的同版本恢复测试，非新候选复用旧state。合成DeepSeek模式配置单独记录 [explicit-synthetic-deepseek-5.json](../../../../../../../artifacts/validation/viewer/approved-ui-restoration-20261102/explicit-synthetic-deepseek-5.json)，不代表生产配置认可。

在WSL项目根目录复现同候选的命令（仅用于同版本恢复；先核对并停止当前PID）：

```sh
O=/home/zhangxiyue/TokenScope/artifacts/validation/viewer/approved-ui-restoration-20261102
TOKENSCOPE_RECOMMENDATION_BUNDLE="$O/fixture-config-5/synthetic-recipes.json" .venv/bin/python -m tokenscope.cli --input-root "$O/inputs" --state-root "$O/state-5"  --asset-root /home/zhangxiyue/TokenScope --cpu-budget 2 serve  --host 127.0.0.1 --port 4191 --viewer-root "$O/dist-5"
```

停止时先比对 `/proc/2680003/cmdline`、cwd与server记录，再发送TERM并检查退出/端口；若PID变更必须重新核实，不能直接照抄kill。若TERM后进程未退，确认仍同命令后再强停；不删state。

运行身份/输入与可复现步骤：
- [base-acceptance-5.json](../../../../../../../artifacts/validation/viewer/approved-ui-restoration-20261102/base-acceptance-5.json)：15个appid/model/run；[visual-5-final/visual-identities.json](../../../../../../../artifacts/validation/viewer/approved-ui-restoration-20261102/visual-5-final/visual-identities.json)：用户运行与MA目录。
- [fixture-config-5/actual-http.json](../../../../../../../artifacts/validation/viewer/approved-ui-restoration-20261102/fixture-config-5/actual-http.json)：诊断history_ready/default_ready/latest_partial三次真实任务。
- [source-link-fixture-5.json](../../../../../../../artifacts/validation/viewer/approved-ui-restoration-20261102/source-link-fixture-5.json)：来源原运行、另一个最近运行和S0来源。
- [search5/real-search-api.json](../../../../../../../artifacts/validation/viewer/approved-ui-restoration-20261102/search5/real-search-api.json)：29APPID搜索receipt；inputs、v2-inputs为本轮合成文件，禁止拿生产数据替代。
- Windows Chrome运行配置：candidate5.config.cjs、analysis5.config.cjs、joint5.config.cjs；对应复制测试仅适配真实生成ID、模块import路径及输入文件。源断言仍在apps/viewer/tests；脚本和日志保留。普通验证：在apps/viewer执行 npm run typecheck、npm run lint、npm test；独立build输出dist-5，未改共享dist。
- 浏览器设 TOKENSCOPE_BROWSER_EXECUTABLE、TOKENSCOPE_EXTERNAL_PREVIEW=1、TOKENSCOPE_TEST_BASE_URL=http://localhost:4191，外框测试另设TOKENSCOPE_REAL_BACKEND=1；FS用TOKENSCOPE_SOURCE_LINK_FIXTURE指向本轮json，joint设TOKENSCOPE_JOINT=1。

## 6. 独立复审交接与未决

18项本轮自测完成，无已知未修复的功能阻断；**独立复审与用户视觉认可仍待完成**。审查方负责协调后续发现，不由本会话自行代签。

审查方必须先停止本候选并确认端口释放，从自己固定的源码/dist、新空state、新浏览器环境重新冷启动；不能直接复用state-5当独立验收。按相同18项和功能保护点复审，保留失败与复测；发现后端疑点交对应后端session，不能改契约迁就页面。核实候选源码摘要及HTTP资源，不以HEAD单独代表未提交候选。

本轮无提交、合并、push、Docker构建、交付包或华为部署。复审通过不自动获得上述授权；原包、原state、批准HTML和其他session修改继续保留。
