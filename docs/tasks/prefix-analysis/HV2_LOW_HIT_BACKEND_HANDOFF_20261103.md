# HV2-R2-LOWHIT 实际交接

2026-11-03；候选 **hv2-lowhit-local-1**。本线实施/测试/profile完成，**待总设计师第二关独立验收**，不代签前端或现场。实际session `01a18be2-7112-7aa2-919b-5137d1f1b1ad`；职责为低命中私有后端。本轮公共窗口关闭，未修改analysis_common、HTTP、监控、Token、前端、CLI/锁或共享总记忆，不commit/push、监听服务、构建、打包或部署。

[公共第一关](../delivery/HV2_COMMON_FREEZE_20261103.json)组合`9ac3e7fd5c5fea9556f957871bb03a0791e79e9404b207462a1cf8e184d7cb8e`，启动逐项匹配；结束仅两份获准prefix调用适配源码变化，原冻结证据未回写。用户后端2.1.0已冻结；本轮实测使用真实user_v2来源绑定，user_run_id/appid/expected_index_revision、window=null，base_run_id不同时提交。

## 实际修改与复现

| 编号 | 证据与问题 | 修复与范围 |
| --- | --- | --- |
| LHR2-01 | collect_l2及collect_dynamics先出现候选截断、再触发比较硬上限时，except用单一reason覆盖CANDIDATE_LOOKUP_TRUNCATED。真实8请求/K1/B3、两通道各复现，repro.log为2 failed/12.20s | 两文件各一行改为按原顺序去重追加停止原因；计数、候选/证据/recipe、停止时点不变。现同时保留CANDIDATE_LOOKUP_TRUNCATED与COMPARISON_COUNT_BUDGET_EXHAUSTED |
| LHR2-02 | 长工具Schema的相同description仍反复regex。N16/K4实测dynamic_recipes调用5346次，slots_in_text10692次，累计0.13364s/0.11802s（后者包含在前者，不相加） | dynamic.py对left==right直接返回[]，等价于原算法最终不会产生任何变化recipe；无缓存、无语义匹配，不改变候选集合/顺序、计费或身份。新单测32×32=1024对字符串与原实现精确对照，覆盖中文、路径、时间、billing header与变化输入 |

源码总修改仅3文件：prefix_analysis/service.py、detection.py、dynamic.py。公共冻结中包含的前两文件以本候选新SHA交第二次验收；不回写第一关manifest。新测得主要额外成本还有公共来源重复读取/身份校验，未擅自增加缓存或改变source验证；如需进一步优化，由总设计师另开公共窗口审查。

## L1–L5与预算核查

新测试`tests/integration/prefix_analysis/test_hv2_coverage.py`使用真实小CSV、GLM固定编码、用户监控user_v2索引、v2 Runtime和TaskControl，不是只调布尔假对象。

- 混合8请求、K16、F5下五条规则各保留1；L4发现数高于L1但不占用L1/L2/L3/L5配额。两通道完整遍历8，候选比较完整，retention_complete=false；完整与保留状态不混淆。
- 字节保留R5：两通道完成扫描，0条finding保留，省略/检测计数保留，不伪造无发现。比较字节预算1：首对未完成比较，报告0完成比较/1已遍历请求，明确COMPARISON_BYTES_EXHAUSTED；检查点取消抛ANALYSIS_INTERRUPTED。
- K1+B3共同停止：两个已发生原因均可见；checked不足8保持partial，不全局提额。
- 工具集合变化只出L3观察、不当成L2排序或自动删除；稳定纯messages对照不出Finding。L4保持needs_association且无recipe，L5保持表示差异且无recipe，不包装为动态字段根因。
- 实际公共low_hit-only任务以失败哨兵禁用Token plugin/adapter，零fragment。保留不足仍完整扫描，编码E1时明确ENCODING_BUDGET_EXHAUSTED；另用E512/实验1单独核查EXPERIMENT_BUDGET_EXHAUSTED。source请求/字节上限1均预检failed，错误码明确。
- 精确>1pp、完整性门槛、pilot通过但full低于门槛、组合与资源兼容由补充15项现有回归再次验证。L4/L5不套收益门槛；旧证据、recipe与模型设置保持。

