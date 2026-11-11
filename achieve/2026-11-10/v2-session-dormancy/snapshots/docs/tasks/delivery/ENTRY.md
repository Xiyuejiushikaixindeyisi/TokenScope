# 版本迭代、镜像打包与审查入口

2026-11-10当前分工：**V3仅负责镜像/交付打包与审批**，不承担代码开发、debug修复、开发调度或开发验收执行。由[全新V3开发会话](../development-v3/ENTRY.md)提交完整候选及验证证据，本线审查发现的问题退回该会话处理；打包须有有效授权。当前四P0仅方向获认可，待Token探索回传后细化，未启动新打包。[最新范围与角色](../product-v3/V3_SCOPE_AND_HANDOFF_20261110.md)。

以下保留V2及ICSL文件交付历史；旧“总负责/版本级debug/独立E2E”职责不延续为V3开发任务。发布身份、原包和证据不改写。

## V2与ICSL文件交付记录

2026-11-05：用户决定V2暂时认为通过，先完成产品宣传；[现场核对与阶段收口](HV2_ACCEPTANCE_CLOSE_20261105.md)为当前状态。当前仅文档整理、记忆、版本提交/push，不启动修复/复测/打包。V3产品和宣传讨论归[既有专职session](../product-v3/ENTRY.md)，[新证据交接](../product-v3/HV2_EVIDENCE_HANDOFF_20261105.md)已发。

本线负责V1/V2/V3版本迭代、版本级debug修复协调、独立端到端验收、Git/归档记忆及授权WSL镜像/代码交付。六线开发窗口关闭，用户后续指定实施时仍公共层先行→相关后端验收冻结→前端→干净环境完整独立验收。

P0：[CURRENT](../../../memory/CURRENT.md) → [SESSIONS](../../../memory/SESSIONS.md) → [阶段收口](HV2_ACCEPTANCE_CLOSE_20261105.md)。P1：[发布身份与SHA](HV2_DELIVERY_20261103.md)、[冻结VERSION](VERSION_HV2_20261103.json)、[冻结随包prompt](../../../prompts/delivery/HUAWEI_V2_HV2_REAL_DATA_20261103.md)、[部署说明](../../../deploy/monitoring/README.md)、[Git约定](../../operations/GIT_WORKFLOW.md)。发布文件的pending仅记录发布时状态，不回写包体。

保留边界：搜索模型入口/DS可达性留V3；异常已列成果偏L4，Token零建议不等于无异常；32GiB容器压力与任务完整性待研究；MA缺失/预热冲突和报告更新不齐不伪造闭环。[原始回传](../../huawei/HUAWEI_V2_ACCEPTANCE_REPORT.md)与根核对分开，用户暂时接受不冒充全项现场重测通过。

五关冻结：[公共](HV2_COMMON_FREEZE_20261103.json)、[用户](HV2_USER_FREEZE_20261103.json)、[MA](HV2_MA_FREEZE_20261103.json)、[Token](HV2_TOKEN_FREEZE_20261103.json)、[低命中](HV2_LOW_HIT_FREEZE_20261103.json)。四入口/L4L5保持，UIR-03留V3。

[新归档](../../../achieve/2026-11-05/hv2-acceptance-close/README.md)保留原字节。新报告称现场旧state/镜像等已清理，现场回退前必须确认恢复介质与匹配state；不能将本机旧包保留等同现场可直接回退。未来交付仍遵守[固定规则](../../operations/DELIVERY_ACCEPTANCE_RULES.md)，包体/backup不上GitHub。

2026-11-05新增授权已闭环：[ICSL合成演示revision2文件包](ICSL_DEMO_R2_PACKAGE_20261105.md)，含数据和现场执行prompt，桌面/WSL保留；仅追加演示，不构建镜像或修改产品。

最新：上述ICSL revision2候选已撤回，停止交付/执行，等待V3新版验收交接；原包和证据保留。

后续清理已完成：WSL错误revision2包及打包/解压副本删除，桌面撤回旧包及原始证据保留。待V3新版数据验收交接后重新核对打包、桌面复制、SHA和新启动消息；现场真实数据/成果保护为前置条件。

最新交付：[ICSL revision3（102条）文件包](ICSL_R3_PACKAGE_20261105.md)核对、解压SHA、桌面复制完成，替代撤回revision2；不是产品V3/镜像升级，现场旧真实数据成果必须保护。
