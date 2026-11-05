# HUAWEI_V2_ACCEPTANCE_REPORT — TokenScope V2 华为实验机真实数据验收报告

> 
> 生成时间：2026-11-03（现场 UTC+8）
> 交付目录：`tokenscope-v2-approved-20261102`（/home/aarc/zhangxiyue/tokenscope-v2-approved-20261102）
> 唯一回传文档：本文件。所有关键源码、命令、证据均嵌入正文，不依赖外部附件。

---

## 0. 结论 / 当前阶段

| 阶段 | 状态 | 关键依据 |
| --- | --- | --- |
| 0. 交付包身份校验 | ✅ 通过 | SHA256SUMS 13/13 OK；镜像ID/manifest一致；HTTP资源SHA与candidate.json一致（§1） |
| 1. 环境实测 | ✅ 通过 | CentOS7/40核/375GiB；Docker 26.1.4/Compose 2.27.1；GPU NVML不匹配但本版CPU运行（§2） |
| 2. 停旧版+干净启动 | ✅ 通过 | FS01旧容器停止移除、端口全释放、新空state冷启动（§3） |
| 3. 真实数据盘点 | ✅ 通过 | 3用户CSV+18 MA CSV全量盘点、字段/行数/SHA/配对验证（§4） |
| 4. 第一阶段A：用户监控 | ✅ 通过（API层） | 3模型34+22+21 appid发布；搜索/排序/分页/导出/幂等全过（§5） |
| 5. 第一阶段A：P90 TTFT | ⚠️ 缺参待用户 | 需要 T/W/K/τ 参数，不填示例值（§5.4） |
| 6. 第一阶段B：MA监控 | ✅ 通过 | 18 CSV/9对全部completed；质量报告/UUID/指标正常（§6） |
| 7. 重启持久性 | ✅ 通过 | catalog/runs/MA/readyz 前后一致（§6.4） |
| 8. **第一次用户验收** | ❌ **用户验收不通过** | 用户明示"用户监控验收不通过"（§9.1） |
| 9. 第二阶段：异常分析 | ✅ 10/10完成（全部partial） | 8小appid两方向全部产出findings；2大appid按用户决策仅low_hit提交，但契约 enable_token_content 约束使其实际也完成token全量（§7） |
| 10. 第二次用户验收 | ⏳ 待用户 | 异常分析10/10完成，报告已生成供审查 |
| 11. UIR-03 | 用户决定留V3，非V2阻断 | 本次未修复 |

**关键结论**：

1. **用户监控验收不通过**：用户反馈 URL 只显示 Qwen。经核实服务端数据完整（S0 catalog=77 覆盖3模型），问题在前端 users 页面浏览器 localStorage 只记忆最近打开的 run（§9.1、§8.1 详细分析）。
2. **用户质疑"动态字段问题"正确**：DeepSeek S000…773 等 appid 实际产出 97-100 个 L4 findings（difference_pointers 指向 messages content 差异），但前端未展示（report 端点 items 为空，findings 需单独 /items/finding 端点获取）（§7.3、§8.2）。
3. **Token异常分析耗时差异极大**：部分 appid 每请求 ~0.7-30s（内容深/长触发慢路径），但 Qwen 两个 5 万+请求大 appid 实测 ~0.04s/请求、30-40 分钟全量完成（encoding_calls=0）。原按用户决策大 appid 仅跑 low_hit，但契约 enable_token_content 约束使其实际完成 token 全量（§7.3/P3 修正）。

---

## 1. 版本表（交付身份）

### 1.1 release-manifest.json 声明的身份

| 项 | 值 |
| --- | --- |
| release_id | `tokenscope-v2-approved-20261102` |
| source_commit | `b17cdc07b0a351d0f5c4fb1b26f0e05be2b3a0af` |
| image_tag | `tokenscope/full-service:tokenscope-v2-approved-20261102` |
| image_id | `sha256:a38d0ab2cfe26154c96adb5e876538893005e5cb100fc5c53640823c391683a8` |
| base_image | `public.ecr.aws/docker/library/python@sha256:a36c24f9cbdf4fd0f52d67f0823eeac19c2028c637cecc392d97f980d4fec56b` |
| platform | linux/amd64 |
| frontend | viewer-uir01-pointer-fix-20261102-c1 |
| public_backend | arpc-local-4 |
| token_private | token-review-20261101-1 |
| token_plugin | token-content-2 |
| source_identity_sha256 | `7e71bbe89bf96ea42c3c7f7a94787faabe4d4e1b38dbe7dc28187b9a061dd4e6` |

### 1.2 模型 revision 与资产 SHA（manifest）

| model_id | revision | tokenizer_config SHA | tokenizer.json SHA | chat_template SHA |
| --- | --- | --- | --- | --- |
| Qwen3.6-27B | `6a9e13bd6fc8f0983b9b99948120bc37f49c13e9` | `5186f0defcd7f232382c7f0aebcd2252d073bb921ab240e407b7ae8745d2b29b` | `5f9e4d4901a92b997e463c1f46055088b6cca5ca61a6522d1b9f64c4bb81cb42` | `e84f32a23fdda27689f868aa4a1a5621f41133e51a48d7f3efcbea2839574259` |
| GLM-5.2 | `cf457fa734ab149ffef225f80893eb38c6ff5cdc` | `98b1271574f41abf89427ae2dda030d94dc9478f0edc5a8bd240db213c6fd5fc` | `19e773648cb4e65de8660ea6365e10acca112d42a854923df93db4a6f333a82d` | `172dc74a35e1752df75ecfb2b2cf9326d2852bb1379868ebeec9571654489679` |
| DeepSeek-V4-Flash-0731 | `7872f01b1d1fe23eabc4c98b48bffcef5a386062` | `6ac8c8dc065ed118161d02dd532749ae3f52c243deac27872134fae2f50d8547` | `8f9f37ca37fdc4f5fd36d5cf4d3b0e8392edb4e894fd10cc0d70b4957c8633cf` | —（无chat_template） |

### 1.3 实际部署配置（compose.yaml + deployment.env）

```
容器:         tokenscope-v2-approved-monitoring-1
Compose项目:  tokenscope-v2-approved
镜像:         tokenscope/full-service:tokenscope-v2-approved-20261102
运行用户:      1015:2006 (zhangxiyue)
资源:         cpus=8, mem_limit=32GiB, pids_limit=256
只读根fs:     read_only=true, cap_drop=[ALL], no-new-privileges
tmpfs:        /tmp size=536870912 mode=1777
挂载:         /inputs ← /home/aarc/zhangxiyue/10.20_Trace_extract (ro)
              /state  ← /home/aarc/zhangxiyue/TokenScope/state/tokenscope-v2-approved-20261102-20261102T0955 (rw)
端口:         127.0.0.1:18002 → 8000
command:      --input-root /inputs --state-root /state --asset-root /app --cpu-budget 8
              serve --host 0.0.0.0 --port 8000 --viewer-root /app/apps/viewer/dist
服务实例ID:   abf57577-2dcc-4ddb-9758-bbbd548ddfdf
健康:         healthz=alive; readyz=ready (3模型 assets=verified)
```

### 1.4 `sha256sum -c SHA256SUMS` 完整结果（交付目录执行，exit=0）

