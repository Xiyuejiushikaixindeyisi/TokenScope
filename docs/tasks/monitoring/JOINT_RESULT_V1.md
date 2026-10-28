# Token监控第一版：前后端联合验收与 review

2026-10-27 / Session 1。候选 `joint-v1-20261027`：后端0.1.0.dev6、前端0.1.0-f006的联合修正版；版本字符串未升级，**必须同时使用候选SHA清单识别修正代码，不能仅凭dev6/f006复用原包**。control schema3、view1、S0 1.0.0保持不变。本文是B005.1联合闭环及B006 P0/P1的统一证据入口，不是Docker、容器或华为现场验收。

## 范围与结论

用户本轮授权真实前后端端到端测试和review，完成即暂停。本机完整服务通过本轮正常链路、恢复、导出、压力、设计核对；分层证据如下。Docker/镜像/代码交付包没有构建，B006打包保持pending。绝密CSV不出现场，本轮全部数据为明确标记的合成数据。

统一证据目录：[joint-v1](../../../artifacts/validation/monitoring/joint-v1)。候选身份和测试汇总见其中 `acceptance.json`、`source-manifest.json`；原前端74项、后端62项交接摘要开始时全部一致，见 `initial-manifests.json`。

实际运行：WSL Ubuntu22.04/.venv Python3.11.16，CPU预算8；构建Node22.22.2/npm10.9.7；浏览器Windows Edge156.0.4314.42、测试runner Node24.22.1/Playwright1.64.1。正式dist由FastAPI同源挂载在8186，无Vite代理；4186仅用于真实源模块harness和确定性故障夹具；8188仅为流式gzip测试代理。安全上下文为localhost，不等同现场远端HTTP。

## Review发现与修复

| 编号 | 问题和影响 | 修正、验证 |
| --- | --- | --- |
| JR01 | 后端serve没有正式前端挂载入口，Vite联调不能证明完整服务可启动 | 增加可选 `serve --viewer-root apps/viewer/dist`，末尾挂载StaticFiles；首页/静态资源、API优先、缺文件及目录穿越测试通过；真实生产dist与API同源测试通过 |
| JR02 | 实际浏览器下载触发线程池换线程，SQLite读连接报ProgrammingError，NDJSON中断；原文流同样有风险 | 请求独占、只读、串行迭代的projection/original连接允许跨线程续读；没有共享并发读写连接。强制两个独立线程交替next及异线程close测试，实际下载/原文/256MiB导出复测通过 |
| JR03 | 前端在响应头校验失败时仅abort文件，没有主动取消未读HTTP body | exportStream外层失败清理取消未锁定body；新增断言cancel=1、abort=1、close=0。143项前端测试及实际文件/故障/压力复测通过 |

计量、编码、DES、聚合、阈值算法和固定S0没有修改；本轮改动是服务装配、流资源生命周期和联合测试。没有新增产品组件或依赖。已查看真实1440px/390px页面截图，无横向溢出和外部资源请求，见desktop.png、mobile.png、visual.json。

Review覆盖：SQLite流迭代/关闭、提交幂等与持久回执、发布原子性/游标/实例隔离、SSE重放和终态单向合并、快照冻结/ETag/只读、设置与规则CAS、导出Worker字节校验/文件提交时机/缓冲上界。当前未保留本轮已复现但未修复的阻断缺陷；现场边界单独列于下文。

## 测试证据与分层

| 范围 | 实际验证与报告 |
| --- | --- |
| 后端回归 | `pytest.log`：166 passed；ruff-final/format-final/mypy-final通过。原164项全保留，新增同源挂载和强制跨线程流2项 |
| 前端回归 | `frontend-final-checks.json`：143 tests、typecheck/lint/build/check-build通过；后加联合脚本类型检查见final-typecheck.log，固定S0生成核对见final-generate.log |
| 全量泊松负载 | `poisson-report.json`：3模型各约1万行、每模型5appid，从UI实际提交直至SSE完成；验证66K/≥200K长尾、H+C=P、尾桶下钻和校验下载。输入复用固定种子271027的B005.1合成文件，不是生产CSV；详细耗时见poisson-measurements.json |
| 实际生产服务 | `production-pass2-report.json`：8 passed，真实3模型UI提交/SSE/15范围、正文证据/下载；15组×1029分箱与权威值逐值一致；真实CAS/冻结历史/丢回执恢复/OPFS正常与错误SHA及空集；含真实和夹具各30次性能，明确分列 |
| 实际恢复与受控时序 | `recovery-pass3-report.json`：2 passed；实际终态先于订阅、真实过期日志reset、7个回执最大4并发、404不重提、进程强杀/重启同实例、错实例409；真实终态SSE先于延迟queued GET，终态不回退 |
| 规则与重复/冲突通知 | `control-report.json`：2 passed；真实规则CAS、多标签页、历史字节不变；真实receipt加受控原生EventSource重复/冲突终态帧，保留原终态并提示。故障帧是测试注入，不是后端自然生成 |
| 网络压缩 | `gzip-final-report.json`：1 passed；实际HTTP流式gzip代理，无Content-Length，浏览器解码后NDJSON SHA及记录数通过 |
| 前端边界补充 | `browser-boundaries-report.json`：17 passed；真实IDB、多tab/配额/隔离及UI契约夹具，导出Worker/字节/中断/大小边界。export-final-report.json另7 passed复测JR03；不累加重复为独立场景，也不把夹具伪称实际后端 |
| 后端资源复测 | `backend-stress.log`指向stress-20261027T115457Z：1001组目录p95 4.76ms、268741368字节NDJSON、服务RSS增量49033216字节，20SSE正常p95 92.65ms；这是独立projection压力夹具，不是伪造业务指标 |
| 回退与离线资源 | `rollback.json`：复制候选源码到隔离恢复目录，固定锁重建，4个dist资源逐字节相同；这是本地恢复检查点，不是交付包。schema/S0未变，恢复代码无需降级业务库；任何回退仍保留实例和回执 |

