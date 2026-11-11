# V3B003 PLAN — 时钟定位与session_clock精确固定化

状态：**CLOSED（本批组件）**。设计r1已按条件授权修订；前置批次关闭后实施，无需重复启动确认。所属条款：D4/AC-CLOCK。总计划：[BATCH_PLAN](../../BATCH_PLAN.md)；设计：[DESIGN](../../DESIGN.md)；底线：[ACCEPTANCE](../../ACCEPTANCE.md)。

## 输入与依赖

V3B002 CLOSED，受控样本/worker可用；固定日期语法、clock块语法和变换版本由本设计批准。

开始前登记：授权消息/日期、实际HEAD与工作树归属、前批CLOSE、设计版本/摘要、环境/模型/配置/契约身份。当前这些实施字段均为待填；不得把文档提交当产品候选。具体预算先记录测试profile，量值不取报告默认300。

## 最小代码范围（拟；本轮未建源码）

- `prefix_analysis/dynamic.py`、`detection.py`：日期和clock结构定位/重叠消歧；必要新增clock专用模块，避免扩大旧通用正则。
- `prefix_analysis/experiments.py`或新V3 handler：clock统一NORMALIZED；复用 `analysis_common/modifications.py` 的PreparedMutation/守卫与协议检查，不复制全局replace链。
- 新增V3 clock意图与适用性记录、业务说明；旧path/CCH、普通时间槽与L3工具逻辑名能力保持。

不改其他会话dirty、监控业务语义/默认源或历史产物；不开发Token私有规则、P1模板页面/Agent/hybrid。未列接口的跨层变化先说明必要性，不做整包重构。

## 函数级接入点

- 现有定位：`dynamic.slots_in_text/text_shape/comparable_slots/locate_recipe/apply_recipe`；`detection.pair_dynamics/compile_dynamic_plan`，保留旧CCH/path调用者。
- 拟增职责边界（名称可批内调整，语义不可静默改变）：`locate_clock_blocks(text) → accepted/unsupported spans`；`compile_clock_recipe(A_findings)`消费自动归因与适用，手动意图另记；`compile_clock_plan(window_source, recipe)`生成每请求守卫，交给既有mutation执行。

## 开发步骤

1. 字段限定system/developer文本含内容块，L3为工具description；先定闭合clock边界，再识别ISO/斜杠/中文日期，合法性/时区/字符位置明确。嵌套/缺闭合/额外指令输出unsupported或业务待确认。
2. 变化归因比较同一逻辑字段掩码后的结构，不能因无关历史/tools差异拒绝全部clock候选；单条或固定值不造L1变化因果。path日期优先按语境，长度不同不是漏检理由。
3. 实现正常诊断内自动clock定位/可比对/变化证据→L1 finding→recipe链，不要求用户预先知道clock。无合格证据保留不足说明，不造L1；指定反事实另记且不能通过自动验收。同字段clock外一致但后续历史长度/角色序列不同为必需自动正例。
4. 冻结固定化recipe：逻辑路径/块语法/序号/版本/常量；自动recipe绑定字段证据支持的shape/条件，不以完整历史作约束，不观察B后扩规则。整块内部变为NORMALIZED并保留标签；不移动时钟、不删除历史，不按请求生成不同常量。日期槽删除不能充当本项通过。
5. 每条具体operation验证原raw SHA/原值与位置，不重叠；只改副本。原样请求raw/Token保持；改后未触及内容语义相同，词法/序列化差异按既有守卫处理且披露。
6. 用真实编码Token IDs验证选定样例的分叉/变换结果，不从字符位置猜Token。记录实际matched/modified集合，用户明确禁止的反事实不执行；其余始终注明时间感知改变和业务待确认。

开始实现前补“具体函数与签名/调用方/错误返回”表；批准语义以内的拆文件记录即可，预算放宽、业务改法、协议语义或范围变化回到评审。中途发现问题立即记[ISSUES](ISSUES.md)，不留到最终批猜根因。

## 测试与退出门禁

- 用例：T10、T11、T12，fixture：F01/F02/F07/F08，精确断言见[总TESTS](../../TESTS.md)。
- 本批选择及命令记录见[TESTS](TESTS.md)；所有新测试落点是计划，当前未创建/运行。
- **必须满足**：T10–T12通过，能产精确clock改法并在副本真实编码；合法负例不误改，块外安全、复杂JSON/工具协议守卫有效；此批不宣称已完成业务收益或前端。
- 必需项NOT_RUN/FAIL/SKIP、阻断未关闭，均不得把[CLOSE](CLOSE.md)改为CLOSED。

## 下一批输入与回退

clock locator/normalizer/recipe版本与fixture、业务语义说明、适用/不适用状态及实改证据；B004用同一规范化规则，B005不能另造正则变换。

回退只撤销本批有归属的源码改动/禁用新V3执行注册，保留已封存产物与旧读取；不执行git reset/clean或覆盖他人改动。回退不能自动恢复Token或旧自动full。若已产生新协议结果，保留对应只读适配；运行清理仅针对已核归属的本attempt，禁止删旧state。具体可逆步骤与文件在CLOSE填写。

完成/受阻时同步[本线记忆](../../../../../memory/tasks/development-v3.md)：状态、候选、测试/issue链接、设计变化、下一步；未闭环不能进入下一批（最终批LOCAL_VALIDATED特例按总计划）。


## 本批实际启动与函数方案（2026-11-10）

前置B002代码门禁CLOSED（历史测试日志事故继续披露），候选v3b002-local-1；r1授权继续，原HEAD及既有dirty保留。新增timestamps.valid_timestamps供既有动态槽与clock复用；session_clock_v3.locate_clock_blocks/clock_fields/clock_shape/normalize_clock负责合法日期、结构边界、system/developer逻辑字段及精确替换。clock_discovery_v3.collect/compile负责自动请求对证据、冻结recipe和PreparedMutation，不靠预指定clock。角色内序号+content文本块路径作为逻辑字段，后续历史不参与可比键；source_pointer保留真实位置。未知/嵌套/不完整clock或额外指令不自动扩大修改。

受控worker的diagnose内部动作消费已完成prepare引用，仅A窗发现/生成改法与编码证明；B窗不读取，收益/完整报告在B005接入，API execution_enabled仍不提前启用。SampleResolvedSource可选BudgetLedger把实际快照读取/校验/解析接入B002计费。compile返回matched/modified精确集合、NO_APPLICABLE_TARGETS/NO_MODIFICATION/BUSINESS_FORBIDDEN；guard失败不发布after。业务说明明确固定时间改变时间感知，非无损保证。公开新提交入口与跨通道候选汇总分别在B005/B004，不在本批重复建调度层。