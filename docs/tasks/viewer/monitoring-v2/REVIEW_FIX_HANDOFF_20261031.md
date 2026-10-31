# 监控V2独立评审问题修复交接 · 2026-10-31

**前端修复及自测完成，待独立复审。** 接收方：“镜像打包和审查”session，由用户转交；本会话未发送跨会话消息，不代审查方关闭问题或宣布最终联合通过。

维护者实际环境 CODEX_SESSION_ID / CODEX_THREAD_ID 均为 `01a18c49-d9b4-7a33-8c04-e5a72adfcc24`。本轮只修 RV2-01/02/03、回归前置及本线交接。未改后端、契约、计量、精确数值、导出校验或 UI-02 配色布局；未构建/导出镜像、打包、部署、写华为 prompt、提交、合 main 或 push。

## 候选与材料身份

审查基线及本轮 HEAD 均为 `5c619f80631dbd0efdcbadffa7eedbf314bb678e`。修复为**未提交工作区差异**，没有新的修复 SHA。开始时前端目录无差异；其他会话已有文档及异常分析源码差异保留。未 reset、清理、拉 main 覆盖工作区或暂存文件。

本轮证据根目录：`artifacts/validation/viewer/RV2-FIX-20261031/`（下文简称 E）。[候选清单](../../../../artifacts/validation/viewer/RV2-FIX-20261031/candidate.json)记录源码/测试/脚本/配置/依赖锁逐文件 SHA256、全部21个前端未提交文件、合成输入摘要。其排序文件摘要映射的聚合 SHA256 为：

`6202ff3db40686320b7ec194a855fcce5a35560abb35808fc56267387662884d`

`E/frontend.patch`保存已跟踪前端差异；新增测试原文件亦须一起接收，不能只应用 patch。`status-before.txt`、`status-after.txt`区分共享工作区背景；不能据全仓库 status 将其他会话修改纳入本批提交。

前端修复文件清单（均相对 `apps/viewer/`）：

- 源码：`src/api/v2/client.ts`、`src/state/v2-pool.ts`、`src/features/v2/V2App.tsx`、`MAMonitor.tsx`、`UserMonitor.tsx`、`Ranking.tsx`，以及 `src/features/exports/Exports.tsx`、`export-controller.ts`。
- 单元/组件：`tests/unit/v2-client.test.ts`、`v2-pool.test.ts`、`v2-task.test.ts`；新增 `tests/component/export-scope.test.tsx`、`v2-connection.test.tsx`。
- 浏览器：新增 `tests/browser/v2-fixtures.ts`、`v2-review-fixes.spec.ts`；修改 `v2-acceptance.spec.ts`、`v2-boundaries.spec.ts`、`v2-ranking.spec.ts`、`v2-ttft.spec.ts`、`v2-user.spec.ts`。
- 输入生成：`scripts/prepare-v2-fixtures.py`新增两个APPID的合成文件，仍不覆盖既有输入。

文档只维护本交接、ENTRY、`memory/tasks/viewer-monitoring-v2.md`及共享 CURRENT/SESSIONS 内本线状态。依赖和锁文件无变更。[不变性核对](../../../../artifacts/validation/viewer/RV2-FIX-20261031/unchanged.json)：140个冻结契约、UI-02原型、S0、样式和导出协议路径与 HEAD 一致；原评审 JSON 列出的14个证据摘要全部一致。原报告及原证据只读，未改审查结论。

## 逐项修复与验证层级

### RV2-01 / P1：MA身份错误清理

修复前：独立评审的真实请求头故障注入返回 `SERVICE_INSTANCE_CHANGED`，客户端只识别用户侧 `INSTANCE_MISMATCH`，13行旧MA数据仍显示、无重新连接入口。修复前证据为原评审 `extra-observations.json`、`ma-identity.png`及容器对应记录，未在本轮重写。

修复：V2Client 同时识别两个已存在的错误码；身份失效同步 abort 客户端 lifetime，再派发全局清理事件。所有请求组合 caller/lifetime signal，发起前及读取响应后检查取消，因此排队调用和忽略取消的迟到响应不能重新进入旧范围。RequestPool 直接监听该 lifetime，同步清队列/取消最多4个在途请求；MAMonitor 卸载继续清理任务、订阅和池。TaskTracker 原有两错误码终止规则保留。V2App 增加连接代次，旧连接的晚到 catalog 不得恢复失效客户端或抢占重新连接。

自测结果：

- **真实 HTTP + 请求头故障注入**：MA目录、实例快照、回执三路径均从真实后端取得409，旧表及画像入口清除，出现重新连接，无自动 POST。实例路径保留其他在途真实响应后放行，旧行不恢复，最多4个请求，不再释放排队项。
- **运行中DTO投影 + 真实身份错误**：先以严格回执投影进入 running，60秒轮询得到真实409，之后推进180秒无新增读取，历史表清除、无POST。
- **故障注入**：普通503/断网刷新目录仍保留13行历史，不出现身份重连；原用户侧身份回归继续通过。
- **单元/组件替身**：两错误码的客户端取消/禁止后续GET和POST、忽略signal的迟到响应、RequestPool同步停止、TaskTracker停止周期查询，以及旧连接迟到不能覆盖重连。

