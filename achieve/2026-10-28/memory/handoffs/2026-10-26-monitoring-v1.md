# Token 监控 v1.0 设计交接

日期：2026-10-26。状态：**第一版最终设计稿待用户审批，审批后下一轮开始 B001**。不是代码完成、镜像已构建或现场验收通过。

## 下一轮最小阅读

1. AGENTS、[CURRENT](../../../../memory/CURRENT.md)、[SESSIONS](../../../../memory/SESSIONS.md)、[监控 ENTRY](../../../../docs/tasks/monitoring/ENTRY.md)。
2. [DESIGN v1.0](../../../../docs/tasks/monitoring/DESIGN.md)、[公共契约](../../../../docs/contracts/MONITORING_V1.md)、[示意 JSON](../../../../docs/contracts/examples/monitoring-v1-illustrative.json)、[batch 规则](../../../../docs/tasks/monitoring/batches/README.md)。
3. [环境核对](../../../../docs/huawei/MONITORING_V100_DESIGN_REVIEW_2026-10-26.md)与 [CODEMAP](../../../../docs/tasks/monitoring/CODEMAP.md)中当前批相关入口；有疑问再读原始报告/对应源码，不重读全部研究仓库。

当前版本集、摘要及历史见 [VERSIONS](../../../../docs/tasks/monitoring/VERSIONS.md)。审批记录应绑定该设计与契约摘要；尚未收到审批时不开始实施。

## 不应重新发散的已确认范围

- 单 CSV 单模型，三份文件；GF 后完整原 JSON 的 J、模型输入 P、输入复用 H、重算 C=P−H、输出 O 分开。
- 三模型用同一链式离散事件仿真；B=GLM 128/Qwen 1536/V4 32，MTP 默认开启，CP 默认 1；Qwen/V4 标为近似，仅增强 hybrid 类不实现。
- 空缓存起始、租户隔离、无限逻辑容量、前请求输入缓存立即可用；不还原生产并发，不使用生成输出构建缓存。
- 坏行跳过、重复 ID 每行独立、UTC/UTC+8、后端权威统计、配置下次运行生效、阈值数值延后。
- 三组 5K 直方图覆盖有限 0–200K 与开放 ≥200K 尾桶；并列众数都返回；P50/P80/P90 图外数值。分析器复用已有结果/同一编码器，展示 GET 不触发分析。

## 环境与交付结论

原报告 SHA256 `198a3e08bc51c57be94d3bffc4f7e7092dfcc66558a90a23bd904ba304aee422`，保持原件不改。现场 40 可调度逻辑 CPU、约 376 GiB 内存、Docker 26.1.4/Compose v2.27.1；共享宿主，资源不是独占。GPU 驱动故障不进入首版 CPU 依赖。

默认单文件任务并发 1、总计算预算 8、容器 8 CPU/32 GiB；批次 256 条或 16 MiB，单条超限独占批次。正式调优须记录，不能改变 Token IDs/指标。工作区和临时目录放 `/home` 下可写路径；现场没有现成 TokenScope 目录。旧内核 3.10、定制 glibc 输出、包兼容性和每文件 <7200 秒仍需真实镜像/负载验证。

最终交付代码包 + 执行 prompt + CPU 镜像，含离线编码资产、Compose 与版本校验清单。B006 现场 Agent 依次做预检/加载/启动/小样本/三文件与重启验收；启动成功不能等同于总体通过。当前只完成设计，不已有这些交付物。

## Batch 纪律与待输入

六批依次为骨架、编码、DES、统计报警、本机统一验证、交付及现场验收。每批启动时写 CONTEXT/PLAN，过程中增量维护 ISSUES/TESTS，末尾 RESULT 对照门槛闭环后更新 [监控记忆](../../../../memory/tasks/monitoring.md)、ENTRY/CODEMAP/批次索引，才能进下一批。B005 统一端到端、健壮性和 M01–M12 设计对照；B006 补现场交付和性能证据。

尚待：用户审批；B002 完整 tokenizer 资产与参考 IDs；B005 三份代表 CSV；B006 实际目录/端口/包与目标机验证。数据未到不阻止早期 batch 的确定性验证，但不能伪造 B005/B006 闭环。阈值数值、增强 hybrid 和完整 PrefixLens 不作为本版开发阻塞。

## 会话维护边界

本 Session 1 `01a1682f-956d-7630-afe7-e123ba38dfc0` 负责监控；前端 fork `01a17811-4c9a-7513-befc-b35723aec96e` 已由用户指派展示。保留其 CURRENT/SESSIONS 记录和 HTML 工作，不再沿用旧主副角色绑定，也不新建/通知会话。Session 2/3 尚按其依赖规划，未取得实际联调证据；自进化 Agent 依赖两类分析设计和代码完成。
