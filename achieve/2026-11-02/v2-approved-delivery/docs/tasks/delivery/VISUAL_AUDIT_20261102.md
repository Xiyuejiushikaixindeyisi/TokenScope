> 归档：本文件保存历史过程，不再是执行入口。2026-11-02用户认可V2可交付，UIR-03留V3、不作V2阻断。现场只用真实数据，分两次用户验收，单份Markdown回传。当前见[交付入口](../../../../../../docs/tasks/delivery/ENTRY.md)；[逐字节原始快照](../../../snapshots/docs/tasks/delivery/VISUAL_AUDIT_20261102.md)。

# 已批准 HTML 与 FS-01 交付页面展示差异审计

日期：2026-11-02。审查会话：`01a1800e-80b4-7400-a78b-a84f5b6e888d`，取自本轮环境的 CODEX_THREAD_ID / CODEX_SESSION_ID。范围：用户明确指定的四个业务入口、最后认可的 L4/L5 展示，以及 `http://localhost:4191/#/settings` 与正式交付镜像的实际页面。只核查、取证和记录，不修改业务代码、回滚或重新构建打包，不提交或推送 Git。

## 结论

**用户指出的框架偏离确实存在，正式交付镜像中能够复现。** 批准的整体导航是“用户监控、搜索与排行、异常分析、MA 集群监控”。实际应用存在三套导航：监控 V2 六项、异常分析五项、设置页六项 V1 导航。点击“运行设置”后，四个已批准的业务入口全部消失，左下角变为“Token 监控 · V1”。这不是浏览器缓存，也不是只发生在 4191 开发服务上的现象。

主要原因是正式接入时把“复用 V1 设置功能”实现成了“切回整个 V1 应用”，并让监控和异常分析分别维护导航。首次记录在监控 V2 接入提交 `ef2b96c4`；异常分析接入提交 `10f4a067` 延续该路径。另有导航图标、间距、用户直方图控件、MA 图表配色/坐标和页签样式等与批准稿不同。

四个业务页的主要内容结构并未全部重做：六卡与三图、TTFT 三栏、排行筛选加表格、MA 全 UUID 表及双页签、异常分析卡片与局部证据、L4/L5 各一卡且最多三例仍在。本报告不会把合成数据不同、已批准的真实历史/任务交互或明确删除 T1 误报成展示回退。

**此前统一审查遗漏了跨页面导航与批准 HTML 的一致性检查。** 验证源码身份、接口、数值和工程用例通过，不能替用户签署整体界面认可；L4/L5 局部认可也不构成更改四入口框架的授权。当前交付包不能继续称为“用户已认可的完整前端展示”。

## 1. 比较对象及身份

| 对象 | 本轮实际核对 |
| --- | --- |
| 批准框架 | 用户本轮再次明确的四入口；监控 [UI-02 认可记录](../../../../../../docs/tasks/viewer/monitoring-v2/PROTOTYPE_UI_02.md)及其 HTML；分析 [UI-04 与 L4/L5 认可记录](../../../../../../docs/tasks/viewer/analysis/VISUAL_BASELINE.md) |
| 监控 HTML | [tokenscope-v2-demo-ui02.html](../../../../../../docs/tasks/viewer/monitoring-v2/prototypes/tokenscope-v2-demo-ui02.html)，SHA256 `799786cb3ee52e0931d2482211f82e594ab0f33ad57969232a7ea2ec06d2eaea` |
| 分析 HTML | [tokenscope-analysis-ui04.html](../../../../../../docs/tasks/viewer/analysis/prototypes/analysis-ui04/tokenscope-analysis-ui04.html)，SHA256 `779e6665985fe02e6df9e7d0483ef8111a16a49c2b61fdb27aacbef58d624f5f` |
| L4/L5 最新批准 | 2026-11-01 正式页面“各一张卡、每类最多三个代表例子”；没有新的 HTML，不用旧 HTML 的逐组展示覆盖这项决定 |
| 用户提供地址 | `http://localhost:4191/#/settings`，本轮实际是 Vite 开发服务；单独验证，不将端口名当版本身份 |
| 当前工作树 | HEAD `9f2a3e60394327e4e6bdc41bd688497ddef21dd7`；前端源码与交付源提交一致；共享未提交文档另行保留 |
| 正式交付版本 | `tokenscope-rv2-fs01-20261102`；源提交 `0263d784b4603cf693b30b809bec2d9311b2732e` |
| 镜像 | `tokenscope/full-service:tokenscope-rv2-fs01-20261102`；ID `sha256:037a641839b4f7d6ae0572f3af0fafc18a8b5e4c269bb9e19998819abce78710` |
| 正式页面核验方式 | 直接启动该已有镜像于隔离端口 18064，使用历史合成输入/state 的副本；未挂载替换 `/app` 或前端 dist，未 build/save/load 或生成新交付包 |
| 资源身份 | 镜像实际 HTTP 返回的 index.html、主 JS、CSS、导出校验 worker 四文件 SHA256 均与交付候选一致，见 [资源核对](../../../../../../artifacts/reviews/visual-audit-20261102/image-resource-identity.json) |