证据：`E/browser-connection.log`；`E/browser-connection-results/v2-review-fixes-RV2-01-real-MA-identity-error-{catalog,snapshot,receipt}/identity-*.png`；`E/browser-poll.log`；`E/test.log`。后台任务running为测试投影，不能称真实长任务恰好在轮询时重启；身份错误响应本身来自真实后端。

### RV2-02 / P1：导出范围隔离

修复前：顶层 Exports 随 snapshot 复用，仅卸载时取消；GLM的真实导出被延迟后切Qwen仍能下载旧文件，并把旧成功提示放在新范围。原 `export-scope.png` / `extra-observations.json` 为浏览器下载回退路径证据；原 `extra-initial.json` 的文件选择器取消不作为成功证据。

修复：Exports 内部按完整 snapshot.identity、filter、sort 键隔离任务；顶层另外绑定 user_run_id。旧组件卸载 abort 并撤销当前 controller，成功、失败、finally均验证归属。用户监控进入排行时卸载顶层导出和请求表导出（原先只是隐藏页面）；离开到MA/V1、服务身份清理仍由原页面卸载处理。beginExport 在文件选择返回、准备发请求及发起浏览器下载前检查取消。现有流取消/释放、Worker终止、sink.abort、SHA/记录数及CSV结构/计数规则保留，未降低断言。

自测结果：

- **16组合真实HTTP延迟**：NDJSON/CSV × 浏览器下载/文件写入替身 × 切运行/切APPID/服务身份变化/进入排行。先取真实后端导出响应，切换后才放行；旧取消按钮消失，无旧下载、无旧close提交、无旧成功提示。文件写入替身收到abort。
- **4组合正常及故障**：两格式×两写出路径。正常30条通过原校验；错误摘要（NDJSON）、错误记录数、网络失败和主动取消均不提交文件。原真实Worker固定字节、UTF8/CSV引号/截断/流中断回归继续通过。
- **组件替身**：旧成功、旧失败及finally在新任务启动后才完成，新任务busy仍在，旧提示不出现；service/run/appid均覆盖，排序变更和离开组件亦取消。

文件API验证层级：`showSaveFilePicker/createWritable/write/close/abort`为受控浏览器替身，响应字节与Worker校验为真实实现；**不是原生系统文件选择器/真实磁盘提交验证**。下载回退路径用真实浏览器 download 事件验证。旧大文件RSS/OPFS压力用例本轮未重新运行，不能据此新增性能承诺。

证据：`E/browser-final.log`、最终受影响重跑 `E/browser-connection.log`，对应 `browser-connection-results/v2-review-fixes-RV2-02-*/after-switch.png`；组件归属检查 `E/test.log`。`src/domain/export-protocol.ts`逐字节未变。

### RV2-03 / P2：初始化计时器重置排行

修复前：原固定时钟复现请求0→20→0，初始化300ms定时器无条件setOffset(0)，覆盖用户已到达的第2页。原 `ranking-reset.json`、`ranking.cjs`及容器失败trace保留。

修复：只有 draft search 与已生效 querySearch 不同才建立300ms timer；生效值变化也触发timer清理。Enter仅在搜索确实变化时提交并重置；生效后取消旧timer。初始化、相同搜索、Enter后迟到timer都不再覆盖翻页。

**固定浏览器时钟 + 严格25行DTO投影**：挂载后不推进时钟，先翻第2页5条，再推进300ms，保持第2页且请求仅0→20；相同搜索Enter仍保持。真实改变搜索299ms不动、300ms回首页；快速输入仅最新条件生效；Enter后立即翻页，再推进旧timer期限仍是第2页。未增加初始化等待、降低操作速度或删除分页断言。

原 `v2-boundaries` 的20+5、超安全整数、null、revision冲突、25个并列众数跨页、200K以外等宽箱断言全部保留并通过。投影只验证前端边界；真实排行查询、条件恢复由原真实后端用例覆盖，不将合成25行称作真实后端排序结果。

## 冷环境前置

v2-user/ranking/ttft 显式 await ready；boundaries 每例显式创建所需 `mv2-f006-user-1`并确认ready；acceptance 的 user helper自行等待ready，MA用例自行建任务并确认completed，不再依赖先跑v2-ma。截图改用测试 outputPath，避免覆写旧F006证据。

额外启动完全空的 `E/cold/state`，只运行 v2-ranking，1项通过（18.4s），未先运行其他用例或预建 `mv2-f001-user`。这是测试前置修正，不是后端缺陷修复，亦不改变固定时钟竞态用例。

