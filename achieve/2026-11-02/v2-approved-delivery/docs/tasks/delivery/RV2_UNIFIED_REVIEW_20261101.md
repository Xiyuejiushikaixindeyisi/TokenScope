> 归档：本文件保存历史过程，不再是执行入口。2026-11-02用户认可V2可交付，UIR-03留V3、不作V2阻断。现场只用真实数据，分两次用户验收，单份Markdown回传。当前见[交付入口](../../../../../../docs/tasks/delivery/ENTRY.md)；[逐字节原始快照](../../../snapshots/docs/tasks/delivery/RV2_UNIFIED_REVIEW_20261101.md)。

# RV2完整服务统一审查与交付最终报告

2026-11-01；审查/交付session `01a1800e-80b4-7400-a78b-a84f5b6e888d`，实际环境ID核实一致。用户认可L4/L5并授权“先审查，归口修复复验，通过后打包交付”，见[执行入口](../analysis/UNIFIED_REVIEW_DELIVERY_EXECUTION_20261101.md)。本轮统一审查、修复复验、WSL构建、容器验收、归档加载与总负责独立接收均通过，交付目录已冻结；华为现场待执行。本报告替代中途“2e0c9a5/待构建”状态，过程原文及失败证据保留在本轮证据目录。

[结构化结果与全部证据SHA256](../../../../../../docs/tasks/delivery/RV2_DELIVERY_RESULT_20261101.json) · [证据目录](../../../../../../artifacts/reviews/analysis-rv2-unified) · [总负责接收核验](../../../../../../artifacts/validation/analysis-delivery-20261101/received-release-verification.json)。Git由总负责统一收口；本线未自行commit/push main，未修改共享CURRENT/SESSIONS。没有远端部署或桌面写入。

## 固定身份与审查范围

| 项目 | 最终身份 |
| --- | --- |
| 发布 | `tokenscope-rv2-20261101` |
| 构建源码及前端dist来源 | `45d9285210dc0b9edeb86c599c7b6bcd942f60b5`，已由总负责push |
| 业务组合 | `analysis-rv2-20261101` |
| 前端 / 公共后端 | `viewer-analysis-ui04-local-3` / `arpc-local-4` |
| Token私有 / 插件 | `token-review-20261101-1` / `token-content-2`（arta-local-1交接） |
| 监控协议 | S0 `1.0.0`、用户 `2.0.0`、MA `1.0.0` |
| 分析协议 | analysis-common-1.0、diagnostics-http-1、diagnostics-discovery-1、analysis-recommendations-1 |
| control / view schema | `3` / `1` |
| 镜像 | `tokenscope/full-service:tokenscope-rv2-20261101`，linux/amd64 |
| 镜像完整ID | `sha256:483db762852b38ef54559cff1bb23ef668ea9296a055ce02aac44a809b427ce5` |

[业务清单](../../../../../../docs/tasks/analysis/VERSION_RV2_20261101.json)179项源码/测试/构建输入在初审、发布工具提交后及收尾复核均与固定提交匹配；聚合SHA256为`b1a261eb987375f15f341515f9d5f066d99324163070776168bf06b9b132885a`。[candidate](../../../../../../artifacts/releases/tokenscope-rv2-20261101/candidate.json)固定182份构建文件、38个Python wheel、三模型8份Tokenizer/Template配置及摘要；代码归档中1314个Git文件经总负责与最终commit逐项核对。源锁、编码资产锁、uv锁、npm锁和冻结契约随固定源码保留。

三模型revision分别为Qwen3.6-27B `6a9e13bd6fc8f0983b9b99948120bc37f49c13e9`、GLM-5.2 `cf457fa734ab149ffef225f80893eb38c6ff5cdc`、DeepSeek-V4-Flash-0731 `7872f01b1d1fe23eabc4c98b48bffcef5a386062`。基础镜像固定`public.ecr.aws/docker/library/python@sha256:a36c24f9cbdf4fd0f52d67f0823eeac19c2028c637cecc392d97f980d4fec56b`。保留Python包`0.1.0.dev6`、npm包`0.1.0-f007`历史标签；它们不单独代表本次功能版本，以固定commit/组件版本为准。

实际源码核对model.ts聚合、recommendations.ts身份校验、Reports/Evidence展示、AnalysisApp取消/迟到/固定历史、缓存与通知生命周期：L4/L5全分页后按完整RequestKey并集计数，各至多一卡、每类最多3例，双方定位无向指纹去重，不将组数或样例数当请求数；L1–L3原门槛、Token缺失/零/P下降C上升、旧T1兼容及只读流程保留。业务GET不启动计算。没有发现业务阻断，未修改前后端业务或契约。[公共独立复审](../../../../../../docs/tasks/prefix-analysis/INDEPENDENT_REVIEW_RESULT_20261101.md)与[Token独立复审](../../../../../../docs/tasks/length-analysis/INDEPENDENT_REVIEW_RESULT_20261101.md)保持各自范围，不把此前测试累计为本轮新全量后端测试。

