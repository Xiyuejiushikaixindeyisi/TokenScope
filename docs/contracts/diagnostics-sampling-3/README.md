# V3 sampling contract

V3B001新增版本，不覆盖V1/V2契约。只描述自动low_hit来源准备请求、receipt及封存样本。注册不解析来源、不加载模型；生产执行等待V3B002资源门禁。正常诊断不接受预指定clock/finding/recipe，L1自动链路后续按r1实现。

`wire.json`和`examples.json`由`scripts/export_sampling_schema.py`生成，`--check`只读核对。外部整数为十进制字符串；内部类型和语义验证仍由Pydantic执行。示例仅为合成协议示例，来源/摘要不是真实验收证据。

SampleManifest保存精确有序A/B成员、父范围与身份、采样规则/profile、排除原因、快照文件摘要。A/B不重叠，禁止时间包络替代成员。原source和旧result不改写；后续诊断不重新验证全源，只验证其窗口文件。样本空/来源改变/准备取消都不发布可用快照。

后续运行状态和评估结果使用独立新版本，不能将sample数据塞入旧full成果或降低旧资格。此版本不表示资源硬控制、L1定位或前端已经通过。