```
DEPLOYMENT_README.md: OK
HUAWEI_AGENT_PROMPT.md: OK
candidate.json: OK
compose.yaml: OK
container-acceptance.json: OK
container-browser.log: OK
container-restart.json: OK
deployment.env.example: OK
docker-save.log: OK
release-manifest.json: OK
tokenscope-v2-approved-20261102-code.tar.gz: OK
tokenscope-v2-approved-20261102-image.tar.gz: OK
unified-container-validation.json: OK
（13/13 OK）
```

### 1.5 实际HTTP资源 vs candidate.json 期望SHA

| 资源 | 实际SHA256 | candidate.json期望 | 匹配 |
| --- | --- | --- | --- |
| / (index.html) | `e4c7e4e0969e52c39bbdc78bb6c48641742d0d75cc79605ef9aed2ae21fa46d6` | 同左 | ✅ |
| /assets/index-BN_hqTE_.js | `1d18c395fb5aca91bc77b469e58376a087a204f46c786d5bf9502c3ad6e55072` | 同左 | ✅ |
| /assets/index-BxqENh7v.css | `7de15a1ce92dc92d4d93a96c70425c1ea22663c5c4653c98cb4d9122ef0254a5` | 同左 | ✅ |
| /assets/export-validator-rZ4O78aZ.js | `e52838c80a214d465b29b1e6049fabe887e80d8077fc5ce121061c8f109e9d41` | 同左 | ✅ |

容器内 `/app/candidate.json` 与交付包 candidate.json 一致（release_id/source_commit/versions/source_identity_sha256 相同）。OpenAPI 66个路径，`x-user-contract-version: 2.0.0` 用户接口9操作完整。

### 1.6 模型运行配置（/monitoring/models/{id}/settings）

| model_id | block_size | block_size_unit | cache_mode | encoding_profile | 策略 |
| --- | --- | --- | --- | --- | --- |
| GLM-5.2 | 128 | simulation_input_tokens | full_block | default | full-block-mtp-v1 |
| Qwen3.6-27B | 1536 | simulation_input_tokens | full_block_approximation | default | full-block-mtp-v1 |
| DeepSeek-V4-Flash-0731 | 32 | simulation_input_tokens | full_block_approximation | thinking_disabled | full-block-mtp-v1 |

**DeepSeek thinking 模式核实**：包内 DEFAULT_SETTINGS 为 `thinking_disabled`。真实数据核对：DeepSeek Trace CSV 中 34233 行有 request_input，其中 14357 行含 `enable_thinking` 键 → 13901 行 `false`、369 行 `true`（主流量为 false，与 profile 一致；369 行 true 为个别请求显式开启，服务端按请求内参数处理，profile 的 default_thinking=false 不影响显式覆盖）。readyz 三个模型 `explicit_request_options_supported: true`。未发现"DeepSeek编码思考模式缺失导致ready项不可用"的情况。

---

## 2. 实际环境证据

### 2.1 环境实测命令与输出（2026-11-02T17:54+0800 / 2026-11-02T09:54Z）

```
$ date -u && date
2026-11-02T09:54:24Z
2026-11-02T17:54:24+0800

$ hostname
aarc22885

$ uname -a
Linux aarc22885 3.10.0-1160.119.1.el7.x86_64 #1 SMP Tue Jun 4 14:43:51 UTC 2024 x86_64 x86_64 x86_64 GNU/Linux

$ nproc && lscpu | grep -E 'Architecture|CPU\(s\)|Model name'
40
Architecture: x86_64
CPU(s): 40
Model name: Intel(R) Xeon(R) Silver 4114 CPU @ 2.20GHz

$ free -g
              total  used  free  shared  buff/cache  available
Mem:            375   21   216      1         137        351

$ df -h /home /var/lib/docker /
/dev/mapper/centos-home  3.6T  3.4T  271G  93%  /home
/dev/sdd                 3.6T  375G  3.1T  11%  /var/lib/docker
/dev/mapper/centos-root   50G   43G  7.6G  85%  /

$ df -i /home /var/lib/docker /
384913792 inodes  381071868 IFree  (1%)  /home
244195328 inodes  236324330 IFree  (4%)  /var/lib/docker
16807368  inodes  15772080  IFree  (7%)  /

$ docker version
Client 26.1.4 / Server 26.1.4

$ docker info --format '{{.Driver}} {{.CgroupDriver}} {{.NCPU}}'
overlay2 cgroupfs 40

$ docker compose version
Docker Compose version v2.27.1

$ id -u; id -g
1015
2006

$ nvidia-smi --query-gpu=name,driver_version --format=csv
Failed to initialize NVML: Driver/library version mismatch  (NVML 550.163 vs 内核驱动)
```

**GPU 状态**：2×NVIDIA V100 存在但 NVML driver/library 不匹配（550.163 与内核驱动版本不一致）。本版为 CPU-only 运行（full-block-mtp-v1），不需要 GPU 透传；未擅自升级驱动/内核/重启宿主，如实记录。

### 2.2 旧TokenScope停止与端口释放

旧容器归属核实（docker inspect）：

```
{
  "Name": "tokenscope-fs01-acceptance-monitoring-1",
  "Image": "tokenscope/full-service:tokenscope-rv2-fs01-20261102",
  "com.docker.compose.project": "tokenscope-fs01-acceptance",
  "com.docker.compose.image": "sha256:037a641839b4f7d6ae0572f3af0fafc18a8b5e4c269bb9e19998819abce78710",
  "Ports": {"8000/tcp": [{"HostIp":"0.0.0.0","HostPort":"18002"},{"HostIp":"127.0.0.1","HostPort":"18001"}]},
  "Mounts": [
    {"Source":"/home/aarc/zhangxiyue/tokenscope-fs01-20261102-acceptance/input","Destination":"/inputs","RW":false},
    {"Source":"/home/aarc/zhangxiyue/tokenscope-fs01-20261102-acceptance/state","Destination":"/state","RW":true}
  ]
}
```

停止命令与结果：

```
$ cd /home/aarc/zhangxiyue/tokenscope-rv2-fs01-20261102
$ docker compose --env-file .../deployment.env -p tokenscope-fs01-acceptance -f compose.yaml -f .../compose.override.yaml down
Container tokenscope-fs01-acceptance-monitoring-1  Stopping/Stopped/Removed
Network tokenscope-fs01-acceptance_service  Removing/Removed
exit=0

$ ss -tlnp | grep -E '1800[012]'     # 无输出 → 端口全部释放
$ docker ps -a | grep -i tokenscope   # 无输出 → 无TokenScope容器
$ ps aux | grep -i tokenscope         # 无输出 → 无TokenScope进程
```

旧state保留未删除：`/home/aarc/zhangxiyue/tokenscope-fs01-20261102-acceptance/state/`（186M，未复制未迁移）。未使用 `down -v`/全局prune。

### 2.3 新空state冷启动证据

```
$ STATE_DIR=/home/aarc/zhangxiyue/TokenScope/state/tokenscope-v2-approved-20261102-20261102T0955
$ mkdir -p "$STATE_DIR" && ls -la "$STATE_DIR"   # 空目录
$ touch "$STATE_DIR/.write_test" && rm "$STATE_DIR/.write_test"  # 可写

$ docker compose --env-file <STATE>/deployment.env -p tokenscope-v2-approved -f compose.yaml config
# 核对：user 1015:2006；/inputs ro；/state rw；127.0.0.1:18002；cpus 8；mem 34359738368；镜像ID正确

$ docker compose ... up -d --pull never
```

冷启动初始状态（首启后立即验证）：

