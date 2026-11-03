# HV2-R3 异常前端接入交接（2026-11-03）

## 测试维护增量：v2 浏览器 fixture（2026-11-03）

总设计师独立335项及静态/build通过后，定向开放仅测试窗口。本次只改下表两份浏览器测试并新增一份测试辅助文件；c3产品源码、生成器、原18项本线输入SHA逐项未变。原240项被测输入清单作为c3当时证据保留，不覆盖；其中两份浏览器测试的本次变化按此addendum单列，供总设计师693项候选清单追加测试身份。

| 测试增量文件（相对项目根目录） | SHA256 |
| --- | --- |
| apps/viewer/tests/browser/analysis-boundaries.spec.ts | `0804d91be1fc6067085c981eda98cd55331a9d2af9ad139fb2b81b8493ad8e1e` |
| apps/viewer/tests/browser/analysis-review-regressions.spec.ts | `e46156921c9f9b9fb4d8bd6cc759e0f9031cd8d2922cb66f9484fb4fc6a4dcb2` |
| apps/viewer/tests/browser/analysis-v2-fixtures.ts | `562c1fab8ca91bad22ffb9322b104e9f20c3f5ea140081e19be95cf78d6933f8` |

适配内容：显式v2 capabilities响应使用冻结wire Schema；v2 catalog添加每binding×direction的selected_reports，保持原defaults/status/default_eligible不改；测试binding的APPID/model/common/source_kind全部取同一report.scope.source，避免从无关旧目录借用模型绑定。旧报告execution明确not_computed、selected_directions=null、telemetry=null，不造扫描统计；使用目录当前task/scope/status。task路径统一识别`/diagnostics/tasks/{id}`与`/diagnostics/v2/tasks/{id}`，不再误把v2路径的tasks段当task_id。通知仍使用原v1 SSE事件协议。

唯一改变的业务期望：旧“first partial has no automatic default”与已冻结v2策略冲突，改为“published partial自动可读、有部分状态、可显式固定历史”。保留defaults=[]和default_eligible=false的fixture，断言两张原卡自动出现、现有“部分结果”提示可见、旧无默认空态不出现、历史选择正确；继续显式选择并核对mode=history/task。没有把partial改ready。其余历史失败保留/时间/刷新详情、局部证据失败与原收益保留/仅GET、通知对齐和固定详情、取消及晚到响应、分页错误不污染新APPID、来源查询取消、禁用存储、方向恢复、双方向历史task/time断言全部保留，未删除测试或降低产品校验。

实际验证：`node node_modules/typescript/bin/tsc --noEmit` exit0，证据`artifacts/validation/viewer/analysis/hv2-r3-20261103/browser-fixtures-typecheck.log`；另以Node仅加载fixture辅助函数，用冻结AJV Schema核对ready、partial-only、混合方向、双方向四组目录及旧execution投影、v1/v2 task路径，exit0，脚本/日志为同目录`browser-fixtures-check.mjs`/`.log`。这不是Playwright浏览器通过结果。本线没有启动服务、访问根4191、运行浏览器、改产品、Git/push或打包；浏览器执行由总设计师使用其唯一真实环境完成。测试窗口现关闭，等待独立运行结果。

候选 **viewer-analysis-hv2-r3-20261103-c3**，本线实现与无监听自测完成，源码窗口关闭，交 V2 总设计师独立复审。实际环境 session `01a19111-344a-75c1-84e0-14db8be08f4f`。不是旧 UIR/RV2 任务，不代签用户视觉或现场验收；未启动 HTTP/Vite/浏览器 E2E、Docker，未提交、合并、push、部署或打包。

本轮 HEAD `7cbe28621f4e46083bf47f9aa14b011b3cb250c4` 加共享未提交候选，不能仅检出 HEAD 替代被测源码。其他 session 修改保持，未操作 CURRENT/SESSIONS/总执行板、监控/MA模块、共享壳或旧冻结契约。只读准备与 A01–A11 见 [PREP](HV2_FRONTEND_PREP_20261103.md)；后端独立验收依据 [总设计师记录](../../delivery/HV2_INDEPENDENT_ACCEPTANCE_20261103.md)。

## 1. 消费身份与实际修复

生成脚本实际验证四份冻结文件清单组合及最终101项依赖文件 SHA。公共第一关的 prefix 适配按低命中第二关合法覆盖，其历史冻结原件不变。

