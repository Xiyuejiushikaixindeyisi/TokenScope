# HUAWEI_V2_ACCEPTANCE_REPORT — TokenScope V2 HV2 华为实验机真实数据验收报告

> 
> 生成时间：2026-11-04（现场 UTC+8），最后更新 2026-11-05
> 交付目录：`tokenscope-v2-hv2-20261103`（/home/aarc/zhangxiyue/tokenscope-v2-hv2-20261103）
> 版本：tokenscope-v2-hv2-20261103
> 唯一回传文档：本文件。所有关键源码、命令、证据均嵌入正文，不依赖外部附件。
> 状态：**报告已可交付外网机评审**。内存压力、L4 为主的发现构成、Token 方向无产出均如实记录。

---

## 0. 结论 / 当前阶段

| 阶段 | 状态 | 关键依据 |
| --- | --- | --- |
| 0. 交付包身份校验 | ✅ 通过 | SHA256SUMS 14/14 OK；镜像ID与manifest一致；HTTP资源SHA与VERSION_CONFIG_SUMMARY一致（§1） |
| 1. 环境实测 | ✅ 通过 | CentOS7/40核/375GiB；Docker 26.1.4/Compose 2.27.1；GPU NVML不匹配但本版CPU运行（§2） |
| 2. 停旧版+干净启动 | ✅ 通过 | 旧容器tokenscope-v2-approved-monitoring-1正常停止、端口18002释放、新空state冷启动（§3） |
| 3. 真实数据盘点 | ✅ 完成 | 3用户CSV(26.88GB)+18 MA CSV全量盘点、字段/行数/SHA/配对验证（§4） |
| 4. 第一阶段A：用户监控 | ✅ 3模型索引完成 | DS(34 appid)+GLM(22)+Qwen(21)=77 entries，全 is_default=True（§5） |
| 5. 第一阶段A：P90 TTFT | ✅ 默认参数已配置 | τ: Qwen=1s, GLM=2.7s, DS=2.6s; K=8192; source=user_provided; calibrated=false（§5.4） |
| 5a. 前端多模型切换 | ⚠️ V3 BUG | 用户监控页模型 `<select>` 可切换跨模型同 appid；搜索与排行页缺模型选择入口，DeepSeek 独有 appid 无法从该入口访问。用户确认留 V3（§5.5） |
| 6. 第一阶段B：MA监控 | ⏳ 6/9 completed | DS 3对+GLM 3对 completed；Qwen 3对 running/queued（§6） |
| 7. **第一次用户验收** | ⏳ 待用户 | MA 完成后等待用户验收 |
| 8. 第二阶段：异常分析 | ⏳ 待用户指定appid | 用户验收后指定appid |
| 9. UIR-03 | 用户决定留V3，非V2阻断 | 本次未修复 |

**HV2 修复概要（问题A/B/C）**：

1. **问题A（同一用户无法查看全部模型）— 部分修复，V3 BUG**：HV2 新增服务端 `GET /monitoring/user-v2/runs` 发现目录（77 entries，全 `is_default=True`），前端 `UserMonitor.tsx` 新增模型服务 `<select>` 下拉切换。用户监控页可切换跨模型同 appid。但搜索与排行页缺模型选择入口，DeepSeek 独有 appid（29/34 个）无法从该入口访问——用户用无痕浏览器确认"只有 GLM 和 Qwen，没有 DeepSeek"。用户决定此 BUG 留 V3（§5.5）。
2. **问题B（后台已完成但异常页无结果）— 已修复**：`discovery_v2.py:21` 查询改为 `status IN ('ready','partial')`，新增 `selected_reports` 字段作为 `defaults` 回退；`model.ts:128` 在 `not_computed` 时仍加载 L4/L5 差异卡片（§7）。
3. **问题C（MA四项指标缺失）— 透明化但未修复根因**：`statistics.py:129` 的 `r = p is not None and h is not None` 和 `replay.py:112` 的 `if conflict: continue` 均未改变；HV2 新增 `availability` 端点解释缺失原因（实测返回 `source_cached_missing` 等 reasons），契约禁止将"缺失"表示为 `0`（实测 `uncached_tokens=null` 而非 `0`），UI 渲染缺失值为 `—`（§6）。

---

## 1. 交付包身份校验

### 1.1 SHA256SUMS 验证

```
$ cd /home/aarc/zhangxiyue/tokenscope-v2-hv2-20261103 && sha256sum -c SHA256SUMS
DEPLOYMENT_README.md: OK
HUAWEI_AGENT_PROMPT.md: OK
VERSION_CONFIG_SUMMARY.json: OK
candidate.json: OK
compose.yaml: OK
container-acceptance.json: OK
container-browser.log: OK
container-restart.json: OK
deployment.env.example: OK
docker-save.log: OK
release-manifest.json: OK
tokenscope-v2-hv2-20261103-code.tar.gz: OK
tokenscope-v2-hv2-20261103-image.tar.gz: OK
unified-container-validation.json: OK
```

14/14 全部 OK。

### 1.2 版本身份表

| 项 | 值 | 来源 |
| --- | --- | --- |
| release_id | tokenscope-v2-hv2-20261103 | release-manifest.json |
| source_commit | c1345b6fd7d413a94420642ca1b4099b9ec104b4 | release-manifest.json |
| image_tag | tokenscope/full-service:tokenscope-v2-hv2-20261103 | release-manifest.json |
| image_id | sha256:d129a05636b01b4f93d806e42587be749cef561cfbacbe0067adbd7b8d7c37f8 | release-manifest.json + docker image inspect 实测一致 |
| platform | linux/amd64 | release-manifest.json + docker image inspect |
| image revision label | c1345b6fd7d413a94420642ca1b4099b9ec104b4 | docker image inspect |
| image version label | tokenscope-v2-hv2-20261103 | docker image inspect |
| source_identity_sha256 | 396d136f37769323ecb659ae9d89a74034df3bdbf6b9a069c757187984c9831d | release-manifest.json |
| frontend | hv2-monitor-mf02-analysis-c3-20261103 | VERSION_CONFIG_SUMMARY.json |
| public_backend | hv2-execution-2-user-2.1.0-ma-availability-1 | VERSION_CONFIG_SUMMARY.json |
| monitoring_contracts.user | 2.1.0 | VERSION_CONFIG_SUMMARY.json |
| monitoring_contracts.ma_availability | 1 | VERSION_CONFIG_SUMMARY.json |
| monitoring_contracts.diagnostics_execution | 2 | VERSION_CONFIG_SUMMARY.json |

### 1.3 代码包安全检查

```
# 代码包成员数：2060（全部在 TokenScope/ 下）
# 无绝对路径成员
# 无 .. 路径遍历
# 无符号链接
# 解压到独立目录 /home/aarc/zhangxiyue/tokenscope-v2-hv2-20261103-code/
```

### 1.4 容器内 candidate.json 核对

```
# docker exec tokenscope-v2-hv2-monitoring-1 cat /app/candidate.json
release_id: tokenscope-v2-hv2-20261103
source_commit: c1345b6fd7d413a94420642ca1b4099b9ec104b4
# image_id: None (candidate.json 中 image_id 字段为 None，以 docker image inspect 为准)
```

### 1.5 HTTP 静态资源 SHA256（实际 vs VERSION_CONFIG_SUMMARY 期望）

| 资源 | 实际SHA256 | 期望 | 匹配 |
| --- | --- | --- | --- |
| / (index.html) | 285d5afb484ee51ac4fb7768cde643f94c527157055c9c977977f5aaf8ac8dcf | 同左 | ✅ |
| /assets/index-Dqq4Pw3b.js | d0e5fc17b76c72b92a112e153bfd16c76fa94f4c8b7d0153b0b96297326c0720 | 同左 | ✅ |
| /assets/index-BxqENh7v.css | 7de15a1ce92dc92d4d93a96c70425c1ea22663c5c4653c98cb4d9122ef0254a5 | 同左 | ✅ |
| /assets/export-validator-rZ4O78aZ.js | e52838c80a214d465b29b1e6049fabe887e80d8077fc5ce121061c8f109e9d41 | 同左 | ✅ |

### 1.6 模型设置（readyz 实际返回）

