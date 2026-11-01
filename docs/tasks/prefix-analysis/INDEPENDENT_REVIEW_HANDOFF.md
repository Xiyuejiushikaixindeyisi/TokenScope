# 低命中率后端与公共层独立复审交接

2026-11-01。实现基线 **arpc-local-3**；完整工作树复审候选 **prefix-common-review-20261101-1**。提供方session `01a18be2-7112-7aa2-919b-5137d1f1b1ad`。这是复审输入，不是独立复审结论、用户验收或发布授权。本轮仅整理文档与核对摘要，未重新运行业务测试、启动服务或分析任务。

[完整启动prompt](../../../prompts/sessions/PREFIX_ANALYSIS_BACKEND_INDEPENDENT_REVIEW.md) · [候选身份](INDEPENDENT_REVIEW_IDENTITY_20261101.json) · [Token独立复审入口](../length-analysis/INDEPENDENT_REVIEW_HANDOFF.md)

## 1. 候选身份与分工

arpc-local-3是AR-L3整体实现、AR-L4局部证据修复、AR-L5具体建议文案修复的叠加，不能仅查AR-L5的5个文件。三份身份的files按版本覆盖后共69个文件，本轮全部匹配当前工作树；新候选另收齐公共/低命中源码、测试、API装配、Schema脚本和相关契约/证据摘要，不覆盖旧身份。

当前观察分支main，HEAD=`5d824b506d9e055bcf397c3846dafc450fcf02e5`。公共/低命中源码与测试目录、新推荐API仍有untracked；app.py为修改状态，**HEAD不是候选版本**。按候选各map逐文件核查；git diff为空不能证明文件无改动，不能遗漏未跟踪文件。工作区有其它会话内容，不整区清理/暂存。

| 归口 | 本轮复审范围/边界 |
| --- | --- |
| 公共/低命中 | analysis_common、prefix_analysis；诊断API、共享app/CLI的诊断装配；公共及低命中测试、Schema导出脚本。本线是唯一维护方 |
| Token | token_content、其单元/集成测试及策略DSL/handler归Token会话01a18fcd-0464-7cf1-b435-4f394bd33e66；本线审查消费/组合边界，不接管其私有源码 |
| 监控 | 编码/资产/理想缓存算法只复用；仅为共享装配及复用正确性检查依赖，不重设计监控功能 |
| 前端 | apps/viewer只读消费和UI-04归前端；浏览器反馈是证据，不由后端代签产品视觉 |

对齐Token候选token-review-20261101-1：本轮核对其17私有源码、19测试、33公共依赖、14契约、5交接输入均匹配；仅身份核对，不代替独立复测。公共与Token对相同依赖出现漂移时先记录差异和归口，不能拿任一方旧测试证明新代码通过。

## 2. 已批准方案及版本优先级

阅读顺序：[设计纠偏0.2](DESIGN_REVISION_20261031.md) → [LH000–009计划](BATCH_PLAN.md) → [AR-C1公共推荐设计](../analysis/RECOMMENDATION_CONTRACT_ALIGNMENT_AR1.md)及[ARPC000–006计划](../analysis/RECOMMENDATION_IMPLEMENTATION_PLAN_AR1.md) → AR-L3/4/5实际交接。早期设计文中的“未编码”“T1–T4”、UI-03、“自动收益留V3”不覆盖当前T2–T4/UI-04方案；以实际源码/冻结Schema/对应版本测试说明能力。