规则适用对数仍未由私有探测器单独计量，公共applicable_pairs=null及明确说明保持；不把比较数当适用数。F配额只防止跨规则饥饿，同规则内按发现顺序保留，不能声称所有业务子型完整覆盖。

## Profile设计与实测

证据根`artifacts/reviews/hv2-lowhit-20261103/`；[结果表](../../../artifacts/reviews/hv2-lowhit-20261103/PROFILE_RESULTS.md)、[机器汇总](../../../artifacts/reviews/hv2-lowhit-20261103/profile-summary.json)。[执行脚本](hv2_profile.py)、[汇总/证据对照脚本](hv2_profile_summary.py)均在本任务文档目录维护。

六结构：稳定messages；96字段长工具Schema；固定完整工具集合交替排列；工具集合变化；合法tool调用及JSON缩进/独立历史问题；动态时间/工具路径/排列/结果表示混合。N8/16×K1/4，每配置前后各一次共48检测例；schema/mixed的N16/K4各额外前后两次共8重复；order/mixed各前后一次完整任务共4。**共60成功profile进程**，另有单独smoke，不并入对照。每例独立进程/独立state，固定seed=20261103与GLM-5.2，原请求/CSV、预算、输入SHA、.prof、functions表与result.json均保留。

模型revision为cf457fa734ab149ffef225f80893eb38c6ff5cdc，3资产实际SHA匹配锁；Python/包版本与源码冻结核对见environment.json。cProfile启用，系统可能有其它会话任务，非隔离性能实验；RSS是含模型初始化的整个独立进程峰值，不是分析增量。本轮没有Qwen或现场容量测试，更不代表V100/容器SLA。

| 实测项 | 结果与边界 |
| --- | --- |
| N16/K4比较 | 同fingerprint单通道54次；有tools的schema/order等两通道各54。混合工具版本减少L2匹配数量；以实际counter为准 |
| schema N16/K4读取 | 两阶段raw重复读取3,281,880字节，encoding_calls=0；仍有读取、解析、匹配、SHA/序列化成本 |
| schema三次wall中位 | 0.50749→0.30175s；before范围0.43835–0.52170，after0.29220–0.39580；CPU中位0.49749→0.29326s |
| schema正则局部 | dynamic_recipes调用仍5346（候选不变），after累计0.000531s，无slots_in_text调用；避免无变化文本正则，而非跳过请求/规则 |
| mixed三次wall中位 | 0.30747→0.29395s，区间交叠；不声称显著/稳定整体提速；CPU中位0.29718→0.28364s |
| RSS | schema进程峰值中位before500328/after492804KiB；仅小样本、含初始化与环境波动，不据此声称内存优化或现场上界 |
| order完整8请求 | after wall4.45659s、CPU4.35972s，encoding18；pilot2.09225s、full2.08940s，full_qualified；整体partial仍如实保留证据截断 |
| mixed完整8请求 | after wall5.32344s、CPU5.21915s，encoding10；两次pilot2.36497/2.40774s均below_gate，未运行full；另两实验not_run。没有伪造full耗时0或完整收益 |

24检测配置前后原CSV SHA相同；完整Finding证据（仅去各独立run固有scope/finding/base_run身份）、原请求SHA/位置/recipe/LCP/规则/原因/扫描比较数逐项相同，telemetry读取与检测计数也完全相同。不能用这些合成等价例替代真实业务删除质量。

读取/解码/身份、候选lookup、pair_dynamics、JSON序列化和token读取成本均可从每例analysis.prof/profile_functions核查；full的evaluation_phase_costs用仅profile脚本内计时wrapper实测pilot/full，产品公共代码未改。阶段是嵌套累计，不相加；source.verify可能涉及全索引文件，raw读取字节不包含所有校验I/O。没有用encoding_calls=0或terminal间隔当成本结论。

## 实际测试、失败与修复记录

