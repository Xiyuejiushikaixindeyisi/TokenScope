# TokenScope 华为 V100 机器环境探测任务

你是运行在目标机器上的 Agent。请为 TokenScope 首版 Token 监控做一次只读环境探测，返回一份有命令证据的 Markdown 报告，供另一台机器上的设计/开发会话评估环境和并行预算。以下就是本次任务，不启动业务开发或部署。

## 背景与边界

用户称目标机器使用 V100，请实际核实，不能按“华为机”推断为 Ascend/NPU。TokenScope 首版分析每模型一份 CSV，以 CPU 上的 Rust tokenizer、Python 编排、缓存离散事件仿真和统计为主，不运行模型前向。性能目标为每文件单模型两小时内，但本次环境探测不做性能验收。

后续可能将应用依赖打入镜像，通过 Docker Compose 启动并提供离线镜像包；本次仅收集前提信息。不要安装/升级软件、改配置、重启服务、提权、执行 sudo、拉取/构建/加载/启动镜像、运行 compose up 或压力测试。不要读取凭据、请求数据、其他用户进程命令行，或导出完整环境变量和 Docker 配置。仅使用已经存在的命令；缺失、权限不足或超时照实记录，不为完成探测修改系统。

## 需要核实的内容

1. **探测位置与系统**：UTC/北京时间、OS 发行版、内核、CPU 架构、glibc；当前处于宿主机、容器、VM 还是其他隔离环境。可参考 `date -u`、`/etc/os-release`、`uname -r`、`uname -m`、`getconf GNU_LIBC_VERSION`。不能确定的层次写未知，不将容器内信息直接称为宿主信息。

2. **实际可用 CPU**：CPU 型号、socket/物理核/逻辑 CPU 总数；当前进程可调度 CPU 的数量与列表；cpuset/affinity 与 cgroup CPU 时间配额分别报告。参考 `lscpu`、`nproc`、`nproc --all`、`/proc/self/status` 的 Cpus_allowed_list，若 Python 已有可读 `os.sched_getaffinity(0)`。由 `/proc/self/cgroup` 和挂载信息定位当前 cgroup，检查 v2 的 cpu.max、cpuset.cpus.effective，或 v1 对应的 quota/period/cpuset；检查可见的父级限制，不能固定假设 cgroup 位于根路径。将 quota/period 转为允许的 CPU 时间份额，区分它与可调度逻辑 CPU 数；不可见的上级限制写未知。记录一次负载快照用于背景，不能当成独占资源保证。输出用于受控并行的保守 CPU 预算建议及推导，明确仍需真实负载验证。

3. **内存与磁盘**：主机/当前命名空间可见的 MemTotal、MemAvailable；适用 cgroup 的内存上限与当前使用量，以及可见父级限制。指出容器可用量可能受配额限制，不能只报告宿主总内存。对已经存在的项目/工作目录，以及能够确认的 Docker 数据目录，读取文件系统类型、剩余空间、inode；不全盘搜索、不做写入测速。目录未知就标未知，不假设本机与开发机路径一致。

4. **GPU 与驱动**：优先使用 `nvidia-smi --query-gpu=index,name,driver_version,memory.total,memory.free,utilization.gpu --format=csv`，记录数量、实际型号、驱动和显存状态；不要报告 UUID/序列号或其他用户任务明细。若存在 `nvcc`，读取其版本。分别说明驱动版本、驱动支持的 CUDA 能力与已安装 CUDA Toolkit，不能把 nvidia-smi 的 CUDA 字样当作 Toolkit 已安装证据。容器内 GPU 不可见也不等于宿主没有 GPU。

5. **Docker 与 Compose（重点）**：分别记录 `docker --version`、`docker version` 中客户端和服务端版本及可访问性；先核实当前 Docker endpoint 是本地还是远程，避免将远程 daemon 的 CPU/驱动信息当成本机。只报告 endpoint 类型，地址脱敏。如果 daemon 不可访问，保留客户端结果和失败原因，不能提权或重启。对于确认的本地 daemon，仅选择性读取 `docker info` 中的架构、内核、NCPU、MemTotal、存储驱动、数据目录、cgroup 版本/驱动、rootless 状态、Runtimes/DefaultRuntime；不要倾倒包含私有 registry、代理或地址的完整输出。分别执行 `docker compose version`（插件）与 `docker-compose --version`（旧独立命令），报告哪个可用、具体版本和错误，不能只写“有 Compose”。无需预设最低版本或替用户升级。

6. **现有运行工具与容器 GPU 支持**：检查已有 Python、pip/uv、Git 版本；与开发参考 CPython 3.11.16、uv 0.12.9 比较，仅记录，不安装。若有 `nvidia-ctk`、`nvidia-container-cli`、`nvidia-container-runtime`，读取各自版本，并结合 Docker 的 runtime 信息说明配置是否可见。工具存在不等于 GPU 容器已经验证；本次不运行测试容器，标记“未验证”。首版 CPU 计量路径不应因缺 GPU runtime 被直接判定不可用。

## 输出格式

只交付一份 `TOKEN_SCOPE_V100_ENVIRONMENT_REPORT.md`：先给摘要表（项目、值与单位、所属层次、状态、证据编号），再解释 CPU/内存有效约束、当前 Docker/Compose 可用性及待确认项，最后内嵌精简命令证据。每项证据包含命令、采集时间、退出码及关键 stdout/stderr；脱敏不影响版本/资源判读。状态区分已确认、未安装、权限不足、不可见、未验证，不能用猜测填空。

明确哪些是当前阻塞、哪些仅待以后打包/性能验收核实；不要宣称两小时目标已达成或镜像已兼容。结果只代表本次快照。若当前任务已有明确项目目录，可将这一份报告保存其中并返回内容；否则直接完整回复 Markdown，不创建猜测路径。不要另交脚本、日志包、截图或多份附件，关键证据直接嵌入正文。