- 人工先查看用户监控/MA监控，再指定源run、appid、异常原因及显式开关。含low_hit依次做低命中和原文Token；仅长度/QPS做Token。32k/70%为调查理由，不是自动告警/自动定罪阈值；不在页面访问时触发分析。
- 只回放该appid的冻结源范围/窗口，同编码身份；不全历史、不混入其他appid、不跨run预热。MA结果只是调查背景，不把MA采集/重算塞入诊断。
- L1动态元数据、L2同完整工具集合顺序、L3工具定义动态内容/漂移；有证据的动态片段可先删除副本并量化，不以尚未证明业务无损阻止候选。业务决定实际采用，不改线上原文或模型配置；cch等已有识别范围不泛化为所有业务字段。
- 自动链完整pilot的绝对收益严格>1个百分点才进入full；完整full严格>1pp才显示低命中优化卡，使用精确未舍入分数。旧显式direct_full接口单列，不伪称经过pilot。完整零/负收益不包装成可优化卡。
- L4/L5独立差异区，不套收益门槛；底层完整两请求JSON保留，UI-04消费局部证据，最多3例不改变全体成员数。L4无可靠关联时不认定同会话历史被改写；L5保持原始JSON表示。
- Token新任务仅T2–T4，工具说明精简不在范围；历史T1读取兼容。公共只维护外壳、快照、归组、guard后的评估与发布，私有选择器/生成DSL由Token校验。初版无依据hypothesis不自动启用。
- 推荐按具体recipe及依据归组；N来自完整回放raw实际改变请求数，M是原scope请求数，不按Finding/样例/Token减少数替代。不同依据相同执行各自prepare后才复用，保留独立prepared/execution/evaluation引用，不跨卡累加收益。
- Token ΔP/ΔC=after-before，前值0比例null；零/负收益及P降C升如实显示。缺依据不伪造after/N/收益。完整advice可ready，技术/预算不完整partial。
- partial仅历史，empty不替换默认；两方向作为整体，只有ready更新其包含方向默认引用。未封存不可读取，旧报告not_computed不回填。Schema与实例/task/scope隔离贯穿存储和GET。

## 3. 实现导航

| 链路 | 主要源码/测试 |
| --- | --- |
| 真实来源与计量 | analysis_common/source.py、encoding.py、evaluation.py、modifications.py；test_source/evaluation/dynamic_replay/l2_replay |
| L1/L3 | prefix_analysis/dynamic.py、detection.py；日期/路径/已知billing头识别、逻辑槽位映射、准确删除片段，不宣称覆盖随机ID全部模式 |
| L2 | prefix_analysis/structure.py、service.py；完整工具集合指纹、唯一function身份、固定排序、保留定义 |
| L4/L5与两阶段 | history.py、candidates.py、experiments.py；有界前序候选、关联不足降级、pilot/full分开覆盖 |
| 推荐与依据 | recommendations.py、proposal_plugins.py、recommendation_grouping.py、recommendation_engine.py；Token实际adapter，配置提交冻结，不执行动态代码 |
| 发布与预算 | runtime/service/storage/discovery、recommendation_runtime/pipeline/publication/execution/store；取消/重试/幂等、outbox、分阶段coverage/停止位置 |
| 局部证据与文案 | evidence_locator.py、recommendation_evidence.py；prefix_analysis/recommendation_groups.py、recommendation_projection.py。AR-L4差异范围/原A-B/缺依据before；AR-L5按实际Plan动作和pointer生成文案 |
| 业务GET | api/diagnostics.py、diagnostic_discovery.py、diagnostic_recommendations.py；recommendation_views.py、bootstrap.py、app.py/cli.py。public-views与内部Recipe区分 |

[机器契约](../../contracts/analysis-recommendations-1/README.md)与[Token adapter协议](../length-analysis/AUTO_ADAPTER_HANDOFF.md)是当前接口入口。原analysis-common-1.0/diagnostics-http-1/diagnostics-discovery-1三个manifest的13文件保持冻结。私有selector/generator及basis scope JSON不直接公开，仅摘要；跨字段/引用限制仍需Pydantic及运行时验证，不能只做JSON Schema结构检查。

## 4. 已有测试证据与前端签收

