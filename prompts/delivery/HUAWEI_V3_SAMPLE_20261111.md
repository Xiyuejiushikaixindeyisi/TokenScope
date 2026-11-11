# 华为执行prompt：tokenscope-v3-sample-20261111（执行说明r2）

本文件是交付后的现场执行说明，不代表本地已在华为执行。用户交付本包并确认现场执行后才开始。本版仅小样本低命中，显式全量延期，自动full禁止；Token新分析休眠，旧结果可读。不得照抄旧V2两类分析一起执行的步骤。不得修改产品代码绕过问题，失败返回同一V3开发会话处理并形成新候选。

## 最新用户批准目标（r2，覆盖旧包内历史执行说明）

本轮服务于真实业务验收、次日向同事展示和与业务方协作修改请求。用户监控、搜索排行、MA已有约15万条真实数据的分析结果已获用户认可：直接复用，只核新版前端展示、模型/用户切换、固定链接和既有功能。禁止重新导入、重新编码、重新计算这些监控成果或启动新的监控/MA run；浏览/刷新不得触发计算。结果缺失时先查旧state、挂载、目录、身份和访问链路，不得用重跑补齐。缺失无法恢复则记录阻断并报告。

旧异常分析结果允许弃用，不要求逐条迁移展示或重验。必须保护原始真实CSV、用户/MA已完成成果、默认绑定、固定链接和旧state一致备份。仅在有已支持、可证明隔离的操作时清理新版工作副本中的旧异常记录；不得手工删共享数据库表、删整个state或影响监控关联。无安全独立清理能力时保留历史记录，明确本次五组新任务及链接，不以清理阻塞分析。该许可不启动Token新分析。

先以只读方式展示已有用户监控和MA，取得第一次用户确认，再按BUS01到BUS05逐一分析。使用原真实来源及自动有界A/B样本；不做15万条全量重算。每组完成后即核前端结果并保存可直接演示的URL。最终保留新版服务供用户通过SSH18002审阅，记录容器/版本/URL，不在结束时自行停掉演示服务；出现安全或资源故障则停止受影响任务并报告。

前端必须能看到：问题位置（角色/JSON pointer/请求片段）、可执行修改方式与前后对照、样本修改前后命中率及提升百分点、A/B范围与完整性、业务语义风险/待业务确认项。建议基于当前实现实际发现，可包括动态字段、tools或messages；不得为过关强造clock或正收益，不承诺未实现的探测能力。不改真实请求或替业务方应用方案。方案缺失、页面不能展示、无适用、负收益和预算不足分别记录；不得手工写入结果或仅在回传文档编造页面不存在的方案。样本收益不代表全量、线上吞吐、TTFT、账单或质量收益。

## 包校验、环境与已有成果保护（先执行）

1. 在交付目录运行`sha256sum -c SHA256SUMS`，全部通过。读取release-manifest.json、candidate.json、VERSION.json和CONTAINER_VALIDATION.md，记录实际release_id/source_commit/image_id/base_image、源码/前端/资产身份。版本为tokenscope-v3-sample-20261111，以清单填写commit与image ID，不使用开发旧PID/实例/state。不要修改文件后继续使用原SHA冒充同包。
2. 记录实际主机CPU、RAM、可用磁盘、Docker/Compose、cgroup、UID/GID、32GiB容器和worker RLIMIT_AS预算。历史V100不代表Ascend；本版CPU运行，不依赖GPU/NVML。命令不存在则先核现有受控安装渠道/权限和离线资源，不擅自变更宿主驱动或假定联网可安装。本机Linux/amd64，不在其他架构强行运行。
3. 盘点归属明确的旧TokenScope服务/worker/前端/容器、镜像、挂载、state/input、端口、固定链接与版本。先GET保存用户全部分页目录/默认绑定、旧异常目录及必要身份摘要（可弃用，不要求逐份重验）、MA结果身份。正常停止本项目旧实例（例如已确认的旧compose项目`docker compose ... stop`），验证进程退出/18002释放。不得全局kill/prune/down -v或删旧包/state/日志；归属不明先核实。旧源数据只读，停后做一致备份并核SHA；不能复制运行中零散SQLite当一致备份。
4. 新建排他attempt工作目录，所有路径落在批准TokenScope工作根，拒绝复用旧attempt；原state/inputs/证据不得作为可写测试目录。先使用独立空state/新浏览器验证新版冷启动/资源身份；旧结果兼容须再停止该临时实例，用停机后的一致旧state**隔离副本**启新版，不写原件、不合并两套新旧数据库、不悄悄初始化覆盖旧state。先对副本核用户/MA旧目录、默认绑定、监控报告摘要和固定链接。如果用户/MA结果无法兼容或旧state缺失，停止并报告，不删监控结果或改默认掩盖；异常旧结果按r2弃用边界处理。
5. 冷启动与历史兼容阶段串行，只保留一套实例占18002。选择经过核验的副本作为后续新版本可写state，保留原始旧state可回退；input映射维持原来容器内/inputs引用，实际权限/mount不同先核。不因新版本重跑全量诊断。原四入口及L4/L5保持。

