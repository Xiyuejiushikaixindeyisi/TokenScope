# UIR-01 鼠标修复独立复审（2026-11-02）

**UIR-01单项通过并关闭；UIR-02及前序已通过能力保持。额外发现既有同文档run切换缺口UIR-03，仍未关闭，因此不宣称整套服务“无未决问题／最终验收通过”。** 用户仅授权本轮鼠标修复及独立复审，本线未扩大源码修复范围，未提交、合并、推送、构建Docker或交付打包。工程结论不代替用户对展示的签字，华为现场未验证。

执行：镜像打包与审查／完整服务总负责；实际环境CODEX_THREAD_ID与CODEX_SESSION_ID均为01a1800e-80b4-7400-a78b-a84f5b6e888d。用户已明确授权将单项问题交前端，已实际发送；前端完成后释放窗口，本线才接管测试服务。源交接：[前端交回](../viewer/monitoring-v2/UIR01_POINTER_FIX_HANDOFF_20261102.md)；[原单项prompt](../../../prompts/sessions/FRONTEND_UIR01_POINTER_FIX_20261102.md)、[c2独立失败记录](APPROVED_UI_FIXES_INDEPENDENT_REVIEW_20261102.md)保持。

## 固定身份与源码审查

候选viewer-uir01-pointer-fix-20261102-c1；HEAD 9f2a3e60394327e4e6bdc41bd688497ddef21dd7，加前序共享未提交及本次增量。不能只凭HEAD/main认定候选。

- 前端交接SHA256：2f201941475efa8b6b8374a643999cf1181c2741a66a0339b3ed30d84f2fd8a5。
- 前端identity-final.json SHA256：0cd0e5aeee23bbda6d3281dd76850be4f6288cfb21a354382b25acbfca45056a。
- 原manifest共1345项，1342项直接匹配；3份前端入口/记忆在manifest后收尾，逐一匹配其final-verification.json补充摘要。实际1345项及共享dirty状态均重新冻结，详见[manifest核验](../../../artifacts/reviews/uir01-pointer-independent-20261102/manifest-check.json)、[本线起始身份](../../../artifacts/reviews/uir01-pointer-independent-20261102/identity-start.json)。不声称1345项均匹配原manifest。
- 相对c2，生产源码只改Requests.tsx；新增rank-pointer.spec.ts、rank-pointer.test.tsx两个测试。完整增量、源码正文和Git差异已保存；[单项差异](../../../artifacts/reviews/uir01-pointer-independent-20261102/preliminary-pointer.diff)、[三文件内容](../../../artifacts/reviews/uir01-pointer-independent-20261102/changed-source.json)。未因共享工作树脏而清理或覆盖其他session修改。

| 本轮文件 | SHA256 |
| --- | --- |
| apps/viewer/src/features/requests/Requests.tsx | 9380f329aeedfaec51ecf8d23f3b5c86d33b52960f41ad23e2c68306cddbe87b |
| apps/viewer/tests/browser/rank-pointer.spec.ts | 38e1ebd8ab7dc3ec195d32cc4b8f0d7d2dd936494525f2cbad73f7e242193d43 |
| apps/viewer/tests/component/rank-pointer.test.tsx | 8d6d5cf2fd8f116f4c62cc900d7206c0c72245a5a1f1d176e1ad8704c5127ed9 |

已阅读实际修复：pointer事件通过getScreenCTM().inverse()将clientX/clientY转换为当前SVG用户坐标，再按原51–384绘图区域取最近索引。矩阵缺失、异常或非有限结果维持已有选点；未缓存旧几何。默认等比布局、颜色、网格/轴、精确整数、键盘、空/单点与每段1000点均保持；没有固定宽屏偏移或拉伸规避。300项非前端保护源码/契约/S0/资产对冻结c5摘要一致；前端锁文件另由1345项全量清单覆盖，未改变。批准UI-02/UI-04摘要分别保持799786cb3ee52e0931d2482211f82e594ab0f33ad57969232a7ea2ec06d2eaea、779e6665985fe02e6df9e7d0483ef8111a16a49c2b61fdb27aacbef58d624f5f。