| 版本/证据 | 已执行事实 | 不能据此声称 |
| --- | --- | --- |
| LH000–009及自审 | [LH验收索引](TESTS.md)、[完整自审](SELF_REVIEW_20261031.md)、[FE-N1结果](batches/FE-N1/RESULT.md) | 历史累计数不是当前单次全套结果 |
| arpc-local-1 | [ARPC006](../analysis/batches/ARPC006/RESULT.md)：293项/292.14s；预算补验2项/7.74s，其中1新增，去重294。监控254/121.42s+MA46/58.97s=300；42模块mypy、ruff、旧13冻结文件核对 | 不能与Token的163/ART4额外测试相加，公共集含Token用例 |
| arpc-local-2 | [AR-L4](FRONTEND_READABILITY_HANDOFF_ARL4.md)：31项/64.90s，L4加强同一用例再跑1项/8.63s；4个修改源码mypy/ruff | 不是在当前文案版本又运行31项；原样例不覆盖新任务 |
| arpc-local-3 | [AR-L5](FRONTEND_COPY_HANDOFF_ARL5.md)：10项/17.25s；修改源码mypy、相关ruff；真实L1/L4/L5报告，L2/L3文案Plan单测 | 没有在local-3再次执行294+300；L2/L3新增文案无新生产收益实验 |
| 前端签收 | [AR-L3接收](FRONTEND_ARL3_ACCEPTANCE_RECEIPT.md)、[AR-L5接收](FRONTEND_ARL5_ACCEPTANCE_RECEIPT.md)；AR-L4浏览器反馈见AR-L5交接。前端核对5/5文件、6/6Schema、1/1测试日志，并读取AR-L5 state完成具体建议、A/B、L4/L5≤3例和窄屏验证 | 用户功能/视觉批准与独立复审尚未通过；后端没有重新运行这些浏览器场景 |

当前前端工程状态见[UI-04验收](../viewer/analysis/ACCEPTANCE_UI04.md)，其ARF000–004完成不等于独立复审通过。旧PROMPT_INDEPENDENT_REVIEW中的UI-03/AF006范围不适用。

测试使用构造请求、策略和引用地址，真实执行固定Tokenizer/Chat Template、原appid回放、同服务worker及GET。没有生产业务授权、输出质量、TTFT/SLA/费用收益或Agent重执行结论。authority.verified是受控配置声明，不是自动完成业务审批。默认空bundle有明确0策略/原因，不能把构造bundle设为生产默认。

## 5. 必须独立核查的边界

以下是审查清单，**不是本轮重新测试通过的结论**。

| 核查项 | 重点失败边界/判据 |
| --- | --- |
| 来源与排序 | appid/run/窗口精确隔离；源损坏、截断、空范围、编码/profile漂移；只读监控结果，缓存回放顺序一致，不悄悄过滤目标 |
| L1/L3准确性 | 相同槽位/模板与实际动态范围对应；工具路径随排列变化时比较请求两侧pointer是否仍正确；无法可靠对应不能伪造A/B。路径/时间删除只限定位片段，不删除业务其余文本 |
| L2条件 | 集合内容变化不能降格为排序；重复/缺失/不支持工具身份明确处理；保留全部定义，排序的确定性与实际Plan一致 |
| L4/L5 | 无session/turn不推断过程；完整原JSON与局部证据可追溯，大整数/转义/重复key/表示差异不丢；差异发现与完整覆盖区别 |
| 精确收益 | 恰好1pp不通过，两阶段分母和窗口正确；direct_full例外标明；N/M非样例数，零和null不同；负收益/P降C升如实保留 |
| 配置和复用 | 配置bytes/版本/未知字段、basis与scope/工具身份一致；提交/幂等/retry快照；每项guard先执行，失败项不能借相同hash成功；规范化操作字节比较而非只比hash |
| 资源与中断 | proposal/组/操作/单Plan/总Plan/编码/回放/例子边界；消费失败与已完成计数；不缩scope凑完整，取消/源变化/失败无假after；缺依据证据失败应partial，不丢已完成结果 |
| 证据可读性 | 精确码点与raw/decoded映射；AR-L4最长公共前后缀差异区间、多个分离变化的截断、零宽删除锚点；重复key歧义不假定位；comparison是原B、after是副本。≤3例不掩盖成员总数；support缺location如何降级 |
| 文案 | AR-L5根据实际独立Plan的handler/primitive/pointer；未知操作不猜删除、无Plan不声称已完成；条件不构成业务授权 |
| 状态与存储 | 顺序执行、取消/重启、封存fsync/rename/事务/outbox竞态；partial/empty/两方向不完整不覆盖默认；重试attempt与原task隔离；孤儿产物不误读 |
| 只读API | 实例/任务/版本/引用隔离，规范十进制字符串分页、末页null、不重漏；GET零分析/编码/提交；未封存/旧报告/不存在/存储异常状态码准确；隐藏内部策略JSON |
| 兼容与整合 | Token四方法/DSL边界，当前T2–T4与旧T1读取；前端同task数据一致。源契约旧manifest不改，新Schema与源码/GET一致；共享app/CLI不破坏监控 |

