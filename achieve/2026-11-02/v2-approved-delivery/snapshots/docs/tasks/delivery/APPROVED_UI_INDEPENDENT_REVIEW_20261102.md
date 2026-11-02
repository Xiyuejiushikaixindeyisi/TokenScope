# 已批准 UI 恢复候选 c5：独立复审结果

日期：2026-11-02。审查角色：镜像打包与审查／完整服务总负责。环境实际 session ID：`01a1800e-80b4-7400-a78b-a84f5b6e888d`。范围为[18项原审计](VISUAL_AUDIT_20261102.md)、[恢复 prompt](../../../prompts/sessions/FRONTEND_APPROVED_UI_RESTORATION_20261102.md)及前端新增的固定历史 run 竞争修复。

**结论：独立复审未通过，UIR-01、UIR-02 两项待前端修复。** 四个业务入口已统一，设置不再替换为 V1 外框；MA 配色、页签、刻度及 L4/L5 各一卡最多三例已核查。工程回归通过不能覆盖下述两项实际问题，也不代表用户视觉认可。本轮未改业务源码，未提交、合并、push、构建 Docker 或生成交付包。

## 1. 候选与干净环境

| 项目 | 实际身份／操作 |
| --- | --- |
| 前端交回 | [APPROVED_UI_RESTORATION_HANDOFF_20261102.md](../viewer/monitoring-v2/APPROVED_UI_RESTORATION_HANDOFF_20261102.md)，SHA256 `9392417656e046cfc427dc6a6a42f9c77ec58c981068ce8786f3ef028e86e3a9` |
| 候选 | `viewer-approved-ui-restoration-20261102-c5`；HEAD `9f2a3e60394327e4e6bdc41bd688497ddef21dd7` 加 22 个未提交源码／测试文件。不是新发布版本 |
| 源码固定 | 488 文件逐项对前端最终 manifest；开始与结束全部匹配。保存 tracked diff 与 4 个 untracked 文件原文；不以 HEAD 单独代表候选 |
| 批准基线 | UI-02 `799786cb3ee52e0931d2482211f82e594ab0f33ad57969232a7ea2ec06d2eaea`；UI-04 `779e6665985fe02e6df9e7d0483ef8111a16a49c2b61fdb27aacbef58d624f5f`；最后 L4/L5 决定覆盖旧逐组展示，T1 不恢复 |
| 停止前序候选 | 核实 PID2680003 完整 argv/cwd 后 TERM；正常退出。Windows/WSL 的4191、4193、8016、4175及本项目旧验收端口释放，未通过另换端口并行验收 |
| 独立环境 | 本线新建空白 `artifacts/reviews/approved-ui-independent-20261102/state`；新 inputs/config；真实 worker 重新生成监控、MA、搜索与诊断结果。没有复用前端 state-5 |
| 构建与启动 | WSL Node22.22.2 独立 build 到本线 dist；同工作区 Python CLI、CPU预算2、4191同源服务。新 service_instance_id `444e3586-5cfd-4ab1-9e6a-1eba1976b495` |
| 浏览器 | Windows Chrome，新 context；不使用个人浏览器缓存。1440×1000、390×844 |
| 结束 | 本线初始服务 PID2703727 在恢复测试前正常退出，重启 PID2750845 完成验证后也正常退出；当前没有保留候选预览，旧 state/输入/日志全部保留 |

四项独立构建资源与前端交回、实际 HTTP 均同摘要：

| 文件 | SHA256 |
| --- | --- |
| index.html | `2c41b7bff760f46d86c54ae57174d86068db4e34b45efba304ca7c555edfa0e4` |
| assets/index-CEgv_duI.js | `663658cdfbf37d0b877fbf444710c0e8bd3025b9240d4b9f1292ffb869287f19` |
| assets/export-validator-rZ4O78aZ.js | `e52838c80a214d465b29b1e6049fabe887e80d8077fc5ce121061c8f109e9d41` |
| assets/index-BxqENh7v.css | `7de15a1ce92dc92d4d93a96c70425c1ea22663c5c4653c98cb4d9122ef0254a5` |

权威记录：[开始身份](../../../artifacts/reviews/approved-ui-independent-20261102/identity-start.json)、[停止前序候选](../../../artifacts/reviews/approved-ui-independent-20261102/old-candidate-stopped.json)、[冷启动与 HTTP 身份](../../../artifacts/reviews/approved-ui-independent-20261102/cold-identity.json)、[输入摘要](../../../artifacts/reviews/approved-ui-independent-20261102/input-identity.json)、[最终清理](../../../artifacts/reviews/approved-ui-independent-20261102/cleanup-final.json)。

