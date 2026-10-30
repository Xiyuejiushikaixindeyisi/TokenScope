# V2 用户监控后端记忆

2026-10-30：会话 ID `01a18bc7-cdb5-7830-a185-ad3aa6257b21`，角色为用户监控后端功能设计与开发。首次登记仅理解职责；当前已完成设计v1.0及batch规划，详情见文末最新记录，未开始代码、部署或打包。

- V1问题：时间格式兼容、模型别名映射、DeepSeek缺省思考；现场thinking_disabled不证明生产缺省，不能静默设为false。原JSON套模板前的长度须先tokenization再统计。
- 给定P90 TTFT目标，先收敛模型、部署、流量、真实性能校准、适用范围与证据不足的表达；不能从总体命中率承诺通用达标百分比。
- 搜索排行覆盖请求长度众数区间、Token量、理想命中率和请求量；UI-01为认可起点，统计语义与用户进一步收敛。
- GB数据按appid×common_name独立统计，暂定空缓存起步；服务级理想潜力不代表生产实例真实命中。与MA监控并行，不负责MA、异常分析、前端及hybrid。
- 依赖V1验收事实、MaaS架构、统一编码与计量；公共模块改动先确定单一维护方。时间/时区、别名和生产思考模式等细节待确认，不能将现场workaround视为源码修复。入口见[用户功能](../../docs/tasks/monitoring/v2-user/ENTRY.md)、[产品记忆](monitoring.md)及[现场验收](../../docs/huawei/MONITORING_V1_ACCEPTANCE_20261030.md)。

## 2026-10-30 初版方案讨论与调研