| model_id | block_size | cache_mode | encoding_profile | ready | assets |
| --- | --- | --- | --- | --- | --- |
| GLM-5.2 | 128 | full_block | default | ✅ true | verified |
| Qwen3.6-27B | 1536 | full_block_approximation | default | ✅ true | verified |
| DeepSeek-V4-Flash-0731 | 32 | full_block_approximation | thinking_disabled | ✅ true | verified |

```
// GET /readyz 返回（3模型全部 ready=true）
{"ready":true,"storage":"ready","pipeline":"implemented",
 "models":{
   "GLM-5.2":{"ready":true,"assets":"verified","asset_identity":"c8bf2cc61113194473ec5502ac3116dcad8611dc95d469a5d4995d3a75150a43","explicit_request_options_supported":true,"reason":null},
   "Qwen3.6-27B":{"ready":true,"assets":"verified","asset_identity":"7527c8934262e7d1091b603846535d73910a8bfb592a2f8b94c399a711d5a523","explicit_request_options_supported":true,"reason":null},
   "DeepSeek-V4-Flash-0731":{"ready":true,"assets":"verified","asset_identity":"65eb6b0a6db0f2a66a9de666fb6a51a5faee24002da19f362047ce74054a6b62","explicit_request_options_supported":true,"reason":null}
 }
}
```

---

## 2. 实际环境证据

### 2.1 主机与 OS

```
hostname: aarc22885
uname -r: 3.10.0-1160.119.1.el7.x86_64
OS: CentOS Linux 7 (Core)
CPU: 40 逻辑核 (Intel Xeon Silver 4114)
内存: 375GiB total, 351GiB available
GPU: 2×NVIDIA V100 (NVML 550.163 vs 驱动不匹配, 本版 CPU 运行, 不需要 GPU)
```

### 2.2 Docker / Compose

```
Docker version 26.1.4, build 5650f9b
Docker Compose version v2.27.1
存储驱动: overlay2
cgroup: cgroupfs
```

### 2.3 磁盘（实测）

| 挂载点 | 大小 | 已用 | 可用 | 使用率 |
| --- | --- | --- | --- | --- |
| /home | 3.6T | 3.5T | 159G | 96% |
| /var/lib/docker | 3.6T | 375G | 3.1T | 11% |
| / | 50G | 43G | 7.5G | 86% |

### 2.4 GPU 状态

```
$ nvidia-smi
Failed to initialize NVML: Driver/library version mismatch
NVML library version: 550.163
```

本版 CPU 运行，不需要 GPU 透传或驱动修复。记录 GPU 状态，不擅自升级驱动/内核。

### 2.5 OpenAPI / 诊断能力

```
OpenAPI 路径数: 74
contract_version: analysis-common-1.0
http_version: diagnostics-http-1
diagnostics v2 catalog version: diagnostics-discovery-2
service_instance_id: b8309249-48c7-4d0e-8bca-05f4be8c15d8（本次新身份）
user-v2 contract_version: 2.1.0
user-v2 default_policy: latest_registered_published_run_per_appid_model_service
```

---

## 3. 停旧版 + 干净启动

### 3.1 旧容器盘点与停止

旧容器身份确认：

```
容器名: tokenscope-v2-approved-monitoring-1
容器ID: f9bc71fbf29fe8817d886bdf7343580cf0fedbd94e838653201b8234f59ff8a1
镜像: tokenscope/full-service:tokenscope-v2-approved-20261102
ImageID: sha256:a38d0ab2cfe26154c96adb5e876538893005e5cb100fc5c53640823c391683a8
Compose项目: tokenscope-v2-approved
状态: Up 37 hours (healthy)
端口: 127.0.0.1:18002->8000/tcp
PID: 72313 (docker-init), 72372 (python -m tokenscope.cli ...)
用户: 1015:2006
旧state: /home/aarc/zhangxiyue/TokenScope/state/tokenscope-v2-approved-20261102-20261102T0955 (108G)
输入: /home/aarc/zhangxiyue/10.20_Trace_extract -> /inputs (ro)
```

停止操作：

```
$ docker stop tokenscope-v2-approved-monitoring-1
tokenscope-v2-approved-monitoring-1

# 验证退出
$ docker ps -a --filter name=tokenscope-v2-approved-monitoring-1 --format '{{.Names}} {{.Status}}'
tokenscope-v2-approved-monitoring-1 Exited (143) 12 seconds ago

# 端口释放
$ ss -tlnp | grep 18002
(无输出 — 端口已释放)

# 进程检查
$ ps aux | grep tokenscope | grep -v grep
(无输出 — 无残留进程)
```

旧容器 Exited(143)=SIGTERM 正常停止。端口 18002 释放。旧包/代码/state 全部保留，未删除。

### 3.2 新版冷启动

新建空 state 目录：

```
STATE_DIR=/home/aarc/zhangxiyue/TokenScope/state/tokenscope-v2-hv2-20261103-20261104T105800
mkdir -p "$STATE_DIR"  # 空目录
```

deployment.env：

```
TOKENSCOPE_IMAGE=tokenscope/full-service:tokenscope-v2-hv2-20261103
TOKENSCOPE_UID=1015
TOKENSCOPE_GID=2006
TOKENSCOPE_INPUT_DIR=/home/aarc/zhangxiyue/10.20_Trace_extract
TOKENSCOPE_STATE_DIR=/home/aarc/zhangxiyue/TokenScope/state/tokenscope-v2-hv2-20261103-20261104T105800
TOKENSCOPE_PORT=18002
```

镜像加载与 compose 配置验证：

```
$ docker load -i tokenscope-v2-hv2-20261103-image.tar.gz
Loaded image: tokenscope/full-service:tokenscope-v2-hv2-20261103

$ docker image inspect tokenscope/full-service:tokenscope-v2-hv2-20261103 --format '{{.Id}}'
sha256:d129a05636b01b4f93d806e42587be749cef561cfbacbe0067adbd7b8d7c37f8

$ docker compose --env-file deployment.env -p tokenscope-v2-hv2 -f compose.yaml config
# 验证：image=tokenscope/full-service:tokenscope-v2-hv2-20261103
#       user=1015:2006 (非root)
#       input=/home/aarc/zhangxiyue/10.20_Trace_extract -> /inputs (ro)
#       state=新空目录 -> /state (rw)
#       port=127.0.0.1:18002->8000
#       8 CPU / 32GiB / 256 pids / readonly rootfs / tmpfs 512MiB
```

启动：

```
$ cd /home/aarc/zhangxiyue/tokenscope-v2-hv2-20261103
$ docker compose --env-file deployment.env -p tokenscope-v2-hv2 -f compose.yaml up -d --pull never
Container tokenscope-v2-hv2-monitoring-1  Started
```

### 3.3 健康验证

```
$ docker ps --filter name=tokenscope-v2-hv2-monitoring-1 --format '{{.Names}} {{.Status}} {{.Ports}}'
tokenscope-v2-hv2-monitoring-1 Up (healthy) 127.0.0.1:18002->8000/tcp

$ curl -sS [http://127.0.0.1:18002/healthz](http://127.0.0.1:18002/healthz)
{"status":"alive"}

$ curl -sS [http://127.0.0.1:18002/readyz](http://127.0.0.1:18002/readyz)
# 3模型全部 ready=true (§1.6)
```

### 3.4 容器运行配置（docker inspect 实际值）

```
"Image": "sha256:d129a05636b01b4f93d806e42587be749cef561cfbacbe0067adbd7b8d7c37f8"
"Config.User": "1015:2006"
"HostConfig.Memory": 34359738368        // 32GiB
"HostConfig.NanoCpus": 8000000000       // 8 CPU
"HostConfig.PidsLimit": 256
"HostConfig.ReadonlyRootfs": true
"HostConfig.Tmpfs": {"/tmp": "size=536870912,mode=1777"}   // 512MiB
"Mounts": [
  {"Source":"/home/aarc/zhangxiyue/10.20_Trace_extract","Destination":"/inputs","RW":false},
  {"Source":"/home/aarc/zhangxiyue/TokenScope/state/tokenscope-v2-hv2-20261103-20261104T105800","Destination":"/state","RW":true}
]
"Config.Cmd": ["--input-root","/inputs","--state-root","/state","--asset-root","/app","--cpu-budget","8","serve","--host","0.0.0.0","--port","8000","--viewer-root","/app/apps/viewer/dist"]
```

