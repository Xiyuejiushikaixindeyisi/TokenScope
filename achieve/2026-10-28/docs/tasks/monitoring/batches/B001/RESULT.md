# B001 闭环结果

状态：**closed**，2026-10-27。批准设计 v1.0；实际开发版本 0.1.0.dev1。满足本批门槛，允许进入 B002。

## 已实现

1. 本地独立 CPython 3.11.16、uv.lock、包入口及格式/类型/测试配置；没有替换系统环境或构建镜像。
2. 不可变三模型设置、128/1536/32 默认值、CP/MTP/能力、revision CAS；队列实际领取时冻结最新 revision，历史快照不变；单运行事务与失败/中断状态。
3. 受限文件引用、安全打开、输入副本/SHA256；CSV 分批验证、原 JSON、UTC 纳秒、质量与定位；重复 ID 保留。SQLite 暂存和质量状态，部分失败不能作为完整输入读取。
4. CLI/API 共用服务；models/settings、health/ready/version、运行状态及提交入口。编码/仿真/统计未完成，因此 submit 明确 503；CLI validate-input 只报告输入质量，不冒充完整分析。
5. 实际 [OpenAPI](../../../../../../../docs/contracts/schemas/monitoring-b001.openapi.json) 记录当前已实现接口；结果/阈值 schema 后续由对应批补充。本批没有改变已批准指标语义。

## 门槛

[测试](TESTS.md)：66 项通过、ruff/format/mypy 和真实 HTTP 进程通过。[问题](ISSUES.md)闭环，1 条非阻断依赖弃用警告保留。源码逐项自查及故障用例补充完成；无其他未决问题影响本批。

当前未提供完整 Token 监控服务。B002 才实现真实三模型编码；B003/B004 才实现仿真与结果。因此不能给前端提供伪造生产数据。

## 版本与回退

[源码 manifest](../../../../../../../artifacts/validation/monitoring/B001/source-manifest.json)绑定源码、测试、依赖锁和 schema；同目录 source-snapshot 保留原文件副本。尚无 Git commit 或 release_id。回退只恢复清单中自有文件；运行数据只用隔离目录，不删除用户输入、不触碰前端/原始证据。SQLite user_version=1，未知版本拒绝打开；不执行降级覆盖。

## 下一批

B002：先按 sources.lock 中固定模型 revision 准备实际词表/模板、验证来源，再实现单条/批量编码、轻量证据和按需映射。若资产无法取得，记录精确阻断，不能用假词表通过 IDs 对齐门槛。
