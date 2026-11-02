# V2批准版本交付：2026-11-02

状态：用户明确认可V2可交付并授权Git/push、WSL构建/打包和Windows桌面交付；执行中，尚未宣称镜像/包完成。版本tokenscope-v2-approved-20261102，基于已独立复审viewer-uir01-pointer-fix-20261102-c1。UIR-03按用户决定留V3，不列V2阻断、不修复；历史复审原文保留。

固定展示：用户监控、搜索与排行、异常分析、MA集群监控四入口，UI-02/UI-04及最后L4/L5认可；本轮仅交付配置/文档整理，不新增业务设计。候选已226单元组件、85浏览器、135鼠标点和120地址恢复通过；正式镜像必须从push的固定commit构建并另做容器/资源/重启验证。

[华为真实数据prompt](../../../prompts/delivery/HUAWEI_V2_REAL_DATA_20261102.md)是唯一当前现场执行入口：Trace3CSV→用户监控（搜索/P90 TTFT）→MA18CSV→第一次用户验收→指定appid两类异常→第二次验收。字段分开核对，停旧服务后空state冷启，SSH18002，最终唯一Markdown嵌关键源码/证据。旧现场prompt已归档，不在华为使用合成验收包。

[固定规则](../../operations/DELIVERY_ACCEPTANCE_RULES.md) · [本次归档](../../../achieve/2026-11-02/v2-approved-delivery/README.md) · [长期教训](../../../memory/DELIVERY_LESSONS.md)。完成后在此记录固定源码/远端SHA、image ID、容器测试、WSL/桌面路径、全部SHA、本地backup、残留项/回退与清理。
