# HV2-R1-MA 后端交接（候选，待独立验收）

2026-11-03。维护 session `01a18ab2-2600-7ae1-8b0e-979dad9ec3be`，本轮环境 CODEX_THREAD_ID/CODEX_SESSION_ID 一致复核。任务来自 V2总设计师；基线 HEAD `7cbe28621f4e46083bf47f9aa14b011b3cb250c4`。仅 MA 源码/测试/本线文档与记忆；不提交/push、不监听服务、不部署打包、不改总执行板。前端接入须待总设计师验收冻结。

## 证据与结论

两份原件 SHA 实际核对一致，未修改：

- `docs/huawei/HUAWEI_V2_ACCEPTANCE_REPORT.md`：`93d6d02d5a4937ecea23491309ea59da1d8e0ad51417ffae6e64b8398ac2487e`。
- `docs/huawei/HUAWEI_V2_INVESTIGATION_REPORT_20261103.md`：`51a5a9430137523b0ccc2a6fd52f9ed48334458a900c58d733718242514eff83`，主要读取§6及相关数据/缺口章节。

报告支持 DS 缺 cached 观测、GLM 部分预热冲突两种结构性路径。本机无华为原始 CSV，以下复现均为明确合成 fixture，不是完整现场逐 UUID 复现。GLM 表称27但6+9+11=26；Qwen48完整 UUID 矩阵、18份完整 SHA、GLM 实际冲突时间边界缺失，仍待现场。

补充勘误：调查§3.2称窗口外记录被标记后不计 assigned；当前 `ingest` 实际在可解析 request_time 超出绑定窗口时抛 OUTSIDE_WINDOW，使任务失败，不是过滤。handle_time 超窗口仅计诊断，仍可参与回放和真实统计。二者不可混用；需要现场分别回传原始两种时间及绑定，不根据报告擅自改过滤语义。A=2/P=0 不是无请求，而是有请求、无有效生产输入字段。

## 修复方案和兼容

既有 independent/paired/pressure 公式未发现本任务所述缺数的计算错误。缺口是无法在四指标附近取得逐指标原因、分母及真实冲突边界。新增**独立可用性投影**，不修改冻结 MA Snapshot 1.0.0、旧 Schema、旧结果或现有指标值：

`GET /monitoring/ma/runs/{ma_run_id}/instances/{instance_uuid}/availability`

- 同原 MA 身份头和 no-store；未发布409、实例不存在404；新响应包裹 service_instance_id、ma_run_id、binding 与 availability。
- `availability.schema_version=1.0.0` 是这个新增解释资源自己的版本，非旧快照版本升级。候选 Schema/样例见本目录 `hv2-availability/`。
- 新任务聚合阶段将严格DTO校验后的解释写入 facts 的独立 availability 表，之后随原封存摘要一起固定。GET只读取投影并校验DTO，不扫描事实、不聚合、不编码、不回放、不补写。
- 老结果没有该表，返回409 `AVAILABILITY_NOT_RECORDED`；原快照继续原样读取。前端应继续展示旧快照现有 independent/paired/hour/bins，提示“历史结果未记录细化原因”，不得自动重算或把它当任务失败。需要新原因时由明确的新分析操作生成新 run，不迁移旧seal。
- 不需要公共app/CLI/锁/构建补丁；原CLI快照不扩字段。新增路由由原MA router装配。旧客户端可继续使用所有原端点。

## 前端字段消费

每个 metric 提供 state（available/partial/unavailable/empty）、sample_count、population_count、numerator、denominator、denominator_unit、reasons。精确整数均十进制字符串；百分比仍读取原快照值，不用JS Number重算大整数。population_count为now的A；partial表示相对A只有部分样本，**不是估计补齐后的全量值**。

| 新解释字段 metrics.* | 原快照值 | 样本/分母 |
| --- | --- | --- |
| paired_ideal_hit_rate | paired_ideal.hit_rate | Q；Q本地输入总量 |
| paired_real_hit_rate | paired_real.hit_rate | Q；Q线上输入总量 |
| independent_ideal_hit_rate | ideal.hit_rate | E；E本地输入总量 |
| independent_real_hit_rate | real.hit_rate | R；R线上输入总量 |
| actual_uncached_tokens | hour.uncached_tokens（与real总量在R非空时一致） | R；无除数 |
| hour_uncached_tokens_per_second | hour.uncached_tokens_per_second | R；固定3600秒 |