- 用户提出修复时间、别名、DeepSeek思考及内网访问；现场报告已核对，统一内网地址目标此前已确认。时间兼容不代表UTC已确认，别名需明确映射，思考缺省待生产证据；不修改V1运行配置。
- TTFT提出按请求估算：未命中token分chunk计算，等待取经验参数或负载函数。应检验共享8192 token预算、缓存读取及P/D开销，整窗口请求分别估算后再求P90；当前P90位置不固定。经验P90等待不与计算分位数直接相加当成P90。
- 本地只读llm-slo-scheduler g5材料有running-first、FCFS和共享8192 token预算及异步batch predictor，但批预测不是逐请求等待时间，性能与现场适用性需验证。参考[vLLM chunked prefill](https://docs.vllm.ai/en/latest/configuration/optimization/)、[Dynamo Planner](https://docs.dynamo.nvidia.com/dynamo/v1.1.0/components/planner)及[Vidur](https://arxiv.org/abs/2405.05465)，不将参考能力当作当前生产实证。
- 排行候选：理想命中率、请求数量、重算Token总量、单请求重算Token众数区间起点；区间宽度、筛选条件、有效范围及长度口径待讨论。原JSON模板前token长度与模板后重算长度分开。
- 本轮为初步调研与产品讨论，未修改源码或部署；深度性能标定、具体修复和方案需继续收敛。

## 用户澄清：首版估算与排行

- CSV时间为UTC。DeepSeek生产缺省未知；用户要求以华为报告现场采用的thinking_disabled为准，应标识为现场假设，不声称生产缺省已核实。
- 首版不建等待队列模型、不逐条展示：用TTFT目标减去给定等待时间得到计算预算，由校准后的计算时间反推可计算token长度，再结合CSV模板后P90请求长度估算所需命中率。条件、适用范围和证据不足须展示；P90长度方法隐含命中及等待等假设，需与用户继续收敛。
- 重算Token明确为模板后输入Token减理想命中Token。用户希望展示众数区间内请求长度的平均值以降低长尾影响、反映常见长度；区间边界、宽度和双峰展示等语义待讨论，需区分原始模板后长度与重算长度。

## 设计审批

用户确认众数区间及其均值都基于每请求重算Token量，并要求设计供审批。已编写[用户监控后端设计v0.1](../../docs/tasks/monitoring/v2-user/DESIGN.md)，含兼容修复、内网访问、排行、TTFT估算、协作和验证建议；状态待用户审批，尚无代码修改或部署。此前关于UTC待确认和“整窗口逐请求估算”的建议已被用户最新澄清覆盖。


## 2026-10-30 两线交叉检查与最终设计

用户授权完成两份设计交叉check、完善本线最终设计及逐batch执行/验收方案、版本/上下文整理；明确本轮不开发、不部署、不打包。已形成[设计v1.0](../../docs/tasks/monitoring/v2-user/DESIGN.md)、[U000–U005计划](../../docs/tasks/monitoring/v2-user/BATCH_PLAN.md)、[交叉检查](../../docs/tasks/monitoring/v2-user/CROSSCHECK_MA_20261030.md)及[版本入口](../../docs/tasks/monitoring/v2-user/VERSIONS.md)，v0.1按字节归档。

交叉核对期间MA从v0.1更新至v1.0，已增量核实：MA现采用显式UTC输入约定，未宣称源导出已验证；统一资源使用已有state_root/worker.lock，用户回填也需接入，不能承诺跨state_root宿主全局控制。两线业务范围/实际与理想量/分箱/有效集合/存储保持隔离；MA设计未被本线修改或代签。

本版收敛：固定chunk情景及lt/le边界，人工假设参数可给明确标识的参考值，无τ不出数；实测校准与计算器完成分开。独立用户绑定/控制库/侧索引、精确稀疏C分箱与并列排序；旧S0/封存不变。每批必须PLAN、ISSUES、TESTS、RESULT及增量记忆，最终逐项设计符合性、E2E和健壮性验收；缺MA/前端/真实性能证据不得称整体交付完成。

当前所有批次planned，未生成代码/业务测试通过记录；下一步待用户审批最终工程选择并明确启动，再执行U000。真实校准仍缺；共享装配签名/维护窗口由U000固定。版本整理是文档版本和旧稿归档，本轮不提交或push其他session工作。

本轮文档检查完成：6份当前Markdown、35个本地链接通过；修正3处归档相对路径，v0.1归档摘要与MA最终稿摘要一致，Git diff --check通过，src/tests/deploy/env无差异。检查与文件摘要见docs/tasks/monitoring/v2-user/DOCUMENT_CHECK.json；未运行业务测试或性能测试。

## 用户批准开发；U000闭环
2026-10-30用户认可最终设计，明确授权从U000逐批开发、通过门槛再推进，暂不部署打包。U000已完成独立契约/基线：169项既有回归通过（155.33s），26正反例、15 schema、9操作及mypy/ruff通过。契约在docs/contracts/user-monitoring-v2，运行API未装配。U001开始；公共csv_reader/domain由本线修改，MA共享app/worker不编辑。真实校准/MA/前端联合保持pending。

## U001闭环
兼容修复已完成：UTC DD/MM含纳秒；明确现场别名；CAS事务内跨模型别名冲突检查；新安装DeepSeek thinking_disabled，旧default未决不改。U001遇到重复逗号、编码profile夹具失配及新测试1线程污染全进程预算，均记录修复，保留严格运行校验。最终205测试通过(158.98s)，真实编码19+1定点通过，mypy/ruff/diff通过。
U000/U001已closed，U002–U005尚未实施；下一步按已授权计划执行U002。源码改动仅domain/csv_reader/storage、新user契约及相应测试；API/worker/缓存算法/运行配置未改。内网参数仅交接，未开放端口、部署或打包。证据和源码资产摘要见U001 RESULT。当前代码尚未git提交，不混入其他会话改动。

## U002开始
用户再次明确授权从U002直接推进至U005，无需每批询问，暂不部署/打包。已新增user_monitoring/statistics.py与test_user_statistics.py：8测试通过，类型检查3文件通过。独立C众数/精确均值不改旧distribution。U002 active，绑定意图、持久索引/原子发布/恢复、资源门槛仍未完成，不能进入U003。问题/测试/结果见batches/U002四文档；后续授权持续有效。

## U002闭环与U003接入
U002：22测试通过，三模型真实facts/隔离/幂等恢复/封存损坏/empty/缺facts/锁及精确箱验证；100k事实10k组资源门槛通过（1.202s，RSS增量约8.75MiB，索引约21.8MiB）。生产投影以磁盘稀疏箱避免并列峰内存无界。进入U003，继续已授权U005目标，不需用户补充信息。

## U003闭环
排行/众数分页及独立HTTP装配完成；28测试通过，Fraction oracle/字面筛选/分页/精度/只读/身份验证。10k组20次查询最慢0.2163s≤2s；mypy49文件和ruff通过。app/CLI按MA预留Dispatcher.register接入用户worker，保留共用worker.lock。进入U004，不要求额外确认。

## U004闭环
TTFT参考计算器及不可变情景/估算接口完成，34测试（含排行回归）通过；1000独立Decimal边界算例约0.054s，精确le/lt及无预算/完全复用/范围外状态明确。并发幂等/旧快照/模型冲突/只读通过。真实校准仍pending。继续U005统一端到端、稳健性及设计符合性验收。

## U005完成：本地后端与真实MA联合验收
2026-10-30，用户要求不中断推进至U005，本次已完成。U002/U003/U004逐批门槛及四文档闭环后进入U005；全量289 passed（222.81s），最终恢复竞争修复15定点测试passed（24.42s）；静态及mypy50源文件通过。
真实本地HTTP/CLI三模型、多appid/duplicate/UTC两格式/工具及多行JSON/坏行→索引→排行→TTFT参考→重启读取通过；MA同UUID跨appid复用、跨UUID不复用、用户appid隔离通过。三队列有待处理任务时真实跨进程worker.lock阻止推进，解锁后完成；索引rename/发布前os._exit中断重建一致。无源文件恢复幂等、预留base不可被历史绑定抢占、缺控制库GET不创建、异常长参数无回显、索引损坏/权限/资产缺失/超长原文/精确数值均有证据。
资源固定预算通过：100k事实/10k组，最终约1.396s、RSS增量约8.63MiB、索引21.8MiB；20次查询最慢0.255s；1000公式边界算例≤2s。均合成数据，不外推现场。
当前身份u005-local-1、用户契约1.0.1（输入上限、计数正则/分页/错误勘误；字段及业务口径不变），user control1/index1；V1 control3/view1/S0 1.0.0及已发布身份保持。共享app/CLI窗口已释放，使用Dispatcher.register(user)。真实校准、前端联调、现场与内网开放仍pending；没有部署、打包、改V1运行配置或创建发布tag。
权威入口：docs/tasks/monitoring/v2-user/ENTRY.md、IMPLEMENTED_API.md、batches/U005/{RESULT,TESTS,ISSUES,DESIGN_CONFORMANCE,VALIDATION_SUMMARY,VALIDATION_MANIFEST.json}。所有批次闭环状态以各RESULT为准；早期active/未实施文字为历史时点。当前共享工作树含其他会话源码文档，未擅自提交它们；按源码SHA清单交接本地版本，非已发布commit。

## 本轮源码提交与前端交接
用户明确授权整理本线版本/前端入口、更新角色状态并提交push，不部署打包。新增FRONTEND_HANDOFF.md和GIT_HANDOFF_20261030.md；后端身份u005-local-1/契约1.0.1，转入前端接入支持与后端维护。共享工作区核实MA实现已closed但未提交，作为共享app/CLI必要依赖一起收录已闭环源码/契约/测试/证据；排除异常分析和前端未完成材料。共享记忆按后端内容单独暂存，工作区保留其他会话进度。提交前fetch确认origin/main=6042a05；待实际push成功再记录确认，不以准备状态冒称成功。
