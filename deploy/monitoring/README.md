# 完整服务交付

此目录是dev6/F007完整前后端的发布入口，替代已归档的env/docker仅后端准备。CPU linux/amd64，Python3.11.16，前端由同源FastAPI挂载；默认仅绑定宿主127.0.0.1:18000。

基础镜像使用Docker Official Image在ECR的固定摘要，具体值写入交付manifest；不从浮动tag发布。构建前在WSL生成离线wheelhouse，按uv.lock/requirements.runtime.txt校验摘要。prepare_monitoring_context.py只复制明确源码、配置、前端dist、编码锁中资产和wheel，不包含生产输入、状态库、Git、凭据或上游仓库。Docker build使用--network=none和固定BASE_IMAGE。容器运行使用只读根、只读输入、独立可写/state、8CPU/32GiB、内部网络，不依赖GPU或外网。

交付目录包括镜像tar.gz、代码tar.gz、compose.yaml、deployment.env.example、release-manifest.json、SHA256SUMS、华为执行prompt和桌面验收说明。代码包包含可维护源码、前端离线dist、编码资产、离线wheelhouse及来源摘要；不承诺只靠代码包在无基础镜像时离线重建。现场应优先docker load已验证镜像，不要求重新编译。

启动前校验SHA256SUMS，docker load后核对manifest的完整image_id。复制环境模板到专用deployment.env，设置image tag、uid/gid、已创建的绝对输入/状态目录及空闲端口。使用：

```sh
docker compose --env-file deployment.env -p tokenscope-v1 -f compose.yaml config
docker compose --env-file deployment.env -p tokenscope-v1 -f compose.yaml up -d --pull never
docker compose --env-file deployment.env -p tokenscope-v1 -f compose.yaml ps
```

健康检查使用/healthz。/readyz可能因DeepSeek缺省思考未决返回503，应读取各模型诊断；不能据此静默选择生产思考默认。合成请求显式关闭思考，只代表测试输入。

首次验收必须使用独立合成input/state。镜像内generate_monitoring_data.py生成固定种子、每模型5appid的泊松数据；verify_service.py显式--submit-synthetic才写入任务，--resume只读核对重启后instance、回执、快照和两格式导出字节。其报告不包含请求正文。浏览器现场检查同源页面、SSE、筛选/详情/导出；普通远端HTTP不能代替安全上下文大文件保存验收，可按现场许可使用SSH本地转发。

回退先停本服务并备份完整state，再加载配套前后端/schema版本；不使用down -v或全局prune。涉及库序号回退必须按项目规则隔离实例。现场旧内核兼容性、资源及生产每文件<7200秒仍须实测。
