> 归档：本文件保存历史过程，不再是执行入口。2026-11-02用户认可V2可交付，UIR-03留V3、不作V2阻断。现场只用真实数据，分两次用户验收，单份Markdown回传。当前见[交付入口](../../../../../../../docs/tasks/delivery/ENTRY.md)；[逐字节原始快照](../../../../snapshots/docs/tasks/viewer/monitoring-v2/APPROVED_UI_REVIEW_FIX_HANDOFF_20261102.md)。

# 已批准 UI 独立复审修复：补充交接（2026-11-02）

本轮角色为已批准展示的前端维护，实际 session ID：01a19111-344a-75c1-84e0-14db8be08f4f。P0 为 UIR-01、UIR-02 及回归中同源的排行路由恢复修复。不重新设计，不修改后端契约。修复和本轮自测完成后交镜像打包与审查 session 01a1800e-80b4-7400-a78b-a84f5b6e888d 独立复审；**不代签用户视觉验收，暂不提交、合并、push、Docker构建或交付打包。**

依据：[补充prompt](../../../../prompts/sessions/FRONTEND_APPROVED_UI_REVIEW_FIXES_20261102.md)、[c5独立复审](../../delivery/APPROVED_UI_INDEPENDENT_REVIEW_20261102.md)、[原18项恢复交接](APPROVED_UI_RESTORATION_HANDOFF_20261102.md)。原c5交接及所有审计/证据/state不覆盖。

## 1. 新候选身份与变更

候选：viewer-approved-ui-review-fixes-20261102-c2。HEAD：9f2a3e60394327e4e6bdc41bd688497ddef21dd7，加c5原未提交修改及本轮6项增量，**不是单独HEAD可代表的发布版本**。完整源码/样式/锁/契约/模型/HTTP摘要在 [identity-final.json](../../../../../../../artifacts/validation/viewer/approved-ui-review-fixes-20261102-c2/identity-final.json)。开工身份与原dirty清单在 [identity-start.json](../../../../../../../artifacts/validation/viewer/approved-ui-review-fixes-20261102/identity-start.json)。本轮仅四个业务源码文件、两个新测试文件；原18项恢复代码不回退。

| 相对 c5 的文件 | SHA256 |
| --- | --- |
| [apps/viewer/src/features/distributions/Distributions.tsx](../../../../../../../apps/viewer/src/features/distributions/Distributions.tsx) | 1e2edc5ea47d72863ac0e23560ac7cfeeeff77a76ea29cad492a3f4f3c059351 |
| [apps/viewer/src/features/requests/Requests.tsx](../../../../../../../apps/viewer/src/features/requests/Requests.tsx) | e7c4db77af94ea8fc8d72771ca57ebad9617a37eb8da5620cef3dd0cbba0be9f |
| [apps/viewer/src/features/v2/UserMonitor.tsx](../../../../../../../apps/viewer/src/features/v2/UserMonitor.tsx) | 810f29d3a6918d667bb064cb5ea5704b83b1991d5d9fda8693340d9880d56c25 |
| [apps/viewer/src/components/AppShell.tsx](../../../../../../../apps/viewer/src/components/AppShell.tsx) | 1d84041078df67c7a5219e6e5559106e74fbd1168ab0db58b7497fb83aab9338 |
| [apps/viewer/tests/browser/ui-review-fixes.spec.ts](../../../../../../../apps/viewer/tests/browser/ui-review-fixes.spec.ts) | 27b9b61570c82edf1f374b9ac1c2bbf06cc9ed7d4ffacd84ca12d2b9f97bd596 |
| [apps/viewer/tests/component/ui-review-fixes.test.tsx](../../../../../../../apps/viewer/tests/component/ui-review-fixes.test.tsx) | e4d88d50fcccc3257278a2c24910a00060e20bf875d9d516cb21520412feee20 |

