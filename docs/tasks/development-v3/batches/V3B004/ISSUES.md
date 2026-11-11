# V3B004 ISSUES

状态：**尚未实施，无运行缺陷复现记录**。下面是设计阶段已知风险，OPEN_DESIGN_RISK不等于已实测bug。关联[PLAN](PLAN.md)、[TESTS](TESTS.md)、[CLOSE](CLOSE.md)。

| ID | 类型 / 状态 | 风险与待解决事项 | 处理与关闭证据 |
| --- | --- | --- | --- |
| V3B004-I01 | DESIGN_RISK / OPEN_DESIGN_RISK；实施退出门禁相关 | **收紧桶误伤L2/L3**：按完整tool SHA或全部messages形状硬切会漏比较；通道各有关系约束和必需oracle。 | 待实现/验证；关联T13、T14、T15，当前无修复/复测。 |
| V3B004-I02 | DESIGN_RISK / OPEN_DESIGN_RISK；实施退出门禁相关 | **伪覆盖/计数**：后置去重或截断成员可把观察数当覆盖；前移有界聚合并暴露未扫描/下界。 | 待实现/验证；关联T13、T14、T15，当前无修复/复测。 |

评审r1落实：L1按逻辑字段可比性选择，不按完整历史角色序列；V2只取前两个角色，不能把设计风险写成已复现的V2全历史bug。T10/T13正负例仍待实现验证。

新增实际问题沿用稳定编号，记录：发现批次/候选、类型（CODE_BUG / ENV_BLOCKER / EVIDENCE_GAP / BUSINESS_CONSTRAINT）、严重度/是否阻断、复现命令/输入身份、预期与实际、根因、修复文件/函数、相关设计变化、首次失败与复测证据、状态/关闭人依据。不得在关闭时删除原失败记录。

关闭需要对应测试通过或明确可核业务决定；“解释了风险”不能关闭功能/资源缺陷。仅设计风险经测试证明不存在时可写VALIDATED_NOT_REPRODUCED并给证据，不虚构修复。业务局限与bug分开，agent不能替用户接受五组底线豁免。

当前实际issue结论：**NOT_EVALUATED**；尚无产品运行或修复。


## 实施闭环
I01 VALIDATED：12比较oracle覆盖L2/L3/稀有clock，后续历史不挡clock；旧回放通过。I02 FIXED：物理pair与成员去重、complete=false说明未覆盖；成员集合最终一次排序，不在每pair重复排序。I03 CODE_BUG/FIXED：mypy变量key/pointers类型复用13项失败，分离变量后137文件通过，候选/clock19项复测通过。初次ruff长行/导入告警已格式化修复。以上覆盖T13–15，证据TESTS。B002历史3个scale文件覆盖事件仍保留披露，不宣称已恢复。

## 独立验收R1补充
RV3-02/03：原cause摘要不足以证明能力保留；工具空/增删及完整代表请求对照由R1补齐。详见../REPAIR_R1/ISSUES.md与TESTS.md；当前VERIFYING。