并排比较仍使用paired；不可用时保留原因，另外展示清楚标明“独立”的可用值。不能用独立值填paired格。四主指标中的任一个无值不遮蔽其他项。真实R仅依赖assigned且prompt/cached有效，不依赖JSON、completion或编码成功。

`bins[0..11]`逐一对应原快照12桶，解释未命中Token/s，分母固定300秒。A=0桶为empty，数值0；A>0且R=0为unavailable/null；0<R<A保留已知子集总量和速率并标partial。整小时同理，只累加已观测R；不能把缺失桶当观测0，也不能把partial小时值外推全量。请求速率仍A/300或A/3600，与真实命中观测缺失无关。

主要原因：source_cached_missing来自该UUID已归属now行的cached_tokens/MISSING_TOKEN_VALUE；invalid_cached包括负数/溢出/大于prompt等；no_valid_prompt表示P=0；no_real_samples/no_ideal_samples/no_paired_samples说明集合为空；warmup_order_conflict仅阻断理想回放；zero_input_denominator表示有样本但输入总和0；no_valid_prewarm是可用冷启动结果的限制，不自动隐藏值。now_field_issues保留字段×原因×条数，非错误请求去重数；不会用全文件原因归咎每个UUID，也不会因completion坏而隐藏真实值。

warmup记录成功编码pre/now计数、pre最大handle、now最小handle，均UTC纳秒格式。encoded_now_count是“成功编码输入数”，在冲突时仍可能>0；coverage.encoded/E是“理想回放结果有效数”，冲突时为0，二者不要混名。时间相等按pre优先再源记录序号；真正冲突只在pre_max>now_min时发生。

## 预热边界审查及待决策略

当前 candidate 必须已归属、hash/appid有效、原始JSON可编码、handle可解析；成功encode才写local_prompt。replay bounds只读local_prompt非空，所以无效pre尾部、编码失败不纳入；prompt/cached/completion坏不代表输入不可编码，不能据这些字段删pre。request_time决定两个窗口，handle决定回放顺序。重复hash保留独立请求；同刻pre先于now；同角色再按源记录序号。源码没有按hash去重，也没有用request_time代替处理顺序。本轮不改此语义。

明确合成示例：相同4096-token输入，Qwen普通链block1536、MTP关闭。pre请求request_time=07:59、handle=08:02；now两请求request_time=08:00/08:03、handle=08:01/08:03，生产prompt=4096、cached=0。

| 策略 | now理想命中Token | 对照含义/影响 |
| --- | --- | --- |
| 当前整UUID停理想（本轮保留） | 两条均不可用 | E=Q=0；R=2，独立真实率0、实际未命中8192不受影响 |
| 丢弃pre尾部后冷启动now（未实施） | 0、3072；总率37.5% | E=Q=2，但已不使用完整pre；本例第二条复用第一条now，不是证明删尾普遍无影响 |
| 按handle混排两窗口、仅统计now（未实施） | 0、3072；总率37.5% | 本例相同，其他有独特pre前缀的流量可能不同；改为按时可见历史，不再是全部pre后now |

若直接先完整pre再now，本例会给两条各3072（75%），第一条使用未来缓存，不能采用。当前证据不足以选择替代方案；建议本轮先保留原语义和新增说明，收齐真实边界后由总设计师判断是否需用户审批新版本策略。任何替代须新策略身份、新run与独立对比测试，不能重写旧seal或仅把status改available。

## 验证与问题记录

本线实现及本地验证完成，候选待总设计师独立验收冻结。原MA测试中的真实监听用例未自行执行，交总设计师在停旧/新state/新浏览器的唯一候选环境验收。日常TestClient不监听网络。

实际命令（项目根目录 `.venv/bin/` 环境）与结果：