UI-02 文档原始 manifest 中的 `b50b784…` 属于缺参保护调整前版本。该文档末尾记录了 2026-10-30 在不改布局配色前提下，将默认等待置空、不默认展示命中率的调整。本轮冻结并比较现存 `799786…` 字节，保留旧 manifest 和原始证据，没有为了消除差异而改写 HTML。分析 HTML 中的 T1 则受后来明确删除决定覆盖。

交付代码包 SHA256：`012ba7e6877da4700d70560fb0ebbc8aeb5e6c2b350083fdeefa4ab859371b27`。镜像包 SHA256：`534460f1de2b8713ec242e9fcb9cf0078e106098a621c7d9fffaccd508cf7986`。本轮 WSL 发布目录全部 15 个文件与开始时一致；桌面副本未改动，既有逐文件比对见 [桌面交付记录](../../../../../../docs/tasks/delivery/FS01_DESKTOP_COPY_20261102.json)。

## 2. 最直接的复现与截图

1. 打开 `http://localhost:4191/#/users`，可以看到四个业务入口，以及额外的“运行设置”“V1监控”。
2. 点击侧栏“运行设置”，地址成为 `#/settings`。
3. 侧栏整体替换为“监控概览、请求长度分布、请求明细、监控信号、运行设置、提交任务”；批准的四个业务入口全部消失，页脚显示 V1。
4. 对正式交付原镜像执行相同操作，结果一致。本轮捕获了直接打开设置与从用户页点击设置的两条路径。隔离端口在取证结束后关闭；现有 4191/8016 服务未停止。

批准的四入口与用户监控主框架：

![批准 UI-02：四入口](../../../../../../artifacts/reviews/visual-audit-20261102/approved-users.png)

正式镜像用户监控首屏：四个业务入口之外新增设置和 V1 入口。

![正式镜像：用户监控首屏](../../../../../../artifacts/reviews/visual-audit-20261102/image-users-top.png)

从上述页面点击“运行设置”后，正式镜像实际显示另一套 V1 工作台：

![正式镜像：点击设置后切成 V1 导航](../../../../../../artifacts/reviews/visual-audit-20261102/image-click-settings.png)

用户提供地址的独立截图：[4191 设置页](../../../../../../artifacts/reviews/visual-audit-20261102/live-settings.png)。这张图与正式镜像的 V1 导航相互印证，不以开发服务代替交付镜像验证。

## 3. 逐项差异、来源和判断

“首次提交”表示本仓库能够核实的首次纳入提交，不推断未提交开发过程或实际操作人的意图。后续集成提交可能包含多位 session 的工作，不能用共用 Git 作者名直接归责个人。“原因”区分源码直接事实与文档支持的实现动机。

### A. 整体框架与导航

