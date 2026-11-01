# Token内容分析后端交接

前端使用：[Token前端接入TA-FE1](FRONTEND_HANDOFF.md) · [启动增量prompt](../../../prompts/sessions/TOKEN_CONTENT_FRONTEND_INTEGRATION.md)；与[公共/低命中前端交接](../prefix-analysis/FRONTEND_HANDOFF.md)共同消费。当前材料已提供，前端实际接收/视觉验收由其会话记录。

2026-10-31，session 01a18fcd-0464-7cf1-b435-4f394bd33e66。TA-D0.3/TA-B0.2已批范围内，TA000–TA006本机实现、真实公共接入、测试与文档闭环。未将参数错配扩展为规则，没有打包、部署或现场结论。

## 入口与版本

- 源码：src/tokenscope/token_content；单元测试tests/unit/token_content；真实集成tests/integration/token_content。
- 公共analysis-common-1.0，插件token-content-1，T1–T4@1，parser=json-exact-1，measurement=content-measures-1，policy=token-policy-1，七类handler@1，授权构造器token-authorization-1。
- 函数、参数与HTTP消费见[IMPLEMENTED_API](IMPLEMENTED_API.md)，冻结核心Schema由公共目录维护；最终工作树摘要见[batches/TA006/CODE_IDENTITY.json](batches/TA006/CODE_IDENTITY.json)。未发布版本标签或交付包。

## 已完成与验证

T1工具定义、T2工具结果、T3同请求完整载荷重复、T4历史结果清单/保留策略。无策略不判超限，不猜Loop/调用次数，模板参与未知不折算Token。位置/单元/观察分层，T2/T4共享，同请求多位置和父子重叠不重复计量。

七类准确参数变换、内嵌JSON一次编译、原值/外层guard、任一失败原子阻断。T3先有精确观察，后有明确授权才生成候选；reference协议/真实值由业务提供，不访问外部工具验证。复杂Schema或不支持位置明确拒绝。外层数字词法变化明确阻断，内嵌数字词法保留。

公共真实路径：人工原因→顺序两方向→原scope Token→封存fragment/证据→显式评估；Token不套>1pp门槛，零/负及P下降C增加可见。同appid、源摘要、源只读、组合独立回放/冲突失败、>64KiB全文、分页逐请求修改/指标、GET不计算、取消/重试均有实测。

最终本线103 unit+9 integration=112 passed/40.03s，ruff/mypy通过。三模型每模型七handler的批量与详细IDs/P一致；GLM真实HTTP覆盖授权和组合。公共跨方向组合/冲突由实际测试test_diagnostic_combinations联合执行通过。详细批次RESULT保留每次执行与初次失败修复，不把规划用例当现场通过。

## 可复现业务样例

| 场景 | 实际样例入口 | 展示依据 |
| --- | --- | --- |
| 无策略内容事实、T2/T4同证据 | test_rules / test_task_service | measures、participation、capture_truncation；无伪Token贡献 |
| 三位置同载荷与显式授权 | test_authorization_http | 原fragment的T3观察、unit/location身份、授权记录、Plan、真实评估 |
| P减少但C增加 | test_authorization_http reference案例 | before/after P/H/C及computed delta；不称必然优化 |
| 零/负效果 | test_task_service、test_token_http | available/direct_full结果保留；display_eligible=false不隐藏Token |
| 参数不足/版本/外部成员拒绝 | test_authorizations、test_task_service | blocked或422，不生成after |
| 组合成功/冲突 | test_authorization_http、公共test_diagnostic_combinations | 同scope独立回放；冲突无after，单项结果不变 |
| 取消/重试/源变化 | test_recovery | interrupted/failed与新attempt；旧报告不覆盖 |

样例由测试生成在临时隔离运行中，不复用真实业务正文；复跑会生成新task/evaluation ID。前端可消费/requests全文、fragment_index、authorization与evaluations/rows；前端视觉/交互仍须对应会话验收。

## 资源与边界

[RESOURCE_PROFILE](RESOURCE_PROFILE.md)含九档独立进程测量及明确配置；预算不同于业务阈值，调用方必须显式提交，不能超限后偷偷缩窗口。只有本机有限合成规模，不承诺华为现场吞吐、真实费用、O节省或任务质量。

共享公共源码由主线维护，本线没有修改API/worker/存储/编码/缓存算法。后续允许联合审查和缺陷修复；Git统一集成由主线协调，未擅自暂存其他会话改动。任何打包部署继续遵守用户“暂不”限制。
