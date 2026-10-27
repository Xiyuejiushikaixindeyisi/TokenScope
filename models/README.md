# 模型适配资产

按实际接入的模型与固定 revision 建立目录，其中包含 tokenizer、chat_templates 和 manifest.json。当前只建立入口，不下载模型或创建虚构 revision。

manifest 记录来源、模型身份、Tokenizer 与 Chat Template 文件 SHA256、thinking/tool 等模式、特殊 Token 配置、相关库版本和一致性验证入口。服务端提供的配置与公开仓库配置需区分。

目标模型系列来自用户的一期讨论；实际支持状态必须以适配验证为依据，不根据目录存在推断已经支持。

小型固定验证样本放 tests/fixtures；大型资产由文件清单追溯，不默认纳入 Git。完整模型权重不属于当前目录初始化任务。