## 装载与启动（按实际路径填写）

代码包tokenscope-v3-sample-20261111-code.tar.gz用于审计/必要重建；解压到新目录，不覆盖现场旧源码。镜像优先load，无需联网构建或现场推镜像仓库：

```bash
docker load -i tokenscope-v3-sample-20261111-image.tar.gz
docker image inspect tokenscope/full-service:tokenscope-v3-sample-20261111
cp deployment.env.example deployment.env
```

手工填写deployment.env：TOKENSCOPE_IMAGE=tokenscope/full-service:tokenscope-v3-sample-20261111，TOKENSCOPE_UID/GID为实际非root用户，TOKENSCOPE_INPUT_DIR为既有真实input挂载根的核实路径，TOKENSCOPE_STATE_DIR为本attempt空state或已验证一致旧state副本，TOKENSCOPE_PORT=18002。目录提前创建，state属主正确；不chmod777原数据，不清空已有目录。

```bash
docker compose --env-file deployment.env -p tokenscope-v3-sample-20261111 -f compose.yaml config
docker compose --env-file deployment.env -p tokenscope-v3-sample-20261111 -f compose.yaml up -d --pull never
curl --fail http://127.0.0.1:18002/healthz
curl --fail http://127.0.0.1:18002/version
curl --fail http://127.0.0.1:18002/diagnostics/v3/capabilities
```

核对docker inspect的image_id、Labels revision/version与manifest一致；核容器candidate.json及HTTP静态文件摘要。healthz仅存活，readyz按模型解释。Compose应非root、只读rootfs/input、独立state、8CPU/32GiB、仅127.0.0.1:18002。不要通过加内存、提高candidate_limit、预置clock/recipe、人工裁小CSV或开启full掩盖资源问题。

真实来源仅用现场已授权数据：/home/aarc/zhangxiyue/10.20_Trace_extract/10.20_Trace/的3CSV供用户及低命中，10.20_MA/18CSV供MA；核存在、schema、完整SHA和配置，不把Trace与MA混用，不夹带ICSL构造数据或任何合成fixture。模型制品与规格映射按实际目录/接口确认，不用清单字符串猜别名。TTFT既有用户参数Qwen1s、GLM2.7s、DeepSeek2.6s，chunk8192、未校准；以现场对应模型身份核对，不默补缺参数。

SSH仍为`ssh -L 18002:127.0.0.1:18002 zhangxiyue@10.67.43.44`，用户电脑访问http://localhost:18002。按下文两阶段人工验收执行；五BUS已指定，但仍须等第一次人工确认后再分析，不能借列出appid越过等待。

## 回退与失败处理

核现场旧镜像/包和**配套旧state**实际存在才承诺回退。回退：停止本次专属compose→封存本次state/失败证据→恢复旧image与匹配旧state/input映射→同18002启动旧服务→核版本、目录和固定链接。旧版本不得打开新版可写state。不删除此次失败目录，不覆盖原包；缺介质明确回退不可用。

