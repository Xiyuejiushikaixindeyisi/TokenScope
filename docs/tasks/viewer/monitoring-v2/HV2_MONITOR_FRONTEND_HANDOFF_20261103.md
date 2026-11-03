# HV2 监控前端总交接 · 2026-11-03

## 初始化自动恢复关闭弹窗竞态修复（2026-11-03）

本项由总设计师重新开放极小产品窗口，**确认是前端竞态，不是只需增加测试等待**。原始独立证据为 `artifacts/reviews/hv2-repair-20261103/e2e-legacy/joint-results/full-real-search-fresh-rea-42e40--inclusive-combined-filters/{trace.zip,error-context.md}`；错误为点击打开运行后input[name=run]消失。UserMonitor的目录自动选择和URL初始化恢复均调用open，回执完成后无条件setModal(false)，因此会关闭其等待期间用户新开的表单并丢失未提交输入。

先添加延迟receipt组件回归、保持产品代码未改作为负向控制：目录自动选择、URL恢复、晚到目录在新建表单打开后再启动自动选择，3项均按预期失败；既有5项及显式打开关闭的正向控制通过（共6通过/3失败）。随后仅给UserMonitor的chooseModel→chooseEntry→open传递closeDialog意图：自动目录选择及URL恢复传false，不拥有用户弹窗关闭权；显式打开仍默认true，成功关闭。没有延长等待、禁止用户打开表单或改布局/身份/取消生命周期。

实际修改仅两个源码/测试文件：

| 文件 | 修复后SHA256 |
| --- | --- |
| apps/viewer/src/features/v2/UserMonitor.tsx | b1b830a425f33008971cd0775e9c2f0adb08d0af776245b296c6b74093213628 |
| apps/viewer/tests/component/user-directory.test.tsx | 44ee7be2d9fec5960407c47ffd9249afc33ed1ebc248be5a74ebf85388d03fd6 |

`npm run typecheck`、`npm run lint`均exit0；`npm test -- --run tests/component/user-directory.test.tsx tests/component/auto-ttft.test.tsx tests/component/user-ranking-fixed.test.tsx tests/component/v2-connection.test.tsx`为4文件27项通过（1.73s），含目录全部9项。证据目录 `artifacts/validation/viewer/HV2-MONITOR-FE-20261103/modal-race/`：negative-control.log、UserMonitor.before.tsx、typecheck.log、lint.log、components.log、handoff.json。负向控制使用延迟fetch回执和真实V2Client/组件，其他S0子视图为原受控替身，不是新浏览器E2E。

本线修复及自测完成，交回总设计师从新候选、新state冷启动独立复验。未启动监听/浏览器、未Git/push/Docker/打包，不将旧候选SHA或先前浏览器通过状态套用到本次新产品增量。

## 第二次定向测试维护增量（2026-11-03）

总设计师回执：hv2-user三项真实浏览器重跑通过（21.2s），MA四项已通过；第二阶段旧功能集合中的v2-ttft用例仍缺指定运行展示就绪。此次仅给 `apps/viewer/tests/browser/v2-ttft.spec.ts` 增加一行：打开receipt后、填T前，等待 `.filter-panel .filter-meta` 包含 `receipt.user_run_id`。原W修改、迟到响应、结果清空及其余断言逐字保留，未修改产品。

测试SHA256由 `07ac98e5aa5e19020ae3a317515ac40ebd6aecefdd70b2de33c980f3aa00de31` 变为 `1a9e2062a7d12d67c41e31a6ff47b877b372425376e83d877c456e3b73e551b5`。`npm run typecheck` exit0；证据 `artifacts/validation/viewer/HV2-MONITOR-FE-20261103/legacy-ttft-readiness-fix/{change.json,checks.json,typecheck.log}`。原candidate.json保持历史身份，由接收方结合两次测试增量核对，不回写旧摘要。

仅测试维护窗口关闭，产品源码窗口继续关闭。未启动服务/浏览器、未Git/push/Docker；本次失败用例由总设计师重跑后继续后续套件，不将其余42项或最终前端状态提前写为通过。

## 定向测试维护增量（2026-11-03）