- `/monitoring/catalog` → `{"total":"0","catalog_revision":"0","items":[]}`，service_instance_id=`abf57577-2dcc-4ddb-9758-bbbd548ddfdf`
- `/monitoring/ma/catalog` → `{"total":"0","catalog_revision":"0","entries":[]}`
- 诊断目录为空；dispatcher.cursor/worker.lock 初始空
- 三个模型 readyz assets=verified（资产SHA见 §1.2 asset_identity 上 readyz 返回）

---

## 3. 真实数据盘点与字段核对（21个真实CSV）

输入根：`/home/aarc/zhangxiyue/10.20_Trace_extract`（只读挂载到容器 `/inputs`）。用户源与MA源字段不同，未混用。

### 3.1 用户监控（10.20_Trace/ 3个CSV）

| 文件 | 字节 | SHA256 | CSV记录数（含换行解析） | 模型 |
| --- | --- | --- | --- | --- |
| `10.20_Trace/DeepSeek-V4-Flash-10.20.csv` | 1,841,596,404 | `5600c009ee10505d4a45ad2e3f13ce6b346f0d3770ecd7104cb951af169b9881` | 36222 | DeepSeek-V4-Flash-0731 |
| `10.20_Trace/GLM-V5.2-10.20.csv` | 4,664,721,198 | `99dfaf7e246520a8c10f6d94d581c47757127cf77829d1b83af4aaab0306c611` | 26505 | GLM-5.2 |
| `10.20_Trace/Qwen-V3.6-27B-10.20.csv` | 20,375,268,478 | `e8e489f987f0b42cd63abff623e56eb3d39127899bd502896f7c5ca8560c200b` | 291911 | Qwen3.6-27B |

- 无BOM（首3字节 `22 68 61` = `"ha`），UTF-8，CRLF换行
- 表头（3文件一致）：```
"hash_id","appid","model_handle_start_time","completion_tokens","request_input"
```
- `model_handle_start_time` 格式 `DD/MM/YYYY HH:MM:SS.ffffff`（day-first），代码 `parse_utc` 支持并当作UTC解析
- `request_input` 内 `model` 字段 ∈ model_aliases（DeepSeek-V4-Flash-8K/32K/64K/128K、GLM-V5.2-32K/64K/128K、Qwen-V3.6-27B-32K/64K/128K 等），与 `domain.py DEFAULT_SETTINGS` 一致
- 时间范围（UTC）：DS 07:00:00.58~~09:18:57；GLM 07:00:00.45~~09:15:41；Qwen 07:00:00.20~09:13:37
- 最小脱敏行示例（DeepSeek，已截断 request_input）：```
"6ad71206-65d9-0500-be57-4f765318fffd","com.huawei.welink.athena","20/10/2026 07:00:03.699033","8","{\"model\":\"DeepSeek-V4-Flash-8K\",\"top_p\":.5,\"stream\":true,\"messages\":[...]}"
```

### 3.2 MA监控（10.20_MA/ 18个CSV / 9对）

| 配对 | pre文件 SHA256(前16) | now文件 SHA256(前16) | pre行数 | now行数 | UUID数 | pre窗口 | now窗口 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| DeepSeek-V4-Flash-32K | `2ab9e3184d27fa4d`… | `d90b19cc4a9210c8`… | 3501 | 3951 | 5(+1空) | 07:00:01~07:59:59 | 08:00:00~08:59:59 |
| DeepSeek-V4-Flash-64K | `51347c06f4ff1c2f`… | `092a0aca68dae31f`… | 1691 | 1388 | 2(+0空) | 07:00:00~07:59:53 | 08:00:00~08:59:53 |
| DeepSeek-V4-Flash-128K | `f6409923224dc76b`… | `68a9770409746f1a`… | 2874 | 2958 | 5(+1空) | 07:00:03~07:59:59 | 08:00:00~08:59:59 |
| GLM-V5.2-32K | `3af28fb623238ffd`… | `52ea18301a93fc10`… | 5377 | 5440 | 6(+1空) | 07:00:00~07:59:59 | 08:00:01~08:59:59 |
| GLM-V5.2-64K | `d394c5fd58ef6c13`… | `3ffa364a9e42d4aa`… | 4393 | 4334 | 9(+1空) | 07:00:00~07:59:59 | 08:00:00~08:59:59 |
| GLM-V5.2-128K | `98e5ec46738c5102`… | `5016d4c923a65d3f`… | 3513 | 3448 | 11(+1空) | 07:00:00~07:59:59 | 08:00:00~08:59:59 |
| Qwen-V3.6-27B-32K | `e08179112877e683`… | `a3a9050741c77b01`… | 110292 | 114838 | 26(+1空) | 07:00:00~07:59:59 | 08:00:00~08:59:59 |
| Qwen-V3.6-27B-64K | `89a4b37a5d29d9b4`… | `e329f6569485a876`… | 21119 | 21746 | 9(+1空) | 07:00:00~07:59:59 | 08:00:00~08:59:59 |
| Qwen-V3.6-27B-128K | `80d695b0a6de8963`… | `986a522c78fa4a9e`… | 12424 | 11492 | 13(+0空) | 07:00:00~07:59:59 | 08:00:00~08:59:59 |

- 表头（18文件一致，10列）：```
"model_standard_name","instance_uuid","hash_id","appid","request_time","model_handle_start_time","prompt_tokens","cached_tokens","completion_tokens","request_input"
```
- `model_standard_name` ∈ {DeepSeek-V4-Flash-32K/64K/128K, GLM-V5.2-32K/64K/128K, Qwen-V3.6-27B-32K/64K/128K}（均为合法 alias）
- **配对验证**：18个CSV形成9对（3模型×3规格），每对 pre 为 [07:00:00, 08:00:00)、now 为 [08:00:00, 09:00:00) 连续UTC一小时窗口，已逐对实测时间边界（非仅数量）；每对 pre/now 共享相同 instance_uuid 集合
- 个别实例UUID为短格式（如 Qwen-128K 含 `"1107"`/`"1108"`），为源数据本身，如实记录不猜测
- MA字段对应代码契约 `monitoring/ma/ingest.py COLUMNS`（§5.2），`source_timezone="UTC"` 与 MA Submit 契约一致

### 3.3 数据质量问题（真实数据，非产品缺陷）

**前导点数字**：三个Trace CSV + MA CSV 的 `request_input` 含非标准 JSON 数字（如 `"top_p":.5`、`"temperature":.3`、`"temperature":.03`、`"top_p":.8`），Python `json.loads` 拒绝（JSON 要求 `0.5`）。读取器将这类行标记 skipped（用户监控 file_quality 的 skipped_rows）。这是数据源格式问题，服务端契约未改动；如需要回补分析需用户授权另存派生文件（转换源码/字段映射/行数守恒记录）。MA quality 报告的 INVALID_JSON 同源。

---

## 4. 功能矩阵（第一阶段）

### 4.1 用户监控运行（3个Trace CSV）

| 模型 | user_run_id | base_run_id | index_revision(前16) | read_rows | valid_rows | skipped_rows | appid数 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| DeepSeek-V4-Flash | `ur-2663d4f5710e4dc9ba06eaa7786328cd` | `6b5a48c5-21fd-4b79-b2b1-9b89d4f5e537` | `c25b2fdf5fd855b9` | 36222 | 19186 | 17036 | 34 |
| GLM-V5.2 | `ur-b2899f15be07490b8c59c50ff41b46d4` | `4378f06d-b955-4cc7-9cf2-1d6bb81ea2c0` | `122dca21465f81df` | 26505 | 12446 | 14059 | 22 |
| Qwen-V3.6-27B | `ur-ebe06e744ee140da98fd8b20d0ae64a5` | `7f3a37b3-561e-4190-8e6e-dc135219d77c` | `c9f842fde87c9b4d` | 291911 | 119066 | 172845 | 21 |

