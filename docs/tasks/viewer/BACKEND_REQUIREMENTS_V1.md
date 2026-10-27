# 监控前端所需后端增补 v0.1

2026-10-27；消费方提案，供监控会话核对；未修改其源码/批准契约，也未发送跨会话消息。完整设计见 [MONITORING_INTERACTION_V1](MONITORING_INTERACTION_V1.md)。当前源码可能继续变化，先核对是否已补齐，再安排实现。

## 1. 已有能力：不要重复开发

| 源码/接口 | 本轮观察 | 前端复用 |
| --- | --- | --- |
| app.py: GET /models；GET/PUT settings | 模型枚举、能力、配置revision | 模型列表实际已经有，覆盖早期调研中的待核对项 |
| POST /analysis-runs、GET /analysis-runs/{id} | 202受理和状态回执 | 手动file_ref提交 |
| service.metrics | appid/offset/limit、total_groups | 汇总/阈值/能力等已有值 |
| service.histograms / statistics.aggregate | 三指标×三宽度已预计算；GET一次选一种宽度 | 不增加统计算法，只组合已有值 |
| service.lengths | metric/区间/分页、rank/ref/hash/time/length | 下钻已具基础；尚不能一次得到J/P/H/C/O多列 |
| GET signals、GET/PUT threshold-rules | 持久信号和规则更新 | 监控报警，不等于分析结果 |
| result_db/control.result | completed索引存在才读取 | 不以文件夹存在判断结果可见 |
| control.complete | 完成索引和报警outbox同事务 | 增加UI发布日志的合适事务边界 |

证据为读取源码，不是执行测试；[源码摘要](../../../artifacts/reviews/viewer-interaction-v1/source-observations.json)。报警outbox仅异常产生，不能代替每个完整运行都需要的UI发布事件。

## 2. 增补项及处理责任

P0为发布/缓存链路必要项；P1为现有监控HTML对应操作的完整性要求，不可缺失却声称全部接入。

| ID | 优先级 | 需要数据或接口 | 额外后端处理 |
| --- | --- | --- | --- |
| BE01 | P0 | 完整结果目录：appid/model、active_run_id、data_range、published_at、publish_seq、snapshot_url、view_schema | 持久组索引/发布目录，查询不扫CSV；目录与cursor一致 |
| BE02 | P0 | SSE完成通知、持久cursor、reset | 在complete事务登记发布日志，提交后发送；断线回放、有界队列、心跳；正常无报警也发 |
| BE03 | P0 | 单run/appid轻量展示包 | 组装已有metrics、全部histograms、冻结配置/规则和固定信号摘要；不重算 |
| BE04 | P0 | 组级实际时间范围、文件/组质量范围标识 | facts按appid取min/max(time_ns)再转UTC；不同精度时间文本不得直接字典序比较；坏行无法归属不分摊 |
| BE05 | P1 | 多列请求列表、单请求详情 | 读取已存J/P/H/C/O、ref/hash/time、原JSON/轻量证据；索引/稳定分页/搜索；禁止GET调用explain_encoding |
| BE06 | P1 | 信号按appid筛选、分页、规则比较类型 | 不把可变消费状态混入immutable包；有界返回 |
| BE07 | P1 | submission_key幂等与回执查回；可选操作终态事件 | 同key同体返回原任务，异体冲突；不能复用报警幂等代替 |
| BE08 | P1 | 全量明细只读流式导出 | 直接读已有事实，不塞进首次展示包 |
| BE09 | P0 | schema/错误/null/大整数/ETag/服务实例标识 | OpenAPI和样例一致，超安全整数可靠序列化，跨实例缓存隔离 |
| BE10 | P0 | latest规则与固定历史读取 | 建议组最大数据时间后publish_seq排序，避免旧文件晚完成覆盖新数据 |

