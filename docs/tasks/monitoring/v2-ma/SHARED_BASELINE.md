# MA提交的已完成公共依赖

2026-10-30。MA代码与测试消费用户监控线U001已闭环的公共兼容修复。本轮先核对并准备了独立依赖候选；验证期间用户线并发完成已获授权的源码集成，最终源码提交9a037466f7211126261ec2026f54b9c19c2e2151已包含这些已闭环依赖和MA源码。本线保留已同步历史，只追加MA版本/交接记录，不重新提交或撤销该线功能。

U001完成事实来自本机`docs/tasks/monitoring/v2-user/batches/U001/RESULT.md`与`artifacts/validation/user-monitoring/U000/u001-identity.json`：全量205项通过、定点及真实模式验证通过。上述其他会话材料保留原地；本次只记录必要依赖来源，不代写该线结果。

| 公共源文件 | U001已验证SHA256 | MA用途 |
| --- | --- | --- |
| src/tokenscope/ingestion/csv_reader.py | b277eab74bb7cb27b5f541567a5ede8f1eec64d491bc5e4e5670cd916bb1ce6b | 同一UTC/ISO/DD/MM纳秒解析，字段定位；MA不复制解析器 |
| src/tokenscope/domain.py | b235a9f554ab6273e5bf414f81b1d4476f04b0d29e1169a6616d7bfd4f4655a4 | 已确认现场模型别名，新安装DeepSeek现场thinking_disabled假设 |
| src/tokenscope/monitoring/storage.py | 60fc1c4364f2b5220a0612fc1e65282d812c9a0b14068bece6d1e510d0374449 | 公共配置CAS事务内别名冲突校验；旧设置不覆盖 |

上述已集成源码包含U001已完成测试及既有夹具调整：tests/unit/monitoring/test_v2_compat.py、tests/integration/encoding/test_v2_defaults.py，以及原test_models.py、test_interfaces.py、test_pipeline.py中与新默认和旧未决模式相关的修改。依赖提交不修改V1运行配置、数据库schema或发布身份。

新DeepSeek默认是现场假设，不能宣称生产缺省已核实；已有default配置保留未决保护，显式请求优先。MA运行中记录公共配置快照和模式来源。

本轮通过独立Git索引导出MA专属候选验证，提取的app.py/cli.py MA部分与M005字节SHA一致。随后确认用户线集成提交已经包含并验证三线装配，不回退该接入；本轮文档提交不携带任何新的他线代码或未完成材料。
