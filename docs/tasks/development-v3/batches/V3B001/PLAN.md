# V3B001 PLAN — 来源准入、自动样本与新版本身份

状态：**CLOSED（来源/样本/协议组件；真实运行门禁后续）**。设计r1已按条件授权修订；前置批次关闭后实施，无需重复启动确认。所属条款：D1/D2/D7。总计划：[BATCH_PLAN](../../BATCH_PLAN.md)；设计：[DESIGN](../../DESIGN.md)；底线：[ACCEPTANCE](../../ACCEPTANCE.md)。

## 输入与依赖

设计评审完成且用户明确授权实施；核实际源码/dirty、只读来源接口与旧契约清单。两项计划修订核对完成后满足本批启动授权。

开始前登记：授权消息/日期、实际HEAD与工作树归属、前批CLOSE、设计版本/摘要、环境/模型/配置/契约身份。当前这些实施字段均为待填；不得把文档提交当产品候选。具体预算先记录测试profile，量值不取报告默认300。

## 最小代码范围（拟；本轮未建源码）

- 新增 `analysis_common/sampling_v3.py`、`sample_source.py`、来源prepare模块：纯元数据选键、分块复制/校验、SampleResolvedSource。
- 扩展 `analysis_common/source.py` 的显式适配入口；只读消费 `monitoring/storage.py`、`encoding/stage.py` 现有格式，不改监控产物或旧run。
- 新增V3 request/receipt/sample/report形状与新schema/examples/manifest目录、`api/diagnostics_v3.py`登记路由及专用存储命名空间；复用wire整数规则/引用校验。旧schema/manifest保持字节身份。

不改其他会话dirty、监控业务语义/默认源或历史产物；不开发Token私有规则、P1模板页面/Agent/hybrid。未列接口的跨层变化先说明必要性，不做整包重构。

## 函数级接入点

- 现有定位：`SourceResolver.resolve_scope`、`ResolvedSource._rows/_view/verify/iter_requests/read_ids`：适配点必须阻止完整raw先进入Python，以及再次递归验证原源。
- 拟增职责边界（名称可批内调整，语义不可静默改变）：`select_windows(metadata_iter, selector, profile) → SamplingDecision`；`prepare_snapshot(decision, source_identity, budget) → sealed SampleManifest3`；`SampleResolvedSource.iter_requests/read_request/read_ids`只接受成员。

## 开发步骤

1. 记录元数据可取字段与SQL计划。按精确appid/source/model及time_ns+record_index分页扫描，禁止无界fetchall/SELECT *；字节长度在数据库或受限BLOB读取中检查，不在Python完整字符串之后才发现超限。
2. 实现确定性自动选窗函数，输入元数据与显式profile，输出A/B精确成员、连续性、排除原因、父分母与摘要。未配置sample_limit也有自动策略；测试profile可很小，生产量值待B002校准。边界时间相同、RequestKey重复hash及整个scope=A均覆盖。
3. 实现prepare：receipt快速登记；全源流式seal校验与入选正文分账；固定chunk中断点；选定正文/Token slice校验复制，前后来源一致性验证后原子封存。I/O计划不能因父scope大直接拒绝。
4. SampleResolvedSource仅暴露manifest成员；不同窗各自身份，发现A拿不到B内容访问能力。禁止依赖原source._rows重新全源扫描。复用既有编码身份及P/token SHA，不重编码全源。
5. 冻结V3对象引用/状态语义与正反例；生成新schema摘要。新增路由先只做登记/查询，执行能力在B002受控worker接入前不生产启用；B001组件测试可直接调用prepare，不能称真实运行门禁完成。
6. 记录来源变更、缺slice、超长单条/空窗口等错误；所有失败不发布可用快照；旧源/旧state SHA不变。来源在目标规模不能流式完成就保持阻断，不能删除seal保护。

开始实现前补“具体函数与签名/调用方/错误返回”表；批准语义以内的拆文件记录即可，预算放宽、业务改法、协议语义或范围变化回到评审。中途发现问题立即记[ISSUES](ISSUES.md)，不留到最终批猜根因。

## 测试与退出门禁

- 用例：T01、T02、T03、T04、T05，fixture：F04/F05/F08/F10，精确断言见[总TESTS](../../TESTS.md)。
- 本批选择及命令记录见[TESTS](TESTS.md)；所有新测试落点是计划，当前未创建/运行。
- **必须满足**：T01–T05的组件、来源和receipt门禁通过；T01真实受控执行链在B002必须再验。自动选样/快照成员准确，诊断不能越过快照；旧契约/原件不变。生产启用仍锁定到B002。
- 必需项NOT_RUN/FAIL/SKIP、阻断未关闭，均不得把[CLOSE](CLOSE.md)改为CLOSED。

## 下一批输入与回退

新对象/适配器/样本fixture及摘要、prepare计费接口、T01组件与待B002集成清单；B002只能消费该边界，不能重新物化原源。

回退只撤销本批有归属的源码改动/禁用新V3执行注册，保留已封存产物与旧读取；不执行git reset/clean或覆盖他人改动。回退不能自动恢复Token或旧自动full。若已产生新协议结果，保留对应只读适配；运行清理仅针对已核归属的本attempt，禁止删旧state。具体可逆步骤与文件在CLOSE填写。

完成/受阻时同步[本线记忆](../../../../../memory/tasks/development-v3.md)：状态、候选、测试/issue链接、设计变化、下一步；未闭环不能进入下一批（最终批LOCAL_VALIDATED特例按总计划）。


## 实施开始记录（2026-11-10）

两项r1计划修订已核对，条件授权生效。起点HEAD 9a071c87b517490e497aa6cc1e53ec066bb4ede0；保留所有既有文档dirty，不切换共享分支/不提交。本批先实现：contracts_v3的样本/prepare对象；sampling_v3流式元数据选窗；source_preparation受控seal/快照；sample_source只读成员适配；独立prepare登记store/router，B002之前不挂生产执行。SQLite正文使用blobopen长度/有界读取，避免length(CAST(TEXT AS BLOB))可能在SQLite内复制超大字段。新冻结目录为diagnostics-sampling-3，运行/结果协议后续独立版本。