## 问题、修复与复验

| 编号 | 问题及处理 | 结论 |
| --- | --- | --- |
| URV2-01 | 原prepare读取共享工作树/旧dist，版本与package含V1固定分支/桌面/prompt。发布归口改为强制固定commit取源、独立前端快照构建、模型/wheel锁校验、代码归档与context逐字节核对、容器结果绑定commit/image。工具提交`2e0c9a5`；[精确交接清单](../../../../../../docs/tasks/delivery/RV2_RELEASE_TOOLS_HANDOFF_20261101.json)。隔离Git测试1 passed/0.20s验证dirty源码、旧dist不混入及坏wheel拒绝；总负责另独立1 passed/0.17s，ruff通过。 | 关闭；最终镜像和归档再核验通过 |
| URV2-02 | 实际执行现场prompt时生成器因输出目录已存在而失败。改挂载父目录，在新子目录生成；修复提交`45d9285`。失败与修复日志分别保留synthetic-generation.log及synthetic-generation-fixed.log。 | 关闭；修正命令实际通过，并从最终commit重建 |
| URV2-03 | 重启发现SQLite内部sqlite_sequence由29→34，终态行仍5。discovery.install的INSERT OR IGNORE回填推进分配计数；业务Schema/行、MAX(seq)、epoch、目录与325地址响应摘要不变。公共维护方固定同commit，12项实际验证旧游标、跨空洞分页、SSE/重连不重不漏。 | 非阻断，归口核验关闭；保留元数据写入和启动成本限制 |

[公共序号核验](../../../../../../artifacts/reviews/analysis-rv2-unified/public-sequence-check/RESULT.md)及其test_sequence_gaps.py、results.log、identity.json的SHA均录入结构化结果。冻结契约将cursor定义为不透明追加顺序，不要求连续+1。本报告不声明整个SQLite字节无变化，也未证明大历史量启动性能；本次没有临时改动冻结业务候选。

## 实际验证与边界

各套独立计数，源码和容器重复执行不相加冒称唯一用例数。

| 验证范围 | 实际结果与证据 |
| --- | --- |
| 本地前端 | typecheck/lint通过；22文件195项单元/组件通过（checks.json、unit.log） |
| 源码浏览器 | Windows Chrome，4191→8016，同实例18项通过/58.6s，其中11受控API、7真实服务（browser.log） |
| RV2只读复核 | 215个GET及L4/L5聚合核验通过；84份原RV1文件未改（rv2-readonly） |
| 最终容器身份与读取 | 4份静态dist字节完全相同；215诊断读取匹配，root/input只读、UID/GID1000:1000、8CPU/32GiB，未设置生产recipe（container-readonly.json） |
| 监控容器验收 | 三模型15合成范围、幂等回执、SSE、CSV/NDJSON字节校验通过（container-acceptance.json） |
| 最终镜像浏览器 | 56 passed/2.6min：17分析、39用户/MA监控；含身份、导出取消、排行、TTFT情景等（container-browser-run.log）。4193开发跳转已在源码回归验证；依赖/src模块导入的开发用例不在生产容器执行 |
| 新诊断真实worker | 默认空recipe配置数0；显式合成诊断`91000ba8-30bd-4d31-bf62-c151c940cb2d`达到ready，真实终态SSE通过（container-new-diagnostic.json） |
| 重启/恢复 | 用户/MA/诊断325地址响应摘要、业务Schema/行一致；另15监控范围快照/回执/导出恢复通过。内部allocator变化单独记录（container-v2-diagnostic-restart.json、container-restart.json） |
| 公共维护方补充 | 4参数探针及原发现层单元/HTTP共12 passed/4.67s，无源码变化（public-sequence-check） |
| 包体及加载 | 代码1708个成员（含目录）、1365普通文件，路径安全无重复/链接；182candidate文件匹配；实际docker load完整镜像ID一致（archive-verification.json、docker-load.log） |
| 总负责独立接收 | 13份校验文件大小/SHA/清单完整，1314个固定Git文件及182构建文件匹配；镜像config身份、平台、标签和验证绑定一致（received-release-verification.json） |

[容器统一结果](../../../../../../artifacts/reviews/analysis-rv2-unified/unified-container-validation.json)绑定最终commit及image_id。隔离测试副本仅调整截图/导入路径，保留业务断言；容器截图在container-screenshots，宽屏列表和390px窄屏L5详情已查看。原测试写死截图路径，源码回归后重新核对旧result的12份截图SHA均完全一致；副本及审计在source-browser-screenshots和screenshot-provenance-audit.json，原证据未改写。

