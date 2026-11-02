# 当前状态

2026-11-02：V2批准版`tokenscope-v2-approved-20261102`已完成固定源码push、WSL构建、容器独立复验、代码/镜像打包和Windows桌面14文件SHA一致交付。WSL原件/旧包保留，backup仅本地；华为真实数据尚未执行。[版本/文件/校验与回退](../docs/tasks/delivery/V2_APPROVED_DELIVERY_20261102.md)。

源码`b17cdc07b0a351d0f5c4fb1b26f0e05be2b3a0af`，镜像`sha256:a38d0ab2cfe26154c96adb5e876538893005e5cb100fc5c53640823c391683a8`。容器85浏览器、135鼠标点、15范围、120地址恢复通过，11重启复测不累加；四入口/批准HTML/L4L5与已复审c1资源一致。UIR-01/02闭环，UIR-03按用户决定留V3、不修、不阻断V2。

华为只用真实Trace3/MA18 CSV，先用户监控（搜索/P90 TTFT）再MA→第一次用户验收→用户指定appid→两类异常→第二次验收。SSH18002；唯一Markdown嵌关键源码/diff/问题复现和证据。[当前执行prompt](../prompts/delivery/HUAWEI_V2_REAL_DATA_20261102.md)。真实TTFT参数/校准、MA配对、编码模式和业务依据现场核实，不能造数或代签。

本地测试容器/本次私有daemon已停、Windows/WSL端口关闭，证据与state保留。每次新候选验收先停旧服务，空state/new dist/新浏览器；[长期教训](DELIVERY_LESSONS.md) · [固定规则](../docs/operations/DELIVERY_ACCEPTANCE_RULES.md)禁止再犯展示偏移、旧服务混淆、记忆滞后、改用户计划和不合格prompt。

[SESSIONS](SESSIONS.md)为角色权威，其他8份未完成修改保留；V1/总设计休眠，hybrid/自进化Agent未启动。[闭环归档](../achieve/2026-11-02/v2-approved-delivery/README.md)保存历史原文，最新决定优先。
