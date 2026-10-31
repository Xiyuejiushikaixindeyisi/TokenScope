# Token监控V2独立端到端评审（2026-10-31）

结论：**当前候选不通过，3项前端问题待闭环**。用户已通过的页面人工验收保持原结论；本报告新增独立源码、真实HTTP、浏览器和本机容器边界检查，不代替或撤销用户签字。未修改业务代码、契约或统计语义，未进行通过后的Git收口。

维护session：01a1800e-80b4-7400-a78b-a84f5b6e888d，本轮环境CODEX_THREAD_ID/CODEX_SESSION_ID一致核实。范围与授权依据：[三端交接](MONITORING_V2_REVIEW_HANDOFF.md)。本轮允许本机临时测试镜像；未导出镜像、形成代码交付包、发布tag、部署、写华为prompt或操作华为机。

## 候选身份

- main/HEAD及本轮读取的远端main：`5c619f80631dbd0efdcbadffa7eedbf314bb678e`。
- 前端`ef2b96c4f605c2b0482d85914dca26c6cd48b5de`、用户后端`a4053db5789fa9460b1fae4097a8835b2554357c`、MA集成`9a037466f7211126261ec2026f54b9c19c2e2151`均为当前HEAD祖先。没有重新拉main覆盖共享工作区。
- 用户契约2.0.0、MA1.0.0、旧S0 1.0.0。包内已有应用版本仍dev6/F007，不能单凭该版本号识别V2；本轮以源码SHA、契约和逐文件摘要识别。
- [候选逐文件摘要及初始工作区](../../../../../../artifacts/reviews/monitoring-v2-20261031/candidate.json)固定源码、测试、配置、依赖锁、契约与构建入口；结束时无候选文件漂移。
- [冻结身份复核](../../../../../../artifacts/reviews/monitoring-v2-20261031/identity-verification.json)：S0、用户/MA manifest、8个实际模型资产、UI-02合计120个不同路径全部匹配；模型revision/配置以encoding-assets.lock、configs及候选摘要为准。
- 其他会话异常分析/研究/交接修改原样保留；未git add .、reset、切换或合并backup。未创建/通知其他会话。

## 阻断问题及责任交接

### RV2-01 / P1：MA服务身份变化未清除旧范围

责任：监控V2前端。状态：**已在源码服务和容器正式dist复现，未修复，未复测关闭**。

