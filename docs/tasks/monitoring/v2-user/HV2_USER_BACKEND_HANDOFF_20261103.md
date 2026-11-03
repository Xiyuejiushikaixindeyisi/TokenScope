# HV2-R1-USER 后端交接：候选实现待独立验收

2026-11-03。角色：V2用户监控后端；实际会话ID 01a18bc7-cdb5-7830-a185-ad3aa6257b21。派发基线7cbe28621f4e46083bf47f9aa14b011b3cb250c4，原交付源码b17cdc07b0a351d0f5c4fb1b26f0e05be2b3a0af。当前本线实现尚未提交；精确文件和SHA见[VALIDATION_MANIFEST.json](batches/HV2-R1-USER/VALIDATION_MANIFEST.json)。

本轮恢复曾误接旧U008并提交/push d55df94；已在历史Git交接及本线记忆追加勘误，不reset/revert，不把该提交说成HV2实现版本。之后未commit/push，未改CURRENT/SESSIONS/总执行板；SESSIONS勘误由总设计师处理。没有修改前端、MA、异常公共源码、共享app/CLI/锁或构建配置，没有监听服务、部署或打包。

## 状态、计划和证据入口

R1-U1目录、R1-U2默认配置、R1-U3自动计算、R1-U4本线验证/候选契约已完成实现和自测；待总设计师独立验收/冻结，不代签前端或现场通过。统一[PLAN](batches/HV2-R1-USER/PLAN.md)、[问题记录](batches/HV2-R1-USER/ISSUES.md)、[实际测试](batches/HV2-R1-USER/TESTS.md)、[闭环](batches/HV2-R1-USER/RESULT.md)。

接口候选 **2.1.0**：[完整契约说明](../../../contracts/user-monitoring-v2/2.1.0/README.md)、[运行OpenAPI](../../../contracts/user-monitoring-v2/2.1.0/runtime.openapi.json)、[Schema](../../../contracts/user-monitoring-v2/2.1.0/schema.json)、[合成样例](../../../contracts/user-monitoring-v2/2.1.0/examples.json)。旧2.0.0冻结文件保持。

## 修复前后

| 问题 | 原情况 | 候选实现及证据 |
| --- | --- | --- |
| 同appid所有模型发现 | 只有已知run读取，V2Records可记50个但不是服务端目录 | GET /monitoring/user-v2/runs读已发布索引，三模型共享appid/单模型对照/空state/分页/重启/固定历史/零写入已测 |
| 同模型历史默认 | 客户端本地记录，无法在干净浏览器发现 | 按服务端登记序最新已发布appid×model_id×common_name，返回is_default；显式选旧run不会切到新历史 |
| 日常TTFT配置 | 人工情景ID和revision为必填 | 独立版本默认及自动计算入口；W/T显式，其他身份来自所选目录项；保留旧情景操作 |
| 默认配置可追溯 | 无逐模型自动默认 | 用户提供三模型τ/K带source/revision/时间及calibrated=false；CAS与幂等/重启/旧快照保持 |
| 622条数差 | 报告归因为窗口/去重但缺证据 | 核实源码无用户时间裁剪/重复hash去重；8行fixture真实编码3有效5拒绝，公共分析同源3条；不伪造现场解释 |

## 前端接入步骤（独立验收冻结后执行）

1. 沿用实例身份握手，所有用户请求带X-TokenScope-Instance-Id。GET /runs；不依赖localStorage、不手填ID、不POST绑定发现。目录为空明确展示尚无已发布用户数据，accepted/failed不会混入。
2. 同筛选沿snapshot+next_offset拉完所有页；409 DISCOVERY_SNAPSHOT_CONFLICT清空当前分页重新读取，禁止拼接不同快照。筛选appid等均精确，模型不能跨服务汇总。
3. 按appid→common_name/model_id展示，默认取is_default，保留可选历史user_run_id/index_revision。空运行appid=null只用于空数据状态。历史默认按登记顺序，而非完成时间/mtime。
4. 用选中项source和appid关联排行/众数与TTFT。若选择刷新、身份变化或返回revision冲突，清除失效计算；不能自动用另一个模型/历史重试原请求。
5. GET /ttft/defaults用model_id+common_name展示当前配置及来源。日常表单只必填等待W和SLO T；K可选覆盖，移除覆盖恢复模型默认。默认≤，如提供严格选项显式lt。缺τ显示待配置，不拿其他模型或示例数字代替。
6. POST /ttft/evaluations，最小示例：