发生问题先复现并嵌关键源码/配置/HTTP/错误，记录处理方式与复测；本轮产品修复回传开发，不擅自改契约/展示/数据或写结果表。允许核实路径/属主等部署配置；任何影响旧数据或超范围动作先报告。

以下现场门槛来自已收口的开发/独立验收交接，提及仓库文档只是来源，执行所需核心要求已完整列出。旧“暂不打包”状态已被本轮用户授权覆盖；现场执行仍需用户交付后的安排。

## 3. 随五组真实分析记录资源（不另起全量监控计算）

资源记录伴随五组分析进行，不作为另起全量任务或延迟演示的理由。取消专项使用独立任务，安排在正常结果保存后，不取消已完成的演示任务；若未执行明确NOT_RUN，不伪报通过。在实际大父范围上不填手动sample_limit，观察自动选A/B及正常完成；记录父范围总数、模型固定开销、profile/预算、自动缩样理由、A/B成员数/连续性/不重叠digest、排除及attempt。计数区分全源流式校验I/O、入选正文读取/解析/编码、发现/评估/发布。

通过：得到可用诊断及适用方案实算，OOM/mem_limit/内存强杀=0；只返回预算不足/超时/保护性kill不能算通过。记录进程树/容器峰值、硬控制类型/范围/单位、各阶段耗时、终态和退出码；RSS峰值与RLIMIT_AS分别列。不得用结束时内存或短合成输入代替真实峰值。单条或模型无法装入的环境边界单列证据，普通总量过大失败保持OPEN。

现场响应/取消沿用TESTS §4：20次health/receipt各自nearest-rank P95≤1s且全成功；取消HTTP≤1s、任务子进程树≤5s结束或确认已成功提交终态，API持续可用。取消专用新attempt不污染五组正常完成结果。记录实测而非复抄本地数字。

## 4. 五组实际原因→可执行方案→样本实算→前端

| ID | 模型 | appid | 初始状态 |
| --- | --- | --- | --- |
| BUS01 | DeepSeek-V4-Flash-0731 | S00000000000000000000000000000773 | NOT_RUN |
| BUS02 | DeepSeek-V4-Flash-0731 | S010320 | NOT_RUN |
| BUS03 | DeepSeek-V4-Flash-0731 | com.huawei.mbs.ilegal.ioc | NOT_RUN |
| BUS04 | DeepSeek-V4-Flash-0731 | com.huawei.newalliance | NOT_RUN |
| BUS05 | Qwen3.6-27B | com.huawei.aidp_dg06 | NOT_RUN |

逐组要求：

- 正常自动发现真实适用原因，给请求对/角色/JSON pointer/块位置/受保护原值及方案来源；不要求每组必须有clock。没有clock不构成失败；无适用方案如实展示并交业务判断，不等同已获得优化收益。L4/L5实际证据保留。
- 前端显示实际方案的修改前后与作用范围。仅在确实发现合格clock且该方案适用时展示其内部替换为同一`NORMALIZED`；其他方案按真实变换展示，不套用clock模板。原始请求不改写。recipe先由A冻结，B不参与调参；A/B连续原顺序、不重叠、各自ledger，不将两窗拼接或混分母。
- 各窗记录N、匹配N、修改N、before/after P/H/C（逐请求及聚合满足P=H+C）、H/P与提升百分点 `100*(H_after/P_after-H_before/P_before)`；各用自身P，P=0为不可用。封存报告、前端、业务摘要同一evaluation与数值。
- 在同一冻结成员/编码/缓存配置上用独立字面前缀核算核对整数与比率，注明独立算法与复用编码/变换的边界。记录实际独立核算方式/结果，不能只看生产报告自称独立通过。
- 页面保留零/负收益；Qwen实际配置若缓存关闭等导致零值，先核实说明，不为过关擅改配置。无适用、无收益、未评估、预算不足、取消、B不足分别记录。A已完成可展示；缺B则该组未关闭，除非用户明确接受该组具体限制。
- 对原因证据上限（如CAUSE_EVIDENCE_TRUNCATED）明确发现覆盖partial；完整窗口实算可以独立complete，不把它说成全部原因已覆盖。
- 给五组各自真实截图/URL、方案/精确局部证据和参考值。各类修改需业务确认；若采用时间固定化，明确它改变时间感知；不承诺业务无损、答案质量、TTFT/账单收益或全量收益。无需复现旧报告正收益幅度。