S0 catalog 合计 **77 条 (appid×model)**（34+22+21），/monitoring/runs 3条 completed，publish_seq=1，view_schema=1。

提交命令（用户监控，DeepSeek 示例）：

```
curl -X POST [http://127.0.0.1:18002/monitoring/user-v2/runs](http://127.0.0.1:18002/monitoring/user-v2/runs) \
  -H "Content-Type: application/json" -H "X-TokenScope-Instance-Id: $INSTANCE_ID" \
  -d '{"submission_key":"trace-deepseek-v4-flash-20261020",
       "file_ref":"10.20_Trace/DeepSeek-V4-Flash-10.20.csv",
       "common_name":"DeepSeek-V4-Flash","model_id":"DeepSeek-V4-Flash-0731"}'
```

响应：`{"user_run_id":"ur-2663d4f5…","state":"accepted",…}`；轮询至 `state=ready`，index_revision 生成。

### 4.2 搜索/排行/排序/分页（DeepSeek 34 appid 实测）

| 动作 | 请求 | 期望 | 实际 | 结果 |
| --- | --- | --- | --- | --- |
| 默认排行 | `GET /rankings?limit=10` | 返回排行 | total=34, next_offset=10 | ✅ |
| 搜索子串 | `GET /rankings?appid_contains=com.huawei&limit=5` | 过滤命中 | total=27，5行 | ✅ |
| 排序降序 | `GET /rankings?sort=request_count&direction=desc&limit=3` | 降序 | 8675→2910→1159 | ✅ |
| 分页 | `GET /rankings?limit=5&offset=5&index_revision=…` | 第二段 | 5行，next_offset=10 | ✅ |
| 分页缺revision | `GET /rankings?limit=5&offset=5` | 409 | 409（INDEX_REVISION_CONFLICT） | ✅ 契约 |
| 非法sort | `GET /rankings?sort=invalid` | 422 | 422 | ✅ 契约 |
| metrics/modes | `GET /modes?appid=com.huawei.nebula.alpha_voc&index_revision=…` | 分箱数据 | bin_width=5000,count=8675,sum=4352192,share=1.0 | ✅ |
| 导出CSV | `GET /analysis-runs/{base}/requests/export?appid=…&format=csv` | 全量 | 200；8675数据行+1表头，2,479,585B | ✅ |
| 导出NDJSON | 同上 `format=ndjson` | 全量 | 200；8677行（含回执行），2,966,053B | ✅ |
| 幂等 | 相同key+相同内容 | 原run_id | 原run_id | ✅ |
| 幂等冲突 | 相同key+不同内容 | 409 | 409 SUBMISSION_KEY_CONFLICT | ✅ |

文件质量（file_quality）在 rankings 响应中可见：`read_rows/valid_rows/skipped_rows`（§4.1 表）。导出 CSV 列包含 `service_instance_id,view_schema_version,run_id,model_id,appid,settings_sha256,source_record_index,hash_id,time_utc,json_tokens,prompt_tokens,ideal_cached_input_tokens,ideal_compute_input_tokens,comple…`（截断），行数与 rankings request_count 一致（8675）。

### 4.3 前端四入口与展示（包内批准UI，未改动）

- 四入口固定：用户监控（`#/users`）、搜索与排行（`#/users/ranking`）、异常分析（`#/analysis`）、MA集群监控（`#/ma`）
- 全局总览：`#/overview`（S0 catalog，77条）
- 六卡/Token去向/直方图/1440-1920宽/L4-L5卡 等展示以包内批准UI为准，未因打包/现场改动
- **用户监控页面 run 选择机制**：浏览器 localStorage（key `tokenscope.v2.1:user:<instance>`），只记忆本浏览器打开过的 run，非服务端全量列表（详见 §9.1 用户验收反馈）

### 4.4 P90 TTFT（batch_reference_total_noncompute_v1）

- 后端可读取真实 P90：rankings 的 `prompt_p90`（如 DS com.huawei.nebula.alpha_voc=1236；Qwen S000…773=15007）
- 场景PUT接口已确认：`POST /monitoring/user-v2/scenarios`（Schema：BatchScenario 需 timing_model=`batch_reference_total_noncompute_v1`、chunk_tokens、chunk_seconds、source、min/max_prompt_tokens 等）
- 评估接口已确认：`POST /monitoring/user-v2/evaluations`（需 target_seconds、waiting_seconds、comparator le/lt、user_run_id、appid、scenario_id+revision）
- **缺参（待用户提供）**：目标T、非计算预算W、chunk_tokens K、chunk_seconds τ。按验收要求不填示例值、不默认W=0、不以V100硬件当校准。功能验收与性能校准分开，当前标记"待用户参数"。

### 4.5 MA监控（18 CSV / 9对，全部 completed）

| 配对 | ma_run_id | state | catalog_revision | quality_issues | UUIDs |
| --- | --- | --- | --- | --- | --- |
| DeepSeek-V4-Flash-32K | `1bb5a14b-6356-44fc-80f4-08c15fc1255c` | completed | 1 | 13103 | 5 |
| DeepSeek-V4-Flash-64K | `86ea66c9-af1a-4067-b01a-60000f33f0cd` | completed | 2 | 5039 | 2 |
| DeepSeek-V4-Flash-128K | `341015a6-b7dd-4777-8e57-fbb12f24827e` | completed | 3 | 10475 | 5 |
| GLM-V5.2-32K | `cc31e0bf-923c-4cef-9d81-9717efbc7517` | completed | 4 | 7990 | 6 |
| GLM-V5.2-64K | `04cf991d-4417-4dfb-ada5-66af73c5a997` | completed | 5 | 8375 | 9 |
| GLM-V5.2-128K | `f6b64f93-4145-4cde-b768-b0a06dbddd78` | completed | 6 | 6972 | 11 |
| Qwen-V3.6-27B-32K | `a9b6572a-1438-4f54-a4f8-c43431a93eef` | completed | 7 | 110799 | 26 |
| Qwen-V3.6-27B-64K | `ceb4da64-97fb-487b-9766-2b5e8f6e7f15` | completed | 8 | 40926 | 9 |
| Qwen-V3.6-27B-128K | `34d7b2a5-17e5-4f1b-9f54-020a6a829210` | completed | 9 | 23634 | 13 |

MA提交命令（DeepSeek-32K 示例）：

```
curl -X POST [http://127.0.0.1:18002/monitoring/ma/runs](http://127.0.0.1:18002/monitoring/ma/runs) \
  -H "Content-Type: application/json" -H "X-TokenScope-Instance-Id: $INSTANCE_ID" \
  -d '{"submission_key":"ma-deepseek-v4-flash-32k-20261020",
       "pre_file_ref":"10.20_MA/DeepSeek-V4-Flash-32K-pre.csv",
       "now_file_ref":"10.20_MA/DeepSeek-V4-Flash-32K-now.csv",
       "model_standard_name":"DeepSeek-V4-Flash-32K","model_id":"DeepSeek-V4-Flash-0731",
       "pre_start":"2026-10-20T07:00:00Z","now_start":"2026-10-20T08:00:00Z",
       "now_end":"2026-10-20T09:00:00Z","source_timezone":"UTC"}'
```