```json
{
  "submission_key": "new-key-kept-for-retries",
  "user_run_id": "<selected source.user_run_id>",
  "appid": "<selected entry.appid>",
  "index_revision": "<selected source.index_revision>",
  "target_seconds": "8",
  "waiting_seconds": "5"
}
```

模型/输入P90/K/τ自动解析，不提交scenario_id/O/model_id。响应外层含source/defaults/request及evaluation；数值/status/reason/limitations从evaluation展示，不前端重算。GET /ttft/evaluations/{id}回读。请求重试复用键，改变输入或希望采用新默认时用新键。自动结果不能发往旧/evaluations/{id}读取。

7. 参数维护是显式POST /ttft/defaults，非日常计算必填：完整配置+expected_revision CAS+幂等键，创建expected_revision="0"，更新读取当前revision。记录source_description；null τ表示明确未配置/停用。不是PATCH，省略K会恢复8192，不按旧配置补齐。
8. 显示“用户提供假设参考，尚未验证真实性能”。W涵盖GF发出之后首Token前全部非计算耗时，不重复O；K覆盖不缩放τ。无预算/无正P90不出百分比，100%附可行性未证实。不把P90长度参考比例当总ΣH/ΣP达标线。

## 用户参数、公式与存储

| common_name | 编码model_id | τ秒 | K |
| --- | --- | --- | --- |
| Qwen-V3.6-27B | Qwen3.6-27B | 1 | 8192 |
| GLM-V5.2 | GLM-5.2 | 2.7 | 8192 |
| DeepSeek-V4-Flash | DeepSeek-V4-Flash-0731 | 2.6 | 8192 |

来源：2026-11-03用户提供，经总设计师HV2-R1-USER派发；不是测量报告。启动时验证精确别名匹配后种入revision1，既有任何版本不覆盖，未知模型不套默认。chunk_tokens和tau_reference_chunk_tokens分别保留，覆盖K不改变τ；配置与自动结果有独立持久快照。

复用现calculate精确有理数：≤时n=floor((T−W)/τ)，严格<时ceil((T−W)/τ)−1；Cmax=min(P90,nK)，参考1−Cmax/P90。T<W/严格T=W无预算；≤且T=W可能是理想化100%参考；无正P90不可用。不建等待队列，不承诺生产P90。

新默认库user_monitoring/ttft_defaults.sqlite3，schema1，在router构造时初始化；业务GET模式只读。旧用户控制schema1/index不变。旧9操作请求/响应引用一致，旧2.0.0快照读取保持。备份整个state；旧二进制不支持新API，不宣称可无损降级。

## Trace来源和公共层映射

产品Trace模型使用用户绑定common_name，model_id为编码模型；不用MA的model_standard_name。目录source含base_run_id/user_run_id/index_revision、输入/manifest/settings SHA、encoder/asset及文件观察范围。它校验索引、manifest和summary，不重新扫描全CSV/Token制品。

公共SourceSelection：
`source_kind=user_v2, user_run_id, appid, expected_index_revision=index_revision, window=null`。
不要同时提交base_run_id（旧契约互斥），它只用于溯源核对。文件观察时间不是appid窗口，不能直接作为半开区间裁剪。公共层仍自行生成scope_id/request_keys_digest。实际SourceResolver合成fixture得到同3条、同manifest/model，未改公共代码。

## 现场过滤审计

两份原件SHA与派发一致，未改原件。调查3 ready/77项为报告事实，非本机现场复现。151320−150698=622尚未闭环，不能归因“全部窗口/去重”。

实际规则：必需五列；hash/appid非空且无NUL，无hash长度≥8要求；completion非负有界整数；UTC纳秒时间解析；严格JSON拒绝重复键/非有限/非法编码等；model可缺省，存在则须匹配注册模型/别名；messages与工具结构需支持；编码失败另记row_errors。facts以source_record_index关联读入与编码记录，保留重复hash，用户投影不另裁时间。

