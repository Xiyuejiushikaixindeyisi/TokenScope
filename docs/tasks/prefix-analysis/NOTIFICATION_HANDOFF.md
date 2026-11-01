# FE-N1 后端实现与前端接入

2026-10-31，公共/低命中 session 01a18be2-7112-7aa2-919b-5137d1f1b1ad。用户转交 FE-N1 并要求增加功能，本轮已实施；用户已确认首次partial无默认、empty不替换、两方向整体ready后才更新已包含方向。此文覆盖旧交接中的“无目录/时间/通知、前端轮询任务”描述；前端交互稿仍由前端维护，不代签其接收或实施。未打包部署。

## 版本与路由

新增独立 `diagnostics-discovery-1`，[Schema/manifest](../../contracts/diagnostics-discovery-1/README.md)。analysis-common-1.0 / diagnostics-http-1 冻结文件未改。无需新增Token插件方法；公共状态边界覆盖诊断、Token评估/授权、低命中direct_full及组合任务。Token私有源码未改。

所有路径前缀 `/diagnostics/discovery`。除 capabilities 外均携带 `x-tokenscope-service-instance`；没有新增凭证协议。采用 **fetch 流式 SSE**，不使用不能带该header的原生EventSource。

| GET后缀 | 请求 | 响应 |
| --- | --- | --- |
| /capabilities | 无 | version/service_instance_id、catalog_url/events_url/terminal_url_template、transport、retention、default_policy、schemas |
| /catalog | 首次省略snapshot，after="0"，limit=1–100（默认50）；续页原snapshot+next_after | version/service_instance_id、snapshot、event_cursor、items、defaults、next_after（null表示末页） |
| /events | 必填cursor（目录event_cursor或已处理SSE id） | text/event-stream；terminal、reset事件及注释heartbeat；不支持隐式tail订阅，不读取Last-Event-ID，重连显式带cursor |
| /tasks/{task_id}/terminal | 一次性恢复已知任务，不定时查询 | version/service_instance_id、terminal；活动任务terminal=null，未知404 |

缺header/缺cursor为422；错实例header409 SERVICE_INSTANCE_MISMATCH；目录非法/未来/不同日志epoch游标409 DISCOVERY_RESET_REQUIRED；分页非法422 INVALID_ARGUMENT。SSE无效游标在流内发reset后结束，不能静默从末尾开始。存储503或流断开由前端退避重连并对齐目录，不转为任务轮询。最多64条并发订阅/进程，超限503 DISCOVERY_STREAM_CAPACITY；慢客户端单次发送10秒超时断开。服务器每秒检查终态日志尾部，20秒无事件发送注释心跳；不读报告、不调用分析，客户端无周期receipt/report GET。

## 目录快照及订阅顺序

1. 先读旧capabilities确认主契约，再读新增capabilities确认扩展版本/同实例。
2. GET catalog，保存snapshot/event_cursor；按同一snapshot和next_after读完，绝不在续页省略snapshot。期间新完成的任务不混入旧快照。
3. 用该event_cursor开始fetch SSE。目录与订阅之间的完成事件已写持久日志，将重放，不存在丢失窗口；也可先订阅并缓存事件再完成旧快照读取。
4. terminal事件只用于提示和触发读取，不充当业务报告。诊断ready后重新对齐目录，以defaults权威引用读取原 `/diagnostics/tasks/{id}/report/items`；读取校验成功后整体切换内容与完成时间。失败保留旧内容及时间，并保留待拉取目标。
5. 保存最后已处理事件id去重；乱序消息不能用本地到达顺序覆盖defaults。重连/打开重新对齐目录，已知活动或评估任务可各做一次terminal恢复查询，补回无报告终态；无须按定时器查询。
6. reset后丢弃旧快照游标，重新capabilities/目录绑定；实例不同的缓存与在途响应隔离。事件cursor含服务实例和持久日志epoch；日志丢失/更换重建会reset。当前无自动日志截断，因此有效游标不会因时间推移过期；未来若引入保留期限须升级协议/实现显式floor reset，当前不伪称有过期清理。

每页defaults为**该快照的完整默认引用集**，可能引用其它页的item；不要将第一页未见item当删除，先完成快照。重复页/事件幂等消费，snapshot、sequence、event_id不作为业务时间。

## 目录与事件字段

Catalog.items只包含有已发布报告的analysis任务；卡片数为0仍保留。评估子任务不入主诊断目录。所有终态（包括无报告failed/interrupted）都进入持久事件日志，可通过terminal恢复。

- `task_id/task_kind/parent_task_id/plan_refs`：任务与父证据关联；组合可多父plan_refs，无单父时parent=null。重试是独立task，沿用原意图，未伪造额外父分析关系。
- `report_published/report_ref/report_digest/status/error_code`：提交发布事实与内容摘要，不代表GET时文件永不损坏。GET仍核验原封存文件；report_ref不是文件URL。blocked评估可能task=partial且无evaluation，继续读取report.reason_codes。
- `scope_id/scope`：完整原范围、模型/资产/配置/源身份与请求摘要；SSE只含scope_id，不发送scope全文。catalog和terminal保存scope。
- `binding={appid,model_id,common_name,source_kind}`、binding_id：默认报告分组键，不包含run或窗口。common_name空时真实返回null，仅表示已知model_id下未知服务名的base/user分组，不宣称区分无法观测的物理服务端点。
- `directions`：analysis按显式enable标志列low_hit/token_content；评估为[]，其实际direction继续读EvaluationResult。没有伪造blocked评估的direction或evaluation_id。
- `sequence`：日志内持久追加顺序（十进制字符串），目录版本snapshot与event_cursor绑定该高水位；legacy的sequence只表示导入顺序。
- `terminal_at`：终态更新事务中捕获的服务器UTC时间；`published_at`：该事务发布报告时刻，未发布为null；`analysis_completed_at`是published_at的业务标签。毫秒精度，并非模型任务执行耗时，不能与数据window混淆。发布成功时两时间相同；旧记录全部null。
- `default_eligible`：新的ready analysis且已发布；不是低命中优化卡片资格。默认引用位于defaults中，按binding_id+direction给task_id/sequence。