## 5. 唯一Markdown回传模板

只回传**一份自包含Markdown**，关键命令、HTTP/页面证据、摘要、日志摘录、失败与复测直接嵌正文；可嵌截图并配文字，不要求额外证据包或让审核者访问现场绝对路径才能理解。原始现场证据本地保留，真实正文按授权最小披露。

```markdown
# 华为V3小样本验收回传
- 执行授权/时间/执行人；第一次与第二次人工验收：状态、用户确认依据
- 实际主机/资源/限制；候选commit+镜像/包/dist/模型资产摘要及本地候选映射
- 来源路径/文件数/摘要/时间范围；监控/MA配置、实际命令与结果
- 旧服务停止、端口释放、新state/浏览器、唯一实例身份；输出路径排他创建检查

## AC-MEM（PASS/FAIL/NOT_RUN及原因）
父范围N、入选A/B N与digest、profile/缩样理由/排除、各阶段I/O/耗时/内存峰值、退出码、OOM/mem_limit/强杀计数；health/receipt原始延迟与P95、取消时序。

## BUS01（BUS02–05逐组同样填写）
实际模型revision/模板/cache配置、appid、来源scope；自动提交JSON/关键HTTP。
请求对/逻辑字段/实际原因、原文→建议修改及语义风险；finding/recipe/plan/evaluation/report摘要。只有实际clock方案才填写NORMALIZED。
| 窗 | N/匹配/修改 | before P/H/C | after P/H/C | before% | after% | 差值pp | 完整性/复核 |
| A | 实填 | 实填 | 实填 | 实填 | 实填 | 实填 | 实填 |
| B | 实填 | 实填 | 实填 | 实填 | 实填 | 实填 | 实填 |
独立复算方法/结果；页面URL/截图及文字数字；业务说明；PASS/FAIL/NOT_RUN与缺项，不自行豁免B。

## 兼容与失败闭环
四入口/L4L5/原用户与MA成果完整性/旧异常弃用或隔离方式/Token休眠/GET零新任务结果；自动full=0，显式full延期未测。
issue、原失败、修复候选（若后续获准）、新attempt复验、遗留限制；不覆盖失败。
保留新版演示服务的容器、版本、端口与五组URL（故障停服须说明）；旧state/包可回退性实核。
最终：本次哪些门禁通过、哪些待验、是否取得第二次人工验收；不得混写本地/现场结果。
```

现场结果直接写入唯一Markdown，按以上BUS01–05逐组列出；无需寻找包外BUSINESS_EVIDENCE.md或另交附件。未测保持NOT_RUN。任何产品修改需新候选身份与受影响验证，不沿用repair-r1-02验收签名。


补充固定阶段顺序：用户监控（含多模型访问、搜索排序、P90 TTFT）→MA→第一次用户确认→上述五组真实low_hit小样本→第二次用户确认。只读复用原监控成果，本轮禁止新增用户监控/MA run或重算全量，不切换默认；有绑定冲突停止说明。页面浏览/刷新/重连只读，不新增POST。

最终仅一份自包含Markdown，正文直接嵌关键源码/最小diff（若后续另获修改授权）、配置命令、容器内复现、错误与HTTP/页面数值、前后测试及SHA。不要另要求证据压缩包或仅给文件路径。实际源正文按授权最小披露。现场没有获得代码修改授权时，不执行源码修改，记录建议与阻断，由开发会话接手。
