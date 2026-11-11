# V3小样本交付结果（2026-11-11）

结论：候选交付审查、授权版本整理/精确Git提交push、WSL镜像/代码打包、包/容器验证及桌面全文件SHA核对已完成。**本地交付可用；华为BUS01–05和真实长输入AC-MEM仍NOT_RUN，人工两阶段验收未执行。** 本线只承担候选审批/版本/打包，不代开发debug或研究独立验收。

## 身份与路径

- 发布：`tokenscope-v3-sample-20261111`，源码main commit `cabf2c68d4d63eaeb24531b51ba4b3a2e2ad1ee0`，已显式push并ls-remote核对。文档收尾提交不改变该包的源码身份。
- 镜像：`tokenscope/full-service:tokenscope-v3-sample-20261111`；ID `sha256:d6d9b5997c5f27e36dccc553db89679686c8c552210ac542ee56c57d382cb6f5`。
- WSL完整目录：`/home/zhangxiyue/TokenScope/artifacts/releases/tokenscope-v3-sample-20261111`；Windows完整目录：`C:/Users/ALIENWARE/Desktop/tokenscope-v3-sample-20261111`。17文件全部复制、逐项字节/SHA相同，两端SHA256SUMS16条通过，另核清单自身SHA；WSL原包保留。
- 使用prompt：[HUAWEI_AGENT_PROMPT.md](../../../artifacts/releases/tokenscope-v3-sample-20261111/HUAWEI_AGENT_PROMPT.md)；[版本/配置摘要](../../../artifacts/releases/tokenscope-v3-sample-20261111/VERSION_CONFIG_SUMMARY.json)、[逐文件清单](../../../artifacts/releases/tokenscope-v3-sample-20261111/SHA256SUMS)、[本机容器说明](../../../artifacts/releases/tokenscope-v3-sample-20261111/CONTAINER_VALIDATION.md)。
- 本地backup：`backup/20261111-tokenscope-v3-sample`，commit `cf7e30e4d72a8c4c02d3ecad0d91417815908245`，parent为上述源码commit。仅小manifest指向本地真实文件/SHA，不设upstream、不push、不merge main，包体及镜像不上GitHub。

## 候选及构建映射

[交付审查](V3_SAMPLE_REVIEW_20261111.md) APPROVED_FOR_AUTHORIZED_PACKAGING；[研究收口](../product-v3/acceptance-v3/CLOSE_20261111.md) LOCAL_ACCEPTED_WITH_SCOPE_DECISION / ONSITE_PENDING。基线9a071c8加未提交候选经精确清单142路径提交；保留70份不归本轮的既有tracked dirty及其他未提交研究/归档/环境资产，不git add-A、不清理共享工作区。

已验repair-r1-02的302源码/17验证/4dist/8编码资产全部一致，实际source manifest SHA 1fb8c3dc6a03dc49ddeb4c4cbc8b260c4ebc79e1cc60cfe04dcdcc5ee2fad820。另固定484项源码/契约/依赖/部署身份，SHA见[VERSION](VERSION_V3_SAMPLE_20261111.json)。从已push固定commit在WSL独立快照构建，Node22.22.2/npm10.9.7，4份重建dist与已验SHA逐字节相同；38离线wheels按hash安装，固定基础镜像、network=none。前后端在同一完整服务镜像，不用旧dist冒充新版。

代码包git archive固定commit并附同一dist/8资产/wheels/candidate；302验收源码及214context文件与归档逐项一致，无重复路径。镜像归档config SHA对应image ID，docker load重新装载后ID一致。legacy pyproject0.1.0.dev6/viewer0.1.0-f007及/version的null release_id保留，不能以这些字符串识别发布；实际发布以OCI version/revision、candidate及固定commit为准。随包当前部署说明覆盖代码包内保留的历史V2部署prompt/README，不执行旧两方向全量方案。

## 实际包/容器验证

- 先核本项目无旧运行服务/容器、18002释放，新空state和新浏览器Compose冷启；非root、只读root/input、8CPU/32GiB/独立state按实际inspect通过，167容器运行文件SHA核对一致。
- 一个16条短clock合成场景，经正常worker和实际页面自动发现/准备/实算/展示完成；只有2次显式POST，刷新/重连0额外POST、0页面错误；任务正常completed无强杀。重启报告及3封存文件SHA不变，仅1任务。
- 历史兼容在隔离一致副本上，以旧HV2与新镜像串行比较：20旧用户目录/默认绑定、4旧诊断report、MA目录（3项）和基础目录响应一致；原272输入/state文件SHA不变。真实浏览器四入口4项通过，旧固定用户/报告可读，0POST/0页面错误。Token旧POST409、旧历史可读，V3目录为空未自动执行。
- 首次私有daemon长socket失败，改项目内短exec-root后成功；首次MA检查编排误用ma-v1得到404，按实际路由修正后通过。失败日志保留，不称产品失败或改源码绕过。既有候选文档/测试尾空白保持原字节，单独披露格式检查，未改验收身份。
- 测试服务/worker/容器已停，18002释放，本次专用Docker daemon停止；旧镜像、旧state/input、日志和包体保留。