| 编号 | 批准稿 / 决定 | 正式交付实际展示 | 对应源码、提交和引入原因 | 判断 |
| --- | --- | --- | --- | --- |
| A01 | 四个业务入口构成统一框架；设置属于既有功能流程 | 从用户页或分析页进入 `#/settings`，整套导航被 V1 六项替换；四入口均不见，侧栏无法直接返回 V2 业务页 | [app.tsx](../../../../../../apps/viewer/src/app.tsx) 28–32 行：只有 users、ma 进入 V2，analysis 单独分流，其他一律 LegacyApp。`ef2b96c4` 建立该分流，`10f4a067` 增加 analysis 分支后仍保留 fallback。交互方案要求复用 V1 设置流程，代码却连同 V1 导航一起复用 | **核心框架偏离，阻断整套展示认可**。设置功能本身不是问题，切换整套工作台才是问题 |
| A02 | UI-02 与 UI-04 桌面侧栏均为四业务入口 | 用户/排行/MA 是四项加“运行设置、V1监控”共六项；分析是四项加“运行设置”共五项；设置又是另外六项 | [V2App.tsx](../../../../../../apps/viewer/src/features/v2/V2App.tsx) 25 行和 [AnalysisApp.tsx](../../../../../../apps/viewer/src/features/analysis/AnalysisApp.tsx) 92 行分别硬编码导航。设置/V1 链接首次即在 `ef2b96c4`；分析导航及分析入口接入是 `10f4a067`，并非该提交首次添加全部额外入口 | **全局导航不一致**，与 A01 同源；没有找到批准把四入口升级成三套工作台的依据 |
| A03 | SVG 图标、分组导航间距与路线对应的页面标题 | 图标换为 `▦ ☷ ◈ ⚙ ↗` 文字符号；V2 侧栏第一业务项位置下移；V2 顶栏在用户、排行、MA 均写“工作台 / Token监控” | V2App 同行首次 `ef2b96c4`；分析导航 `10f4a067`。V2 把原型分组包裹结构改成单个 nav 的平铺元素，图标改为文字；顶栏标题写成常量。1440×1000 下首项 y：UI-02 111px、V2 135px，分析分别约 116px | 可确认的局部视觉差异。208px 侧栏、深浅底色仍在；不能称完全保留原导航样式 |
| A04 | 用户要求四业务入口在统一框架内；原型窄屏会隐藏侧栏 | 正式 V2 窄屏提供四业务链接；正式分析窄屏仅用户监控、异常分析、MA，缺少直接进入搜索排行的链接 | AnalysisApp 92 行 `mobile-analysis-nav` 仅三链接，`10f4a067`；另一个移动导航由 V2App 自行维护 | 模块整合不一致。**原 HTML 窄屏也没有四链接移动菜单**，故不将其描述成从原型删除已有菜单；问题是正式应用跨模块入口不齐 |

### B. 用户监控与搜索排行

