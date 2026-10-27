# 前后端交互调研：TokenScope 学习与讨论材料

日期：2026-10-27。状态：调研建议，非接口定稿或选型审批。用户本轮批准现有 HTML，授权补充上下文和研究，不实现接口、不改 HTML。

## 项目依据

阅读监控 DESIGN v1.0、APPROVAL、ENTRY 及 MONITORING_V1。DESIGN 保留审批原稿“待审批”措辞，实际已由 2026-10-27 APPROVAL 覆盖。后端 B001 正在进行，批准设计不等于服务已实现。

- 第 4 节：统计/分位数/三种分箱宽度预计算，GET 不做编码或仿真。
- 第 5/10 节：启动冻结配置；PUT expected_revision 防并发覆盖；旧结果不被新配置解释。
- 第 10 节：后台运行返回 run_id、只读分页、完整结果封存后可见、SQLite 存储。
- file_ref 是服务器输入目录的相对引用；浏览器本地文件选择不等于上传或服务端可读。
- 每文件最长两小时的任务与快速读取结果必须分离。
- 请求身份是 run_id + source_record_index，hash_id 可重复。
- 业务报告继续按 appid × 模型，仅展示已发布建议；操作者的提交反馈与业务报告内容分开讨论。

## 概念与候选方式

前端负责交互和渲染；HTTP API 负责参数校验及结果读取/命令受理；后台 worker 负责耗时计算。逻辑分层不要求部署多个服务。JSON 是交换格式，REST 是接口组织方式，轮询/SSE/WebSocket 是更新方式，React/Vue 是界面工具，不能放在同一维度选一项。

| 方式 | 原理 | TokenScope 中的判断（建议） |
| --- | --- | --- |
| HTTP 资源接口 + JSON | GET 读取，POST 启动，PUT 更新 | 与已批准设计一致，作为主要候选 |
| 轮询 | 定时 GET 任务状态/结果目录 | 小规模长任务首选；仅轮询小状态，完成后停止 |
| SSE | 服务端单向推送事件 | 将来通知新结果可考虑，结果仍通过 GET 读取 |
| WebSocket | 保持双向通信 | 当前没有持续双向实时需求，不作为首版必要组件 |
| GraphQL | 调用者选择所需字段，服务端按类型解析 | 多消费者复杂关联查询时可评估，当前固定页面与现有 API 尚无引入理由 |
| 自包含静态报告 | 数据内嵌 HTML 或随文件发布 | 适合冻结示例/离线评审，配置持久化与多批次查询需要额外服务 |

轮询也是 HTTP；SSE 不替代配置写入接口。采用 HTTP 不意味着页面整页刷新。取消浏览器请求也不等于取消后台计算任务。

## 候选交互流程

操作者显式 POST 提交 file_ref/model_id → 快速取得 run_id → 后台独立处理 → 前端按需 GET 状态 → 完整发布后 GET 汇总/直方图。HTTP 202 + Location/Retry-After 是可参考模式，不是本项目已经冻结的返回码/字段。重试提交的幂等规则仍需确认，报警 event_id 幂等不等于任务提交幂等。

浏览业务看板：先确定已完成运行，再固定 run_id/appid/model，读取汇总及所选直方图；点击区间只读对应明细页；展开单请求才取已有内容。GET 不能为了展示缺少的详细映射而调用 explain_encoding，后者是分析显式调用。

新结果出现时提示更新或按协商策略切换；不让指标、直方图与明细分别指向不同 latest。run_id 是内部快照定位，不新增跨 CSV 业务窗口协议。

## 流畅性与一致性

- 分层加载：摘要和图先返回；分页明细不携带每行完整 prompt/Token IDs；证据按需读取。
- 5K 单图 41 箱，三图 123 箱，无须为绘图传全量请求。精确分位数和众数由后端给出。
- 查询缓存键包含 run_id/appid/model/metric/bin_width/筛选/排序/分页等相关变量；它是浏览器结果缓存，不是 KV cache。
- 同范围翻页可保留旧页并标示正在切换；换 appid 或模型时不在新标题下展示旧范围数据。取消过时请求并检查响应范围，防止迟到响应覆盖当前选择。
- 后端分页减少传输/查询量；虚拟列表只减少 DOM 渲染，两者不同。若请求数增大，需用实际数据验证分页延迟和内存。
- 历史封存统计与可变状态分别缓存；报告发布状态、信号消费状态和配置 revision 不能因 run_id 固定就无限缓存。
- 网络错误不解释为无建议；null 不变成 0；同一范围旧完整结果可以明确保留。读取重试和写入重试策略分开。
- 模型设置保存需服务端确认 revision；冲突后重新读取/比较，不静默覆盖；展示结果快照与下一运行配置分别呈现。
- 建议页面与 API 同源提供；离线部署使用本地构建资源，正式应用不依赖 CDN，也不要求浏览器直接打开 SQLite。

## 正式设计前需要协商的接口缺口

现有第 10 节接口清单没有完整定义：运行列表/最近完整结果发现、可选模型与 appid 枚举、单请求已存正文/证据详情、统一分页/筛选响应、分析建议发布与关联、提交幂等、读取错误和版本冲突响应。这里只标记需要核对，不能据此认定 B001 未实现，也不擅自改其公共契约。

上传是可选扩展；首版优先讨论手动放服务器文件 + file_ref 的真实流程。appid 选择器不是访问权限隔离；若涉及多业务方共享访问，需要确认实际部署与授权边界。

