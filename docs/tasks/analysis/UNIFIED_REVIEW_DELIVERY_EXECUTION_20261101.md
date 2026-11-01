# RV2统一审查、修复复验与交付执行

2026-11-01（北京时间）。异常分析功能总负责：`01a19111-344a-75c1-84e0-14db8be08f4f`；镜像打包与审查：`01a1800e-80b4-7400-a78b-a84f5b6e888d`。

## 用户最新认可与授权

用户原话：

> 这版L4/L5展示我认可。把prompt主动发给镜像打包与审查session，先完成统一审查，发现问题由你协调对应session修复，复验通过后再打包交付，最后给我交付文件、版本和校验摘要。

本条明确认可RV2的L4/L5展示，并授权实际发送、统一审查、归口修复复验及复验通过后的打包交付；不再重复申请打包许可。不扩展为生产策略批准、现场验收或远端部署。

## 执行顺序与分工

1. 总负责发送[完整prompt](../../../prompts/sessions/ANALYSIS_UNIFIED_REVIEW_DELIVERY_RV2.md)及本条新授权，目标为已登记审查打包会话，不新建会话。
2. 审查方核对已发布main `8bfae19a28c14e93b5611114729f8cfde0d33c5e`，其中被测源码提交`10f4a0674892c9f331f262b91e6a6118a17ac4ac`。以[版本清单](VERSION_RV2_20261101.json)和实际当前字节核验，不混入共享区其他8份改动。
3. 发现问题由总负责分派：前端本会话、低命中/公共`01a18be2-7112-7aa2-919b-5137d1f1b1ad`、Token私有`01a18fcd-0464-7cf1-b435-4f394bd33e66`；发布工具/容器由审查打包会话处理。普通问题自主修复复测，范围/冻结接口变更说明后再确认。
4. 审查方独立复验，关闭阻断后基于固定源码候选正式打包、容器验证及交付。Git由总负责统一收口，发布脚本若改动先回传精确清单，避免并行提交或构建未签收的dirty源码。
5. 新产物放本项目`artifacts/releases/<实际新版本>/`，旧V1包不覆盖。回传镜像包、代码包、执行prompt、manifest和SHA256，包含必要模型/依赖/配置身份和明确未携带项。没有远端部署。
6. 总负责核对最终文件存在性、大小、SHA256、源码/配置/镜像身份与验证结论，再给用户交付入口。

## 当前状态

统一审查、归口修复复验、最终容器与归档加载检查、总负责独立接收核验均通过。交付版本`tokenscope-rv2-20261101`；固定构建源码`45d9285210dc0b9edeb86c599c7b6bcd942f60b5`已push并核实远端；后续报告/记忆提交不改变包内源码身份。发布目录冻结，未远端部署，华为现场待执行。

- [镜像包](../../../artifacts/releases/tokenscope-rv2-20261101/tokenscope-rv2-20261101-image.tar.gz)：204,553,967 bytes，SHA256 `951a89a4fd3cf94577239669107e4a8d80aa69426e5d7e005a96929a63a0b3d7`。
- [代码包](../../../artifacts/releases/tokenscope-rv2-20261101/tokenscope-rv2-20261101-code.tar.gz)：71,071,747 bytes，SHA256 `3fd0ac85e0ed59598fdd3228a61dd0d90256ae43b2fcb2e6f47f1b665f8410ea`。
- [现场执行prompt](../../../artifacts/releases/tokenscope-rv2-20261101/HUAWEI_AGENT_PROMPT.md)、[版本manifest](../../../artifacts/releases/tokenscope-rv2-20261101/release-manifest.json)、[完整SHA256SUMS](../../../artifacts/releases/tokenscope-rv2-20261101/SHA256SUMS)。镜像ID `sha256:483db762852b38ef54559cff1bb23ef668ea9296a055ce02aac44a809b427ce5`，平台linux/amd64。
- [统一审查报告](../delivery/RV2_UNIFIED_REVIEW_20261101.md)、[独立接收核验](../../../artifacts/validation/analysis-delivery-20261101/received-release-verification.json)、[归档load核验](../../../artifacts/reviews/analysis-rv2-unified/archive-verification.json)。

本轮源码195项单元/组件、18项浏览器及215只读GET通过；最终镜像56项浏览器、215诊断读取、15监控范围/导出及重启后325地址摘要检查通过，新诊断任务ready和终态SSE通过。重启引起内部sqlite_sequence增长，业务行/Schema/公开游标/目录不变；公共归口另做12项复验确认跨空洞分页/重连不丢失不重复，[归口证据](../../../artifacts/reviews/analysis-rv2-unified/public-sequence-check/RESULT.md)。不把它描述为整个SQLite字节无写入，也不承诺大历史启动性能。

总负责接收核对13份校验清单文件、代码包1314个固定Git文件、182个candidate文件全部一致；镜像归档config的SHA与完整镜像ID一致，revision/version/platform和测试绑定一致。所有包体只保留项目内，不上传GitHub；原V1交付、RV1证据和其他8份未提交文档保持原位。Token生产策略、真实业务质量、TTFT性能校准和华为现场仍按原边界，未因本机交付通过而代签。

## 过程记录

完整prompt及用户原话已通过工具发送到登记会话，工具返回目标threadId；实际执行turn `01a195f4-22fd-73b3-bc13-8b195d50d799`处于active/inProgress。审查方已明确回执接受授权、身份核实一致，并开始检查候选和发布工具；同意不并行Git、不改共享CURRENT/SESSIONS、不写桌面或远端部署。当前统一审查进行中，尚无统一通过或新交付包结论。

审查阶段回传：179项候选同时匹配工作树/固定提交，前端静态/单元、18项浏览器及215个只读GET通过，RV2业务源码未发现阻断。发现发布工具仍沿用V1版本/桌面/共享工作树取源，已归口修复；[精确交接清单](../delivery/RV2_RELEASE_TOOLS_HANDOFF_20261101.json)包含6个发布文件及其摘要。总负责复查后独立重跑隔离Git测试（1 passed/0.17s）与ruff通过；接下来统一提交、从新固定提交构建和做容器复验，尚不将源码检查通过等同容器交付通过。

发布工具与授权文档提交`2e0c9a588e87ca517947d158e3d6473d2ec4ed8f`已push并核实远端。容器阶段实际执行现场prompt发现生成器目标目录已存在，归口将挂载父目录与新建子目录分开，修正命令已在镜像实执行通过（synthetic-generation-fixed.log），首次失败证据保留；2文件后续提交`45d9285210dc0b9edeb86c599c7b6bcd942f60b5`已push且远端一致，已回传为最终构建候选。业务179项身份不变，前次镜像不作为最终交付。
