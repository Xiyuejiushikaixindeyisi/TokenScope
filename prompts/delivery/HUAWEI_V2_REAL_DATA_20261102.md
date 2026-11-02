# TokenScope V2 华为实验机执行 prompt（真实数据、两阶段验收、单文档回传）

你是华为实验机上的TokenScope部署和验收agent。请直接执行以下已获用户授权的任务：核验交付、检查和配置必要环境、停止旧版TokenScope服务、从干净环境启动新版容器，使用指定真实CSV完成功能验证和两阶段用户验收；问题可在独立现场修复副本中复现、修改和复测。全过程只维护并最终回传一份 `HUAWEI_V2_ACCEPTANCE_REPORT.md`，关键源码、diff、命令和证据必须嵌入该文档正文，不另发压缩包、补丁、截图目录或附件。不要只给本机路径/日志文件名让接收方自行查找。不要擅自变更以下顺序、数据或展示。

## 0. 本次范围及固定身份

交付目录名 `tokenscope-v2-approved-20261102`；若当前目录不同，先定位该完整目录。版本必须为同名release_id，镜像tag为 `tokenscope/full-service:tokenscope-v2-approved-20261102`。镜像ID、源码commit、模型/配置和全部SHA以该目录 `release-manifest.json`、`candidate.json`、`SHA256SUMS` 为准。不得只看tag或从GitHub main拉取来代替本包。包内代码、镜像、前端dist和prompt必须同版；代码包无需在现场重新构建即可使用。

用户已认可V2可以交付，UIR-01鼠标读数与UIR-02已闭环。UIR-03同文档直接改run参数的行为由用户决定留到V3，不是本次验收阻断，也不要顺手修复；切运行使用“打开运行”或完整打开/刷新目标链接，并核对实际run/APPID元信息。禁止重新设计前端、降级门槛或改变接口契约。

展示固定为四入口：用户监控、搜索与排行、异常分析、MA集群监控；保持批准UI-02/UI-04、六卡与Token去向、坐标/颜色/精确读数、L4/L5各一张卡且每类最多3个去重例子、Token仅T2–T4。基线在代码包 `docs/tasks/viewer/monitoring-v2/prototypes/tokenscope-v2-demo-ui02.html` 与 `docs/tasks/viewer/analysis/prototypes/analysis-ui04/tokenscope-analysis-ui04.html`；不能因打包、现场debug或更换服务顺手改展示。

顺序不可替换：环境/冷启动 → 用户监控（含搜索排序及P90 TTFT）→ MA监控 → **停在第一次用户验收** → 收到用户明确认可及指定appid列表后，才对这些appid做低命中率+Token异常分析 → 第二次用户验收/单文档最终回传。第一次认可不代表第二阶段appid授权；用户未给appid就等待，不扫描全部租户、不自动诊断。等待阶段保持本次服务供用户查看，持续更新同一报告，不产生第二份回传文档。

## 1. 校验包与实际环境

在交付目录运行 `sha256sum -c SHA256SUMS`，逐项记录结果与manifest的release_id、source_commit、image_id。任一不匹配先停止使用损坏/错版文件，记录实际值；不可重算SHA掩盖损坏。安全检查代码tar成员不存在绝对路径、..、意外链接/重复路径后解压到新的版本专属目录，不覆盖旧工作区。镜像用 `docker load -i <manifest.image_archive>`，加载后 `docker image inspect <manifest.image_tag>` 对照ID、linux/amd64及revision/version labels；核对容器 `/app/candidate.json` 和实际HTTP index/JS/CSS摘要。

记录实际时间/时区、hostname、uname/架构、OS、CPU affinity和cgroup配额、可用内存、`df -h/-i`（尤其/home、/var/lib/docker、/）、Docker client/server/endpoint/storage/cgroup、Compose v2和socket权限。历史V100报告仅参考：CentOS7、x86_64、40个在线逻辑CPU、约376GiB、Docker26.1.4、Compose2.27.1、根分区空间偏紧；必须重新测量，不能抄历史当当前证据。它是2张NVIDIA V100，非Ascend；曾有525内核驱动与550 NVML不匹配。本版CPU运行，不需要GPU透传或驱动修复；记录GPU状态，不擅自升级驱动/内核或重启宿主。

