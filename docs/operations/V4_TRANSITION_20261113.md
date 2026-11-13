# V3收口及V4入口/Git整理记录

2026-11-13用户确认V3验收通过，并授权整理V4入口、身份、任务、启动prompt、人机/本机华为协作、记忆及Git提交。核心仅汇报和模型演进；小版本Tokenizer/Template复用优先核证。用户另行要求两V3线整理的产品/开发上下文一并审阅接入，保留原作者经验，不把它们当新会话已开工。

## 本轮范围

- main：V3现场两份原始报告、核对/用户通过记录、已授权现场prompt与同步记录；V4总入口/任务/协作/复用矩阵/三份启动prompt；两线交接材料、各级导航/休眠登记/记忆；整理前11份原字节快照和摘要。
- 用户给出的两线材料：[产品上下文](../tasks/product-v4/ENTRY.md)、[开发上下文](../tasks/development-v4/DEVELOPMENT_CONTEXT_20261113.md)。两新V4角色实际ID未知，待本人启动登记。本线未创建/发送/唤醒会话，没有把旧ID转给新角色。
- 产品代码、测试、锁、运行配置未修改；未运行新分析、服务或构建；原始报告与交付包不改写。文档链接/摘要核验与报告算术记录不是产品复测。
- Git本轮只本地提交，不push；backup分支不合并main，不上传GitHub。其他并行修改先识别作者和范围，获本用户明确指向的两份交接材料纳入，其余无关修改不带入。

## 本地交付分支

backup/20261112-tokenscope-v3-c04从e45eace9844bca5a6d6b26a1b225a1ef4a7e73a3更新为4cb38e5008d413d663d0cee21ba808984dbac6c0，仅local-delivery/tokenscope-v3-c04-20261112.json小型元数据。无upstream；不checkout共享工作树、不推送、不包含包体。此次指针补记prompt-r1及用户已接受状态，原提交仍保留。

WSL及桌面20文件再次逐SHA一致。代码包仍3aaed3c5c46d4e662399f191bf328978581bae35180c36a8fd968d16db39c58e；镜像包仍52d3682751a3054533fb884ebc17138aa7b2f9474bfee1d84588a76290afbe87。构建源码仍57fe9f64d78f6363ee18a12ff97693e00ae1fe3d，本次文档commit不是新产品版本。

## 验证与证据

原验收/补证SHA保持9a9fc02d369409838cdf1597e95ba2085f7bc804007d913aaad86436024c8daf / f5c8717451f8dca6a8cf18b2855f7120397313ac16fe8b1cda388d89933557d4。归档manifest逐项核对11份快照，原位置相对链接语义保留。新入口/启动/上下文链接检查，git diff --check及精确暂存范围审查后提交。

本地机器记录保存在artifacts/reviews/v4-transition-20261113/（backup-update、最终检查/提交身份）；不用向Git提交包体或机器产物。实际main提交ID以Git记录及本轮最终回复为准。入口：[V4](../tasks/v4/ENTRY.md)；[V3用户通过](../tasks/delivery/V3_USER_ACCEPTANCE_20261113.md)。

检查结果：304处当前文档链接全部有效，11份归档快照SHA匹配。git diff --cached --check仅发现原字节快照AGENTS.md原有末尾空行；为保留SHA不修写快照，排除snapshots后当前文档差异检查通过。该历史格式提示不是产品/验证失败。
