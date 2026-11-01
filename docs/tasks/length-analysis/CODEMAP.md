# Token异常分析代码地图

当前增量ARTA：auto_config/auto_targets负责T2/T4私有配置与目标；auto_duplicates负责T3显式授权与真实引用；auto_proposals实现公共四方法；current_plugin提供token-content-2，旧plugin保留历史。入口[AUTO_ADAPTER_HANDOFF](AUTO_ADAPTER_HANDOFF.md)，最终163项验证/摘要见[batches/ARTA004](batches/ARTA004/RESULT.md)。

> 2026-10-31最终实施：src/tokenscope/token_content覆盖TA000–TA006，本线112项通过。当前文件/依赖身份见[batches/TA006/CODE_IDENTITY.json](batches/TA006/CODE_IDENTITY.json)，调用面见[IMPLEMENTED_API](IMPLEMENTED_API.md)。旧“没有本线实现/拟模块/待H3”属于设计核对历史；真实结果与限制见BACKEND_HANDOFF。

| 当前本线模块 | 责任 |
| --- | --- |
| json_values / measurements / extraction | 严格JSON/数值词法、源内容度量、单请求提取与双层定位 |
| policies / rules | 显式策略匹配、T1/T2/T4事实与超限 |
| duplicates | T3完整载荷精确比较、碰撞复核、非重叠量化 |
| candidates / transformations | 待参数候选、七类guard保护变换与内嵌编译 |
| authorizations | 已存T3成员与显式业务依据派生候选，公共提交/worker两次复核 |
| plugin / stops | analysis-common-1.0静态插件、状态/预算停止位置 |

公共H1/H2源/编码/评估由主会话维护，本线仅消费。无新增Tokenizer、DB、worker或HTTP模块。

核对日期2026-10-31，设计版本TA-D0.2。当前没有本线运行实现；以下区分已存在依赖与拟新增模块。首轮核对HEAD为ac0699863a4dbe5824862d9d3c1b64a7ecd48d50，所列核心依赖当时git status无修改；本轮复核直接依赖及Dispatcher用于接口对齐。本文件记录只读源码核对，不代表测试通过。

## 1. 已存在的直接依赖

| 文件 | 关键符号/事实 | 本线用法与限制 |
| --- | --- | --- |
| [csv_reader.py](../../../src/tokenscope/ingestion/csv_reader.py) | validate_request、validate_function、RequestRecord；Chat Completions结构，文本内容，arguments字符串 | 固定协议能力；不把未支持原生Responses/Anthropic格式当已有输入 |
| [models.py](../../../src/tokenscope/encoding/models.py) | source_fields、ModelEncoder.prepare/options/render/render_deepseek | source_fields仅字符串引用；模板参与需具体身份核验 |
| [batch.py](../../../src/tokenscope/encoding/batch.py) | EncodedRequest、encode_batch、explain、ids_digest | 统一J/P/IDs和详细一致性复核；没有原字段精确归属 |
| [stage.py](../../../src/tokenscope/encoding/stage.py) | encode_input、encoded_requests | 只使用最终编码成功集合，不能分析ingestion成功但编码失败记录为正常输入 |
| [shards.py](../../../src/tokenscope/encoding/shards.py) | TokenSlice、read_slice | 公共层校验IDs摘要，Token线按需消费 |
| [storage.py](../../../src/tokenscope/monitoring/storage.py) | RawRequestStore、request_records、replay_records | 原始请求及appid/time_ns/source_record_index顺序；源库不能写入修改副本 |
| [service.py](../../../src/tokenscope/monitoring/service.py) | result_db、explain_encoding | 只读结果、资产/IDs核对；显式复核不能放GET中 |
| [views.py](../../../src/tokenscope/monitoring/views.py) | request_identity、stored_evidence、detail、body、evidence | detail为64KiB preview；body完整，source_fields可分页；分析不能用preview |
| [simulation.py](../../../src/tokenscope/monitoring/simulation.py) | PrefixLedger、make_strategy、replay | 主会话公共评估复用，本线不直接改算法或调replay改源事实 |
| [user service](../../../src/tokenscope/user_monitoring/service.py) | UserRunService.receipt | user_run_id映射base_run_id/common_name；公共来源解析复用 |
| [user projection](../../../src/tokenscope/user_monitoring/projection.py) | populate/build | facts的P/H/C校验和用户索引；本线不把排行当内容诊断 |
| [domain.py](../../../src/tokenscope/domain.py) | ModelSettings、capability | 原运行配置身份；不可要求业务用户改配置修复内容问题 |

## 2. 已有测试参考（未在本轮执行）

