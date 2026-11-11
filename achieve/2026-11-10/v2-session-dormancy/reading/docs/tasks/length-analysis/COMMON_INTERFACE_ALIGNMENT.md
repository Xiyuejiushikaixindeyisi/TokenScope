> V2历史材料，仅供追溯，不是当前启动/修复/打包指令。[原始字节](../../../../originals/docs/tasks/length-analysis/COMMON_INTERFACE_ALIGNMENT.md) · [当前会话登记](../../../../../../../memory/SESSIONS.md)。下文仅迁移导航链接，历史决定和结果未更新。

# Token内容分析公共接口对齐提案

> 2026-10-31更新：公共draft-2第9.2节已接纳本文三项技术选择；Token线已在[TA-D0.3](../../../../../../../docs/tasks/length-analysis/DESIGN_ALIGNMENT_DRAFT2.md)核对接受新增编排/展示语义。本文此前“公共接纳pending”已被覆盖，正式Schema/实现/联调仍未完成。原draft-1摘要仅记录历史核对身份。

版本TA-C0.2，2026-10-31。本线可实施的协议提案，未冻结、未编码、未代签公共维护方接受。对照[analysis-common-draft-1](../analysis/BACKEND_COMMON_CONTRACT_DRAFT.md)，本次读取SHA256为defa979a56d1b677c4ccefaa4ce91f0a86bfb5db237593b4b34be221861684f4。公共文件由低命中主会话维护；本文件落实[接口需求](../../../../../../../docs/tasks/length-analysis/INTERFACE_REQUIREMENTS.md)中的三个未决点，相关验收见[分批计划](BATCH_PLAN.md)。

## 1. 本次收敛决定

| 事项 | 本线选择 | 对公共草案的最小增量 |
| --- | --- | --- |
| 内嵌JSON修改 | 本线严格解析内层，预编译为一个受保护的外层字符串replace_value；保存内层操作清单 | Plan保留typed operation payload、内外层guards和manifest；公共执行器不再实现另一套JSON解析规则 |
| 证据去重 | 原位置身份、内容视图、规则观察分层；T2/T4引用同一单元 | 接收location_id/unit_id/observation_id及关系，聚合按集合/区间并集 |
| 插件接入 | 一个token_content插件，内部选择T1–T4；静态注册给公共分析服务 | 固定输入/输出Schema、能力声明、纯变换处理器注册；不为每条规则注册worker |

这三个设计选择已在本线明确；公共方是否纳入下一版契约仍为pending，不能将“提案完成”写成“两线已签收”。参数错配研究不注册插件规则、不进入T1–T4计划。

## 2. 输入与能力边界

复用公共RequestKey、RequestView、AnalysisScope、EncodingContext，不新增同义公共类型。source_record_index、时间和计数字段在线上JSON中沿用十进制字符串约定；本线纯分析内部可用整数，wire转换归公共层。

RequestView须给出完整原文lazy读取和raw_sha256、源记录位置、原计量及身份引用。raw_body_complete=true表示已读全存储值；capture_truncation=unknown表示不知道采集前是否截断，两者独立。原H/C为空时不做P=H+C断言；值齐全且同口径时校验。原O只作背景。

required capabilities为完整原文、固定范围身份、纯结果保存协议；optional为字段模板参与、精确映射及详细编码复核。optional缺失时字段为unknown/null，不能阻止内容事实分析。运行时路径与源DB连接不暴露给插件。

## 3. 内嵌JSON的定位、保护与编译

### 3.1 TargetLocation

| 字段 | 含义 |
| --- | --- |
| request_key / raw_sha256 | 精确源请求及原文身份，hash_id不作主键 |
| source_pointer | 外层解析JSON中的位置，例如/messages/4/tool_calls/0/function/arguments |
| embedded | null代表没有内层；否则含format=json、parser_version、pointer；pointer空串代表内层根，不能与null混同 |
| text_range | 仅字符串局部操作需要；解码Unicode码点半开区间，不能混用UTF-8或Token偏移 |
| original_type / value_guard | 目标原类型和原值摘要；新增字段用absent guard，不能用null代替不存在 |
| outer_string_guard | 有embedded时必需，对整个解码外层字符串UTF-8求SHA256 |

Pointer转义遵循现有字段引用约定：~0为~、~1为/；对象数字key与数组下标由原容器类型解释。首期数组位置必须为现存非负索引，禁止通配符和隐式追加。所有定位指向冻结的原始快照，不能在执行中重新用工具名或相似文本查找目标。

### 3.2 严格解析与序列化