## 实际命令与结果

环境：WSL Ubuntu22.04 / Linux6.18.33.2，Python3.11.16，Node22.22.2 / npm10.9.7；Windows驱动Node24.19.0、Edge156.0.4314.50、项目锁定Playwright1.64.1。见 E/environment.txt、windows-node-version.txt、edge-version.txt。

| 集合 | 结果 | 日志 |
| --- | --- | --- |
| npm run typecheck / lint / build | 均exit0；Vite仍有既有500kB chunk提示 | E/typecheck.log、lint.log、build.log、checks.json |
| npm run test 全量 | **16文件173项通过** | E/test.log |
| 扩展原25项浏览器集合，加入当时25项修复用例 | **50项通过，1.9m** | E/browser-final.log |
| 最后补连接代次保护后的受影响回归（acceptance4 + 修复26） | **30项通过，51.4s** | E/browser-connection.log |
| 独立空state仅排行 | **1项通过，18.4s** | E/cold/browser.log |
| 追加运行中MA轮询定点（亦包含在上述30项内） | **1项通过，9.3s** | E/browser-poll.log |

各集合重叠，不相加报告通过数量；50项执行后只增补连接代次保护及其测试，随后全量npm四检查和受影响30项再次通过。原159项单元/组件断言保留，新增14项。首次失败日志保留：`E/test-initial.log`中两项因Node/jsdom DOMException跨realm instanceof断言失败，改验name=AbortError；`E/browser-fixes.log`中新增fixture用了非模型别名common_name，后端正确拒绝MODEL_MISMATCH，该轮中止，修正为既有模型别名后21项定点通过（browser-fixes-2.log）。没有修改后端错误码换取通过。

在仓库根目录：

```sh
.venv/bin/python artifacts/validation/viewer/RV2-FIX-20261031/checks.py
# 脚本在apps/viewer依次执行 npm run typecheck / lint / test / build，记录退出码
.venv/bin/python apps/viewer/scripts/prepare-v2-fixtures.py <新的输入目录>
.venv/bin/tokenscope --input-root <新输入目录> --state-root <新state> --cpu-budget 2 serve --host 127.0.0.1 --port 18041
# apps/viewer内
TOKENSCOPE_BACKEND_URL=http://127.0.0.1:18041 npm run dev -- --port 14183 --strictPort
```

Windows浏览器实际执行形态（Node路径见环境；独立端口已先核实空闲）：

```powershell
$env:TOKENSCOPE_REAL_BACKEND='1'
$env:TOKENSCOPE_BROWSER_EXECUTABLE='C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe'
$env:TOKENSCOPE_EXTERNAL_PREVIEW='1'
$env:TOKENSCOPE_TEST_BASE_URL='http://127.0.0.1:14183'
node apps/viewer/node_modules/@playwright/test/cli.js test --config apps/viewer/playwright.config.ts 'v2-.*spec.ts' monitoring.spec.ts full-journey.spec.ts operations.spec.ts export-fixture.spec.ts cache.spec.ts --workers 1 --reporter line --output <本轮新证据目录>
# 最后受影响重跑：用 v2-review-fixes v2-acceptance 替代上行文件筛选
# 冷环境：baseURL改14184，仅 v2-ranking.spec.ts
```

后续直接跑完整筛选会包含新增的运行中MA用例（现共51项）；本轮没有把分次运行冒称为一次51项运行。不要增加分页测试等待来替代 clock 场景。

## 服务、复现与交回边界

本轮主测试端口18041/14183，输入 `E/inputs`、状态 `E/state`；额外冷启动18042/14184，输入 `E/cold/inputs`、状态 `E/cold/state`。启动命令、PID、后台日志分别在 services.py/processes.json/backend.log/frontend.log 和 cold 子目录。所有输入均合成，非现场CSV；新增multi-app.csv为30条分为app-a/app-b各15条。

本轮四个测试端口已停止，输入/state与日志保留，见 `E/cleanup.json`；原8000/4173仍HTTP200，未停止、未覆盖其输入/state。复现请另选空闲端口及新的state，不清理原验收或审查state。打开 `/#/users`/`/#/ma`，用测试helper创建并等待任务，按上述三问题步骤注入；最直接是运行已新增到工作区的 v2-review-fixes 用例。

待审查方独立复测：核对本候选逐文件摘要，复查生命周期/竞态，运行完整当前51项选定源码浏览器集合及四项npm检查，再对正式dist进行本机临时测试镜像与Docker E2E；本轮未执行Docker，也未在此宣布容器或最终联合通过。原生文件选择器/磁盘中止、代表性真实数据和性能校准仍不在本轮证明范围。

复审通过后才由审查方按已有授权整理三端Git、直接合main并显式push；本会话未执行这些动作。仍禁止交付镜像、交付包、部署及华为prompt，等待异常分析前后端设计/开发/验收后的统一交付安排。
