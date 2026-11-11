# 华为V3小样本验收交接材料（2026-11-11）

**准备完成，待执行授权；本材料不是打包、部署或真实数据访问授权。** 当前候选repair-r1-02本地独立验收通过，五组真实业务及真实大源仍NOT_RUN。显式full用户决定延期，不测试/不启动；自动full必须为0。Token新分析休眠，修复留V3.5。

此文面向后续现场执行agent；执行前由用户确认实际交付版本和执行权限。镜像会话只做审查/授权后的打包，代码debug回V3开发。无需再次要求用户选择已指定的五组appid。

## 1. 阅读、版本与路径门禁

先读[本地收口](LOCAL_ACCEPTANCE_CLOSE_20261111.md)、[逐项验收](ACCEPTANCE.md)、[交付固定规则](../../operations/DELIVERY_ACCEPTANCE_RULES.md)。已验候选302源码manifest SHA `1fb8c3dc6a03dc49ddeb4c4cbc8b260c4ebc79e1cc60cfe04dcdcc5ee2fad820`，前端index SHA `1210d1e7f7e4dc21036a4249a86046cfb9f4dc32deb0fb11fdcc42751fa1ee0b`。

目前只有基线HEAD加未提交源码，没有可宣称已发布的V3 commit/镜像。后续获授权交付时填写真实commit、镜像digest、代码/前端包摘要、依赖与模型资产摘要，并核对与本地候选的映射；缺失则保持待交付，不填占位值后开测。不要从共享dirty直接打包，不复用candidate.json中本地PID/state/合成源路径作为现场配置。

执行前核实际主机、CPU/RAM/磁盘、容器/进程限制、模型revision/tokenizer/template/cache配置；历史V100不是当前机器自动证明，不推断Ascend。真实Trace历史路径 `/home/aarc/zhangxiyue/10.20_Trace_extract/10.20_Trace/`（3CSV）及10.20_MA（18CSV）仅作线索，现场核存在性、schema、授权和五组覆盖；不默造数据/配置/TTFT参数。

每次attempt先记录将写入的绝对路径，确认落在批准的TokenScope工作根，拒绝已有目录，使用带时间/唯一后缀的新目录且排他创建；新state与原数据/旧state/历史证据路径互不重叠。禁止复用本地attempt-01等示例、覆盖旧日志、清空历史或把真实数据放Git。失败后新attempt保留旧失败，不在旧文件上修数。

## 2. 分阶段执行和停止点（取得现场授权后）

1. 盘点归属明确的TokenScope旧服务/worker/前端/测试容器，正常停止并验证退出与端口释放；不误停无关服务。保留原数据、包、state、报告。以确定候选、新state、新浏览器冷启动，不另换端口让旧版并行。版本/健康/静态资源身份留证。
2. 按用户监控→搜索排行/P90TTFT→MA顺序完成真实数据验证，保留四入口及L4/L5；**第一次人工验收**。缺真实参数不填0；未取得人工确认不自动越过。若用户认可已有对应候选的确认，记录其具体依据，不代签。
3. 在确认后的五组范围执行正常low_hit诊断。记录实际提交JSON/HTTP、task/source/sample/recipe/evaluation/report身份；不提交clock指针/regex/手写recipe/finding，不人工裁小CSV、不调大candidate_limit掩盖问题、不使用full。可用正常页面或同一公开API，页面必须读取新封存报告。
4. 按下述资源与逐组收益门禁验收，失败如实留证；保留成功窗口，禁止为正收益重抽样。刷新/重连/历史查看不能新增POST；旧Token结果可读且不新执行。完成后**第二次人工验收**，单Markdown回传。
5. 临时测试进程退出且端口确认；若用户要求保留审阅服务，明确其PID/身份/端口。现场发现代码问题回传证据交开发修复；不得让打包agent自行debug或用临时脚本注入结果“通过”。

固定访问方式（实际主机仍须核实）：`ssh -L 18002:127.0.0.1:18002 zhangxiyue@10.67.43.44`，本机浏览器 `http://localhost:18002`；不改为公网暴露。回退前核现场旧包/state真实可用，未核实不能承诺回退；不删除旧state解决冲突。

## 3. 真实大源AC-MEM

在实际大父范围上不填手动sample_limit，观察自动选A/B及正常完成；记录父范围总数、模型固定开销、profile/预算、自动缩样理由、A/B成员数/连续性/不重叠digest、排除及attempt。计数区分全源流式校验I/O、入选正文读取/解析/编码、发现/评估/发布。

