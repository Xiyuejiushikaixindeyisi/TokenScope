# B005.1 验收方案与实际记录 v0.2

状态：**实施已获批准，S1–S5后端门槛已闭环，164项全回归通过；真实联合仍pending**。表中场景仍是验收要求，实际证据见文末，不把计划值当成实测。既有B005的145项作为回归基线。

## 后端门槛

| ID / 需求 | 测试场景与断言 | 拟执行位置 |
| --- | --- | --- |
| A01 BE01/10 | 三模型×5appid目录；旧CSV晚完成、相同最大时间重跑、缺组不归零、空结果；按数值时间+序号选latest | publications单测/HTTP E2E |
| A02 BE01/02 | 目录和cursor同事务；目录返回后订阅前发布；分页中新增发布409，不拼接两版本 | 实际HTTP+SSE并发 |
| A03 BE02 | complete在封存前、封存后提交前、事务各写点、commit后通知前崩溃；不出现部分组；恢复只一条publication | recovery故障/独立进程kill |
| A04 BE02 / R1-01/03 | 正常无报警/有报警/重复报警同源重跑均有发布；no_valid_rows事件不覆盖旧组；failed/interrupted终态，无新快照 | E2E/claim失败/worker恢复 |
| A05 BE02/09 / R1-02/05/08 | Last-Event-ID优先、重复回放、过期/未来/跨实例reset、日志全清/部分清理后的持久水位边界、20s注释心跳、重启身份不变 | 实际SSE/可注入时间 |
| A06 BE02 | 慢消费者、满连接上限、连接断开、长期空闲：有界内存，无控制库长读/写锁，worker不等待客户端 | 压力/取消/锁竞争 |
| A07 BE03/09 | 快照逐项等于原metrics及全部1029桶；冻结设置/规则/信号摘要；修改配置/消费状态后原ETag和字节不变；If-None-Match→304 | API/独立原结果对照 |
| A08 BE04 | 不同UTC小数秒精度/同刻文本形式/乱序；组与文件范围不同；未知坏行不分摊；组内/跨组重复范围明确；null不当0 | projection单测 |
| A09 BE05 | J/P/C排名不同、H/O排序、相等长度稳定次序、hash重复均保留、hash前缀字面量转义、区间左闭右开、200K尾桶、极大offset | requests API |
| A10 BE05 | 原JSON字符/空白精确，64KiB UTF8安全预览，完整流式正文；轻证据分页；未知字段归因不伪造；错appid/ref404；无模板正文 | detail API |
| A11 BE06 | 按appid分页信号，比较方向/冻结rule revision/实际值正确；同event跨run关联正确；无消费者仍pending_consumer | signals API |
| A12 BE07 / R1-01/06/07/08 | 同key并发/丢回执/重启返回同run；异体409；首次提交校验失败不占key；回查前不再次检查已移动输入；新key可重跑同文件 | submission集成 |
| A13 BE08 / R2-01–08/10 | 全量/筛选导出与独立SQL事实逐行一致，重复不丢；NDJSON结束清单/校验、CSV表头和安全转义、断线释放；无正文默认泄露 | export流式/内存 |
| A14 BE09 | 2^53−1/2^53/64位边界、负delta、null、序号/计数字符串；JSON/TS无损往返、设置/规则适配共用CAS；旧API兼容；未知/未完成明确404/409 | wire单测/API契约 |
| A15 全部 | 把encode/render/replay/aggregate/explain替换为失败哨兵后遍历所有GET仍可读取；原结果mtime/摘要不变 | 只读集成 |
| A16 迁移/回退 | schema2→3、历史无效行/零信号/冻结旧设置、回填中断重启不重复、未回填503、旧sealSHA不变；恢复schema2备份 | migration集成 |
| A17 原能力 | 原145项及新增测试全通过，ruff/format/mypy通过；三模型B005独立参考与batch等价不退化 | 全回归/实际HTTP E2E |
| A18 性能 / R2-09 | 新增预处理计时；目录/快照/请求/SSE/导出资源和并发指标达下列目标；失败不得静默降门槛 | view E2E性能报告 |