MA实例详情（DeepSeek-32K 实例 `0a5bf216-53d9-40ad-967f-49365bcd1c20`）关键值：

```
{
  "coverage": {"assigned":"740","production_input":"730","real":"0","encoded":"345","paired":"0"},
  "pre_assigned":"674","pre_encoded":"230","ideal_status":"available",
  "production_input_tokens":"6342361",
  "ideal": {"sample_count":"345","totals":{"input_tokens":"3145388","cached_tokens":"1131456","uncached_tokens":"2013932"},"hit_rate":0.3597190553279913},
  "real": {"sample_count":"0","totals":{"input_tokens":"0","cached_tokens":"0","uncached_tokens":"0"},"hit_rate":null},
  "hour": {"seconds":3600,"request_count":"740","real_count":"0","requests_per_second":0.20555555555555555,"uncached_tokens_per_second":null}
}
```

MA quality 报告问题行分类（以 DeepSeek-32K 为例，total=13103）：`INVALID_ID:1`、`INVALID_JSON:2`、`INVALID_MESSAGES:1`、`MISSING_TOKEN_VALUE:6`（其余为前导点数字触发的 INVALID_JSON 批量）。**real=0 是数据源只有 request_input、无实测命中观测**，如实标记（不插值、不把实际高于理想判错）。目录/规格选择、完整UUID、摘要/展开、质量两页签、三种箱宽、12×300秒桶与整小时总量守恒由服务端契约保证，API 层已核验（bins 12个、3600s、requests_per_second 守恒）。

### 4.6 重启持久性验证（同版本重启，重用同一state）

```
# Pre-restart:
catalog total=77 revision=3
DeepSeek-V4-Flash: state=ready  index_rev=c25b2fdf5fd855b9
GLM-V5.2:          state=ready  index_rev=122dca21465f81df
Qwen-V3.6-27B:     state=ready  index_rev=c9f842fde87c9b4d
MA catalog total=9 revision=9
readyz: ready=True

docker compose --env-file <STATE>/deployment.env -p tokenscope-v2-approved -f compose.yaml restart

# Post-restart:
catalog total=77 revision=3        （一致）
3× user-v2 runs: state=ready      （index_revision 不变）
MA catalog total=9 revision=9     （一致）
readyz: ready=True                 （一致）
→ 通过：已发布结果/回执/摘要恢复，GET不新增计算

---

## 5. 关键源码嵌入（包内原版，未修改）

### 5.1 用户监控 CSV 读取（src/tokenscope/ingestion/csv_reader.py）

```python
REQUIRED_COLUMNS = (
    "hash_id",
    "appid",
    "model_handle_start_time",
    "completion_tokens",
    "request_input",
)
```

```
def parse_utc(
    value: str, *, source_timezone: str = "UTC", field: str = "model_handle_start_time"
) -> tuple[int, str]:
    """Accept ISO calendar time, assuming UTC when no suffix; retain nanoseconds."""
    if source_timezone != "UTC":
        raise InvalidRow("UNSUPPORTED_SOURCE_TIMEZONE", field)
    normalized = value.strip()
    day_first = re.fullmatch(
        r"(\d{2})/(\d{2})/(\d{4}) (\d{2}:\d{2}:\d{2}(?:\.\d{1,9})?)", normalized
    )
    if day_first:
        day, month, year, clock_text = day_first.groups()
        normalized = f"{year}-{month}-{day} {clock_text}"
    # ... 解析为 UTC ns，保留纳秒；时间戳超 2^63 拒绝
```

### 5.2 用户监控 Submit 契约（src/tokenscope/user_monitoring/contracts.py）

```
class Submit(DTO):
    submission_key: Text
    file_ref: Text
    common_name: Text
    model_id: ModelId
```

### 5.3 MA CSV 列与 Submit 契约（monitoring/ma/ingest.py + contracts.py）

```
# ingest.py
COLUMNS = (
    "instance_uuid", "hash_id", "appid", "request_time", "model_handle_start_time",
    "prompt_tokens", "cached_tokens", "completion_tokens", "request_input",
)
# model_standard_name 可选列：非空值必须等于 binding.model_standard_name（MIXED_SPEC）
# request_time 必须落在 [pre_start, now_start) / [now_start, now_end)（OUTSIDE_WINDOW）
# cached_tokens <= prompt_tokens（CACHE_EXCEEDS_INPUT）
```

```
# contracts.py
class Submit(DTO):
    submission_key: Text
    pre_file_ref: Text
    now_file_ref: Text
    model_standard_name: Text
    model_id: Literal["GLM-5.2", "Qwen3.6-27B", "DeepSeek-V4-Flash-0731"]
    pre_start: Text
    now_start: Text
    now_end: Text
    source_timezone: Literal["UTC"] = "UTC"

    @model_validator(mode="after")
    def check_windows(self) -> Self:
        start, middle, end = [
            parse_utc(value)[0] for value in (self.pre_start, self.now_start, self.now_end)
        ]
        if middle - start != 3600_000_000_000 or end - middle != 3600_000_000_000:
            raise ValueError("pre and now must each span exactly one consecutive hour")
        if self.pre_file_ref == self.now_file_ref:
            raise ValueError("pre and now must reference distinct files")
        return self
```

> 
> 注：MA 契约硬校验 pre/now 各恰好连续一小时且文件不同。现场 9 对提交窗口（07-08/08-09）全部通过此校验，非仅数量匹配。

### 5.4 诊断契约（analysis_common/contracts.py）

```
class SourceSelection(Contract):
    source_kind: Literal["base", "user_v2"]
    base_run_id: Name | None = None
    user_run_id: Name | None = None
    appid: Name
    window: TimeWindow | None = None
    expected_index_revision: Name | None = None

    @model_validator(mode="after")
    def one_source(self) -> Self:
        if self.source_kind == "base":
            if self.base_run_id is None or self.user_run_id is not None:
                raise ValueError("base source requires only base_run_id")
            if self.expected_index_revision is not None:
                raise ValueError("base source has no user index revision")
        elif self.user_run_id is None or self.base_run_id is not None:
            raise ValueError("user_v2 source requires only user_run_id")
        return self
```

```
class DiagnosticSelection(Contract):
    reason_codes: tuple[Literal["low_hit", "request_length", "qps"], ...]
    enable_low_hit: bool
    enable_token_content: bool

    @model_validator(mode="after")
    def validate_routing(self) -> Self:
        if not self.reason_codes or len(set(self.reason_codes)) != len(self.reason_codes):
            raise ValueError("reason_codes must be nonempty and unique")
        if self.enable_low_hit != ("low_hit" in self.reason_codes):
            raise ValueError("reason and low_hit switch disagree")
        if not self.enable_token_content:
            raise ValueError("selected reasons require token_content")
        return self
```

### 5.5 诊断预算与 token 全量迭代（analysis_common/service.py）

```
@staticmethod
def _preflight(source: ResolvedSource, control: TaskControl) -> None:
    if source.scope.request_count > control.options.max_source_requests:
        raise ExecutionStopped("SOURCE_REQUEST_BUDGET_EXHAUSTED")
    total = 0
    for row in source._rows():
        control.checkpoint()
        length = len(row["request_input"].encode("utf-8"))
        if length > control.options.token_selection.budget.max_request_bytes:
            raise ExecutionStopped("REQUEST_BYTES_EXHAUSTED")
        total += length
        if total > control.options.max_source_bytes:
            raise ExecutionStopped("SOURCE_BYTES_EXHAUSTED")
    # ... 深度扫描（max_depth 超限 → SOURCE_DEPTH_EXHAUSTED）
