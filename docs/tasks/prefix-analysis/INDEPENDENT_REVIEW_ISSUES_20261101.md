# 低命中/公共层独立复审问题清单 · 2026-11-01

审查session：01a1800e-80b4-7400-a78b-a84f5b6e888d。候选prefix-common-review-20261101-1 / arpc-local-3。以下保留原候选独立失败证据；维护方arpc-local-4修复后，审查方已独立复验，PCR-01/PCR-02均关闭，最终结论见[复审报告](INDEPENDENT_REVIEW_RESULT_20261101.md)。审查方未修改业务代码。

## PCR-01（P1）：L3工具顺序改变后，comparison引用了另一个工具

归口：公共/低命中维护方。源码：src/tokenscope/analysis_common/recommendation_evidence.py，edit_examples的finding.source_pointer过滤及counterpart构造。检测阶段已按逻辑工具名记录两侧不同pointer，但展示阶段直接把当前操作pointer复制到另一请求。

复现：6条GLM-5.2构造请求，工具a的description为动态/tmp/job-i加稳定长文本，工具b的description为other；奇数请求交换a/b顺序。collect_dynamics识别L3，compile_dynamic_plan按a正确定位并真实回放，收益gate通过。随后project_low_hit + edit_examples生成原A/原B/after。请求1的before为工具a，但comparison指向请求0的/tools/1/function/description，即工具b的other。请求0的对照还因source_pointer相等过滤被漏掉。

独立失败用例：[test_independent_edges.py](../../../artifacts/reviews/prefix-common-independent-20261101/test_independent_edges.py)。日志：[edge.log](../../../artifacts/reviews/prefix-common-independent-20261101/edge.log)，1 failed / 5.91s。生成例子保留在pytest-edge目录。执行：WSL根目录，PYTHONPATH=tests:tests/integration/analysis .venv/bin/pytest -p conftest artifacts/reviews/prefix-common-independent-20261101/test_independent_edges.py --basetemp=<全新不存在的项目内目录> -q。

修复要求：按recipe.slot_key/逻辑工具名分别解析两请求的实际pointer，不能用同一个数字下标；无法可靠映射应明确降级，不能伪造原B。保持原始请求、实际删除Plan及收益口径，不改冻结Schema凑通过。

复测标准：交换和不交换顺序、双侧样例均指同一工具a且raw摘要及码点准确；comparison为原B，after为A修改副本；无法定位/工具缺失时显式处理；原有真实收益及L1/L2/L3回归保持。

## PCR-02（P2）：低命中候选扫描不完整时，推荐仍宣称members_complete=true

归口：公共/低命中维护方。源码prefix_analysis/recommendation_projection.py的project_low_hit固定members_complete=True；recommendation_publication.publish_low_hit接到complete=False后只传给difference_groups，没有传给推荐投影。

独立复现：同一6请求appid，candidate_limit=1触发候选截断；正常submit/process_next封存为partial，low_hit阶段candidate_coverage_partial=true。已识别L1的完整Plan仍可对6请求回放，该评估和N/M应保留，但推荐支持成员集合不完整却返回members_complete=true，混淆检测覆盖与已知Plan评估覆盖。AR-C1第3节要求扫描不完整时members_complete=false。

用例test_independent_edges.py::test_review_partial_findings_members_not_claimed_complete；日志partial.log：1 failed, 1 deselected / 7.75s。完整封存报告与推荐保存在pytest-partial下partial.json。修复要求：将发现/成员覆盖传入投影，缺省不能把partial支持集合当完整；保留独立完整评估的N/M/收益，不扩大为全任务失败或丢已有成果。复测须同时覆盖candidate截断partial和完整ready，验证成员完整性与评估完整性分别表达、默认引用不被partial覆盖。此复现使用原projection源码；PCR-01维护窗口期间，仅evidence源码可能改变，与本问题断言无关。


关闭记录：最终146项公共/低命中、4项审查方独立边界、6项Token专项、215个RV1 GET验证通过；新增两侧映射/完整性断言保留。原失败日志不改写，当前问题状态均closed，适用arpc-local-4固定候选。
