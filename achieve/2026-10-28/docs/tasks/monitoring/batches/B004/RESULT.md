# B004 闭环

closed，代码0.1.0.dev4/schema2；131项全回归和ruff/format/mypy通过。三模型编码→DES→统计→封存→completed/outbox已接通；HTTP后台单worker和CLI共服务，GET只读；每组精确统计/三种箱宽、空态/并列众数、签名适用性、规则CAS/幂等和事务故障恢复已验证。

产物写入后才发布控制库索引，重跑事件关联首次result_ref；无效行跳过，DeepSeek缺省未决明确失败。控制库增量schema2；回退使用B003代码快照及事前旧控制库备份，不能让旧schema代码读取新库。源码清单/快照已冻结。

实际API说明在docs/contracts/MONITORING_IMPLEMENTED_API.md，OpenAPI为monitoring-b004.openapi.json。本批为合成小样本真实编码集成，B005统一真实进程/泊松压力/故障与设计对照尚未完成；生产数据不在本机提供，按用户新决定全部自合成。允许进入B005。未构建镜像或交付包。