## 2. UIR-01：降序辅助图仍使用错误轴说明，缺少批准的读数表达（P2）

**复现：** 启动本报告保留的同候选环境，打开 `/#/users?run=ur-7603efaac11849b09b379ea64f873494&appid=synthetic-orders`；在“请求长度分布”将“分布视图”切为“降序明细 · 辅助视图”。

实际三个卡片均继续写“纵轴：请求数；横轴：Token 长度区间”；若先选占比则仍写请求占比。但绘制的是按长度降序排列的请求，应该以 Token 长度为纵轴、请求排名为横轴。当前 canvas 只有蓝色折线，没有批准稿中的坐标、刻度、网格和三个指标的颜色区分。图注“精确值见下表”也不成立：三个图卡内没有对应表；页面下方请求表有独立排序、筛选和分页，不能自动代表三个曲线的当前分段。

源码定位：[Distributions.tsx](../../../apps/viewer/src/features/distributions/Distributions.tsx) 第19行不按视图切换轴说明，第33–36行新增 DistributionRank；复用 [Requests.tsx](../../../apps/viewer/src/features/requests/Requests.tsx) 第28–36行旧 RankChart，后者只有固定蓝线及“下表”文案。本轮将旧组件直接用于三图，暴露其原来依赖相邻表格的假设；没有证据指向后端排序或统计错误。

批准 UI-02 的 `drawRankChart` 从第176行起含 Token／请求排名坐标、网格和指标颜色。必须按原稿恢复，不再设计新图，也不将曲线删除来避开问题。

**修复要求与复测：** 区分直方图与降序图文案；按批准稿恢复轴、刻度、网格、颜色及可对应的精确读数。保持已有固定 run/appid、整数精度、每段≤1000条与分段读取；不把局部分段称为全量，也不把原型合成数据搬入页面。对三指标、0/单点/空数据、大整数、首段及后续段、错误重读、切回直方图在1440/390宽复测；断言标题与实际数据维度一致、排名范围正确、精确值能对应当前曲线。保留下方明细筛选、导出和来源功能。

证据：[实际复现 JSON](../../../artifacts/reviews/approved-ui-independent-20261102/independent-probes.json)、[问题截图](../../../artifacts/reviews/approved-ui-independent-20261102/probe-rank.png)、[批准降序图](../../../artifacts/reviews/approved-ui-independent-20261102/visual-final/approved-rank-1440.png)、[候选降序图](../../../artifacts/reviews/approved-ui-independent-20261102/visual-final/candidate-rank-1440.png)。对应原审计 U03 尚未闭环。

## 3. UIR-02：“跳至内容”破坏 hash 路由并进入404（P2）

**复现：** 在有效用户监控、异常分析或设置页，键盘聚焦“跳至内容”，按 Enter。用户／设置地址变成 `#main`，分析变成 `#analysis-main`，页面标题为“页面不存在”，原 run/appid/task/direction 等查询参数丢失。

已独立验证三条带有效运行或报告的路径，均先等待业务页面加载后再操作：

- 用户：`/#/users?run=ur-7603efaac11849b09b379ea64f873494&appid=synthetic-orders`。
- 分析：`/#/analysis?binding=f860b372ec762939acba36cbffbfebab82e97836215f52df683a96900b0e2256&task=e2d80f0d-7226-4bc5-9f33-9d75f0734d7c&direction=low_hit&mode=history`。
- 设置：`/#/settings?run=26174973-b01f-435d-9eda-50d44cbb91f3&appid=synthetic-orders&model=GLM-5.2`。

源码：[AppShell.tsx](../../../apps/viewer/src/components/AppShell.tsx) 第10行是普通 hash 锚点；[app.tsx](../../../apps/viewer/src/app.tsx) 第27行将 hash 当路由解析，导致 `#main`／`#analysis-main` 不是合法页面。旧壳已有相同写法，本轮统一组件继续保留；不能说是本轮首次引入，也不能因为是旧缺陷就将新统一框架判定无问题。

**修复要求与复测：** 保留键盘跳至内容能力，移动焦点／视口到对应 main，不能修改路由或追加破坏返回行为的历史记录；main 应可编程聚焦。覆盖用户、排行、MA、分析、设置及旧深链接，Enter 后主内容获得焦点，URL、run/appid/model/task、方向、报告与固定历史均保持；前后退仍正确。不能隐藏或删除 skip 链接换通过。增加能在当前候选失败的回归断言。

