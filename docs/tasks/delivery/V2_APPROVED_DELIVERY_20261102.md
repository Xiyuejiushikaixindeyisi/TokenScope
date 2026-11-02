# V2批准版本交付：2026-11-02

本机交付完成：固定源码已push main，WSL镜像构建、容器独立复验、代码/镜像归档与docker load验证通过，完整14文件已复制Windows桌面且逐项SHA256一致。旧包及WSL原件保留，backup仅本地。华为真实数据与两次用户验收尚未执行，不能以本机合成结果代签。

用户明确认可V2可以交付；UIR-03暂不修、留V3，不作本版阻断。UIR-01/02已闭环，四入口“用户监控、搜索与排行、异常分析、MA集群监控”、UI-02/UI-04及最后L4/L5展示保持。本轮没有新增业务设计或修改UIR-03。[历史审查/修复原文](../../../achieve/2026-11-02/v2-approved-delivery/README.md)。

## 固定版本

| 项目 | 实际值 |
| --- | --- |
| 发布版本 | `tokenscope-v2-approved-20261102` |
| 源码提交及已核实origin/main源码检查点 | `b17cdc07b0a351d0f5c4fb1b26f0e05be2b3a0af` |
| 镜像tag | `tokenscope/full-service:tokenscope-v2-approved-20261102` |
| 镜像ID | `sha256:a38d0ab2cfe26154c96adb5e876538893005e5cb100fc5c53640823c391683a8` |
| 平台/构建环境 | linux/amd64，WSL Ubuntu-22.04 |
| 基础镜像 | `public.ecr.aws/docker/library/python@sha256:a36c24f9cbdf4fd0f52d67f0823eeac19c2028c637cecc392d97f980d4fec56b` |
| 本地备份分支 | `backup/20261102-tokenscope-v2-approved` |
| 本地备份提交 | `4b71d52ac979ce2b5a3157d8176083549c753fc0` |

从已push固定commit生成上下文和dist，网络关闭的Docker构建使用锁定离线wheel/模型资产；未读共享dirty源码或旧dist。实际容器/app/candidate.json、镜像revision/version标签、HTTP四个资源和已复审c1逐项一致；无/app/src或dist覆盖挂载。源码/资源/锁/冻结S0及用户2.0.0、MA1.0.0/模型资产身份见[版本清单](VERSION_V2_APPROVED_20261102.json)、包内candidate.json与[结构化交付结果](V2_APPROVED_DELIVERY_RESULT_20261102.json)。后续仅交付记录/记忆收口提交，不改变本包固定源码和资源。

## 本轮实际容器验证

核实旧TokenScope服务与相关端口关闭后，用新空state、单一候选和全新Chrome上下文启动；实例`bf9a6f1f-5eaa-4fd1-af9f-ef1d675a916d`。先验证生产默认无测试recipe、空目录，再仅为本机合成覆盖挂载独立fixture配置；该覆盖不进入镜像或交付目录，华为不得使用。

- 15个监控范围、3模型、CSV/NDJSON摘要和真实worker回执通过；独立29行搜索筛选/排序、用户来源运行、MA真实容器API和诊断任务通过。
- 85项不同浏览器用例通过：监控42、异常分析18、FS-01来源3、联合8、展示修复10、鼠标4。覆盖搜索、P90 TTFT、固定运行、缓存/事件生命周期、响应丢失恢复、导出取消/损坏摘要/空结果；没有删除断言来换通过。
- 独立135次实际鼠标位置与API排名/hash/源记录/Token数对照通过，宽度390/1440/1920/2560及resize、1005条第二段均覆盖；UIR-03按用户决定用明确打开/刷新目标运行，不扩大为本轮路由修复。
- 40组批准HTML/实际容器截图与DOM保留，无页面异常、业务写入或横向溢出。人工查看代表性的用户页、MA图、L4/L5和移动页；四资源SHA同已独立复审版本。截图不是现场用户签字。
- 历史S0延迟响应与多个catalog回调保持固定run，不提交计算。正常stop、确认端口释放、start后120个GET摘要和四控制库业务表记录保持；GET不新增计算。15范围恢复及11项重启浏览器复测通过，后者不累加到85个不同用例。
- 代码tar安全路径/无重复/无链接，全部Git文件对固定commit blob及182个candidate摘要通过；镜像tar配置摘要/标签匹配，实际docker load后ID仍相同。