```

```
# token_content 方向对每个请求全量分析（无抽样）：
checked, complete = 0, True
for request in source.iter_requests():
    control.request(request)
    fragment = plugin.analyze_request(
        request, options.token_selection,
        EvidenceCapabilities(),
        RunControl(options.token_selection.budget, control.cancelled),
    )
    # ... 写入 fragment/fragment_index
    checked += 1
    complete &= fragment.coverage.complete
    control.checkpoint()
```

> 
> 此循环是 Token 分析耗时的根因：与请求数线性正相关，无法按请求抽样（`max_units` 只限制提取单位）。实测数据见 §8.3。

---

## 6. 问题清单（编号/现象/归属/严重性/根因/修复/状态）

### P1 用户监控验收不通过 — 前端只显示最后一个打开的运行（用户报告，未修复）

- **现象**：用户访问 `#/users?run=<ur-ebe…>`（Qwen）后，用户监控页面只显示 Qwen，看不到 DeepSeek/GLM 数据。用户原话："你提供的 URL 只显示 Qwen，我怀疑浏览器没有保留三个模型的全量分析数据，或者错误地删除了前一个模型的数据"。
- **归属**：前端（users 入口）浏览器 localStorage 设计。服务端数据完整。
- **严重性**：**验收阻断（第一阶段）**。
- **根因分析（含证据）**：
  - 服务端完整：S0 catalog total=77（DS 34 + GLM 22 + Qwen 21），`/monitoring/runs` 3 条 completed，数据无丢失（§4.1）。
  - 前端 users 页 run 列表存于浏览器 `localStorage`，key 形如 `tokenscope.v2.1:user:<service_instance_id>`，只记忆**本浏览器打开过/提交过**的 run（前端JS：`remember(e){...runs:[e,...t.runs.filter(...)].slice(0,50)}`）。下拉切换的是本地记忆，非服务端全量。
  - 用 `#/users?run=<Qwen的user_run_id>` 打开时，默认 run=Qwen；localStorage 未含其他模型 → 页面只有 Qwen。
  - `#/overview` 全局总览页（S0 catalog）显示全部 77 条，已验证数据完整可用。
- **修复**：本次不修改前端（避免改变批准UI/契约）。**未修复**，如实记录；可后续改进（users 页增加"所有已发布运行"入口或改为服务端查询）。
- **用户要求**：如实记录到回传文档，不处理为通过。

### P2 诊断分析结论未在前端展示 — report 端点 items 为空（用户质疑，未修复）

- **现象**：用户在前端异常分析页看不到 L1-L5 卡片/分析结论。用户原话："为什么在前端我没有看到问题分析结论？比如L1卡片什么的？比如S00000000000000000000000000000773我认为他一定存在一些动态字段问题的"。
- **归属**：前端展示层 / API 数据组织（report 端点不聚合 items）。
- **严重性**：展示阻断（第二阶段）。
- **根因分析（含证据）**：
  - `GET /diagnostics/tasks/{id}/report` 返回 `"items": {}`（空），但 `GET /diagnostics/tasks/{id}/items/finding?limit=100` 实际返回 **100 个 findings**（每个任务）。
  - 前端若只读 report 端点则看不到 findings。findings 需单独 `/items/finding` 端点获取。
  - **用户质疑正确**：S000…773 确实存在动态字段问题——97 个 L4 findings，difference_pointers 指向 `/messages/0/content`、`/messages/3/content` 等（§7.3 详细证据）。
- **修复**：本次不修改前端。**未修复**，如实记录；建议前端异常分析页调用 `/items/finding` 渲染 L1-L5/T2-T4 卡片。
- **用户要求**：回传文档如实记录（含展示、Token耗时、数据量、用户质疑）。

### P3 Token异常分析耗时极长（性能约束，未修复）

- **现象**：token_content 方向全量逐请求分析，耗时与请求数线性正相关；大 appid（>5万请求）需 10-12 小时。
- **归属**：诊断引擎性能（CPU-only 8核预算，token 编码/比较）。
- **严重性**：中（影响大 appid 分析时效，不影响正确性）。
- **根因**：service.py token_content 循环 `for request in source.iter_requests()` 全量分析（§5.5），无请求级抽样；`max_units` 仅限制提取单位。
- **实测数据**：

| appid | 请求数 | token_content 实际耗时 | 每请求 |
| --- | --- | --- | --- |
| Qwen app_000000030502 | 905 | ~750s | ~0.83s |
| DeepSeek S000…773 | 1047 | ~760s | ~0.73s |
| DeepSeek com.huawei.ipd.tianzhou.ai | 864 | ~400s | ~0.46s |
| DeepSeek com.huawei.mbs.ilegal.ioc | 661 | ~480s | ~0.73s |
| Qwen com.huawei.aidp_dg06 | 171 | ~820s | ~4.8s |
| Qwen com.huawei.meca.admin.digital | 51 | ~1540s | ~30s |
| Qwen S000…773 (**实测完成**) | 54602 | ~30-40min（token全量） | ~0.04s |
| Qwen S000…1679 (**实测完成**) | 52098 | ~30-40min（token全量） | ~0.04s |

> 
> **重要修正（实测）**：两个 Qwen 大 appid 的 token_content **实际全量完成**（checked=54602/52098），耗时约 30-40 分钟而非预估 10-12 小时。每请求 ~0.04s。原因：Qwen 请求在 token_content 插件的分析路径较快（block_size=1536 大块、编码调用少、encoding_calls=0），而 meca.admin.digital（51请求/25分钟）是特例——其请求内容特殊触发慢路径。
> 注：aidp_dg06/meca.admin.digital 每请求耗时高，与其请求内容长/深（Qwen block_size=1536、长 prompt）相关。

- **修复**：本次不修改。**未修复**，如实记录；建议后续版本支持请求抽样/并行/增量分析。
- **用户决策**：8 小 appid 两方向 + 2 大 appid 仅 low_hit（实际因契约 enable_token_content 约束，大 appid 也完成了 token 全量）。

### P4 诊断任务提交 INVALID_ARGUMENT（已解决）

- **现象**：POST /diagnostics/tasks 返回 `{"error":{"code":"INVALID_ARGUMENT","message":"Invalid diagnostic input"}}`。
- **归属**：用户后端契约校验（SourceSelection.one_source）。
- **根因**：payload 同时传 `user_run_id` 和 `base_run_id`；契约要求 user_v2 来源**只允许 user_run_id**（§5.4）。
- **修复**：移除 base_run_id 字段 → 提交成功（202）。**已闭环**。

### P5 诊断任务 SOURCE_REQUEST_BUDGET_EXHAUSTED（已解决）

- **现象**：max_source_requests=1000 时 DeepSeek S000…773（1047请求）失败。
- **根因**：`_preflight` 要求 `scope.request_count <= max_source_requests`（§5.5）。
- **修复**：max_source_requests=100000、max_source_bytes=5368709120。**已闭环**。

### P6 诊断任务 SOURCE_DEPTH_EXHAUSTED（已解决）

- **现象**：max_depth=8 时失败；真实数据 JSON 最大嵌套深度 19 层（实测）。
- **根因**：`_preflight` 扫描 request_input JSON 深度超限。
- **修复**：max_depth=32。**已闭环**。

### P7 真实CSV request_input 前导点数字（数据源问题，非产品缺陷）