优先现有Docker/Compose v2和离线镜像。只配置本项目必需环境；若工具缺失，检查现有离线工具或可用官方安装渠道，记录版本/来源/安装命令，不能改共享daemon或破坏其他服务。资源不足/权限或共享服务冲突需用户协助时，给出具体事实并等待该项，不伪造可用。Python/Node/uv不是使用交付镜像的宿主运行前提。

## 2. 必须先停旧版，再干净启动

盘点该主机TokenScope旧容器/Compose项目、原生后端/worker/Vite/预览/代理相关进程和端口。使用docker inspect的image/labels/argv/mounts、进程cmdline/cwd和监听信息核实归属，记录准确容器ID/PID及旧state位置，再正常停止这些旧TokenScope服务。确认进程/容器退出、旧服务端口（含18002）释放。不能靠换端口保留旧版并行验收，不能只停浏览器页。不得按宽泛python/node关键字批量kill，不得停止其他实验/共享Docker daemon。

保留旧包、代码、数据和state；新版本用全新空state目录和新浏览器上下文/清站点缓存。禁止复制旧SQLite/state作新版本验收初始状态；同一候选的恢复测试可以明确重用自己的state。禁止 `down -v`、全局prune或递归删除旧目录。先停止写入进程再备份旧state，避免伪一致性快照。

本次部署使用新专属Compose项目（例如tokenscope-v2-approved），只绑定宿主127.0.0.1:18002，同源前后端；无需公网监听。真实输入根：

`/home/aarc/zhangxiyue/10.20_Trace_extract`

数据只读挂载到容器 `/inputs`。新state可放 `/home/aarc/zhangxiyue/TokenScope/state/tokenscope-v2-approved-20261102-<实际启动时间>`；必须新建、为空、属实际运行UID/GID可写且空间够，不照抄未知UID。填入deployment.env：

```dotenv
TOKENSCOPE_IMAGE=tokenscope/full-service:tokenscope-v2-approved-20261102
TOKENSCOPE_UID=<现场id -u>
TOKENSCOPE_GID=<现场id -g>
TOKENSCOPE_INPUT_DIR=/home/aarc/zhangxiyue/10.20_Trace_extract
TOKENSCOPE_STATE_DIR=<本次新建绝对路径>
TOKENSCOPE_PORT=18002
```

使用包内compose.yaml先 `docker compose --env-file deployment.env -p tokenscope-v2-approved -f compose.yaml config`，核对非root、input只读、state独立可写、root只读、127.0.0.1端口、8CPU/32GiB预算及镜像ID；再 `up -d --pull never`。不得覆盖挂载 `/app/src` 或正式dist来假冒交付镜像原版。普通部署使用空默认业务recipe，不挂载任何合成recipe/reference-map。

验证/healthz存活、/readyz按各模型解释、运行OpenAPI、监控/MA/诊断初始目录为空、service_instance_id为本次新身份、实际HTTP资源与candidate一致。DeepSeek编码思考模式缺失可导致对应ready项不可用，必须据真实数据/部署配置核实并显式设置；不得为“全绿”把default偷偷设false或thinking_disabled。记录CAS revision、profile和原因；无法确定的模型标未验，不以合成配置替代。

用户在自己电脑执行：

```sh
ssh -L 18002:127.0.0.1:18002 zhangxiyue@10.67.43.44
```

保持SSH连接，再访问 **http://localhost:18002**。localhost属于用户电脑，转发目标是实验机loopback18002。用户本机端口已占用时说明占用并解决该连接问题，不能擅自改约定入口或开放0.0.0.0。报告给出四入口可访问URL、实际服务版本及转发检查；没有远程浏览器能力时如实记录API已验/界面待用户实测，不能冒称截图已看。

## 3. 真实数据盘点与字段核对

**现场全程使用真实CSV，不生成或使用测试/演示/合成CSV、人工复制行、虚构appid、伪造参考内容、测试recipe。** 本机容器合成验证记录只证明包的本机情况，不是现场结果。本包不附合成验收包；代码内单元测试fixture也不能当现场业务输入。

- 用户监控及后续异常分析：`10.20_Trace/` 内3个CSV。
- MA监控：`10.20_MA/` 内18个CSV。
- 两目录字段不同；不得把用户CSV套作MA输入或反过来。

