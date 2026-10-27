# TOKEN_SCOPE_V100_ENVIRONMENT_REPORT

**探测时间**: 2026-10-26 13:02–13:26 UTC（本地 21:02–21:26 CST）
**执行方式**: 只读命令探测，未安装/升级软件、未改配置、未提权、未运行容器/镜像/compose、未做压力测试。结果仅代表本次快照。

## 摘要表

| # | 项目 | 值与单位 | 所属层次 | 状态 | 证据 |
|---|------|----------|----------|------|------|
| 1 | 时间/时区 | 2026-10-26 13:0x UTC = 21:0x CST，Asia/Shanghai (+0800) | 宿主 | 已确认 | E1 |
| 2 | OS 发行版 | CentOS Linux 7 (Core)，VERSION_ID=7 | 宿主 | 已确认 | E2 |
| 3 | 内核 | 3.10.0-1160.119.1.el7.x86_64 | 宿主 | 已确认 | E2 |
| 4 | CPU 架构 | x86_64 | 宿主 | 已确认 | E2 |
| 5 | glibc | getconf/ldd 均报 2.42（非官方 CentOS7 的 2.17，banner 含自定义文案，来源待核） | 宿主 | 已确认（值按命令输出） | E2 |
| 6 | 隔离环境 | 物理机 Huawei 2288H V5；systemd PID1、无容器 marker、systemd-detect-virt=none | 宿主 | 已确认 | E3 |
| 7 | CPU 型号 | Intel(R) Xeon(R) Silver 4114 @ 2.20GHz（max 3.0GHz，L3 14MB） | 宿主 | 已确认 | E4 |
| 8 | CPU 拓扑 | 2 socket × 10 core × 2 thread = 40 逻辑 CPU；possible 0-223，online/present 0-39 | 宿主 | 已确认 | E4,E5 |
| 9 | 可调度 CPU | 40 个（affinity 0-39；nproc=40；taskset 0-39） | 宿主 | 已确认 | E4,E5 |
| 10 | cgroup CPU 配额 | v1：cpu.cfs_quota_us=-1（无配额），period 100000；cpuset.cpus=0-39 | 宿主 cgroup v1 | 已确认（可见链无限制） | E6 |
| 11 | 负载快照 | loadavg 2.84/3.76/3.49；up 19 天（背景参考，非独占保证） | 宿主 | 已确认 | E19 |
| 12 | 内存 | MemTotal 375.9 GiB；MemAvailable 352.8 GiB；swap 4 GiB 全空闲 | 宿主 | 已确认 | E7 |
| 13 | cgroup 内存 | limit≈2^63（无上限）；usage 6.1 GB(user.slice)/18.7 GB(root) | 宿主 cgroup v1 | 已确认（可见链无限制） | E8 |
| 14 | 根分区 `/` | xfs，总量 50 GiB，可用 ≈4.3 GiB（92%） | 宿主 | 已确认 | E9 |
| 15 | `/home`（工作区） | xfs，总量 ≈3.6 TiB，可用 ≈401 GiB（90%）；inode IFree 3.81e8（1%） | 宿主 | 已确认 | E9 |
| 16 | `/var/lib/docker` | /dev/sdd ext4，总量 ≈3.58 TiB，可用 ≈3.03 TiB（11%）；inode IFree 2.36e8；目录内容不可读（root 0700） | 宿主/Docker daemon | 空间已确认 / 内容权限不足 | E20 |
| 17 | GPU | 2 × Tesla V100-PCIE-32GB（PCI 0000:3b:00.0、0000:86:00.0；GPU Excluded: No） | 宿主 | 已确认（经 /proc/driver/nvidia） | E11 |
| 18 | GPU 驱动 | 内核模块 NVRM 525.105.17（2023-03-28） vs 用户态 NVML 库 550.163.01 → **版本不匹配** | 宿主 | 已确认（根因：dmesg NVRM API mismatch） | E10,E11 |
| 19 | nvidia-smi | 不可用：`Failed to initialize NVML: Driver/library version mismatch` | 宿主 | 不可用（驱动不匹配） | E10 |
| 20 | 显存 | 型号名标称 32 GB/卡（合计 64 GB）；实际使用/空闲未获得 | 宿主 | 未验证 | E10,E11 |
| 21 | CUDA Toolkit | nvcc 12.4 V12.4.99（/usr/local/cuda → NAS 上 CUDA12.4.0_CUDNN9.11.1）；另有 /usr/local/cuda-9.0 | 宿主 | 已确认 | E12 |
| 22 | Ascend 痕迹 | /usr/local/Ascend、/etc/ascend_install.info 存在，但无 npu-smi → 有安装痕迹，非 NPU 运行环境 | 宿主 | 痕迹已确认 / 工具不可用 | E13 |
| 23 | Docker 客户端 | 26.1.4（build 5650f9b），Context default | 宿主 | 已确认 | E14 |
| 24 | Docker daemon | 26.1.4；containerd 1.6.33；runc 1.1.12；**本地** unix socket（DOCKER_HOST 未设置）；Name=aarc22885 | 本地 daemon | 已确认 | E14 |
| 25 | docker info 关键项 | x86_64；内核 3.10；NCPU=40；MemTotal≈376 GiB（与宿主一致）；overlay2(extfs)；RootDir=/var/lib/docker；CgroupVersion=1；CgroupDriver=cgroupfs；DefaultRuntime=runc | 本地 daemon | 已确认 | E14,E15 |
| 26 | Docker 权限 | 用户 zhangxiyue 属 docker 组；socket 可访问（docker ps 成功） | 宿主 | 已确认 | E21 |
| 27 | Rootless | 不可见（docker info 26.1.4 无 Rootless 字段）；无 rootless 迹象，推断非 rootless | 宿主 | 不可见（推断） | E14 |
| 28 | Compose v2 插件 | `docker compose version` → v2.27.1 | 宿主 | 已确认 | E16 |
| 29 | Compose 旧命令 | `docker-compose --version` → 1.26.0 | 宿主 | 已确认 | E16 |
| 30 | Python | 3.11.16（miniconda3，`/home/aarc/zhangxiyue/miniconda3/bin/python3`）——与参考 CPython 3.11.16 一致 | 宿主 | 已确认 | E17 |
| 31 | pip / conda | pip 26.2.1（miniconda env）；conda 26.7.1 | 宿主 | 已确认 | E17 |
| 32 | uv | **未安装**（PATH 及常见目录均无） | 宿主 | 未安装 | E17 |
| 33 | git | 1.8.3.1（CentOS 7 自带）；user.email 未配置 | 宿主 | 已确认 | E17 |
| 34 | NVIDIA 容器工具 | nvidia-ctk 1.13.5；nvidia-container-cli 1.13.5；nvidia-container-runtime 1.13.5；config.toml 存在；Docker Runtimes 含 nvidia | 宿主 | 已确认（配置可见）；GPU 容器未验证 | E18,E15 |
| 35 | 两小时性能目标 / 镜像兼容性 | — | — | 未验证（本次不做性能验收与镜像运行） | — |

