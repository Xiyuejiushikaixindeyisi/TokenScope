# B005.1 实施与验收结果

2026-10-27：S0冻结1.0.0；dev6/schema3/view1后端候选，S1–S5后端闭环，backend_ready_for_joint。真实前端联合pending；B006未启动，无Docker或交付包。最终状态以本页最新闭环记录为准。

[S0固定契约](S0_CONTRACT.md)与[实施PLAN](PLAN.md)、[TESTS](TESTS.md)为批准基线；原方案阶段记录见S0/RESULT及评审响应。

## 2026-10-27 S1执行增量

S1完成：目录/latest、sidecar、数值时间/质量范围、schema3备份回填和原子发布已实现；10项新旧流水线测试、ruff/format/mypy通过。进入S2，父batch未闭环。

## S2局部闭环 / S3开始
持久终态事件、SSE重放/reset/心跳及慢发送保护已实现并通过8项组合检查。开始S3只读快照；S4/S5及真实前端联合仍待完成，未打包。

## S3局部闭环 / S4开始
只读快照已接入，冻结统计逐值一致、ETag/304、设置变更不改变历史内容、GET编码哨兵及损坏拒绝通过；实际快照通过固定S0 JSON Schema验证。开始S4操作链路，综合门槛留S5。

## S4首轮完成 / S5综合进行中
请求多列分页/正文/证据/导出、设置规则适配、持久幂等回执与实例防护已实现，首轮检查通过。S5补充故障、压力及真实HTTP三模型全流程；不得据此宣称全批完成或联合就绪。

## 最终后端闭环（2026-10-27）

**S1–S5 closed，backend_ready_for_joint。** 代码0.1.0.dev6 / control schema3 / view schema1，S0契约1.0.0保持不变。已完成本批后端约定并停止；真实前端联合J/R1/R2、容器及V100现场验收仍pending，不进入B006构建或打包。

- S1：完整结果目录/latest/版本游标、不可变投影、组与文件质量/时间范围、schema2一致性备份和可恢复回填。
- S2：完成/空结果/失败/中断同事务持久事件；SSE重放、reset、心跳、容量/慢发送和共享空尾部读取。
- S3：轻量快照、已有1029桶/分位/指标、冻结配置规则/信号摘要、ETag/304；GET不编码、不仿真、不聚合。
- S4：统一多列请求分页、原文/轻证据详情、精确整数设置规则适配、信号分页、提交幂等/持久回执/实例防护、NDJSON/CSV导出及断流关闭。
- S5：原145项+新增19项共164 passed，ruff/format/mypy31源码通过；三模型×5appid真实HTTP合成E2E、独立计量参考、重启与进程kill恢复、1001组/256MiB压力、SSE重复耗时对照、迁移回退均通过。14份实际响应通过固定Schema，101个S0文件摘要保持一致。

### 证据与设计核对

| 需求/门槛 | 实现与实际证据 |
| --- | --- |
| BE01/02，A01–A06 | publications/storage/pipeline/events；test_publications、test_events、test_view_recovery及真实E2E/压力报告。publication、组目录、事件同事务；封存前后/事务失败/提交后退出均有检查 |
| BE03/04，A07–A08 | projection/views；快照全部统计与9直方图逐值等于原结果；固定UTC9位、组/文件范围、重复/坏行scope，历史字节不受新设置影响 |
| BE05/06，A09–A11 | views/API；同一次排序分页返回全部列，重复hash保留；原JSON精确还原/64KiB预览；轻证据与信号分页，同outbox事件可正确关联不同run |
| BE07/08，A12–A13 | receipt同事务入队，并发8次同key只一run；输入移动/日志清理仍可恢复；异体及实例冲突拒绝；NDJSON字节摘要/CSV结构与转义、空导出和断流释放通过 |
| BE09，A14–A16 | 2^53以上精确字符串、规则CAS/旧接口兼容、严格查询字段；GET失败哨兵及原seal/mtime不变；中断回填恢复、实际dev5源码读取恢复的schema2备份通过。TS消费属于后续前端联合 |
| A17–A18 | 164项全回归、实际三模型独立参考、性能及资源报告；下表为本机实测，不代替V100或浏览器测量 |