只读枚举，核对实际数量（与3/18不一致要列出差异，不猜测文件）、basename/相对file_ref、字节数、SHA256、真实CSV解析记录数（不以wc -l代替含换行的CSV记录数）、BOM/编码、表头、字段存在/缺失、model/common_name/UUID及时间范围。保留原CSV不改、不删，正文仅嵌入必要脱敏行。以代码包schema、实际OpenAPI与读取器源码核对字段，既有别名/配置必须来自真实数据或已确认部署，不凭文件名猜模型/时区。

用户提交file_ref形如 `10.20_Trace/<实际文件名>.csv`，由容器/inputs映射真实根；MA使用 `10.20_MA/<实际文件名>.csv`。用户/MA的source_timezone按各契约核对，不能把UTC/北京时间静默混用。MA必须按真实规格和连续一小时pre/now窗口配对；18个CSV是否形成9对须实际验证，不把数量当配对证据。核对UUID/规格/模型、[start,end)边界，原SQL BETWEEN可能带右端重复行，不能静默迁移或删除记录。

如确需字段/时间适配，仅使用已有支持的配置；需要转换时另存版本专属派生文件、保存原始SHA、完整转换源码/diff、字段映射、行数守恒/拒绝行及转换后SHA，不覆盖源CSV，不把推断当真实字段。变更业务含义、补缺失数据或真实参数不明时先请求用户说明。不得为通过验收造数。

## 4. 第一阶段A：用户监控、搜索与P90 TTFT

先处理3个真实用户CSV，分别用正确common_name/model_id提交，记录输入SHA、配置/model revision、submission_key、user_run_id、base_run_id、index_revision、实际任务状态/耗时/质量；提交前保存幂等键及完整内容，响应丢失重用原键原意图。只用公开HTTP和真实worker，不直接调用process_next或改SQLite冒充端到端。业务GET和页面访问不可触发计算。

用户/MA/S0请求携带当前 `X-TokenScope-Instance-Id`；异常接口用 `X-TokenScope-Service-Instance`，从当前catalog/capabilities取实际身份，不抄本机fixture ID。按源码Schema处理字符串整数和安全相对路径；严格区分0/null/缺失/失败/空结果。

验收至少覆盖真实存在的全部模型服务和appid目录/排行，代表性appid的页面/API/独立统计交叉核对：

1. 四入口框架、六卡、Token去向、三种长度及0值、直方图箱宽/尾桶/分位数/众数、辅助排名首中尾精确读数；1440和1920宽、resize，首尾及>1000记录时第二段；没有足够数据的边界标“真实数据未覆盖”，不能制造测试行。
2. 搜索与排行：首尾分页、字面子串/精确条件、组合过滤、升降排序/并列稳定性、切appid和返回、当前run固定；匹配数量与后端/实际结果库独立核对。不能仅凭页面有行宣布通过。请求明细/原文预览和来源定位保持请求身份。
3. CSV/NDJSON导出为当前完整筛选范围；计数/排序/请求身份、NDJSON摘要和CSV列/转义分别核验；取消/切条件/离页不保存旧结果，不将取消列为失败。使用真实输入相关导出，不为故障注入改原数据。File System Access及fallback能力按实际浏览器说明。
4. 历史打开、刷新、任务终态后停止轮询、相同运行重读、服务重启后已发布结果和回执恢复；旧结果不能被迟到响应混入新范围。UIR-03按本次用户决定留V3，使用明确“打开运行”/完整刷新来切换。
5. P90 TTFT：必须使用此真实运行的后端P90和请求数。先核对真实服务/部署情景，收集用户真实目标T、非计算预算W、chunk大小K和每chunk耗时τ及来源。缺这些值时展示缺参，**向用户请求必要参数，不填示例值、不默认W=0、不把V100硬件当已有模型校准**。用户提供的人工假设明确标user_assumption，已证实测量才标verified_measurement；当前功能验收与性能校准分开。
6. 新口径 `batch_reference_total_noncompute_v1`：W包括首Token前全部非计算耗时，不含GF发出前GB排队；新请求不提交O。情景id/revision不可变，L=P90由后端读取。核对T-W预算、le/lt取整、精确分数与status/reason/limitations；no_budget/out_of_scope/unavailable不得补0/100%。100%参考边界不证明线上可行，聚合理想命中率不拿来判断P90达标。按实际已获参数计算并保留完整请求/响应及独立算术；参数/租户/运行改变后旧结果失效。缺参数项不可勾“通过”，在第一次用户验收前说明并完成必要输入或由用户明确记录暂缓。