证据：[三条有效路由复现](../../../artifacts/reviews/approved-ui-independent-20261102/skip-link-three-routes-valid.json)、[404截图](../../../artifacts/reviews/approved-ui-independent-20261102/probe-skip.png)。初次补充探针的 settings 使用了不存在的 fixture 字段，生成 `run=undefined`，保留 `skip-link-three-routes.json` 原文；本结论使用已修正真实 base_run_id、等待设置加载后的 valid 记录，不依赖该错误样例。

## 4. 原18项逐项复核

以下是本线代码、浏览器和视觉核查结果，不是用户最终签字。全部图片与 DOM 位于[视觉索引](../../../artifacts/reviews/approved-ui-independent-20261102/visual-final/summary.json)，40组页面捕获另有1张 MA 细节图；无 pageerror、横向溢出或非GET写请求。原型与正式合成数据不同，不要求数值或整张截图像素相等。

| 编号 | 复审观察 | 结果／证据范围 |
| --- | --- | --- |
| A01 | settings／旧深链接保留四入口与原功能，返回用户运行可用 | 结构修复有效；全壳键盘路径另有 UIR-02 |
| A02 | 用户、排行、MA、分析、设置共用 AppShell，主导航仅四项、顺序一致 | 源码＋42监控＋18分析；未出现 V1 侧栏 |
| A03 | SVG、208px侧栏、分组间距及当前模块标题恢复 | 两视口截图／DOM；不以静态稿的演示标记作为正式文案 |
| A04 | 窄屏四入口齐全，分析含搜索排行，导航不堆成大块 | 390宽外框断言、全页面无横向溢出；键盘另见 UIR-02 |
| U01 | 六卡3×2、Token去向、TTFT与三图仍在 | 15范围精确数值、1029箱及独立分位数断言通过 |
| U02 | 新建／打开／历史／已知ID／任务状态保留，TTFT缺参不造结果 | 42监控及joint；真实操作与静态样例的差异有交互依据 |
| U03 | 直方图控件、众数摘要恢复；新增的降序视图未完整还原 | **未通过：UIR-01** |
| U04 | 顶部导出、紧凑信号空态恢复；请求明细仍支持筛选和导出 | 取消、真实SHA损坏中止、空结果及响应丢失恢复通过；不将真实30行等同原型样例行数 |
| R01 | 筛选／排序／上下界／表格／20条分页保持 | 29APP真实合成搜索API与浏览器，大小写、字面量、边界及分页通过 |
| R02 | 显式范围、运行／revision及返回路径保持 | 固定历史run与来源3项通过 |
| M01 | 三摘要、13个UUID、蓝青配对条、全部实例与两页签保持 | MA真实fixture与浏览器；0/null与集合差异保留 |
| M02 | 真实目录横排规格、表头质量入口、展开详情恢复 | 总览／质量截图及MA用例；历史和已知ID仍可用 |
| M03 | 请求蓝／重算青，Y刻度、网格及均值线恢复 | 人工查看MA细节；小于1的压力可读；NULL断点、0点及整小时后端均值保持 |
| M04 | 填充选中态、分布刻度和众数摘要恢复 | 趋势／分布切换、箱宽／纵轴、200K尾桶用例 |
| D01 | UI-04范围、类别、卡片、详情、通知、历史/cache保持 | 18个不同分析用例；错误／partial保留旧报告 |
| D02 | L4/L5各一卡，详情最多三例；跨组去重、旧group链接与返回保持 | 桌面／窄屏L4/L5截图及分析断言；未恢复逐组造卡 |
| D03 | Token只含T2–T4；真实收益／局部证据保持 | 源码未改Reports/Evidence、18分析；未恢复T1 |
| D04 | 分析使用相同四入口，FS-01精确run来源跳转保持 | 来源3项及重启后重复3项；全壳键盘另有 UIR-02 |

Token首屏部分证据是既有懒加载提示，截图不代表所有卡片局部证据已经加载；对应证据展开与错误恢复由分析浏览器用例验证。没有将静态截图数作为全部功能通过数。

## 5. 本线实际验证