## 联合完整服务门槛（不能用假服务关闭）

| ID | 实际浏览器+后端的验收动作 |
| --- | --- |
| J01 | 首次进入发现appid/模型并展示完整快照；UTC转北京时间；J/P/H/C/O、分位/众数/尾桶和后端逐值一致 |
| J02 | 新运行正常完成→SSE→目录→新快照整体替换；明细/历史固定/编辑时提示新结果而不强制切走，不出现跨run混用 |
| J03 | 刷新/断线/重连/重复和迟到事件/游标过期/服务重启；缓存按实例/schema/run隔离，同一快照不重复拉取，无定时指标轮询 |
| J04 / R2 | 分箱宽度/数量占比/区间下钻、多列分页、详情/原文、全量导出；合法偏好保留、旧页码清除，无图表拼页错误 |
| J05 / R1 | 实际file_ref提交→丢回执重试/查回→终态；设置与阈值CAS冲突保留草稿；新设置只影响下一运行；空/失败/缺组不显示假0 |
| J06 / R2 | 前端离线构建资源与同版本后端同源运行；schema不兼容/缓存额度不足/接口失败有可见降级；版本、浏览器网络证据、回退记录齐全 |

J01–J06由后端Session 1统一执行；前端提供F006固定版本和自身范围证据，在统一验收记录中绑定前端资源摘要、后端代码SHA、OpenAPI摘要、数据/资产身份。此前HTML视觉检查和B005后端E2E都不覆盖这些门槛。未提供实际前端代码时只写pending，不在本轮替它实现。

## 数据与性能目标（用户已批准）

使用B005固定种子271027、3模型×5appid、约1万行/文件真实词表合成负载；另加可人工核算的小样本、相同/不同时段文件、无有效行、重复/坏行、Unicode工具、66K和≥200K尾部。大整数序列化使用独立DTO边界夹具，不伪称生产数据。目录规模另用≥1000组合成已存元数据测试，与三模型主负载分开标记。

本机8CPU约束下记录至少30次查询的p50/p95、冷/热状态、并发数及完整环境身份：
- 100项目录响应p95≤300ms；单组快照响应p95≤500ms；50条请求页p95≤500ms。
- 代表负载单组未压缩快照≤512KiB（不含正文），9直方图合计1029桶；规则数量/额外字段一起记录，超标需分析修正或明确评审。
- 20条SSE连接含1个慢消费者；正常连接提交至事件可读p95≤1s；慢连接不阻塞发布。与无订阅基准相比运行耗时增幅目标≤10%，重复实验排除噪声。
- 全量导出额外RSS目标≤64MiB；停止读取后资源释放。记录大单条正文/轻证据的体量上限和实际峰值。
- 新文件整个处理至持久发布<7200s，包含视图生成/封存/发布；本机合成通过不替代V100真实数据验收。
- 前端缓存交互≤100ms、首次组读取+渲染≤1s为联合测试目标，后端单独延迟不能代替这些数字。超标记录原因、修正/复测，不能把计划值写成实测值。

## 实际验证入口

实施S0补齐检查入口后：
```text
.venv/bin/python scripts/validation/check_batch.py B005.1
.venv/bin/python scripts/validation/run_monitoring_e2e.py --batch B005.1
.venv/bin/python scripts/validation/stress_monitoring_view.py
.venv/bin/python scripts/validation/measure_sse_overhead.py
```

上述脚本已实现；run_monitoring_view_e2e.py由主E2E调用，check_batch支持B005.1。浏览器联合脚本命令由实际前端实施后写入，不虚构可运行命令。产物根artifacts/validation/monitoring/B005.1/，记录源码清单、环境、时间、命令/退出码、输入SHA、失败与复测、SSE事件轨迹、性能和回退报告；原始请求不出现在普通日志。

## 方案阶段历史检查（非当前实施状态）

仅检查方案文档/链接、19份B006历史文件摘要和批准设计摘要；检查报告见[plan-check.json](../../../../../artifacts/reviews/monitoring-b005-1/plan-check.json)。新增业务测试、前端联调、性能、Docker均未执行；不能填写A01–A18/J01–J06通过。


