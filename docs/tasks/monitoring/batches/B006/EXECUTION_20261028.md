# B006本轮交付执行（2026-10-28）

用户已明确授权：先将现有修改合并main并push GitHub，然后开始Docker构建、镜像打包和代码交付包；产物在WSL构建并移动到Windows桌面，包体不上GitHub，本地backup分支管理，同时交付华为Agent部署与测试prompt。该授权覆盖本轮具体完整服务候选的常规构建实现与验证，不沿用旧backend_only方案。

前置已完成：F007人工通过、[统一审查](PREPACKAGE_REVIEW_20261028.md)通过，现有修改31ab864711741e85385a7f9dc94317d6bd8b7267已推送origin/main，远端SHA已核实。开始delivery/package-management源码分支，交付前将通过检查的交付工具合并main并显式push；包体只留本地。

## 本轮具体范围与门槛

- linux/amd64 CPU完整镜像：后端dev6、前端F007、schema3/view1/S0 1.0.0；Python3.11.16、固定requirements/uv.lock与8个Tokenizer/Template资产。前端dist已独立复现且与审查摘要一致。
- 基础镜像：public.ecr.aws/docker/library/python:3.11.16-slim-bookworm；固定RepoDigest `sha256:a36c24f9cbdf4fd0f52d67f0823eeac19c2028c637cecc392d97f980d4fec56b`，本机image ID `sha256:3ad37ccd1797321f4bda14f483941a4f7a2b9eca454847b22652e59f5baab8c9`。Docker Hub连接EOF、bullseye标签不存在，改为同官方镜像ECR来源的bookworm固定版本；旧内核兼容仍待现场。
- 新入口deploy/monitoring，不复用旧env/docker发布路径。明确白名单context；预下载并按锁SHA验证wheel，镜像安装时--network none、pip --no-index --require-hashes；镜像包含前端离线资源，不含生产数据/状态/凭据/研究仓库。
- Compose独立project、默认loopback18000、非root、只读根/输入、专属state、8CPU/32GiB、专属bridge网络（初版internal-only端口问题已修正，见结果）。健康检查只判断healthz，DeepSeek生产默认未决单列。
- 本地先验证标准库部署检查脚本，然后容器三模型5appid合成输入→15范围/指标/ETag/请求/NDJSON SHA/CSV/SSE/幂等→重启instance/receipt/结果字节不变；实际浏览器再验证F007同源页面与导出。容器约束与离线性记录实际inspect，不把配置文件存在当验证通过。
- 通过后docker save压缩镜像和代码归档，manifest绑定源码commit、base digest、image ID、配置/资产/资源/代码包/镜像包摘要及测试层级。代码包包含源码、dist、编码资产与wheelhouse。保留失败日志，不反复用镜像替代业务开发。
- WSL完成后移动整个交付目录到Windows桌面TokenScope-monitoring-v1-20261028；前后SHA核对。项目内保留小型清单、验证记录及桌面引用，本地backup/20261028-monitoring-v1提交小型manifest管理包体位置与摘要，不将包体装入Git对象库、不push backup。
- 华为prompt执行预检/校验load/专属部署/合成及浏览器验证/重启恢复；现场真实CSV及<7200秒单文件目标另验，不回传正文、不升级共享宿主或修GPU。

回退仅本服务、保留state与回执、配套schema/前后端；不清共享8000、不down -v、不prune。首次Docker工具与daemon放项目artifacts内，非系统安装；测试daemon完成后停止，本机预览8000不动。

实际命令与日志：artifacts/builds/monitoring-v1-20261028；最终实测、修正及交付摘要见[RESULT_20261028](RESULT_20261028.md)。