| 命令 | 实际结果 | 证据（artifacts/validation/monitoring/v2-ma/HV2-R1/下） |
| --- | --- | --- |
| pytest tests/unit/ma/test_availability.py tests/unit/ma/test_statistics.py -q | 首轮17 passed，4.88s | targeted.txt |
| pytest tests/unit/ma -k "not test_live_http_background_worker" -q | 60 passed、1 deselected，77.21s；包括三模型真实资产、封存/故障/进程恢复 | ma-regression.txt |
| pytest tests/unit/ma/test_availability.py -q | 最终增量21 passed，5.22s；补编码失败边界、严格负例及有效旧seal读取 | final-incremental.txt |
| pytest tests/unit/monitoring/test_simulation.py tests/unit/monitoring/test_statistics_rules.py tests/integration/monitoring/test_interfaces.py tests/integration/monitoring/test_views.py tests/integration/monitoring/test_view_operations.py -q | 受影响回归40 passed，14.73s | affected-regression.txt |
| ruff check src/tokenscope/monitoring/ma src/tokenscope/api/ma.py tests/unit/ma docs/tasks/monitoring/v2-ma/hv2-availability/generate.py | 通过 | ruff.txt |
| ruff format --check 同上路径 | 24文件通过 | format.txt |
| mypy src/tokenscope/monitoring/ma src/tokenscope/api/ma.py | 10源码通过 | mypy.txt |
| python docs/tasks/monitoring/v2-ma/hv2-availability/generate.py | 9个合成严格DTO样例；旧Schema全部模型、旧OpenAPI全部路径及已有components逐项相等 | contract.txt |
| git diff --check -- src/tokenscope/monitoring/ma src/tokenscope/api/ma.py tests/unit/ma | 通过 | 本轮命令输出 |

pytest仅既有Starlette/httpx弃用warning。60与21有重复，不把两数相加当互不重叠测试。最终源代码与60项回归时一致；后续仅扩测试/生成文档。新增业务端点的TestClient验收包含响应身份、no-store、未发布409、未知UUID404、错误服务身份409、重复GET前后全封存文件SHA不变；旧fixture封存有效且GET仍不改数据库。没有运行浏览器/监听服务/华为CSV，不能标现场通过。

修复前后：原快照算法和数值保持一致；缺cached合成例E=1/R=Q=0，独立ideal=75%，旧paired为null；新解释明确源cached缺失且保留独立ideal。冲突合成例A=P=R=1/E=Q=0，独立real=25%，小时已知未命中75/3600；新解释提供真实有效编码边界08:02>08:01，未改变该值。零cached显示0%而非缺失；零prompt总量的命中率null但未命中量0有效；坏JSON/坏completion不影响R；部分观测的已知小时量保留并标partial。

本轮问题闭环：初次静态检查发现两处长行、局部state类型和同名变量声明，已修正并复查；无测试断言删除或Schema绕过。预热检测未发现需修代码的边界bug，故replay.py保持原样。调查的现场具体冲突尚未补证，仍不声称已修复所有GLM真实冲突。

### 源码身份、精确清单及冻结依赖

[逐文件SHA](hv2-availability/source-manifest.json)覆盖5份源码+1份测试；组合身份 `15194270d39e4e51950c83fd10d7694a3282d9c96a0b9ffbfd7c882b3d2f96f5`。算法为排序path→SHA256映射的紧凑JSON再SHA256。不是Git提交ID；本线未commit/push。

本轮源码/测试精确文件：

- `src/tokenscope/monitoring/ma/availability.py`（新增DTO与纯聚合期解释）。
- `src/tokenscope/monitoring/ma/ingest.py`（只新增投影表）。
- `src/tokenscope/monitoring/ma/statistics.py`（聚合后写新投影）。
- `src/tokenscope/monitoring/ma/service.py`（只读读取及旧结果明确缺资源错误）。
- `src/tokenscope/api/ma.py`（新增解释路由，复用原guard）。
- `tests/unit/ma/test_availability.py`（新增合成和HTTP/历史兼容测试）。