## 干净环境与实际执行

已读进程argv/cwd并准确停止前端PID3033544，SIGTERM正常退出；WSL与Windows的4191/4193/8016/4175/18061–18065均释放，没有旧TokenScope服务、测试容器daemon/shim并行。无关编辑器/语言服务保留：[停止记录](../../../artifacts/reviews/uir01-pointer-independent-20261102/old-candidate-stopped.json)、[Windows端口](../../../artifacts/reviews/uir01-pointer-independent-20261102/windows-after-old-stop.json)。

独立目录artifacts/reviews/uir01-pointer-independent-20261102；新空state、新合成输入、独立WSL dist与新Chrome contexts。启动PID3043666，service_instance_id 72df8e0a-3b46-454b-9370-cc02a3d8611f；启动时实际GET监控和诊断目录均空，未复制前端state。四资源独立构建、前端交接及实际HTTP SHA三方一致：[冷启动身份](../../../artifacts/reviews/uir01-pointer-independent-20261102/cold-identity.json)、[启动argv/env](../../../artifacts/reviews/uir01-pointer-independent-20261102/server.json)。

| 资源 | SHA256 |
| --- | --- |
| index.html | e4c7e4e0969e52c39bbdc78bb6c48641742d0d75cc79605ef9aed2ae21fa46d6 |
| assets/index-BN_hqTE_.js | 1d18c395fb5aca91bc77b469e58376a087a204f46c786d5bf9502c3ad6e55072 |
| assets/export-validator-rZ4O78aZ.js | e52838c80a214d465b29b1e6049fabe887e80d8077fc5ce121061c8f109e9d41 |
| assets/index-BxqENh7v.css | 7de15a1ce92dc92d4d93a96c70425c1ea22663c5c4653c98cb4d9122ef0254a5 |

DeepSeek合成运行显式设置thinking_disabled并记录CAS版本，仅为新测试state；源契约/模型文件不改。随后显式提交监控/诊断/用户合成任务；读取页面不会被算作提交授权。

| 本线实际验证 | 结果与证据 |
| --- | --- |
| typecheck、lint、WSL build | 全部exit0；[执行记录](../../../artifacts/reviews/uir01-pointer-independent-20261102/checks-linux.json)，大chunk警告保留 |
| 单元/组件 | 26文件226项通过；[日志](../../../artifacts/reviews/uir01-pointer-independent-20261102/unit-linux.log) |
| 监控/MA/TTFT/取消/导出 | 42通过；[结果](../../../artifacts/reviews/uir01-pointer-independent-20261102/monitoring-result.json) |
| 分析/缓存/SSE/历史/partial | 18通过；[结果](../../../artifacts/reviews/uir01-pointer-independent-20261102/analysis-result.json) |
| FS-01两类来源和固定运行 | 3通过；[结果](../../../artifacts/reviews/uir01-pointer-independent-20261102/source-result.json) |
| 真实搜索与联合 | 8通过；[结果](../../../artifacts/reviews/uir01-pointer-independent-20261102/joint-result.json) |
| 原UIR修复行为 | 10通过，含键盘、skip、排行往返/范围、1005条分段；[结果](../../../artifacts/reviews/uir01-pointer-independent-20261102/fixes-result.json) |
| 新鼠标回归 | 4场景、144次点位匹配；[结果](../../../artifacts/reviews/uir01-pointer-independent-20261102/pointer-result.json)、pointer-results中的原始API行/坐标/读数 |
| 本线另写鼠标oracle | 135点全部匹配，0脚本错误/写请求；[结果](../../../artifacts/reviews/uir01-pointer-independent-20261102/independent-pointer-oracle.json) |
| 真实API/独立数据期望 | 15基础范围、29条搜索结果独立oracle、历史ready/default-ready/latest-partial诊断、1005条请求；[基础](../../../artifacts/reviews/uir01-pointer-independent-20261102/base-acceptance.json)、[搜索](../../../artifacts/reviews/uir01-pointer-independent-20261102/search/real-search-api.json)、[诊断](../../../artifacts/reviews/uir01-pointer-independent-20261102/fixture-config/actual-http.json)、[1005](../../../artifacts/reviews/uir01-pointer-independent-20261102/rank-segment-fixture.json) |
| 旧S0历史响应竞争 | 真实响应延迟1200ms，3次目录回调及刷新仍保持指定旧run，无写请求；[记录](../../../artifacts/reviews/uir01-pointer-independent-20261102/history-race.json) |
| 视觉和框架保持 | 40组1440/390截图及DOM，0溢出/脚本错误/写请求；[摘要](../../../artifacts/reviews/uir01-pointer-independent-20261102/visual-final/summary.json) |
| 同版本重启 | 先停3043666并确认端口释放，再启动3097294；120地址SHA一致、4个控制库业务表行数/摘要保持、GET未新增业务；[结果](../../../artifacts/reviews/uir01-pointer-independent-20261102/restart-result.json) |
| 重启后新浏览器 | 来源3＋原修复4＋鼠标4，共11通过；[来源](../../../artifacts/reviews/uir01-pointer-independent-20261102/restart-source-result.json)、[原修复](../../../artifacts/reviews/uir01-pointer-independent-20261102/restart-fixes-result.json)、[鼠标](../../../artifacts/reviews/uir01-pointer-independent-20261102/restart-pointer-result.json)，不重复累加不同用例数 |