| 检查 | 独立结果 | 记录 |
| --- | --- | --- |
| typecheck／lint | 均退出0 | [checks.json](../../../artifacts/reviews/approved-ui-independent-20261102/checks.json)及对应log |
| 单元／组件 | 24文件、215项通过 | [unit-linux.log](../../../artifacts/reviews/approved-ui-independent-20261102/unit-linux.log) |
| WSL生产前端build | 通过；4资源匹配交回及实际HTTP | [build.log](../../../artifacts/reviews/approved-ui-independent-20261102/build.log)、cold-identity.json |
| 监控浏览器 | 42通过 | [monitoring.log](../../../artifacts/reviews/approved-ui-independent-20261102/monitoring.log) |
| 分析浏览器 | 17通过＋修正旧fixture链接后该1项通过，共18个不同用例 | [analysis.log](../../../artifacts/reviews/approved-ui-independent-20261102/analysis.log)、[单项复测](../../../artifacts/reviews/approved-ui-independent-20261102/analysis-legacy-retest.log) |
| 来源／联合 | 3＋8通过；不同浏览器用例合计71 | [source.log](../../../artifacts/reviews/approved-ui-independent-20261102/source.log)、[joint.log](../../../artifacts/reviews/approved-ui-independent-20261102/joint.log) |
| 真实合成API | 三模型15范围、29APP搜索、重新生成的ready/history/partial诊断 | [base-acceptance.json](../../../artifacts/reviews/approved-ui-independent-20261102/base-acceptance.json)、[搜索oracle](../../../artifacts/reviews/approved-ui-independent-20261102/search/real-search-api.json)、[诊断身份](../../../artifacts/reviews/approved-ui-independent-20261102/fixture-config/actual-http.json) |
| 固定历史run竞争 | 在旧snapshot实际HTTP响应上延迟1200ms，目录至少两次重读；最终3次catalog、快照和刷新仍固定旧run；无写请求 | [history-race.json](../../../artifacts/reviews/approved-ui-independent-20261102/history-race.json) |
| 同候选服务重启 | 111地址逐字节SHA一致，service_instance不变；四个控制库业务表行及内容摘要一致，读取未新增业务记录 | [restart-result.json](../../../artifacts/reviews/approved-ui-independent-20261102/restart-result.json) |
| 重启后新context | 来源3＋四入口2再次通过，不重复计入71 | [restart-source.log](../../../artifacts/reviews/approved-ui-independent-20261102/restart-source.log)、[restart-monitoring.log](../../../artifacts/reviews/approved-ui-independent-20261102/restart-monitoring.log) |
| 独立问题探针 | UIR-01／02稳定复现，未修复 | 第2、3节证据 |

`app.tsx`／`snapshot-coordinator.ts` 新增的历史run竞争修复是实际行为变更，本线单独验证，没有按“纯展示”免测。读取探针和恢复检查未发现GET触发计算；这不等于断言SQLite整体字节或内部分配器计数恒定。错误注入、断网和导出校验边界沿已有受控网络方法验证，不称所有用例都没有网络替身。本次不是Docker或华为现场验收，不覆盖15万规模性能或生产TTFT校准。

设置／fixture失败单独归类，未掩盖：PowerShell脚本受AllSigned阻止后未执行，未改变策略；Windows原生依赖不匹配导致Vitest启动失败，转WSL同源码后215通过；复制用例的相对路径先修正；旧group测试硬编码了前端任务ID，改为本线实际历史任务及L4组ID后只复测该项，保留原断言和失败trace；冷启动诊断探针补必需实例header；首次视觉脚本误选不存在的hist值，改为histogram后另存visual-final，原失败目录保留。没有将上述设置错误报成后端缺陷，也没有删除断言或跳过用例换通过。

## 6. 保全、交回与下一轮

488文件及两批准HTML、22项候选改动、handoff、15个WSL冻结交付文件保持；HEAD不变。其他session原有未提交内容保留，本线只新增review证据、本文与修复补充prompt，更新本线入口／记忆／协作状态。保全见[preservation-final.json](../../../artifacts/reviews/approved-ui-independent-20261102/preservation-final.json)。旧原审计与前端原始失败、自测证据均保留。

当前前端候选未通过；可直接转发[两项补充修复prompt](../../../prompts/sessions/FRONTEND_APPROVED_UI_REVIEW_FIXES_20261102.md)。修复后以新的候选标识和manifest交回，不覆盖c5原始证据；本线再从停旧服务、新空state、新浏览器冷启动独立复审。不得借修复重新设计、回退L4/L5或删除现有业务。修复及独立复审通过仍不等于用户认可，也不自动授权提交／push／镜像或交付打包。

本次候选服务已停止。如仅需复现同版本，先确认无其他TokenScope服务，再根据 `artifacts/reviews/approved-ui-independent-20261102/server-restarted.json` 的 command/env/cwd 启动，使用该报告保留的state；这只是同版本问题复现，不能作为下一新版的干净验收环境。不要照抄旧PID杀进程。