| 本机实测 | 最终值 |
| --- | --- |
| 每模型行数 | GLM 9994，Qwen 10112，DeepSeek 10131；各5appid，固定合成种子271027 |
| 提交至完成 | GLM 21.58s，Qwen 28.22s，DeepSeek 26.58s，均包含持久发布；单文件7200s门槛通过 |
| 15组查询p95最大值 | 目录7.50ms、快照18.22ms、50条请求13.66ms；每组30次 |
| 最大快照 | 87,414 bytes，低于512KiB |
| 1001组目录 | 100条页p95 7.25ms，固定revision完整遍历 |
| 256MiB导出 | 268,741,368 bytes；额外服务端RSS49,086,464 bytes（约46.8MiB），低于64MiB |
| 20条SSE（含1慢） | 正常连接终态提交→可读p95 122.11ms；慢消费者不阻塞发布 |
| SSE重复耗时对照 | 无订阅/20订阅各3次，中位19.924s/19.862s，约-0.31%（噪声范围内无明显增幅），10%目标通过 |
| 大正文读取 | 各模型最大合成正文约1.32MB，轻证据1456–4139 bytes；精确SHA匹配，服务端RSS增量2,080,768 bytes |

最终总清单：[backend-acceptance.json](../../../../../artifacts/validation/monitoring/B005.1/backend-acceptance.json)。

- 全门槛：[20261027T091811Z-report.json](../../../../../artifacts/validation/monitoring/B005.1/20261027T091811Z-report.json)（含命令/日志/退出码）；[源码清单](../../../../../artifacts/validation/monitoring/B005.1/source-manifest.json)。
- [最终HTTP E2E](../../../../../artifacts/validation/monitoring/B005.1/20261027T092108Z/report.json)、[压力](../../../../../artifacts/validation/monitoring/B005.1/stress-20261027T092249Z/report.json)、[订阅开销复测](../../../../../artifacts/validation/monitoring/B005.1/sse-overhead-20261027T091050Z/report.json)、[大正文读取](../../../../../artifacts/validation/monitoring/B005.1/large-detail-read.json)。
- [实际响应/固定契约检查](../../../../../artifacts/validation/monitoring/B005.1/runtime-contract-check.json)、[dev6实际OpenAPI](../../../../contracts/schemas/monitoring-dev6.openapi.json)。原计量设计/契约、10个编码计量算法文件和第三方锁条目未改；uv lock --check --offline通过。

### 交接、回退与停止点

前端按冻结S0继续接入，实际启动方式及接口见[运行API](../../../../contracts/MONITORING_IMPLEMENTED_API.md)和[监控交接](../../../../../memory/handoffs/2026-10-27-monitoring-development.md)。F006交付固定源码/构建资源/锁/测试/问题/回退后，Session 1统一执行真实J01–J06及R1/R2；不能用本批后端E2E关闭浏览器门槛。

回退前停止服务并完整保留schema3状态、sidecar及运行文件；使用自动生成的control.schema2.backup.sqlite3与已保留dev5源码恢复。回退不会让dev5看到schema3期间新提交的任务，新状态保留用于重新前滚/对照；禁止旧代码直接打开schema3。该读取回退已由实际旧源码测试，不是只修改版本号。

未决生产事项：DeepSeek缺省思考、GLM CP映射、GF编码资产等价、V100性能。它们不由本机合成结果代替；DeepSeek测试显式关闭思考不是生产缺省决定。没有Docker镜像、代码交付包或现场部署；B006 pending，仍须用户另行同意。


## 联合补充

2026-10-27前后端统一E2E/review完成并暂停，详见[联合报告](../../JOINT_RESULT_V1.md)。原164项为后端基线；联合修正后166项通过，候选SHA另存joint-v1/source-manifest.json，不覆盖本批原证据。
