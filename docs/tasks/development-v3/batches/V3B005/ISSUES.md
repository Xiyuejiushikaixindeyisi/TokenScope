# V3B005 ISSUES

**当前范围决定（2026-11-11）：显式 full 延期（DEFERRED_BY_USER，未实现/未运行，不记PASS），不再是本期V3门禁；自动full仍禁止。候选repair-r1-02为LOCAL_ACCEPTED_WITH_SCOPE_DECISION / ONSITE_PENDING，独立R2已关闭RV3-01/02/03。大源自动缩样和五组session_clock样本参考率优先，真实BUS01–05及现场AC-MEM待华为验收。暂不打包。**

本条为最新状态，覆盖下文历史“待裁定/待独立复验”；原日志、原失败与当时勘误保持。B005按修订范围CLOSED；B007本地收口，整体现场门禁未关闭。见[本地收口](../../LOCAL_ACCEPTANCE_CLOSE_20261111.md)、[华为交接](../../HUAWEI_ACCEPTANCE_HANDOFF_20261111.md)。

状态：**尚未实施，无运行缺陷复现记录**。下面是设计阶段已知风险，OPEN_DESIGN_RISK不等于已实测bug。关联[PLAN](PLAN.md)、[TESTS](TESTS.md)、[CLOSE](CLOSE.md)。

| ID | 类型 / 状态 | 风险与待解决事项 | 处理与关闭证据 |
| --- | --- | --- | --- |
| V3B005-I01 | DESIGN_RISK / OPEN_DESIGN_RISK；实施退出门禁相关 | **比率掩盖分母变化**：P和C下降也可命中率下降；必须并列P/H/C和pp，不能只显示百分比或声称账单/TTFT收益。 | 待实现/验证；关联T16、T17、T18、T19，当前无修复/复测。 |
| V3B005-I02 | DESIGN_RISK / OPEN_DESIGN_RISK；实施退出门禁相关 | **无B被当失败或通过**：保留A且正确解释B；业务完整门禁按ACCEPTANCE，未复核不假造独立通过。 | 待实现/验证；关联T16、T17、T18、T19，当前无修复/复测。 |

新增实际问题沿用稳定编号，记录：发现批次/候选、类型（CODE_BUG / ENV_BLOCKER / EVIDENCE_GAP / BUSINESS_CONSTRAINT）、严重度/是否阻断、复现命令/输入身份、预期与实际、根因、修复文件/函数、相关设计变化、首次失败与复测证据、状态/关闭人依据。不得在关闭时删除原失败记录。

关闭需要对应测试通过或明确可核业务决定；“解释了风险”不能关闭功能/资源缺陷。仅设计风险经测试证明不存在时可写VALIDATED_NOT_REPRODUCED并给证据，不虚构修复。业务局限与bug分开，agent不能替用户接受五组底线豁免。

当前实际issue结论：**NOT_EVALUATED**；尚无产品运行或修复。


## 实施问题记录
I03 CODE_BUG/修复待复测：attempt-03为30 passed/8 failed80.49s。8失败均发生报告GET；worker实算已完成，但严格Pydantic模型使用model_validate解析JSON字典，tuple字段不接受list。改为model_validate_json保留严格类型，不放宽契约。attempt-04复验API/幂等/篡改拒绝。
I04 CODE_BUG/修复待复测：A完成但B硬退出时初版仅留窗口checkpoint、报告没有A。改为每窗完成立即封存报告，B后续失败不覆盖A；B无窗口单独unavailable。
I05 静态类型：新增状态枚举/role变量、checkpoint tuple注解已修复，最终mypy复核。业务限制继续保留；合成Qwen零提升如实显示，不承诺五业务正提升。

I03 FIXED_VERIFIED：attempt04八API用例通过；未放宽strict。I04 FIXED_VERIFIED：attempt05真实子进程在B阶段exit7，A报告保持完整可读。I05 FIXED_VERIFIED：mypy140通过、状态单元与ruff通过。新增schema与窗口守恒校验避免将不完整/符号错误结果发布；无收益/业务时间语义不归类编码故障。

## 独立验收R1补充
RV3-01/02：原WindowEvaluation只接受clock，R1扩展冻结PrefixFinding进入同一预算/守卫/A/B。详见../REPAIR_R1/ISSUES.md与TESTS.md；当前VERIFYING。

## 2026-11-11 T19勘误
原记录只证明无自动full、GET/幂等不新增任务；显式full新范围/预算/prepare身份未实现也未测试，T19为部分验证，不能整体PASS。开发遗漏及两项底线影响见../../FULL_SCOPE_GAP.md。无用户延期决定，不删除原条款，原测试日志保留。