文档检查首轮发现plan-check.json自身尚未落盘而暂报1条缺失链接；报告生成后重查，未修改业务代码。原首轮报告保留plan-check-first.json；最终检查以plan-check.json为准。

## v0.2 R1/R2联合扩展（全部待执行）

**唯一统一执行负责人：后端Session 1。** 前端F006交接自己的验证证据/构建/已知问题，不能据此单独关闭完整服务。以下与原A/J门槛并列必需，映射前端V08–V10及F004/F005；由统一候选、真实浏览器、实际后端绑定证明。

### R1恢复正确性

| ID | 触发时序 | 必须断言 / 映射 |
| --- | --- | --- |
| R1-01 | 任务在首次catalog之前failed或completed，cursor已跨过终态 | SSE处理器先装且连接就绪，再一次GET读到真实终态；A04/A12/J05 |
| R1-02 | 离线超过保留期/reset，目录不含失败run | 新订阅就绪后查持久receipt；日志清理不删除receipt；A05/J05 |
| R1-03 | 对齐GET读取running期间任务终止 | 后续SSE捕获终态；先到终态不被迟到GET的running/queued覆盖；A04/J05 |
| R1-04 | 事件重复/GET乱序/互相冲突终态 | 相同终态幂等，不同终态显示协议错误并显式对齐；不任意覆盖；J05 |
| R1-05 | 首次订阅/重连/页面恢复/重复onopen/提交回执触发重叠 | key+实例+连接代次去重，最多4并发；无周期状态或指标轮询；A05/J05 |
| R1-06 | POST已受理但响应丢失，CSV后来移动 | 原key查回同run/current状态；显式同key重试不重建任务；A12/J05 |
| R1-07 | POST未受理，GET key返回404 | 显示“尚未确认”，不伪造failed、不自动换key重提；允许显式同key重试；A12/J05 |
| R1-08 | 目录后服务实例变化/旧实例回执/常规重启 | 旧实例不查新实例；带错防护头409且无入队；同实例重启可恢复，ReceiptStore不随结果缓存清理；A05/A12/J05 |

网络证据记录事件seq/cursor、GET开始/状态读取/响应到达、连接代次和最终UI状态；不得只记录后端事件已发送。故障/乱序通过受控代理时明确标注，不冒充生产自然时序。

### R2导出完整性、实际保存和资源

| ID | 场景 | 必须断言 / 映射 |
| --- | --- | --- |
| R2-01 | 真实服务正常/空NDJSON，Unicode/重复hash/引号换行 | metadata身份、预计数、唯一summary/实际数、原request行UTF8+LF的SHA一致；空集也有结束清单；A13/J04 |
| R2-02 | 提前断流/缺summary/错SHA/summary后多余数据/缺最终LF | 中止/abort，不显示成功，后端流中失败不补成功summary；A13/J04 |
| R2-03 | CSV嵌入CR/LF、引号跨chunk、头错、错误行数/非法EOF | 按逻辑记录解析、列数/头/计数通过才成功；不以换行数或SHA冒称通过；A13/J04 |
| R2-04 | UTF8多字节字符在网络/64KiB应用切片处分开，非法字节 | 合法切点不误判；非法UTF8中止；原字节摘要不受重新序列化影响；A13/J04 |
| R2-05 | 用户取消、断网、慢sink、磁盘错误 | 实际reader/worker/文件流释放、abort；校验前不close；残留空占位标未完成，不删除用户文件；J04/J06 |
| R2-06 | secure context/文件API能力齐全的目标Edge/Chrome | 用户激活选文件、真实write/close/abort及覆盖行为证据；mock sink不足以关闭；J06 |
| R2-07 | 无文件流能力；备用16MiB−1/恰好16MiB/16MiB+1解码字节 | 限内完整验证后Blob；超限取消、不无验证普通下载；有压缩/无Content-Length也按实际解码字节硬计数；J04/J06 |
| R2-08 | 单条序列化逻辑记录1MiB边界，长hash/appid | 超限UI明确拒绝，不截断/改摄入计量；限内可解析；64KiB切片、最多4片在途；A13/J06 |
| R2-09 | ≥256MiB合成流、单记录≤1MiB、慢sink/重复实验 | 应用队列计数器证明上界，浏览器64MiB为优化目标、256MiB为用户批准验收上限（256MiB/1GiB各3次及增长检查）；后端RSS≤64MiB单独测；不text/blob/arrayBuffer全量读取大文件；A18/J04/J06 |
| R2-10 | 实际入口/反向代理/内容压缩或消息长度变化 | 传输分帧/压缩长度不混作内容字节；摘要覆盖解码后原始request行，头可用、导出不被缓冲为全量；A13/J06 |