| 编号 | 批准稿 / 决定 | 正式交付实际展示 | 对应源码、提交和引入原因 | 判断 |
| --- | --- | --- | --- | --- |
| U01 | 六卡 3×2、Token 去向条、TTFT 三栏、三张长度分布 | 主结构保留；数据来自当前固定合成运行 | UserMonitor 组合 Overview、TTFT、Distributions；接入于 `ef2b96c4` | **主结构一致**。本轮没有证据支持“用户监控页面整体被重做”的结论 |
| U02 | 原型顶部为分析报告/指标口径/导出样例等展示操作，服务以横排模型按钮呈现 | 正式顶部是“打开运行/新建分析”，增加运行状态；模型绑定所选运行，另有历史记录及折叠“按APPID打开基础结果” | [UserMonitor.tsx](../../../../../../apps/viewer/src/features/v2/UserMonitor.tsx) 约 200–210 行，`ef2b96c4`；[INTERACTION_V2](../../../../../../docs/tasks/viewer/monitoring-v2/INTERACTION_V2.md) 已要求真实运行、打开历史、已知 ID、按钮/弹窗承接流程 | 存在布局密度和控件差异，其中功能接入有明确依据。不能把静态样例按钮不同一律判为擅自改框架；这些依据也不能授权 A01 |
| U03 | 三图头部有视图、区间宽度、纵轴下拉；突出显示众数箱、请求数和占比的摘要块 | 正式复用 V1 三图，使用“分箱”与“显示请求占比”复选框；众数信息变成普通文本，没有同样的突出摘要块和相同控件排列 | [Distributions.tsx](../../../../../../apps/viewer/src/features/distributions/Distributions.tsx) 12–27 行；组件来自 F007，相关历史为 `31ab864`；`ef2b96c4` 在 V2 中直接复用。不是 FS-01 引入 | **局部展示偏离**。三图和众数数据仍在，不能误报成丢失统计功能；复用旧组件未完全落实 UI-02 样式 |
| U04 | 原型告警空态、顶部导出入口与紧凑请求明细区域 | 正式拼入既有 Signals、独立 Exports 区和 Requests；空态与区域排布沿旧组件，长列表使页面更长 | UserMonitor 210 行；原始组合已在 `ef2b96c4`。当前 blame 为 `cd14fc73` 的原因包含后续导出修复，不能把整段原始排布都算到修复提交 | 局部呈现差异；保留 S0 导出、明细和信号有功能依据，未证明其外观等同批准稿 |
| R01 | 搜索/排序/上下界折叠条件、表格、分页 | 上述主要结构保持，正式运行按真实条目渲染 | [Ranking.tsx](../../../../../../apps/viewer/src/features/v2/Ranking.tsx)，`ef2b96c4` | **主结构一致**。原型每页 4 条是评审投影，正式每页 20 条有交互文档明确依据，不列为擅改 |
| R02 | 原型服务可切换，时间/范围以展示文案呈现 | 正式模型来自当前选中运行，显示真实运行 UUID，增加刷新排行等操作；筛选栏排列有所变化 | Ranking 66–78 行，`ef2b96c4`；固定运行/revision 读取和恢复要求导致真实身份需要可辨识 | 可确认控件/文案差异；运行身份和真实查询流程有依据，UUID 文案不是本次四入口框架偏离的根因 |

### C. MA 集群监控

| 编号 | 批准稿 / 决定 | 正式交付实际展示 | 对应源码、提交和引入原因 | 判断 |
| --- | --- | --- | --- | --- |
| M01 | 三摘要位、全部 UUID、配对理想/真实蓝青条、下方“流量趋势 / 长度分布” | 主要表格和两页签内容保留，12 个五分钟桶和整小时均值仍展示 | [MAMonitor.tsx](../../../../../../apps/viewer/src/features/v2/MAMonitor.tsx)、[MACharts.tsx](../../../../../../apps/viewer/src/features/v2/MACharts.tsx)，`ef2b96c4` | **主结构一致**；本次合成 UUID/数值不同不能用于声称计算变更 |
| M02 | 顶部横排规格按钮、表头数据质量入口、“展开详情” | 规格变成下拉选择，加入历史/任务状态/已知运行 ID；数据质量变为下方“运行质量记录”，“展开详情”改“查看画像” | MAMonitor 约 190–199 行，`ef2b96c4`；真实目录、已知运行和历史恢复有交互依据，质量区域采用独立 details | 功能接入造成的局部排布变化，部分有依据；质量入口位置与原稿不同仍需如实记录 |
| M03 | 请求压力蓝色，实际重算压力青色；图中有 Y 轴刻度/网格辅助读数 | 两张趋势图均为蓝色，均值线也使用同一蓝色；没有原稿的数值 Y 刻度/网格，数值需看均值、悬浮提示或展开 12 桶表 | MACharts 9–18 行，`ef2b96c4`。共用 Trend 组件把线与点写死为 `var(--blue)`，没有颜色参数；SVG 仅画基线、均值和数据点 | **直接可见的样式与读数辅助退化**，与数据不同无关。本轮未据此认定后端计算错误 |
| M04 | “流量趋势 / 长度分布”为清晰的选中态页签；分布图延续原型图表样式 | 正式使用普通描边按钮，虽有 aria-pressed，但没有原稿的填充选中态；分布图刻度/摘要也被简化 | MACharts 约 32 行及 Distribution，`ef2b96c4`；页面使用通用 button / 自绘简化 SVG，没有复现原型完整样式 | **局部视觉偏离**；两页内容仍能切换，不报告为功能失效 |