- [test_models.py](../../../tests/integration/encoding/test_models.py)：三模型工具fixture、批量/详细IDs一致性、特殊Token字面值；只作为真实编码测试组织参考。
- [test_views.py](../../../tests/integration/monitoring/test_views.py)：监控结果读接口；本线只读结果规则需新增接入验证。
- [test_simulation.py](../../../tests/unit/monitoring/test_simulation.py)：公共缓存规则；本线不复制一套缓存测试/实现。
- [test_user_runs.py](../../../tests/integration/monitoring/test_user_runs.py)：用户运行与基础run绑定；不当作异常分析接入通过。

## 3. 拟新增模块（未创建、路径待公共命名确认）

建议本线模块放src/tokenscope/token_content/，保持与公共analysis_common模块分离：

| 拟模块 | 责任 |
| --- | --- |
| models.py | 本线ContentUnit、策略、Observation/Fragment逻辑类型；复用公共RequestKey和证据引用 |
| extraction.py | 原协议枚举、内嵌JSON单层解析、外层/内层定位、工具归属状态 |
| measurements.py | 字符/字节/行数/条目及结构表示大小，父子重叠排除 |
| detectors.py或detectors/ | T1–T4纯规则，调用同一已解析单元，不负责缓存 |
| transformations.py | 本线guarded变换处理器，嵌入JSON与配对/结构不变量 |
| analysis.py | 逐请求纯分析入口、确定性输出及预算/取消边界；不创建第二队列/库 |
| plugin.py | Descriptor与四个逻辑调用面；静态注册给公共服务，不注册独立Dispatcher processor |

测试建议放tests/unit/token_content、tests/integration/token_content，具体公共接入路径由主会话登记后确认。当前不创建这些目录或源文件，不占用API/CLI/worker/锁文件编辑窗口。

## 4. 公共职责与待接入

主会话维护来源/报告/评估封装、接口和存储。Token线在[INTERFACE_REQUIREMENTS](INTERFACE_REQUIREMENTS.md)提供I1–I7需求，[TA-C0.2](COMMON_INTERFACE_ALIGNMENT.md)明确三项接入协议，[BATCH_PLAN](BATCH_PLAN.md)给出TA000–TA006验收；未修改公共设计或发送跨会话消息。模型编码/缓存计量继续由监控维护。

补核对[dispatcher.py](../../../src/tokenscope/monitoring/dispatcher.py)：Processor.process_next与Dispatcher.register用于公共任务调度，实际processor持共享worker.lock；Token内容插件不是独立processor。本次SHA256为625128f62f0eed84d0be0053edeefa647cab1d5175b8051f6a5055947b58c16e。

## 5. 本次读取文件身份

以下摘要用于定位本次设计依据。未来源码变化后应重新核对直接受影响内容，不以本表代替当前源码。

| 文件 | SHA256 |
| --- | --- |
| src/tokenscope/ingestion/csv_reader.py | b277eab74bb7cb27b5f541567a5ede8f1eec64d491bc5e4e5670cd916bb1ce6b |
| src/tokenscope/encoding/models.py | f7efb223eb8ccc4577f032065564a1f8f44fe44a93157a6be1062361c03481c1 |
| src/tokenscope/encoding/batch.py | 900b3bf9adf1e770ea368f26fcf35c227d8ee2c54ce91d83d785b88141ccbda1 |
| src/tokenscope/encoding/stage.py | 0a3d8fe0211a31c09a645a6dbd779b31b2d4d6ed202ec245e8591275bd4530d8 |
| src/tokenscope/encoding/shards.py | 1ea6145650967adfc97f97c98de826674bffbfcff143e01c6a248e76071e76e4 |
| src/tokenscope/monitoring/storage.py | 60fc1c4364f2b5220a0612fc1e65282d812c9a0b14068bece6d1e510d0374449 |
| src/tokenscope/monitoring/service.py | c47b89bbba2ed405d8d3e7bd3ad501e9272cf3e3d4a62a0271a36c74704c0fbc |
| src/tokenscope/monitoring/views.py | 0eeee38d2a426dfa09c74a3536290a3b8fb11e4d0627d0d65a30dbc0decd7195 |
| src/tokenscope/monitoring/simulation.py | 10e6d20ee0b8e2886e57d241a80bae69a1f0aa607896f484827df47550a0be17 |
| src/tokenscope/user_monitoring/service.py | 842d8dbbc3ed04414c97bdac460bb5017c3df2c1d3cc4a5998f87be3f7710c77 |
| src/tokenscope/user_monitoring/projection.py | 9420d2c991af65cb622851dee54c8d44bbe0603e9e6cf35ffc7e8122223a77fd |
| src/tokenscope/domain.py | b235a9f554ab6273e5bf414f81b1d4476f04b0d29e1169a6616d7bfd4f4655a4 |