- 只解析一层JSON字符串，不递归猜测二次编码。拒绝重复key、非有限数、孤立代理项、非法语法；解析不足只影响相应观察/方案，不改写源数据质量结论。
- parser_version固定数字处理。建议json-exact-1保留数字词法，不经float舍入；结构比较时1与1.0可保守视为不同，true与1必须不同，规则方法公开记录。该约定只用于本线比对/变换，不更换统一编码器。
- 修改序列化保留对象key插入次序、数组次序及未改数值词法；字符串不做Unicode归一化。确定性空白/转义策略与serializer_version写入manifest。比较用的排序表示不用于写回业务JSON。
- 如果现有解析/序列化链无法保持非目标数值或结构，返回SERIALIZATION_UNSUPPORTED，不借用默认浮点序列化悄悄改变参数。

### 3.3 两阶段应用

create_plan阶段：确定具体请求集合与准确参数，读取原文并验证外层guard；本线变换处理器执行内层语法/目标guard/业务约束检查，在副本上计算最终外层字符串，输出PreparedMutation。此时不编码、不回放。方案待参数时只保留候选，不能创建貌似可评估的空计划。

evaluate_plan阶段：公共层重新校验scope与原文/原值身份，将已编译的替换/数组操作应用到副本；核对非目标子树及协议不变量，复用原validate_request与统一编码。任何目标失败，整个方案blocked，不发布after或收益。公共层保存before/after摘要与每项真实变化。

PreparedMutation的最小字段为handler_id/version、target、guards、public_primitive、replacement或删除位置、source_operations、business_basis_ref、invariants、manifest_fragment。大replacement可保存受摘要保护的内部blob引用，不使用客户端文件路径。最终Plan必须冻结替换值/摘要，不能评估时再调用LLM生成文本。

### 3.4 同位置、数组与组合

1. 两个内层操作位于同一外层字符串：由同版本处理器对同一原值一次编译，形成一个replace_value；不是依次应用两个基于旧值计算的替换。
2. 同目标相同操作及参数只保留一份执行，合并finding_refs；同目标不同替换、父子覆盖、重叠文本区间拒绝为PLAN_OPERATION_CONFLICT。
3. 明确不相交的内层字段可组合，但须一次编译并验证整体不变量。公共层不得根据最终字符串相似度猜测合并。
4. 同数组删除多个元素先解析原位置/guards，编译为保留原元素身份的最终数组；允许改变删除点后的下标，其他元素值及相对次序不变。普通消息删除不得移除tool/function角色或携带调用的消息。
5. 与L类消息移动/前缀改写发生冲突时，首期不做自动重定位；要求生成明确的新组合计划。组合仍单独编码回放。

构造示例（非实际测试）：arguments源字符串为{"document":"全文A","mode":"brief"}。工具协议允许document_ref后，计划记录对内层/document的删除guard、/document_ref的absent guard及真实引用doc://case-7；本线编译为{"mode":"brief","document_ref":"doc://case-7"}，公共层仅替换外层arguments字符串。该引用由业务提供，本线不创建文件、不访问外部工具。若mode被顺带改变或引用协议不支持，则拒绝。

### 3.5 manifest最小字段

scope_digest、request_key、operation_ids、handler/parser/serializer版本、原/新raw摘要、外层路径、内层路径与源操作、目标原/新值摘要、guard结果、业务依据、serialization_changed、non_target_structure_verified、协议校验结果。公共编码后补充原/新IDs摘要及P；不能由变换处理器填虚构Token收益。显示片段截断与实际全文处理独立记录。

## 4. 证据身份与聚合

### 4.1 三层身份

| 层 | 身份材料 | 排除项/用途 |
| --- | --- | --- |
| location_id | identity_schema_version、RequestKey、raw_sha256、source_pointer、embedded定位/解析版本、可选text_range | 不含rule_id、工具名、显示片段；原位置可跨方向共用 |
| unit_id | location_id、representation、measurement_version | 不含T2/T4或其解释标签；同位置不同度量视图明确区分 |
| observation_id | rule_id/version、排序后的参与unit_ids、predicate/method、policy摘要或null | 同一证据可以有多个业务判断；策略改变必须产生新观察 |

id采用带类型前缀的SHA256。摘要输入是固定版本的元数据编码（UTF-8、key确定序、计数十进制字符串、无多余空白）；不把原载荷排序序列化后的结果误作原文摘要。摘要碰撞或相同id内容不同应报完整性错误，不能覆盖。具体编码样例与公共Schema一起固定于TA000。

ContentUnit的unit_kind改作facets/角色描述而非身份材料：同一个/messages/3/content可同时是T2的大返回与T4的历史结果，复用同unit_id。parent_unit_id、container_unit_id、overlap_relation表达父子关系；不能因两个单元值相同就合并不同位置。

### 4.2 计数与去重