| 冻结 | 组合 SHA256 |
| --- | --- |
| 公共 | `9ac3e7fd5c5fea9556f957871bb03a0791e79e9404b207462a1cf8e184d7cb8e` |
| 用户2.1.0 | `4d9e2e5d6c7031ff0aaa266114b92dbcb8684b9a80d722d2cfae9de8ad1d7dc0` |
| Token | `14419e5bba5af85a3ffa20d6330b3fa29c2d926bd81ef1f3462e30b118b4f00d` |
| 低命中 | `10f643bc56fa59936dcfd7d17f4aabf1163aba4d479c47662366d13c879e011b` |

新增版本化 `diagnostics-execution-2.json`、原始合成样例副本和 `execution-2-lock.json`；旧 generated 与旧锁不改。capabilities 验证实例、方向、至少一种、只读兼容、路由、选择/预算策略和完整 Schema。Schema 比较完全解析本地 ref，允许定义重命名，保留字段约束及漂移拒绝；没有按 ref 名猜等价或删除 AJV 校验。

| 问题/要求 | 本次行为与对应模块 |
| --- | --- |
| 全 partial 裸入口无报告 | client.ts 显式握手 `/diagnostics/v2/capabilities`，读取 v2 catalog；AnalysisApp 消费 selected_reports。完整分页后核对选中引用、ready优先/partial fallback和最新发布顺序；旧defaults仍按原完整资格校验。无ready才选择已发布非legacy analysis partial，不把partial写为ready。 |
| 跨页/模型/方向混读 | 固定snapshot/event_cursor/选择集，拒绝循环、重复task、选择遗漏/错误；核对binding APPID/model/common/source_kind与scope来源。selected引用可以在后页，等收全再验证。历史显式task优先，不随新发布跳转；迟到响应被取消。 |
| 无建议遮住差异 | 继续分别读report、summary、recommendations、difference-groups；零recipe/空建议不遮住已有差异。旧not_computed不再整体提前遮盖差异读取，但严格保留summary/page availability、数量及引用校验，不虚构旧报告内容。 |
| 状态原因含糊 | GET v2 execution，核验task/scope/终态和明确方向；现有提示/折叠详情分别解释无配方、fragment内部不完整、fragment保留截断、finding保留截断、候选查找截断、比较/编码预算、业务依据缺失。显示扫描/比较/保留维度及规则统计，null为未提供；适用对数null为未单独统计，不写0。 |
| 计量误读 | low_hit rule_coverage由原只读分页读出，校验规则范围和十进制计数/适用状态。发现/保留条数不称请求数，source重读计数和嵌套耗时不做总量图，不把工程遥测全部铺到卡片。 |
| HV2-AF-01 分页缓存丢页 | 首读、加载更多统一调用analysisReportKey，键包含实例、实际契约、task/scope/digest/方向；局部证据缓存也加入契约/方向。补测更多→详情→返回焦点→切方向→缓存重读，第二页保持。 |
| 目录缓存版本误标 | 新目录元数据独立保存于metadata.v2，记录实际discovery-2/execution-2，仍只投影100项、2MiB、7天元数据，不存请求正文；旧v1缓存只读兼容，不改写旧契约身份，不作为自动任务发现来源。 |
| 通知/恢复 | 继续原SSE terminal/reset，重连重新握手与对齐v2目录；心跳不发GET，重复通知不重复对齐，不新增轮询。服务实例/契约变更清正文缓存；v2不可用给明确失败，不吞错回退到v1。旧report-1在v2服务下仍可读，execution not_computed明确说明没有新版记录。 |
| 精确来源跳转 | SourceLink保留FS-01 run/APPID/实例和base/model/common匹配，新增用户2.1.0精确user_run_id+APPID目录核验、manifest/asset/encoder和receipt/index一致检查；跳转携带revision。基准base来源仍走原overview深链，不改成V1整套导航。 |

**SourceIdentity不保存原始index_revision。** 本次revision来自当前核验过的不可变user run receipt及目录，不声称与“原报告索引revision”比较。原报告保存的base/user/model/common/manifest/asset/encoder用于关联核验。无匹配来源或索引变化时阻止跳转，不按相似模型名、文件观察时间或另一运行兜底。用户目录到分析提交映射由监控前端维护：`source_kind=user_v2,user_run_id,appid,expected_index_revision,window=null`，不同时传base_run_id；本页只读，没有新增提交/评估表单或POST分析。