| 最终实际HTTP资源 | SHA256 |
| --- | --- |
| index.html | 9515e3cf640e96d63aa4664625d29f36c4b8457e6428e4a82328362bc9489942 |
| assets/index-CHXcFvtG.js | bc9852a916576059fde7a4d04dee187d0f9430319e31551b676437c0316f623d |
| assets/export-validator-rZ4O78aZ.js | e52838c80a214d465b29b1e6049fabe887e80d8077fc5ce121061c8f109e9d41 |
| assets/index-BxqENh7v.css | 7de15a1ce92dc92d4d93a96c70425c1ea22663c5c4653c98cb4d9122ef0254a5 |

同源运行服务实例：6bf4dd25-05cd-4d2a-ba50-ff5f5c4a84d7；当前 PID 2899497。唯一预览 [http://localhost:4191/#/users](http://localhost:4191/#/users)。模型、S0、锁和后端301项摘要保持，ignored模型资产对c5权威manifest核对；自身源码和文件身份见manifest，不仅核对Git HEAD。其他session的未提交修改原位保留；没有覆盖CURRENT、SESSIONS或交付线文档。

## 2. 两项修复与附带路由修复

| 项目 | 根因与修复 | 源码入口 | 本轮验证 |
| --- | --- | --- | --- |
| UIR-01 | 三图沿用直方图轴说明，旧canvas无刻度且假设有相邻对应表。改为UI-02 Token纵轴/请求排名横轴、5条网格与刻度、灰蓝/蓝/青三指标颜色；按当前分页offset显示绝对排名。悬停或左右键显示当前点hash、源记录、精确Token，取消不真实的“见下表” | [Distributions.tsx:19](../../../../../../../apps/viewer/src/features/distributions/Distributions.tsx#L19)、[Requests.tsx:28](../../../../../../../apps/viewer/src/features/requests/Requests.tsx#L28) | 1440/390三指标真实排序对API、首段/次段/返回、错误重读、0/单点/空、大整数、切回直方图与请求页辅助图 |
| UIR-02 | 普通hash锚点被路由解析成不存在页面。保留可键盘操作链接，阻止默认锚点导航，为当前main设置tabIndex=-1并focus/scrollIntoView；不写URL/history | [AppShell.tsx:10](../../../../../../../apps/viewer/src/components/AppShell.tsx#L10) | 用户/排行/MA/分析/设置/overview/requests，两宽度Enter后main焦点、URL及history长度、现有报告数保持；前进后退 |
| UIR-02回归附带问题 | 从设置/MA进入排行，恢复最近运行的follow固定写回users，导致排行和历史导航被覆盖。按当前实际hash保留users/ranking；原run/appid恢复逻辑不变 | [UserMonitor.tsx:72](../../../../../../../apps/viewer/src/features/v2/UserMonitor.tsx#L72) | 第一候选UIR-02回归失败留证；第二候选两个宽度和全量既有排行/来源/历史回归通过 |

曲线的数据仍是已有GET /analysis-runs/{run}/requests，sort_by为当前指标、sort_order=desc、limit=1000；没有新计算或后端排序变更。源值始终是十进制字符串/BigInt；仅受限像素值转Number。刻度可缩写，当前点精确值不缩写。空数据不画伪造曲线，0与单点保留。图内读数属于该图自己的当前段，不借用下方独立筛选表。原Requests辅助图复用同一修复，原表格/筛选/详情/导出保留。

## 3. 复现、失败与复测链

- 原始复现按独立审查的两项步骤执行，c5问题来自原审计，不改其原证据。用未改c5 dist资源在独立浏览器中替换静态响应、读取本轮真实后端作负向对照：[c5-negative-control.json](../../../../../../../artifacts/validation/viewer/approved-ui-review-fixes-20261102/c5-negative-control.json)；轴断言失败、skip将有效URL改成#main并进入404。不是将旧服务重新并行启动。
- 新增组件测试第一次存在fixture括号/参数类型错误，后续精确值选择器同时命中SVG title和读数段；失败保留在red-tests/checks系列，修正测试定位后通过。未把编译失败称为有效负向测试；有效c5负向证据是上述浏览器记录。
- 第一候选 fixes.log、fixes-retest.log、fixes-final.log 保留：先发现前进/后退失败，补目标页等待后排除单纯时序；一次目标h1选择器有隐藏页面歧义，改为可见精准heading；最终确认是follow重写排行URL，实施上述源码修复。
- 第一候选已核实PID2793318并TERM正常退出、4191释放，见 [candidate1-stopped.json](../../../../../../../artifacts/validation/viewer/approved-ui-review-fixes-20261102/candidate1-stopped.json)；第二候选重新独立空state、全新浏览器，不复用第一候选数据。
- 第二候选新增10项全部通过，旧71项重新执行全部通过。所有数值/身份/缓存/导出断言保留；artifact测试副本只沿用已记录的模块路径、动态fixture ID、真实输入文件适配，不删除原断言换通过。
- outDir在项目外会保留旧文件：二次本地构建留下一个未被index引用的旧JS。已移出服务目录保存在unused-build-assets，[unused-build-assets.json](../../../../../../../artifacts/validation/viewer/approved-ui-review-fixes-20261102-c2/unused-build-assets.json)记录原摘要；活动入口/模块字节不变。最终服务目录四资源与独立dist-verify完整相等，重新核验HTTP和重启，未删除原构建证据。

## 4. 本轮功能与视觉验证

| 检查 | 第二候选结果 | 记录 |
| --- | --- | --- |
| typecheck/lint/单元组件/build | 25文件222项通过；build退出0 | [candidate2-final-checks.log](../../../../../../../artifacts/validation/viewer/approved-ui-review-fixes-20261102/candidate2-final-checks.log) |
| 新测试最终typecheck/lint | 通过 | [final-test-checks.log](../../../../../../../artifacts/validation/viewer/approved-ui-review-fixes-20261102-c2/final-test-checks.log) |
| 原监控V2/MA/TTFT/取消与完整性/四入口 | 42通过 | [monitoring.log](../../../../../../../artifacts/validation/viewer/approved-ui-review-fixes-20261102-c2/monitoring.log) |
| 原异常分析/SSE/cache/history/partial/返回 | 18通过 | [analysis.log](../../../../../../../artifacts/validation/viewer/approved-ui-review-fixes-20261102-c2/analysis.log) |
| FS-01精确run来源 | 3通过 | [source.log](../../../../../../../artifacts/validation/viewer/approved-ui-review-fixes-20261102-c2/source.log) |
| 真实搜索与S0联合（15范围、1029箱/分位数、CAS/历史/OPFS/SHA） | 8通过 | [joint.log](../../../../../../../artifacts/validation/viewer/approved-ui-review-fixes-20261102-c2/joint.log) |
| UIR-01/02新增行为 | 10通过；两宽度 | [fixes.log](../../../../../../../artifacts/validation/viewer/approved-ui-review-fixes-20261102-c2/fixes.log) |
| 真实API生成 | 15基础范围、搜索、诊断ready/history/partial、1005条分段运行 | [base-acceptance.json](../../../../../../../artifacts/validation/viewer/approved-ui-review-fixes-20261102-c2/base-acceptance.json)、[search-api.log](../../../../../../../artifacts/validation/viewer/approved-ui-review-fixes-20261102-c2/search-api.log)、[fixture-config/actual-http.json](../../../../../../../artifacts/validation/viewer/approved-ui-review-fixes-20261102-c2/fixture-config/actual-http.json)、[rank-segment-fixture.json](../../../../../../../artifacts/validation/viewer/approved-ui-review-fixes-20261102-c2/rank-segment-fixture.json) |
| 服务最终重启 | 118地址SHA一致，业务表不变，GET未新增业务 | [restart-result-final.json](../../../../../../../artifacts/validation/viewer/approved-ui-review-fixes-20261102-c2/restart-result-final.json) |
| 最终资源清理后恢复浏览器 | 10项新增＋3项来源，单独记录，不累计为不同用例 | [restart-browser.log](../../../../../../../artifacts/validation/viewer/approved-ui-review-fixes-20261102-c2/restart-browser.log) |

不同浏览器用例合计81项（原71＋新增10）；旧候选结果不计入。本轮也不以此替代用户视觉认可。首段/后续段采用真实后端1005请求，对三指标分别核对API；大整数90071992547409931、503重读和空数组采用受控网络边界，明确区分真实后端事实与客户端边界注入。

同Windows Chrome、1440×1000和390×844、全新context完成40组批准稿/候选截图与DOM，另有图表局部及真实后续段截图。[visual-final/summary.json](../../../../../../../artifacts/validation/viewer/approved-ui-review-fixes-20261102-c2/visual-final/summary.json)记录无脚本错误、无横向溢出、无非GET写请求。实际查看桌面/窄屏三指标、首段与后续段，标签、刻度、颜色、读数/段范围可见。不要求不同数据的整图像素相等。

| 对照 | 桌面 | 窄屏 |
| --- | --- | --- |
| 批准UI-02降序图 | [visual-final/approved-rank-1440.png](../../../../../../../artifacts/validation/viewer/approved-ui-review-fixes-20261102-c2/visual-final/approved-rank-1440.png) | [visual-final/approved-rank-390.png](../../../../../../../artifacts/validation/viewer/approved-ui-review-fixes-20261102-c2/visual-final/approved-rank-390.png) |
| 新候选完整页 | [visual-final/candidate-rank-1440.png](../../../../../../../artifacts/validation/viewer/approved-ui-review-fixes-20261102-c2/visual-final/candidate-rank-1440.png) | [visual-final/candidate-rank-390.png](../../../../../../../artifacts/validation/viewer/approved-ui-review-fixes-20261102-c2/visual-final/candidate-rank-390.png) |
| 当前曲线局部 | [visual-final/rank-detail-1440.png](../../../../../../../artifacts/validation/viewer/approved-ui-review-fixes-20261102-c2/visual-final/rank-detail-1440.png) | [visual-final/rank-detail-390.png](../../../../../../../artifacts/validation/viewer/approved-ui-review-fixes-20261102-c2/visual-final/rank-detail-390.png) |
| 真实第1001–1005条 | [rank-segment-1440.png](../../../../../../../artifacts/validation/viewer/approved-ui-review-fixes-20261102-c2/rank-segment-1440.png) | [rank-segment-390.png](../../../../../../../artifacts/validation/viewer/approved-ui-review-fixes-20261102-c2/rank-segment-390.png) |

## 5. 原18项逐项保持情况

| 编号 | 本轮保持/补齐结论与证据 |
| --- | --- |
| A01 | 统一AppShell与settings/旧深链保留；UIR-02键盘路径修复，新增两宽度行为通过 |
| A02 | 四入口名称/顺序不改，原42监控及18分析导航断言通过 |
| A03 | SVG/208px/分组/间距/配色未改；40组对照保留 |
| A04 | 窄屏四入口保持，skip和前后退覆盖390 |
| U01 | 六卡/Token去向/TTFT/三图保持；联合15范围数值通过 |
| U02 | 真实运行/历史/已知ID/任务/情景保持；仅纠正恢复时误改排行路径 |
| U03 | UIR-01补齐降序轴、读数、配色；直方图箱宽/占比/众数/分位数/尾桶原断言不删 |
| U04 | 信号、导出入口/取消/校验和请求明细保持 |
| R01 | 20条排行、过滤/排序/上下界/防抖保持，真实搜索回归通过 |
| R02 | 固定run/revision及来源保持，修复最近运行恢复抢回用户页 |
| M01 | 三摘要/全部UUID/蓝青对比未改，MA回归通过 |
| M02 | 实际目录规格/质量入口/展开/历史未改 |
| M03 | 蓝青趋势/刻度/网格/后端整小时均值/12桶/0/null未改 |
| M04 | 页签/分布/200K尾桶/独立样本未改 |
| D01 | 卡片/证据/历史/cache/SSE/partial旧内容保护未改，18用例通过 |
| D02 | L4/L5各一卡、每类≤3例、去重及返回未改；两宽度截图/原断言通过 |
| D03 | Token仍T2–T4，未恢复T1；Reports/Evidence源码未改 |
| D04 | 分析共用四入口和skip修复；FS-01 run来源不回退 |

UI-02 SHA256 799786cb3ee52e0931d2482211f82e594ab0f33ad57969232a7ea2ec06d2eaea、UI-04 SHA256 779e6665985fe02e6df9e7d0483ef8111a16a49c2b61fdb27aacbef58d624f5f 保持。原c5固定历史run竞争修复未动。上述是本轮自测保持情况，仍交独立复审，不能代签用户认可。

## 6. 环境、复现与交回

开工重新盘点：[processes-before.json](../../../../../../../artifacts/validation/viewer/approved-ui-review-fixes-20261102/processes-before.json)、[windows-ports-before.json](../../../../../../../artifacts/validation/viewer/approved-ui-review-fixes-20261102/windows-ports-before.json)；审查方已停c5，本轮未发现存活TokenScope服务/worker、dockerd或测试容器，4191/4193/8016/4175释放。未误停编辑器或其他项目。第一候选退出后第二候选再新建空state；[cold-identity.json](../../../../../../../artifacts/validation/viewer/approved-ui-review-fixes-20261102-c2/cold-identity.json)证明真实空目录、独立service_instance与HTTP资源。旧包、旧state、输入和失败证据全部保留。

唯一候选当前PID 2899497，精确argv/env/cwd：[server-final.json](../../../../../../../artifacts/validation/viewer/approved-ui-review-fixes-20261102-c2/server-final.json)，退出/端口清理：[restart-old-stopped-final.json](../../../../../../../artifacts/validation/viewer/approved-ui-review-fixes-20261102-c2/restart-old-stopped-final.json)、[cleanup-final.json](../../../../../../../artifacts/validation/viewer/approved-ui-review-fixes-20261102-c2/cleanup-final.json)。后端运行工作区原源码；无Docker。固定synthetic输入位于本轮inputs，额外rank-segments.csv是原合成30行循环生成1005行。全部运行/报告ID从本轮API产生，不硬编码旧审查运行。

同候选恢复命令（先按server-final核对当前PID与命令、停止并确认端口释放；只用于明确的同版本恢复测试）：

    cd /home/zhangxiyue/TokenScope
    O=/home/zhangxiyue/TokenScope/artifacts/validation/viewer/approved-ui-review-fixes-20261102-c2
    TOKENSCOPE_RECOMMENDATION_BUNDLE="$O/fixture-config/synthetic-recipes.json" .venv/bin/python -m tokenscope.cli --input-root "$O/inputs" --state-root "$O/state" --asset-root /home/zhangxiyue/TokenScope --cpu-budget 2 serve --host 127.0.0.1 --port 4191 --viewer-root "$O/dist"

UIR复测：先打开source-link-fixture.json指定的user_run_id与appid，再选择降序；三图按左右键读数，对照GET同run/appid/sort_by/offset。rank-segment-fixture.json对应1005条；两类分析来源和固定报告见source-link-fixture/fixture-config/actual-http。键盘在上述七类路由聚焦“跳至内容”并Enter，验证URL不变且main获焦点，再走四入口前后退。Windows测试入口为apps/viewer/tests/browser/ui-review-fixes.spec.ts，设置TOKENSCOPE_SOURCE_LINK_FIXTURE为本轮文件、TOKENSCOPE_EXTERNAL_PREVIEW=1、TOKENSCOPE_TEST_BASE_URL=http://localhost:4191及Chrome执行路径。原回归配置为monitoring/analysis/source/joint.config.cjs；环境与输入生成脚本、全部日志随证据保留。

审查方须核对并停止本候选、确认退出/端口释放，从独立新state、新dist、新浏览器再次冷启动复审，不直接复用本现场作为独立通过。共享前端编辑窗口交回后释放；后续发现由审查方协调归口。本轮无已知未修复功能阻断；仍待独立复审和用户视觉判断。既有大chunk构建警告保留，合成1005条不是大规模性能或华为现场验收。发布/提交/push/打包仍没有授权。