本轮文档/记忆精确文件：本交接；本线ENTRY.md、FRONTEND_HANDOFF.md仅增当前交接链接；`hv2-availability/{generate.py,schema.json,examples.json,candidate.openapi.json,source-manifest.json}`；`memory/tasks/monitoring-v2-ma.md`仅追加。原有未提交文档内容保留；其他session文件未接管。验证日志留在artifacts，不纳入业务交付源码。

**契约工具待总设计师安排的冻结动作：** 旧 `docs/contracts/ma-monitoring-v2/{schema.json,design.openapi.json,manifest.json}`保持原件。既有 `scripts/contracts/validate_ma_contract.py`将运行时完整OpenAPI和旧快照逐字节比对，因此新端点加入后其全量相等检查本轮实际退出1并报 `Stale protocol artifact: design.openapi.json`（证据 `artifacts/validation/monitoring/v2-ma/HV2-R1/legacy-contract-check.txt`），不能声称该旧校验器全量通过。候选生成器已独立证明所有旧路径/已有components与Schema不变，并生成包含新端点的完整候选OpenAPI。建议总设计师冻结本目录扩展契约后，安排契约工具维护窗口：保留旧契约冻结校验，新增本扩展的完整OpenAPI与DTO校验入口；不要覆盖旧Schema/旧seal。本线未越界修改scripts/contracts或公共文件。前端接入以冻结后的解释资源与旧快照双读为准。

## 现场补证/复验（真实数据限定）

1. 先核对候选源码/镜像/运行配置、服务身份；由总设计师按固定交付流程停旧、确认端口释放、独立新state冷启动。保留旧CSV、旧包/state/结果，不改原文、不补0、不混Trace数据。
2. 全部9制品18CSV给出完整路径、bytes、SHA256、准确规格、pre/now窗口、时区、原始request_time与handle各自min/max及窗外计数。完整UUID，不用前8字符作关联键。发现request_time窗外先解释文件/绑定身份，不静默过滤。
3. DS6CSV逐文件计cached的空串、null字面值、合法0、正整数、非法整数、cached>prompt；向上游确认字段是否产生、是否导出丢失。报告只能证明导出文件缺值，不能单凭空列断言网关未采集。无法取得观测则真实指标保持缺失，独立ideal仍验收，不伪造“已恢复”。
4. 每制品每完整UUID列A/P/R/E/Q、pre已归属/编码数、独立/paired各样本与输入/命中/未命中总量、小时A/R/未命中/速率和可用性原因；与质量行逐一对应，不能从全文件的错误数推单UUID原因。
5. 每冲突UUID给出成功编码pre最大handle及now最小handle，附对应role/CSV记录序号/hash、原始request_time/handle；同时给原始所有记录边界和有效编码边界，列被排除原因。等时与真正大于分开。报告缺失这部分，当前尚不能确认每个真实冲突属于哪种输入。
6. 全UUID检查12桶连续且每桶300秒、总A/R等于小时A/R；只累加有效R的未命中量与小时已知总量相等；缺观测桶保留null，空桶0。小时固定3600，不以有数据桶数缩短分母。核对线上prompt与本地prompt差异，不能据两率差直接承诺SSD/路由收益。
7. 用户原四入口HTML中核对：DS明确缺源cached但显示独立ideal；GLM冲突明确原因但显示独立real/小时量；有效cached=0显示真实0%；P=0显示无有效输入；空桶0和缺失断点区分。保存实际DOM/截图与精确API同一run/UUID映射，不能用200或completed代替用户验收。
8. 唯一Markdown回传，嵌9制品完整UUID矩阵、18SHA、冲突边界、守恒核验、关键源码、执行命令及真实正反例（只脱敏必要信息）。不得只引用现场外部JSON/脚本作为完整证据。源数据补齐仍是数据依赖；前端、完整E2E、现场结果分别验收。

## 契约工具窗口闭环（2026-11-03追加，最新）

依据总设计师收到候选后的直接授权，本轮仅修改契约工具和新增测试，业务源码/指标/replay不动。此前旧工具失败日志保留；上文待安排工具窗口事项现已完成。检查升级为旧冻结兼容与新扩展完整检查，候选仍待独立验收冻结。