MA 趋势批准稿：左蓝、右青，以及对应页签和坐标辅助。

![批准稿 MA 趋势](../../../../../../artifacts/reviews/visual-audit-20261102/approved-ma-trend.png)

正式镜像 MA 趋势：两图均蓝、页签和坐标表达不同。数据集不同，所以不比较曲线数值是否相等。

![正式镜像 MA 趋势](../../../../../../artifacts/reviews/visual-audit-20261102/image-ma-trend.png)

### D. 异常分析及最后认可的 L4/L5

| 编号 | 批准稿 / 决定 | 正式交付实际展示 | 对应源码、提交和引入原因 | 判断 |
| --- | --- | --- | --- | --- |
| D01 | APPID/模型范围、低命中与 Token 类别切换、优化建议与差异卡片、详情中的局部证据和具体改法 | 页面整体结构与颜色系统保持；正式接入添加通知状态、紧凑历史选择、最新/固定历史状态 | AnalysisApp，`10f4a067`；[视觉基线](../../../../../../docs/tasks/viewer/analysis/VISUAL_BASELINE.md)与交互文档明确认可轻量缓存、历史切换和详情返回 | **主要信息结构一致**；真实状态/历史使卡片起点略下移，不把该差异自动判为未经讨论的重设计 |
| D02 | 最新批准为 L4、L5 各一张卡，每类详情最多三个代表例子 | 正式合成报告显示各一卡，详情最多三例；L4/L5 详情截图和 DOM 已分别保留 | [Reports.tsx](../../../../../../apps/viewer/src/features/analysis/Reports.tsx) 中 ReportCards/ReportDetail 及 [Evidence.tsx](../../../../../../apps/viewer/src/features/analysis/Evidence.tsx)，`10f4a067` 纳入的 RV2 实现；[RV2 记录](../analysis/JOINT_VALIDATION_RV2_20261101.md) | **与最后批准一致**。不为了对齐更早逐组卡片而建议回退；这项认可不能扩展为 A01/A02 已获认可 |
| D03 | UI-04 原 HTML 有 T1，但后续明确删除；Token 范围为 T2–T4 | 正式只展示当前范围；真实报告的分组数、收益值、构造配方可用状态不同于静态样例 | 同一分析接入提交与已记录范围决定 | **属于已批准范围/真实数据差异**，不列为缺失页面或展示回退；本轮未重新验证全部诊断算法 |
| D04 | 分析也处于同一四入口框架 | 分析独立维护五项导航，移动端仅三业务入口；设置仍切 V1 | AnalysisApp 与 app.tsx，`10f4a067` 继承既有 fallback | **A01/A02/A04 在分析页面的表现**，不是 L4/L5 卡片批准能够覆盖的问题 |

对照截图：[UI-04 分析主页](../../../../../../artifacts/reviews/visual-audit-20261102/approved-analysis.png)、[正式分析主页](../../../../../../artifacts/reviews/visual-audit-20261102/image-analysis-orders.png)、[正式 L4 详情](../../../../../../artifacts/reviews/visual-audit-20261102/image-L4.png)、[正式 L5 详情](../../../../../../artifacts/reviews/visual-audit-20261102/image-L5.png)、[UI-04 Token 页](../../../../../../artifacts/reviews/visual-audit-20261102/approved-token.png)、[正式 Token 页](../../../../../../artifacts/reviews/visual-audit-20261102/image-token.png)。详情截图为滚动后的完整页面，固定侧栏在截图中的纵向位置不用于判定布局错误。

## 4. 提交链与代码原因