SSE terminal.data 在上述元数据（不含scope）之外包含version/service_instance_id/event_id。无需从事件拼装业务指标，原文和指标走既有证据接口。目录没有新增“查询最新业务指标”或分析副作用。

## 默认选择与保留

仅新的ready诊断有资格按提交发布sequence更新其包含方向；partial/empty/failed/interrupted不替换。两方向任务整体partial时，不让其中单方向独立成为默认。Token-only ready只更新Token方向，原低命中默认引用保留；不同模型/common_name/source_kind分别选择。

默认顺序按**发布顺序**，不按数据窗口：旧窗口任务晚完成，只要ready，也会更新相同binding/方向的默认引用，UI同时明确数据窗口供用户判断。重试同规则。用户显式历史查看选择具体task，不改变服务器默认引用。partial/empty有已发布报告则进入历史目录，首次仅有它们时defaults为空，可显式查看部分/空范围报告，不能渲染为正常诊断。

没有自动删除目录、事件或报告；新监控批次不会清空历史。外部人为删除文件将使GET失败，目录不自动隐去或替换该结果；不承诺被删原文仍可读取。当前目录默认引用计算会遍历已发布ready历史，适用于低频分析；未给大规模历史目录延迟SLA。

## 原子发布与历史迁移

沿用先fsync/rename封存、再数据库事务发布的顺序。新增SQLite AFTER UPDATE触发器在同一终态事务插入不可变outbox行：事务回滚两者均不存在；提交后即使进程在发通知前退出，重启仍可重放。封存后提交前崩溃的孤儿成果不进目录，worker恢复将running标interrupted并产生终态事件。取消排队、运行失败、重启恢复均经过相同触发器，不依赖各调用点手动发事件。

初始化数据库时一次性导入既有终态，保留原report_digest/scope/intent，不读取mtime回填时间，不重算原报告。legacy=true时间null；旧记录没有可信原发布顺序，因而进入历史目录但**不自动选择默认**。前端可显式查看旧报告并显示“完成时间未提供”。现有已持有旧报告的浏览器无需清空它，新报告合格且成功读取后才切换。

回退可停止新增router注册，保留旧路由和数据库附加表/触发器；不删除用户报告。旧后端沿用原tasks表，附加日志仍能捕获其终态更新；冻结Schema保持。回退后的前端发现扩展不可用应提示，不悄悄改为轮询。

## 最小响应与事件样例

空目录（游标为占位，实际值原样保存）：

```json
{"version":"diagnostics-discovery-1","service_instance_id":"service-A","snapshot":"service-A:epoch-A:0","event_cursor":"service-A:epoch-A:0","items":[],"defaults":[],"next_after":null}
```

活动任务一次恢复：

```json
{"version":"diagnostics-discovery-1","service_instance_id":"service-A","terminal":null}
```

reset的完整SSE帧：

```text
event: reset
data: {"version":"diagnostics-discovery-1","service_instance_id":"service-A","reason":"DISCOVERY_RESET_REQUIRED","catalog_url":"/diagnostics/discovery/catalog"}

```

失败错误体示例：

```json
{"error":{"code":"SERVICE_INSTANCE_MISMATCH","message":"Diagnostic instance differs"}}
```

完整ready/partial/评估元数据可直接读取[合成响应样例](../../contracts/diagnostics-discovery-1/examples.json)，由测试同一构造器产生，仅供接入，不是业务测量。精确结构以wire.json为准；终态缺少evaluation并不违反本协议。Token/combined零负值保留，低命中>1pp展示规则不变。

## 验证与接收

新增测试覆盖原子提交/回滚、发布后立即可读、目录—订阅窗口重放、固定分页、重复消费、重启、模型/方向隔离、首次partial/empty、评估不覆盖、无报告终态、旧时间null、非法/未来/异实例reset、SSE断线释放容量、心跳不读报告、真实HTTP及冻结旧契约。测试代码时钟mock首次影响asyncio全局时钟，已改为模块局部时钟对象后通过；不算产品缺陷。

本轮两线联合199项通过（排除既有三个资源基准）、专用协议最终7项通过、监控兼容300项通过；ruff/mypy通过，详见[实际结果](batches/FE-N1/RESULT.md)，重叠集合不相加。未做前端浏览器联合、代理长连接现场或高并发压测，不将本地HTTP/ASGI测试称为这些验收。消费者先读取新增capabilities与Schema，登记本扩展manifest，再更新原“无目录/无通知”能力表；不得更新TA006历史摘要掩盖公共实现演进。本轮未自动向前端/Token会话发消息。
