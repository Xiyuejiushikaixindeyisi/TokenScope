# HV2修复与完整交付结果（2026-11-03）

本轮已完成六线统筹、公共层优先独立验收、依赖后端冻结、前端接入、源码及固定镜像独立验收、WSL打包和Windows桌面全文件SHA核对。**本机合成验收通过，华为真实数据及用户两阶段验收尚未执行。** 本记录由V2总设计师 `01a1800e-80b4-7400-a78b-a84f5b6e888d` 汇总实际结果，不代替用户展示签字或现场报告。

## 版本与文件

- 交付版本：`tokenscope-v2-hv2-20261103`；源码main提交：`c1345b6fd7d413a94420642ca1b4099b9ec104b4`，已显式push origin main并核对远端。后续文档收尾提交不改变包体身份。
- 镜像：`tokenscope/full-service:tokenscope-v2-hv2-20261103`，ID `sha256:d129a05636b01b4f93d806e42587be749cef561cfbacbe0067adbd7b8d7c37f8`。
- WSL原目录：`/home/zhangxiyue/TokenScope/artifacts/releases/tokenscope-v2-hv2-20261103`。
- Windows完整目录：`C:\Users\ALIENWARE\Desktop\tokenscope-v2-hv2-20261103`。
- 本地备份分支：`backup/20261103-tokenscope-v2-hv2`，commit `8a67599e1d05c138ddd0e983e0facdf5406d0f43`；只跟踪manifest与SHA清单指针，包体留本机，不push、不合main。
- 686项源码/依赖摘要组合：`396d136f37769323ecb659ae9d89a74034df3bdbf6b9a069c757187984c9831d`；模型revision/8资产摘要、dist/离线轮子身份见包内candidate、VERSION_CONFIG_SUMMARY及[固定版本清单](VERSION_HV2_20261103.json)。694项最终审查输入组合 `7146eb2f3a82af78b7f42be498d9a5303a9f5dc28dc11a7774fe43f4bd0aede7`。两者输入范围不同。

以下15个文件已在WSL和桌面逐项核对字节数及SHA，全部一致；两端均执行SHA256SUMS的14条校验，另独立核对SHA256SUMS本身。两份gzip完整性通过，镜像归档config SHA与实际Image ID一致；代码归档固定commit及候选字节已逐项核验。

| 文件 | 字节数 | SHA256 |
| --- | ---: | --- |
| DEPLOYMENT_README.md | 2668 | `7d8e12a1e89548253ede767e4c4e9598ea3eaf18c7cff7cb848ccb4045e8d764` |
| HUAWEI_AGENT_PROMPT.md | 30192 | `c2502b463b3d462dfe4dc7f6c9c1a28f4ad63e7b22ecddb3641ff1e030ffba97` |
| SHA256SUMS | 1269 | `8110b9d03ac026a6ce9309504134726dd259e94e2145aed3fcc1a597ededa8d9` |
| VERSION_CONFIG_SUMMARY.json | 6063 | `21ad5927d7ef9a54412e893753cca0d681604cce7c46f6734085b31778855651` |
| candidate.json | 28011 | `152fb79d1c5f977a1babb8beef862c933a57600e8ab45d45d05cbb2dd27ea559` |
| compose.yaml | 1325 | `134d6d9665615b4246ac472714df8d533a43c99dc0b407399a96d11ca2d56dd3` |
| container-acceptance.json | 6775 | `244dbe3d3f6d0ce3f503b5779e035b17345f764f41397ff04bc383d5cd7c348b` |
| container-browser.log | 18706 | `e2fe0c9a14ea3435d4c55444a8981ee57537e602ba1854cb4b97315a5d90a809` |
| container-restart.json | 6774 | `371b69cf48b2f310d9fcca56595d1bd2d14d7a14f8ff317f80ed3c5ceff3811b` |
| deployment.env.example | 303 | `4fc2077b94d48d163e673d187df85e11ced08ab6d6cd48a7e6d4f1d8dc95ec02` |
| docker-save.log | 0 | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| release-manifest.json | 8215 | `daf6011a2e719de2f594115b16e1b7050c039591628ffa676b1fd054dae987a1` |
| tokenscope-v2-hv2-20261103-code.tar.gz | 71955956 | `407f70e2f57e32096c3a5642f0c134eddfa4bd0aae898aa86d9d998f589e857c` |
| tokenscope-v2-hv2-20261103-image.tar.gz | 204597137 | `28babab8bb5f1d320c28cb7f3875c03c1a68eaed3dccee4785188c689ffc4303` |
| unified-container-validation.json | 2091 | `3e86adf485acd4fab6cf339a67fc1a6613cf6bbfbb6a9a48852729562f45f2fa` |