精确新增/修改文件及 SHA256：

| 文件 | SHA256 |
| --- | --- |
| scripts/contracts/validate_ma_contract.py（修改） | 3b8ddd4754db8d474d44c3fa9cb5c0e7411191f3796538b6e1808c31a0cb92fd |
| scripts/contracts/validate_ma_availability.py（新增） | 8e11108cc134a975447df26301b529bea71f11114be668c0f84b674c1f29ea06 |
| tests/unit/ma/test_contract_tools.py（新增） | 8cdca6db012fadb4c7efd423582d0f06919b151be3ec0bea5eef4a03d9a9814f |

原manifest逐文件SHA断言和旧2正例/4负例、frontend.examples DTO验证全部保留；另外固定原manifest自身SHA b29e3edfac5ce5fc6cf9d46f11df0b0cbd71b1738bb898ef3b423c309faa81e9，防止重新生成manifest掩盖冻结字节变化。旧Schema完全相等，旧OpenAPI路径/操作/组件/元信息逐项相等。运行时完整OpenAPI必须等于candidate.openapi.json，新增路径集合必须恰为availability且仅GET；扩展完整DTO Schema必须等于运行时生成。9样例逐个DTO验证并核对原快照片段的identity、coverage、独立/paired样本/分子/分母、小时及12桶，另8个严格/null/0/未知原因/额外字段负例必须拒绝。没有放宽产品Schema。

旧工具--write现在明确退出2，禁止覆盖冻结目录及manifest；新工具只读，无write模式。本轮没有运行候选生成器改写制品。原冻结目录所有文件字节与原manifest一致，原5源码+1测试组合身份仍为15194270d39e4e51950c83fd10d7694a3282d9c96a0b9ffbfd7c882b3d2f96f5。

实际执行（项目根目录）及结果：

- `.venv/bin/python scripts/contracts/validate_ma_contract.py`：通过，覆盖旧契约/身份、完整扩展、旧样例和严格负例；日志artifacts/validation/monitoring/v2-ma/HV2-R1/contract-combined.txt。
- `.venv/bin/python scripts/contracts/validate_ma_availability.py`：通过，独立入口也先核对旧身份与兼容，再检查扩展；日志同目录contract-extension.txt。
- `.venv/bin/pytest tests/unit/ma/test_contract_tools.py -q`：13 passed in 1.52s；日志同目录tool-tests.txt。变异覆盖旧Schema/path/component/metadata漂移、候选route/DTO/sample漂移、同时伪造runtime与candidate的额外未声明路由、manifest改字节、冻结文件改字节及--write拒绝；正向检查前后全契约JSON SHA不变。
- `.venv/bin/ruff check scripts/contracts/validate_ma_contract.py scripts/contracts/validate_ma_availability.py tests/unit/ma/test_contract_tools.py`：通过；同路径ruff format --check：3 files already formatted。

检查器通过仅代表工具检查结果，不代表总设计师已独立通过或冻结候选。未提交push、监听服务、打包、改共享总文档。唯一工具窗口工作完成，交回总设计师收口。
## 2026-11-03 总设计师独立验收冻结（最新状态）

V2总设计师01a1800e-80b4-7400-a78b-a84f5b6e888d已明确通知：MA后端及契约工具独立通过，涵盖66项本线、13项工具，以及额外混合UUID原因隔离、0/null、桶与小时守恒核验。冻结清单：docs/tasks/delivery/HV2_MA_FREEZE_20261103.json；组合身份9b48fb244963ce153b009a9a2d0d9050d084bd6c1bb43eec27ddf49f313fd9fa。此状态覆盖前文候选待冻结的历史描述；冻结内容保持原字节。

本次冻结范围为MA新增availability资源及兼容契约工具，原指标和预热策略保持。源码窗口、工具窗口均已关闭；监控前端当前仅接入MA。本线转为等待问题后的归口维护，不再自行测试、提交/push或监听服务。后端独立验收不代表前端或华为现场验收；DS真实观测缺失、GLM真实冲突边界及现场完整证据仍待补证，不代签通过。