## 1. CPU / 内存有效约束

**CPU**
- 物理拓扑：2 socket × 10 物理核 × 2 超线程 = 40 逻辑 CPU（Intel Xeon Silver 4114）。`possible=0-223` 是平台最大扩展能力，实际 `online/present=0-39`，**可调度即 40 核**。
- `nproc --all` 输出 224 是受 `Cpus_allowed_list: 0-223` 迷惑的旧版 coreutils 行为；`nproc`（=40）、`taskset -pc`（0-39）、Python `os.sched_getaffinity(0)`（40 个，0-39）、/proc/cpuinfo（40）一致，以 40 为准。
- **cgroup 无 CPU 配额**：v1 全部控制器（无 v2 unified），`cpu.cfs_quota_us=-1`（无限）、`cpu.cfs_period_us=100000`；cpuset 根 0-39；可见的 user.slice 链同样无配额。不可排除管理侧隐藏限制，但当前进程视图无 CPU 时间上限。
- 负载快照 loadavg 2.84/3.76/3.49，相对 40 核很低，仅作背景参考。注意宿主上同时运行着 21 个 Docker 容器（daemon 统计）且 docker 组多用户共用，资源非独占。

**保守并行预算建议（推导，需真实负载验证）**
- 首版为 CPU 密集计量（Rust tokenizer + 离散事件仿真），40 逻辑 CPU 无配额限制可用。
- 考虑到共享宿主（21 运行容器、多用户 docker 组）与未做压力测试，建议 **初始并行度 8–16**（即逻辑 CPU 的 20–40%），按 `min(待分析文件数, 16)` 起步；观察实际吞吐与宿主干扰后再扩。
- 若后续确认干扰小，可逐步上探至 24–32，但本次无性能数据支撑，不宣称可满载。

