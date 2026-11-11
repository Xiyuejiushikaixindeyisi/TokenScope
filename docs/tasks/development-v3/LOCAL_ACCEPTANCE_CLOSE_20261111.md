# V3本地验收收口（2026-11-11）

状态：**LOCAL_ACCEPTED_WITH_SCOPE_DECISION / ONSITE_PENDING**。用户明确延期显式full，优先大数据自动缩样和五组session_clock样本参考提升率；暂不打包。延期未指定版本，不自动转入V3.5。Token异常修复仍留V3.5，旧结果只读保留。

## 范围与设计核对

| 范围 | 收口结果 | 证据/下一步 |
| --- | --- | --- |
| D2/D3 大源有界准备、自动缩样、资源/取消 | 本地通过，真实负载待验 | 独立R2：2200条自动A512+B512正常完成；真实长输入AC-MEM仍NOT_RUN |
| D4/D6/D7 自动clock→精确固定化→实算→前端 | 本地通过，五BUS待验 | 正常请求不指定clock/recipe/finding；同窗before/after、B冻结改法复核；现场逐组留新结果 |
| D4/D5 非clock及L2/L3/L4/L5兼容 | RV3-01/02/03独立复验关闭 | R2真实HTTP/worker/browser；原R1不通过记录保留 |
| D6 原T19 | 拆分T19-A本期必需、T19-B用户延期 | 自动full=0/旧结果兼容保留；显式full未实现/NOT_RUN，不能写PASS |
| B001–B006 / B007 | 修订范围组件闭环 / 本地收口 | 整体V3业务验收尚未关闭，禁止以合成结果代填BUS |

权威规范：[DESIGN r2](DESIGN.md)、[TESTS](TESTS.md)、[底线验收](ACCEPTANCE.md)。原B005遗漏显式full及T19误签事实见[FULL_SCOPE_GAP](FULL_SCOPE_GAP.md)，本次用户决定不是追溯伪造原测试通过。

## 候选与独立证据

- 基线HEAD `9a071c87b517490e497aa6cc1e53ec066bb4ede0` **加未提交候选源码**，不是发布commit；仅取HEAD不能得到V3。
- 候选：[repair-r1-02](../../../artifacts/validation/development-v3/V3B007/repair-r1-02/candidate.json)。302源码manifest SHA256 `1fb8c3dc6a03dc49ddeb4c4cbc8b260c4ebc79e1cc60cfe04dcdcc5ee2fad820`。
- 前端 `artifacts/validation/development-v3/REPAIR-R1/attempt-07/dist`，index SHA256 `1210d1e7f7e4dc21036a4249a86046cfb9f4dc32deb0fb11fdcc42751fa1ee0b`；所有dist文件摘要见candidate.json。
- 本轮在确切根目录只读核302条source manifest，漂移0，manifest摘要一致；PowerShell环境THREAD/SESSION均为 `01a1c449-6a9b-7a83-912a-5a9ff77c703d`，WSL不继承这两个变量。未修改源码/测试/契约/配置/state，未启动服务或重跑测试。
- [独立R2原报告](../product-v3/acceptance-v3/REVIEW_20261110_R2.md)及[研究侧11日收口](../product-v3/acceptance-v3/CLOSE_20261111.md)；研究侧11日又核302源码、17验证文件、4dist、8编码资产一致。

| 已实际执行的独立验证 | 结果与限制 |
| --- | --- |
| 正常HTTP/worker/真实浏览器10场景 | 通过；覆盖clock、非clock、工具、新L4/L5；不注入发现结果 |
| 9完整窗口逐请求P/H/C及百分点 | 字面前缀独立算法核对通过；复用编码/变换原语，不称独立tokenizer |
| 后端104项、前端兼容34项 | 通过；不是所有历史测试全绿 |
| 大源2200→A512+B512 | 正常完成、exit0、无强杀，17.202s，监督RSS峰值301903872 bytes；512由该次预算产生，不冻结默认数量 |
| 原因证据截断 | L4达到128上限时CAUSE_EVIDENCE_TRUNCATED；discovery partial与两窗evaluation complete分别陈述 |
| 响应/取消 | 5组各20health/receipt探针全成功，最大P95 5.308ms；取消HTTP13.392ms，worker退出0.537s；仅本地证据 |
| 重启/只读 | 10报告/26封存文件摘要不变，刷新重连0额外POST；验收结束临时服务已退出 |

原始日志目录 `artifacts/validation/product-v3/independent-20261110-02/` 与 `artifacts/validation/development-v3/V3B007/independent-review-20261110-02/`。硬控制为RLIMIT_AS地址空间限制，不能称RSS硬限；本地构造输入不证明华为真实长请求容量。

## 未通过、未执行与保留披露

- 五BUS与现场真实大源AC-MEM均NOT_RUN；0/负收益允许如实发布，不保证发现clock或正收益。缺B/无适用/预算不足不自行关闭业务门禁。
- 原全Python895通过/7失败，修正两个编译分派测试替身后定向38及全unit663通过；不改原失败日志，不说原全套已通过。旧source-link缺fixture三跳过、旧脚本八项ruff问题仍保留；详[修复测试](batches/REPAIR_R1/TESTS.md)。
- B002误覆盖三份历史scale JSON原件不可恢复；新内容副本不是旧证据备份。事件与预防修复继续见B002 ISSUES，不声称所有历史证据完好。
- Docker/容器、发布commit、包内身份、华为现场两阶段人工验收均未完成。本轮没有Git提交/push、镜像/代码包构建、现场执行、跨会话派发。

## 交接与后续门禁

[华为验收交接](HUAWEI_ACCEPTANCE_HANDOFF_20261111.md)已准备，待后续授权和确定交付物后执行。已有[镜像审查prompt](../product-v3/acceptance-v3/PACKAGING_REVIEW_PROMPT_20261111.md)供用户转发；本线没有发送或启动该会话。

本地无已知未闭环的本轮独立验收代码阻断。后续若候选/配置变化或现场发现问题，由V3开发定位修复、记录问题和受影响复测，再独立复验；不恢复旧六线，不将debug交给镜像会话。不因文档收口自动打包。
