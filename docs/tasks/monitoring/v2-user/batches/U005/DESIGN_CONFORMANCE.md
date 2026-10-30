# 设计符合性自检

依据获批DESIGN v1.0和BATCH_PLAN；2026-10-30开发Agent自检，不代替前端/现场签收。U-R编号为本次对照索引，覆盖完整设计章节。

| 要求 | 实现入口 | 证据与结论 |
| --- | --- | --- |
| U-R01 GB appid×common_name、空缓存、原JSON J、P/H/C、duplicate | user_monitoring/service.py；复用基础pipeline/encoder/replay | 三模型HTTP、test_user_runs、test_v2_defaults、长JSON保真；通过 |
| U-R02 UTC两格式、别名/CAS、DeepSeek明确默认与旧配置保留 | ingestion/csv_reader.py、domain.py、monitoring/storage.py | U001全量/编码及本次全量；通过；生产缺省未知不变 |
| U-R03 绑定/幂等/历史回填/独立身份 | user_monitoring/storage.py、service.py | 并发8请求、基础响应丢失、预留绑定拒绝、旧run、MA错误身份；通过 |
| U-R04 C开放稀疏箱、准确sum/count、全部并列、最低箱代表 | user_monitoring/projection.py | 独立算例、>2^53/64位累计、200k开放箱、空/多峰及分页；通过，不改V1/MA尾桶 |
| U-R05 四指标精确筛选、UTF8稳定排序、过滤后分页 | user_monitoring/ranking.py | Fraction oracle、NULL/AND/字面%_/中文、revision、只读HTTP；通过 |
| U-R06 固定chunk、le/lt、P90参考非总体阈值 | user_monitoring/estimator.py | 1000 Decimal独立枚举、50%/75%示例、n0/无预算/0P90/覆盖外；通过 |
| U-R07 情景来源/不可变版本/评估快照 | contracts.py、estimator.py | 并发幂等、模型服务冲突、旧快照/重启、人工假设限制；软件通过，真实性与负载适用由操作者确认 |
| U-R08 独立API/control1/index1与封存、GET无副作用 | api/user.py、user_monitoring模块 | 9操作/严格DTO、缺库不创建、损坏索引拒绝、tmp原子发布/原seal不变；通过 |
| U-R09 同state_root单重任务额度、MA隔离、旧S0 | api/app.py、cli.py、既有Dispatcher.register | 真实CLI持锁时3类待处理任务均不推进，解锁后全部完成；MA同UUID跨appid命中/跨UUID0，用户跨appid0；旧S0全回归通过 |
| U-R10 资源、故障恢复、版本/渐进闭环 | U000–U005记录、validation脚本 | 预设资源门槛、真实进程退出重建、源损坏/权限/资产缺失、289回归+增量15；通过 |

实现细化：未发布索引在重启后从已核验源完整重建，即使rename已完成也不凭残存文件名直接发布；满足可恢复/不半发布要求。base seal摘要间接绑定原配置与资产快照；不复制改写原签名。计数使用十进制字符串/Python整数；源单值仍遵统一facts的范围。

不包含：等待队列建模、逐请求TTFT仿真、真实性能自动校准、生产路由切换、自动采集、hybrid、前端页面、监听开放/打包部署。界面UI-01由前端负责，未代签。