**内存**
- 宿主 375.9 GiB 总量、352.8 GiB 可用；cgroup memory limit=2^63（无上限），当前用量远低于任何可能限制。首版进程为轻量计量，无内存瓶颈迹象。
- 注意 `MemTotal` 以宿主级别为准；若未来进程放入容器，容器可用量受镜像编排层（compose 未配置）约束，本次不适用。

## 2. GPU 现状（重点核实结论）

- **用户所称 V100 属实**：经内核 proc 接口（绕过 NVML）确认 2 × Tesla V100-PCIE-32GB，PCI 0000:3b:00.0 / 0000:86:00.0，GPU Excluded: No。**这是 NVIDIA 卡，不是 Ascend/NPU**（Ascend 仅有安装痕迹目录，无 npu-smi，不可用）。
- **驱动已损坏/不匹配（当前阻塞 GPU 侧）**：内核模块 NVRM **525.105.17**（2023-03-28，GCC 4.8.5 构建）与用户态 NVML 库 **550.163.01** 版本不一致，dmesg 明确 `NVRM: API mismatch: client 550.163.01 vs kernel module 525.105.17`。后果：nvidia-smi 完全不可用、无 `/dev/nvidia0`/`nvidia1` 设备节点。修复需对齐版本（降用户态库到 525 系列，或升内核模块到 550 系列）——属运维动作，本次未执行。
- **驱动 vs Toolkit 区分**：CUDA Toolkit 已安装（nvcc 12.4 V12.4.99，位于 /mnt/nas1 NFS 挂载的 CUDA12.4.0_CUDNN9.11.1；另有 cuda-9.0）。但 nvidia-smi 的 "CUDA" 字样并非 Toolkit 证据——本次 nvidia-smi 根本不可用，Toolkit 证据来自 nvcc 路径。驱动 525.105.17 属 CUDA 12.0 分支，与 NVML 550 用户态库不匹配；CUDA 实际可运行性未验证（标注：未验证）。
- **首版影响**：首版为纯 CPU 计量路径，**不依赖 GPU runtime**，驱动不匹配不构成首版硬阻塞；仅当未来需要 nvidia-smi/GPU 侧监控时才被阻塞。

## 3. Docker / Compose 可用性

- **endpoint 为本地**：DOCKER_HOST/DOCKER_CONTEXT 均未设置，context=default，socket `/var/run/docker.sock`，daemon Name=aarc22885。`docker info` 的 NCPU=40、MemTotal≈376 GiB 与宿主一致，进一步确认是本地 daemon 而非远程。
- 用户 zhangxiyue 在 docker 组，`docker ps` 可正常访问 daemon（无需 sudo，未用 sudo）。
- **Compose 两个版本均可用**：v2 插件 `docker compose version` → **v2.27.1**；旧独立命令 `docker-compose --version` → **1.26.0**。推荐使用 v2 插件。两者均可用于后续 compose up（未实际启动任何东西）。
- Runtimes 含 **nvidia**（nvidia-container-runtime 1.13.5 已注册为 daemon runtime，DefaultRuntime=runc），NVIDIA 容器工具链（nvidia-ctk/cli/runtime 均 1.13.5）与 config.toml 均存在——**工具与配置可见，但 GPU 容器未验证**；且当前驱动不匹配状态下 GPU 容器大概率不可用。首版 CPU 计量路径不应因缺 GPU runtime 被判定不可用。
- Rootless 状态不可见（docker info 的 Go 类型无 Rootless 字段），推断为非 rootless，未验证。
- 私有 registry/代理等敏感字段未导出；`/var/lib/docker` 目录内容（overlay2 等）权限不足不可读，但空间数据已通过 df 获得。