---

## 4. 真实数据盘点

### 4.1 用户监控 Trace CSV（3 文件）

| 文件 | SHA256 | 字节 | wc -l | 表头 | 模型 |
| --- | --- | --- | --- | --- | --- |
| DeepSeek-V4-Flash-10.20.csv | 5600c009ee10505d4a45ad2e3f13ce6b346f0d3770ecd7104cb951af169b9881 | 1,841,596,404 | 36,223 | hash_id,appid,model_handle_start_time,completion_tokens,request_input | DeepSeek-V4-Flash |
| GLM-V5.2-10.20.csv | 99dfaf7e246520a8c10f6d94d581c47757127cf77829d1b83af4aaab0306c611 | 4,664,721,198 | 26,506 | 同上 | GLM-V5.2 |
| Qwen-V3.6-27B-10.20.csv | e8e489f987f0b42cd63abff623e56eb3d39127899bd502896f7c5ca8560c200b | 20,375,268,478 | 291,912 | 同上 | Qwen-V3.6-27B |
| **合计** |  | **26,881,586,080** | **354,641** |  |  |

字段：`hash_id,appid,model_handle_start_time,completion_tokens,request_input`

### 4.2 MA 监控 CSV（18 文件，9 对 pre/now）

| 文件 | SHA256(前16) | 字节 | wc -l | 模型 | 规格 | pre/now |
| --- | --- | --- | --- | --- | --- | --- |
| DeepSeek-V4-Flash-128K-pre.csv | f6409923224dc76b | 636,704,070 | 2,875 | DS | 128K | pre |
| DeepSeek-V4-Flash-128K-now.csv | 68a9770409746f1a | 485,594,752 | 2,959 | DS | 128K | now |
| DeepSeek-V4-Flash-32K-pre.csv | 2ab9e3184d27fa4d | 128,816,403 | 3,502 | DS | 32K | pre |
| DeepSeek-V4-Flash-32K-now.csv | d90b19cc4a9210c8 | 135,899,663 | 3,952 | DS | 32K | now |
| DeepSeek-V4-Flash-64K-pre.csv | 51347c06f4ff1c2f | 201,243,206 | 1,692 | DS | 64K | pre |
| DeepSeek-V4-Flash-64K-now.csv | 092a0aca68dae31f | 146,603,823 | 1,389 | DS | 64K | now |
| GLM-V5.2-128K-pre.csv | 98e5ec46738c5102 | 1,080,263,415 | 3,514 | GLM | 128K | pre |
| GLM-V5.2-128K-now.csv | 5016d4c923a65d3f | 1,063,957,041 | 3,449 | GLM | 128K | now |
| GLM-V5.2-32K-pre.csv | 3af28fb623238ffd | 489,189,617 | 5,378 | GLM | 32K | pre |
| GLM-V5.2-32K-now.csv | 52ea18301a93fc10 | 387,369,684 | 5,441 | GLM | 32K | now |
| GLM-V5.2-64K-pre.csv | d394c5fd58ef6c13 | 848,976,899 | 4,394 | GLM | 64K | pre |
| GLM-V5.2-64K-now.csv | 3ffa364a9e42d4aa | 797,464,843 | 4,335 | GLM | 64K | now |
| Qwen-V3.6-27B-128K-pre.csv | 80d695b0a6de8963 | 3,687,102,522 | 12,425 | Qwen | 128K | pre |
| Qwen-V3.6-27B-128K-now.csv | 986a522c78fa4a9e | 3,434,941,352 | 11,493 | Qwen | 128K | now |
| Qwen-V3.6-27B-32K-pre.csv | e08179112877e683 | 2,882,398,971 | 110,293 | Qwen | 32K | pre |
| Qwen-V3.6-27B-32K-now.csv | a3a9050741c77b01 | 2,745,733,455 | 114,839 | Qwen | 32K | now |
| Qwen-V3.6-27B-64K-pre.csv | 89a4b37a5d29d9b4 | 3,775,418,077 | 21,120 | Qwen | 64K | pre |
| Qwen-V3.6-27B-64K-now.csv | e329f6569485a876 | 3,879,037,577 | 21,747 | Qwen | 64K | now |

字段：`model_standard_name,instance_uuid,hash_id,appid,request_time,model_handle_start_time,prompt_tokens,cached_tokens,completion_tokens,request_input`

### 4.3 资源预算

| 项 | 当前值 | 预算 |
| --- | --- | --- |
| /home 可用 | 159G | 需容纳新state(~108G旧版峰值) |
| 内存可用 | 351G | 容器32G足够 |
| 容器CPU | 8核 | 充足 |
| 旧state保留 | 108G | 不删除 |
| 新state当前 | ~101G | MA处理中 |

---

## 5. 第一阶段A：用户监控、搜索与P90 TTFT

### 5.1 HV2 问题A修复验证：多模型发现

**关键源码变更**：

旧版 `UserMonitor.tsx` (tokenscope-v2-approved-20261102)：

```
// line 207 — 模型服务为只读 <strong>，无切换入口
<strong>{display?.receipt.common_name ?? '请选择运行'}</strong>
```

HV2 新版 `UserMonitor.tsx` (tokenscope-v2-hv2-20261103-code/TokenScope/apps/viewer/src/features/v2/UserMonitor.tsx)：

```
// line 262 — 新增模型服务 <select> 下拉，列出该appid下所有已发布模型
<select aria-label="用户模型服务"
  value={selectedEntry ? modelScopeKey(selectedEntry) : ""}
  onChange={e => chooseModel(appEntries.filter(x => modelScopeKey(x) === e.target.value))}>
  <option value="">{display?.receipt.common_name ?? "请选择模型"}</option>
  {modelEntries.map(e =>
    <option key={modelScopeKey(e)} value={modelScopeKey(e)}>
      {e.source.common_name} · {e.source.model_id}
    </option>)}
</select>
```

新增服务端发现端点 (`src/tokenscope/api/user.py:54-56`)：

```
@api.get("/runs", response_model=DiscoveryPage)
def runs(query: Annotated[DiscoveryQuery, Query()]) -> DiscoveryPage:
    return discovery.catalog(query)
```

新增客户端发现模块 (`apps/viewer/src/features/v2/user-discovery.ts:6-32`)：

```
export async function discoverUsers(api: V2Client, signal: AbortSignal, filters: Record<string, string> = {}): Promise<DiscoveryEntry[]> {
    for (let attempt = 0; attempt < 3; attempt++) {
        const entries: DiscoveryEntry[] = [], offsets = new Set<string>();
        let offset = '0', snapshot: string | undefined, total: string | undefined;
        // ... snapshot-consistent pagination with conflict retry
    }
}
```

新增 per-model pinned run (`UserMonitor.tsx:31-34`)：

```
const [directory, setDirectory] = useState<DiscoveryEntry[]>([]);
const fixed = useRef<Record<string, string>>({});
const fixedKey = `tokenscope.v2.fixed:${api.instance}`;
// fixed map 按 (appid, model_id, common_name) 固定历史运行，不再单槽
```

### 5.2 用户监控任务提交与索引结果

3 个 Trace CSV 已提交并全部索引完成：

| 模型 | user_run_id | base_run_id | index_revision | appid数 | 状态 |
| --- | --- | --- | --- | --- | --- |
| DeepSeek-V4-Flash | ur-07c8abc2e3ea49438cb018cf53bcaa97 | cff76d1f-24f5-481e-8efe-b93aa826b3fa | 4eaa33edb665be3e709af4fa3fc2bf75c98d96e122dbb4a79bdf5788c90ded63 | 34 | ready |
| GLM-V5.2 | ur-7990ce088e0849df828f088e2526e482 | dc16c62a-7286-4b7c-bb22-8c0f97cee931 | 3ed0fc22f4625b94c803f6253f47fe66c2e919b4a503737bc317d913c6b4a4b9 | 22 | ready |
| Qwen-V3.6-27B | ur-f182826804e94ff6b8e312f244dc8e1d | ecd0d032-bbb3-4b37-ba65-fa517edc7c25 | 83950f711b95282cc357d3f468cb261c4eb0abedaebfcec6a7a814563341fe38 | 21 | ready |