- **现象**：request_input 含 `.5`/`.3`/`.8`/`.03` 等非标准 JSON 数字，`json.loads` 拒绝 → skipped（DS 17036 / GLM 14059 / Qwen 172845 行）。
- **归属**：数据源格式。产品契约未改动。
- **建议**：数据生产侧规范化；如需回补分析另存派生文件（需用户授权，记录转换源码/SHA/行数守恒）。**未修复（非缺陷）**。

### P8 诊断任务 IDEMPOTENCY_CONFLICT（现场操作，已解决）

- **现象**：同一 submission_key 的第一次失败运行（含 base_run_id 的错误 payload）与修正后 payload（不含 base_run_id）意图不同 → 409。
- **根因**：幂等键基于完整 intent；错误 payload 已注册。
- **修复**：改用新 submission_key（`-v2-` 后缀）。**已闭环**。

---

## 7. 第二阶段：用户指定 appid 异常分析

### 7.1 授权与范围（用户原话记录）

> 
> "最后，完成MA验收后进入异常分析验收。对以下 模型*appid 进行异常分析，包括低命中率和Token异常。
> DeepSeek-V4-Flash: S00000000000000000000000000000773, S010320, com.huawei.ipd.tianzhou.ai, com.huawei.mbs.ilegal.ioc, com.huawei.newalliance
> Qwen-V3.6-27B: S00000000000000000000000000000773, S00000000000000000000000000001679, app_000000030502, com.huawei.aidp_dg06, com.huawei.meca.admin.digital"

大 appid 策略（用户选择）："先跑8小appid+2大appid low_hit"（2026-11-02 用户答复 AskUserQuestion）。

### 7.2 分析配置

- 来源：user_v2（复用第一阶段 user_run_id + expected_index_revision，不传 base_run_id）
- 8 小 appid：单任务 `reason_codes:["low_hit","request_length"]` + `enable_low_hit:true` + `enable_token_content:true`（两方向同范围）
- 2 大 appid：脚本意图传 `reason_codes:["low_hit"]` 仅 low_hit；但 **DiagnosticSelection 契约 `enable_token_content` 必须为 True**，且 stages 属性 = `("low_hit","token_content")`，因此任务**实际仍执行了 token_content 阶段**（全量 54602/52098 请求，见 §7.3 与 P3 修正）
- Token 规则：T2、T3、T4；低命中规则：L1–L5
- 预算：max_request_bytes=1048576, max_units=256, max_comparison_bytes=1048576, max_depth=32, max_candidates=32, max_encoding_calls=2000, candidate_limit=32, pilot_limit=4, max_source_requests=100000, max_source_bytes=5368709120, max_findings=100, max_experiments=20, max_combinations=10

提交命令（DeepSeek S000…773 dual 示例）：

```
curl -X POST [http://127.0.0.1:18002/diagnostics/tasks](http://127.0.0.1:18002/diagnostics/tasks) \
  -H "Content-Type: application/json" -H "x-tokenscope-service-instance: $INSTANCE_ID" \
  -d '{"request":{"submission_key":"diag-DeepSeek-S00000000000000000000000000000773-v2-20261102",
       "source":{"source_kind":"user_v2","user_run_id":"ur-2663d4f5710e4dc9ba06eaa7786328cd",
                 "appid":"S00000000000000000000000000000773",
                 "expected_index_revision":"c25b2fdf5fd855b9d236000e93857fc0adfb76182ac608fd5664edde9f269134"},
       "selection":{"reason_codes":["low_hit","request_length"],
                    "enable_low_hit":true,"enable_token_content":true}},
      "options":{"version":"diagnostics-runtime-1",
                 "token_selection":{"rule_ids":["T2","T3","T4"],"policies_json":"[]",
                   "budget":{"max_request_bytes":"1048576","max_units":"256",
                             "max_comparison_bytes":"1048576","max_depth":"32",
                             "max_candidates":"32","max_encoding_calls":"2000"}},
                 "candidate_limit":"32","pilot_limit":"4",
                 "max_source_requests":"100000","max_source_bytes":"5368709120",
                 "max_findings":"100","max_experiments":"20","max_combinations":"10",
                 "max_encoding_calls":"2000"}}'
```

响应：`{"task_id":"28c4393f-…","attempt":"1","status":"queued",…}`

### 7.3 分析结果汇总（findings 实测）

| 模型 | appid | 请求数 | 方向 | 状态 | L1 | L2 | L3 | L4 | L5 | T2/T3/T4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| DeepSeek | S00000000000000000000000000000773 | 1047 | dual | partial | 0 | 0 | 3 | 97 | 0 | 见报告items |
| DeepSeek | S010320 | 1038 | dual | partial | 0 | 0 | 2 | 98 | 0 | 见报告items |
| DeepSeek | com.huawei.ipd.tianzhou.ai | 864 | dual | partial | 0 | 0 | 1 | 99 | 0 | 见报告items |
| DeepSeek | com.huawei.mbs.ilegal.ioc | 661 | dual | partial | 0 | 0 | 1 | 99 | 0 | 见报告items |
| DeepSeek | com.huawei.newalliance | 104 | dual | partial | 0 | 0 | 2 | 98 | 0 | 见报告items |
| Qwen | app_000000030502 | 905 | dual | partial | 0 | 0 | 0 | 100 | 0 | 见报告items |
| Qwen | com.huawei.aidp_dg06 | 171 | dual | partial | 0 | 0 | 0 | 100 | 0 | 见报告items |
| Qwen | com.huawei.meca.admin.digital | 51 | dual | partial | 0 | 0 | 2 | 98 | 0 | 见报告items |
| Qwen | S00000000000000000000000000000773 | 54602 | dual（实际含token） | **partial（已完成）** | 0 | 0 | 12 | 88 | 0 | 全量54602 |
| Qwen | S00000000000000000000000000001679 | 52098 | dual（实际含token） | **partial（已完成）** | 0 | 0 | 0 | 100 | 0 | 全量52098 |

> 
> findings 数量受 `max_findings=100` 预算封顶（offset=100 已确认无更多）。L1/L2/L5 未触发为如实结果，不凑卡。**低命中 L3/L4 与 Token T2-T4 的完整 items 均可通过 `/diagnostics/tasks/{id}/items/{finding|fragment|rule_coverage|plan|experiment}` 端点获取**（P2 已记录前端未展示问题）。

### 7.4 实际 finding 证据（DeepSeek S000…773 示例，完整结构）

```
{
  "finding_id": "finding:9200bcb5bb5dd29b01e10653e9c21699b9cb1cbf2b02f675dc42bff9cc8110c2",
  "rule_id": "L4",
  "rule_version": "1",
  "comparison": {
    "left": {"base_run_id": "6b5a48c5-21fd-4b79-b2b1-9b89d4f5e537", "source_record_index": "122"},
    "right": {"base_run_id": "6b5a48c5-21fd-4b79-b2b1-9b89d4f5e537", "source_record_index": "152"},
    "left_raw_sha256": "ce9424ae873d709eac4cf3237474d8a470ceff7b9c1ad31a9afe226179c5e52c",
    "right_raw_sha256": "3d77119628bb29949fef572808db7194ac469cab796421f76e90e66d576c86af",
    "difference_pointers": ["/messages/0/content"],
    "association_ref": null,
    "lcp_tokens": "16268"
  },
  "source_pointer": "/messages/0/content",
  "advice": "可比请求历史内容不同；无可靠关联，不认定同一会话改写。",
  "recipe_json": null,
  "evidence_status": "needs_association"
}
```