前置c1的226单元/组件及2项固定提交工具测试记录保留，不冒充本轮容器测试。测试副本仅适配当前fixture身份/导入路径和批准展示定位；原数值/身份/缓存/恢复/导出断言保持。全部原始证据在`artifacts/reviews/v2-approved-20261102/`；原评审失败/修复证据未改写。

## 交付文件与校验

WSL原件：`/home/zhangxiyue/TokenScope/artifacts/releases/tokenscope-v2-approved-20261102`。
Windows验收目录：`C:\Users\ALIENWARE\Desktop\tokenscope-v2-approved-20261102`。

| 文件 | bytes | SHA256 |
| --- | ---: | --- |
| tokenscope-v2-approved-20261102-code.tar.gz | 71491773 | `d7609dfaf9eaae0db01e00b563d608efbcee06c70705ccbab4b590d4d03f317b` |
| tokenscope-v2-approved-20261102-image.tar.gz | 204548673 | `1996e82c0053985441ded8fbe8af93480130998290f95612732258fbfe954f5e` |
| SHA256SUMS自身 | 1185 | `5bff93eb831c1cacb3726c62180bc4d9ea3c6525f4b8da207c50571de4be2a74` |

完整目录另含HUAWEI_AGENT_PROMPT.md、compose.yaml、deployment.env.example、DEPLOYMENT_README.md、candidate.json、release-manifest.json及容器验证记录。没有SYNTHETIC_ACCEPTANCE包。13条SHA256SUMS及清单自身，共14文件在两端逐项字节数/SHA一致；[全部文件校验记录](V2_APPROVED_DESKTOP_COPY_20261102.json)。

本地backup仅增加manifest和SHA256SUMS指针管理包体，代码/镜像压缩包不进入Git对象。main仅源码/说明/非敏感交付记录，所有backup无推送。其他8份session未完成文档修改仍保留；未唤醒休眠角色。旧V1、RV2和FS01交付及既有桌面包均保留。

## 华为执行与未决项

直接给华为agent使用[当前完整prompt](../../../prompts/delivery/HUAWEI_V2_REAL_DATA_20261102.md)，包内为同字节HUAWEI_AGENT_PROMPT.md。必须校验SHA和真实环境，核实停旧容器/进程、端口退出后新空state冷启，不能另换端口并行旧版。

真实根`/home/aarc/zhangxiyue/10.20_Trace_extract/`：Trace3CSV供用户监控及其扩展异常分析；MA18CSV字段和pre/now窗口独立核对。先用户监控（搜索排序/P90 TTFT）再MA，第一次用户验收且明确appid后才两类异常，随后第二次用户验收。真实TTFT的T/W/K/τ、思考模式、MA配对与业务recipe依据现场核实，缺失不能造数/默填或称通过；性能校准与功能验证分开。本机不保证真实数据覆盖所有规则。

用户电脑执行`ssh -L 18002:127.0.0.1:18002 zhangxiyue@10.67.43.44`，访问http://localhost:18002。华为最终只回传`HUAWEI_V2_ACCEPTANCE_REPORT.md`，关键源码/diff、容器内复现、配置、日志/HTTP和修复前后结果直接嵌正文；不要求额外附件。

本地验收容器与本次私有Docker daemon已正常停止，Windows/WSL相关端口均关闭，state/日志/包体保留。现场部署只需docker load，不承诺缺少基础镜像时能完全离线重建源码包。

回退时正常停止本次专属Compose项目（不down -v/prune），保全失败state；用旧镜像配对应旧state备份启动，不用旧镜像读新迁移库，也不并行混用。UIR-03明确留V3；其余现场待验证项按上文如实记录，不降低门槛或替用户签字。

## 文档与记忆

23份闭环评审/交接/旧prompt按原字节归档到achieve，并保留可导航副本/原入口跳转；原证据、冻结契约和已发布文件不动。11个session入口和角色记忆同步当前交付/真实数据/两次验收/单文档协议，CURRENT与本线记忆已收口。[归档映射](../../../achieve/2026-11-02/v2-approved-delivery/ARCHIVE_MAP.json) · [固定规则](../../operations/DELIVERY_ACCEPTANCE_RULES.md) · [必须遵守的教训](../../../memory/DELIVERY_LESSONS.md)。已记录展示漂移、未停旧服务、记忆滞后、擅改计划和旧现场prompt错误，并以实际检查记录约束后续工作。
