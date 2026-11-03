# HV2-R1-TOKEN-PREP：私有分析准备与公共依赖

2026-11-03；状态：准备完成，等待公共层独立验收及准确冻结版本/实施派发。不是产品修复或现场复现报告。

## 身份、范围与依据

环境 CODEX_THREAD_ID 与 CODEX_SESSION_ID 均为 `01a18fcd-0464-7cf1-b435-4f394bd33e66`。角色：Token异常私有后端维护；P0核实原因/成本与公共依赖，P1准备可验证优化。总设计师为 `01a1800e-80b4-7400-a78b-a84f5b6e888d`。本轮仅本文件、本线ENTRY和memory/tasks/length-analysis.md；不改公共源码、CURRENT、SESSIONS、执行板，不发送跨会话消息。

已读AGENTS、CURRENT、SESSIONS、docs/README、本线ENTRY、[执行板](../delivery/HV2_REPAIR_EXECUTION_20261103.md)、[总计划](../delivery/V2_REPAIR_COORDINATION_PLAN_20261103.md)。HEAD实际为 `7cbe28621f4e46083bf47f9aa14b011b3cb250c4`；原交付源码 `b17cdc07b0a351d0f5c4fb1b26f0e05be2b3a0af`。以下公共行号仅指此次读取的基线，不预判并行修改后的冻结接口。

两份现场原件摘要已实际核对一致，原文不改：验收报告 `93d6d02d5a4937ecea23491309ea59da1d8e0ad51417ffae6e64b8398ac2487e`；调查报告 `51a5a9430137523b0ccc2a6fd52f9ed48334458a900c58d733718242514eff83`。重点读调查§3/§5/§7、验收P3。报告是现场回传，不是本线亲自重跑结果；外部JSONL/脚本及真实最小反例未完整嵌入，无法据此完成现场因果归属。

## 一、已确认路径与不能合并的根因

| 项目 | 源码与证据 | 判断及归口 |
| --- | --- | --- |
| low_hit-only仍执行Token | analysis_common/service.py:422–434在低命中后直接进入Token循环；调查与验收记录两大Qwen实际执行Token | 已确认方向控制缺陷，公共层修复；两大Qwen下一次只能low_hit，不为性能采样额外启动Token。 |
| 全局findings预算触顶 | runtime.py:59–63；现场100条L3/L4、低命中只checked少量请求 | 低命中发现/扫描覆盖问题归公共层。不能由100条推定全部请求或规则完成。 |
| Token fragment不完整 | plugin.py:74–96提取失败；139–175规则停止/局部提取错误；199–221候选生成停止和coverage | 私有独立停止链，包括单位/深度/比较字节/候选预算、局部解析错误。需逐fragment原因与stop_location，不能凭零recipe归因。 |
| TOKEN_FRAGMENT_INCOMPLETE | recommendation_engine.py:64–69在读取fragment后检查coverage.complete，失败即抛出，早于adapter.propose | 直接原因是fragment不完整，不是configured_recipe_count=0。不改partial为ready。 |
| 零recipe | recommendation_engine.py:56–97未对空bundle提前返回；auto_proposals.py:85–97先校验/摘要/extract，再迭代recipes | 完整fragment仍逐请求重读/重提取但无提案；不完整fragment可先停止。零recipe与前述原因可同时存在，不能相互替代。 |
| 有recipe但无业务依据 | auto_proposals.py的applicability分支；recommendation_engine.py:140附近advice/basis分支 | 与零配置/技术失败独立；保留advice_only、modified_requests=null、evaluation_ref=null，不写0/收益。 |
| checked全量 | service.py:466–473不论fragment是否complete均checked+=1，并独立累积complete | checked仅遍历请求数，不是规则完成数或可评估数；需同时看rule_results/coverage/reasons。 |

**进一步因果校正：在此次基线未找到“全局findings耗尽直接导致Token fragment不完整”的代码边。** service.py:436给每个请求新建RunControl，使用token_selection.budget；plugin不消费TaskControl.findings。应分别记录低命中全局预算、Token每请求预算、推荐预算，再按同任务fragment连接证据。现场报告不能补出这个不存在于已读代码的因果关系。本轮也不认定所有fragment均由同一私有问题触发。

L4差异不是动态字段浪费或会话改写证据；无最终DOM，不能确认空页具体组件路径。151320与150698差622缺逐行映射，不能全归窗口/去重；Qwen逐UUID/MA SHA缺口保留给归口方。原报告P3耗时及“块大小解释快慢”缺任务内profile，调查的terminal间隔含调度等待；都不作为本线性能基准。

## 二、实际成本路径（源码分析，未测耗时）

