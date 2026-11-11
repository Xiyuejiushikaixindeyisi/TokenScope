# ICSL场景构造样本 revision3交付

2026-11-05：用户授权由V3会话验收后交本线核对、打包并复制桌面，现已完成。revision3是数据修订号，不是V3产品部署。替代撤回的80条版本；旧桌面包保留撤回标记，WSL错误包已清理。

## 文件与身份

- WSL：`/home/zhangxiyue/TokenScope/artifacts/releases/tokenscope-icsl-r3-20261105`。
- 桌面：`C:\Users\ALIENWARE\Desktop\tokenscope-icsl-r3-20261105`。
- 包：`tokenscope-icsl-r3-20261105.tar.gz`，580,566字节。
- 包SHA256：`8be11f790761fdff502ef658033611b05d983799527e3cdc1b69d8def5e73b48`。
- CSV：15,921,971字节，102条，SHA256 `e1425657987dce4ad312d33c7e40a3ac98a822ec7ed928fb7979f1dcc785678b`。
- [完整文件清单/校验](../../../artifacts/releases/tokenscope-icsl-r3-20261105/PACKAGE_VALIDATION.json)；[随包prompt](../../../artifacts/releases/tokenscope-icsl-r3-20261105/tokenscope-icsl-r3-20261105/HUAWEI_PROMPT.md)。
- 共13份内容文件+SHA256SUMS。四份必需输入、README及8份本机验收/审查证据；不含本机state/本机提交JSON/模型/源码/镜像/真实数据/旧版本。压缩包SHA、解压后13项SHA、桌面三文件与WSL对照全部通过；WSL原包保留。

## 独立核对

读取[V3验收](../product-v3/icsl-demo/revision3/LOCAL_ACCEPTANCE.md)与截图，并独立解析全部CSV：com.huawei.icsl.base，GLM-5.2，102个唯一UUID；62对话（40双请求22单请求）；system首行随机五位CCH，同对话不变，不同对话不同；时间间隔7–72秒；请求原文无demo/synthetic/合成数据字样。三份本地模型资产SHA与manifest一致。

读取当前已完成的本机full评估102条（GET分页，不新提交分析），逐行确认仅删除/messages/0/content首行billing，其余字段不变；full complete/available/display_eligible且计数与manifest一致。before P2855919/H1026688/C1829231，after P2853567/H2572672/C280895；35.949479%→90.156355%，UI35.95%→90.16%。[独立核对记录](../../../artifacts/reviews/icsl-r3-package-20261105/INDEPENDENT_REVIEW.json)。

长度均值27,999.21、标准差533.86、范围26,603–29,364来自已有真实分词证据；5K箱102条全25K–30K，仅是单柱，不能称页面显示高斯。整体partial/候选留存限制和输出0占位如实保留。构造来源在说明/manifest/回传明确，不冒称真实ICSL、推理时延/吞吐改善；页面无需加demo字段。不声称华为已通过。

## 现场要求及实际操作边界

只追加现有V2，新input目录、现场run/revision/task，核查同appid在各模型的冲突与隔离，已有真实数据/成果/固定链接/MA/四入口/L4L5保留；有冲突先停，不能覆盖真实默认结果。裸入口新选择允许变化。现有正常服务不停止，不改产品/配置/预算/recipe，不重建镜像，不复制本机state。真实任务优先，若须升级/改挂载/重启则先报告。最终一份Markdown，关键请求响应/源码（如问题涉及）/修改片段/复现/测试证据正文嵌入。

原作者资料不改，随包prompt补充校验、HV2身份、分页与现场隔离、SSH和单文档要求，纠正原default关系不变的歧义；附录与原要求按用户最新授权解释。本轮未改产品、未重启服务、未Git提交push/上传或远程执行。其他session修改保留。