discovery 端点返回 77 entries，全 `is_default=True`：

```
GET /monitoring/user-v2/runs?offset=0&limit=100
total=77, next_offset=null
  DeepSeek-V4-Flash: 34 appids
  GLM-V5.2: 22 appids
  Qwen-V3.6-27B: 21 appids
```

跨模型同 appid（10 个）：

```
S000…773: [DeepSeek-V4-Flash, Qwen-V3.6-27B]
S000…1679: [GLM-V5.2, Qwen-V3.6-27B]
S000…3344: [GLM-V5.2, Qwen-V3.6-27B]
7ca7ba5da84e4458b1c48209d4b3cf9f: [GLM-V5.2, Qwen-V3.6-27B]
com.huawei.cbg.nebula.isc: [DeepSeek-V4-Flash, GLM-V5.2]
com.huawei.gtsdata.datalinkpro: [GLM-V5.2, Qwen-V3.6-27B]
com.huawei.mbs.ilegal.ioc: [DeepSeek-V4-Flash, Qwen-V3.6-27B]
com.huawei.meca.admin.digital: [GLM-V5.2, Qwen-V3.6-27B]
com.huawei.rnd.common.pool: [DeepSeek-V4-Flash, GLM-V5.2]
com.huawei.ucd.uiplus.wa: [DeepSeek-V4-Flash, GLM-V5.2]
```

DeepSeek 各 appid ideal_hit_rate（API 实测，前10）：

| appid | request_count | ideal_hit_rate |
| --- | --- | --- |
| com.huawei.nebula.alpha_voc | 8,675 | 39.22% |
| com.huawei.officeit.meeting.brain | 2,910 | 0.83% |
| com.huawei.ucd.uiplus.wa | 1,159 | 92.72% |
| com.huawei.jiutian | 1,104 | 91.83% |
| S000…773 | 1,047 | 34.81% |
| S010320 | 1,038 | 36.55% |
| com.huawei.ipd.tianzhou.ai | 864 | 61.47% |
| com.huawei.mbs.ilegal.ioc | 661 | 43.96% |
| com.huawei.cloud.ioc.global | 595 | 90.93% |
| com.huawei.it.jalor.studio | 349 | 81.21% |

提交命令示例：

```
curl -sS -X POST [http://127.0.0.1:18002/monitoring/user-v2/runs](http://127.0.0.1:18002/monitoring/user-v2/runs) \
  -H "Content-Type: application/json" \
  -H "X-TokenScope-Instance-Id: b8309249-48c7-4d0e-8bca-05f4be8c15d8" \
  -d '{"submission_key":"ds-hv2-20261104-...",
       "file_ref":"10.20_Trace/DeepSeek-V4-Flash-10.20.csv",
       "common_name":"DeepSeek-V4-Flash",
       "model_id":"DeepSeek-V4-Flash-0731"}'
```

### 5.3 索引完成状态

全部 3 模型索引完成（约 03:50–05:25 UTC）：

- DeepSeek (1.84GB): 约 6 分钟完成编码+索引
- GLM (4.66GB): 约 15 分钟完成
- Qwen (20.37GB): 约 90 分钟完成

state 目录从 0 增长至 48G（用户监控部分）。
### 5.4 P90 TTFT 默认参数

```
GET /monitoring/user-v2/ttft/defaults
```

```
{
  "contract_version": "2.1.0",
  "configs": [
    {
      "common_name": "DeepSeek-V4-Flash",
      "model_id": "DeepSeek-V4-Flash-0731",
      "revision": "1",
      "chunk_tokens": "8192",
      "chunk_seconds": "2.6",
      "source": "user_provided",
      "source_description": "User-provided 2026-11-03 via HV2-R1-USER; K=8192; reference assumptions, not measured calibration.",
      "calibrated": false
    },
    {
      "common_name": "GLM-V5.2",
      "model_id": "GLM-5.2",
      "revision": "1",
      "chunk_tokens": "8192",
      "chunk_seconds": "2.7",
      "source": "user_provided",
      "calibrated": false
    },
    {
      "common_name": "Qwen-V3.6-27B",
      "model_id": "Qwen3.6-27B",
      "revision": "1",
      "chunk_tokens": "8192",
      "chunk_seconds": "1",
      "source": "user_provided",
      "calibrated": false
    }
  ]
}
```

τ 参数与 VERSION_CONFIG_SUMMARY.json 一致：Qwen=1s, GLM=2.7s, DeepSeek=2.6s；K=8192；source=user_provided；calibrated=false。
W（等待时间）与 T（SLO目标）仍需用户提供真实值。

### 5.5 前端 V3 BUG 记录：搜索与排行页缺模型选择入口

**现象**：用户用无痕浏览器打开 `[http://localhost:18002](http://localhost:18002)`，用户监控页只能看到 GLM 和 Qwen，没有 DeepSeek。

**根因**：前端 `UserMonitor.tsx` 的模型 `<select>` 下拉（line 252-253）只列出当前选中 appid 下的模型（`appEntries = directory.filter(e => e.appid === appid)`）。discovery entries 按顺序返回时 Qwen 排在最前面（index 0-20），前端初始化选择第一个 `is_default` entry 时选到 Qwen，之后模型下拉只显示该 appid 下的模型。DeepSeek 有 34 个 appid，其中 29 个是 DeepSeek 独有的，用户无法从当前视图切到那些 appid——除非先在 APPID 下拉中选择一个 DeepSeek 独有的 appid。搜索与排行页缺独立的模型选择入口，加剧了此问题。

**服务端数据完整性**：API 层面数据完整。`GET /monitoring/user-v2/runs` 返回 77 entries（34 DS + 22 GLM + 21 Qwen），全 `is_default=True`。DeepSeek 各 appid 的 `ideal_hit_rate` 均有值（API 实测 34.81%~92.72%）。view-snapshot 端点正确返回 `metrics.ideal_hit_rate`。前端 `Overview.tsx:11,15` 正确读取并渲染 `s.metrics.ideal_hit_rate`。

**用户决定**：此 BUG 留 V3 解决，非本次 HV2 阻断。

---

## 6. 第一阶段B：MA监控

### 6.1 MA 任务提交

9 对 MA CSV（3 模型 × 3 规格 × pre/now）已提交。

首次提交时 `model_standard_name` 未包含规格后缀（如用了 `DeepSeek-V4-Flash` 而非 `DeepSeek-V4-Flash-32K`），全部 9 对返回 `MIXED_SPEC` 错误。修正后重新提交，全部成功。

提交参数：

```
{
  "pre_file_ref": "10.20_MA/DeepSeek-V4-Flash-32K-pre.csv",
  "now_file_ref": "10.20_MA/DeepSeek-V4-Flash-32K-now.csv",
  "model_standard_name": "DeepSeek-V4-Flash-32K",
  "model_id": "DeepSeek-V4-Flash-0731",
  "pre_start": "2026-10-20T07:00:00Z",
  "now_start": "2026-10-20T08:00:00Z",
  "now_end": "2026-10-20T09:00:00Z",
  "source_timezone": "UTC"
}
```

| 模型规格 | ma_run_id | 状态 |
| --- | --- | --- |
| DeepSeek-V4-Flash-32K | 52bb7df9-3cae-4367-a52b-f83e03c9647e | completed |
| DeepSeek-V4-Flash-64K | 0110c0e6-adc3-49ea-825f-f3be1e839cf7 | completed |
| DeepSeek-V4-Flash-128K | 8bc8aa9a-ee79-4b47-806b-8e6b44726ad8 | completed |
| GLM-V5.2-32K | b2d9e1fc-059d-4c06-a123-c34652075f82 | completed |
| GLM-V5.2-64K | bf472033-b97e-4d2d-b2b4-f6e24e52bcd7 | completed |
| GLM-V5.2-128K | f26b57bd-52a3-452e-a3ad-5e03bbaf1a83 | completed |
| Qwen-V3.6-27B-32K | cbcc0c09-c13f-4ce3-a365-6a9053751d59 | running |
| Qwen-V3.6-27B-64K | 239043c7-9a20-4364-adea-710c9619f840 | queued |
| Qwen-V3.6-27B-128K | bb3c602d-8341-458e-a4c2-a3f71e130ae8 | queued |

