# RV1：统一入口及前端独立复审修复验收

2026-11-01后续RV2已取代本文件作为当前验收：L4/L5各一张卡、每类≤3例，见[联合报告](../../analysis/JOINT_VALIDATION_RV2_20261101.md)。当前8016已加载arpc-local-4、运行PID见RV2 service.json；本文件原测试和版本身份保持历史，不改写成新执行。

2026-11-01，`viewer-analysis-ui04-local-2`。本轮依据用户拒绝双入口并要求独立复审/修复BUG的指令执行。UI-04配色布局保持，未改批准HTML、后端业务源码或接口，未打包部署。

## 统一入口

**[打开异常分析](http://localhost:4191/#/analysis)**。默认应用`synthetic-orders`、模型`GLM-5.2`，低命中率和Token异常两个页签均从同一后端实例读取。

[直接打开Token页签](http://localhost:4191/#/analysis?direction=token_content)。旧`4193`仅作302跳转，进入4191的Token页签；不再运行第二套前端/数据代理。早期两个独立端口的验收方法已撤回，原证据和报告未改写。

建议验收顺序：

1. 在低命中页看6条影响请求及约70.24个百分点预期命中率提升，打开局部证据；随后点击Token页签，应用、模型和报告时间保持。
2. Token页查看T2、T3引用、T3普通消息删除、T4四项具体建议及Token变化，返回低命中页。
3. 历史报告选择13:54:13的完整报告，在两方向间切换；应保留这份历史报告和时间。打开详情、刷新、返回列表，仍是同一报告。
4. 手动选择13:54:33的部分结果可看到未完成提示；点击“查看最新”应回到13:54:28的完整报告。部分结果不覆盖默认完整报告。

以上时间均为2026-11-01北京时间。当前统一输入与业务策略是构造样例；Tokenizer/离线回放及封存读取真实执行，不是生产收益或生产策略授权。

## 问题及修复

| 问题 | 修复 |
| --- | --- |
| 两个地址连接独立state，无法连贯验收 | 由公共后端使用既有链路生成同实例、同appid的双方向报告；4191单代理，4193跳转。没有拼接数据库或伪造实例身份 |
| 切换到无报告方向后一直加载，或残留其他方向错误 | 读取状态随目标切换清理；无目标结束加载；空目录、无该方向报告、失效历史链接分别提示 |
| 旧分页失败污染新应用 | 分页独立加载/错误状态；切换目标中止旧请求，迟到结果不写入新页面 |
| 切换应用后旧来源请求仍导航旧监控 | 来源请求在entry变化/卸载时中止，导航前再次验证请求有效性 |
| 禁用localStorage时通知反复重连 | 存储对象获取也纳入容错，目录/报告/SSE保持可用 |
| 多差异卡片同时读取证据，拖延历史读取 | 卡片进入或接近可见区域时读取证据预览；详情按需立即读取，保留完整差异分页和局部例子 |

附带修正：初始方向优先选择有该方向默认/历史报告的绑定；失效绑定提供返回目录；同一历史报告跨方向保持task；详情返回以实例/绑定/方向/任务定位卡片，恢复滚动与焦点；重试只清理目标报告缓存。

初始失败证据、独立问题分级和复验结论见[独立复审报告](INDEPENDENT_REVIEW_20261101.md)。独立审查者取证及编写专项测试，主会话修改前端。用户视觉认可不由工程检查代签。

## 数据与版本身份

- 本次前端联调与RV1封存生成使用`arpc-local-3`与Token `arta-local-1/token-content-2`；接口`analysis-recommendations-1`及discovery-1不变。后续公共独立复审修复版为`arpc-local-4`，不能把前端此前的浏览器执行记为该新版本重跑。
- 新验收数据身份`unified-acceptance-rv1-20261101-1`；[归口交接与实际GET](../../prefix-analysis/UNIFIED_ACCEPTANCE_RV1_HANDOFF.md)。前端核验6交接/日志文件、4数据文件，以及110项后端/测试/Schema依赖摘要一致。
- service instance：`0cf8b18b-224f-44f3-959d-bbfc1cfe010e`；binding：`f860b372ec762939acba36cbffbfebab82e97836215f52df683a96900b0e2256`。
- 历史ready：`d69ce286-8461-4b0e-bc95-83b341b9c47b`；默认ready：`4f5a4bd6-c09e-4ac4-a5aa-9f5fdd832633`；最新partial：`11ab16c3-1ea4-4d71-b6d7-a41b828564ee`。三任务同scope，两方向defaults均指向第二个ready。
- 一张合格L1优化卡及四张Token优化卡；L4/L5保留后端实际差异分组、分页读取、每组详情最多3例。不会在前端按样例数改写影响请求数，也不相加收益。
- UI-04 HTML SHA256仍为`779e6665985fe02e6df9e7d0483ef8111a16a49c2b61fdb27aacbef58d624f5f`。

后续状态更正（2026-11-01）：已读取[低命中/公共实际独立复审报告](../../prefix-analysis/INDEPENDENT_REVIEW_RESULT_20261101.md)，`arpc-local-4`在该范围通过；PCR-01工具交换对照、PCR-02成员完整性问题由后端归口修复并独立复验关闭，旧RV1在新版215个只读路由检查中兼容且原始84文件未变。报告不覆盖Token私有全范围。Token已获其本线用户授权并实际发起T2–T4独立复审，见[最新交接状态](../../length-analysis/INDEPENDENT_REVIEW_HANDOFF.md)，当前待实际结论。此前“两后端只有交接”仅为前端测试时点记录，已不代表当前状态。

本次更新仅接收复审状态，不重写旧测试身份或封存报告、不重启验收服务；来源摘要见`artifacts/validation/viewer/analysis/review-20261101/backend-review-update.json`。Token配方/业务策略仍由其后端维护；后续若需新状态，由公共后端正常生成封存，不拼接旧SQLite或复用旧报告ID。

## 验证记录

最终类型/静态、单元/组件、真实联合浏览器和专项独立回归结果以[本轮结果清单](../../../../artifacts/validation/viewer/analysis/review-20261101/result.json)和独立报告为准。首次联合历史读取超时已保留，修复屏外证据预取后按原断言复测，不延长等待来掩盖问题。

最终typecheck/lint通过，21文件191项单元/组件测试通过；17个不同浏览器用例通过（主线10项、独立专项7项），另有独立审查者真实统一实例7条操作链验证通过，不重复累计为测试数。主线最终执行有8项通过、2项因并行测试共用trace输出目录失败；这2项在隔离输出目录复验通过（15.5秒）。独立专项最终隔离执行7/7通过（17.7秒）。全部6项复审发现已关闭，用户功能/视觉验收仍待确认。

证据目录：`artifacts/validation/viewer/analysis/review-20261101/`。`browser-main.log`为修复性能前9/10结果，`unified-followup.log`为原失败场景复验；`browser-main-final.log`、`browser-ui-final.log`及`frontend-final-checks.log`为最后主线验证。专项最终日志为`reviewer-regressions-isolated.log`，真实同实例检查为`unified-independent-final.json`。失败日志原位保留，不把trace目录竞争的失败记为通过，也不重复累计重跑数量。

截图：[低命中首屏](../../../../artifacts/validation/viewer/analysis/review-20261101/browser/low-list-1440.png) · [Token卡片](../../../../artifacts/validation/viewer/analysis/review-20261101/browser/token-list-1440.png) · [局部证据详情](../../../../artifacts/validation/viewer/analysis/review-20261101/browser/low-detail-1440.png) · [窄屏Token详情](../../../../artifacts/validation/viewer/analysis/review-20261101/browser/token-detail-390.png)。

## 本机运行与恢复

当前仅一份验收后端8016、一份前端4191；4193为旧地址跳转。后台进程/日志见`unified-service.json`、`unified-frontend-services.json`。未设置开机自启。

后端状态根：`artifacts/validation/unified-rv1-20261101-01/{inputs,state}`。恢复时先核对端口及进程所有者，已有服务不重复启动；在WSL项目根目录及apps/viewer目录分别运行：

```bash
.venv/bin/tokenscope --input-root artifacts/validation/unified-rv1-20261101-01/inputs --state-root artifacts/validation/unified-rv1-20261101-01/state serve --host 127.0.0.1 --port 8016
# 独立终端，在apps/viewer目录
TOKENSCOPE_BACKEND_URL=http://127.0.0.1:8016 npm run dev -- --host 127.0.0.1 --port 4191 --strictPort
```

不要重新执行生成脚本覆盖当前state；浏览只需要已封存数据。旧ARL5/ART4的独立服务已退出，本机文件仍保留。若需旧4193地址兼容，执行证据目录内`redirect-old-token.cjs`；它只返回统一地址的302。
