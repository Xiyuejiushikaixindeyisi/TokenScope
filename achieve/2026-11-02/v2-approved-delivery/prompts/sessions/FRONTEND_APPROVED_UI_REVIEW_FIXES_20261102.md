> 归档：本文件保存历史过程，不再是执行入口。2026-11-02用户认可V2可交付，UIR-03留V3、不作V2阻断。现场只用真实数据，分两次用户验收，单份Markdown回传。当前见[交付入口](../../../../../docs/tasks/delivery/ENTRY.md)；[逐字节原始快照](../../snapshots/prompts/sessions/FRONTEND_APPROVED_UI_REVIEW_FIXES_20261102.md)。

# 前端恢复 c5 独立复审：两项补充修复 prompt

你继续负责 TokenScope 已批准 UI 的恢复，保持当前四入口框架及最后认可的 L4/L5，不重新设计。先读 AGENTS.md、memory/CURRENT.md、memory/SESSIONS.md，再读 docs/tasks/delivery/APPROVED_UI_INDEPENDENT_REVIEW_20261102.md。登记本人实际环境 session ID，保留所有其他 session 修改，只更新自己的协作状态。

本轮基于 `viewer-approved-ui-restoration-20261102-c5`：HEAD `9f2a3e60394327e4e6bdc41bd688497ddef21dd7` 加22项未提交源码／测试，原交接为 docs/tasks/viewer/monitoring-v2/APPROVED_UI_RESTORATION_HANDOFF_20261102.md。原交接 SHA256 `9392417656e046cfc427dc6a6a42f9c77ec58c981068ce8786f3ef028e86e3a9`，不能只拉main代替候选。独立证据在 artifacts/reviews/approved-ui-independent-20261102，原始文件不改写。

独立回归215单元组件、71个不同浏览器用例、15范围、真实搜索与诊断、111地址同版本重启均通过；四入口与MA主要恢复有效，但下列两项尚未通过。不能用原通过数豁免问题，也不能在修复后沿用c5结果冒称新版已验收。

## UIR-01：补齐降序辅助图（P2，原审计U03未闭环）

复现：用报告所列同候选复现环境，打开 `/#/users?run=ur-7603efaac11849b09b379ea64f873494&appid=synthetic-orders`；在“请求长度分布”选择“降序明细 · 辅助视图”。三图仍写“纵轴：请求数；横轴：Token长度区间”，只有蓝线，无坐标／刻度／网格；“精确值见下表”不对应三个图各自的排序、范围和分页。新环境中使用新生成的有效run/appid，不能硬编码上面的旧ID进测试。

定位：apps/viewer/src/features/distributions/Distributions.tsx 第19行轴说明、第33–36行 DistributionRank；apps/viewer/src/features/requests/Requests.tsx 第28–36行复用的 RankChart。对照 docs/tasks/viewer/monitoring-v2/prototypes/tokenscope-v2-demo-ui02.html 的 drawRankChart（第176行起）。报告及 probe-rank.png、visual-final/approved-rank-1440.png、candidate-rank-1440.png为依据。

修复：沿批准稿恢复 Token纵轴／请求排名横轴、可读刻度／网格及三指标颜色；视图切换时说明同步。精确读数必须能对应当前曲线／当前分段，不能声称不存在或无对应关系的“下表”。保留固定run/appid、原始整数、≤1000条分段、上一／下一段及错误重读；不虚称全量，不增加后端计算或改排序契约，不删除该视图。若复用RankChart，验证原请求明细的辅助图不受影响。

复测：三指标、空数据、0、单点、大整数、首段与后续段、错误重读、切回直方图；1440×1000及390×844检查标签和真实绘图维度一致、绝对排名范围正确、颜色／刻度可读、精确值可追溯。保留分位数、众数、箱宽／请求数／占比、尾桶、明细过滤及导出原断言。按批准HTML展示，不另做图表产品设计。

## UIR-02：修复“跳至内容”导致404（P2）

复现：加载有效用户页、分析报告页、设置页后，用键盘聚焦“跳至内容”，按Enter。用户／设置变为 `#main`，分析变为 `#analysis-main`，显示“页面不存在”，原范围和固定报告参数丢失。三条真实有效路由及操作结果见 skip-link-three-routes-valid.json；probe-skip.png为截图。

定位：apps/viewer/src/components/AppShell.tsx 第10行普通hash锚点，与 apps/viewer/src/app.tsx 第27行hash路由冲突。旧壳已有此问题，本轮公共壳保留了它；不要把来源不同当成免修理由。

修复：保留可用的键盘跳至内容，聚焦并滚动至对应main；保证main可编程聚焦。不得更改当前路由、查询参数或增加错误历史项，不能隐藏／删除skip链接换通过。

复测：用户／排行／MA／分析／设置／旧深链接；Enter后主内容获得焦点，URL、run/appid/model/task、分析方向、历史固定状态、已显示报告不变；前后退正确。增加在c5会失败、修复后通过的行为断言，而非仅断言存在链接。桌面与窄屏均检查。

## 不可破坏的范围与交回标准

- 四个主入口固定为“用户监控、搜索与排行、异常分析、MA集群监控”；设置与兼容深链仍在同一框架，不恢复V1导航。
- UI-02 SHA `799786cb3ee52e0931d2482211f82e594ab0f33ad57969232a7ea2ec06d2eaea`、UI-04 SHA `779e6665985fe02e6df9e7d0483ef8111a16a49c2b61fdb27aacbef58d624f5f` 不改。L4/L5各一卡最多三例、去重及返回保持；Token仅T2–T4。
- FS-01精确run来源、固定历史run竞争修复、缓存／SSE／请求取消、导出取消与SHA／字节／行数校验、0/null和大整数保持。GET不触发分析。后端／契约／锁／S0／模型资产不改，实质问题回审查线归口。
- 新版E2E先核实Windows/WSL旧TokenScope服务、worker、预览和测试容器，停旧并确认PID退出／端口释放；不靠换端口并行。审查方c5服务已停止，仍需开工时重新盘点。新候选使用新空state、真实合成输入、独立dist和全新浏览器。旧包/state/证据保持，不误停其他项目。
- 运行typecheck、lint、单元组件、build及受影响浏览器／联合回归，保留失败与修复链，不删除断言换通过。新建证据目录和候选ID，记录源码／资源／锁／契约／资产及HTTP摘要；截图并排对照批准HTML。
- 新建统一补充交接 `docs/tasks/viewer/monitoring-v2/APPROVED_UI_REVIEW_FIX_HANDOFF_20261102.md`，逐项列UIR-01/02改动、源码行号、复现与复测、18项原恢复保持情况、候选manifest、进程／端口／state／HTTP身份、未决。原c5交接／证据不覆盖；更新自己的入口和记忆。
- 完成后释放前端编辑窗口，交回镜像打包与审查 session `01a1800e-80b4-7400-a78b-a84f5b6e888d` 重新独立复审；不自行宣告用户认可。

**本轮暂不提交、合并、push，不构建Docker，不生成代码／镜像交付包。普通前端build用于验证不等于打包批准；独立复审通过也不自动获得发布授权。**