BE04是小型元数据聚合，不新增Tokenization、命中算法或诊断算法。BE03可封存时预生成每组JSON，也可按需确定性只读组装；两者均须同版本不可变。预生成时间纳入7200秒预算。快照体量、目录成本与分页延迟需实测。

## 3. 建议接口形状（待后端确认命名）

### 目录
GET /monitoring/catalog?appid=...&model_id=...&offset=0&limit=100

响应包含service_instance_id、view_schema_version、cursor、catalog_revision、items、next_offset。项包含appid/model/active_run_id/publish_seq/data_range_utc/published_at/snapshot_url。分页绑定catalog_revision，过期重读，不拼接不同目录版本。无筛选可用于appid发现，模型枚举仍复用GET /models。缺失组不是零流量结果。no_valid_rows可列运行目录但不创建appid。

### 通知
GET /monitoring/events?after=<cursor>；text/event-stream。首连after，重连Last-Event-ID优先。模型级result_published事件携带id、run_id、model_id、publish_seq、published_at、view_schema_version，不附海量appid/指标。当前范围随后查询目录，由目录决定该事件是否改变active_run_id。

建议事件示例见 examples/monitoring-publication.example.json（人工构造，不是实测）。publish_seq持久单调，不用时间推算。事件过期返回reset并提示重取目录；日志容量/保留策略后端确定并测试。慢连接可断开后回放，不保持SQLite长写锁，不阻塞计算。后端内部读事件日志不等于浏览器轮询指标。

### 快照
GET /analysis-runs/{run_id}/view-snapshot?appid=...

| 字段组 | 要求 |
| --- | --- |
| identity | service_instance_id/view_schema_version/run_id/appid/model_id/publish_seq |
| provenance | 组data_range_utc、file_data_range_utc、published_at、source_label、冻结settings、encoding/algorithm身份、simulation_semantics |
| metrics | 直接复用GroupMetrics命名和公式 |
| distributions | metric → bin_width → 现有完整Histogram，覆盖1000/2000/5000 |
| quality | file_quality和确能归属的group_quality，明确scope |
| thresholds | 当前结果冻结的规则/比较状态，不替换成今天编辑的规则 |
| signal_summary | 当前组固定信号数/分页引用，不含可变消费状态 |
| capabilities/links | 已有请求内容/证据/导出能力，不承诺不存在的模板正文 |

同run/appid/schema的内容不可变；未知组/运行404，未发布拒绝读取，不以部分200应答。ETag与内容摘要序列化规则需明确。强制绑定run读取，GET不重新aggregate。

### 请求明细
建议GET /analysis-runs/{id}/requests 和 /requests/{source_record_index}。
列表固定appid/run，offset/limit沿用现有方式，支持长度指标区间及稳定排序、hash搜索。不能用J/P/C三次排名分页拼接多列，各排名集合不同。详情按ref联结已有记录，正文分片或预览须标明截断，仅影响展示不影响计量；缺模板文本则不提供该视图，不现场重新编码。hash_id重复搜索应保留所有匹配。

## 4. 联调所需样例与验收

后端提供OpenAPI/错误结构，以及正常、无有效行、缺组、坏行/重复、≥200K、null、大整数、不同配置结果样例；通知重放/reset样例与固定schema身份。样例标注synthetic，真实结果另记证据。

顺序建议：BE01/04/10目录语义→BE02持久通知→BE03/09快照→BE05–08操作完整性。前端可并行用假服务验证交互，但不宣称真实联调。

必验：事务提交后发送前崩溃恢复；目录与订阅之间发布不漏；重复事件去重；旧文件不抢新数据；慢客户端不拖任务；GET不触发编码；所有图/明细固定run；保存设置不改旧快照；任务提交幂等/冲突。原监控验收标准不降低。

请后端会话核对并确认：latest排序、预生成或只读组装、游标保留/reset、提交终态反馈、请求详情能力、大整数序列化。本文不擅自修改其实现或分配任务。