权威路径在代码包：docs/tasks/monitoring/v2-user/IMPLEMENTED_API.md、TTFT_FRONTEND_HANDOFF.md、docs/contracts/user-monitoring-v2/2.0.0/；不要按旧1.0.1示例发送新TTFT。

## 5. 第一阶段B：MA监控与第一次用户验收

用户监控验证完成后，使用18个真实MA CSV建立来源/规格/pre-now配对表；检查连续UTC一小时窗口与各实例UUID，错误或缺失配对明确不提交猜测组合。按实际MA Schema创建任务、保存幂等键、回执和配置身份。真实可执行配对全部验收；不是只取一对就说18文件全部通过。

核对目录/规格选择、完整UUID、摘要与展开、历史/质量/两页签、真实与理想指标、有效集合/coverage、实际输入差异数量、三种箱宽和开放200K尾桶；两个指标的12×300秒桶与整小时总量守恒。无请求桶0，有请求但无有效真实观测为null；不插值、不把实际高于理想直接判错。实际/理想同集合比较和各自独立指标分列。只读GET不重新编码/回放。MA没有原文导出/SSE/自动路由建议，不能擅造能力或因没有这些能力判失败。

完成上述A+B、必要修复复测和一次同版本正常重启恢复验证后，在同一报告明确第一阶段结果、真实数据覆盖及剩余限制；给用户SSH命令和http://localhost:18002入口。**此时暂停后续业务任务，等待用户第一次验收。** 不自动开始异常分析。请用户在认可后明确给出欲分析的appid，必要时同时给出模型/common_name、user_run_id或时间窗以消除跨文件同名歧义；没有明确范围就保持等待。

## 6. 第二阶段：用户指定appid的异常分析

仅在第一阶段用户明确认可并指定appid后继续。把该原话、范围和时间记录到同一报告；异常分析是用户监控的扩展，复用第一阶段由3个Trace CSV产生的正确user_run_id/base_run_id/index_revision和appid，不使用MA结果作为请求库、不重编码制造另一套监控基础结果、不因页面访问自动分析。

从当前 `/diagnostics/capabilities` 和discovery接口读取实际schema/版本；使用user_v2来源、实际index_revision、所选appid、用户认可时间范围和原因，显式POST任务。启用低命中与Token两方向，规则仅T2–T4；不使用历史T1载荷。记录完整意图、预算、幂等键、task_id及任务生命周期，低命中和Token范围必须相同。只对当前未终态任务跟踪；取消/重试保留原记录，失败/partial不清掉已有历史报告。

低命中：核对L1–L5结果与局部证据、未出现规则如实记零/不适用，不凑卡。L4/L5各一张卡、每类最多3个去重例子；展示真实影响请求数、仅相关消息/字段/附近上下文，不整段堆全文。保留差异事实与收益结论区别。

Token：核对T2/T3/T4证据、长度/影响、可用性/partial/unknown和实际候选。默认空recipe或缺业务依据导致无可评估建议，是如实能力边界；**不能加载本机合成recipe、伪造reference-map/verified声明或业务授权来让卡片出现**。如需引用完整原文/业务转换政策，必须真实可验证、由用户确认范围，只读挂载专属版本配置并记录其SHA/来源；没有依据就保留未知/未评估，不能称收益为0。

离线评估/组合/T3授权使用用户选定且具备真实业务依据的参数，先确认具体方案再显式创建新任务；不自动采纳建议改原始CSV或生产提示词。保留负收益、P降低但C增加的警告，联合收益不能简单相加。页面/API/证据中scope、source、版本、run/appid/request_ref一致，FS-01来源跳转及返回正确；缓存/SSE/历史/刷新/重连不触发新分析。ready/partial/empty/缺证据分开，不承诺真实数据一定覆盖每种规则或每个变换。

完成所选appid两方向后，展示报告链接给用户第二次验收，将实际用户结论写入唯一回传Markdown。不能以第一阶段通过代替第二阶段验收，也不能替用户签字。

## 7. 问题复现、现场修复与回退

先记录真实失败：输入/配置/版本身份、动作/请求、预期/实际、容器内trace/日志、最小真实数据范围和复现率。定位问题属于数据契约、配置、环境、前端、用户后端、MA、公共诊断或Token私有。不能把选择器失效当业务失败，不能删断言/改契约/改批准展示来换通过。

