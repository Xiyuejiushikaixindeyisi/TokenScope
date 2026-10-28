# TokenScope 工作约定

## 工作范围

- 项目根目录为 /home/zhangxiyue/TokenScope，Windows 可通过 WSL UNC 路径访问同一目录。
- 新增源码、文档、研究材料、数据、环境资产和交付物均放在本项目内。兄弟项目可作为只读参考，不作为本项目的新维护入口。
- 新 session 先读本文件和 memory/CURRENT.md，再由 docs/README.md 进入自己的任务入口。按任务、工作状态和依赖选择文档与代码，不全量阅读 docs、所有上游仓库或其他任务实现。
- 最新用户决定确定工作范围；对应版本的源码、实际测试和现场证据确定能力事实。设计目标、材料描述和验证结果分开表达。

## 当前边界

- 当前阶段和允许开展的工作以 memory/CURRENT.md 为准。目录创建不构成业务实现、调研任务或部署任务的启动。
- 2026-10-23 的一期目标输入覆盖早期 V0.1 中不一致的设想。用户明确第一版目标尚需分任务讨论和规划；目录审批不等于功能设计或实施计划审批。session、turn、trace 数据可用性待确认。
- 协调会话负责协调任务划分、session 职责、阅读范围与人机工作方式；各任务的调研、讨论、设计和实现由对应 session 与用户共同推进，不在本会话提前制定全部任务的实施阶段和验收门槛。
- 当前任务入口见 docs/tasks/README.md。统一编码、计量和理想命中率计算由 Token 监控维护；原因分析消费其结果或复用同一实现。展示读取已有成果，不在页面访问时触发分析。
- 会话安排和启动依赖以 docs/architecture/TASK_SESSION_WORKFLOW.md 为准。监控设计后才 fork 并启动两类诊断任务；两类诊断设计和代码均完成后才启动自进化 Agent 的调研、设计和开发。
- 不把参考项目中的环境、审批、Git 或现场运维规则直接继承为 TokenScope 要求。

## 开发和交付

- 功能先在项目本地环境实现并测试。打包前必须取得用户同意，之后再构建镜像和交付包；不以反复构建 Docker 镜像作为日常开发循环。
- 华为交付包含镜像、代码和执行 prompt，记录对应版本、配置身份和校验摘要。当前监控交付目标为已有环境报告的华为V100；其他机器独立核实，不能按“华为机”名称推断为Ascend/NPU。
- upstream 保存固定来源，env/sources.lock.json 记录已引入源码身份。自有实现放 src 或 crates；必要上游补丁放 patches，不能仅留在上游工作树中。
- Tokenizer 与 Chat Template 绑定模型 revision、配置模式和文件摘要。真实数据与生成产物默认不进入 Git，必要来源清单和验证记录另行维护。
- 原始证据不改写；核对、勘误和结论放 docs 并指向证据。历史版本不覆盖当前入口。

- 四个现有session职责以memory/SESSIONS.md为准：总设计休眠；监控后端负责后端及华为启动验收/debug；前端负责监控及两类分析界面；审查打包负责统一审查及授权后的交付。
- 当前监控维护/现场入口为docs/tasks/monitoring/ENTRY.md，交付入口为docs/tasks/delivery/ENTRY.md。B005.1计划/设计/TESTS和冻结S0是维护依据，已完成审批不重复申请。
- 已闭环批次、旧prompt和过期记忆归档到achieve；原始证据、冻结契约和已发布交付文件保持身份，归档后更新入口和链接。
- 协作、交接、联合验收及打包顺序统一维护于 docs/architecture/TASK_SESSION_WORKFLOW.md；授权内按batch/步骤验证闭环后推进，不把整理文档当作恢复编码或打包授权。

## Git协作

- 个人项目不使用PR；通过检查后直接将源码分支合并main并显式push origin main。
- backup/*仅本地；代码包和镜像包不得上传GitHub，含产物的备份分支不可合并main。具体流程见docs/operations/GIT_WORKFLOW.md。
- 两类分析未来分支按用户启动，不因规划自动创建或开发。

## session 协作

- memory 用于研发协作；产品自进化 Agent 的调查记录放 artifacts/agent_runs，不能混入研发长期记忆。
- 同一工作区的 session 修改共享文件前读取最新状态，按 memory/SESSIONS.md 分工，避免同时改写同一模块或整份共享文档。
- 不因目录、模板或角色规划自动创建新会话、委派子 Agent、向其他会话发送消息或设置自动化。
- 每轮结束更新实际进度及必要交接。CURRENT 保持简短并链接权威文档；AGENTS 不持续堆叠历史日志。