总设计师真实冷启动复测发现测试定位/就绪问题，授权仅维护 `apps/viewer/tests/browser/hv2-user-discovery.spec.ts`。已将全部用户展示身份断言限定到 `.filter-panel .filter-meta`，避免同时匹配排行metadata；自动TTFT及延迟TTFT在输入T/W前，先等待该展示metadata包含指定user_run_id，避免对恢复中的旧display输入后被正确清空。τ/K/精确比例/历史/模型切换/零POST断言全部保留，没有用固定等待掩盖就绪。

该测试SHA256由 `9d80b20d8e712b30ac2eeb4e3b8b677ea49ab8ed888f34ba03f06c5f19cf277d` 变为 `a1a7fbc1d149b550646c65af96b8e834ce740c72c3672b28e3db3b270d8dd3b1`。这是原50文件候选的单文件测试增量，不回写旧candidate.json或冒称原组合SHA仍代表修改后测试。证据：`artifacts/validation/viewer/HV2-MONITOR-FE-20261103/user-browser-readiness-fix/{change.json,checks.json,typecheck.log}`；`npm run typecheck` exit0。

本线未修改产品源码/import、未运行浏览器/监听/Git/Docker。Windows客户端import测试harness由总设计师处理。总设计师此前回执335项全前端及四项静态/构建检查、13UUID MA四个实际浏览器用例通过，属于接收方证据；本次测试修正仍待其重跑，不代签用户浏览器或最终前端通过。

接收回执：总设计师已核对下述50文件候选并独立审读，6文件75项定点通过（2.02s），源码前后SHA一致；已复制5份新HTTP输入。源码窗口现关闭，等统一冷启动浏览器/视觉，当前不代表最终前端通过。此为接收方回执，本线未再次运行或合并计数。

**MA与用户目录/TTFT接入源码及本线自测完成，候选冻结供独立复审；待总设计师唯一冷启动E2E与视觉复核。** 未代签最终通过，未回到历史RV2/UIR/Git交付任务。MA细节见[正式MA交接](HV2_MA_FRONTEND_HANDOFF_20261103.md)。

## 身份、清单和冻结依据

实际session `01a18c49-d9b4-7a33-8c04-e5a72adfcc24`（2026-11-03两环境ID一致再次核实）。HEAD `d55df94b6e58117a698dbd14667b7836e67cd50f`，本线50个源码/生成/测试/脚本文件均未提交。

证据根目录 E=`artifacts/validation/viewer/HV2-MONITOR-FE-20261103/`。**完整精确路径、逐文件SHA256、输入SHA、包/锁/批准原型不变摘要见 E/candidate.json**。owned_files排序紧凑JSON映射的组合SHA256：

`c4280716635dc0b7e0dd472cf7c98a3f6ac80cacec9125dc02ac09fc09645404`

`E/frontend.patch`只含9个已跟踪文件的diff，必须一并接收41个新增文件。`E/frontend-context.json`是共享前端源码/测试/脚本只读快照，不把其他模块登记为本线所有；`E/status-at-handoff.txt`保留其他会话差异。禁止据全仓status整仓暂存。本线不reset/清理/覆盖其他修改。

两后端冻结清单已逐文件、组合核实，交接前再次一致：

- 用户 `docs/tasks/delivery/HV2_USER_FREEZE_20261103.json`：`4d9e2e5d6c7031ff0aaa266114b92dbcb8684b9a80d722d2cfae9de8ad1d7dc0`，22文件；消费2.1.0，旧2.0.0文件与9个操作兼容断言保留。
- MA `docs/tasks/delivery/HV2_MA_FREEZE_20261103.json`：`9b48fb244963ce153b009a9a2d0d9050d084bd6c1bb43eec27ddf49f313fd9fa`，17文件；旧1.0.0加availability，不改变业务语义、S0或数值。

主要文件分组（全部以apps/viewer为前缀）：

