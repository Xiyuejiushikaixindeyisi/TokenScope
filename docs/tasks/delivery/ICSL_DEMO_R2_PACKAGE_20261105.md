# ICSL合成演示revision2文件包（2026-11-05）

> **已撤回候选（2026-11-05）**：用户否决80条/50K revision2。停止交付/现场执行；此前启动消息失效。按用户后续指示，WSL错误包及打包/解压副本已清理；Windows桌面已撤回旧包与原始验收证据保留。WSL仅留撤回、核验及清理记录。等待新版重新验收交接，下文仅为历史制作记录。

用户通过V3产品宣传会话明确授权向本线交接制作数据与执行prompt压缩包。本轮只交付追加合成演示文件，不是V2升级/镜像重建/远程执行；本机现有18002演示服务保留，未停启或改state。本线实际环境session ID再次核实为01a1800e-80b4-7400-a78b-a84f5b6e888d。

## 交付与核验

- WSL目录：`/home/zhangxiyue/TokenScope/artifacts/releases/tokenscope-icsl-demo-r2-20261105`。
- Windows桌面：`C:\Users\ALIENWARE\Desktop\tokenscope-icsl-demo-r2-20261105`。桌面复制了tar.gz、其.sha256、PACKAGE_VALIDATION.json，三个文件均逐字节SHA一致；WSL原文件保留。
- 压缩包：`tokenscope-icsl-demo-r2-20261105.tar.gz`，1,126,557字节。
- SHA256：`249e2c2e9f707ac125a8b6fe3f4530835616bbfafbe00133d519970aa5a16eb4`。
- 内含11份内容文件及SHA256SUMS，共12文件。tar解压到独立验证目录，11项完整SHA全部通过；CSV解析确认80条。无符号链接或越界成员。
- CSV：22,411,777字节，SHA256 `f59ed3cee7544180e3b12627852a1517b6996b8383b565a708ea23f3ae7d7bb5`。
- 验证记录：[PACKAGE_VALIDATION.json](../../../artifacts/releases/tokenscope-icsl-demo-r2-20261105/PACKAGE_VALIDATION.json)。

## 内容及范围

四份必需文件：CSV、manifest.json、diagnostic-submission-template.json、HUAWEI_PROMPT.md。另有README、本机验收摘要、三个验证JSON、监控和详情两张截图、SHA256SUMS。只从白名单取文件；不含v1、真实业务数据、模型/源码/镜像、本机state、本机诊断提交文件或完整evaluation rows。包体位于忽略的artifacts，不上传GitHub。本轮未Git提交/push或创建备份分支。

数据与既有验收来自[V3本机验收](../product-v3/icsl-demo/LOCAL_ACCEPTANCE.md)。revision2合成appid demo.synthetic.icsl.glm52.cch.v2，GLM-5.2/GLM-V5.2；约50K输入、80条。已记录的本机full80离线命中35.898228%→90.051281%只用于合成机制展示，不是真实ICSL、时延/吞吐或生产收益证明。整体partial及16MiB长消息方案发布限制保留。本线此次核对已有证据、数据身份/模板/相关API源码及压缩解压，不声称重跑80条或现场通过。

随包prompt保留原执行要求，补充压缩解压校验、期望HV2身份、完整读取接口、现场占位符/分页、挂载阻断、SSH和单Markdown正文证据要求。纠正“原is_default必须不变”的过严文字：新默认选择允许变化，旧run/appid/source/revision/固定链接与结果必须保留。原作者prompt/证据未改写。

本次是授权追加合成演示，现有正常服务不冷启动；新版部署E2E停旧规则仍适用其他新版任务。真实任务优先，不清state、不覆盖前端/原成果、不改产品/全局预算/recipe，不开Token方向。现场身份或挂载不满足须报告，不能擅自升级/重启。最终仅一份Markdown，关键请求/响应/修改片段、问题复现及测试证据正文嵌入。

## 用户后续指示与WSL清理

WSL的tar.gz、相邻SHA文件、打包内容目录和解压验证副本已删除，保留PACKAGE_VALIDATION.json、撤回说明和[CLEANUP_RECORD.json](../../../artifacts/releases/tokenscope-icsl-demo-r2-20261105/CLEANUP_RECORD.json)。Windows桌面旧包SHA核对未变；产品研究目录的原始证据、服务/state与其他发布包未处理。上文路径和包体信息为历史记录，不能视为当前WSL包仍存在。

下一步等待V3新版数据验收并交接，再独立核对数据/分布/CCH/身份隔离/全量评估/现场保护要求后重新打包，以新版独立目录复制桌面、核对全部SHA，给用户新的启动消息。不得复用旧版执行授权/数值结论；已有真实数据和分析结果必须保留，不能混入或覆盖同appid真实结果。
