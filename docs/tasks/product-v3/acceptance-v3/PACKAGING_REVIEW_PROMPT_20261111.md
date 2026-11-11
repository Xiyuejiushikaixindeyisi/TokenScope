# 给“镜像打包与审查”的V3交付审查与授权打包prompt

2026-11-11。以下内容可直接发送给“镜像打包与审查”会话 `01a1800e-80b4-7400-a78b-a84f5b6e888d`。

---

请接收TokenScope V3小样本低命中率分析候选，完成交付审查；审查通过后继续进行版本整理、Git提交与按项目约定push、镜像打包，准备发给华为机的代码包、镜像和使用prompt。用户已明确授权这条执行链，不需要在审查通过后再次申请打包许可。

项目根目录 `/home/zhangxiyue/TokenScope`，Windows对应 `\\wsl.localhost\Ubuntu-22.04\home\zhangxiyue\TokenScope`。请从确切根目录工作，保留其他会话未提交内容，不操作兄弟项目。

## 一、当前范围与职责

用户2026-11-11明确决定：**V3先交付小样本分析，显式全量评估延后。** 原D6/T19显式full条款不再阻断本候选，也不据此补开发；自动全量保持关闭。延期未指定版本，不自动加入V3.5。

研究/独立验收会话已完成R1问题交开发修复及R2独立复验，当前结论为 **LOCAL_ACCEPTED_WITH_SCOPE_DECISION / ONSITE_PENDING**。源码本地通过，五组华为真实业务和真实长输入资源验收仍未完成。不是整体生产验收通过。

你负责候选/交付审查、版本整理、Git提交和镜像/代码交付打包，不承担编码、debug、开发调度或开发验收执行。审查发现代码问题请列出证据并退回用户，由V3开发会话 `01a1c449-6a9b-7a83-912a-5a9ff77c703d` 修复、研究会话独立复验；不唤醒旧六条V2线。更新你自己的交付入口、记忆和实际职责状态，记录审查结论及执行进度。

**本次直接用户授权（2026-11-11）**：“把这份prompt发给‘镜像打包与审查’session。审查通过后由‘镜像打包与审查’session进行版本整理、Git提交和镜像打包，准备发给华为机的代码包、镜像和使用prompt，注意保留已有数据和分析结果。”此决定覆盖此前“未授权Git/构建”“待用户转发”等阶段状态。审查通过后在上述范围内执行并完成必要的包/容器验证；本轮准备交付文件，不直接部署华为机或扩大真实数据访问，不把本地通过写成现场通过。

## 二、最小阅读链

1. `AGENTS.md`、`memory/CURRENT.md`、`memory/SESSIONS.md`、`docs/tasks/delivery/ENTRY.md`，明确角色。若旧入口仍写“等待独立复验/full待裁定”，以下本轮决定覆盖旧状态。
2. `docs/tasks/product-v3/acceptance-v3/CLOSE_20261111.md`：用户范围决定、验收收口、候选身份与现场边界。
3. 同目录 `REVIEW_20261110_R2.md`：本线实际独立结果与证据。仅按需回看R1，不必恢复全部研究/宣传历史。
4. `docs/tasks/development-v3/batches/REPAIR_R1/CLOSE.md`、`TESTS.md`、`ISSUES.md`及 `docs/tasks/development-v3/BUSINESS_EVIDENCE.md`：开发交接、已知限制与五业务待验。
   同时读最新 `docs/tasks/development-v3/LOCAL_ACCEPTANCE_CLOSE_20261111.md` 与 `HUAWEI_ACCEPTANCE_HANDOFF_20261111.md`，将现场步骤整理进使用prompt；其中此前“打包待授权”由本次用户授权覆盖，现场执行仍待后续安排。
5. `docs/operations/DELIVERY_ACCEPTANCE_RULES.md`、`docs/architecture/TASK_SESSION_WORKFLOW.md`、`docs/operations/GIT_WORKFLOW.md`；部署相关再读 `deploy/monitoring/README.md` 与 `memory/DELIVERY_LESSONS.md`。最新三角色分工及本次用户范围优先，不恢复旧总设计/六线修复流程。

## 三、确定候选，不能直接从共享dirty打包

