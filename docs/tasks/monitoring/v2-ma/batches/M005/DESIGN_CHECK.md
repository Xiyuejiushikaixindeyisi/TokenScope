# 最终设计符合性矩阵

2026-10-30；最终测试结论及候选源码SHA见本批RESULT与IMPLEMENTATION_MANIFEST.json。本表关联实际测试，不能用历史V1验收代替本轮运行。测试文件均位于tests/unit/ma，既有回归注明原位置。

| 条款 | 实现符号 | 证据/测试 | 边界 |
| --- | --- | --- | --- |
| MA01 | replay.replay规范化范围键；公共make_strategy | test_replay::test_real_assets_share_only_within_uuid；既有test_simulation历史参考 | 跨appid/P共享为实例模型假设，不复现P调度 |
| MA02 | pre/now顺序，不续用旧ledger | test_acceptance::test_batch_replay_prewarm_and_repeat；test_replay三模型 | pre不计now，重复运行新账本 |
| MA03 | Submit、ingest时间归属 | test_contracts::test_windows；test_ingest::test_boundary_fails_pair；DD/MM纳秒test_acceptance及公共csv_reader回归 | request_time事件未知，统一UTC约定 |
| MA04 | scopes.status/理想字段null | test_replay::test_conflict_does_not_discard_real；test_acceptance仅pre；test_service空输入 | 冲突UUID不做理想对照，真实保留 |
| MA05 | 独立candidate/生产字段；Q仅聚合 | test_ingest::test_independent_fields_and_original；test_statistics::test_weighted_metrics_partial_bins_and_histograms | 有效子集不称全流量 |
| MA06 | metric/TokenTotals，精确Python累计 | test_statistics加权90%与超int64；test_contracts精确整数/零分母 | 各自分母，不输出收益差值 |
| MA07 | pressure/12固定桶/InstanceSnapshot校验 | test_statistics空桶/缺失桶/整小时；test_snapshot_contract反例 | 300/3600固定分母，不是吞吐 |
| MA08 | 公共distribution＋Histogram严格DTO | test_statistics尾桶/独立N；既有test_statistics_rules；test_snapshot_contract | 原200K尾桶不改变，用户开放箱独立 |
| MA09 | EncodingBatchService/TokenShardWriter/make_strategy | test_replay三模型真实资产；既有test_simulation参数化独立参考；test_models模式/模板/资产 | 普通链式近似，无hybrid实现 |
| MA10 | InputRoot、CSV独立角色/序号 | test_ingest原文换行/重复；test_failures缺头/引号/非法编码/混规格；既有test_paths；资源长单条 | 原文不修复，重复hash不去重 |
| MA11 | Store.complete、seal/verify、Processor.recover | test_service幂等/只读/封存恢复；test_acceptance真实os._exit/SQLite；test_failures磁盘；test_processes真实锁 | 不完整结果不进入目录，旧发布稳定 |
| MA12 | 独立namespace/库，app/CLI局部接入 | 全部既有monitoring测试；test_processes双队列；旧S0摘要核对 | 用户索引真实联合另待接入 |
| MA13 | 固定合成resource脚本/阶段runtime | resource-attempt01、最终复测resource-attempt02/report.json | 非现场性能，无新增耗时保证 |
| MA14 | MaService快照/目录/质量，HTTP真实路由 | test_service；test_acceptance::test_live_http_background_worker；契约验证器 | 后端通过；正式前端联调仍pending |
| X01 | MA独立scope适配，原appid留存 | MA01证据 | 不造V1 UUID租户 |
| X02 | 生产U与理想C分开命名/数据源 | MA05/06证据 | 不消费用户排行C当真实U |
| X03 | 公共有界distribution只读复用 | MA08及用户统计已存在测试 | 不修改用户开放箱 |
| X04 | 公共parse_utc/UTC声明 | MA03；用户U001接入源码SHA | 不把request_time称GF到达 |
| X05 | 公共配置claim快照/显式请求优先 | test_acceptance::test_settings_frozen_at_claim；test_models；runtime模式来源 | thinking_disabled为现场假设，不证明生产缺省 |
| X06 | 独立质量集合 | MA05 | JSON失败不抹除生产观测 |
| X07 | 保守时序冲突 | MA04 | 不引入未来缓存 |
| X08 | 同worker.lock；Dispatcher持久轮转 | test_processes实际进程；CLI轮转 | V1+MA通过；用户适配器尚未就绪，三类真实联合pending |
| X09 | 三身份、独立MA协议/状态 | test_service服务身份/目录；协议生成 | 不扩写冻结S0 |
| X10 | SESSIONS共享维护窗口 | app/cli局部diff、公共SHA清单 | 未改用户实现，未发送跨会话消息 |
| X11 | 不提供TTFT/最优算法/SSD收益字段 | contracts/API/统计源码审查 | 仅画像及实验选景依据 |
| X12 | M000–M005四文档/增量记忆 | 各batch RESULT、TESTS、ISSUES、PLAN | 前端/现场/发布与本机后端分开 |

## 审查发现与处置

- 原直方图字段为通用JSON对象，最终改为严格Histogram/Bin/Summary DTO并校验箱边界/计数/覆盖；重新生成协议及全量测试。
- CLI每次启动重置轮转会让持续V1队列占先，改为state_root/dispatcher.cursor跨进程保存位置。它只保护轮转；真正执行仍必须持原worker.lock，不用新锁替代。
- 运行中配置可能变化，在claim快照后执行能力检查；新增测试证明快照不受管理员后续设置影响。
- 封存同步包括子目录，错误回执增加安全error_detail以保留role/源序号，不回显原文；失败/原始证据保留。
- 新测试预算2与旧测试预算8冲突，修复测试夹具预算，保留生产CPU保护；历史失败日志保留。

没有自动采集、路由算法推荐/切换、TTFT反求、异常诊断、hybrid仿真、监听配置变更、镜像或交付包。临时loopback服务仅用于验收并已由测试finally终止。