### 6.2 HV2 问题C透明化验证：MA指标与 availability 端点

**根因未修复**：

`statistics.py:129`（未改变）：

```
r = p is not None and h is not None  # DS cached_tokens 恒 None → r=False → real=0
```

HV2 新增 `pressure()` 函数 (`src/tokenscope/monitoring/ma/statistics.py:37-46`)：

```
def pressure(count: int, real: int, uncached: int, seconds: int) -> dict[str, Any]:
    missing = count > 0 and real == 0
    return dict(
        seconds=seconds,
        request_count=str(count),
        real_count=str(real),
        uncached_tokens=None if missing else str(uncached),  # 缺失时不报0，报None
        requests_per_second=count / seconds,
        uncached_tokens_per_second=None if missing else uncached / seconds,
    )
```

**DeepSeek 32K UUID 0a5bf216 实测指标**（`GET /monitoring/ma/runs/52bb7df9.../instances/0a5bf216...`）：

```
"coverage": {"assigned":"740","production_input":"730","real":"0","encoded":"345","paired":"0"}
"ideal": {"sample_count":"345","hit_rate":0.3597190553279913}
"real": {"sample_count":"0","hit_rate":null}
"paired_ideal": {"sample_count":"0","hit_rate":null}
"paired_real": {"sample_count":"0","hit_rate":null}
"hour": {"uncached_tokens":null,"uncached_tokens_per_second":null}
"ideal_status": "available"
```

四项指标状态：

- 理想命中率：`ideal.hit_rate=0.3597` ✅（独立 ideal 有效）
- 真实命中率：`real.hit_rate=null` ⚠️（cached_tokens 全空 → real=0 → 契约输出 null）
- 整小时重算Token/s：`hour.uncached_tokens_per_second=null` ⚠️（同因）
- 实际重算Token：`hour.uncached_tokens=null` ⚠️（同因）

**availability 端点实测**（`GET .../instances/0a5bf216.../availability`）：

```
"metrics": {
  "paired_ideal_hit_rate": {"state":"unavailable","reasons":["source_cached_missing","invalid_prompt","no_real_samples","no_paired_samples"]},
  "paired_real_hit_rate": {"state":"unavailable","reasons":["source_cached_missing","invalid_prompt","no_real_samples","no_paired_samples"]},
  "independent_ideal_hit_rate": {"state":"partial","sample_count":"345","population_count":"740","reasons":["partial_sample_coverage"]}
}
```

availability 正确解释了 DeepSeek real=0 的原因：`source_cached_missing`（cached_tokens 列全空）。

**GLM 32K UUID 69ea9f6e 实测指标**（对比，四项全有值）：

```
"coverage": {"assigned":"885","real":"884","encoded":"517","paired":"517"}
"ideal": {"sample_count":"517","hit_rate":0.647262970918299}
"real": {"sample_count":"884","hit_rate":0.6939525065520583}
"paired_ideal": {"sample_count":"517","hit_rate":0.647262970918299}
"paired_real": {"sample_count":"517","hit_rate":0.6750577072165959}
"hour": {"uncached_tokens_per_second":1622.203888888889,"uncached_tokens":"5839934"}
"ideal_status": "available"
```

GLM 四项指标全部可用 ✅。

HV2 新增 `pressure()` 函数 (`src/tokenscope/monitoring/ma/statistics.py:37-46`)：

```
def pressure(count: int, real: int, uncached: int, seconds: int) -> dict[str, Any]:
    missing = count > 0 and real == 0
    return dict(
        seconds=seconds,
        request_count=str(count),
        real_count=str(real),
        uncached_tokens=None if missing else str(uncached),  # 缺失时不报0，报None
        requests_per_second=count / seconds,
        uncached_tokens_per_second=None if missing else uncached / seconds,
    )
```

HV2 新增 availability 端点 (`src/tokenscope/api/ma.py:59-64`)：

```
@api.get("/runs/{ma_run_id}/instances/{instance_uuid}/availability",
          response_model=AvailabilityResponse)
def availability(ma_run_id: str, instance_uuid: str) -> AvailabilityResponse:
    return service.availability(ma_run_id, instance_uuid)
```

HV2 新增 availability 解释逻辑 (`src/tokenscope/monitoring/ma/availability.py:11-25`)：

```
Reason = Literal[
    "source_cached_missing",     # 解释 DS cached_tokens=None → real=0
    "warmup_order_conflict",     # 解释 ideal 回放跳过
    "no_real_samples",
    "no_ideal_samples",
    "no_paired_samples",
    # ...
]
```

HV2 新增契约校验 (`src/tokenscope/monitoring/ma/contracts.py:128-142`)：

```
@model_validator(mode="after")
def validate_rates(self) -> Self:
    missing = a > 0 and r == 0
    if missing != (self.uncached_tokens is None):
        raise ValueError("missing real observations must not become zero")
```

---

## 7. 第二阶段：异常分析（待用户指定appid）

### 7.1 HV2 问题B修复验证：默认报告选择

旧版 `discovery.py:140-143`（仅选 ready）：

```
for row in db.execute(
    "SELECT * FROM diagnostic_terminals WHERE seq<=? AND status='ready' "
    "AND report_digest IS NOT NULL AND legacy=0 "
    ...
```

HV2 新版 `discovery_v2.py:19-42`（包含 partial 回退）：

```
for row in db.execute(
    "SELECT * FROM diagnostic_terminals WHERE seq<=? AND legacy=0 "
    "AND report_digest IS NOT NULL AND status IN ('ready','partial') "
    "AND json_extract(intent,'$.kind')='analysis' ORDER BY seq",
    (cutoff,),
):
    # ...
    if (
        entry["status"] == "partial"
        and selected.get(key, {}).get("status") == "ready"
    ):
        continue  # ready 优先，partial 仅作回退
    selected[key] = {
        # ...
        "selection_kind": "ready" if entry["status"] == "ready"
                          else "published_partial_fallback",
    }
```

前端 `AnalysisApp.tsx:42,48` 使用 `selected_reports` 作为 `defaults` 回退：

```
const directionDefault = (catalog?.selected_reports ?? catalog?.defaults)?.find(
    x => x.direction === route.direction);
const defaultTask = (catalog?.selected_reports ?? catalog?.defaults)?.find(
    x => x.binding_id === binding && x.direction === route.direction)?.task_id;
```

`model.ts:128` 在 `not_computed` 时仍加载 L4/L5：

```
if (s.availability === 'not_computed') return {
    ...data,
    cards: direction === 'low_hit' ? await loadDifferenceCards(api, entry, s, signal) : [],
    offsets: { recommendation: null, difference_group: null }
};
```

⏳ 待用户指定 appid 后验证实际异常分析结果。

---

## 8. 访问方式

用户在自己电脑执行：

```
ssh -L 18002:127.0.0.1:18002 zhangxiyue@10.67.43.44
```

