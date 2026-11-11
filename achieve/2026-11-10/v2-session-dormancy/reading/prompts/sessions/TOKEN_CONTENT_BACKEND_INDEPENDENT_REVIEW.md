> V2历史材料，仅供追溯，不是当前启动/修复/打包指令。[原始字节](../../../originals/prompts/sessions/TOKEN_CONTENT_BACKEND_INDEPENDENT_REVIEW.md) · [当前会话登记](../../../../../../memory/SESSIONS.md)。下文仅迁移导航链接，历史决定和结果未更新。

# Token异常后端独立复审启动 prompt

2026-11-01用户已明确授权启动；本prompt已实际发送至审查session 01a1800e-80b4-7400-a78b-a84f5b6e888d。按归口修复并复验、形成实际报告；尚无Token私有全范围通过结论。下文公共arpc-local-3是原快照，当前公共arpc-local-4须记录依赖漂移，不覆盖旧身份。

---

请对 TokenScope Token异常后端进行独立源码及本机测试复审。本次不打包或部署，包括不构建临时测试镜像，不构建前端发布包，不执行Git提交、合并或push；不接触生产数据/远端机器。先明确你的实际session ID、独立复审角色、任务阶段、优先级与依赖，并更新自己的登记；未知ID如实记录，不继承提供方ID，也不创建其他会话。

项目根目录 /home/zhangxiyue/TokenScope（Windows同目录为 \\wsl.localhost\Ubuntu-22.04\home\zhangxiyue\TokenScope）。先读 AGENTS.md、memory/CURRENT.md、memory/SESSIONS.md、docs/README.md，再按以下顺序核对：

1. docs/tasks/length-analysis/INDEPENDENT_REVIEW_HANDOFF.md：复审范围、验证矩阵、命令、证据保护及授权边界。
2. docs/tasks/length-analysis/INDEPENDENT_REVIEW_IDENTITY_20261101.json：候选 token-review-20261101-1。Token私有17源码+19测试/基准辅助文件的总体摘要31fd67c2e7432baf24daf6ed8b43cf024a4ebc22824f689ec8f833e56ae0b564；每文件SHA权威。观察HEAD=5d824b506d9e055bcf397c3846dafc450fcf02e5，但私有源码/测试未跟踪，HEAD不是候选。核对所有map并报告漂移；不清理共享工作区、不漏untracked、不覆写旧身份。
3. docs/tasks/length-analysis/AUTO_ADAPTER_HANDOFF.md、AUTO_RECIPE_SCHEMA.json、batches/ARTA004/RESULT.md、FRONTEND_READABILITY_ART4.md及其EXAMPLES/IDENTITY。
4. docs/contracts/analysis-recommendations-1/README.md及manifest/public-views；docs/tasks/prefix-analysis/FRONTEND_REWORK_IMPLEMENTATION_HANDOFF_ARL3.md → FRONTEND_READABILITY_HANDOFF_ARL4.md → FRONTEND_COPY_HANDOFF_ARL5.md；公共当前arpc-local-3。同时参阅docs/tasks/analysis/batches/ARPC006/RESULT.md。
5. docs/tasks/viewer/analysis/ACCEPTANCE_UI04.md：当前viewer-analysis-ui04-local-1。不要使用仍写UI-03/AF006和“自动收益留V3”的旧PROMPT_INDEPENDENT_REVIEW.md作为本轮范围。

Token提供方01a18fcd-0464-7cf1-b435-4f394bd33e66维护token_content及本线测试；公共/低命中01a18be2-7112-7aa2-919b-5137d1f1b1ad维护任务/归组/证据/回放/API；前端01a19111-344a-75c1-84e0-14db8be08f4f维护展示。不要接管对方源码。问题给出精确复现并归口修复。

当前已实现T2–T4自动建议/离线量化，编号保留；新plugin token-content-2不输出T1，旧token-content-1/T1报告兼容。工具定义只读做身份/schema验证，工具定义诊断统一低命中且不增长度精简。四方法adapter协议token-auto-proposals-1，generator_identity=token-content-recipes-1；公共推荐/只读GET为analysis-recommendations-1。参数错配、自进化Agent不在复审实现范围。

优先复测：严格版本/配置/basis作用域与工具摘要；T2字段/行条目选择；T4最后K与K=0、完整容器替换；T3真实引用映射与普通副本授权、Observation无Finding、不得删除调用消息；prepare重新推导原文/目标/参数、内嵌JSON词法及变更guard；原appid全scope回放、raw变化N/M、noop/零负/P降C升；每依据独立prepare而同操作复用Evaluation；各预算/取消/源变化/重试/partial不覆盖ready；局部证据与最多3例、缺依据before可见而N/after未知；历史T1/legacy不回填、GET无分析写入及实例/task/scope隔离。

已有历史结果是162项完整回归+1边界增量=163，ART4另1项定向测试；公共294项分析包含重叠，不累加成新的全量数字。这些不是你的复审结果，请运行本线完整unit+integration及mypy/ruff，再按风险选择公共集成测试，记录实际命令、日志、退出码、计数、耗时、环境身份。使用交接中的全新basetemp，路径存在就换名，不允许pytest清空正在给前端展示的旧state。无需镜像，使用已有.venv；不擅自升级依赖。

所有样例输入、策略、引用均为明确synthetic；真实的是固定资产编码、worker、回放和GET。verified basis字段不是生产审批，fixture://本地映射核对不是远端工具协议验证，结果不证明业务质量/TTFT/生产收益。默认空bundle不增加前端参数表单，不装载测试策略为生产默认。四项方案独立评估，收益不相加。

ART4可复用根目录 artifacts/validation/art4-readable-20261031-01/test_chinese_recipes_actual_se0；task=716967b3-3e69-4f58-82e8-37f5e7715b8d，instance=2fceceeb-ea9d-4d67-9c63-da25cca35c1e。先GET capabilities核对实例，再读封存报告；本机端口状态以UI-04验收入口为准，不能重复启动或终止其他会话服务。前端工程验收已回传，用户功能/视觉验收仍不能代签。

最终将独立复审结果沉淀在项目内，给出：候选/漂移、审查范围、实际测试证据、按严重度的问题与归口、修复复测情况、限制及通过/有条件通过/不通过结论。没有问题也要列未验证事项。不要把交接准备或测试通过等同于生产策略批准、用户视觉批准或发布授权。此任务结束不自动打包部署或Git收口。
