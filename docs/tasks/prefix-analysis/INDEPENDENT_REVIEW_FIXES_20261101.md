# PCR-01 / PCR-02 维护方修复交接

2026-11-01。维护方01a18be2-7112-7aa2-919b-5137d1f1b1ad；修复候选arpc-local-4，基于arpc-local-3。仅维护方结果，独立结论由审查会话01a1800e-80b4-7400-a78b-a84f5b6e888d提供。

## 修改

- PCR-01：recommendation_evidence.counterpart_pointer按dynamic recipe.slot_key分别解析当前与另一原请求的实际pointer；当前目标须与Plan一致，两侧hash与Finding相符；不再要求Finding记录的右侧pointer等于当前侧操作pointer。不能可靠映射时comparison=null并在before.reason_codes给COMPARISON_TARGET_UNRESOLVED，不展示另一个工具。修改副本和收益算法不变。
- PCR-02：publication将发现完整性传给project_low_hit，默认保守false；members_complete与完整Plan评估/N/M独立，partial成员附CANDIDATE_COVERAGE_PARTIAL。Recommendation运行时校验对低命中允许partial支持集合+完整独立Plan，但prepared/scope/modified引用等约束保持；Token仍强制完整proposal成员后才available。公开JSON Schema结构未变，运行时语义修正必须按本次新身份核查。
- 回归新增工具顺序交换/不交换、双侧同工具a/原hash/码点、after与before同请求；缺工具或目标错配不能返回错误pointer。新增candidate_limit=1的partial与16的ready对照，分别验证members完整性和完整6请求收益。

## 维护方验证（非独立签收）

首轮PCR-01相关旧回归26 passed/50.66s。维护方复跑审查edge文件时PCR-01通过、同步新增的PCR-02失败，日志保留；没有改审查用例。首次PCR-02参数化运行3 failed/2 passed，揭示原Recommendation.available硬绑members_complete=true；修正该运行时校验后最终38 passed/55.28s。包括模型/Schema冻结、定位、两项新集成、实际前端报告及Token自动链公共编排。4源码mypy、7文件ruff通过。

最终命令：
```bash
.venv/bin/pytest tests/unit/analysis_common/test_recommendations.py tests/unit/analysis_common/test_recommendation_freeze.py tests/unit/analysis_common/test_evidence_locator.py tests/integration/analysis/test_recommendation_tool_identity.py tests/integration/analysis/test_recommendation_member_coverage.py tests/integration/analysis/test_recommendation_frontend_reports.py tests/integration/analysis/test_recommendation_engine.py --basetemp=artifacts/validation/pcr01-02-maintainer-20261101-02 -q
```

最终日志artifacts/validation/pcr01-02-maintainer-20261101-final.log；失败/中间日志pcr01-maintainer-20261101.log、pcr01-repro-maintainer-20261101.log、pcr01-02-maintainer-20261101.log均保留。生成样例在新basetemp；原ARL5/ART4/RV1封存数据不回填。

[新文件与完整源码/测试身份](INDEPENDENT_REVIEW_FIX_IDENTITY_20261101.json)供审查方独立复验。没有打包、部署、正式前端变更或Git发布。本候选尚待独立结论，不能仅凭38通过关闭问题。
