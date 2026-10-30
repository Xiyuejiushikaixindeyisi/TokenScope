# MA监控后端实现入口

2026-10-30。设计v1.0、独立协议1.0.0；本机代码，未部署打包。最终验证及源码摘要见[M005](batches/M005/RESULT.md)。

| 文件 | 职责与主要符号 |
| --- | --- |
| src/tokenscope/monitoring/ma/contracts.py | Submit、Receipt、Coverage、HitMetric、Pressure、Histogram、InstanceSnapshot及目录/质量DTO，跨字段守恒 |
| src/tokenscope/monitoring/ma/ingest.py | initialize/ingest/connect，双角色SQLite事实、原文与质量；公共parse_utc/validate_request消费 |
| src/tokenscope/monitoring/ma/replay.py | encode有界批与TokenShardWriter；replay按UUID/pre-now/处理时间调用公共make_strategy |
| src/tokenscope/monitoring/ma/statistics.py | aggregate/file_quality/histograms，Python精确累计、公共distribution、预生成投影 |
| src/tokenscope/monitoring/ma/storage.py | Store/normalize，提交幂等、claim配置快照、MA单库事务发布与revision |
| src/tokenscope/monitoring/ma/pipeline.py | Processor、seal/verify；同worker.lock，快照→摄入→编码→回放→统计→封存→发布/恢复 |
| src/tokenscope/monitoring/ma/service.py | MaService，提交与回执、只读目录/快照/质量分页 |
| src/tokenscope/monitoring/dispatcher.py | Dispatcher/register，进程内及跨CLI轮转；各处理器独立持同worker.lock，不能嵌套 |
| src/tokenscope/api/ma.py | 六个MA HTTP操作与服务身份检查；api/app.py局部装配 |
| src/tokenscope/cli.py | ma-submit、ma-run、ma-snapshot、ma-catalog；work-once使用公共轮转 |
| scripts/contracts/validate_ma_contract.py | DTO Schema、实际路由OpenAPI、样例及摘要一致性验证 |
| scripts/validation/run_ma_monitoring_e2e.py | 固定合成资源场景及双轮指标一致性；禁止外推现场时效 |

输入按既有InputRoot受控相对引用，原始数据/Token/运行产物在state_root/ma与artifacts，默认不入Git。MA不修改V1 control/view schema、旧seal、用户排行或统一仿真算法。

用户线维护公共csv_reader/domain/control设置兼容；本线仅消费。用户索引/回填可通过Dispatcher.register接入，其process_next必须持同state_root/worker.lock；当前真实三类联合验收仍等待用户线适配器，不冒称已接入。