位置：[V2Client错误处理](../../../../../../apps/viewer/src/api/v2/client.ts#L72)。错误事件只识别`INSTANCE_MISMATCH`，但MA经旧S0 guard实际返回`SERVICE_INSTANCE_CHANGED`。TaskTracker虽识别该错误可停止周期查询，MA目录/逐行读取仍不会触发V2App全局清理。

复现：打开已完成MA运行，等13个实例加载；刷新目录时让浏览器请求携带失效服务ID，转发给真实后端，返回真实409 `{error:{code:SERVICE_INSTANCE_CHANGED,message:Reload service identity}}`。页面仅显示错误文案，13行旧实例仍在，重新连接按钮0个。

期望：按交互方案第2节清旧选择/结果、停止旧作用域请求并提供重新连接；不得自动重发POST。建议统一识别两条业务线的身份错误，补目录、快照、回执三条路径的回归，验证请求池取消和迟到响应不重新填回旧数据。不修改后端错误契约迁就前端。

证据：[源码观察](../../../../../../artifacts/reviews/monitoring-v2-20261031/extra-observations.json)、[容器观察](../../../../../../artifacts/reviews/monitoring-v2-20261031/docker-browser/extra-observations.json)、[截图](../../../../../../artifacts/reviews/monitoring-v2-20261031/ma-identity.png)。本次为真实HTTP错误加浏览器请求头故障注入，未破坏实际服务identity库。

### RV2-02 / P1：切换运行后旧导出继续，成功提示落在新范围

责任：监控V2前端。状态：**源码服务及容器均复现，未修复，未复测关闭**。

位置：[用户页独立Exports挂载](../../../../../../apps/viewer/src/features/v2/UserMonitor.tsx#L210)、[Exports仅卸载时取消](../../../../../../apps/viewer/src/features/exports/Exports.tsx#L8)。用户页顶层Exports没有范围key，切换snapshot时组件复用，原AbortController未取消。请求表内的Exports随Requests key卸载，与此顶层实例不同。

复现：GLM运行开始顶层NDJSON导出，延迟真实导出响应；打开已完成Qwen运行，待新范围展示；此时仍有“取消导出”按钮，放行旧响应后下载GLM的30条文件，Qwen范围下出现“30条请求校验完成，SHA256与记录数一致”。文件校验本身没有错，错误在作用域生命周期和提示归属。

期望：运行/APPID/服务或页面范围变化取消旧导出，迟到结果不能更新新范围提示；亦需覆盖CSV和文件写入API路径。建议按完整导出范围隔离组件或显式中止/清理旧任务，并补真实流延迟回归。不能通过删除SHA/记录数校验解决。

证据同上extra-observations，两端均`requested=true`、`pending_after_switch=1`并下载旧base文件；[截图](../../../../../../artifacts/reviews/monitoring-v2-20261031/export-scope.png)。用浏览器支持的下载回退路径验证，主动关闭showSaveFilePicker能力；首次文件选择器被取消的观察保留在extra-initial.json，不算成功导出证据。原始导出字节由真实后端生成。

### RV2-03 / P2：排行初始化搜索计时器重置用户已翻到的页码

责任：监控V2前端。状态：**容器原回归失败＋独立时钟复现，未修复，未复测关闭**。

位置：[Ranking搜索effect](../../../../../../apps/viewer/src/features/v2/Ranking.tsx#L23)。effect首次挂载也无条件在300ms后setOffset('0')，即使search没有变化。

复现：首次载入当前运行排行，300ms内点击下一页；正常请求offset=20并显示第2页，初始定时器触发后又请求offset=0并回第1页。容器正式dist比开发服务快，原v2-boundaries用例实际触发。网络trace显示0→20→0；独立浏览器时钟固定后，先确认5条/第2页，再推进300ms，变20条/第1页。

期望：只有实际生效搜索条件改变才重置页码；初始化与未改变搜索不覆盖用户翻页。保留300ms搜索、回车、条件恢复、revision冲突及精确数值原断言。

证据：[稳定复现](../../../../../../artifacts/reviews/monitoring-v2-20261031/ranking-reset.json)、[复现脚本](../../../../../../artifacts/reviews/monitoring-v2-20261031/ranking.cjs)、[原失败trace](../../../../../../artifacts/reviews/monitoring-v2-20261031/browser-results/v2-boundaries-synthetic-co-acad1-er-null-and-200K-tied-modes/trace.zip)。此25行DTO为严格合成前端投影；真实后端分页/排序另由后端回归及真实排行用例覆盖，不把合成DTO说成生产排行。

## 实际测试矩阵

| 范围 | 本轮结果 | 证据 |
| --- | --- | --- |
| Python全量tests/unit + tests/integration | 381 passed，354.10s；1条Starlette/httpx弃用提示 | [pytest.log](../../../../../../artifacts/reviews/monitoring-v2-20261031/pytest.log) |
| Ruff src/tests、mypy src/tokenscope | 均通过 | [checks.json](../../../../../../artifacts/reviews/monitoring-v2-20261031/checks.json)及同目录日志 |
| 前端typecheck、lint、build | 均通过；Vite已有体积提示 | 同目录typecheck/lint/build.log |
| Vitest全量 | 14文件159项通过 | [test.log](../../../../../../artifacts/reviews/monitoring-v2-20261031/test.log) |
| 源码前端+真实隔离后端 | MA预建1项通过后，完整选定25项通过，1.5m | [browser.log](../../../../../../artifacts/reviews/monitoring-v2-20261031/browser.log) |
| 容器正式dist+同源真实API | MA预建1项通过；13项首轮11通过/2失败 | [容器browser.log](../../../../../../artifacts/reviews/monitoring-v2-20261031/docker-browser/browser.log) |
| 容器失败区分 | boundaries分页失败为RV2-03；ranking等待.metric-grid失败为冷环境缺少mv2-f001-user预建，任务ready后原用例复跑通过 | [ranking-retest.log](../../../../../../artifacts/reviews/monitoring-v2-20261031/docker-browser/ranking-retest.log) |
| 追加边界 | RV2-01/02两环境均确认；RV2-03固定时钟确认 | extra-observations.json、ranking-reset.json |
| 源码服务重启 | 89个GET地址前后响应摘要一致，控制库逻辑摘要不变 | [source-restart.json](../../../../../../artifacts/reviews/monitoring-v2-20261031/source-restart.json) |
| 容器重启 | 同上，独立容器state的89个地址 | [container-restart.json](../../../../../../artifacts/reviews/monitoring-v2-20261031/container-restart.json) |
| 冻结/资产与候选 | 120路径匹配；源码测试前后无漂移；4个容器静态文件逐字节等于本轮dist | identity-verification.json、environment-checks.json |

数字属于不同范围，不能相加声称全部独立案例；预建与复测亦不重复算新用例。25项中V1兼容11项使用严格协议投影/故障注入；V2真实链路亦含模拟异常/大整数边界。新增3缺陷不因旧测试全部通过而关闭。

源码检查覆盖api/user、api/ma、V2Client、TaskTracker/RequestPool、UserMonitor/Ranking/TTFT/MAMonitor、S0 Requests/Exports及后端user service/ranking/estimator、MA service/pipeline和Dispatcher。结合实际回归确认精确Fraction排序/计算、null/0、固定情景/旧W+O、路径根限制、同key恢复、用户base绑定、原子发布/中断恢复、存储故障及三队列接入；没有发现需要修改冻结计量契约的证据。不是对所有未枚举故障作无缺陷保证。

读取/重启补充验证覆盖用户回执/排行/众数、MA目录/回执/实例/质量、历史TTFT情景与评估、S0快照/明细/NDJSON/CSV。检查H+C=P、ETag/304、NDJSON每行SHA/实际条数、CSV14列/行数，前后控制库logical dump摘要相同；没有调用重建接口。终态数据重启可读不等于强杀计算中现场恢复已实测；后者相关代码故障覆盖以pytest范围为准。

## 复现与构建记录

独立合成输入由仓库prepare-v2-fixtures.py生成，位于artifacts/reviews/monitoring-v2-20261031/inputs；新state位于同目录state。没有复用/覆盖前端历史runtime或F006证据。模型1/2/3为各30条合成请求；不是华为真实数据。

命令均在项目WSL执行，浏览器在Windows Edge运行：

```sh
.venv/bin/python -m pytest -q
.venv/bin/ruff check src tests
.venv/bin/mypy src/tokenscope
# apps/viewer内；WSL Node22.22.2/npm锁定环境
npm run typecheck
npm run lint
npm run test
npm run build
.venv/bin/python apps/viewer/scripts/prepare-v2-fixtures.py artifacts/reviews/monitoring-v2-20261031/inputs
.venv/bin/tokenscope --input-root artifacts/reviews/monitoring-v2-20261031/inputs --state-root artifacts/reviews/monitoring-v2-20261031/state --cpu-budget 2 serve --host 127.0.0.1 --port 18031
# Vite单独14173，TOKENSCOPE_BACKEND_URL=http://127.0.0.1:18031
```

浏览器驱动为Windows Node24.19.0及仓库锁定Playwright、Edge156；没有替换项目Node22构建环境。精确测试配置/执行辅助脚本位于[证据目录](../../../../../../artifacts/reviews/monitoring-v2-20261031)：playwright.config.cjs、checks.py、services.py、extra.cjs、ranking.cjs、restart.py。源码选定v2-*.spec.ts及monitoring/full-journey/operations/export-fixture/cache；容器使用同样正式UI用例，排除需要Vite /src动态导入的v2-api及开发harness用例，不向容器伪加Vite服务。先MA预建，再确保mv2-f001-user已ready以消除已有用例的隐式前置。

容器记录位于[本机测试构建目录](../../../../../../artifacts/builds/monitoring-v2-review-20261031)：

- 仅本机测试tag：`tokenscope/local-test:mv2-review-20261031`。
- image ID：`sha256:8fbc284b8b3afc275e203a8a55ade5d6e62d4653446bbd0fb75c8d5daadb3beb`。
- base：`public.ecr.aws/docker/library/python@sha256:a36c24f9cbdf4fd0f52d67f0823eeac19c2028c637cecc392d97f980d4fec56b`；linux/amd64、CPU。
- Docker26.1.4/Compose2.27.1复用项目工具和项目专属daemon；--network=none离线构建，38个锁定wheel，116个上下文文件。
- 原prepare脚本的旧contract字段仅代表S0；本轮临时context/candidate.json额外明确purpose、user_contract2.0.0、ma_contract1.0.0和review_identity。未将旧V1交付manifest冒充V2身份，未修改发布脚本的生产语义。
- 复用compose配置：非root1000:1000、只读根/输入、独立可写state、8CPU/32GiB、专属bridge、宿主回环18032。inspect显示healthy；/healthz、/readyz、/models均200（本轮候选事实，不沿用V1早期ready503）。本机swap能力限制不作为现场能力承诺。
- build-command.json、context/candidate.json、image-inspect.json、compose-resolved.yaml、container-inspect.json、container.log、environment-checks.json记录实际身份/资源/挂载/日志；容器同源OpenAPI/静态资源及两监控后端实际可访问。
- [清理记录](../../../../../../artifacts/reviews/monitoring-v2-20261031/cleanup.json)：本轮源服务/前端、测试容器/网络及专属daemon已停止；测试镜像和state/日志留本机复现。原8000/4173仍HTTP200，未停止。未清理原V1交付或其他session状态。

## 关闭条件与交接

本轮审查结果为不通过，因此没有执行条件性的统一提交/合main/push，也没有制造重复源码提交。当前三端代码本来就在main历史中。其他session未完成文档保持原样；本轮只追加评审结果、自己的记忆/状态及交付入口。

下一步由监控V2前端维护方修复RV2-01/02/03并补回归，审查方在新候选复核源码/依赖摘要，复跑受影响单元/浏览器及正式dist容器边界；冷启动测试前置需显式建立，不通过增加等待掩盖分页竞态。关闭问题后再执行交接约定的Git统一收口。本报告是可读取交接，未自动发送跨session消息或代替用户启动修复。

真实性能校准、代表性现场CSV、华为环境/资源/驱动/旧内核及生产时限仍未由本次合成测试证明。异常分析开发/验收与统一交付阶段保持原安排。