## 实际修复与独立验收

| 范围 | 已实现与验收结果 | 保持的边界 |
| --- | --- | --- |
| 异常公共层 | 显式方向、每规则保留/每方向比较预算、扫描与覆盖遥测、ready优先及已发布partial发现；独立41项及末项3个重叠专项通过 | partial不冒充ready；禁用方向不调用其探测器；业务GET只读 |
| 用户后端 | 同APPID全部模型与不可变历史目录，2.1.0自动TTFT默认；独立62项及6个大整数/精确小数额外场景 | 旧2.0.0可读兼容；用户与异常同Trace模型规格 |
| MA后端 | 独立availability预计算，逐指标有效分母/缺数原因、独立与paired分离；66项、13契约变异与混合UUID额外验证 | 旧Snapshot1.0.0字节不变，缺失不补0、不编造cached，不擅改预热冲突策略 |
| Token私有 | 结构序列化复用、公共预算消费；171项及510种原实现等价比较 | 未新增生产recipe、DSL、T1或收益承诺 |
| 低命中私有 | 多停止原因完整保留、等文本快速路径；62项及1024文本对/276证据/24配置等价 | 保持L1–L5语义；两个prefix适配的当前身份由第二关冻结覆盖，第一关原证据不重写 |
| 前端 | 完整多模型/历史发现、W/SLO日常输入、MA缺数解释、partial成果读取；统一339单元组件、typecheck/lint/build通过 | 四入口UI-02/UI-04与最后L4/L5、UIR-01/02及现有功能保持；UIR-03留V3 |

五关冻结：[公共](HV2_COMMON_FREEZE_20261103.json)、[用户](HV2_USER_FREEZE_20261103.json)、[MA](HV2_MA_FREEZE_20261103.json)、[Token](HV2_TOKEN_FREEZE_20261103.json)、[低命中](HV2_LOW_HIT_FREEZE_20261103.json)。按依赖先验收后正式开放对应前端，分线自测不代替根独立验收。

根审查新增两项真实问题已定向修复、负向控制及回归闭环：HV2-AF-01首读/分页缓存版本键不一致；HV2-MF-02迟到自动恢复回执关闭用户新打开表单。后者3个旧实现负向用例失败，最小修复只让自动恢复保留弹窗/草稿，显式打开保持原行为。没有通过延迟测试点击掩盖产品问题。

源码与容器分别从停止旧服务、端口释放、全新state/浏览器开始，均完成**88个不同浏览器用例**（默认状态10、独立完整状态78），每轮135个真实鼠标数值核对，涵盖三模型/15scope、搜索排行、精确数值、历史、TTFT、MA、两类异常、恢复、SSE与导出取消/结构/行数/SHA。40个批准原型/实际页面捕获场景及窗口尺寸检查保留，最终lazy内容就绪再截图，无页面错误/横向溢出/业务GET写入；已实际检查四入口、MA及L4/L5页面，不代替用户人工签字。

固定镜像WSL Compose验证通过：非root、只读rootfs、输入只读/state可写、无/app源码/dist覆盖；镜像内145项实际源码/配置/模型/dist与固定候选SHA一致，HTTP资源与源码候选一致。默认配置无外部合成recipe；另一个独立本机回归state使用合成fixture override验证历史功能，该override/input/state未随包交付。