- 当前基线HEAD：`9a071c87b517490e497aa6cc1e53ec066bb4ede0`，**加已验收的未提交源码**。该HEAD单独不含V3实现，不得拿它冒充V3发布commit。
- 候选目录：`artifacts/validation/development-v3/V3B007/repair-r1-02/`。
- `source-sha256.json`：302源码文件；该manifest文件SHA256为 `1fb8c3dc6a03dc49ddeb4c4cbc8b260c4ebc79e1cc60cfe04dcdcc5ee2fad820`。
- `candidate.json` SHA256：`9d97e97bd7cc62d322276d4d08726ec99e4bd2a74df50bd88b3446f83e8f5fc0`。记录的是历史本地候选进程身份/配置，不把旧PID、service_instance_id当成当前在线服务。
- `validation-sha256.json` SHA256：`f14d639bc84e963585a42431891433a8003db3ac9aff2ddb65c118eb7408afde`。
- 已验收前端目录：`artifacts/validation/development-v3/REPAIR-R1/attempt-07/dist`。全部4文件摘要见candidate.json：

| 文件 | SHA256 |
| --- | --- |
| index.html | 1210d1e7f7e4dc21036a4249a86046cfb9f4dc32deb0fb11fdcc42751fa1ee0b |
| assets/index-B0E5_SiJ.css | 2a4679590e374dcd7e3ab19a34dfc3adfe3ab5f05329cc3d14dc0e79d15cc0e2 |
| assets/index-D_8T_suS.js | 6c1bc68d589d4531129e6281ad62e9b524ddfa02ca1b07b18aed8d2b2bc50630 |
| assets/export-validator-rZ4O78aZ.js | e52838c80a214d465b29b1e6049fabe887e80d8077fc5ce121061c8f109e9d41 |

研究会话2026-11-11再次核对：302源码无新增/丢失/漂移，17验证文件、4个dist文件、8个模型编码资产及保护文档一致。证据 `artifacts/validation/product-v3/handoff-20261111-01/identity-check.json`；同目录git-status.txt为当时共享工作树记录。

源码manifest是验收身份，不是完整发布包含清单。请另核依赖锁、模型/模板资产、契约、启动/部署文件和变更归属。共享dirty包含文档归档和其他工作，禁止 `git add -A`、全局reset/clean、替别人提交或将全部dirty无差别收入包。

审查通过后，按 `GIT_WORKFLOW.md` 精确暂存获准交付且归属明确的文件，完成版本整理、提交、合并main（如需要）及显式 `git push origin main`，不使用PR。从固定commit在WSL构建，核提交内容与已验收源码/配置对应，再记录源码包、前端、镜像及资产摘要。重建dist若有差异要说明原因和影响；产品变化交开发及研究复验，不能当普通打包调整悄悄带入。候选中的旧开发版号或空release_id不是发布身份，必须记录实际交付版本及其与已验候选的映射。交接时尚未执行本次Git提交/push或镜像构建。

## 四、本地验收证据及限制

独立证据根 `artifacts/validation/product-v3/independent-20261110-02/`；现有E2E驱动路径限制下，本线独占输出 `artifacts/validation/development-v3/V3B007/independent-review-20261110-02/`。这是研究会话重新运行的新state/新浏览器，不是拿开发自测代签。

- 10个正常HTTP/worker/实际页面场景，覆盖自动clock及历史轮次变化、CCH/普通日期/path、工具顺序/description/增删、新L4/L5证据；RV3-01/02/03已关闭。
- 自动发现→位置/原文→冻结改法→实算→前端展示；没有预置clock指针、recipe或finding冒充自动发现。原DeepSeek CCH编码相同例实际0pp，正确展示；不承诺每个CCH都有收益。
- 9个完整窗口用不调用生产PrefixLedger的字面前缀算法核对逐请求及聚合P/H/C、摘要和百分点，全部一致；编码/变换原语复用，不能称独立tokenizer校验。
- 104项后端检查、34项前端兼容通过；旧结果/默认和固定历史、Token新执行休眠覆盖。重启读取10报告、26封存文件保持，浏览/刷新/重连0额外POST。
- 2200条构造源自动A512+B512正常完成，两窗实算完整；L4原因组上限触发时明确 `CAUSE_EVIDENCE_TRUNCATED`。样本规模由预算决定，不能宣传固定300/512条或全量原因全覆盖。
- 本地示例约1K输入，不证明华为实际长输入资源底线。资源5组API探针P95最大5.308ms、取消HTTP13.392ms、worker停止0.537秒仅本地证据。硬限为RLIMIT_AS，不称RSS硬限。
- 当时Windows/WSL无可用Docker CLI，未验镜像/容器。此次已授权构建及必要的本地包/容器验证：先核现有构建环境，核包内身份、容器启动和隔离副本上的兼容性。遇到实际环境阻断时记录原因，不虚报已构建；不重跑无变化的全部开发/独立测试来替代打包审查。

