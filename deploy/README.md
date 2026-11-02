# 部署入口

2026-11-02当前：[V2批准交付](../docs/tasks/delivery/V2_APPROVED_DELIVERY_20261102.md) · [华为真实数据两阶段执行prompt](../prompts/delivery/HUAWEI_V2_REAL_DATA_20261102.md) · [固定规则](../docs/operations/DELIVERY_ACCEPTANCE_RULES.md) · [闭环归档](../achieve/2026-11-02/v2-approved-delivery/README.md)。UIR-03由用户留V3，不是V2阻断；旧记录只作历史。

后续在这里维护 Dockerfile、Compose 和启动、验证、回退说明。当前只创建目录，没有镜像或可运行服务。

用户明确的推进顺序为：本地环境实现与测试 → 用户同意打包 → 构建并验证服务交付物。

最终向华为机交付镜像、代码和执行 prompt。发布版 Compose 应与冻结镜像身份对应；服务数量、端口、数据挂载和现场操作流程在后续计划中确定。