1. 初始分析：plugin.py:74 extract；extraction.py:51–53 UTF-8长度检查与严格JSON解析；json_values.py:28–68先扫描深度、再json.loads、再dumps验证Unicode。外层与内嵌JSON分别解析，不能把外层深度19认作所有内嵌串也低于32。
2. 每个结构单位：extraction.py:73消耗max_units，82 measure、91再次规范化序列化/摘要，108–136递归children；measurements.py:16对结构重新dumps。子树会在祖先和自身多次遍历，深链的工作量更接近各子树大小之和，可能随深度增加，不等于请求字节一次扫描。units上限在add前检查，但单个父容器序列化仍可能昂贵。
3. tools/functions：extraction.py:162–189即使只跑T2–T4仍构造定义及全部子单位。身份识别及T3工具参数Schema核验需要定义；“不做T1”不意味着可以直接删定义库存。移除其证据单位会影响unit/fragment身份和预算，不属于未经审查的无语义变化优化。
4. T3：duplicates.py:28–38候选再次dumps/编码/hash并累加比较字节；49–79精确组且排除重叠。并非只有低成本hash。结构子单位、长消息、多次相同载荷同时增加序列化、bucket内存及父链工作；不能取消精确比较只留hash。
5. 自动建议：auto_proposals.py:85–97每次验证整个bundle和raw摘要，即使空recipe仍extract；有T3时auto_duplicates.py:95–112在appid匹配后又extract并loads。同请求多个匹配T3 recipe可能多次重做；不匹配appid的T3会在内部提取前返回，但外层extract已发生。
6. 再准备：auto_proposals.py:_prepare重新构造与校验授权目标是防篡改边界，不直接删除。fragment序列化/Schema再验证、SQLite写入(service.py:438–465)和推荐阶段source.read_request也有CPU/I/O成本。

encoding_calls=0只说明相应编码计数没有增长，不计JSON解析、SHA、Python对象/Schema、比较、持久化等成本；不据此推CPU、延迟或缓存命中结论。

## 三、公共层需先冻结的消费条件

- 方向选择及disabled/not-run语义：low_hit-only不得调用Token插件/提案/准备/编码；历史已封存双方向报告保留，不重写。
- 请求遍历数、规则完整数、适用数、预算停止点与各方向预算归属；不得用checked冒充全部规则完成。明确fragment不完整时保留哪些已知事实及推荐阶段如何解释。
- 区分零recipe、业务依据缺失、规则不适用、预算中断、技术失败；如公共层为空bundle跳过扫描，须明确scan coverage语义、取消检查、source验证以及历史兼容，不能私有适配器自行把“不扫描”冒称全量checked。
- partial历史发现/读取与默认选择、L4/L5展示、推荐summary/可见性及旧报告兼容由公共层/前端负责；本线只消费冻结字段，不自拟新HTTP或Schema版本。
- 冻结身份包括机器契约、源文件SHA、真实响应样例、复验命令；公共冻结后再确定私有测试适配。app/CLI/锁/构建文件本轮无补丁需求。

## 四、后续可优化候选及门槛（尚未实施）

| 候选 | 预期减少的工作 | 前置及兼容约束 |
| --- | --- | --- |
| 空bundle不做无用库存重提取 | 从每完整请求一次额外extract降为0 | 优先公共空配置分支；私有若加空返回仍保留既有bundle、raw/scope校验和必要取消检查。预算计数/错误可见性变化须由公共冻结明确，不悄悄吞错误。 |
| 单次add共用规范序列化结果 | measure与content_sha256避免同子树重复dumps | 字节/词法/Unicode、排序、unit/location ID和错误完全一致；不跨请求缓存，避免内存无界。 |
| 同请求多个recipe复用只读Inventory | 外层与T3重复extract | 当前不同调用共用RunControl、会消耗预算，复用会改变预算停止时点，不能声称严格零语义变化；须先冻结逻辑计费，保留重新授权验证和防篡改。 |
| 选择后再构建不必要索引/解析 | 空/不适用recipe少建maps或parse | 不降低输入/身份校验，不改变非法bundle拒绝；先profile确定占比。 |

不做：全局提额、隐式抽样、删除规则或Schema断言、扩大Token执行范围、删工具定义单位以伪造提速、用跨请求缓存混淆raw/模型/scope。性能达标值需基线后确定，不承诺倍数或现场SLA。

## 五、T2–T4适用性及最小研究输入

| 规则 | 现能力可表达 | 不能判定/负例与待补依据 |
| --- | --- | --- |
| T2 | rules.py:114–158工具结果容器计量；有明确limit/allowed_fields策略时237–268产生越界发现；无策略是内容事实、NO_APPLICABLE_POLICY | 普通user内JSON不自动当tool result；大字段可能业务必需。需实际脱敏结果、字段必需性/单位/阈值、允许投影/截取的业务依据；不从字节直接算节省。 |
| T3 | duplicates.py:49–53、77要求非重叠重复组至少一tool_result；精确文本/保留数值词法的结构相等 | 普通消息重复/few-shot/引用不自动归T3；tool重复也可能是必要历史。需完整疑似重复位置及合法近似反例、目标角色/参数和明确删除/引用授权；引用协议与Schema另核。 |
| T4 | 同请求工具结果顺序/后续消息数；显式retain_last按工具身份和保留单位判断 | 后续消息多不代表失效；截断/去重需要业务保留约定，工具结果内容重复不是自动可删。缺会话关联不判loop、重试次数或跨请求历史改写。 |