**not_computed边界：** 冻结后端 sealed(present=false) 返回summary difference_group_count=0，差异页也为空；当前实际主路径是computed+零recipe/无建议+已有L4/L5。早期本线试验的“not_computed摘要+computed差异页”只是混合投影假设，不是现场或真实后端复现；最终代码拒绝这种availability不一致。保留初次日志，最终回归验证旧空差异页仍被读取、漂移被拒绝，没有为假设场景放宽契约。

## 2. 批准展示与业务边界

UI-02 SHA `799786cb3ee52e0931d2482211f82e594ab0f33ad57969232a7ea2ec06d2eaea`；UI-04 SHA `779e6665985fe02e6df9e7d0483ef8111a16a49c2b61fdb27aacbef58d624f5f`。四入口、配色、布局、卡片主体和最后认可L4/L5保持；未改全局CSS或共享App/V2App。最终CSS资源摘要与前轮一致，不能因此替代浏览器视觉验收。

L4/L5各一卡，完整RequestKey跨组去重计请求，每类最多3个双侧来源去重代表例子；局部证据/旧group深链/返回位置保持，不逐组造卡。L4只说明消息内容差异，不能推断动态字段浪费或同会话改写。L1–L3完整full/direct_full评估且收益严格>1pp；Token仅T2–T4，保留evaluated/advice、影响请求、输入/计算Token变化、null/0、大整数，不恢复T1/hybrid/Agent/逐项评估。原始冻结例子含旧options中的T1字段只是完整字节副本，不会被前端提交或用于新增T1展示。

UIR-03留V3。现有监控/搜索排行/MA、取消/导出完整性和精确整数回归断言未删；对应源码仍归另一session。页面GET不提交任务，也不为缺配方生成生产业务依据或承诺真实收益。

## 3. 实际验证与证据

证据根：[hv2-r3-20261103](../../../../artifacts/validation/viewer/analysis/hv2-r3-20261103)。最终18项本线源码/生成资源/测试组合 SHA：`61a430bf0ffe931fa5e91713e1a5455b0d518fc2e1293620ed1373cbe105735c`；[identity-c3.json](../../../../artifacts/validation/viewer/analysis/hv2-r3-20261103/identity-c3.json)记录全部逐文件SHA及240项共享前端被测输入。与identity-before-c3逐项一致，验证期间无输入漂移。完整构建包含共享树监控线已实现部分，不把其工作计为本线修改。

实际用WSL Node `22.22.2`绝对路径运行以下工具（等价于对应npm脚本），目录apps/viewer；Python使用项目.venv，不依赖Windows PATH里的其他Node。

| 实际命令 | 结果/证据 |
| --- | --- |
| `node scripts/generate-analysis-execution.mjs` | 101冻结依赖一致，新增资源可再生；freeze-final.log。 |
| `node node_modules/typescript/bin/tsc --noEmit` | exit0，typecheck-c3.log。 |
| `node node_modules/eslint/bin/eslint.js src tests vite.config.ts` | exit0，lint-c3.log。 |
| `node node_modules/vitest/vitest.mjs run` | **35文件/335测试通过**，tests-c3.log；包含共享监控线测试，不与专项重复累加。 |
| `node node_modules/vite/bin/vite.js build --outDir /home/zhangxiyue/TokenScope/artifacts/validation/viewer/analysis/hv2-r3-20261103/dist-c3` | exit0，build-c3.log；普通本地构建，未覆盖共享dist/旧候选，不是交付打包。现有大chunk warning保留，未改构建或包锁消警。 |
| `.venv/bin/python -m pytest tests/integration/analysis/test_execution_v2_integration.py::test_v2_http_and_readonly_legacy --basetemp=artifacts/validation/viewer/analysis/hv2-r3-20261103/testclient-state -q` | **1通过**，testclient.log；实际create_app/TestClient，合成任务、GET零提交/处理和状态文件不变断言；无TCP监听。保留Starlette/httpx弃用warning。 |
| 以`TOKENSCOPE_ANALYSIS_ACTUAL_EXAMPLES=/home/zhangxiyue/TokenScope/artifacts/validation/viewer/analysis/hv2-r3-20261103/testclient-state/test_v2_http_and_readonly_lega0/v2-actual.json`运行execution-v2.test.ts | 当时19项通过，actual-testclient-consumer.log；真实TestClient响应经前端Schema、selected引用和execution身份检查。最后增加的元数据测试使该文件20项，已含335项最终回归；不冒称另一次真实HTTP/browser联调。 |