| 提交 | 核实到的变化 | 对本次问题的作用 |
| --- | --- | --- |
| `ef2b96c4f605c2b0482d85914dca26c6cd48b5de`，2026-10-31 | 监控 V2 正式接入：V2App、UserMonitor、Ranking、MAMonitor、MACharts，以及 App 中 V2 / Legacy 分流 | 首次建立“V2 页面 + V1 整体 fallback”；额外设置/V1 入口、旧分布组件复用、MA 简化绘图均已存在 |
| `cd14fc73b77e7baff4fa9b45f3dc886f7c996272` | 监控复审修复，包括导出路径相关调整 | 未统一导航；不能因为 UserMonitor 当前整行 blame 指向本提交，就认定该行所有布局从此才出现 |
| `10f4a0674892c9f331f262b91e6a6118a17ac4ac`，2026-11-01 | 异常分析 RV2 纳入；App 新增 AnalysisApp 分支；V2 中接入分析链接；分析维护另一套导航 | 将同一产品变成 V2App / AnalysisApp / LegacyApp 三个独立页面外框；继承设置回 V1；L4/L5 最新形态亦在该版本链中 |
| `45d9285210dc0b9edeb86c599c7b6bcd942f60b5` | 前一版统一交付的固定源码 | 上述展示差异已随此前 RV2 交付存在，不是 FS-01 独有 |
| `0263d784b4603cf693b30b809bec2d9311b2732e` | FS-01 正式修复与交付源 | 对比 45d9285 的前端生产源码，只有 SourceLink 中 `user_run_id` → `run` 一行；没有布局或样式修改 |

当前路由关键代码（[app.tsx](../../../../../../apps/viewer/src/app.tsx) 28–32 行）直接解释设置为何切换整个框架：

```tsx
const route = useSyncExternalStore(subscribe, currentPage);
const page = route.split('?')[0] ?? 'users';
if (page === 'analysis') return <AnalysisApp/>;
if (!window.location.hash || page.startsWith('users') || page.startsWith('ma'))
  return <V2App page={page}/>;
return <LegacyApp/>;
```

`settings` 不在前两个分支中，因此必定进入 LegacyApp。LegacyApp 包含自己的完整侧栏、顶栏、六个 V1 页面和 V1 页脚，并非只有一个设置表单。V2App 和 AnalysisApp 又都直接链接 `#/settings`，构成了可从主流程触达的界面切换。

文档的“配置编辑沿用 V1 设置/阈值流程”可以解释为什么保留原功能，但并未要求替换整体导航。[INTERACTION_V2.md](../../../../../../docs/tasks/viewer/monitoring-v2/INTERACTION_V2.md) 同时要求保留既有侧栏、布局、密度和已批准页面结构。**把功能兼容实现为整套旧应用切换，是能由源码证明的引入机制；没有证据表明用户批准过该整体替换。**

另一条源码可见的兼容路径是 SourceLink 对基础来源使用 `#/overview`，也会落入 LegacyApp。本轮直接浏览器复现的是“运行设置”路径；不把未在本轮点击验证的所有来源链接一并宣称复现完成。

提交依据保存在 [route-introduction.txt](../../../../../../artifacts/reviews/visual-audit-20261102/route-introduction.txt)、[route-blame.txt](../../../../../../artifacts/reviews/visual-audit-20261102/route-blame.txt)、[V2 原始导航](../../../../../../artifacts/reviews/visual-audit-20261102/v2-original-navigation.txt)、[分析集成差异](../../../../../../artifacts/reviews/visual-audit-20261102/analysis-integration.txt)、[组件行级来源](../../../../../../artifacts/reviews/visual-audit-20261102/component-provenance.json)、[FS-01 源码差异](../../../../../../artifacts/reviews/visual-audit-20261102/FS01-source-diff.txt)。结合原始提交与忽略 CRLF 的差异读取，避免把整行格式变化误判为首次引入。

## 5. 为什么此前测试通过却没有拦住

1. **包体身份正确不代表界面符合批准稿。** 本轮证明固定镜像确实交付了固定源码；源码中已经包含导航分裂，Docker 没有重新生成另一套布局。
2. **导航测试接受了 V1 兼容页，而未要求四入口始终保留。** [analysis.spec.ts](../../../../../../apps/viewer/tests/browser/analysis.spec.ts) 约 62–64 行的 `analysis navigation preserves monitoring and MA routes` 验证返回用户/MA，再直接访问 `#/overview` 并断言标题“监控概览”。该用例会把当前回 V1 的能力视为通过，没有验证设置页的统一导航和返回路径。
3. **旧视觉用例的基线不覆盖本次 V2 整体框架。** [visual.spec.ts](../../../../../../apps/viewer/tests/browser/visual.spec.ts) 的 F007 对照针对 V1、六卡、侧栏宽度和网格；这些检查即使通过，也不能证明 UI-02 的四入口及 MA 新页签/配色保持。
4. **功能回归与局部认可被扩大解释。** 运行身份、固定版本、缓存、恢复、导出以及 L4/L5 卡片可以分别正确；它们不能证明整个产品导航符合批准 HTML。此前统一审查没有把这两个结论分开，是本审查线的遗漏。

