> V2历史材料，仅供追溯，不是当前启动/修复/打包指令。[原始字节](../../../originals/prompts/sessions/PREFIX_ANALYSIS_BACKEND_INDEPENDENT_REVIEW.md) · [当前会话登记](../../../../../../memory/SESSIONS.md)。下文仅迁移导航链接，历史决定和结果未更新。

# 低命中率后端与公共层独立复审启动 prompt

你负责TokenScope低命中率后端及公共层的独立复审。本prompt准备于2026-11-01；用户将它交给你并明确启动后再执行，不因文件存在自动创建/唤醒其他会话。

工作根目录：/home/zhangxiyue/TokenScope（Windows映射\\wsl.localhost\Ubuntu-22.04\home\zhangxiyue\TokenScope）。

先读AGENTS.md、memory/CURRENT.md、memory/SESSIONS.md、docs/README.md。登记你自己的实际session ID、独立复审角色、当前阶段、P0/P1范围和依赖；实际ID未知就写未知，不能复用提供方01a18be2-7112-7aa2-919b-5137d1f1b1ad。复审不接管各维护方角色。

P0读取：
1. docs/tasks/prefix-analysis/INDEPENDENT_REVIEW_HANDOFF.md
2. docs/tasks/prefix-analysis/INDEPENDENT_REVIEW_IDENTITY_20261101.json
3. docs/tasks/length-analysis/INDEPENDENT_REVIEW_HANDOFF.md及其身份文件
4. docs/tasks/viewer/analysis/ACCEPTANCE_UI04.md和公共FRONTEND_ARL5_ACCEPTANCE_RECEIPT.md

基线是arpc-local-3，完整候选prefix-common-review-20261101-1，由AR-L3/4/5叠加。本候选不是Git HEAD：main/5d824b506d9e055bcf397c3846dafc450fcf02e5仅为整理时观察，源码/测试大量untracked。先逐map核对当前摘要，记录缺文件/漂移，检查未跟踪文件；不能只看git diff。Token候选token-review-20261101-1作为消费依赖，不代签其私有实现；共享依赖不一致先说明影响。

复审范围：src/tokenscope/analysis_common、prefix_analysis、诊断API与app/CLI必要装配、对应测试/Schema。监控编码/理想命中算法只检查复用，不另造计量。Token私有策略DSL/handler归Token；apps/viewer归前端，不越权修改。

必须以已批准方案和当前实现逐项对照：
- 人工appid/源范围/异常原因/显式开关；low_hit先低命中再原文Token，长度/QPS仅Token；无阈值自动启动、不跨appid或全历史预热。
- L1/L3准确动态片段可删除副本并量化，业务决定采用；L2只对同完整工具集合固定排序；不改模型配置/线上原文。L4/L5差异独立、完整原证据可追溯，不推断缺失session/turn/Loop。
- 自动pilot严格>1pp再full，完整full严格>1pp才优化卡，恰好1pp不可通过；旧显式direct_full单独标明。原scope的N/M来自完整raw实际改变，不用样例数替代。
- Token新任务T2–T4、旧T1读取；无依据假设默认禁用。每项依据/guard先验证才可复用同操作执行；不同依据不误合/不累计收益。零负收益、P降C升、前值0比例null准确。
- 快照/幂等/retry、scope/原文hash/参数guard、预算边界、取消/源损坏/重启/封存/outbox竞态；不缩scope伪完整，不生成假after。partial/empty不替换旧默认，两方向整体ready。
- AR-L4精确Unicode码点及raw/decoded映射，重复key不假定位；多处变化截断、零宽删除锚点；before原A、comparison原B、after副本；缺依据保留before、不造N/收益，最多3例不影响总数。
- AR-L5标题/建议须对应真实Plan位置/handler/primitive并保留条件，未知操作不猜删除；新recipe ID变化不能跨task串读。
- GET零分析/编码/任务写入；只读封存、实例/task/scope隔离、正确分页和legacy not_computed，私有策略JSON不公开。当前机器Schema含跨字段运行时验证，不只看Schema结构。

特别审查限制：低命中发布阶段对已计算Plan的预算核算不是前置内存限制；256提案上限不保证大appid容量；15万请求/华为生产性能未校准；现有messages不等于原生Responses；测试配置verified不是生产审批。工具排列变化下两侧动态pointer/A-B对应、缺location的support、长片段多差异边界、未完成结果的状态及覆盖必须给出实际依据。

已有证据分版本：ARPC006为293全套+2边界（1新增，去重294）和监控254+MA46=300；AR-L4为31项+同一用例加强重跑1项；AR-L5为10项。不能相加当单次当前回归，也不能与Token重复计数。前端已消费签收/浏览器检查，但用户功能/视觉批准及独立复审尚未完成。

执行方式：先身份/源码审查，再按交接第6节使用现有.venv运行适当独立测试。pytest basetemp必须是全新不存在目录，先检查；存在就换后缀，绝不清掉前端封存state。不要安装/升级依赖，不启动无关服务；读取既有服务先检查实例和端口，不终止他人进程。保存命令、退出码、耗时、数量、工具/模型身份、stdout/stderr；环境失败与产品失败分开。按发现追加Token集成或监控兼容，不能用历史通过数替代本次结果。

请将独立复审结果写入docs/tasks/prefix-analysis/INDEPENDENT_REVIEW_RESULT_20261101.md（若已有他人结果则用新文件名，不覆盖），并更新你自己的session/记忆登记。报告包括候选/依赖摘要与漂移、逐项检查和证据、严重度问题列表（文件/行/复现/影响/归口）、实际测试、未覆盖边界和通过/有条件通过/不通过。发现问题先交维护方修复并以新身份复测，不擅自改业务代码/契约凑通过；不能代签Token/前端独立复审或用户视觉。

暂不打包或部署：不构建临时测试镜像、Docker镜像、前端发布包或代码交付包，不远端操作、不Git提交/合并/push，不创建/唤醒新会话或委派子Agent。当前交接准备不是执行授权；收到用户启动指令后完成上述复审范围再报告。
