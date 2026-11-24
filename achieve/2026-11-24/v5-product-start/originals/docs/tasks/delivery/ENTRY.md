# 镜像打包与审查入口

2026-11-13：**用户已确认V3验收通过**，[验收决定](V3_USER_ACCEPTANCE_20261113.md)。本线持续版本/Git/交付职责；两个V3产品/开发会话休眠，V4新角色待启动，见[SESSIONS](../../../memory/SESSIONS.md)。

当前本轮：整理[V4入口](../v4/ENTRY.md)、两核心任务、角色/启动prompt、本机华为/人机协作和记忆，精确本地Git提交，不push。没有编码、停服务、重算、构建或发布新包。V4产品目标先由用户确认具体方案，后续交付按相应授权，不沿用V3一次性全量重算许可。

## V3已收口的权威记录

- [发布/WSL与桌面/prompt同步](V3_C04_DELIVERY_20261112.md)：固定源码57fe9f6，tokenscope-v3-c04-20261112，完整20文件校验；代码包/镜像不变。
- [现场补证核对](V3_C04_SUPPLEMENT_REVIEW_AND_CLOSE_20261113.md)：BUS01/ICSL整数收益复核、L4覆盖受限、不相加；用户通过决定以上文为准，不代造全量/线上收益。
- [已执行华为prompt](HUAWEI_V3_C04_ACCEPTANCE_PROMPT_20261112.md)是历史任务，不是V4部署说明。
- [构建前独立审查](V3_C04_REVIEW_20261112.md) · [固定身份](VERSION_V3_C04_20261112.json) · [本人记忆](../../../memory/tasks/delivery.md)。

## V4协作入口

[任务范围](../v4/SCOPE_TASKS.md) · [模型资产复用](../v4/MODEL_REUSE_MATRIX.md) · [协作边界](../v4/COLLABORATION.md)。产品负责汇报方案/DEMO与需求验收，开发负责获准编码及测试，本线接收固定候选作版本/交付，不代产品debug。

[Git规则](../../operations/GIT_WORKFLOW.md) · [交付规则](../../operations/DELIVERY_ACCEPTANCE_RULES.md) · [流程](../../architecture/TASK_SESSION_WORKFLOW.md)。main不含包体/真实数据，backup仅本地，不push --all。旧包/state/报告不改；[历史入口快照](../../../achieve/2026-11-13/v3-close-v4-start/README.md)保留本轮前过程。