rule_coverage（DeepSeek S000…773）：

```
[
  {"checked_requests":"1047","candidate_comparisons":"19091","partial":true,"reason_codes":[]},
  {"checked_requests":"3","candidate_comparisons":"4","partial":true,"reason_codes":["FINDING_BUDGET_EXHAUSTED"]}
]
```

> 
> **用户质疑验证**：S000…773 的 97 个 L4 findings 中 difference_pointers 指向 `/messages/0/content`、`/messages/3/content` 等，**证实存在动态字段（请求间内容差异）**。部分任务（如 DS ipd.tianzhou.ai）还触发了 `COMPARISON_BYTES_EXHAUSTED`（比较字节预算上限）→ partial，如实记录。

### 7.5 Token 分析（T2-T4）items 证据

Token 方向 fragments 已写入（每请求一个 fragment，含 locations/units/observations/finding_candidates）。以 DeepSeek S000…773 为例，`/items/fragment` 返回 1047 个 fragment（与请求数一致，token_content checked=1047）。具体 T2/T3/T4 规则覆盖与候选可经 `/items/finding`、`/items/fragment`、`/items/plan` 端点读取；规则仅 T2-T4（recommendations/capabilities 确认 token_rule_ids=["T2","T3","T4"]），未使用历史 T1 载荷。**默认空 recipe，无可评估建议时如实保留未知/未评估，不加载合成 recipe 或伪造 verified 声明**。

---

## 8. 用户验收记录（完整原话与处理）

### 8.1 第一次用户验收（2026-11-02）— 用户监控验收不通过

**用户验收原话（2026-11-02，验收反馈）**：

> 
> "首先，跑MA集群监控的数据分析。其次，用户监控验收不通过（你只需要如实记录到回传文档中即可）
> 1、你提供的 URL 只显示 Qwen，我怀疑浏览器没有保留三个模型的全量分析数据，或者错误地删除了前一个模型的数据
> 最后，完成MA验收后进入异常分析验收。对以下 模型*appid 进行异常分析，包括低命中率和Token异常。
> DeepSeek-V4-Flash: S00000000000000000000000000000773, S010320, com.huawei.ipd.tianzhou.ai, com.huawei.mbs.ilegal.ioc, com.huawei.newalliance
> Qwen-V3.6-27B: S00000000000000000000000000000773, S00000000000000000000000000001679, app_000000030502, com.huawei.aidp_dg06, com.huawei.meca.admin.digital"

- **MA 验收**：用户指令"跑MA集群监控的数据分析" → 9对 MA 全部 completed（§4.5），MA 验收通过（用户未单独指出 MA 问题）。
- **用户监控验收**：**不通过**（P1 详细记录，未处理为通过）。
- **异常分析授权**：上述 10 个 appid 明确授权；大 appid 策略用户选择"先跑8小appid+2大appid low_hit"（2026-11-02）。

### 8.2 用户主动质疑记录（2026-11-02/03，异常分析期间）

1. **前端看不到分析结论**（用户原话）：
   > "为什么在前端我没有看到问题分析结论？比如L1卡片什么的？比如S00000000000000000000000000000773我认为他一定存在一些动态字段问题的"
   - 用户质疑正确：S000…773 存在 97 个 L4 动态字段差异 findings（§7.4）。
   - 前端未展示根因：report 端点 items 为空，findings 需 `/items/finding` 端点（P2）。
2. **回传文档内容要求**（用户原话）：
   > "回传文档中需要记录这些问题，包括展示、Token异常分析时间很久、某些模型的数据量比较大等。尤其是用户主动的提问质疑。"
   - 已在 P2/P3/P7、§7、§8 如实记录。
3. **报告生成方式要求**（用户原话）：
   > "报告不能由看门狗生成，应该由agent综合上下文、验收要求、bug和修复、数据异常、用户反馈，综合生成，关键证据和代码嵌入正文。报告是最高优先级"
   - 本报告由 agent 综合上下文亲自撰写，非脚本自动拼装。
4. **大appid策略**（用户选择）："先跑8小appid+2大appid low_hit"

### 8.3 第二次用户验收

待用户。异常分析 **10/10 全部完成**（含两个大 appid 的 token_content 全量，见 §7.3/P3 修正），本报告已生成供审查。

---

## 9. 重启/恢复/回退

- **同版本重启恢复**：`docker compose restart` → catalog/runs/MA/readyz 前后一致（§4.6）✅ 通过
- **回退**：未执行（无需回退）。若需回退：正常停止本次项目（保留 state/日志）→ 用原旧镜像 `tokenscope/full-service:tokenscope-rv2-fs01-20261102` 及其匹配旧 state 备份启动，**不能用旧镜像读新版迁移后数据库**；不用 down -v/prune。
- 未执行的中断/容量测试：如实标记**未执行**（未为测试杀共享 daemon）。

## 10. 最终运行位置 / 访问方式 / 未决事项

- 服务：`[http://localhost:18002](http://localhost:18002)`（实验机 loopback，需 SSH 转发）
  ```sh

  ssh -L 18002:127.0.0.1:18002 [zhangxiyue@10.67.43.44](mailto:zhangxiyue@10.67.43.44)
  ```
  保持 SSH 连接后访问 `[http://localhost:18002](http://localhost:18002)`。

- 四入口可访问 URL（localhost）：
  - 全局总览：`[http://localhost:18002/#/overview](http://localhost:18002/#/overview)`（3模型77 appid）
  - 用户监控：`[http://localhost:18002/#/users?run=<user_run_id>](http://localhost:18002/#/users?run=<user_run_id>)`
  - 搜索与排行：`[http://localhost:18002/#/users/ranking?run=<user_run_id>](http://localhost:18002/#/users/ranking?run=<user_run_id>)`
  - 异常分析：`[http://localhost:18002/#/analysis](http://localhost:18002/#/analysis)`
  - MA集群监控：`[http://localhost:18002/#/ma](http://localhost:18002/#/ma)`
- 服务版本：tokenscope-v2-approved-20261102（镜像ID a38d0ab2…）；容器 tokenscope-v2-approved-monitoring-1；state `/home/aarc/zhangxiyue/TokenScope/state/tokenscope-v2-approved-20261102-20261102T0955`
- **未决事项**：
  1. P90 TTFT 参数（目标T/非计算预算W/chunk K/τ）待用户提供 → 当前"缺参"未通过
  2. P1 用户监控前端 localStorage run 记忆设计 → 待用户决定是否改进
  3. P2 前端不展示诊断 findings → 待前端改进（调 /items/finding）
  4. P3 Token 分析性能 → 待后续版本优化
  5. 两个大 appid（Qwen S000…773/S000…1679）token_content 实际已全量完成（契约 enable_token_content 约束），无需补跑
  6. 用户监控第一次验收不通过待用户复核（本报告已如实记录）

## 11. 自检

- 全文关键源码/diff/命令/证据嵌入正文，不依赖外部附件（§5 源码、§7.4 findings、§4 命令）
- 合成/本机历史未冒称真实/现场（全部为 10.20 真实 CSV + 本次部署实测）
- 第一次用户验收记录为**不通过**（用户明示，P1）；第二次待用户
- UIR-03 未修复（用户留 V3，非 V2 阻断）
- 未擅自变更顺序/数据/展示/契约
- 用户主动质疑（§8.2）与数据异常（§3.3）均已如实记录
- 未修复项均未打勾（P1/P2/P3/P7 未闭环）

---