J01：发现/指标/北京时间/全部分箱及量化值；J02：实际发布与编辑固定/完整替换；J03：实际断线、reset、重启、缓存与受控重复/迟到；J04：多列明细/筛选/原文/导出；J05：实际幂等回执和设置/规则CAS；J06：正式同源构建、离线资源、故障降级、版本和回退。上述联合证据与原A门槛共同覆盖，不用前端单测代替真实正常链路。

R1-01/02/03/05/07/08见recovery；R1-04见control原生SSE故障及既有receipt组件断言；R1-06见joint.spec真实丢响应/同key返回原run，输入移走后仍幂等的后端回归保持通过。R2-01/02/06见实际OPFS/空集/错误摘要，R2-03/04/05/07/08/09见真实Worker+字节夹具+文件压力，R2-10见实际gzip。逻辑记录1MiB、应用64KiB且最多4片（实际1片）、fallback16MiB不变。

真实后端30次浏览器性能p50/p95(ms)：首次288.3/358.5；50行32.4/56.0；缓存18.1/31.2。另有契约假服务30次，不混入真实统计。`production-pass2-measurements.json`保留全部样本。

`export-final-measurements.json`：256MiB三次增量58.44/68.19/95.51MiB；1GiB三次158.76/187.03/153.92MiB。均低于用户批准256MiB验收上限，部分高于64MiB优化目标；中位增长比约2.33（门槛<3，32MiB基线下限）。Windows浏览器进程WorkingSet采样，不是JS堆，也不证明严格常数空间。真实OPFS文件写入、close/abort和最终文件大小均验证；选择器为受控句柄，不声称操作了人工OS保存对话框。

## 失败与复测保留

- 首次integration在JR02处下载中断，runner等待未完成下载被终止；server.log保留异常，空报告不计通过；integration-fixed通过后再次生产候选通过。
- joint-pass1测试误找alert，实际页面在status显示SHA错误并abort；改正确定位后4 passed。
- 恢复脚本先仅改hash，没有重新加载注入的IDB回执；修正reload。第二次故障脚本在页面切换后使用已dispose的Playwright响应，修正复制响应字节并等待路由收尾；第三次2 passed。不是产品修复。
- 恢复测试worker结束后清理了它启动的服务子进程，随后production-final/gzip首轮连接拒绝；独立重启服务后production-pass2/gzip-final通过。失败报告未删除。
- 新增测试的TS ArrayBuffer类型/可空error_code及Python导入排序问题修正；最终静态检查通过。失败日志仍保留。

## 尚不由本轮证明的事项

本机合成验收不代替V100生产CSV、现场CPU/驱动/容器和两小时性能验收。DeepSeek缺省思考仍pending（测试请求显式提供选项）、GLM CP映射、GF tokenizer/template资产等价仍按原未决维护。Qwen/V4为批准的普通链式近似，不声称实现hybrid。远端浏览器安全上下文与实际OS保存位置/覆盖行为留现场确认。

Docker、基础镜像、Compose和交付包的执行授权仍由用户决定；本轮通过不构成自动授权。B006仅引用本报告作为P0/P1前置，不执行P2以后的构建/归档/部署。

## 复现入口

项目本地运行正式完整服务（合成输入、独立状态，非Docker）：

```sh
.venv/bin/python -m tokenscope.cli --input-root artifacts/validation/monitoring/joint-v1/inputs --state-root artifacts/validation/monitoring/joint-v1/state --asset-root /home/zhangxiyue/TokenScope serve --host 127.0.0.1 --port 8186 --viewer-root apps/viewer/dist
```

浏览器使用apps/viewer/playwright.config.ts、Windows项目Playwright CLI、固定Edge；设置TOKENSCOPE_EXTERNAL_PREVIEW=1、TOKENSCOPE_TEST_BASE_URL、TOKENSCOPE_BROWSER_EXECUTABLE；真实三模型integration另设TOKENSCOPE_REAL_BACKEND=1，joint*.spec另设TOKENSCOPE_JOINT=1。`joint-recovery.spec.ts`有明确破坏性测试动作：仅针对本报告独立state和已记录PID强杀/重启，不能指向共享或生产服务。gzip脚本/用例分别为scripts/validation/joint_gzip_proxy.mjs和joint-gzip.spec.ts，后者需TOKENSCOPE_JOINT_GZIP=1。所有命令、端口、测试输入均不应用到生产状态。


闭环：本轮30个不同浏览器场景按生产服务/受控故障/前端边界分层通过（重复复测不累加）；三模型有效请求9972/10089/10107，共30168，UI提交到完成约18.96/21.06/19.90秒。101项S0摘要不变，候选144项源码/资源摘要最终复核一致。自有8186后端、4186测试harness和8188压缩代理已停止，其他会话服务未操作。Session 1已暂停。