| 部分 | 实际文件 |
| --- | --- |
| 客户端/握手 | src/api/v2/client.ts、openapi-equivalence.ts、user-contract.ts |
| 用户页面 | src/features/v2/UserMonitor.tsx、user-discovery.ts、Ranking.tsx、TTFT.tsx、AutoTTFT.tsx |
| MA页面 | src/features/v2/MAMonitor.tsx、MACharts.tsx、MAAvailability.tsx |
| 生成契约 | generated/ma的AvailabilityResponse.ts/json、availability.openapi.json；generated/user的15个HV2*.ts、hv2-schemas.json、hv2.openapi.json、legacy.openapi.json（均位于src/api/v2） |
| 生成/输入脚本 | scripts/generate-ma-availability.mjs、generate-user-discovery.mjs、prepare-ma-availability-fixtures.py、prepare-user-discovery-fixtures.py |
| 新单元/组件 | tests/unit/{ma-availability,user-discovery}.test.ts；tests/component/{ma-availability,auto-ttft,user-directory,user-ranking-fixed}.test.tsx |
| 新浏览器/投影 | tests/browser/{hv2-ma-availability,hv2-user-discovery}.spec.ts；tests/fixtures/ma-availability.ts、ma-availability-runtime.openapi.json、user-runtime.openapi.json |
| 既有浏览器适配 | tests/browser/v2-acceptance.spec.ts、v2-boundaries.spec.ts、v2-ttft.spec.ts |

本线文档另含本总交接、MA交接、握手修正记录、ENTRY及memory/tasks/viewer-monitoring-v2.md；未修改共享CURRENT/SESSIONS/执行板。

## 用户目录与固定历史

冷浏览器通过GET /monitoring/user-v2/runs完整分页发现所有APPID×模型×历史。首响应snapshot贯穿后续页，记录数/offset/快照一致性检查通过后才一次发布；409 DISCOVERY_SNAPSHOT_CONFLICT清空局部收集，最多3轮从头读。取消或旧响应不再发下一页/覆盖新选择。发现过程不POST绑定、不依赖本机运行记录。

原模型与APPID控件位置不变，原“选择分析结果/打开运行”弹窗中提供完整服务目录、刷新与历史选择，同时保留已知ID/本机最近/新建/绑定入口。is_default只用于首次未固定的模型选择；显式历史保留run/index_revision，并按APPID×model_id×common_name保存固定选择，切模型回来、刷新目录、页面重载不自动换新发布。固定历史缺失或revision变化明确报错，不回退默认。空运行appid=null不列为租户，未知APPID不选其他租户。

原TaskTracker处理中60秒、终态停止、失败保留历史行为保留。快照/排行检查所选run/revision/model身份；排行仍20条、300ms字面搜索、Enter、显式范围、原排序/众数/导出。revision冲突保留一次重读，但继续携带固定revision，不再去掉revision暗换数据；持续冲突须显式重选。初始化计时器不会重置页码的新固定时钟测试通过。

数据质量详情保留原runtime来源，显示Trace模型、run/index和输入/manifest/settings/encoder/asset身份、文件观察时间及固定来源链接。文件时间不作为APPID过滤窗口。产品页面不展示互斥参数说明或提交JSON。

给异常前端消费者的映射（只在交接说明，不要求用户手拼）：

```json
{"source_kind":"user_v2","user_run_id":"所选用户运行","appid":"所选APPID","expected_index_revision":"所选索引版本","window":null}
```

base_run_id仅溯源，不与user_run_id同时提交。`analysisSource(entry)`已实现并测试该完整有效全集映射；`monitorSourceUrl(entry)`生成带run/appid/revision的固定监控链接。**异常页SourceLink.tsx的revision补齐已由总设计师派发异常前端，本线未越界修改；跨异常入口往返整体验证仍待其合入与独立E2E。** 不虚构现有异常路由已消费这些参数。

## TTFT日常操作及历史

保留三栏。日常只输入W与SLO T，默认≤；W空值不等于0，显式0有效。模型参数由GET /ttft/defaults按model_id/common_name成对读取，不硬编码三模型τ。条件弹窗可覆盖K或恢复模型默认，查看来源、参数版本、τ适用K，文案明确“用户提供、尚未校准”。K变化不缩放τ；未知/缺τ明确禁用估算。