## 4. 磁盘与打包前提

- `/var/lib/docker`（独立盘 /dev/sdd，ext4）：**可用 ≈3.03 TiB**，inode 充足——离线镜像包存放无忧。
- `/home`（工作区，xfs）：可用 ≈401 GiB，inode 充足。
- **`/` 根分区仅剩 ≈4.3 GiB（92%）**：后续若向根分区写临时文件/日志需注意，产物建议放 /home 或 /var/lib/docker 所在盘。
- `/mnt/nas1` 等为 NFS 挂载（`192.168.20.50:/nas01`，NFSv3），CUDA Toolkit 位于其上；工作区已有 MemScope 系列目录，但无 TokenScope 项目目录（未创建，避免猜测路径）。

## 5. 阻塞项与待核实项

**当前阻塞**
- NVIDIA 驱动/用户态库版本不匹配（525.105.17 vs 550.163.01）→ nvidia-smi 与 GPU 计算不可用；修复需运维对齐版本。首版 CPU 计量不依赖 GPU，**不阻塞首版**。

**仅待以后打包/性能验收核实**
- 两小时单模型性能目标：未验收（本次明确不做性能验收）。
- 镜像兼容性：未构建/拉取/运行任何镜像，CentOS 7 + 定制 glibc 2.42 环境下 Rust tokenizer/Python 编排的镜像内运行行为未验证。
- uv 未安装（参考 uv 0.12.9），若打包流程依赖 uv 需另行安装（本次未装）。
- git 1.8.3.1 过旧（仅记录）。
- GPU 显存/利用率读数、CUDA 可运行性：待驱动修复后验证。
- Rootless 状态、/var/lib/docker 内部结构：不可见/未验证。
- 并行预算（8–16 起步）基于本快照推导，需真实负载验证。

---

## 6. 命令证据（内嵌精简版）

采集时间均为 UTC。脱敏不影响版本/资源判读。

**E1 时间与时区** — 2026-10-26 13:02:48 UTC，rc=0
```
$ date -u '+%F %T UTC'
2026-10-26 13:02:48 UTC
$ date '+%F %T %Z (%z)'
2026-10-26 21:02:48 CST (+0800)
$ readlink -f /etc/localtime
/usr/share/zoneinfo/Asia/Shanghai
```

**E2 OS / 内核 / 架构 / glibc** — 2026-10-26 13:02:48 UTC，rc=0
```
$ cat /etc/os-release
NAME="CentOS Linux"  VERSION="7 (Core)"  VERSION_ID="7"
$ uname -s -r -m
Linux 3.10.0-1160.119.1.el7.x86_64 x86_64
$ getconf GNU_LIBC_VERSION        # rc=0
glibc 2.42
$ ldd --version | head -1          # rc=0
ldd (👴 老爷机尊享版 GNU libc 👴) 2.42
```
注：CentOS 7 官方 glibc 为 2.17，此处 2.42 且 banner 含自定义文案，疑似定制构建；仅按命令输出记录，来源待核。

**E3 隔离环境（宿主判定）** — 2026-10-26 13:02:54 UTC
```
$ ls /.dockerenv /.containerenv      # 均不存在，rc=2
$ cat /proc/1/sched | head -1
systemd (1, #threads: 1)
$ /usr/bin/systemd-detect-virt
none
$ cat /sys/class/dmi/id/product_name /sys/class/dmi/id/sys_vendor
2288H V5
Huawei
```
`/proc/1/cgroup` 各控制器均挂根路径（`11:net_prio,net_cls:/` …），本会话在 systemd user.slice（`1:name=systemd:/user.slice/user-1015.slice/session-18190.scope`）。结论：物理机宿主 shell，非容器/VM。

**E4 CPU 结构** — 2026-10-26 13:12:53 UTC，rc=0
```
$ lscpu | grep -E 'Architecture|CPU\(s\)|Thread|Core|Socket|NUMA node|Model name|CPU max|L3'
Architecture: x86_64
CPU(s):                40
Thread(s) per core:    2
Core(s) per socket:    10
Socket(s):             2
NUMA node(s):          2
Model name:            Intel(R) Xeon(R) Silver 4114 CPU @ 2.20GHz
CPU max MHz:           3000.0000
L3 cache:              14080K
$ nproc
40
$ nproc --all
224
$ python3 -c 'import os; print(len(os.sched_getaffinity(0)), sorted(os.sched_getaffinity(0)))'
40 [0, ..., 39]
$ taskset -pc $$     # rc=0
pid 9731's current affinity list: 0-39
```