原始失败/探针仍保留：daemon脚本CRLF及浏览器导入路径属于本轮工具配置；低candidate_limit=4使12请求覆盖不足而返回partial，后续以新submission key和limit=128得到ready，未篡改原partial；restart初版包含内部分配计数而失败，后续仍严格断言全部业务数据并单列其变化；包体探针将data/README/.gitkeep误认生产数据，最终只允许这类空布局文件。未通过删业务断言、改契约或覆盖原结果换取通过。

## 交付文件与本地管理

全部产物在WSL项目内`/home/zhangxiyue/TokenScope/artifacts/releases/tokenscope-rv2-20261101/`，不写桌面、不上传GitHub。14个实际文件，其中SHA256SUMS列出其余13个文件；目录冻结，不再补写测试或报告到该目录。

| 文件 | 字节 | SHA256 |
| --- | ---: | --- |
| [镜像包](../../../../../../artifacts/releases/tokenscope-rv2-20261101/tokenscope-rv2-20261101-image.tar.gz) | 204553967 | `951a89a4fd3cf94577239669107e4a8d80aa69426e5d7e005a96929a63a0b3d7` |
| [代码包](../../../../../../artifacts/releases/tokenscope-rv2-20261101/tokenscope-rv2-20261101-code.tar.gz) | 71071747 | `3fd0ac85e0ed59598fdd3228a61dd0d90256ae43b2fcb2e6f47f1b665f8410ea` |
| [华为Agent执行prompt](../../../../../../artifacts/releases/tokenscope-rv2-20261101/HUAWEI_AGENT_PROMPT.md) | 8609 | `88955f9613e4c4c5b06047c9c05ee26c76f5d3f6d40488a406bfe991c5664c13` |
| [release-manifest](../../../../../../artifacts/releases/tokenscope-rv2-20261101/release-manifest.json) | 6887 | `c6493df20d4160e64bb609a74496eabb7605a8f54f86edd9e00e82fec16ce02f` |

[完整SHA256SUMS](../../../../../../artifacts/releases/tokenscope-rv2-20261101/SHA256SUMS)自身SHA256为`42811bdab9b9f4558ab7966cb83d395a8b0eb2bfbe56177d018257ad05ca5072`。同目录包含compose、env示例、部署README、candidate及容器验证记录。代码包包含固定源码、正式dist、编码资产和38个wheel；不含模型权重、生产CSV/state、凭据、默认测试recipe或Docker基础镜像tar。因此现场优先load已验证镜像，缺基础镜像时不承诺只凭代码包离线重建。

本地`backup/20261101-tokenscope-rv2`提交`dd58917b8eecc9b9791fb6f4605394e6cb6a529e`，父提交为最终构建源码，仅额外跟踪小型release-manifest/SHA256SUMS；包体不上Git对象库，无upstream、未push，禁止合并main。创建使用独立index，未切换main或改动共享index；[记录](../../../../../../artifacts/reviews/analysis-rv2-unified/local-backup.json)。此分支不是异机灾备。

仅本次Compose项目tokenscope-rv2-acceptance已down（未用-v），18061验收容器停止，input/state保留。确认无其他运行容器后，按准确pid/cmdline/data-root关闭本轮启动的项目专用daemon；4191与8016前后仍HTTP200。[清理记录](../../../../../../artifacts/reviews/analysis-rv2-unified/cleanup.json)。其他session未提交修改原位保留。

## 现场边界、未决与回退

本机WSL Ubuntu-22.04、Docker26.1.4/Compose2.27.1、Python3.11.16、Node22.22.2；精确运行包版本见runtime-environment.json。[V100历史报告](../../../../../../docs/huawei/TOKEN_SCOPE_V100_ENVIRONMENT_REPORT.md)为x86_64/CentOS7内核3.10/40逻辑CPU，驱动525与NVML550曾不匹配且/home空间需重核。本包走CPU，不以本机通过推断华为当前Docker权限、空间、驱动或内核条件通过，prompt要求逐项现场预检。

华为服务启动/功能验收、真实MA数据、TTFT性能校准、生产Token策略/引用服务可达性与业务质量均未由本次测试代签。默认无recipe没有量化建议是预期；tool_calls:null保守partial、DeepSeek思考模式和真实CSV有效子集需按配置如实报告。没有新远端部署或自动生产切换授权。

切换前保存旧image_id、Compose/env及其匹配的完整state备份；失败只停新的专属服务，恢复旧镜像及匹配旧state/独立端口，不让旧镜像打开升级过的新state，不down -v、全局prune或删除旧发布。当前旧V1交付及原证据均保留。剩余现场事项由对应监控维护方沿执行prompt回传实际结果。
