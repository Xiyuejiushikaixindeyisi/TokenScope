# 镜像打包与审查入口

2026-11-24当前任务：整理[V5产品方向及启动prompt](../product-v5/ENTRY.md)，更新文档和本人记忆；后续用户已授权将本轮文档定向提交并推送main，保留V4.1与其他session未提交修改。不编码、停服务、验证产品或构建。本人角色/实际ID见[SESSIONS](../../../memory/SESSIONS.md)。

**V4.1是小改动，由其session完成本机端到端验证，不需要镜像/代码交付包，不需要华为验证。** [V4.1入口](../v4/simulator-v41/ENTRY.md)；不增加本线验收关卡，不插入V5需求或修改其活动文件。V5当前仅产品方案讨论，Token异常继续休眠，用户后续提供推理技术材料。

[本轮整理记录](../../operations/V5_DOCUMENTATION_HANDOFF_20261124.md)；[旧prompt/入口快照](../../../achieve/2026-11-24/v5-product-start/README.md)。V3已获用户验收通过，原发布身份与证据保留。

## V3已收口的权威记录

- [发布/WSL与桌面/prompt同步](V3_C04_DELIVERY_20261112.md)：固定源码57fe9f6，tokenscope-v3-c04-20261112，完整20文件校验；代码包/镜像不变。
- [现场补证核对](V3_C04_SUPPLEMENT_REVIEW_AND_CLOSE_20261113.md)：BUS01/ICSL整数收益复核、L4覆盖受限、不相加；用户通过决定以上文为准，不代造全量/线上收益。
- [已执行华为prompt](HUAWEI_V3_C04_ACCEPTANCE_PROMPT_20261112.md)是历史任务，不是V4部署说明。
- [构建前独立审查](V3_C04_REVIEW_20261112.md) · [固定身份](VERSION_V3_C04_20261112.json) · [本人记忆](../../../memory/tasks/delivery.md)。

## V4协作入口

[任务范围](../v4/SCOPE_TASKS.md) · [模型资产复用](../v4/MODEL_REUSE_MATRIX.md) · [协作边界](../v4/COLLABORATION.md)。产品负责汇报方案/DEMO与需求验收，开发负责获准编码及测试，本线接收固定候选作版本/交付，不代产品debug。

[Git规则](../../operations/GIT_WORKFLOW.md) · [交付规则](../../operations/DELIVERY_ACCEPTANCE_RULES.md) · [流程](../../architecture/TASK_SESSION_WORKFLOW.md)。main不含包体/真实数据，backup仅本地，不push --all。旧包/state/报告不改；[历史入口快照](../../../achieve/2026-11-13/v3-close-v4-start/README.md)保留本轮前过程。
