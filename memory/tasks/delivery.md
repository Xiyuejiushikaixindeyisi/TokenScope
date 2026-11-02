# 审查与交付维护记忆

实际session ID：01a1800e-80b4-7400-a78b-a84f5b6e888d，2026-11-02环境CODEX_THREAD_ID/CODEX_SESSION_ID一致复核。角色：镜像打包与审查／完整服务总负责；负责统一复审、授权后构建/交付和现场完整验收统筹，问题按各模块归口。

本轮已完成`tokenscope-v2-approved-20261102`：固定源码`b17cdc07b0a351d0f5c4fb1b26f0e05be2b3a0af`已push main；WSL构建镜像`sha256:a38d0ab2cfe26154c96adb5e876538893005e5cb100fc5c53640823c391683a8`，实际容器85浏览器/135独立鼠标点/15范围/120GET恢复通过，11重启复测不累加。四入口/HTML/L4L5保持，HTTP四资源同c1；UIR-03由用户留V3，不修复或阻断V2。

代码/镜像包及prompt等14文件在`/home/zhangxiyue/TokenScope/artifacts/releases/tokenscope-v2-approved-20261102`，完整复制`C:\Users\ALIENWARE\Desktop\tokenscope-v2-approved-20261102`且全部SHA一致；旧包、WSL原件保留。实际docker load验证通过，backup`backup/20261102-tokenscope-v2-approved`仅本地manifest/SHA指针，不push、不合main。其他8份未完成文档修改保留。[完整结果/文件SHA/回退](../../docs/tasks/delivery/V2_APPROVED_DELIVERY_20261102.md) · [结构化记录](../../docs/tasks/delivery/V2_APPROVED_DELIVERY_RESULT_20261102.json)。

P0下一步：接收华为唯一Markdown，依其真实数据与容器证据核对环境/用户监控搜索P90TTFT/MA/第一次用户验收，收到明确appid才两类异常和第二次验收；现场尚未执行，本机通过不能代签。[当前prompt](../../prompts/delivery/HUAWEI_V2_REAL_DATA_20261102.md)规定真实Trace3/MA18、SSH18002、停旧服务冷启、关键源码/diff/证据直接嵌正文。普通现场修复须留可重建补丁；展示/契约/用户计划变更另由用户决定。

本地容器与本次私有daemon正常退出、Windows/WSL端口关闭；证据/原输入/state保留于artifacts/reviews/v2-approved-20261102。23份关闭评审/交接/prompt归achieve，11角色入口及记忆同步，不唤醒其他角色。[长期教训](../DELIVERY_LESSONS.md)和[固定规则](../../docs/operations/DELIVERY_ACCEPTANCE_RULES.md)必须先读，防止展示漂移、未停旧服务、记忆滞后、擅改计划、合成现场/多附件prompt再次发生。

早期交付/失败/修复/暂停均为历史，完整原文保留在[本线旧记忆快照](../../achieve/2026-11-02/v2-approved-delivery/snapshots/memory/tasks/delivery.md)，对应[归档索引](../../achieve/2026-11-02/v2-approved-delivery/README.md)。不把旧状态当最新授权，也不改写旧证据。