通过：得到可用诊断及适用方案实算，OOM/mem_limit/内存强杀=0；只返回预算不足/超时/保护性kill不能算通过。记录进程树/容器峰值、硬控制类型/范围/单位、各阶段耗时、终态和退出码；RSS峰值与RLIMIT_AS分别列。不得用结束时内存或短合成输入代替真实峰值。单条或模型无法装入的环境边界单列证据，普通总量过大失败保持OPEN。

现场响应/取消沿用TESTS §4：20次health/receipt各自nearest-rank P95≤1s且全成功；取消HTTP≤1s、任务子进程树≤5s结束或确认已成功提交终态，API持续可用。取消专用新attempt不污染五组正常完成结果。记录实测而非复抄本地数字。

## 4. 五组自动clock→固定化→实算→前端

| ID | 模型 | appid | 初始状态 |
| --- | --- | --- | --- |
| BUS01 | DeepSeek-V4-Flash-0731 | S00000000000000000000000000000773 | NOT_RUN |
| BUS02 | DeepSeek-V4-Flash-0731 | S010320 | NOT_RUN |
| BUS03 | DeepSeek-V4-Flash-0731 | com.huawei.mbs.ilegal.ioc | NOT_RUN |
| BUS04 | DeepSeek-V4-Flash-0731 | com.huawei.newalliance | NOT_RUN |
| BUS05 | Qwen3.6-27B | com.huawei.aidp_dg06 | NOT_RUN |

逐组要求：

- 正常自动L1发现合格clock变化，给请求对/角色/JSON pointer/块位置/受保护原值；后续历史不同不误筛可比字段。只有普通日期删除、L4证据或人工指定反事实，不关闭BUS。
- 前端显示完整clock内部替换为同一`NORMALIZED`，外部文本/工具/历史保持语义内容；原始请求不改写。recipe先由A冻结，B不参与调参；A/B连续原顺序、不重叠、各自ledger，不将两窗拼接或混分母。
- 各窗记录N、匹配N、修改N、before/after P/H/C（逐请求及聚合满足P=H+C）、H/P与提升百分点 `100*(H_after/P_after-H_before/P_before)`；各用自身P，P=0为不可用。封存报告、前端、业务摘要同一evaluation与数值。
- 在同一冻结成员/编码/缓存配置上用独立字面前缀核算核对整数与比率，注明独立算法与复用编码/变换的边界。记录实际独立核算方式/结果，不能只看生产报告自称独立通过。
- 页面保留零/负收益；Qwen实际配置若缓存关闭等导致零值，先核实说明，不为过关擅改配置。无适用、无收益、未评估、预算不足、取消、B不足分别记录。A已完成可展示；缺B则该组未关闭，除非用户明确接受该组具体限制。
- 对原因证据上限（如CAUSE_EVIDENCE_TRUNCATED）明确发现覆盖partial；完整窗口实算可以独立complete，不把它说成全部原因已覆盖。
- 给五组各自真实截图/URL、方案/精确局部证据和参考值。时间固定化改变时间感知，需业务确认；不承诺业务无损、答案质量、TTFT/账单收益或全量收益。无需复现旧报告正收益幅度。

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
请求对/逻辑字段/clock片段→NORMALIZED、finding/recipe/plan/evaluation/report摘要。
| 窗 | N/匹配/修改 | before P/H/C | after P/H/C | before% | after% | 差值pp | 完整性/复核 |
| A | 实填 | 实填 | 实填 | 实填 | 实填 | 实填 | 实填 |
| B | 实填 | 实填 | 实填 | 实填 | 实填 | 实填 | 实填 |
独立复算方法/结果；页面URL/截图及文字数字；业务说明；PASS/FAIL/NOT_RUN与缺项，不自行豁免B。

## 兼容与失败闭环
四入口/L4L5/旧结果/Token休眠/GET零新任务结果；自动full=0，显式full延期未测。
issue、原失败、修复候选（若后续获准）、新attempt复验、遗留限制；不覆盖失败。
结束进程/端口或获准保留审阅服务；旧state/包可回退性实核。
最终：本次哪些门禁通过、哪些待验、是否取得第二次人工验收；不得混写本地/现场结果。
```

现场实测回填[BUSINESS_EVIDENCE](BUSINESS_EVIDENCE.md)，未收到报告前保持NOT_RUN。任何产品修改需新候选身份与受影响验证，不沿用repair-r1-02验收签名。