保留披露：开发原全pytest895通过/7失败和后续unit663/定向38复测分开；独立104/34另列。旧source-link fixture缺失跳过、历史脚本lint、B002三份scale JSON原件丢失仍按记录保留。不要改写失败日志、删除待验项或说“所有测试全绿”。

## 五、华为真实验收安排，待授权执行

BUS01–05及真实负载AC-MEM当前均NOT_RUN：

| BUS | 模型 | appid |
| --- | --- | --- |
| 01 | DeepSeek-V4-Flash-0731 | S00000000000000000000000000000773 |
| 02 | DeepSeek-V4-Flash-0731 | S010320 |
| 03 | DeepSeek-V4-Flash-0731 | com.huawei.mbs.ilegal.ioc |
| 04 | DeepSeek-V4-Flash-0731 | com.huawei.newalliance |
| 05 | Qwen3.6-27B | com.huawei.aidp_dg06 |

现场prompt需基于已有授权的真实来源和真实配置，正常页面显式低命中分析，自动缩样及自动L1；不预置clock/recipe，不靠加大candidate_limit、人工小CSV或启动full掩盖资源问题。记录来源范围/总数、A/B选取与排除、预算、耗时/内存、是否正常完成；记录精确字段/改法、样本N/匹配N/修改N、before/after P/H/C和百分点，A/B分开核算，页面与封存报告一致。

无clock、无B、无收益、预算不足、评估不完整分别保留；旧报告提升不能直接填入新结果。时间固定化是诊断反事实，需要业务确认时间语义，不能自动改业务请求。真实大源要自动有界完成；保护性kill/预算不足不替代资源底线通过。

现场仍按用户监控→MA→第一次人工确认→指定appid/模型/范围低命中分析→第二次确认。上述五组是已指定待验对象，不扩大到其他appid。Token新分析继续休眠，不能照抄旧“低命中+Token一起运行”的prompt。

后续执行时先核实际主机、环境/32GiB等真实资源预算、模型revision/模板/缓存配置；不按“华为机”推断Ascend。已有V100仅作环境依据。SSH18002、单Markdown回传保持：关键配置、命令、实际HTTP/页面证据、状态/前后数值、失败与复验直接嵌正文，不要求另回传日志目录/证据包。

## 六、数据保护、回退及最终交付要求

- 四入口“用户监控、搜索与排行、异常分析、MA集群监控”和L4/L5保留；页面访问只读，不触发分析。旧结果/默认绑定保持，不用新state初始化覆盖旧state或悄悄切换默认appid。
- 新版本验收前盘点并正常停止核实归属的旧TokenScope进程/服务/测试容器，验证端口释放；独立新state、新浏览器与确定候选冷启动。不可换端口把旧版留着并行验收；不可误停不明归属进程或无关项目。仅审查文档时不停止服务。
- 旧数据/state/日志/镜像/代码包/原始报告保留。需要历史兼容时使用隔离副本，不写原件。回退先核现场旧包和state真实存在，再列恢复步骤；没有备份不能承诺原位回退，禁止以删除旧数据解决冲突。
- 高优先级四象限HTML `docs/tasks/product-v3/promotion/quadrant-detail/dist/index.html`（SHA `8d76928147dd8a4f274fd0e160a916a493e7878d4ba14c7c339683877ba2a354`）及四页宣传稿、两份华为原报告保持。宣传稿不是产品前端实现规格；构造样本不得混入真实BUS验收或覆盖统计。
- 本轮审查通过后准备并交付镜像、代码包、运行/验收prompt、版本与依赖/模板资产身份、逐文件校验、已知限制、回退说明及包/容器验证记录。产物放项目 `artifacts/releases/<版本>/`；包体/镜像/真实数据不上GitHub。若另有适用的Windows桌面复制授权，保留WSL原件并逐文件核SHA。
- Token异常开发仍V3.5；不启动T1/新T2–T4、hybrid、Agent、SSD或顺带重设计UI。UIR-03仅待讨论，不新增为本候选阻断。

请先完成并记录候选审查：精确文件/资产、身份映射、已知限制和回退安排。审查通过即继续完成已授权的版本整理、Git提交/push、镜像与代码包及使用prompt，不停在计划或再次等待同项授权。最终向用户交付实际版本/commit、Git提交与push结果、镜像和代码包绝对路径及SHA256、使用prompt路径、包/容器验证结果、旧数据和分析结果保护说明、现场仍待验项。若审查或构建受阻，列明对应候选、可复现证据及已完成/未完成部分；不自行修产品代码，不执行华为部署。
