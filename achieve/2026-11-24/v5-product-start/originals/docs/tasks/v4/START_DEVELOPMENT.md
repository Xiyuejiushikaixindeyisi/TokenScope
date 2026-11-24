# 可直接发给新会话：V4模型演进与开发

你负责TokenScope V4模型演进技术核查，以及后续明确获准的实现与测试。项目根/home/zhangxiyue/TokenScope（Windows通过WSL UNC访问）。先读AGENTS.md、memory/CURRENT.md、memory/SESSIONS.md、docs/README.md，再进入docs/tasks/v4/ENTRY.md、SCOPE_TASKS.md、MODEL_REUSE_MATRIX.md、COLLABORATION.md。从本人环境获取实际ID，登记memory/SESSIONS.md和memory/tasks/development-v4.md；未知如实写未知，不使用休眠V3会话或父会话ID。

背景：2026-11-13用户明确V3验收通过；产品固定commit57fe9f64d78f6363ee18a12ff97693e00ae1fe3d，发布tokenscope-v3-c04-20261112。现有两条V3线休眠，当前新角色不继承旧全量计划/Token任务。V4核心是汇报和模型演进，产品汇报由对应产品角色负责，你独立审查实现选择，不盲从产品文档中的技术假设。

用户希望Qwen3.6→3.8、GLM5.2→5.3、DeepSeekV4→V4.1，并尽可能复用小版本的Tokenizer/Chat Template。首轮仅只读源码、既有锁文件及官方/现场证据，整理最小方案，不改产品代码/锁文件、不启动计算或容器。新官方资料如需查询优先厂商一手仓库/文档；不能凭名字或第三方报道断言兼容。缺私有资产由用户转发华为只读prompt取得摘要，不自行下载权重或访问私有服务。

再读原开发线交接docs/tasks/development-v4/DEVELOPMENT_CONTEXT_20261113.md中的审批、批次闭环和证据保护；其编写时“方向待确定”按当前SCOPE_TASKS已收敛两核心更新，不把历史候选全部恢复。

定向入口：env/encoding-assets.lock.json、models/README.md、统一编码/模型注册及user/MA契约。按问题查源码，不全量读上游。需要字段时沿真实引用找定义，不能用过期API。V3报告判断见docs/tasks/delivery/V3_C04_SUPPLEMENT_REVIEW_AND_CLOSE_20261113.md。

首轮完成：
1. 明确当前ID/别名/规格/MA制品与目标的映射，未知列待确认；先填写MODEL_REUSE_MATRIX.md的证据状态。
2. Tokenizer与Template分别比较revision/SHA及实际有效配置；核special tokens、BOS/EOS、tools/消息协议、thinking默认、generation prompt及运行库。相同文件可优先共享不可变资产，但不能让新模型冒用旧模型结果身份或静默覆盖旧锁。
3. 提出少量适用模式的渲染文本/token IDs对照计划及内存验证。有限样本相同不能证明所有输入等价；Template不同可只共享Tokenizer。新chunk_seconds需用户参数或现场标定，未给保持待配置。
4. 提交最小实现影响：模型注册/资产映射、缓存身份、API和旧结果兼容、MA制品关联、必要前端影响；不为三模型先造新插件框架。公共模型/后端契约先验证冻结，再前端接入。
5. 交出“哪些可共享/不可共享/证据不足＋实现计划＋所需现场证据”，请用户批准具体实施范围。不要将本启动prompt当成已批准编码。

后续获准实施时：在项目本机WSL实现并做针对性测试；新候选E2E停止本项目旧服务、释放端口、独立state/浏览器冷启，保留旧state/包。不反复Docker替代开发。产品页面变化须先由用户明确批准DEMO，保留四入口/L4/L5，不增加独立样本模块。编程缺陷由你修复，不让镜像会话代写代码。

交接固定候选源码/资产摘要、明确测试及未测范围、可复用资产结论、原结果兼容、资源与回退限制；由产品做需求验收，再交镜像线审查和获授权打包。用户尚未授权V4华为部署或全量重算，不能继承V3那次全量许可。现场单Markdown正文嵌关键原始证据；不要把本机合成/离线新编码当真实新模型线上收益。

不要自动唤醒V3/V2、派子agent、发消息、改其他会话文件、提交/push或打包；首轮更新本人记忆，保留共享工作树其他修改。Token重复/巨大返回研究只是后续候选，不启动私有规则开发。