本轮不同浏览器用例85，全部0skip/0retry/0flaky。新增鼠标和独立oracle来自真实后端，不注入API数据；既有边界测试含网络/时钟/文件替身，不能把全部85描述为无替身。复用旧测试仅适配路径/导入深度及动态新fixture身份，原断言保留；[改编记录](../../../artifacts/reviews/uir01-pointer-independent-20261102/test-adaptations.json)、[历史fixture映射](../../../artifacts/reviews/uir01-pointer-independent-20261102/analysis-legacy-fixture-correction.json)。

独立135点覆盖S0三指标1440→1920→390→2560→1440连续resize；请求辅助图三种宽度；用户30条与1005条第一、第二段三种宽度。目标取浏览器实际circle中心，期望取实时API对应行；同时核对排名、hash、源记录与精确Token，未复用实现换算公式。

实际查看1920截图确认：首点#1 / synthetic-0 / 源记录1 / 418 Token；第二段#1001 / synthetic-10 / 源记录1001 / 162 Token。见[用户首点](../../../artifacts/reviews/uir01-pointer-independent-20261102/pointer-results/rank-pointer-pointer-uses--105aa-across-viewport-resize-user/user-first-1920-2.png)、[第二段首点](../../../artifacts/reviews/uir01-pointer-independent-20261102/pointer-results/rank-pointer-pointer-uses--5a406-wport-resize-second-segment/second-segment-first-1920-2.png)。前端旧c2负向对照证据原位保留，不冒称由本线重跑了其鼠标负向测试。

四入口名称/顺序、设置同壳、六卡与三图、搜索排行、MA表和趋势/分布、UI-04、L4/L5各一卡每类≤3例、T2–T4及FS-01保持。本次无CSS/布局生产差异；40组证据与实际抽查的用户全页、L4窄屏、宽屏精确读数相符。原18项仍按[恢复交接](../viewer/monitoring-v2/APPROVED_UI_RESTORATION_HANDOFF_20261102.md)追溯，不产生新展示设计或用户认可。

## 新发现：UIR-03 同文档run参数变化没有切换运行（未修复）

优先级P1：URL指向B，展示和任务仍属于A，可能令分享/历史导航身份与显示脱节。本轮独立复现的是同页替换run；同页appid及跨运行back/forward尚未单独复测，不把推断当已证实。

复现（需要本轮保留state重新启动；本轮结束已停服务）：

1. 新浏览器打开 `/#/users?run=ur-4438e8a227b14e7480c4b4928adc32f7&appid=synthetic-app-1`，选择降序辅助视图；元信息为A，图30点。
2. 同一文档仅将hash改为 `#/users?run=ur-843ee8970c3448ae83c9c50de129d75f&appid=synthetic-app-1`，保留其他地址部分。等待后URL已为B，但元信息仍A、曲线30点；B实际首段应1000点。
3. 完整刷新，才载入B并显示1000点。
4. 用冻结c2静态资源在同一个新后端做浏览器响应替换控制（仅静态资源，不启动旧服务、不替换API），相同行为复现；两次均无非GET写请求。