本线新增/增强覆盖：partial-only裸入口、ready优先、显式历史与组件重挂载、跨页snapshot/selection变化、重复和循环、APPID/model/common/source绑定漂移、实例迟到响应、禁用方向不借报告、SSE心跳/重复terminal/reset/断线重连/停止、零recipe有差异、旧not_computed合法空页及非法混合投影、独立原因/null/0/超安全整数、收益0.5/1/1.1pp与不完整门槛、分页缓存重读/详情返回焦点、来源revision与封存身份。

### 失败与复测链（原件保留）

- typecheck-first.log：状态组件误引未导出的integer且有未使用类型；改为本模块精确BigInt格式化，后续类型检查通过。
- sse-first.log：测试在stream建立前发帧；改成等待连接就绪后保留全部生命周期断言，sse-second.log及最终全套通过。不是删断言或业务吞错。
- 总设计师预审指出more写旧key：统一构造器并新增跨详情/方向重读回归；pagination-source-first.log通过。目录元数据后续另存v2，旧v1不改写。
- [negative-controls.json](../../../../artifacts/validation/viewer/analysis/hv2-r3-20261103/negative-controls.json)：隔离副本加载HEAD原AnalysisApp/SourceLink，仅作为针对旧UI的控制，不替换共享树。裸入口1项按预期失败（0卡片）；source筛选`uses`同时匹配`refuses`，实际6失败/3通过/4跳过，失败包括缺revision、错误user run/来源未拒绝。第三组在隔离新代码故意恢复旧more key，1项失败（重读丢第二页）。共3组负向，完整输出和被替换源码SHA保留，不能称全部旧版本E2E。
- 初始命令的WSL PATH含空格导致shell解析失败，随后用Node绝对路径；一条PowerShell编辑命令引号解析失败、未执行，随后使用正确转义。未触发服务或Git写入。功能失败、修复和最终结果按日志分开，不沿用旧UIR通过数。

## 4. 冷浏览器独立复验交接

本线未创建监听进程/容器，无本线服务需要停止。总设计师开始完整E2E前仍须盘点Windows/WSL的TokenScope旧服务、worker、预览和测试容器，确认归属后停止、确认退出及端口释放；保留旧包/state/证据，独立新state与全新浏览器，不能另换端口保留旧版并行。使用当前冻结后端+精确前端候选，而非只用HEAD或旧dist。

1. 冷空localStorage直接打开 `/#/analysis`：用真实合成后端产生只有published partial的目录，确认无需手输task即可看到L4/L5，时间/范围/部分状态准确；先核HTTP资源与本候选SHA。
2. 同binding×direction构造ready+新partial：仍默认ready；显式历史partial固定task、scope、digest，刷新/重启/SSE新发布不跳走。低命中单选不触发Token；双选分别看各方向，APPID与Trace模型切换不串。
3. computed零recipe且有差异时，建议空态与L4/L5并存；每类一卡≤3去重例子、唯一请求数正确，保留受限提示。旧not_computed在当前后端应为0组，不期待不存在的现场结果。
4. 多页建议与差异、selected引用在后页；中途失败/重试、snapshot变化、无效历史、服务实例变化、前后台/断线重连；重点“加载更多→详情→返回→切方向再回来”第二页/焦点/滚动保持。
5. 逐项核对扫描、比较、保留及业务原因，不用checked或空数组推断；applicable_pairs=null不显示0，不把各规则或嵌套计时相加。低命中>1pp完整门槛和Token量化/建议区分。
6. 原监控来源按钮：精确user run/APPID/base/model/common/manifest/asset/encoder，目录与receipt revision一致；URL使用run+appid+revision；错误发布身份阻止跳转，另一最近运行不覆盖。base老来源仍在统一框架。监控前端源提交使用其冻结2.1.0映射，不加base_run_id或裁剪window。
7. 按UI-02/UI-04及最后L4/L5做1440×1000和390×844截图/DOM对照，测试详情局部证据、返回滚动、四入口及旧深链；连同搜索排行、MA、导出取消/SHA/字节/行数、UIR-01/02现有回归，由总设计师组织。UIR-03仍V3。

本线没有新增需要用户审批的功能范围或后端接口变更。未决为总设计师的真实冷浏览器E2E、视觉复审、后续镜像/现场验收及真实业务策略/收益证据；本线自测不代替这些。源码窗口关闭后如独立复审发现问题，由总设计师重新派发精确修复窗口；无跨会话消息、子Agent、提交或打包动作。