本轮已经纠正结论口径：工程验证记录继续作为对应范围的原始事实保留，但不再作为用户整套展示已认可的依据。不通过删除断言、重写历史结论或归咎于浏览器选择器来消除问题。

## 6. 证据覆盖、边界与保全

本轮共保存 **30 组页面截图及 DOM/导航观察**：20 组主捕获、10 组细节捕获。桌面采用 1440×1000，窄屏采用 390×844；比较基线使用同一浏览器和对应视口。覆盖用户、排行、MA 总览与两页签、低命中、Token、L4/L5、设置以及移动导航。使用既有合成运行副本，不比较原型假数据与正式数据的数值相等，也不将本轮展示取证称为重新完成全套端到端验收或华为现场验收。

主捕获记录 `blocked=[]`、`pageerrors=[]`；脚本拦截非 GET/HEAD/OPTIONS 网络请求。没有点击提交分析、修改配置等写操作。服务启动自身可能维护副本运行状态，因此不声称 state 副本字节不变；旧验收 state、旧包和批准 HTML 均未作为可写运行目录。

- [主捕获索引](../../../../../../artifacts/reviews/visual-audit-20261102/capture-summary.json)与[细节索引](../../../../../../artifacts/reviews/visual-audit-20261102/detail-summary.json)：页面 URL、可见导航及对应截图文件名。
- [开始身份](../../../../../../artifacts/reviews/visual-audit-20261102/identity-start.json)、[镜像 inspect](../../../../../../artifacts/reviews/visual-audit-20261102/container-inspect.json)、[HTTP 资源摘要](../../../../../../artifacts/reviews/visual-audit-20261102/image-resource-identity.json)。
- [源码/基线/包体保全检查](../../../../../../artifacts/reviews/visual-audit-20261102/preservation.json)、[隔离环境清理](../../../../../../artifacts/reviews/visual-audit-20261102/cleanup.json)、[最终保全和证据清单](../../../../../../artifacts/reviews/visual-audit-20261102/final-verification.json)。
- 原始截图、DOM、命令输出、Git 差异及浏览器脚本均在 `artifacts/reviews/visual-audit-20261102/`；报告另提供 [自包含 HTML 副本](../../../../../../artifacts/reviews/visual-audit-20261102/report.html)，嵌入本文截图，便于直接阅读。

隔离镜像容器、专用 Docker daemon 和本轮基线 HTTP 服务在取证完成后停止；原 4191/8016 保持运行。业务源码、两个批准 HTML、15 个 WSL 交付文件和其他 session 的 8 份未提交文档保持。仅新增本报告/取证材料，并增量更新本审查线入口与记忆；无代码修复、Git 回滚、构建、打包、提交、推送或向其他 session 下发任务。

## 7. 本轮结论及后续边界

当前状态为：**展示审计完成，统一框架一致性不通过；尚未修复。** A01/A02 是必须先处理的核心问题；A03、U03/U04、M03/M04 等为明确可见的局部差异，A04 为正式移动导航整合问题。U02、R02、M02、D01 的真实流程接入有既有设计依据，不能借这些依据改掉四入口框架，也不应盲目删除必需的真实运行交互。

若后续用户要求修复，应以既有四入口和 UI-02/UI-04 加最后 L4/L5 决定为约束：统一各页面外框，保留既有业务/契约能力；逐项对照本报告验证设置往返、来源跳转、桌面/窄屏入口、用户三图和 MA 双页签/配色，并保持 L4/L5 最新展示。这里仅列修复验收应覆盖的问题，不构成本轮修改代码或打包的授权。