8行fixture包含3条有效同hash="h"（一条07:00，两条09:18:57，JSON均省略model）及5条错误；真实GLM编码后count=3/distinct hash=1。拒绝码INVALID_JSON×2、INVALID_MESSAGES、MODEL_MISMATCH、INVALID_COMPLETION_TOKENS各1；源CSV字节不变，用户投影及分析同源均3。独立报告审计model必须字符串/hash≥8、普通json.loads等不等同产品规则，不能直接相减解释数据丢失。

若要解释622，需要同一CSV SHA/实际配置/同一审计脚本与逐source_record_index分类及row_errors计数对照；仅为定位此差异所需，不是TTFT参考计算必要参数，也不要求上传绝密CSV。现场仍单Markdown嵌脱敏证据。

## 未决及独立复验范围

- 候选2.1.0等待总设计师独立审查、接口冻结，再交前端；没有代签页面或真实现场结果。
- 目录每页枚举已发布索引和分组；未扫CSV，但大历史规模性能仍需评估；快照为指纹不是持久MVCC。任一发布索引损坏明确错误，不静默忽略。
- 真实TTFT精度/模型适用条件、622数差仍未验证。用户参数使参考计算可运行，不等于已校准。
- SSE真实监听测试/浏览器/完整E2E未运行。本轮只TestClient/本地fixture，后续由总设计师先停旧服务并确认端口释放，独立新state和浏览器统一验收；本线不自行另开端口。

## 最终自测结果

不监听端口的用户/S0监控回归271 passed（151.66s），CSV/编码62 passed（46.09s），修复后定点27 passed（17.49s）；mypy12源文件与ruff通过。候选14操作、8个正反例、旧9操作requestBody/responses及冻结文件核对通过。首轮失败及修复、明确排除项保留于TESTS/ISSUES，不称真实E2E通过。

## 本轮源码SHA256

| 文件 | SHA256 |
| --- | --- |
| src/tokenscope/api/user.py | 5dd61592088354ab4b020f68fbef8b086b5346844bbaf6caa030f19b0b6c1830 |
| src/tokenscope/user_monitoring/discovery_contracts.py | 814a58febb41db68ec4bd2bbb7c35569e09742446bbf9cb9502b4c1ea05dfb30 |
| src/tokenscope/user_monitoring/discovery.py | 7e842a12f46a05095650aca5c4a8a99c92610f40e2cb1957f50c0d0561af90c1 |
| src/tokenscope/user_monitoring/defaults.py | e0710a9a3bfda5b3982bb60d53ab662158f19ce9655fc5c6b8e62207c6e75d45 |

## 2026-11-03最新：独立验收通过，冻结后交前端

总设计师确认HV2用户后端独立通过，权威[冻结清单](../../delivery/HV2_USER_FREEZE_20261103.json)状态backend_independently_accepted，identity为4d9e2e5d6c7031ff0aaa266114b92dbcb8684b9a80d722d2cfae9de8ad1d7dc0。此前“候选/待独立验收”描述为历史时点；冻结清单及本通知覆盖该状态，不回写冻结文件。

据总设计师回执：独立运行62项及额外6个跨三模型、P90超过2**53、精确小数le/lt等号边界测试通过，并核对本线最终271监控/62编码及文件SHA。这是独立验收方结果，本线本次未重新运行测试。

冻结范围是用户多模型发现和自动TTFT 2.1.0及清单内文件身份，旧2.0.0兼容材料保持；不含前端验收、现场准确性或真实校准。监控前端正式接入已派发，本线源码窗口关闭。现场622条差异、TTFT真实性能和大历史目录规模仍未决；后续问题由总设计师归口，不自行恢复修改/复测/提交push/监听服务。

本次仅追加入口、交接及本线记忆状态；既有VALIDATION_MANIFEST中的文档SHA指追加之前的自测交接快照，不重新生成该历史清单。源码/测试/契约冻结身份以总设计师冻结清单为准。