**E5 CPU 计数澄清** — 2026-10-26 13:17:52 UTC
```
$ grep -c '^processor' /proc/cpuinfo
40
$ cat /sys/devices/system/cpu/online /sys/devices/system/cpu/possible /sys/devices/system/cpu/present /sys/devices/system/cpu/offline
0-39
0-223
0-39
40-223
$ grep Cpus_allowed_list /proc/self/status
Cpus_allowed_list:  0-223
```
说明：`possible 0-223` 为平台扩展能力；`online/present/affinity=0-39` 才是实际可用。`Cpus_allowed_list 0-223` 为宽容内核展示，与 taskset/affinity 的 0-39 不一致，后者为准。

**E6 cgroup v1 CPU 配额** — 2026-10-26 13:18:02 UTC
```
$ cat /sys/fs/cgroup/cpu/user.slice/cpu.cfs_quota_us /sys/fs/cgroup/cpu/user.slice/cpu.cfs_period_us
-1
100000
$ cat /sys/fs/cgroup/cpuset/cpuset.cpus
0-39
$ cat /sys/fs/cgroup/cpu.max   # v2 标记，不存在
cat: /sys/fs/cgroup/cpu.max: No such file or directory
$ grep ' cgroup ' /proc/mounts | head -2
cgroup /sys/fs/cgroup/systemd cgroup ... name=systemd
cgroup /sys/fs/cgroup/cpuset cgroup ... cpuset
```
可见链（root、user.slice）均 quota=-1（无 CPU 时间上限）。pids：user.slice pids.current=284，无 pids.max。

**E7 内存** — 2026-10-26 13:13:10 UTC，rc=0
```
$ grep -E 'MemTotal|MemAvailable' /proc/meminfo
MemTotal:       394169752 kB
MemAvailable:   370003292 kB
SwapTotal:        4194300 kB   SwapFree: 4194300 kB
$ free -h
Mem:  375G total, 20G used, 340G free, 14G buff/cache, 352G available
```

**E8 cgroup 内存** — 2026-10-26 13:18:02 UTC
```
$ cat /sys/fs/cgroup/memory/user.slice/memory.limit_in_bytes /sys/fs/cgroup/memory/user.slice/memory.usage_in_bytes
9223372036854771712     # =2^63-1，无上限
6124437504              # 6.1 GB
$ cat /sys/fs/cgroup/memory/memory.limit_in_bytes /sys/fs/cgroup/memory/memory.usage_in_bytes
9223372036854771712
18685460480             # 18.7 GB（根）
```

**E9 磁盘** — 2026-10-26 13:18:05 UTC，rc=0
```
$ df -T /; df -T /home
/dev/mapper/centos-root  xfs 52403200 47831856 4571344  92% /
/dev/mapper/centos-home  xfs 3847258716 ... 421069440  90% /home   # 可用 ≈401 GiB
$ df -i /home
/dev/mapper/centos-home  Inodes=384913792 IUsed=3837451 IFree=381076341 IUse%=1
```

**E10 GPU：nvidia-smi 不可用 + 根因** — 2026-10-26 13:17:59 / 13:18:35 UTC
```
$ nvidia-smi --query-gpu=index,name,driver_version,memory.total,memory.free,utilization.gpu --format=csv
Failed to initialize NVML: Driver/library version mismatch
NVML library version: 550.163
$ dmesg | grep -i nvidia | tail -2
NVRM: API mismatch: the client has the version 550.163.01, but
NVRM: this kernel module has the version 525.105.17.
$ ls /dev/nvidia[0-9]*
ls: cannot access /dev/nvidia[0-9]*: No such file or directory
```