调查§7只足够安排结构分层：带工具长链、普通消息对照、深Schema/嵌入JSON。真实最小正反例与脚本正文未提供，不新造生产recipe/节省数，不恢复T1，不增长度精简职责。参数错配仍独立研究；本轮不扩展。

## 六、后续最小复现/profile计划（本轮未执行）

仅收到公共验收通知后执行，先几十个合成请求，不长全量，不监听服务。fixture标明synthetic，不冒称现场数据。

1. 状态矩阵：低命中预算耗尽而Token片段完整；独立max_units/max_depth/max_comparison_bytes/max_candidates停止；局部非法内嵌JSON/tool_calls:null；完整+空bundle、不完整+空bundle、完整+缺basis。记录各阶段/规则coverage、停止原因、checked/eligible和summary，区分每条链。
2. 方向测试：low_hit-only设置Token analyze/propose/prepare为失败哨兵，必须零调用；双方向低命中partial不得自动破坏Token独立控制。公共维护方先提供其独立通过证据，本线复验消费。
3. 结构规模：纯消息无tool、1工具/2结果、较长工具链、嵌入JSON宽/深变化。单请求字节固定时变units/depth，固定结构时变payload大小；层级逼近预算上下界但不使用现场5万请求。合法few-shot、必要引用、相同/近似载荷和重叠单位分别为负例/事实正例，不擅给生产授权。
4. 分段记录：wall/process CPU、峰值内存、parse/dumps/sha/extract调用数、序列化总字节、units/比较字节/候选/encoding_calls、fragment与SQLite大小、读取次数。初始analyze、proposal、prepare、持久化分别计时；带profile与不带profile分开，固定种子/环境/revision/模型资产/预算，重复小样本看中位与范围。
5. 等价门槛：相同有效输入结果/身份/精度/空值/授权语义保持；所有声明的预算停止、取消/恢复和错误路径有断言；合法负例不产生可执行删除。仅对确认热点改动运行定向回归，再按批准批次运行本线套件。新状态字段按公共冻结版本校验，旧封存报告仍可只读。
6. 成本门槛：空配置快路径不得再做库存提取；不增加实质峰值内存和序列化量，非空策略无经重复对照确认的性能回退。耗时数值阈值在基线profile后给总设计师审定；本轮无性能实测/提速声明。E2E仅总设计师协调停旧/新state/新浏览器环境。

## 七、本轮实际交接

实际操作：读取环境ID；Get-Content/rg定向检索；WSL git rev-parse HEAD；Python hashlib核对原件与所列源码。未执行pytest/profile/收益回放/服务/容器，未改产品源码、测试、契约、原始证据；无修复前后运行对比可报。上述缺陷属于静态路径确认，现场首个不完整fragment的原因与成本热点仍待证据。

精确变更仅本文件、docs/tasks/length-analysis/ENTRY.md、memory/tasks/length-analysis.md。产品契约差异：无；旧报告兼容未改。入口/记忆只写本线进度，不覆盖共享总状态。完成后停止，等待公共层独立验收、冻结版本与私有实施任务；不轮询、不发新会话、不commit/push/打包部署。

## 本次读取的源码摘要

- `src/tokenscope/token_content/plugin.py`：`43155917fb2ee28140e69dcc940746e0a28ce5c304ee7a5874c908ce963aa4c8`
- `src/tokenscope/token_content/extraction.py`：`0bc914470882ab975398ca6a25b9e01bbe0d690cf2373927000ecd5c52426b87`
- `src/tokenscope/token_content/auto_proposals.py`：`d7d0718e86b6e01059e372a53771cb52eb903a8e5731fd7af246e64501319575`
- `src/tokenscope/token_content/auto_duplicates.py`：`48a9f4bf1135e8118fc152065a3d47722014c417a762875c38230491698dfb19`
- `src/tokenscope/token_content/duplicates.py`：`1229d032470ea5fc5c88c8fed671c1323265abf6832a1f63954a36e26983d282`
- `src/tokenscope/analysis_common/service.py`：`ddad2163bb4131f5f680817deee4f7ec3cc902fc77762985f24db4fb6b4c3770`
- `src/tokenscope/analysis_common/recommendation_engine.py`：`01fde28e490926505a8fc159b4956ac63e4bcc4e5d84a6afc1e323dbd72b2efe`
- `src/tokenscope/analysis_common/runtime.py`：`9b2dd457ba5363854b90e94d75c8f84bc00bd4d61ca583430b61bf9850eb67e7`