## 5. 精确文件与候选资源摘要

下表由identity-c3.json生成；文档改动另为本交接、本线ENTRY和memory/tasks/viewer-analysis.md。实际日志、隔离负向副本和TestClient state仅在上述artifacts证据目录，不加入交付源码清单。

| 本线文件（相对项目根目录） | SHA256 |
| --- | --- |
| apps/viewer/scripts/generate-analysis-execution.mjs | `c7c85c8589da18dfc6a2de8c0d60e035d9ddb14521778abe794c99c776031386` |
| apps/viewer/src/api/analysis/client.ts | `7b31c411c9394bea38ea0cec71ec7fffcaf50611f7ac635cf85025f0341af0ac` |
| apps/viewer/src/api/analysis/execution-2-lock.json | `22f1e246aece76c6db2903d93ab8844b1d75aeb9427ad28aab5ba465ca745e5c` |
| apps/viewer/src/api/analysis/execution.ts | `ffbd3459d77cacdfbfd7b3bd9f61e03c71eccba67fc51b70ca9aad8e1bca99e0` |
| apps/viewer/src/api/analysis/generated/diagnostics-execution-2.examples.json | `77d248778cd62d6a6bf8d32e0d2b4eed2283e4485b11b3fac4b6f134776a156a` |
| apps/viewer/src/api/analysis/generated/diagnostics-execution-2.json | `0394829eaefbce540bafca552134d9c5e77f0f49b32839a7c9c8faca09b37c1f` |
| apps/viewer/src/features/analysis/AnalysisApp.tsx | `d94b628b1e7c1c3f7ea3ceddf17f877eb10cb7f275aeab727f6a850b3abdd8e4` |
| apps/viewer/src/features/analysis/Evidence.tsx | `d38d58bd5e08b17cbc5aea51f94b8b2067c226fea52a1aeeb0ffcd8851239a19` |
| apps/viewer/src/features/analysis/ExecutionStatus.tsx | `7fdb8db695414de7414dbad4404e8ca99309909e69ebda72c7978a051a8927b0` |
| apps/viewer/src/features/analysis/Reports.tsx | `c39899daa3093e2559a051bf9f55a948eca9283c6d274556d70474b11482c6d8` |
| apps/viewer/src/features/analysis/SourceLink.tsx | `1461d9c5e47006e881caf27e739227b6af51bdde226780c084f286e7f3ea029a` |
| apps/viewer/src/features/analysis/model.ts | `c569d8872d2b049b099e1853f15f5de3c1e0bd9be7c203fc78bb538cdb1f782e` |
| apps/viewer/src/state/analysis-cache-key.ts | `bdc722d19c12b28bc7b46e958082ee1423e38a4f85ee425c0ef051c86a379a0c` |
| apps/viewer/src/state/analysis-metadata.ts | `ecd53d61aab198b8479d92ee890e7744fb27e9ae56a4125f251a6087e7c09b9a` |
| apps/viewer/tests/component/analysis-execution-v2.test.tsx | `5e33c1119a4fe9230dc666d57a56931ad9df61c2129c8716fe3ca10b60382461` |
| apps/viewer/tests/component/analysis-source-link.test.tsx | `422e12fb2d3381e61445385f2baa6e45e11d19fd754f2f3cc18d0a9edac68139` |
| apps/viewer/tests/unit/analysis/discovery-v2-lifecycle.test.ts | `10352ce659bad5d6a6bf2132f3e8f37e3166e7da1dadb966af39fb3c21e672b0` |
| apps/viewer/tests/unit/analysis/execution-v2.test.ts | `0645f7871a0f9d050fcd16a2dd2a6ee85baa02cf54271ccedaba563d874a2442` |

| 本地候选资源（dist-c3） | SHA256 |
| --- | --- |
| index.html | `86fe0481a78142ef94591e828c32234bb47b8faa83e697738eb9caaba418acda` |
| assets/export-validator-rZ4O78aZ.js | `e52838c80a214d465b29b1e6049fabe887e80d8077fc5ce121061c8f109e9d41` |
| assets/index-BxqENh7v.css | `7de15a1ce92dc92d4d93a96c70425c1ea22663c5c4653c98cb4d9122ef0254a5` |
| assets/index-DT_13Mu5.js | `9e50b232776de1f99e8861fb4dea4d8cdb65fa36d1ba39e4d0c66dd7b644d468` |