已知限制需明确评价，不通过措辞掩盖：默认256提案不是15万请求容量承诺；低命中旧检测/实验受RuntimeOptions约束，新推荐发布对既有低命中Plan的核算发生在其计算后，不是前置RSS限制。ARPC006整套峰值RSS1,667,784 KiB包含模型缓存，wall4:52.64且与监控运行部分重叠，不能外推单任务SLA。候选索引预算可能导致覆盖partial；大报告GET摘要校验有I/O成本；私有孤儿目录没有自动清理承诺。现有messages协议不等于原生Responses，Loop/过程分析未实现。生产场景和华为大规模校准仍待另行授权/数据。

## 6. 复测和证据保护

收到独立复审执行指令后，先核对本候选摘要与Token依赖，再选择测试。本轮只整理，不执行下面命令。WSL项目根目录，使用已有.venv、不安装升级依赖；不得复用原basetemp，因为pytest会清空它。

```bash
# 不存在才执行；存在则换新的后缀，不删除。
test ! -e artifacts/validation/prefix-common-independent-review-20261101-01 && .venv/bin/pytest tests/unit/analysis_common tests/unit/prefix_analysis tests/integration/analysis --basetemp=artifacts/validation/prefix-common-independent-review-20261101-01 -q
.venv/bin/mypy src/tokenscope/analysis_common src/tokenscope/prefix_analysis src/tokenscope/api/diagnostics.py src/tokenscope/api/diagnostic_discovery.py src/tokenscope/api/diagnostic_recommendations.py src/tokenscope/api/app.py
.venv/bin/ruff check src/tokenscope/analysis_common src/tokenscope/prefix_analysis src/tokenscope/api/diagnostics.py src/tokenscope/api/diagnostic_discovery.py src/tokenscope/api/diagnostic_recommendations.py tests/unit/analysis_common tests/unit/prefix_analysis tests/integration/analysis
```

Token私有/联合自动链复测按其INDEPENDENT_REVIEW_HANDOFF，使用另一个新basetemp；其既有测试包含三模型、缺依据、零/负/P降C升和中文具体方案。涉及共享装配/监控复用变更或发现风险时，追加tests/unit/monitoring、tests/integration/monitoring、tests/unit/ma至新目录；不以堆叠重复测试替代源码审查。保留实际命令、退出码、数量、耗时、工具/模型身份和日志；缺资产/环境故障与业务失败分开。已知Starlette/httpx弃用warning如实记录，不擅自升级。

只读展示可使用[AR-L5](FRONTEND_COPY_HANDOFF_ARL5.md)的`artifacts/validation/arl5-20261031-01/test_frontend_low_hit_and_diff0/{inputs,state}`，前端报告已在8011消费，4191/4193为页面入口；端口/进程是历史观察，先检查，不重启或终止别人的服务。Token中文状态见其[ART4](../length-analysis/FRONTEND_READABILITY_ART4.md)。不提交新分析即可读取旧报告；要验证改动后生成逻辑则在全新测试状态生成，不回填旧报告。

## 7. 复审输出与授权边界

复审者登记自己的实际session ID、角色、范围与依赖；未知ID写未知，不能复用提供方ID。输出候选/漂移、已核查矩阵、按严重度列问题（文件/行/复现/影响/归口）、实际测试日志、未测项和环境限制，并给明确通过/有条件通过/不通过及阻断项。

缺陷交公共、Token或前端归口修复，新身份重新验证；本次prompt默认审查和隔离本地测试，不擅自改业务源码/契约让测试通过。不得把提供方通过记录当独立结论，不把前端工程签收当用户批准。

本次只授权整理交接：不自动创建/唤醒/发送到复审会话。prompt供用户后续显式启动；不授权打包、临时测试镜像、Docker构建、前端发布包、代码交付包、部署、远端操作或Git提交/合并/push。审查角色名称不是发布许可；生产策略批准、用户视觉批准、独立复审和交付授权分别记录。