默认state正常停启后156资源及业务表行一致；完整容器state停启后154资源及业务表行一致，GET零业务写入；重启后追加6项浏览器复测全部通过（重复项不加到88）。源码完整state另有88资源一致性记录，与156/154为不同集合，不混算。测试结束正常停止容器与本轮私有dockerd，8000/8139/4173/4175/4191/18002已释放；旧包、旧state及原证据保留。

测试执行器路径、旧选择器、异步目标就绪、真实not_eligible计数语义、fixture绝对路径、dialog可访问名称等适配与最初失败日志均保留；没有删除身份/数值/缓存/恢复/导出断言。容器首次setup未带实例header的409是有效保护，补header后继续，未作为产品失败或放松校验。

## 华为下一步与未决项

使用包内`HUAWEI_AGENT_PROMPT.md`；仓库同文：[完整现场prompt](../../../prompts/delivery/HUAWEI_V2_HV2_REAL_DATA_20261103.md)。可以直接将该文件全文输入现场agent。先核对SHA和CPU/驱动/Docker/Compose/磁盘峰值及旧服务归属，停止旧版后新state冷启动；仅使用真实Trace3 CSV与MA18 CSV，先量级/预算后运行。访问：`ssh -L 18002:127.0.0.1:18002 zhangxiyue@10.67.43.44`，浏览器`http://localhost:18002`。

第一阶段用户监控（含多模型/搜索排序/P90 TTFT）→MA→等待用户验收；用户明确appid/模型/方向后才第二阶段低命中和Token异常。最终只回传**一份Markdown**，关键源码、diff、命令、复现、修复与前后证据直接嵌入正文。普通现场软件问题在隔离副本复现修复复测并记录；涉及契约/批准展示/算法策略改变先交总设计师，不自行改产品边界。

TTFT默认τ：Qwen-V3.6-27B=1s、GLM-V5.2=2.7s、DeepSeek-V4-Flash=2.6s，K8192可选覆盖，K变化不自动缩放τ。以上为用户参数，尚未真实性能校准。独立/配对MA指标不可互相代替；DeepSeek原cached缺失不能通过软件造数。真实量级成本、Trace622差异、MA18完整SHA/逐UUID/预热冲突时间、>1MiB请求分布、tools/messages新探测器正反例与收益仍需现场补证；本包仅包含有本机证据支持的修复与局部优化，不声称新探测器研究完成或真实全规模预算通过。

回退：保留2026-11-02旧包、旧镜像及其匹配state；停新版后按[旧发布身份](V2_APPROVED_DELIVERY_20261102.md)恢复旧镜像+旧state，不用旧镜像打开新版state。WSL/桌面旧代码包SHA `d7609dfaf9eaae0db01e00b563d608efbcee06c70705ccbab4b590d4d03f317b`、旧镜像包SHA `1996e82c0053985441ded8fbe8af93480130998290f95612732258fbfe954f5e` 已复核未变。

## 证据、归档与协作

本机原始证据总目录：`artifacts/reviews/hv2-repair-20261103/`。重点：`source-final-result.json`、`source-candidate-r3.json`、`image-files-verified.json`、`container-default/`、`container-legacy/`、`unified-container-validation.json`、`archive-integrity.json`、`release-frozen.json`、`desktop-copy.json`、`local-backup.json`、`old-packages-preserved.json`、`final-cleanup.json`、`source-push.json`。文件路径按实际存在性核对，不上传inputs/state/包体。

闭环执行/评审/计划和旧入口快照见[归档索引](../../../achieve/2026-11-03/hv2-delivery-closed/README.md)，旧派发prompt见[归档](../../../achieve/2026-11-03/hv2-session-prompts/README.md)。冻结契约、模型身份、批准HTML和两份华为报告保持原位/原字节；八份其他session原有未提交修改继续保留，混合文件只提交本轮独立增量。六线开发窗口关闭，后续只按现场实际问题定向恢复。
