# V4 MaaS架构与试点副本记忆

2026-11-15由主会话按用户明确fork指令登记。实际fork ID `01a1de7c-a6fd-7043-baa7-987f03d5af3c`，应用标题“TokenScope V4 MaaS架构与试点”，fork／read工具已核同项目目录与idle状态。本文件不是副本已自核／已开工的回执；首次从自身环境核验，不沿用主会话或V3 ID。

入口：[maas/ENTRY](../../docs/tasks/product-v4/maas/ENTRY.md)；[独立启动prompt](../../docs/tasks/product-v4/sessions/START_MAAS_20261115.md)；[三线协作](../../docs/tasks/product-v4/SESSION_COLLABORATION_20261115.md)。

职责：先设计两个DeepSeek0731 appid的简单试点，验证缓存集中与服务表现；用户讨论设计后再准备prompt-3，经用户转交华为、获得初步结果后研究场景分类的MaaS网关改进，形成待同事粗评材料。对象为com.huawei.ucd.uiplus.wa与com.huawei.cloud.ioc.global，不叠加多个长度物理池。未来阶段以初步结果为依赖，Tokenization成本／编码复用继续pending。

三架构／现网流量研究为高优先级正文，P2为次高优先级先行材料；req/s与并发、服务标签与硬上限、TokenScope配置与生产配置、理想与真实命中必须分开。MA画像为Qwen单小时、附件缺口保留，不与试点混分母。

所有权：maas目录、三架构研究正文、P2核对正文、本文件。共享入口／CURRENT／SESSIONS由主会话维护；原证据只读。最终HANDOFF交主会话审核与提交。当前只准备入口，设计／结果／架构粗评稿均未生成；不执行产品改造、现场实验、服务、构建、commit/push或给同事发消息。