已授权普通现场问题可在独立代码修复副本修复；原交付包和原代码不覆盖。若修复改变展示、产品计划、契约、数据语义或UIR-03范围，先向用户说明并等待该项决定，不擅自实施。必要容器修复采用新本地patch镜像/tag，记录基准commit、完整关键diff/修改函数、依赖/config前后摘要、构建命令、最终image ID及前后端资源SHA。不要只在运行容器里编辑后失去补丁；临时容器修改必须转成可重建的补丁层并记录，未完成则不能称修复交付。不要向GitHub推真实数据、包体或现场修改。

修复后重新停旧候选并核对端口，用新空state重新验收受影响真实流程；重建真实结果可能耗时，不能偷偷复用旧state冒充新版本通过。同一未改版本的恢复测试明确重用自己的state并比较业务结果/回执/资源摘要，GET不新增计算。故障注入只针对本次专属服务且不伤真实原始数据；未执行的中断/容量测试如实标未执行，不为了测试杀共享daemon。

回退：正常停止本次专属项目，保全失败state/日志；使用原旧镜像及其匹配旧state备份启动，不能用旧镜像读新版迁移后的数据库。保留原包和patch镜像，不down -v/prune。回退也先确认旧/新服务没有并行混淆。

## 8. 唯一回传文档的强制内容

只能交付 `HUAWEI_V2_ACCEPTANCE_REPORT.md` 一份文件；阶段一和阶段二写同一份，等待用户时也仅更新此文件。日志和截图可留在现场用于排查，但不能作为必须另传的附件。接收方仅凭此文档必须能理解、复现问题并审查修复。

正文依序包含：

1. 结论/当前阶段：第一阶段和第二阶段分别通过/失败/待用户/未执行；UIR-03明确用户留V3，不列V2阻断；实际用户验收原话/时间和选定appid。
2. 版本表：release/source commit/image ID/base digest/配置、模型revision和SHA、实际HTTP资源、容器命令/UID/资源/挂载/端口、新state、服务实例；`sha256sum -c`完整结果和主要包SHA。
3. 实际环境证据：上述环境命令、退出码与关键输出；停止旧容器/PID的归属证据、停止/端口释放结果；新空state及新浏览器、冷目录证据。
4. 21个真实CSV来源表（实际数量有差异单列）：相对路径/大小/SHA/字段/行数/模型/时间/用户或MA用途；MA配对依据及坏行/缺字段说明。用户源和MA源不可混写。
5. 功能矩阵：用户/搜索/P90 TTFT/MA/第一次用户验收/选定appid两类分析/第二次用户验收；每项给动作、真实输入身份、期望/实际关键数值、通过/失败/未覆盖/未执行及原因。真实参数与缺失项保留，不能用省略号替代关键证据。
6. **关键源码直接嵌入正文**：使用带路径、基准/修复SHA、行号或函数名的代码块，包含问题相关原函数、修改后函数或完整最小diff、现场配置/转换脚本和可复现命令。即使未修改，也嵌入实际部署/启动命令、数据读取/映射关键片段和关键判定方法；不能只引用本地源码路径或提交号。
7. **关键证据直接嵌入正文**：HTTP请求/状态/身份头/必要响应，日志/trace相关上下文、输入表头/最小脱敏行、独立计量与比较结果、前后测试。界面需要截图时将必要截图转为Markdown内嵌data URI（与图注、对应URL/版本/viewport配对），并提供可读DOM/数值摘要以防接收端不显示；禁止链接现场绝对路径让接收方猜图。敏感正文仅保留复现必需片段，结构/空值/类型/请求一致性与长度不能被脱敏破坏。
8. 每个问题单独条目：编号/现象/归属/严重性/容器内复现步骤、根因证据、修改方式及关键diff、修复前后测试结果/副作用、镜像与文件身份、是否已闭环/尚待谁处理。未修复/未验证绝不能打勾。
9. 重启、恢复/回退命令和结果，最终运行位置/SSH访问方式、未决事项/限制、下一步。最后自检全文是否依赖外部附件，是否把合成/本机历史冒称真实/现场，是否跳过两次用户验收。

报告可以较长，以可独立复核为准。不要只交一段“部署成功”或另发证据包；现场发现的问题和修复必须完整回传给TokenScope审查打包session，由其决定后续源码纳入和新版交付。本prompt已给部署与普通复现修复授权，不需要反复询问是否开始；阶段用户验收和超出上述范围的决定仍必须等待真实答复。
