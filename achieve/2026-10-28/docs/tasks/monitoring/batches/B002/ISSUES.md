# B002 问题记录

| ID | 问题/影响 | 处理与证据 | 状态 |
| --- | --- | --- | --- |
| B002-01 | DeepSeek Recipe 默认思考，先前参考官方 vLLM0.23 缺省相反；新参数声明 GF 0.30.0rc2，不能沿用旧版本结论 | 用户指定 pending；Qwen/GLM 模板默认；代码明确报缺省未决，显式模式可测；三模型参数仅筛选沉淀未激活 | pending_user_evidence，整批不关闭 |
| B002-02 | numpy 下载重试拖慢环境准备 | 原 uv 安装最终成功，精确锁版本不变；两次备用尝试已中断。不是编码性能测试 | closed |
| B002-03 | 首轮格式/依赖缺失、Jinja2 未显式依赖、Qwen 内嵌与外置 chat_template 重复 | 补直接依赖；按外置固定模板优先；最终静态检查通过 | closed |
| B002-04 | Qwen added_tokens_decoder 的 JSON dict 不能直接传给构造器；新版参考 API 默认返回映射 | 转为 AddedToken 对象；独立参考显式 return_dict=False；真实 IDs 对齐通过 | closed |
| B002-05 | 自查：CPU 预算进入编码身份；SDK codepoint 区间与契约 byte 单位不同 | 身份排除 CPU；所有公共区间转 UTF-8 byte；1/4线程身份一致及中文边界测试通过 | closed |
| B002-06 | 来源引用可能误把补入的 model 字段说成来自原 JSON；Recipe 对部分模板开关未实现 | 源字段取原请求；不支持的模板模式明确行错误，不能静默忽略；按需重编码验证摘要 | closed |
| B002-07 | 当前按需映射提供精确 prompt offsets 和 JSON pointer references，没有证明每个 Token 对应唯一原 JSON 字段 | 显式 partial/unknown，符合当前契约允许缺失来源；不能作为完整字段贡献统计；后续分析消费时继续评估 | documented_limitation |

没有替换批准设计、激活现场 profile 或启动增强 hybrid。完整输入编码落盘与运行服务衔接、扩大参数模式覆盖及 B002 最终复审尚未完成；待 DeepSeek 缺省选择明确后共同完成本批关闭，不提前进入 B003。

增量：B002-01 的生产默认仍 pending，但按最新继续 B002–B006 授权，编码实现以明确拒绝缺省、显式模式参考一致收口，不宣称生产模式已确定。B002-08：编码阶段同库流式读写会互锁，RawRequestStore 改 WAL，保留失败日志和复测；全量落盘阶段补质量计数与失败未封存测试。
