# V3B007 PLAN — 统一E2E、健壮性与五组底线验收

状态：**LOCAL_VALIDATED**。设计r1已按条件授权修订；前置批次关闭后实施，无需重复启动确认。所属条款：D0–D8/AC-MEM/AC-CLOCK。总计划：[BATCH_PLAN](../../BATCH_PLAN.md)；设计：[DESIGN](../../DESIGN.md)；底线：[ACCEPTANCE](../../ACCEPTANCE.md)。

## 输入与依赖

V3B006 CLOSED；前六批CLOSE/记忆/候选链完整；冷启动与真实数据范围有相应授权。打包/现场本轮未授权。

开始前登记：授权消息/日期、实际HEAD与工作树归属、前批CLOSE、设计版本/摘要、环境/模型/配置/契约身份。当前这些实施字段均为待填；不得把文档提交当产品候选。具体预算先记录测试profile，量值不取报告默认300。

## 最小代码范围（拟；本轮未建源码）

- 新增/适配 `scripts/validation/` 受控V3合成源与候选验证入口；不得直接调用历史两方向全跑脚本。
- 新增 `tests/integration/analysis/` 端到端/故障用例及viewer真实后端browser用例，输出证据清单；发现bug回所属批次修复。
- 本批新建DESIGN_CHECK.md及BUSINESS_EVIDENCE.md记录最终代码/设计映射与五组证据（实施验收时再建）；不在原报告补写结果。

不改其他会话dirty、监控业务语义/默认源或历史产物；不开发Token私有规则、P1模板页面/Agent/hybrid。未列接口的跨层变化先说明必要性，不做整包重构。

## 函数级接入点

- 现有定位：`scripts/validation/analysis_frontend_server.py`是历史流程参考，不当V3已验证启动器；现有Playwright配置的external preview入口需核唯一候选。
- 拟增职责边界（名称可批内调整，语义不可静默改变）：验证驱动只编排正常CLI/API，不复制检测/编码/收益算法；另设独立整数指标校核与设计追踪输出。运行身份清单绑定所有日志/截图。

## 开发步骤

1. 核每批状态与产品diff归属，冻结候选源码/dist、旧契约、依赖/模型/profile。盘点并仅停止旧TokenScope服务/进程/容器，验证端口释放；保留旧包/state/证据，无并行旧版换端口。
2. 独立新state、新浏览器context，从合成监控源产出→自动prepare→诊断→clockA/B→封存→真实页面；核全链service/source/sample/plan/evaluation/report/HTTP资源身份，实际模型编码不可被mock替代。
3. 执行大源自动缩样与进程树峰值/取消/响应性、连续窗口完整性、重复密集候选、无clock大单条等场景；故障注入覆盖超时/磁盘满/崩溃/重启/半写/取消发布竞态/幂等，停止后无孤儿。
4. 执行完整Python质量/回归、viewer质量/构建/组件及真实浏览器；旧结果隔离副本、Token休眠、四入口/L4L5、监控/MA/统一计量均核对。harness和真实后端记录分开。
5. 按D0–D8逐条填实现函数、T-ID、证据、偏差/限制；问题回所属batch ISSUES，修复和重跑受影响门禁后再更新CLOSE，不能以最后总通过数覆盖未解决设计偏差。
6. 在获准真实数据环境逐BUS01–05执行：自动缩样无mem_limit；正常诊断自动L1发现→定位→clock固定化A/B实算（不预指定clock/recipe）；页面问题证据/片段/指标与封存结果一致，汇成一份可给业务讨论的Markdown。时间语义、样本分母与未复核限制明确。不得复制旧收益作为结果。
7. 本地没有真实数据时仅LOCAL_VALIDATED并列BUS NOT_RUN/阻断，交待现场验收候选供打包评审；经另行授权回传真实证据后再闭环。停止临时测试进程/说明保留项，增量更新本线记忆与最终交接。

开始实现前补“具体函数与签名/调用方/错误返回”表；批准语义以内的拆文件记录即可，预算放宽、业务改法、协议语义或范围变化回到评审。中途发现问题立即记[ISSUES](ISSUES.md)，不留到最终批猜根因。

## 测试与退出门禁

- 用例：T24、T25、T26、T27、T28、T29、T30，fixture：F01–F12，以及获准真实BUS01–05（不得合成替代），精确断言见[总TESTS](../../TESTS.md)。
- 本批选择及命令记录见[TESTS](TESTS.md)；所有新测试落点是计划，当前未创建/运行。
- **必须满足**：T24–T30和AC-MEM、BUS01–05逐项通过、全设计映射完整、阻断清零才CLOSED。仅本地工程完成可LOCAL_VALIDATED；五组缺数据/参考值或B限制未经明确接受时不得总体CLOSED。
- 必需项NOT_RUN/FAIL/SKIP、阻断未关闭，均不得把[CLOSE](CLOSE.md)改为CLOSED。

## 下一批输入与回退

源码/dist候选与摘要、profile/环境、完整测试/设计对照/五组证据状态、issue清单/回退说明，供镜像审批及另行授权打包。镜像/现场/人工验收身份分开记录，debug仍归本线。

回退只撤销本批有归属的源码改动/禁用新V3执行注册，保留已封存产物与旧读取；不执行git reset/clean或覆盖他人改动。回退不能自动恢复Token或旧自动full。若已产生新协议结果，保留对应只读适配；运行清理仅针对已核归属的本attempt，禁止删旧state。具体可逆步骤与文件在CLOSE填写。

完成/受阻时同步[本线记忆](../../../../../memory/tasks/development-v3.md)：状态、候选、测试/issue链接、设计变化、下一步；未闭环不能进入下一批（最终批LOCAL_VALIDATED特例按总计划）。



## B007实际启动方案
前置B003–B006组件闭环，按用户连续授权。test-output-preflight发现旧U004/U007固定产物写入，已仅改测试输出至tmp_path；断言/产品语义未改。
进程盘点见attempt01：唯一旧TokenScope服务PID1173429、18002、icsl-demo/local/state和旧hv2 dist，核命令后SIGTERM且端口关闭；保留旧state/输入/dist。Windows无TokenScope服务（仅编辑器/工具），WSL无docker CLI/socket/daemon，无运行测试容器迹象；未停无关编辑器。
新增v3_local_e2e.py→正常CLI服务/HTTP监控→v3_browser_e2e.mjs真实浏览器点击来源prepare/诊断→刷新断线重连GET-only→导出已封存报告。新目录exist_ok=False，复测换attempt，finally停服务并校验18002释放。v3_independent_check.py使用字面Token前缀独立oracle，不调用生产PrefixLedger/strategy，逐行P/H/C/摘要及Fraction复核。
两模型16条和DeepSeek2200条合成来源，不注入finding/recipe。浏览器headless独立context，源码/HTTP构建资源/state/instance身份绑定。全量Python回归与正常服务E2E为不同证据，现场五组不以合成替代。源码验证不构建镜像/交付包。

## 实际退出
按用户最新授权完成本地验证，五业务留华为机；实际命令/结果/差异见TESTS、ISSUES、CLOSE与总DESIGN_CHECK。上文拟定文件名由v3_local_e2e.py、v3_browser_e2e.mjs、v3_independent_check.py、v3_restart_browser.mjs及test_v3_legacy_readonly.py承担，无另建重复端到端框架。