显式POST /ttft/evaluations携带submission_key、run/appid/index_revision、W/T、le与所读default_revision；可选K。无scenario/model/O注入。失败后原意图同键重试，改变输入/配置版本后新键；持久记录不触发自动POST。按服务/run/index/APPID/model/common_name隔离组件，操作代次+AbortController阻断旧成功/错误/finally污染新范围。

展示response.evaluation权威status/reason、比例、精确Fraction、P90、块数、可计算Token及limitations；不在浏览器重算公式、不把null补0/100%。历史自动评估用GET /ttft/evaluations/{id}；旧/evaluations/{id}、旧scenarios/{id}/{revision}仅显式只读入口，保留lt/W+O历史。新旧命名空间不混用。

## 契约生成与验证

运行两个独立生成器前逐文件验证后端freeze。用户新增DTO使用冻结2020-12 Schema完整运行校验、不强制转换或补默认；TypeScript tuple生成仅做prefixItems→tuple语法适配，不改运行Schema。原generated/user与generated/ma旧文件保持，新增文件加前缀/独立文件，避免覆盖旧契约。

verifyUserContract严格核对2.1.0的14操作，并将旧9操作仅版本标记提升到2.1.0后再次逐结构比较。MA和用户均在真实运行时读取/openapi.json；本地ref展开消除组件重命名差异，字段/类型/约束/参数/路由/错误响应保留。真实create_app聚合文档fixture及漂移拒绝测试已通过；缺失/外部/循环/sibling引用明确拒绝并有深度/节点上限。尚不能将此单测说成已在真实监听服务握手。

## 实际检查与证据层级

最终环境：WSL Ubuntu22.04 / Linux6.18.33.2，Node22.22.2、npm10.9.7、Python3.11.16，见 `E/final-checks/environment.json`。在apps/viewer执行：

| 命令/集合 | 实际结果 | 证据 |
| --- | --- | --- |
| npm run typecheck | exit0 | E/final-checks/typecheck.log |
| npm run lint | exit0 | E/final-checks/lint.log |
| npm test | 32文件301项通过 | E/final-checks/test.log |
| npm run build | exit0；保留原500kB chunk提示 | E/final-checks/build.log |
| 用户定点4文件 | 41项通过：19单元、15 TTFT、5目录、2固定排行 | artifacts/validation/viewer/HV2-USER-FE-20261103/targeted.log |
| MA定点2文件 | 34项通过 | MA握手记录及上述最终全量日志 |

各集合重叠，不能相加。最终结果/命令/退出码见 `E/final-checks/checks.json`。此前整合299项日志是补排行固定版本2项前阶段，不能取代最终301项。

单元/组件：真实V2Client、严格DTO、fetch替身；目录测试的无关S0展示子组件/快照为受控投影。覆盖全三模型默认、缺W/0、缺τ、K覆盖/恢复、默认版本、新旧意图、延迟/换范围、精确超安全整数Fraction、0/1/null/无预算，目录冷启动/多历史/冲突/身份/延迟，排行固定时钟与revision。后端公式正确性仍由后端独立验收证明，不将合成DTO投影称真实算术复算。

原单元/组件回归保留；浏览器旧TTFT操作从新建情景改为自动默认，旧历史表单改为显式历史类型，保留W=0/禁止O/legacy只读及延迟失效断言。原20+5/大整数/null/revision/并列众数/>200K、导出取消/SHA/记录数未删除。初次测试中的jsdom dialog缺实现、S0时间投影缺9位小数已修测试替身，失败日志保留在HV2-USER-FE-20261103/{ttft-initial,directory-initial}.log，未改后端契约换通过。

## 合成输入与待执行浏览器

三输入脚本均已成功执行（E/fixtures.json），新目录只有合成CSV、**无验收state**，没有启动监听端口或浏览器。实际路径：

```text
/home/zhangxiyue/TokenScope/artifacts/validation/viewer/HV2-MONITOR-FE-20261103/inputs/hv2-user-1.csv
/home/zhangxiyue/TokenScope/artifacts/validation/viewer/HV2-MONITOR-FE-20261103/inputs/hv2-user-2.csv
/home/zhangxiyue/TokenScope/artifacts/validation/viewer/HV2-MONITOR-FE-20261103/inputs/hv2-user-3.csv
/home/zhangxiyue/TokenScope/artifacts/validation/viewer/HV2-MONITOR-FE-20261103/inputs/hv2-ma-matrix-pre.csv
/home/zhangxiyue/TokenScope/artifacts/validation/viewer/HV2-MONITOR-FE-20261103/inputs/hv2-ma-matrix-now.csv
```

