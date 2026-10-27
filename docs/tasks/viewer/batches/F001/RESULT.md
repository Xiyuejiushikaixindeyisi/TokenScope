# F001 闭环记录

状态：**closed，2026-10-27**。范围仅工程与契约基础；不代表完整前端或联合服务完成。

| 退出门槛 | 结果与证据 |
| --- | --- |
| S0固定与完整类型/样例 | S0 1.0.0全部摘要一致；生成67个DTO，75个JSON样例通过，见CONTRACT_MATRIX.md |
| 精确值与接口边界 | 大整数/负delta/null/UTC纳秒/UTF8/scope/cursor/错误/bin-width/limit；102项单元组件通过 |
| 工程和依赖 | package-lock，Node22.22.2/npm10.9.7；typecheck/lint/build通过 |
| 根路径/hash路由/离线资源 | 静态检查及真实Edge检查通过，无外部请求/脚本错误，390px无溢出 |
| R1/R2边界 | S0已确认；回执样例、正常/空NDJSON原字节摘要通过；业务状态机/流式保存尚属后续批 |

代码地图：apps/viewer/src/api、src/domain、app.tsx、styles、scripts、tests；完整映射见CONTRACT_MATRIX.md与viewer/CODEMAP.md。实际源码、锁文件、构建资源SHA及环境见artifacts/validation/viewer/F001/recheck/source-manifest.json和environment.json。

I01契约依赖、I02环境命令、I03cursor缺校验、I04 Linux浏览器依赖均有处置与复测记录；当前无阻断。失败证据保留，未降低门槛。已验证的是Windows Edge；Linux浏览器未通过启动，不能宣称跨平台通过。

回退边界：撤回本批apps/viewer源码/锁/构建，保留原批准HTML及全部后端数据。回退基线原apps/viewer仅.gitkeep；本批无生产数据迁移。未实际执行删除式回退；未创建Docker、镜像或代码交付包。

允许进入F002。后端统一真实联合验收；Docker与交付包仍须用户另行同意。
