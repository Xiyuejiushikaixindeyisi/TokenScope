# V3B006 PLAN — 前端clock证据与新旧结果兼容

状态：**CLOSED（组件）**。设计r1已按条件授权修订；前置批次关闭后实施，无需重复启动确认。所属条款：D7/AC-CLOCK。总计划：[BATCH_PLAN](../../BATCH_PLAN.md)；设计：[DESIGN](../../DESIGN.md)；底线：[ACCEPTANCE](../../ACCEPTANCE.md)。

## 输入与依赖

V3B005 CLOSED，收到封存结果/schema/状态正反例；B002旧写入口策略已生效。

开始前登记：授权消息/日期、实际HEAD与工作树归属、前批CLOSE、设计版本/摘要、环境/模型/配置/契约身份。当前这些实施字段均为待填；不得把文档提交当产品候选。具体预算先记录测试profile，量值不取报告默认300。

## 最小代码范围（拟；本轮未建源码）

- `apps/viewer/src/api/analysis/`新增V3 client/校验生成物与独立lock，不改旧冻结schema；必要 `navigation.ts` /来源目录版本分派。
- `features/analysis/model.ts`、`Reports.tsx`、`ExecutionStatus.tsx`、必要Evidence组件：clock方案、样本参考值、限制状态。保留四入口和L4/L5主体。
- `api/diagnostics_v3.py`、旧diagnostics与bootstrap/dispatcher：补齐capabilities/历史读取适配，复核全部mutating routes、CLI/恢复入口门禁。

不改其他会话dirty、监控业务语义/默认源或历史产物；不开发Token私有规则、P1模板页面/Agent/hybrid。未列接口的跨层变化先说明必要性，不做整包重构。

## 函数级接入点

- 现有定位：`features/analysis/model.ts`的`cardFromRow`旧过滤，`api/analysis/recommendations.ts`旧scope/总量校验；新增样本适配不可在原函数里全局关闭保护。
- 拟增职责边界（名称可批内调整，语义不可静默改变）：新增V3 report client/validator及`sampleCardFromOutcome`（拟名），只读封存outcome；Reports/ExecutionStatus消费明确版本与状态。副作用层不增加GET后自动submit。

## 开发步骤

1. 按对象版本选adapter，保留AJV/BigInt/范围、总分母、摘要校验；新样本scope不能伪装旧full scope；历史缺字段输出unknown而不是0。
2. clock卡显示自动L1问题、finding/请求对/recipe关联和精确JSON位置/前后片段、NORMALIZED、A/B的N/命中率/pp/P/H/C/matched/modified、来源与评估引用、时间感知业务说明；零/负值可见，不受旧full资格过滤。
3. 在现有范围/状态/建议区显示自动缩样和原因、partial/B不完整。所有已尝试recipe可查；无适用、未计算、预算不足分开；不新增采样向导/模板产品或改四入口布局主体。
4. 完整报告默认优先、固定历史选择和失败时已读结果保持；partial不抢默认。旧Token报告/搜索/链接可读，新Token执行明确休眠，缺bundle不阻塞低命中。
5. 穷举submit/retry/evaluate/combination/authorization/CLI/旧队列与服务重启；不得绕过新预算、恢复Token或自动full。查询、刷新、翻页、方向切换、历史/重连均不发分析POST。
6. 组件/浏览器harness覆盖新状态；真实后端页面接入在B007完成。如本批提前跑真实新版本E2E，必须执行旧服务退出/唯一候选/新state/新browser规则。

开始实现前补“具体函数与签名/调用方/错误返回”表；批准语义以内的拆文件记录即可，预算放宽、业务改法、协议语义或范围变化回到评审。中途发现问题立即记[ISSUES](ISSUES.md)，不留到最终批猜根因。

## 测试与退出门禁

- 用例：T20、T21、T22、T23，fixture：F09/F10/F11/F12，精确断言见[总TESTS](../../TESTS.md)。
- 本批选择及命令记录见[TESTS](TESTS.md)；所有新测试落点是计划，当前未创建/运行。
- **必须满足**：T20–T23通过；clock成功/零/负/partial可见且数字来自封存evaluation；新旧严格校验、历史默认、四入口/L4L5保持；所有GET无任务副作用，所有Token写入口休眠。harness不替代B007真实E2E。
- 必需项NOT_RUN/FAIL/SKIP、阻断未关闭，均不得把[CLOSE](CLOSE.md)改为CLOSED。

## 下一批输入与回退

前后端契约与构建候选身份、UI状态/历史/入口测试、真实E2E所需启动参数与用例；无手填收益/真实正文进入fixture。

回退只撤销本批有归属的源码改动/禁用新V3执行注册，保留已封存产物与旧读取；不执行git reset/clean或覆盖他人改动。回退不能自动恢复Token或旧自动full。若已产生新协议结果，保留对应只读适配；运行清理仅针对已核归属的本attempt，禁止删旧state。具体可逆步骤与文件在CLOSE填写。

完成/受阻时同步[本线记忆](../../../../../memory/tasks/development-v3.md)：状态、候选、测试/issue链接、设计变化、下一步；未闭环不能进入下一批（最终批LOCAL_VALIDATED特例按总计划）。


## B006实际接入方案（2026-11-10）
前置B005 CLOSED，新增独立sample-v3 client与SampleDiagnostics组件，插入现有业务优化建议页面，保留原四入口/旧报告/L4L5。客户端按冻结schema+BigInt检查新样本报告守恒/pp/范围/recipe；不改旧adapter。
来源使用已有monitoring/catalog及user-v2/runs GET，选择后显式“分析当前来源”才POST prepare并在本次用户操作链中POST diagnosis；刷新/读历史不延续提交动作。任务轮询仅GET，取消显式POST；已有完整报告保留，partial只显式选取。新增V3任务列表GET提供持久历史，不存原始报告到浏览器localStorage。新增源分页与任务分页按已有目录限额，只列选择，不分析。
SampleReport组件显示精确clock片段/JSON路径/请求对/recipe、A/B样本N和matched/modified/P/H/C/命中率/pp、抽样范围/原因/独立复核缺项、业务时间语义。无B/未算/零/负/预算状态均可见。报告卡不重新编码/模拟。