user-1/2/3分别GLM/Qwen/DeepSeek，统一APPID hv2-shared，各25行。MA13UUID及说明见MA交接。同目录还有原v2用例所需model-1/2/3.csv、multi-app.csv、mv2-*.csv，共15文件，摘要见candidate.json。重新生成请用全新目录：

```sh
.venv/bin/python apps/viewer/scripts/prepare-v2-fixtures.py <新输入目录>
.venv/bin/python apps/viewer/scripts/prepare-ma-availability-fixtures.py <同一新输入目录>
.venv/bin/python apps/viewer/scripts/prepare-user-discovery-fixtures.py <同一新输入目录>
```

两个新脚本exclusive-create，已有目标会报错，不清空旧证据。已编写但**未执行**浏览器：MA4项、用户3项，分别在hv2-ma-availability.spec.ts/hv2-user-discovery.spec.ts。用户覆盖真实三模型同APPID/历史与新发布/重载、自动TTFT全默认/K恢复/历史读取、延迟真实响应切模型；均自行显式创建合成任务并等待ready/completed，不依赖其他用例顺序。截图/HTTP响应会输出到本次独立测试目录。

总设计师按当前规则先停旧服务/进程/测试容器、确认端口释放，再独立新state/新浏览器唯一冷启动；本线不另开并行旧新服务。由总设计师指定backend/frontend端口和模型资产；启动形态：

```sh
.venv/bin/tokenscope --input-root <上述输入或新生成目录> --state-root <全新state> --cpu-budget 2 serve --host 127.0.0.1 --port <后端端口>
# apps/viewer内；由总设计师启动正式dist或所需源码测试环境
TOKENSCOPE_BACKEND_URL=http://127.0.0.1:<后端端口> npm run dev -- --port <前端端口> --strictPort
TOKENSCOPE_REAL_BACKEND=1 TOKENSCOPE_EXTERNAL_PREVIEW=1 TOKENSCOPE_TEST_BASE_URL=http://127.0.0.1:<前端端口> npx playwright test tests/browser/hv2-ma-availability.spec.ts tests/browser/hv2-user-discovery.spec.ts --workers=1 --reporter=line --output=<新证据目录>
# 另跑原完整v2/导出/S0及共享入口集合；不能用以上7项取代完整E2E。
```

本轮未实际用任何测试端口，未建state，未停其他会话服务；没有需要本线关闭的测试服务。Docker、正式dist实际HTTP、冷重启、视觉及跨分析源链接均由总设计师统一独立复核，不计入本轮通过数量。

## UI保持、待验与授权边界

UI-02 SHA `799786cb3ee52e0931d2482211f82e594ab0f33ad57969232a7ea2ec06d2eaea`、UI-04 SHA `779e6665985fe02e6df9e7d0483ef8111a16a49c2b61fdb27aacbef58d624f5f`与HEAD一致。未改批准HTML、全局样式、app/V2App、共享S0、异常模块或依赖锁；四入口/L4/L5、UIR-01/02保持，UIR-03留V3。原模型/范围位置、排行、TTFT三栏、MA表格/画像/12桶保留；新增状态文字和W输入对高度/移动端的影响尚待实际视觉复核。

剩余限制：无真实浏览器/现场性能证明；大规模历史目录分页扫描成本未现场校准；用户默认τ仍非实测，unknown配置不可借用；源缺cached与预热冲突仍如实显示；Trace审计622条差异不由本线虚构根因；跨异常SourceLink固定revision由归口异常前端补齐后联合验证。

本线未commit/push、未构建/导出Docker镜像、未打包部署或编写华为prompt，未改共享记忆或发送跨会话消息。当前前端源码窗口交回总设计师独立复核；后续Git/构建/交付仅由总设计师按其当前授权统筹，不从本交接推导额外授权。