- affected_requests为RequestKey并集；同一hash_id的两条记录不合并。同载荷跨请求保留不同身份，不据此判断重复执行。
- 涉及字节仅在同representation/unit下合计不重叠位置：容器与子字段不可加总；文本区间同位置取并集；没有可证明的覆盖关系时不产出跨层总量。
- T3重复组至少含一个tool_result，排序后的原位置集合和精确比较方法决定组身份。哈希只筛候选，逐值验证后才下结论。
- 完全相同字符串k处才给(k−1)份重复字节；结构等价但原表示不同只给各位置度量，不伪造统一节约量。多个重复组有嵌套重叠时统一排除或不提供合计。
- 不同策略/规则的发现可以独立展示，证据与相同修改候选共用；收益按evaluation_id引用，跨卡片不求和。
- 公共持久化键为report_id＋稳定对象id；同一attempt重复提交完全相同fragment幂等，内容不同为冲突。新报告保留新发布身份，不覆盖旧报告。

构造示例：R17的U3为/tool结果，T2引用U3并指出字段白名单；T4引用同U3并指出保留策略。报告有2条观察、1个结果单元、1个涉及请求。若T3另引用arguments内U4，同请求两位置仍只计1个涉及请求；T2与T3的修改需组合重算。

## 5. 插件接入协议

### 5.1 静态注册与职责

拟plugin_id=token_content，规则集合T1/T2/T3/T4。包位置src/tokenscope/token_content，由本线维护；公共analysis_common、API/CLI/worker装配由主会话维护。客户端仅提交已允许的方向/规则/策略参数，不能提交Python模块路径、任意脚本或新的处理器。

主会话在公共服务初始化时静态注册插件及变换处理器。已存在Dispatcher.register接收的是持共享worker.lock的Processor；本线插件不实现process_next、不单独注册Dispatcher、不持源数据库、不另起线程池。

Descriptor包含plugin_id/version、兼容的公共契约版本、parser/measurement版本、rule_versions、policy_schema_version、支持的handler_id/version与required/optional capabilities。未知版本或重复注册id报错，不用静默兼容掩盖语义变化。正式版本尚未分配，此处不虚构已冻结1.0。

### 5.2 逻辑调用面

| 调用 | 输入 | 输出与副作用边界 |
| --- | --- | --- |
| describe | 无 | Descriptor；不读取源数据 |
| validate_selection | rule_ids、policy与资源预算 | 规范化配置或明确错误；不检查业务内容 |
| analyze_request | 不可变RequestView、选择配置、EvidenceCapabilities、RunControl | TokenAnalysisFragment；逐请求纯分析，T1–T4共用一次提取 |
| prepare_mutation | 原RequestView、候选、显式参数与业务依据 | PreparedMutation或不可执行原因；不写源、不编码、不调用工具 |

公共层负责流式读取、调度、持久化、归组、任务状态与评估。插件不自己调用save_observations；返回纯fragment，由公共层验证引用均属于scope后保存。需要映射时消费公共预先提供的证据；缺失采用unknown，不从GET或插件内自行加载Tokenizer。

Fragment包括request_key/raw_sha256、版本引用、locations/units、observations、finding_candidates、modification_candidates、rule_results、coverage、reason_codes。外部HTTP envelope及状态码由公共方定义，本线不能返回另一套API收据。

### 5.3 状态与预算

规则执行状态completed/not_applicable/partial/failed/not_checked与判定状态met/not_met/unknown分开。completed+unknown可表示已检查但缺策略/映射，不能改写成“没有问题”。每条规则保存checked_units/eligible_units、未查原因及停止位置；跨规则检查数不相加当请求总数。

RunControl提供固定BudgetSpec、取消检查与预算累计。至少在请求边界、结构遍历/精确比较批次、变换编译前检查；不承诺中断已经进入的第三方解析调用。单请求超预算时显式partial，不把截断正文当全文；公共层对总体deadline和worker中断负责。本线不新建取消HTTP API。

预期数据不足局部降级；源摘要/范围失配由公共层阻断；意外插件异常记录方向failed并保留错误码，不能降成无发现，其他方向已完成事实可保留。取消按公共草案映射interrupted，已封存结果不改，显式重试新attempt。

## 6. 可签收项目与待办

| 项 | 本线状态 | 公共维护方需要确认 |
| --- | --- | --- |
| 受保护外层替换＋内层变更清单 | 方案已明确 | Plan/manifest是否接纳这些字段，prepare处理器的归属及注册位置 |
| 位置/单元/观察三层身份 | 方案已明确 | 公共元数据编码、稳定id和保存冲突协议 |
| 一个插件、四条纯规则 | 方案已明确 | 内部类型与静态registry版本、公共输入能力和状态映射 |
| 消息删除/组合冲突 | 方案已明确 | 公共原子应用是否覆盖remove普通消息；不自动重定位原则 |
| 验收责任 | 本线计划已形成 | 公共真实评估可用版本及联合验证接口；不以mock替代 |

以上需公共维护方在其契约中纳入或列出差异，并记录实际版本/摘要后才称双方对齐。不是重新审批产品，也不要求等待全部公共实现才能做独立规则。当前用户明确暂不编码，所有后续批次均planned。
