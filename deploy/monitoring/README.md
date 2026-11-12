# 完整服务构建与交付

2026-11-12：本轮用户明确暂不编写华为机prompt。构建使用`--defer-onsite-prompt`，candidate/release manifest标记`onsite_prompt_status=deferred_by_user`，交付根目录不提供执行prompt；下文“包含prompt/按包内prompt执行”仅适用于明确附带说明的其他版本，不授权本轮现场部署。用户将在本机打包结束后另行讨论现场任务。

当前发布范围为监控V2/MA及异常分析RV2正式前后端；CPU linux/amd64，同源FastAPI静态资源。旧monitoring-v1-20261028包和manifest冻结，不能覆盖。

有效打包授权后，prepare_monitoring_context.py须指定固定--source-commit；源码、配置、部署文件和版本从Git对象读取，前端在独立快照目录用已安装锁定工具构建，不读共享dirty源码或旧dist。wheelhouse逐包SHA须在requirements.runtime.txt中；模型资产须匹配固定commit编码锁。构建用固定BASE_IMAGE摘要、--network=none及pip --no-index --require-hashes。candidate.json记录实际组合版本、commit、dist、模型与文件摘要。

Dockerfile包含监控/MA/用户/诊断完整Python源码、正式dist、编码资产和运行依赖，不含生产输入/state、凭据或默认测试策略。运行Compose使用非root、只读root/input、独立可写state、8CPU/32GiB、专属bridge及127.0.0.1端口绑定；默认空业务recipe。

先在独立input/state完成容器检查，package_monitoring.py验证合成监控与重启报告、浏览器结果、绑定image_id/source_commit的完整服务validation。代码包git archive固定commit，加同一dist/模型/wheels/candidate，并逐文件核对context；镜像由docker save生成。release-manifest.json、SHA256SUMS、现场prompt及结果一同交付，仅项目artifacts/releases新目录。backup分支仅本地，按本次授权完整复制Windows桌面并校验，保留WSL原包、不上传包体。

使用manifest实际tag、宿主UID/GID及新建绝对input/state目录填写deployment.env：

```sh
docker compose --env-file deployment.env -p tokenscope-rv2 -f compose.yaml config
docker compose --env-file deployment.env -p tokenscope-rv2 -f compose.yaml up -d --pull never
```

现场步骤只按包内HUAWEI_AGENT_PROMPT.md执行：真实Trace3/MA18、用户监控→MA→第一次用户验收→指定appid两类异常，最终仅一份Markdown嵌关键源码和证据。先停旧服务再用空state冷启，宿主127.0.0.1:18002通过SSH转发访问。优先docker load，不要求联网安装/重建；代码包虽带wheelhouse/编码资产/dist，不带Docker基础镜像或模型权重。healthz是存活，readyz按模型解释，DeepSeek缺省思考不可擅自置false。默认无Token策略不是故障。现场CPU/磁盘/Docker/Compose须重核，不以V100名称推断GPU依赖。本机通过不代签现场。

回退先停止专属项目并保全state，恢复旧镜像及配套备份state；不让旧版本读取可能升级的新库，不删除旧包，不使用down -v或全局prune。