**E11 GPU：内核 proc 直接证据（2× V100）** — 2026-10-26 13:25:10 UTC，rc=0
```
$ cat /proc/driver/nvidia/version
NVRM version: NVIDIA UNIX x86_64 Kernel Module  525.105.17  Tue Mar 28 18:02:59 UTC 2023
GCC version:  gcc version 4.8.5 20150623 (Red Hat 4.8.5-44) (GCC)
$ ls /proc/driver/nvidia/gpus/
0000:3b:00.0  0000:86:00.0
$ cat /proc/driver/nvidia/gpus/0000:3b:00.0/information
Model:    Tesla V100-PCIE-32GB
DMA Size: 36 bits   Bus Location: 0000:3b:00.0
Device Minor: 0     GPU Excluded: No
$ cat /proc/driver/nvidia/gpus/0000:86:00.0/information
Model:    Tesla V100-PCIE-32GB
Device Minor: 1     GPU Excluded: No
```
（UUID/Video BIOS 字段被内核遮蔽为 `?`，无需额外脱敏。）

**E12 CUDA Toolkit（nvcc）** — 2026-10-26 13:17:59 UTC
```
$ command -v nvcc
/usr/local/cuda/bin/nvcc
$ nvcc --version | grep -E 'release|Build'
Cuda compilation tools, release 12.4, V12.4.99
Build cuda_12.4.r12.4/compiler.33961263_0
$ readlink -f /usr/local/cuda
/mnt/nas1/programs/CUDAToolkits/CUDA12.4.0_CUDNN9.11.1
$ ls /usr/local/cuda-9.0/bin/nvcc    # 另有 2019 年的 cuda-9.0
```
注：Toolkit 位于 NFS 挂载（`192.168.20.50:/nas01 /mnt/nas1 nfs vers=3`）。驱动 525.105.17 属 CUDA 12.0 分支，与 NVML 550 库不匹配；CUDA 可运行性未验证。

**E13 Ascend 痕迹（非 NPU 环境）** — 2026-10-26 13:17:59 UTC
```
$ ls -ld /usr/local/Ascend /usr/local/Ascend/driver /etc/ascend_install.info
drwxr-xr-x 3 root root 20 Feb 12  2026 /usr/local/Ascend
drwxr-xr-x 5 root root 52 Feb 12  2026 /usr/local/Ascend/driver
drwxr-xr-x 2 root root  6 Feb 12  2026 /etc/ascend_install.info
$ ls /usr/bin/npu-smi /usr/local/bin/npu-smi
ls: cannot access ...: No such file or directory
```

**E14 Docker 版本 / endpoint / info** — 2026-10-26 13:18:08 UTC
```
$ docker --version
Docker version 26.1.4, build 5650f9b
$ echo "DOCKER_HOST=${DOCKER_HOST:-unset} DOCKER_CONTEXT=${DOCKER_CONTEXT:-unset}"
DOCKER_HOST=unset DOCKER_CONTEXT=unset
$ ls -l /var/run/docker.sock
srw-rw---- 1 root docker 0 Oct  7 11:23 /var/run/docker.sock
$ docker context ls --format '{{.Current}}|{{.Name}}'
true|default
$ docker version | grep -E 'Version|API|OS/Arch|Server:'
Client: 26.1.4  API 1.45  linux/amd64   # 亦含 Server: 26.1.4，containerd 1.6.33，runc 1.1.12
$ docker info --format 'Name={{.Name}}|ServerVersion={{.ServerVersion}}|Arch={{.Architecture}}|Kernel={{.KernelVersion}}|NCPU={{.NCPU}}|MemTotal={{.MemTotal}}|Driver={{.Driver}}|RootDir={{.DockerRootDir}}|CgroupVersion={{.CgroupVersion}}|CgroupDriver={{.CgroupDriver}}'
Name=aarc22885|ServerVersion=26.1.4|Arch=x86_64|Kernel=3.10.0-1160.119.1.el7.x86_64|NCPU=40|MemTotal=403629826048|Driver=overlay2|RootDir=/var/lib/docker|CgroupVersion=1|CgroupDriver=cgroupfs
```
`Rootless=` 模板字段报错（该版本类型无此字段）→ 不可见。`docker info` 中 Containers=43（21 running）、Images=633、SecurityOpts=[seccomp builtin]；私有 registry/代理字段已排除不导出。