后续建议按页面动作逐项定义：触发动作、范围、请求参数、返回字段、加载行为、异常行为、缓存/刷新、验收条件，再决定 React/Vue、查询库及具体分页方案。OpenAPI 可用于表达双方接口合同；采用哪一版本需考虑实际后端工具兼容性。

## 官方证据与案例（查阅于 2026-10-27）

1. [Azure 异步请求应答模式](https://learn.microsoft.com/en-us/azure/architecture/patterns/asynchronous-request-reply)：长任务先受理、状态查询、完成后取结果；可参考 202/Location/Retry-After。模式参考，不要求 Azure、云部署或消息中间件。
2. [Grafana 使用看板](https://grafana.com/docs/grafana/latest/visualizations/dashboards/use-dashboards/)：手动刷新与可配置自动刷新；默认不自动刷新看板。借鉴刷新控制，不引入其查询执行架构。
3. [GitHub REST 分页](https://docs.github.com/en/rest/using-the-rest-api/using-pagination-in-the-rest-api)：只返回部分结果，使用后续页链接。说明大结果分批读取，不决定 TokenScope 的 offset/cursor 选择。
4. [TanStack Query 查询键](https://tanstack.com/query/latest/docs/framework/react/guides/query-keys)：把影响查询结果的变量纳入键，隔离缓存范围。
5. [TanStack 分页示例](https://tanstack.com/query/latest/docs/framework/react/guides/paginated-queries)：可保留上一页等待新页，避免反复跳空；跨租户不可照搬。
6. [TanStack 查询取消](https://tanstack.com/query/latest/docs/framework/react/guides/query-cancellation)：消费 AbortSignal 才能取消对应请求；不是后台任务取消。
7. [TanStack 默认行为](https://tanstack.com/query/latest/docs/framework/react/guides/important-defaults)：默认视数据为 stale，重新聚焦等可引发刷新，需按快照语义配置。
8. [MDN SSE](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events/Using_server-sent_events)：单向服务端事件；[WebSocket](https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API)：双向连接。
9. [GraphQL 官方学习入口](https://graphql.org/learn/)：类型、字段选择、查询/修改/订阅。
10. [HTTP 缓存](https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching)：ETag/条件读取/304；不能代替应用范围校验。
11. [OpenAPI 规范](https://spec.openapis.org/oas/v3.2.1.html)：HTTP API 的机器可读描述；本项目未因此选定该规范版本。

上述资料用于解释机制和形成建议；本轮未 clone 外部实现、安装依赖、运行后端或取得性能证据。

## 2026-10-27 更新：完整快照、缓存与当前范围

最新用户约束覆盖此前“首选轮询”的调研建议：

- 当前仅推进 Token 监控的前后端交互和展示。低命中率/Token 异常分析的正式交互与详细展示，等各自分析器完成设计后再继续；已有 HTML 是获批视觉参考，不等于分析接口冻结。
- 监控只展示完整计算结果，不随计算进度改变数值。现有监控 DESIGN 第 10 节按整个 run 封存发布；沿用此边界，不擅自改为每 appid 提前发布，后者是用户允许的最小完整单元而非当前已实现能力。
- 浏览器缓存每个两小时数据批次的轻量展示结果；切换页面复用对应版本。两小时是数据覆盖范围，不是缓存到期后必须清空的 TTL。
- 不定时轮询指标。新的完整结果发布后，取得完整展示快照，再整体更新指标和图表，明确数据时间范围及生成时间。
- 推荐候选为 SSE 推送完成通知 + 按版本 GET 结果 + 浏览器缓存；直接推送完整轻量 JSON 也可行。此传输选型仍是建议，需与后端协商，不声称现有服务已提供 SSE/快照包。
- 页面首次打开/断线重连时对齐最近完整版本，弥补离线期间通知；不依赖只有在线才能接收的消息保存历史数据。重复/迟到通知按版本去重，不回退到旧版本。
- 缓存由 appid/model/run 或结果版本标识；内存覆盖站内切换，跨刷新缓存可采用 IndexedDB 等持久化机制，容量和权限边界后续确定。轻量包含总量、分位数、分箱、众数和质量/时间信息，不预装所有原始 prompt/IDs。
- 分析模块仅记录用户原则：异常触发或用户显式启动；无周期轮询；每 appid×模型×分析类型展示最近一次已发布的完整分析，标明分析时间及其数据范围。一个月前的结果继续保留，不因新监控批次覆盖/删除，也不冒充当前异常。具体 API 待分析器设计后确定。

### 本机 kvcache-blog 的直接证据

只读检查 /home/zhangxiyue/kvcache-blog/assets/js/kv-cache-lab.js：
- mount，约 4352–4373 行：存在 precomputedUrl 且未内嵌结果时 fetch，response.json() 后传给 initialize。
- initialize，约 3654–3670 行：接收 data.precomputed，并建立每次 mount 的 resultCache Map。
- SHA256：9ae1556092f4c60dcdbb5e26750617bb29d2deadc0351802c1d9980331cd8243。
- scripts/kv-cache-lab-compact-precomputed.mjs 的 compactPrecomputedFile 读取 JSON、压缩结构并写出 JSON。
- 证据支持预计算 JSON 加载与页面内使用，不证明跨刷新持久化，也不是 JSONL 格式。其源码还含浏览器计算/worker，不将这部分搬入 TokenScope。
- 项目 CATALOG 的 upstream/kvcache-blog 路径实际不存在，本轮检查的是兄弟项目只读源码；未修改原文件或引入依赖。
