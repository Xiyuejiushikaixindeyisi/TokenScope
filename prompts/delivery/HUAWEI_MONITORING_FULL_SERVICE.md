# TokenScope完整服务：华为V100实验机执行prompt

你负责在当前华为实验机部署本次TokenScope离线交付，并实际验证服务。用户已授权本服务的环境配置、加载镜像、启动专属容器和合成可用性测试。先定位用户投递的交付目录，读取其中release-manifest.json、SHA256SUMS、compose.yaml及验收报告；缺少目录或文件时向用户索取具体路径，不猜生产数据位置。

## 身份与预检

1. 在交付目录执行`sha256sum -c SHA256SUMS`，全部通过才继续。记录release_id、source_commit、backend/frontend/schema、基础镜像digest、最终image_id及包摘要。代码包与镜像包必须同一release_id，不在现场更改源码掩盖问题。
2. 只读核对uname/架构、Docker客户端和daemon版本、context/endpoint、`docker compose version`、id、CPU affinity/cgroup、内存和交付/状态目录磁盘。参考报告为CentOS7/x86_64/内核3.10、Docker26.1.4、Compose2.27.1、40逻辑CPU、V100；这是历史快照，实际情况另记。首版CPU路径不请求GPU、不修NVIDIA驱动、不推断为Ascend。不要升级宿主内核/glibc、改共享Docker配置、安装证书或清理其他容器。
3. 选择用户可写的/home专属目录；根分区历史仅余4.3GiB，勿将包、状态和大量临时数据写入根分区。确认当前用户能访问正确Docker daemon，端口18000空闲；冲突时选择其他端口并记录，不停已有服务。Compose v2不可用或权限不足时报告具体阻断，不盲目sudo安装。

## 加载与专属环境

4. 从manifest读取image_archive，执行`docker load -i <image_archive>`，再`docker image inspect <image_tag>`，完整Id必须等于manifest.image_id，架构必须linux/amd64。不运行docker pull，不依赖现场外网或在线pip/npm安装。
5. 解压code_archive到新目录（先检查tar清单路径无绝对路径或..），读取其中deploy/monitoring/README.md。不要覆盖已有源码或运行库。
6. 首次合成验收规划新的input路径，创建专属父目录、state和report目录，input留给下一步生成器创建。复制deployment.env.example为deployment.env，写入manifest.image_tag、实际`id -u`/`id -g`、input/state绝对路径和空闲端口。不要复用生产state；保留非root、只读根/输入、8CPU、32GiB、pids限制和专属bridge网络。遇权限问题仅修正自己的专属目录，不chmod共享目录或改为privileged。
7. 用加载的镜像生成独立合成输入：执行`docker run --rm --network none --user "$(id -u):$(id -g)" -e PYTHONPATH=/app/src -v "<专属测试父目录>:/work" --entrypoint python <image_tag> /app/scripts/validation/generate_monitoring_data.py /work/input --seed 281028 --mean-requests 100 --long-per-app 1`。生成器要求input尚不存在，先建父目录而不是input。它生成每模型5appid的泊松数据、长尾和边界，DeepSeek请求显式关闭思考，仅测试使用。把deployment.env输入路径指向此生成目录。
8. 使用唯一Compose project名称（例如tokenscope-v1-20261028），运行`docker compose --env-file deployment.env -p <project> -f compose.yaml config`并检查，再`up -d --pull never`。记录容器ID、镜像ID、挂载、配额、健康状态和日志，不关闭其他服务。

## 实际验证

9. 检查`curl -fsS http://127.0.0.1:<port>/healthz`、主页和JS/CSS。读取/readyz及/models；DeepSeek缺省思考未决的503须单列，不能自动改生产默认，也不能把所有模型判为失败。GLM CP映射、GF资产等价仍需现场对齐。
10. 使用代码包里的`python3 scripts/release/verify_service.py --url http://127.0.0.1:<port> --submit-synthetic <input>/manifest.json --report <report>/before-restart.json`。该命令明确写入三个合成任务，检查15范围、H+C=P、快照/ETag、SSE持久终态、同key幂等、NDJSON SHA/数量与CSV结构/数量。要求Python3.11标准库；若宿主Python不适用，可在已加载镜像内执行同一脚本，通过容器自身127.0.0.1:8000访问并把输入/报告路径按挂载映射，不在线安装依赖。
11. 仅重启本Compose monitoring服务。执行同一脚本的`--resume <report>/before-restart.json --report <report>/after-restart.json`模式（不带--submit-synthetic），验证instance、回执和已发布快照/导出字节不变。记录实测耗时、峰值和资源，而不是把计划值填作结果。
12. 提供用户可访问的浏览器入口。默认只绑定宿主loopback，可在许可范围内从用户电脑建立`ssh -L <本地端口>:127.0.0.1:<服务端口> <实际用户>@<实际主机>`后访问localhost。不要未经授权把服务绑定公网。实际检查筛选、三模型精确值、历史/质量/详情、SSE、NDJSON/CSV导出和取消。核实secure context与showSaveFilePicker/createWritable；能力不足仅支持≤16MiB验证后下载，不能声称大文件路径通过。需要HTTPS/网络调整时先给出具体方案由用户决定。
13. 初次合成服务验收通过后报告给用户。真实CSV只在现场，在用户明确指定文件和模式后采用独立生产input/state进行真实性能验收；目标每文件<7200秒。不得复制、上传或回传原始请求正文、CSV、Token IDs、完整库或敏感配置。

## 报告与失败处理

输出一份脱敏报告：release身份、实际环境差异、全部命令/退出码、镜像/容器健康、三模型及15范围结果、SSE/恢复/导出/浏览器能力、资源和耗时、访问地址、明确通过/失败/未执行。分别记录本机容器证据、现场合成证据和现场真实数据证据。缺浏览器或生产输入时标未执行，不把curl通过当浏览器或生产验收。

遇失败保留日志和专属状态，不改业务算法或降低门槛；先核查包摘要、挂载权限、端口、旧内核兼容和资源，向用户提供最小脱敏错误。回退仅停本服务、保留新state并恢复配套发布单元；不down -v、不prune共享Docker、不删除其他任务数据。容器尚未通过时不得宣布部署完成。