**E15 Docker Runtimes** — 2026-10-26 13:18:38 UTC
```
$ docker info --format 'DefaultRuntime={{.DefaultRuntime}}|Runtimes={{.Runtimes}}'
DefaultRuntime=runc|Runtimes=map[io.containerd.runc.v2:... nvidia:... runc:...]
```
（runtimes 明细含 nvidia-container-runtime 注册项，其余为 OCI 特性描述，省略。）

**E16 Compose（两个版本）** — 2026-10-26 13:18:08 UTC，均 rc=0
```
$ docker compose version
Docker Compose version v2.27.1
$ docker-compose --version
docker-compose version 1.26.0, build unknown
```

**E17 工具链** — 2026-10-26 13:17:55 / 13:18:44 UTC
```
$ readlink -f "$(command -v python3)"; python3 --version
/home/aarc/zhangxiyue/miniconda3/bin/python3.11
Python 3.11.16
$ python3 -m pip --version
pip 26.2.1 from /home/aarc/zhangxiyue/miniconda3/lib/python3.11/site-packages/pip (python 3.11)
$ conda --version
conda 26.7.1
$ uv --version            # 未安装
bash: uv: command not found        # 且 .local/bin、/usr/local/bin、/usr/bin 均无 uv，rc=2
$ git --version
git version 1.8.3.1
```

**E18 NVIDIA 容器工具** — 2026-10-26 13:18:14 UTC
```
$ nvidia-ctk --version
NVIDIA Container Toolkit CLI version 1.13.5
$ nvidia-container-cli --version | head -2
cli-version: 1.13.5   lib-version: 1.13.5
$ nvidia-container-runtime --version | head -2
NVIDIA Container Runtime version 1.13.5   spec: 1.1.0-rc.2
$ ls -l /etc/nvidia-container-runtime/config.toml
-rw-r--r-- 1 root root 897 Jul 18  2023 /etc/nvidia-container-runtime/config.toml
```
工具/配置存在且 Docker Runtimes 已含 nvidia，但未运行测试容器 → GPU 容器支持标"未验证"。

**E19 负载快照** — 2026-10-26 13:18:14 UTC
```
$ uptime
21:18:14 up 19 days, 9:55, 2 users, load average: 2.84, 3.76, 3.49
```

**E20 /var/lib/docker 磁盘与权限** — 2026-10-26 13:18:40 UTC
```
$ df -T /var/lib/docker; df -i /var/lib/docker
/dev/sdd  ext4 3845559112 391095252 3259096548  11% /var/lib/docker   # 可用 ≈3.03 TiB
/dev/sdd  Inodes=244195328 IUsed=7839319 IFree=236356009 IUse%=4
$ ls /var/lib/docker
ls: cannot open directory /var/lib/docker: Permission denied     # root 0700，内容不可见
```

**E21 docker 组与 socket 访问** — 2026-10-26 13:26:13 UTC
```
$ id -nG
GeneralAI docker aarcnas GeneralAI_nas
$ timeout 10 docker ps --format '{{.ID}}' | head -3
c561cce543cc 93e79ab7a4b8 05535bfec07e        # daemon 可访问，容器 ID 已脱敏
```
（docker 组含大量成员，成员清单属其他用户信息，不导出。）

---

**结论**：环境为华为 2288H V5 物理机上的 CentOS 7 宿主（非容器/VM），2× Intel Xeon Silver 4114（40 逻辑 CPU，无 cgroup 配额），375.9 GiB 内存，磁盘充足（注意 / 根分区仅余 ~4.3 GiB）；GPU 确认为 **2× Tesla V100-PCIE-32GB**（非 Ascend），但**驱动 525.105.17 与用户态 NVML 550.163.01 不匹配**导致 nvidia-smi 与 GPU 计算当前不可用。Docker 26.1.4 本地 daemon 可访问，Compose v2.27.1 与独立 1.26.0 均可用，NVIDIA 容器工具链 1.13.5 已配置（GPU 容器未验证）。首版 CPU 计量路径不受 GPU 驱动问题影响；两小时性能目标与镜像兼容性未验证。并行建议 8–16 起步，需真实负载确认。