- repro.log：2 failed（真实LHR2-01），原失败保留。
- fixed.log：23 passed/1 failed；失败来自新增测试同时要求编码预算与实验预算作为同一not_run原因。现公共优先保留首个编码停止；测试拆成E1与E512两档，保留两类断言，未修改公共优先级或删除业务检查。
- final-tests.log：**47 passed/113.93s**，覆盖全部prefix单测/新增真实v2集成、动态/排序回放、公共v2、工具对照与成员覆盖。
- gate-resources-corrected.log：**15 passed/91.26s**，独立增跑实验、组合、资源、精确gate契约。首个命令误写不存在test_evaluation.py，gate-resources.log记no tests ran，未算通过；修正为test_contracts后实际执行。
- mypy.log：11份prefix源码通过；ruff-final.log：全部本线源码/测试与两个profile脚本通过。
- 首个smoke脚本将CSV列名误写model_handle_time，smoke.log保留KeyError；按实际REQUIRED_COLUMNS改completion_tokens，smoke2退出0。只是合成脚本缺陷，未改业务CSV协议。
- 公共冻结结尾核对仅允许prefix/service、detection两项变化；公共API/Schema/旧wire/锁保持。Token本轮并行私有工作不由本报告代签。

实际复验命令（basetemp必须全新，保留旧目录）：

```bash
.venv/bin/pytest tests/unit/prefix_analysis tests/integration/prefix_analysis tests/integration/analysis/test_dynamic_replay.py tests/integration/analysis/test_l2_replay.py tests/integration/analysis/test_execution_v2_integration.py tests/integration/analysis/test_recommendation_tool_identity.py tests/integration/analysis/test_recommendation_member_coverage.py --basetemp=artifacts/reviews/hv2-lowhit-independent-NEW -q
.venv/bin/pytest tests/integration/analysis/test_experiments.py tests/integration/analysis/test_diagnostic_combinations.py tests/integration/analysis/test_diagnostic_resources.py tests/unit/analysis_common/test_contracts.py --basetemp=artifacts/reviews/hv2-lowhit-gates-NEW -q
.venv/bin/mypy src/tokenscope/prefix_analysis
.venv/bin/ruff check src/tokenscope/prefix_analysis tests/unit/prefix_analysis tests/integration/prefix_analysis docs/tasks/prefix-analysis/hv2_profile.py docs/tasks/prefix-analysis/hv2_profile_summary.py
.venv/bin/python docs/tasks/prefix-analysis/hv2_profile.py --output artifacts/reviews/hv2-lowhit-profile-NEW --case schema --n 16 --k 4 --mode detect
```

所有profile实际参数/命令/退出码见profile-runs.json、before-repeat-runs.json、after-profile-runs.json。汇总脚本需要已有本轮原证据，只新生成汇总，不回填原run。首轮harness快照保存在profile-harness-before.py，后续版本添加pilot/full计时，不改变检测路径；对照差异与限制已说明。

## 华为交接与待核查边界

[可直接输入华为agent的预算/抽样prompt](HV2_LOW_HIT_BUDGET_PROMPT_20261103.md)提供来源绑定、≤16条研究样本、两通道C(N,K)与B上限、各规则F/R配额、source/request/比较字节、编码E/实验/Plan预算及停止条件。研究档位不是生产默认：正式appid仍完整scope，sample-only来源独立标记，不能冒充全量收益；两大Qwen始终low_hit-only。

需真实业务最小证据：同appid/模型原始完整两JSON及raw hash/顺序、对应tools身份/版本、messages角色/tool_call关联、所疑动态字段完整位置、合法必要内容反例、业务输出字段/历史保留语义。缺这些只记录结构/差异，不从品牌/长Schema/重复统计生成人工未认可的新删除recipe，不判loop或同会话改写。

当前无公共契约必改缺口，第一关接口可直接消费新增并存reason_codes；未新增字段。进一步减少公共重复读取/验证若需要缓存，会触及scope身份/源变化检测和内存界限，必须另行审查，不借本阶段修改。真实大规模、Qwen成本、生产业务收益、前端展示与华为现场仍未验收。

交付的源码/测试/脚本/文档和证据SHA见同目录HV2_LOW_HIT_IDENTITY_20261103.json。只更新本线ENTRY与memory/tasks/prefix-analysis.md。完成后等待总设计师独立验收，未获通知不推进前端或其它窗口。