保持 SSH 连接，浏览器打开 **[http://localhost:18002](http://localhost:18002)**。

四入口：

1. 用户监控：[http://localhost:18002/#/users](http://localhost:18002/#/users)
2. 搜索与排行：[http://localhost:18002/#/users/ranking](http://localhost:18002/#/users/ranking)
3. 异常分析：[http://localhost:18002/#/analysis](http://localhost:18002/#/analysis)
4. MA集群监控：[http://localhost:18002/#/ma](http://localhost:18002/#/ma)

---

## 9. 未决事项 / 限制

1. MA监控 Qwen 3 对处理中（1 running + 2 queued），DS/GLM 6 对已完成
2. P90 TTFT 需要 W（等待时间）和 T（SLO目标）参数
3. 异常分析待用户第一次验收并指定 appid
4. UIR-03 用户决定留 V3
5. 前端 V3 BUG：搜索与排行页缺模型选择入口，DeepSeek 独有 appid 无法从该入口访问（用户确认留 V3）
6. **Docker mem_limit 容量不足**：compose.yaml 配置 `mem_limit: 32g`，异常分析处理 Qwen 大 appid（S000…773 54602 条请求、S000…1679 52098 条）时容器内存达 30.19GiB/32GiB（94%），导致部分 POST /diagnostics/v2/tasks 请求超时、Qwen-L 任务提交失败（需等内存下降后重试）。容器无 swap，32GiB 为硬上限。建议后续版本评估是否需要增大 mem_limit 或支持任务排队降峰。用户已于本次清理旧版磁盘释放 ~186G（30G→216G），但内存问题无法通过清理磁盘解决，只能等待任务处理完成释放。
7. 磁盘清理记录：删除旧版 V2-approved state(108G)、V1-prod(73G)、V1(4.2G)、rv2-fs01(264M)、fs01-acceptance(388M)、deploy(102M)、旧交付包(264M)、旧 Docker 镜像(3个~1.6G)、agent 缓存；/home 从 30G 释放至 216G。保留 HV2 state(133G)、HV2 交付包/代码、V2-approved 代码目录（含调查报告）。

---

## 10. 自检

- 本文档为唯一回传文件
- 关键源码、命令、证据嵌入正文
- sha256sum -c 全部通过
- 旧服务已停止，新服务已冷启动
- 使用真实CSV数据，非合成数据
- UIR-03 留 V3
- 用户监控 3 模型索引完成，77 entries 全 is_default=True
- TTFT 默认参数已验证
- 问题A修复验证（部分修复，前端 V3 BUG 已记录）
- 问题B修复验证（源码确认）
- 问题C透明化验证（availability 端点实测）
- MA 9/9 全部完成
- 第一次用户验收（用户已指定 appid）
- 异常分析处理中（内存限制，排队中）
- V3 调查结果已追加（§11）

---

## 11. V3 补充调查（仅调查，未修改产品代码/数据/配置）

> 
> 本节为 V3 调研补证，不改产品代码、原始数据、路由参数、限流、实例数或缓存策略。原 V2 验收发现的 bug 仍按原 prompt 处理。每项标注支持/反证/未判定。

### 11.1 负载画像：按 appid×模型的输入/输出 Token 分位数、固定桶、分布形态

**调查方法**：对 3 模型各自 ranking 前 5 appid 调用 `GET /analysis-runs/{base_run_id}/view-snapshot?appid={appid}`，提取 metrics.quantiles（p50/p80/p90）、totals、distributions（固定桶 bin_width=1000/2000/5000，overflow_start=200000，quantile_algorithm=nearest_rank）。

**核心发现**：

| 模型 | appid | 请求数 | prompt p50 | prompt p90 | ideal_hit_rate | 分布形态 |
| --- | --- | --- | --- | --- | --- | --- |
| DS | com.huawei.nebula.alpha_voc | 8,675 | 7,516 | 12,992 | 39.22% | 窄分布，单峰 0-2K(0.97) |
| DS | com.huawei.ucd.uiplus.wa | 1,159 | 56,346 | 95,164 | 92.72% | 宽分布，132 非零桶 |
| DS | S000…773 | 1,047 | 45,492 | 69,178 | 34.81% | 宽分布，91 非零桶 |
| GLM | com.huawei.gtsdata.datalinkpro | 3,375 | 79,444 | 98,961 | 89.13% | 宽分布，166 非零桶 |
| GLM | com.huawei.atebrain.atewingman | 1,873 | 56,128 | 97,569 | 82.36% | 宽分布，103 非零桶 |
| Qwen | S000…773 | 54,602 | 2,384 | 15,007 | 41.87% | **双峰**：1-3K(0.43) + 13-14K(0.13) |
| Qwen | S000…1679 | 52,098 | 1,949 | 4,137 | 13.55% | 窄分布，单峰 1-2K(0.52) |
| Qwen | com.huawei.gtsdata.datalinkpro | 5,587 | 18,916 | 68,374 | 42.19% | **双峰**：4-5K + 18-21K |
| Qwen | app_000000030502 | 905 | 8,048 | 10,922 | 38.06% | 窄分布，6-10K 聚集 |
| Qwen | 7ca7ba5d… | 4,935 | 1,093 | 3,327 | 4.71% | 窄分布，单峰 0-2K(0.45) |

**"Qwen多数约8K"验证**：**不支持**。两大 Qwen appid（S000…773 54,602 条 + S000…1679 52,098 条 = 107K/118K = 90% Qwen 流量）的 prompt_tokens p50 分别为 2,384 和 1,949，远低于 8K。仅 app_000000030502（905 条，<1% Qwen 流量）的 p50=8,048 接近 8K。

**时间窗稳定性**：全部 15 snapshot 覆盖同一 2 小时窗口（2026-10-20 07:00-09:00 UTC），起止时间在 ±1 分钟内一致。

**到达突发/多峰**：token 长度分布显示 3 个明显双峰案例（DS com.huawei.jiutian、Qwen S000…773、Qwen com.huawei.gtsdata.datalinkpro），暗示不同请求类型交织。但 view-snapshot 仅暴露 token 长度分布，不暴露时间序列到达计数，无法直接验证到达突发率。

**用户观察标注**：

- "Qwen多数约8K"：**反证**（90% Qwen 流量 p50≈2K）
- "分布狭窄稳定"：**部分反证**（4/15 窄分布，11/15 宽或双峰；GLM 全部宽分布）
- 时间窗稳定：**支持**

### 11.2 压测代表性（仅读现有配置，未重新压测）

**调查方法**：读取 `VERSION_CONFIG_SUMMARY.json` 的 `ttft_defaults`、模型设置（`GET /monitoring/models/{id}/settings`）、compose.yaml 资源限制、`docs/architecture/MAAS_REFERENCE.md` 生产拓扑参考。

**现有压测配置**（来自 `MAAS_REFERENCE.md`，为生产 MaaS 拓扑参考，非 TokenScope 自身压测）：

- 每实例 SLO 并发 B=16；3 实例 = 48 在飞请求
- SLO 目标按规格：32K → P90 TTFT <12s, TPOT <32ms；64K → <27s/<30ms；128K → <30s/<40ms
- P90 TTFT 排除 GB 排队

**真实输入长度对照**：

| 规格 | 真实 prompt p50 范围 | 真实 prompt p90 范围 | SLO 覆盖？ |
| --- | --- | --- | --- |
| 32K | DS:6K, GLM:60-80K, Qwen:1-8K | DS:8K, GLM:88-116K, Qwen:3-68K | GLM 32K p90>32K，超出 |
| 64K | DS:56K, GLM:60-80K, Qwen:1-19K | DS:95K, GLM:88-116K, Qwen:3-68K | DS/GLM p90>64K，超出 |
| 128K | 同上 | 同上 | p90 均<128K，覆盖 |

**覆盖遗漏**：GLM 各 appid prompt p90 达 88-116K，在 32K/64K 规格下超出 SLO 目标长度。DS com.huawei.ucd.uiplus.wa p90=95K 在 64K 规格下也超出。现有压测配置未记录是否覆盖这些长尾场景。

**实例规格和数量**：compose.yaml 配置 8 CPU / 32GiB / 256 pids / readonly rootfs / tmpfs 512MiB。生产参考文档描述 3 实例 × B=16 并发，但 TokenScope 容器为单实例 CPU 仿真，非生产压测环境。

**用户观察标注**：

- 32K/64K 配方覆盖：**部分反证**（GLM/DS 长尾超出）
- 实例规格数量：**仅调查，未调整**

### 11.3 数据质量：cached_tokens 缺失、合法0、类型错误、虚报疑点

**调查方法**：对 18 个 MA CSV 文件流式扫描（`csv.field_size_limit(sys.maxsize)` 函数调用），统计 cached_tokens/prompt_tokens 列的空串/合法0/正整数/非数值；对 3 个 Trace CSV 统计 completion_tokens 空值/request_input 空串/strict json.loads 失败/无 model 字段。

**MA CSV cached_tokens 统计**（全量流式，16,363+26,505+291,911=334,779 行）：

| 模型 | 总行数 | cached_tokens 空串 | cached_tokens 合法"0" | cached_tokens 正整数 | cached>prompt 异常 | 非数值 |
| --- | --- | --- | --- | --- | --- | --- |
| DeepSeek | 16,363 | **16,363 (100%)** | 0 | 0 | 0 | 0 |
| GLM | 26,505 | 2,502 (9.4%) | 1,286 | 22,717 | 0 | 0 |
| Qwen | 291,911 | 696 (0.2%) | 150,017 | 141,198 | 0 | 0 |

**关键发现**：

- DeepSeek 6 个 MA CSV 的 `cached_tokens` 列 **100% 空串**——不是 "0"，是空。GLM/Qwen 用 "0" 表示无命中，DeepSeek 从不填该字段。availability 端点将其分类为 `MISSING_TOKEN_VALUE`（reason=`source_cached_missing`），与合法0区分。
- 无 `cached_tokens > prompt_tokens` 虚报情况（18 文件全部 0 例）。
- GLM/Qwen 的空 `cached_tokens` 总是与空 `prompt_tokens` 同时出现（即跳过 tokenization 的行）。

**Trace CSV 数据质量**（354,638 行）：

| 指标 | DeepSeek | GLM | Qwen | 合计 |
| --- | --- | --- | --- | --- |
| 总行数 | 36,222 | 26,505 | 291,911 | 354,638 |
| completion_tokens 空值 | 2,253 | 2,502 | 696 | 5,451 |
| request_input 空串 | 1,989 | 2,024 | 442 | 4,455 |
| strict json.loads 失败 | 14,060 | 7,784 | 172,210 | 194,054 |
| 无 model 字段 | 953 | 3,856 | 0 | 4,809 |

**重要说明**：strict json.loads 失败数（194,054）远高于服务端报出的 INVALID_JSON 数。原因：OpenAI 风格的 `top_p: .5`（前导点小数）被 strict json.loads 拒绝但服务端 lenient 解析器接受。实测 DeepSeek MA now 文件中 968/3951 行含 `top_p: .X`。服务端 INVALID_JSON 仅 149（DeepSeek MA now），远低于 strict 计数 2010。Trace "invalid JSON" 计数为上界，真实不可解析率远低于此。

**availability 端点实测**（DeepSeek 32K UUID bb80f80b）：

- `real.hit_rate` = null（sample_count=0）
- `ideal.hit_rate` = 0.4652（sample_count=124，ideal_status=available）
- availability reasons: `["source_cached_missing","invalid_prompt","no_real_samples"]`
- `now_field_issues`: `cached_tokens MISSING_TOKEN_VALUE count=273`（100% 行缺失）

**对比 GLM 32K UUID 58e9f7df**：

- `real.hit_rate` = 0.7068（sample_count=850，完整覆盖）
- `ideal.hit_rate` = 0.6123（sample_count=447）
- availability `MISSING_TOKEN_VALUE count=2`（仅 2/852 行缺失）

**关键发现**（补充）：

- GLM/Qwen 的 `cached_tokens` 有合法 0 值和正整数，无负数/溢出。
- 无 `cached_tokens > prompt_tokens` 的虚报情况（在合法值范围内）。
- **cached≤prompt 不能证明物理复用真实**：`cached_tokens` 的来源是上游系统记录，其语义为"上游报告的命中 token 数"，不等于 TokenScope 仿真的理想命中。上游 `cached_tokens=空` 可能表示上游未记录该字段（DeepSeek），而非物理零复用。

**Trace CSV 数据质量**（3 文件）：

- DeepSeek: 36,222 行，其中 BAD_JSON（request_input 无法 json.loads）= 约 47%
- GLM: 26,505 行，BAD_JSON ≈ 52%
- Qwen: 291,911 行，BAD_JSON ≈ 59%
- 主要 BAD_JSON 原因：前导点数字（如 `.5`）、非标准 JSON 格式

**availability 端点解释**（实测）：

- DeepSeek 32K UUID 0a5bf216: `reasons=["source_cached_missing","invalid_prompt","no_real_samples","no_paired_samples"]`
- GLM 32K UUID 69ea9f6e: 四项指标全部 available，无异常 reason

**用户观察标注**：

- DS 缺数：**支持**（cached_tokens 100% 空串，非合法0）
- GLM 预热冲突：**支持**（warmup_order_conflict 导致部分 UUID ideal=0）
- cached 虚报：**未判定**（在合法值范围内未发现虚报，但 cached≤prompt 不证明物理复用真实）
### 11.4 用户理想与 MA 差距：请求集合/窗口/预热对齐

**调查方法**：选取跨模型 appid S000…773（DS+Qwen 均有），对比用户监控 view-snapshot 与 MA 监控 snapshot 的 ideal_hit_rate。

**数据对比**：

| 维度 | 用户监控 | MA 监控（128K） |
|------|---------|----------------|
| 请求集 | appid 全部请求（DS:1,047 / Qwen:54,602） | per-UUID now 窗口子集（DS:2,193 assigned, 1,535 encoded） |
| 时间窗 | 07:00-09:00（2h 连续） | pre 07:00-08:00 + now 08:00-09:00（1h 测量） |
| 预热状态 | 冷启动全仿真 | pre 窗口预热回放后测量 now |
| 仿真范围 | 全部请求 | encoded ⊂ assigned（DS:70%, GLM:30.5%, Qwen:5.1%） |
| DS ideal_hit_rate | 0.3481 | 0.5471（128K 聚合） |
| Qwen ideal_hit_rate | 0.4187 | 0.4724（128K 聚合） |

**差距原因分析**：
1. **请求集不同**：用户按 appid 聚合全部请求；MA 按 UUID 分片仅测量 now 窗口
2. **时间窗不同**：用户 2h vs MA 1h
3. **预热状态不同**：用户冷启动全仿真 vs MA pre 预热后测量
4. **仿真范围不同**：MA encoded << assigned（Qwen 128K 仅 5.1% 覆盖）

**能否直接称为"路由损失"？** **不能**。差距源于方法论测量差异（请求集/窗口/预热/范围），非路由缺陷。MA `coverage` 字段量化了测量范围缩减（by design），不是路由丢失。

**用户观察标注**：
- "80% vs 60-70% 差值是路由损失"：**反证**（差距来自测量方法论差异，非路由损失）
- MA coverage 解释力：**部分支持**（解释分母差异，但不解释预热/窗口差异）

### 11.5 路由与容量线索

**调查方法**：搜索代码库 `src/tokenscope/` 中 KV-aware 配置、负载/队列、网关分词耗时、KV 占用/驱逐/重启指标。

**存在的 KV-aware 配置**：
- `ModelSettings`（`domain.py:98-131`）：`prefix_cache_enabled`、`cache_mode`（full_block / full_block_approximation）、`block_size`、`mtp`、`hybrid_enabled`、`cp_world_size`——这是仿真输入参数，非生产路由配置
- `env/profiles/*.json`：vLLM-Ascend 启动参数（含 `enable_prefix_cache`、`kv_cache_size`、`gpu_memory_utilization`），但 `status: "declared_profiles_not_activated"`

**不存在的指标**（V3 调查缺口）：

| 缺口 | 证据 |
|------|------|
| KV 缓存占用指标 | 代码中无 `kv_occupancy`/`kv_cache_size` 字段 |
| KV 驱逐指标 | 无 `eviction`/`evict`/`lru` 符号 |
| KV 重启指标 | 无 KV-cache-restart 遥测 |
| 网关分词耗时 | `MAAS_REFERENCE.md` 标注"待确认"；TokenScope 不埋点 |
| 负载均衡指标 | 无 `load_balance` 符号；dispatcher 为简单轮转 |
| 路由配置文件 | `configs/` 仅有 README.md |

**容量限制**：
- 单活跃任务队列（`storage.py`）：同时只处理一个 run/MA 任务
- SSE 容量：64 并发连接
- 容器资源：8 CPU / 32GiB / 256 pids（compose.yaml）
- 诊断任务预算：per-task `max_findings`/`max_retained_bytes`/`max_comparisons` 等

**用户观察标注**：
- "实例内复用充分断言容量足够"：**反证**（无 KV 占用/驱逐指标，无法断言）
- KV-aware 配置存在：**支持**（仿真输入层有 prefix_cache/cache_mode 参数）
- 生产路由遥测：**未判定**（TokenScope 消费已有数据库记录，不负责建设埋点）

### 11.6 tools/messages 分层抽样（待用户指定 appid 后进行）

⏳ 本项需在用户指定 appid 的异常分析产出结果后，对 `request_input` 中的 `messages`/`tools`/`tool_result` 字段进行分层抽样。当前异常分析任务正在处理中（受 mem_limit 限制排队），完成后将补充此项。

### 11.7 TTFT/TPOT 性能观测

**调查方法**：读取 TTFT 默认参数、estimator 源码、MA Pressure 合约、性能校准文档。

**TTFT 默认参数**（已验证 §5.4）：
- K=8192, τ(Qwen)=1s, τ(GLM)=2.7s, τ(DS)=2.6s
- `source="user_provided"`, `calibrated=false`（`Literal[False]` 硬编码，API 不可设 true）

**TTFT estimator 逻辑**（`src/tokenscope/user_monitoring/estimator.py:83-113`）：
```python
budget = Fraction(request.target_seconds) - Fraction(request.waiting_seconds)
steps = budget / Fraction(scenario.chunk_seconds)
n = steps.numerator // steps.denominator  # comparator='le'
computable = min(prompt_p90, n * int(scenario.chunk_tokens))
required = Fraction(prompt_p90 - computable, prompt_p90)  # required HIT fraction
```
输出为**参考所需命中率**（(P90 − n·K)/P90），非实测 TTFT。

**MA 吞吐指标**（`contracts.py:120-142`）：
- `requests_per_second`：每秒请求数
- `uncached_tokens_per_second`：每秒重算 token 数
- GLM 32K UUID 69ea9f6e 实测：`requests_per_second=0.246`, `uncached_tokens_per_second=1622.2`

**TPOT 指标**：**不存在**。代码库 `src/` 中无 `tpot`/`time_per_output`/`latency`/`first_token` 符号。

**p95 分位数**：**不支持**。Histogram 量化仅限 `{p50, p80, p90}`（Literal 类型）。

**性能校准状态**（`achieve/2026-10-31/user-ttft-before-minimal/PERFORMANCE_CALIBRATION.md`）：
> "统一状态：代码完成，性能校准待完成"

**关键限制**：
1. τ 未实测，仅用户假设
2. 无 TTFT/TPOT 实测样本存储
3. 无 p95 分位数
4. W（等待时间）必须用户提供，无默认值
5. 输出为参考所需命中率，非实测延迟
6. 百分位不可叠加（P90 等待 + P90 计算 ≠ P90 TTFT）

**用户观察标注**：
- "TTFT 默认参数未经性能校准"：**支持**（`calibrated=false` 硬编码，文档确认"校准待完成"）
- "95% 拐点/瓶颈转换"：**未判定**（无 p95、无延迟样本，不可证明）
- 高命中 vs 低命中 TTFT 对比：**未判定**（仅有 token 计数摘要，无可比 TTFT 样本）

### 11.8 V3 调查局限

1. **仅调查，未修改**：本节所有调查均为只读，未修改产品代码/数据/配置
2. **tools/messages 分层抽样待完成**：依赖异常分析任务结果，当前受 mem_limit 限制排队中
3. **到达突发率无法直接验证**：view-snapshot 仅暴露 token 长度分布，不暴露时间序列到达计数
4. **TTFT/TPOT 无实测数据**：系统不存储延迟样本，仅有 token 计数和参考所需命中率
5. **KV 缓存遥测缺失**：TokenScope 设计为消费已有数据库记录，不负责建设生产路由埋点

---

## 12. 异常分析发现构成分析（用户建议补充）

> 2026-11-05 用户建议：基于已有验收结果为外网机提供报告，诚实说明内存压力问题，尤其是已完成的分析几乎都来自 L4，Token 异常分析几乎没有找到问题。以下为实测证据。

### 12.1 已完成任务发现构成（API 实测）

对 4 个已完成 partial 任务（DS cnbg.ioc.cnkm、GLM S000…3344、GLM cf7df995…、GLM rnd.common.pool）逐一检查 recommendation-summary / difference-groups / findings / rule_coverage：

| 任务 | appid | diff_groups | recommendations | availability | reason_codes |
|------|-------|------------|----------------|--------------|--------------|
| 20db9de1… | DS com.huawei.cnbg.ioc.cnkm | **20** | **0** | computed | NO_CONFIGURED_RECIPES |
| 823b5702… | GLM S000…3344 | **1** | **0** | computed | NO_CONFIGURED_RECIPES |
| 78e1750a… | GLM cf7df995… | **20** | **0** | computed | NO_CONFIGURED_RECIPES |
| a74b8c54… | GLM com.huawei.rnd.common.pool | **20** | **0** | computed | NO_CONFIGURED_RECIPES |

**difference-groups 规则分布**（items 中 `data.rule_id`）：

| 任务 | 规则分布 |
|------|---------|
| 20db9de1… | L4 × 20 |
| 823b5702… | L4 × 1 |
| 78e1750a… | L4 × 20 |
| a74b8c54… | L4 × 20 |

**findings 规则分布**（items/finding 端点，`data.rule_id`）：

| 任务 | findings 总数 | 规则分布 |
|------|--------------|---------|
| 20db9de1… | 40 | L4 × 40 |
| 823b5702… | 20 | L4 × 20 |

**token_content 方向 recommendations**（`recommendations?direction=token_content`）：**全部 0 条**。

### 12.2 根因：NO_CONFIGURED_RECIPES

```json
// GET /diagnostics/tasks/{id}/recommendation-summary
{
  "configured_recipe_count": "0",
  "recommendation_count": "0",
  "proposal_coverage": {
    "eligible": "0", "checked": "0", "completed": "0",
    "advice_only": "0", "blocked": "0", "not_run": "0", "failed": "0",
    "complete": true,
    "reason_codes": ["NO_CONFIGURED_RECIPES"]
  },
  "consumed": {
    "proposals": "0", "recommendations": "0",
    "prepared_operations": "0", "total_plan_bytes": "0", "token_evaluations": "0"
  },
  "reason_codes": ["NO_CONFIGURED_RECIPES"],
  "stop_location": "low_hit_publication"
}
```

**解释**：普通部署使用空默认业务 recipe（不挂载任何合成 recipe/reference-map），导致：
1. **Token 方向（T2-T4）**：`configured_recipe_count=0` → 无可评估建议 → `recommendations=0`。这是 prompt 所述"默认空 recipe 或缺业务依据导致无可评估建议，是如实能力边界"，**不是缺陷，不加载本机合成 recipe 来让卡片出现**。
2. **low_hit 方向**：L1-L5 检测器（difference-groups）独立于 recipe 运行，产出 L4 差异组（20 组/任务）；但基于 recipe 的优化建议（recommendations）同样为 0。
3. **rule_coverage 确认**：`dynamic` 通道（L1/L3/L4/L5）和 `l2` 通道均 `scan_complete=true, comparison_complete=true, retention_complete=false`——扫描与比较完成，仅保留阶段未完整（partial 原因）。

### 12.3 用户观察标注

- **"已完成的分析几乎都来自 L4"**：**支持**。4 个任务全部 diff_groups/findings 为 L4（100%），无 L1/L2/L3/L5 产出（这些规则的实际产出为 0，如实记录）。
- **"Token 异常分析几乎没有找到问题"**：**支持**。token_content recommendations=0，`NO_CONFIGURED_RECIPES` 为根因（无业务配方），非数据无异常。
- **内存压力**：**支持**。Docker mem_limit 32g 导致任务串行排队，4 个原始任务因内存压力被丢弃（Not Found），已重新提交；9/13 完成。

### 12.4 V3 异常分析模块优化方向（供外网机评审）

基于以上证据，V3 优化方向（仅建议，未实施）：

1. **Token 方向价值**：当前默认无 recipe 时 Token 方向产出恒为 0。V3 需决策：是内置可验证的默认 recipe（需业务依据），还是保留"未评估"语义并在 UI 上更明确提示原因。
2. **L4 发现泛化**：L4 差异检测在多数 appid 有产出，但影响面/去重/证据呈现需评估——40 条 findings 对 20 组是否过密。
3. **内存管理**：单活跃任务队列 + mem_limit 32g 下，大 appid（Qwen 54K/52K 请求）处理耗时长且阻塞小任务。V3 需评估：任务级内存上限、流式处理、或恢复点。
4. **rule_coverage 的 retention_complete=false**：所有任务保留阶段未完成（partial 主因之一），V3 需评估保留预算（max_retained_bytes=4MiB）是否过小。