完整本机证据：[review目录](../../../artifacts/reviews/v3-delivery-20261111/)，含identity/302映射、源码diff、build/load、167运行摘要、兼容前后HTTP/页面截图、重启、归档、桌面及清理记录。镜像验证仅本机合成，不重签研究的10场景/9窗口/104后端/34前端。

## 范围、数据保护与现场待验

本期仅小样本低命中；显式full用户延期（未实现/未测试，不记PASS），自动full禁止，Token新执行休眠，旧成果可读。样本收益不称全量收益，不保证clock/正收益；时间固定化为需业务确认的反事实。保留原895/7失败、后unit663/定向38复测、旧fixture跳过/lint及B002三份历史scale证据丢失，不说所有历史测试全绿。

现场真实Trace3/MA18须重核身份/schema/规模/32GiB预算；用户监控（搜索/P90TTFT）→MA→第一次人工确认→既定五组真实low_hit→第二次确认，Token不执行。五BUS：DeepSeek下S00000000000000000000000000000773、S010320、com.huawei.mbs.ilegal.ioc、com.huawei.newalliance；Qwen下com.huawei.aidp_dg06。AC-MEM须真实大源自动缩样正常完成，保护性kill/只预算不足不能替代通过。本地短输入不证明真实容量。

现场先保全旧目录/默认/固定链接与报告摘要，停旧一致备份，空state仅验证冷启；历史兼容及后续工作在一致副本，原state不写、不用新初始化覆盖旧结果。若无法兼容先停报问题，不删旧数据。回退先实核旧包/image+配套旧state可用；停止本专属项目保全新state/失败证据后恢复匹配旧环境，旧image不得打开新库。无备份不承诺回退。

SSH18002；唯一Markdown回传，关键配置/命令/容器复现/源码或获准diff/HTTP/页面/前后验证证据正文嵌入。包不含真实数据、构造输入、state、凭据或默认recipe，本轮未部署华为/新增真实数据访问。产品问题交V3开发，研究复验，不唤醒旧六线。

## 全部交付文件

| 文件 | 字节数 | SHA256 |
| --- | ---: | --- |
| CONTAINER_VALIDATION.md | 1,903 | `db0e9eb2ec655e1adc6dbfaf18e6262eb210c849e67489875d6cf6f0af4afb6f` |
| DEPLOYMENT_README.md | 1,750 | `936c84b0c138bab16e2efdb7d7c89aa46793d58518a4088d03bd077dfebbbbaf` |
| HUAWEI_AGENT_PROMPT.md | 12,265 | `2b69acbc47f475d5408b9d510e5b02f1c5a86a364f20e1e401fdeea046b81b2e` |
| SHA256SUMS | 1,444 | `a003f08f640e0ff6eac00f8b09d21e6b0830058e87f2803a34b33888c181bb70` |
| VERSION.json | 62,183 | `58ea9a1cb5856436b2efd4cbd1a807d3354f63036a5344a7ce7241eccc4939b8` |
| VERSION_CONFIG_SUMMARY.json | 11,735 | `c6056049552707cae890b82dc6d20dfd2ced7aef96227ba14377b433ca6962b9` |
| candidate.json | 30,712 | `cdc9f180b0954ad4a6f23bc903cb2389a3d3c80549d55d4c9aadc8b40374c9a6` |
| compose.yaml | 1,325 | `134d6d9665615b4246ac472714df8d533a43c99dc0b407399a96d11ca2d56dd3` |
| container-acceptance.json | 7,688 | `89006f64e989b5770a183d218e5a134a979b365055808a35fdaa06fe5d0fcbab` |
| container-browser.log | 346 | `fbb8172139b98585c8a2a11182427ea17a84134595532b897729a804b5e73d5a` |
| container-restart.json | 752 | `9656db09a6afa43c3c4bf5b40b66d9319f13b5a2d539377f84ec743f6128895e` |
| deployment.env.example | 303 | `4fc2077b94d48d163e673d187df85e11ced08ab6d6cd48a7e6d4f1d8dc95ec02` |
| docker-save.log | 0 | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| release-manifest.json | 8,267 | `fb27f8c0590e8cb5a8c20ccedf509ca0695126e0cf64d23c6ca7b737fa21778d` |
| tokenscope-v3-sample-20261111-code.tar.gz | 72,813,377 | `26e6cd8e344f34433a656aa81223f9f7aca985eb4a0062d74da2e26782ee940d` |
| tokenscope-v3-sample-20261111-image.tar.gz | 204,651,311 | `631fea7c0f2cf315679713a7167e415e13f40c55bc77068edb7587aac1321832` |
| unified-container-validation.json | 1,754 | `ee476f9e16eb8323d8f4bd7177d0fb18ada89f2664e8a19b502c67f21403f749` |
