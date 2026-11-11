# V3B006 ISSUES

状态：**尚未实施，无运行缺陷复现记录**。下面是设计阶段已知风险，OPEN_DESIGN_RISK不等于已实测bug。关联[PLAN](PLAN.md)、[TESTS](TESTS.md)、[CLOSE](CLOSE.md)。

| ID | 类型 / 状态 | 风险与待解决事项 | 处理与关闭证据 |
| --- | --- | --- | --- |
| V3B006-I01 | DESIGN_RISK / OPEN_DESIGN_RISK；实施退出门禁相关 | **前端过滤误隐藏**：旧cardFromRow只接受优化full，新样本必须独立类型与显示规则，不能降低旧资格。 | 待实现/验证；关联T20、T21、T22、T23，当前无修复/复测。 |
| V3B006-I02 | DESIGN_RISK / OPEN_DESIGN_RISK；实施退出门禁相关 | **旧入口绕过**：旧API/CLI/retry/恢复可能跳过V3；清单全覆盖，旧读能力与新执行禁用分离。 | 待实现/验证；关联T20、T21、T22、T23，当前无修复/复测。 |

新增实际问题沿用稳定编号，记录：发现批次/候选、类型（CODE_BUG / ENV_BLOCKER / EVIDENCE_GAP / BUSINESS_CONSTRAINT）、严重度/是否阻断、复现命令/输入身份、预期与实际、根因、修复文件/函数、相关设计变化、首次失败与复测证据、状态/关闭人依据。不得在关闭时删除原失败记录。

关闭需要对应测试通过或明确可核业务决定；“解释了风险”不能关闭功能/资源缺陷。仅设计风险经测试证明不存在时可写VALIDATED_NOT_REPRODUCED并给证据，不虚构修复。业务局限与bug分开，agent不能替用户接受五组底线豁免。

当前实际issue结论：**NOT_EVALUATED**；尚无产品运行或修复。


## 实施问题闭环
I01 FIXED_VERIFIED：样本计数使用真实admitted_count，未用不存在eligible_count；客户端校验样本ID/窗口keys摘要/分母/改法摘要/符号。篡改负例通过。
I02 VALIDATED：343项完整viewer回归通过，旧full解释器未放宽，四入口/旧Token/L4L5保留。
I03 FIXED_VERIFIED：capabilities核对冻结schema，执行禁用时按钮禁用；历史刷新/重读无分析POST。无B/未完成不会用0代替。完整候选真实浏览器验证移交B007，不在本批伪称通过。

## 独立验收R1补充
RV3-03：原新面板仅摘要，R1补通用改法卡/完整原文对照；旧区可读不能替代新链。详见../REPAIR_R1/ISSUES.md与TESTS.md；当前VERIFYING。