R2记录浏览器/OS/访问URL/secure context/文件能力、应用缓冲断言、测量工具和基线/峰值/重复次数；JS堆与进程RSS分开。64KiB×4、1MiB、16MiB为已批准前端最终稿的参数；≥256MiB/内存目标未实测，不能直接填通过。小文件备用路径复制峰值也须测试。正常真实服务、故障代理/夹具、frontend-only分列。

### 本次文档/夹具检查

R1/R2实现测试未执行。新完整协议夹具见[README](../../../../contracts/examples/monitoring-view-v0.2/README.md)，只对人工NDJSON字节摘要和CSV解析记录数做离线核对；没有启动API/浏览器或生成256MiB压力流。[v0.2检查报告](../../../../../artifacts/reviews/monitoring-b005-1-v0.2/review-check.json)记录实际文档/样例/源码摘要核对，旧plan-check保持历史不覆盖。

## S0已执行的契约门槛

[S0测试记录](S0/TESTS.md)及[实际报告](../../../../../artifacts/validation/monitoring/B005.1/S0/contract-check.json)仅验证固定Schema、完整成功错误样例、SSE帧、导出SHA/逻辑记录、坏数据拒绝及字节边界。A01–A18、R1/R2真实API/浏览器和J门槛仍待执行；不混记为本批业务测试通过。

## 2026-10-27 S1执行增量

S1实际检查：artifacts/validation/monitoring/B005.1/S1/checks.json及0–3.log；4项新增publication测试+6项旧pipeline=10 passed。首轮ruff发现长SQL/导入/格式问题，整理后复测通过。

## S2实际检查
ruff check/format、mypy27源码通过；实际HTTP SSE重放/Last-Event-ID优先/心跳/reset/容量、超时释放、失败事件事务回滚/保留/实例持续，加S1回归共8 passed（20.80s）。证据artifacts/validation/monitoring/B005.1/S2/checks.json。其余崩溃和负载门槛在S5，不把局部检查代替全批验收。

## S3实际检查
ruff check/format、mypy28源码、test_views 1项集成测试通过（3.06s）；独立jsonschema4.23.0验证实际snapshot符合固定S0 ViewSnapshot。实际响应artifacts/validation/monitoring/B005.1/S3/snapshot.json。

## S4局部检查
2项操作集成通过（4.93s），12个实际响应通过固定S0 Schema，见artifacts/validation/monitoring/B005.1/S4/actual。ruff/mypy通过；首次全回归155通过、迁移版本旧断言1失败，已修正，等待最终重跑。

## 最终验证状态

A01–A18后端范围通过，逐项证据与实测值集中在[RESULT最终闭环](RESULT.md)。全回归164 passed（147.48s），ruff/format/mypy31源码通过；最终候选HTTP/压力重跑通过。14份实际DTO、101个固定S0文件校验通过。浏览器TS/R1/R2/J门槛未冒称通过，待前端F006。全部失败与复测见ISSUES，原日志保留。


## 2026-10-27 统一联合验收增量

用户授权后已执行正式同源前后端及R1/R2测试、review与修复，详见[统一联合报告](../../JOINT_RESULT_V1.md)。上文“待前端/未执行”属于方案和后端闭环时的历史状态；不覆盖本次实际记录。打包仍pending。
