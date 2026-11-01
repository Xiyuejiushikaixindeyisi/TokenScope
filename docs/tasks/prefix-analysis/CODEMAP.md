# 低命中后端实际代码地图

2026-10-31，公共analysis-common-1.0、HTTP diagnostics-http-1。目录均为本项目自有实现；原DESIGN中的拟建描述已由下表替代。

| 路径（src/tokenscope下） | 实际职责 |
| --- | --- |
| analysis_common/contracts.py、plugins.py、wire.py、schema.py | 冻结严格Schema、稳定证据身份、精确门槛、插件/预算协议和decimal wire |
| analysis_common/source.py、encoding.py | base/user_v2只读scope、原文/切片身份、原模型资产/profile编码复核 |
| analysis_common/modifications.py、evaluation.py | 原值/嵌入保护、原子副本、数字词法保护、同make_strategy逐scope回放 |
| analysis_common/runtime.py、storage.py、service.py | 显式资源、独立任务/封存、顺序调度、重试、显式候选/授权/组合评估 |
| analysis_common/presentation.py、bootstrap.py | 精确收益与显示字段；注册真实Token插件 |
| prefix_analysis/candidates.py、structure.py、service.py | SQLite前序索引、L2同集合排序与计划 |
| prefix_analysis/dynamic.py、detection.py | L1/L3动态片段与工具定义/集合差异 |
| prefix_analysis/history.py、comparison.py | L4/L5差异、完整两请求原文/摘要 |
| prefix_analysis/experiments.py | 连续pilot选择、完整full、兼容动态组合与独立门槛 |
| api/diagnostics.py | 实例校验、手动提交/读取/取消重试/授权及组合HTTP |
| api/app.py、cli.py | 新router与Dispatcher处理器注册，不改旧监控语义 |
| token_content/* | Token会话维护，公共仅消费插件与authorizations纯函数 |

统一编码复用encoding/models.py、batch.py、shards.py及AssetRegistry；缓存复用monitoring/simulation.py中的PrefixLedger/make_strategy；来源复用MonitoringService.result_db、verify_seal及UserRunService索引身份。不能调用会写原库的replay来分析原始来源。

验证分别在tests/unit/analysis_common、tests/unit/prefix_analysis、tests/integration/analysis；真实消费者在Token线测试目录，不能以mock代替。Schema导出为scripts/export_diagnostics_schema.py，本层另存docs/contracts/diagnostics-http-1，不覆盖H0。