[两版本完整记录](../../../artifacts/reviews/uir01-pointer-independent-20261102/same-document-query-observation.json)、[当前截图](../../../artifacts/reviews/uir01-pointer-independent-20261102/query-switch-candidate.png)、[可运行只读脚本](../../../artifacts/reviews/uir01-pointer-independent-20261102/query-switch-observation.cjs)。源码UserMonitor SHA810f29d3a6918d667bb064cb5ea5704b83b1991d5d9fda8693340d9880d56c25与c2相同；app解析page时剥离query，UserMonitor仅以service identity为key、初始化effect依赖[]读取run/appid，同页query变更不重新open。实际代码和前端只读核对一致；前端未新增修改。

[INTERACTION_V2共同规则及运行选择](../viewer/monitoring-v2/INTERACTION_V2.md)要求URL范围恢复、分享链接校验及切范围身份一致，未找到允许忽略同页run切换的批准条款。因此不能把此问题降格为测试脚本问题或已认可限制。既有FS-01覆盖从分析页面返回（UserMonitor已卸载），未覆盖此边界。

UIR-01按固定目标运行的新文档进行独立鼠标验证是有效隔离；这不豁免UIR-03。UIR-03单列待用户安排后归前端修复；本轮不自动扩大到路由重构。临时复现绕行：完整刷新目标链接或通过“打开运行”校验加载目标；后者是现有实现路径，本线本次未针对UIR-03另行测试其所有边界。正式修复应覆盖A→B、appid、浏览器历史、慢旧响应、防重复请求及现有排行返回，不触发业务计算。

## 失败、修正与收尾

- 核验脚本起初把manifest的protected_unchanged数量当成映射，服务停止前即失败；改为读取冻结保护文件清单，原检查未减少。
- 末尾核验发现tsc -b更新了未跟踪的tsconfig.tsbuildinfo生成缓存（新增测试路径）。已保留生成副本，并仅在恢复字节SHA与开工摘要完全匹配后恢复该缓存，未改源码/测试或其他未提交内容；[记录](../../../artifacts/reviews/uir01-pointer-independent-20261102/generated-cache-restored.json)。
- 独立鼠标脚本从user30同文档切到user1005，30/1000计数不符。最初猜测加载时序，补等待后仍失败，进一步独立确认上述UIR-03。原脚本、进度及错误保留；最终每个目标运行明确打开新文档，再执行同样135点身份/数值断言，未删断言换通过。
- 路由观察脚本初始.filter-meta定位歧义，改为带GB范围标识的实际展示元信息；原脚本保留。[设置与排查记录](../../../artifacts/reviews/uir01-pointer-independent-20261102/setup-correction.txt)。

结束时准确停止本线3097294，正常退出、WSL/Windows端口释放；没有保留预览或旧服务。[结束记录](../../../artifacts/reviews/uir01-pointer-independent-20261102/cleanup-final.json)、[Windows](../../../artifacts/reviews/uir01-pointer-independent-20261102/windows-final-ports.json)。新旧state、输入、截图、失败记录及旧包保留。最后复核源码/资源/锁/契约/模型、1345项身份和其他session脏文件，只有本线4份入口/记忆更新允许变化；旧FS-01交付15文件摘要不变，HEAD未变：[保留核验](../../../artifacts/reviews/uir01-pointer-independent-20261102/preservation-final.json)。

证据根固定为artifacts/reviews/uir01-pointer-independent-20261102；[证据SHA清单](../../../artifacts/reviews/uir01-pointer-independent-20261102/evidence-manifest.json)。本报告不授权提交/push/打包，不把本机合成通过说成华为或生产规模通过。下一步仅处理UIR-03待决及用户展示验收；不得继续引用旧“整体无阻断”结论作为新交付批准。
