# HUAWEI_V2_INVESTIGATION_REPORT — TokenScope V2 华为实验机只读调查

> 
> 生成时间：2026-11-03（现场 UTC+8）
> 调查性质：**只读调查，未实施产品修复，暂无修复后结果**
> 唯一交付文件：本文件。所有关键源码、命令、证据均嵌入正文，不依赖外部附件。
> 现场项目：/home/aarc/zhangxiyue/tokenscope-v2-approved-20261102-code/TokenScope

---

## 0. 结论摘要

| 调查项 | 结论 |
| --- | --- |
| 身份与资源核对 | ✅ 通过（容器/镜像/源码/HTTP资产/API/模型配置均与交付声明一致） |
| 21文件清单与数据量级 | ✅ 完成（SHA256全对齐；独立审计见§3） |
| 问题A：同一用户无法查看全部模型 | **已证实前端入口缺失**（UserMonitor 绑定单 user_run + localStorage 记忆，非服务端数据丢失） |
| 问题B：后台已完成，异常页没有结果 | **已证实默认入口无报告 + 推荐卡片为空**（10任务全 partial 非 ready → defaults=[]；configured_recipe_count=0 → recommendations 为空） |
| 问题C：MA 四项指标缺失 | **已证实两类根因**：DS 全部 cached_tokens 列空 → real=0；GLM 部分 UUID warmup_order_conflict → ideal 缺失 |
| tools/messages 工作负载 | ✅ 分层采样完成（§7） |
| 用户第二次验收 | **不通过**（用户明确，见 §8） |

**关键结论（对应旧报告勘误）**：

1. 旧报告"无实测命中观测"的说法**不成立**：GLM/Qwen 的 cached_tokens 列有值（GLM-32K-pre 5119 行 int、Qwen-32K-pre 110050 行 int），仅 DeepSeek 6 个文件该列 **100% 空串**。
2. 用户质疑"动态字段问题"**成立且有量化证据**：DeepSeek 工具型 appid 每请求携带 41-90KB 工具定义 Schema（§7），L4 消息差异 97-100 条/任务。
3. "Qwen/DeepSeek 不是典型 agentic infra" 假设**部分证伪**：DeepSeek 全部指定 appid 为高度 agentic（每请求 38-90 消息、27-51 工具调用），Qwen app_000000030502 为纯对话（每请求 2 消息、0 工具）。

**未实施产品修复**：本轮仅调查，未修改产品源码、配置、测试、HTML/dist、契约、recipe、原 CSV、业务数据库与已发布结果；未新建正式监控/异常分析/收益评估任务。以下修复建议仅为后续开发机审查 session 的输入。

---

## 1. 执行范围与实际身份

### 1.1 日期与 session

| 项 | 值 |
| --- | --- |
| 本地日期 | 2026-11-03（UTC+8） |
| 主机 | aarc22885（10.67.43.44） |
| 现场项目根 | /home/aarc/zhangxiyue/tokenscope-v2-approved-20261102-code/TokenScope（注意：/home/aarc/zhangxiyue/TokenScope 仅含 state，现场源码在此代码包目录） |
| session ID | **未知**。环境变量 CODEX_THREAD_ID/CODEX_SESSION_ID 在本会话不可得；不沿用开发机/前后端 ID（AGENTS.md 要求如实登记未知） |
| 本轮新增文件 | artifacts/research/ 下 8 个脚本/数据文件（清单见§9.2） |

### 1.2 交付身份核对（实际现场）

| 项 | 声明 | 实际核对 | 一致 |
| --- | --- | --- | --- |
| release_id | tokenscope-v2-approved-20261102 | 容器 /app/candidate.json 同 | ✅ |
| source_commit | b17cdc07b0a351d0f5c4fb1b26f0e05be2b3a0af | candidate.json 同 | ✅ |
| image_tag | tokenscope/full-service:tokenscope-v2-approved-20261102 | docker images 同 | ✅ |
| image_id | sha256:a38d0ab2cfe26154c96adb5e876538893005e5cb100fc5c53640823c391683a8 | `docker inspect` Image 字段同 | ✅ |
| service instance ID | abf57577-2dcc-4ddb-9758-bbbd548ddfdf | healthz/capabilities 返回同 | ✅ |
| state | /home/aarc/zhangxiyue/TokenScope/state/tokenscope-v2-approved-20261102-20261102T0955 | 挂载 `/state` rw 同 | ✅ |
| inputs | /home/aarc/zhangxiyue/10.20_Trace_extract | 挂载 `/inputs` ro 同 | ✅ |

容器运行配置（`docker inspect` 实际值）：

```
"Image": "sha256:a38d0ab2cfe26154c96adb5e876538893005e5cb100fc5c53640823c391683a8"
"Config.User": "1015:2006"
"HostConfig.Memory": 34359738368        // 32GiB
"HostConfig.NanoCpus": 8000000000       // 8 CPU
"HostConfig.PidsLimit": 256
"HostConfig.ReadonlyRootfs": true
"HostConfig.Tmpfs": {"/tmp": "size=536870912,mode=1777"}   // 512MiB
"Mounts": [
  {"Source":"/home/aarc/zhangxiyue/10.20_Trace_extract","Destination":"/inputs","RW":false},
  {"Source":"/home/aarc/zhangxiyue/TokenScope/state/tokenscope-v2-approved-20261102-20261102T0955","Destination":"/state","RW":true}
]
"Config.Cmd": ["--input-root","/inputs","--state-root","/state","--asset-root","/app","--cpu-budget","8","serve","--host","0.0.0.0","--port","8000","--viewer-root","/app/apps/viewer/dist"]
```

状态：`docker ps` → `tokenscope-v2-approved-monitoring-1` **Up 27 hours, health=healthy**（healthcheck 最近5次 ExitCode=0）；`127.0.0.1:18002` 端口监听；无 TokenScope 进程在容器外。

### 1.3 HTTP 静态资源 SHA256（实际 vs candidate.json 期望）

| 资源 | 实际SHA256 | 期望（candidate.json） | 匹配 |
| --- | --- | --- | --- |
| / (index.html) | e4c7e4e0969e52c39bbdc78bb6c48641742d0d75cc79605ef9aed2ae21fa46d6 | 同左 | ✅ |
| /assets/index-BN_hqTE_.js | 1d18c395fb5aca91bc77b469e58376a087a204f46c786d5bf9502c3ad6e55072 | 同左 | ✅ |
| /assets/index-BxqENh7v.css | 7de15a1ce92dc92d4d93a96c70425c1ea22663c5c4653c98cb4d9122ef0254a5 | 同左 | ✅ |
| /assets/export-validator-rZ4O78aZ.js | e52838c80a214d465b29b1e6049fabe887e80d8077fc5ce121061c8f109e9d41 | 同左 | ✅ |

### 1.4 容器内源码 vs 代码包 SHA（4 个关键文件逐字节一致）

```
/app/src/tokenscope/analysis_common/service.py    = 645ed266…090130
/app/src/tokenscope/analysis_common/contracts.py  = 727682c8…655139
/app/src/tokenscope/monitoring/ma/contracts.py    = 8eca3bb8…9bf2a83
/app/src/tokenscope/ingestion/csv_reader.py       = b277eab7…bb1ce6b
（与代码包目录四个文件 sha256sum 完全相同）
```

### 1.5 API / OpenAPI / 模型配置

- OpenAPI 66 路径，`x-user-contract-version: 2.0.0` 用户接口 9 操作（与旧报告一致）。
- `/monitoring/models/{id}/settings` 实际返回（与包内 DEFAULT_SETTINGS 一致）：

| model_id | block_size | cache_mode | encoding_profile | strategy |
| --- | --- | --- | --- | --- |
| GLM-5.2 | 128 | full_block | default | full-block-mtp-v1 |
| Qwen3.6-27B | 1536 | full_block_approximation | default | full-block-mtp-v1 |
| DeepSeek-V4-Flash-0731 | 32 | full_block_approximation | thinking_disabled | full-block-mtp-v1 |

- `/diagnostics/capabilities`：contract_version=analysis-common-1.0, http_version=diagnostics-http-1, schemas 含 submission/retry/token_evaluation/low_hit_evaluation/combination/authorization。
- `/diagnostics/discovery/capabilities`：transport=fetch-sse, **default_policy=ready_analysis_per_binding_direction_publication_order**（问题B关键：默认仅选 ready）。
- `/diagnostics/recommendations/capabilities`：read_only=true, token_rule_ids=[T2,T3,T4], adapters 含 token-auto-proposals-1。

### 1.6 主机资源（实际重查）

| 项 | 值 |
| --- | --- |
| CPU | 40 逻辑核（Intel Xeon Silver 4114）；`uptime` load=4.83,3.77,3.35（轻载） |
| 内存 | 375GiB，free -g: total=375 avail=351（足够） |
| 磁盘 | /home 96%已用 Avail 163G；/var/lib/docker 11%已用 Avail 3.1T；/ 86%已用 Avail 7.5G |
| inode | /home 2%已用；/var/lib/docker 4%已用；/ 7%已用（充足） |
| tmpfs 容器 | /tmp 512MiB（容器内，未测余量，只读调查未写入） |
| 容器配额 | 8 CPU / 32GiB / 256 pids（旧报告一致） |

**磁盘注意**：state 目录当前 **108G**（runs 47G + ma 61G + diagnostics 424M + view-artifacts 81M）。/home 仅剩 163G；若后续重跑大 appid 或新 state，需评估磁盘余量（旧 state 保留策略需用户决定）。

---

## 2. 执行边界遵守声明

- 未修改产品源码/测试/HTML/dist/契约/recipe/原CSV/业务数据库/已发布结果；未 commit/push/构建镜像/打包。
- 未 POST 新建诊断/监控/收益任务；未重算、未改配置、未手工改库。仅 GET 只读接口（携带正确身份头）与独立只读脚本。
- 只读脚本**未实例化会建表/迁移的产品 Store**；SQLite 未以可写方式打开（本轮未读业务 sqlite，全部证据来自 HTTP API + 原 CSV 流式扫描）。
- 原 CSV 文件未被写入（所有扫描只读；产物写入 artifacts/research/）。
- 浏览器复现使用独立临时 profile（firefox --headless --profile $(mktemp -d)），未触碰用户原浏览器缓存；SSH 转发方式不变（ssh -L 18002:127.0.0.1:18002 [zhangxiyue@10.67.43.44](mailto:zhangxiyue@10.67.43.44) → [http://localhost:18002](http://localhost:18002)）。
- 保留现有失败状态，未停容器/未重启/未新建服务。
- 运行中日志/WAL 自然变化与本轮写入明确区分：state 下 dispatcher.cursor、worker.lock 等运行态文件有服务自身自然写入（mtime 变化属服务运行，非本轮写入）；本轮新增文件仅限 artifacts/research/ 与最终报告。

---

## 3. 21文件清单与数据量级

### 3.1 用户监控（Trace 3 文件）

| 文件 | SHA256（完整） | 字节 | CSV逻辑记录数 | 表头 | 时间范围(UTC) | appid数 |
| --- | --- | --- | --- | --- | --- | --- |
| DeepSeek-V4-Flash-10.20.csv | 5600c009ee10505d4a45ad2e3f13ce6b346f0d3770ecd7104cb951af169b9881 | 1,841,596,404 | 36,222 | hash_id,appid,model_handle_start_time,completion_tokens,request_input | 07:00:00.577685 ~ 09:18:57.139602 | 62 |
| GLM-V5.2-10.20.csv | 99dfaf7e246520a8c10f6d94d581c47757127cf77829d1b83af4aaab0306c611 | 4,664,721,198 | 26,505 | 同上 | 07:00:00.449403 ~ 09:15:41.892777 | 28 |
| Qwen-V3.6-27B-10.20.csv | e8e489f987f0b42cd63abff623e56eb3d39127899bd502896f7c5ca8560c200b | 20,375,268,478 | 291,911 | 同上 | 07:00:00.203309 ~ 09:13:37.962902 | 53 |

合计：**26,881,586,080 字节、354,638 条记录**（与旧报告一致）。均无 BOM、UTF-8、CRLF。

### 3.2 MA监控（10.20_MA/ 18 文件）

每文件 SHA256（完整值在 artifacts/research/csv_21_scan.json；此处前16位）、字节、记录数、UUID 分布：

| 文件 | SHA256(前16) | 字节 | 记录数 | UUID数(含空) | 窗口(UTC) |
| --- | --- | --- | --- | --- | --- |
| DeepSeek-V4-Flash-128K-pre.csv | f6409923224dc76b | 636,704,070 | 2,874 | 6 | 07:00:03.85 ~ 08:00:21.78 |
| DeepSeek-V4-Flash-128K-now.csv | 68a9770409746f1a | 485,594,752 | 2,958 | 6 | 08:00:01.03 ~ **09:18:57.14** |
| DeepSeek-V4-Flash-32K-pre.csv | 2ab9e3184d27fa4d | 128,816,403 | 3,501 | 6 | 07:00:01.20 ~ 08:09:00.17 |
| DeepSeek-V4-Flash-32K-now.csv | d90b19cc4a9210c8 | 135,899,663 | 3,951 | 6 | 08:00:00.29 ~ 09:12:03.71 |
| DeepSeek-V4-Flash-64K-pre.csv | 51347c06f4ff1c2f | 201,243,206 | 1,691 | 2 | 07:00:00.76 ~ 07:59:53.24 |
| DeepSeek-V4-Flash-64K-now.csv | 092a0aca68dae31f | 146,603,823 | 1,388 | 3 | 08:00:01.05 ~ 09:09:34.02 |
| GLM-V5.2-128K-pre.csv | 98e5ec46738c5102 | 1,080,263,415 | 3,513 | 12 | 07:00:00.45 ~ 08:11:27.37 |
| GLM-V5.2-128K-now.csv | 5016d4c923a65d3f | 1,063,957,041 | 3,448 | 12 | 08:00:00.92 ~ 09:11:09.53 |
| GLM-V5.2-32K-pre.csv | 3af28fb623238ffd | 489,189,617 | 5,377 | 7 | 07:00:01.02 ~ 08:09:01.55 |
| GLM-V5.2-32K-now.csv | 52ea18301a93fc10 | 387,369,684 | 5,440 | 7 | 08:00:01.33 ~ 09:11:24.98 |
| GLM-V5.2-64K-pre.csv | d394c5fd58ef6c13 | 848,976,899 | 4,393 | 10 | 07:00:00.97 ~ 08:14:22.60 |
| GLM-V5.2-64K-now.csv | 3ffa364a9e42d4aa | 797,464,843 | 4,334 | 10 | 08:00:01.01 ~ 09:15:41.89 |
| Qwen-V3.6-27B-128K-pre.csv | 80d695b0a6de8963 | 3,687,102,522 | 12,424 | 13 | 07:00:00.20 ~ 08:00:00.17 |
| Qwen-V3.6-27B-128K-now.csv | 986a522c78fa4a9e | 3,434,941,352 | 11,492 | 13 | 08:00:00.23 ~ 08:59:59.96 |
| Qwen-V3.6-27B-32K-pre.csv | e08179112877e683 | 2,882,398,971 | 110,292 | 27 | 07:00:00.35 ~ 08:10:35.47 |
| Qwen-V3.6-27B-32K-now.csv | a3a9050741c77b01 | 2,745,733,455 | 114,838 | 27 | 08:00:00.25 ~ **09:13:37.96** |
| Qwen-V3.6-27B-64K-pre.csv | 89a4b37a5d29d9b4 | 3,775,418,077 | 21,119 | 10 | 07:00:00.37 ~ 08:00:00.03 |
| Qwen-V3.6-27B-64K-now.csv | e329f6569485a876 | 3,879,037,577 | 21,746 | 9 | 08:00:00.66 ~ 08:59:59.99 |

**注意（与旧报告一致且需强调）**：多个 now 文件的实际最大时间戳**超出 08:00-09:00 窗口**（DS-128K-now 到 09:18、GLM-64K-now 到 09:15、Qwen-32K-now 到 09:13），即 MA 窗口外有尾部请求被 ingest 标记 OUTSIDE_WINDOW 或 handle_outside。MA run binding 的 pre_start/now_start/now_end 均为 07:00/08:00/09:00 UTC（契约 `check_windows` 硬校验通过），超出部分不计入 assigned。

### 3.3 Trace 有效性审计（独立脚本流式全量，非抽样）

主因分类（互斥主因；次因可重叠）：

| 主因 | 计数 | 说明 |
| --- | --- | --- |
| VALID | 151,320 | 严格有效（5列、hash_id≥8、appid非空、时间可解析、completion整数、request_input JSON 含 model 字符串字段） |
| BAD_JSON | 194,042 | request_input 无法 `json.loads`（**含前导点数字**，如 `.5`、`.8`；源数据格式问题） |
| NO_MODEL_FIELD | 4,809 | JSON 合法但缺 `model` 键或值非字符串 |
| EMPTY_JSON | 4,455 | request_input 空串 |
| BAD_JSON_ROOT | 12 | JSON 根非对象 |
| **合计** | **354,638** | 与 CSV 记录数守恒 |

每模型：

| 模型 | 原始 | 严格有效 | 跳过 | 有效占比 |
| --- | --- | --- | --- | --- |
| DeepSeek-V4-Flash-0731 | 36,222 | 19,220 | 17,002 | 53.1% |
| GLM-5.2 | 26,505 | 12,841 | 13,664 | 48.4% |
| Qwen3.6-27B | 291,911 | 119,259 | 172,652 | 40.9% |
| 合计 | 354,638 | 151,320 | 203,318 | 42.7% |

**与旧报告基线的口径差异（勘误）**：旧报告记 "150,698 有效、203,940 跳过、拒绝 57.51%"；本次独立审计为 151,320 有效、203,318 跳过。差异原因：旧报告统计的是**监控索引**（含时间窗口/去重等二次过滤）后的行数，本次为**原始 CSV 记录数**的严格有效性；两者定义不同，不构成数据矛盾。另：旧报告称"DeepSeek S000…773=1047 条"，本次原始有效 1048 条，差异 1 条为索引窗口边界过滤（该 appid 有 1 条 09:18:57 越界请求被 task scope 排除）。

### 3.4 指定 10 个 appid 的有效请求数（原始文件 vs 任务 scope）

| 模型 | appid | 原始记录 | 严格有效 | 跳过 | 任务 scope request_count |
| --- | --- | --- | --- | --- | --- |
| DeepSeek | S000…773 | 1,163 | 1,048 | 115(BAD_JSON) | 1,047 |
| DeepSeek | S010320 | 1,067 | 1,042 | 25(NO_MODEL) | 1,038 |
| DeepSeek | com.huawei.ipd.tianzhou.ai | 2,012 | 868 | 1,144(BAD_JSON 9/NO_MODEL 44/EMPTY 1091) | 864 |
| DeepSeek | com.huawei.mbs.ilegal.ioc | 764 | 666 | 98(BAD_JSON 75/NO_MODEL 23) | 661 |
| DeepSeek | com.huawei.newalliance | 109 | 104 | 5(NO_MODEL) | 104 |
| Qwen | app_000000030502 | 905 | 905 | 0 | 905 |
| Qwen | com.huawei.aidp_dg06 | 202 | 171 | 31(BAD_JSON) | 171 |
| Qwen | com.huawei.meca.admin.digital | 51 | 51 | 0 | 51 |
| Qwen | S000…773 | 140,540 | 54,602 | 85,938(BAD_JSON) | 54,602 |
| Qwen | S000…1679 | 53,537 | 52,112 | 1,425(BAD_JSON) | 52,098 |
| **合计** |  | **200,350** | **111,569** |  | 10任务 request_count 合计 111,541 |

**勘误说明**：10 个 appid 原始有效合计 111,569 与 10 任务 scope 合计 111,541 差 28 条，全部为 scope 窗口/边界过滤（如 ipd.tianzhou.ai 868→864、S010320 1042→1038、Qwen S000…1679 52112→52098 各差 4~14 条）。任务实际分析范围为 scope request_count（111,541），与旧报告一致。

### 3.5 raw_body 大小与结构（全量流式 + 指定appid分层样本）

全文件字节分布（log2 桶直方图近似分位数；max 为全扫描最大值，精确）：

| 文件 | P50(≈) | P90(≈) | P95(≈) | P99(≈) | max(精确) |
| --- | --- | --- | --- | --- | --- |
| DeepSeek-V4-Flash-10.20.csv | 6,143 | 196,607 | 196,607 | 393,215 | 845,023 |
| GLM-V5.2-10.20.csv | 196,607 | 393,215 | 393,215 | 786,431 | 1,047,042 |
| Qwen-V3.6-27B-10.20.csv | 24,575 | 196,607 | 393,215 | 393,215 | 1,182,936 |

（近似方法：按 2 的幂桶中点估计；max 是全文件扫描精确最大值。）

指定 appid 的**全量解析**结构（10 个 appid 全部行 json.loads 统计，非采样）：

| appid | 解析OK | messages总数 | 角色分布(主) | tools | tool_calls | tool_results | 最深嵌套 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| DS S000…773 | 1,048 | 63,931 | system 1037/assistant 29386/tool 29416/user 4092 | 999 | 27,540 | 29,416 | 13 |
| DS S010320 | 1,067 | 114,175 | assistant 54290/tool 53627/system 1038/user 5220 | 1,020 | 51,466 | 53,627 | 13 |
| DS ipd.tianzhou.ai | 912 | 28,572 | assistant 13670/tool 11528/user 2773/system 601 | 501 | 9,395 | 11,528 | **19** |
| DS mbs.ilegal.ioc | 689 | 39,080 | assistant 17515/tool 17623/system 666/user 3276 | 627 | 15,868 | 17,623 | 13 |
| DS newalliance | 109 | 9,374 | assistant 4560/tool 3920/user 790/system 104 | 103 | 3,920 | 3,920 | 13 |
| Qwen app_000000030502 | 905 | 1,816 | user 908/assistant 3/system 905 | **0** | 0 | 0 | 3 |
| Qwen aidp_dg06 | 171 | 14,334 | assistant 6700/tool 6530/user 933/system 171 | 167 | 6,271 | 6,530 | 13 |
| Qwen meca.admin.digital | 51 | 5,744 | assistant 2706/tool 2447/user 540/system 51 | 51 | 2,372 | 2,447 | 13 |
| Qwen S000…773 | 54,602 | 197,305 | **user 109141**/system 35357/assistant 52789/tool 18 | 14,611 | 15 | 18 | 10 |
| Qwen S000…1679 | 52,112 | 59,127 | user 52210/assistant 2877/tool 3917/system 123 | 119 | 2,787 | 3,917 | 13 |

（注：本统计为全量解析 10 个 appid 的 request_input；"工具型"特征与"Qwen S000…773 大 appid 低 tool 密度" 形成鲜明对照。**不将普通消息内 JSON 误判为真实工具返回**，见 §7。）

### 3.6 各研究范围预算表

| 研究范围 | 实际量级（实测） | 当前上限（实测快照） | 覆盖/超限 | 停止点 | 建议 |
| --- | --- | --- | --- | --- | --- |
| 任务输入 | scope 合计 111,541 请求 | max_source_requests=100000（每任务 payload 实际值） | 大 Qwen 54,602/52,098 < 100000 → 未触顶 | — | 大 appid 无需提额 |
| 单请求 | 实测最大 1,182,936 字节（Qwen全文件）/ 845,023（DS） | max_request_bytes=1048576（1MiB） | **Qwen 最大 1.18MB > 1MiB 单请求上限**（若个别请求超限，preflight 会拒绝整任务或截断） | — | 需评估单请求 >1MiB 的分布（§3.5 P99≈393KB，长尾未知） |
| 嵌套深度 | 指定 appid 最深 19（ipd.tianzhou.ai） | max_depth=32 | 未触顶（<32） | — | 32 足够 |
| 低命中候选 | DS S000…773 comparisons=19091 | candidate_limit=32, max_comparison_bytes=1MiB | 已产出但 L1/L2 因 FINDING_BUDGET_EXHAUSTED 只查 3 条 | FINDING_BUDGET_EXHAUSTED | 低命中扫描预算不足（见 §6） |
| Token 比较 | token_content 全量 checked（1047~54602） | max_encoding_calls=2000 | 大 Qwen encoding_calls=0（缓存复用），85c247db=105 | 未触顶 | — |
| 发现数 | 每任务 findings 恰 100 条 | max_findings=100 | **触顶**（L4/L3 各 97-100/2-12） | 100条封顶 | 需区分"展示上限"与"证据保留上限"（见 §6.2） |
| 建议扩展 | recommendation_count 全 0（configured_recipe_count=0） | RecommendationBudget（proposals/prepared_operations 等） | 未触顶，因**配方为 0** | TOKEN_FRAGMENT_INCOMPLETE | 先解决配方/依据缺失（见 §6） |
| 存储 | state 108G（runs 47G+ma 61G+diag 424M+view-artifacts 81M） | 主机 /home Avail 163G | **/home 96%已用** | 磁盘余量 | 后续新 state/重跑需用户决定旧 state 保留 |
| CPU/内存 | 容器 8CPU/32GiB；主机 load<5/40 | 配额未变 | 未超 | — | — |

**未知项**：单请求 >1MiB 的精确占比未单独全量统计（P99≈393KB 但 max 1.18MB 提示长尾存在，需分桶确认超限请求数）；10 任务墙钟耗时仅能从 terminal_at 间隔推断（串行执行间隔，见 §3.7），无任务内分阶段计时。

### 3.7 既有任务耗时与性能（终端时间推断，非精确计时）

10 个唯一任务按 `terminal_at`（诊断 catalog 发布字段）串行完成（seq 9-21，中间有 3 个重复提交被幂等拒绝或作为额外任务，见 §6.1）：

| seq | task_id | appid | request_count | terminal_at(UTC) | 与上一条间隔 |
| --- | --- | --- | --- | --- | --- |
| 9 | 103c517b… | DS S000…773 | 1,047 | 2026-11-02T15:17:24.848Z | — |
| 12 | 28c4393f… | DS S000…773(重试) | 1,047 | 2026-11-03T02:37:19.783Z | 11h20m（含夜间停顿） |
| 13 | 9d70799b… | DS S010320 | 1,038 | 02:53:28.023Z | 16m9s |
| 14 | 362863da… | DS ipd.tianzhou.ai | 864 | 03:00:33.817Z | 7m6s |
| 15 | cb2d4aa8… | DS mbs.ilegal.ioc | 661 | 03:09:08.442Z | 8m35s |
| 16 | ee4a4510… | DS newalliance | 104 | 03:13:16.919Z | 4m8s |
| 17 | f771bb41… | Qwen app_000000030502 | 905 | 03:29:50.185Z | 16m33s |
| 18 | 92e9e512… | Qwen aidp_dg06 | 171 | 03:45:42.298Z | 15m52s |
| 19 | 85c247db… | Qwen meca.admin.digital | 51 | 04:13:33.977Z | 27m52s |
| 20 | f67facf6… | Qwen S000…773 | 54,602 | 06:52:24.864Z | 2h38m51s |
| 21 | 502ec477… | Qwen S000…1679 | 52,098 | 07:15:21.956Z | 22m57s |

**重要（对旧报告 P3 的修正依据）**：大 Qwen S000…773（54,602 请求）从 seq19 结束（04:13:33）到 seq20 完成（06:52:24）间隔 2h38m51s，但**间隔含调度间隙，非纯执行时间**；旧报告称"30-40 分钟全量完成"为现场实测（每请求 ~0.04s），本报告不采信也不否定（无任务内计时，标注为未知）。S000…1679（52,098）seq20→seq21 间隔 22m57s 与旧报告"30-40 分钟"接近。**不能仅按请求数线性外推**，也不能用 encoding_calls=0 推断没有 CPU 成本（token_content 循环逐请求执行，见 §6.3）。

---

## 4. 问题A：同一用户无法查看全部模型

### 4.1 用户反馈

> 
> V1 同一用户入口可以看到该用户使用的所有模型；V2 一个 URL 似乎只能看到某个模型（用户原话："你提供的 URL 只显示 Qwen，我怀疑浏览器没有保留三个模型的全量分析数据"）。

### 4.2 服务端数据事实（只读接口）

1. **S0 基础目录（/monitoring/catalog）**：total=77 条目，覆盖 3 模型 × 62+28+53 个原始 appid 的去重后 77 组合。**同一 APPID 在多个模型下存在**，例如：
   - `S00000000000000000000000000000773`：DeepSeek-V4-Flash-0731 + Qwen3.6-27B（两个 user-run 均含）
   - `com.huawei.mbs.ilegal.ioc`：DeepSeek + Qwen
   - `com.huawei.meca.admin.digital`：GLM + Qwen
   - `com.huawei.gtsdata.datalinkpro`：GLM + Qwen
   - `com.huawei.rnd.common.pool`：DeepSeek + GLM
   - 单模型存在对照：`S010320`（仅 DeepSeek）、`app_000000030502`（仅 Qwen）、`com.huawei.atebrain.atewingman`（仅 GLM）
2. **V2 用户运行（/monitoring/user-v2/runs/{user_run_id}）** 实际 3 条，每模型一条，**state=ready**：

| user_run_id | common_name | model_id | base_run_id | index_revision(前16) |
| --- | --- | --- | --- | --- |
| ur-2663d4f5710e4dc9ba06eaa7786328cd | DeepSeek-V4-Flash | DeepSeek-V4-Flash-0731 | 6b5a48c5-21fd-4b79-b2b1-9b89d4f5e537 | c25b2fdf5fd855b9 |
| ur-b2899f15be07490b8c59c50ff41b46d4 | GLM-V5.2 | GLM-5.2 | 4378f06d-b955-4cc7-9cf2-1d6bb81ea2c0 | 122dca21465f81df |
| ur-ebe06e744ee140da98fd8b20d0ae64a5 | Qwen-V3.6-27B | Qwen3.6-27B | 7f3a37b3-561e-4190-8e6e-dc135219d77c | c9f842fde87c9b4d |

（注：monitoring 接口身份头为 `X-TokenScope-Instance-Id`；诊断接口为 `X-TokenScope-Service-Instance`。无身份头时 user-v2 runs 返回 `INSTANCE_MISMATCH`——但浏览器前端由 V2App 的 `verifyUserContract()` 自动携带，非问题A 根因。）

3. **V2 用户监控的 APPID 排行**：每个 user-run 独立（如 Qwen run rankings 仅含 Qwen 的 21 个 appid）。

### 4.3 前端读取链（源码证据）

- `V2App.tsx`：`connect()` 调 `verifyUserContract()` + `getJson('CatalogResponse','/monitoring/catalog')`，随后 `setApi(new V2Client(service_instance_id))`；`page.startsWith('users') → <UserMonitor key={api.instance}/>`。
- `UserMonitor.tsx`：
  - `const store = useRef(new V2Records(api.instance, 'user'))`；`persist(() => store.current.remember(r.user_run_id))` → **最近运行只写浏览器 localStorage**，key=`tokenscope.v2.1:user:{instance}`（v2-records.ts）。
  - 模型区域渲染：`<strong>{display?.receipt.common_name}</strong><small>{display?.receipt.model_id}</small>` —— **静态来自单个 receipt**，无"切换到其他模型"入口。
  - `open(run)`：`const id = q.get('run') ?? saved.runs[0] ?? saved.intent?.runId` —— 只打开一个 run。
  - APPID 下拉来自 `display?.ranking?.rows`（单模型排行）。
- **对照 V1**（`state/catalog.ts` 的 `loadCatalog`）：分页读 `/monitoring/catalog` **全目录**，`items.map(item => JSON.stringify([item.appid, item.model_id]))` 以 (appid, model) 为键生成模型按钮——V1 同一 APPID 可跨模型切换。V1 app.tsx 按 catalog 条目渲染。

### 4.4 复现步骤与结论

| 步骤 | 预期（V1） | 实际（V2） |
| --- | --- | --- |
| 浏览器打开 `[http://localhost:18002/#/users](http://localhost:18002/#/users)` | 显示所有模型×APPID 入口 | **无历史分析**（若本机无 localStorage 记录），提示"打开运行/新建分析" |
| 打开 Qwen run `ur-ebe06e744ee140da98fd8b20d0ae64a5` | — | 显示 Qwen 21 appid，模型区域固定 Qwen |
| 刷新页面 | — | `saved.runs[0]` 恢复 Qwen run（localStorage），仍只显示 Qwen |
| 打开 DS run `ur-2663d4…` | — | 显示 DS 34 appid，但**之前的 Qwen 视图被覆盖**（同一 localStorage key 只记最近一个） |
| 从搜索排行返回 | — | `history.replaceState` 保持当前 run，无跨模型切换 |

**已证实根因**：V2 前端 UserMonitor 设计为**单 user_run 绑定**（模型区域静态、最近运行 localStorage 单槽、无目录/模型切换 UI），服务端数据完整（77 目录条目 + 3 个 ready user-run）。**数据存在但入口缺失**，非服务端删除/丢失。

**影响范围**：所有多模型用户均受影响（本现场 3 个模型全部无法在同一入口查看）。GLM/Qwen 共享 appid（如 meca.admin.digital、gtsdata.datalinkpro）无法对照。

### 4.5 修复建议（本轮仅建议）

1. **恢复目录驱动的模型发现**：UserMonitor 增加"模型/用户运行切换"区，读取 `/monitoring/user-v2/runs` 可用列表（或从 catalog 派生 common_name 列表），同一 APPID 可切换到其他模型的 user-run（各 run 独立 rankings/snapshot，不混合计算）。
2. **保留 V2 搜索/排行/TTFT**：切换模型仅替换 `receipt`，Ranking/TTFT 组件保持按新 run 重读。
3. **localStorage 槽位扩展**：`V2Records.runs` 已支持 50 条，但 UI 只显示 `recent` 列表；可在"打开运行"弹窗显示全部 3 个模型 run。
4. **不做**：不以跨租户 userhash 聚合，不把不同模型指标混合；多 URL/手填 run ID 不能作为解决方案。
5. 同 APPID 多模型的可访问 ≠ 跨模型指标混合（各模型独立口径）。

---

## 5. 问题B：后台已完成，异常页没有结果

### 5.1 用户反馈

> 
> "为什么我在前端没有看到问题分析结论？比如 L1 卡片什么的？比如 S000…773 我认为它一定存在一些动态字段问题的"（用户第二次验收不通过）。

### 5.2 服务端事实（只读接口完整核对）

**10 个唯一任务（诊断 catalog 13 条含 3 条重复提交）**：全部 `status=partial`、`report_published=true`、**`default_eligible=false`**、`catalog.defaults=[]`。

| task_id(前8) | appid | request_count | 方向 | status | report_published | default_eligible |
| --- | --- | --- | --- | --- | --- | --- |
| 103c517b | DS S000…773 | 1,047 | low_hit+token | partial | true | false |
| 9d70799b | DS S010320 | 1,038 | low_hit+token | partial | true | false |
| 362863da | DS ipd.tianzhou.ai | 864 | low_hit+token | partial | true | false |
| cb2d4aa8 | DS mbs.ilegal.ioc | 661 | low_hit+token | partial | true | false |
| ee4a4510 | DS newalliance | 104 | low_hit+token | partial | true | false |
| f771bb41 | Qwen app_000000030502 | 905 | low_hit+token | partial | true | false |
| 92e9e512 | Qwen aidp_dg06 | 171 | low_hit+token | partial | true | false |
| 85c247db | Qwen meca.admin.digital | 51 | low_hit+token | partial | true | false |
| f67facf6 | Qwen S000…773 | 54,602 | low_hit+token | partial | true | false |
| 502ec477 | Qwen S000…1679 | 52,098 | low_hit+token | partial | true | false |

（13 条含 3 条 app_000000030502 重复（f0f39a39/f1fc27f7/f771bb41，seq 10/11/17）与 1 条 DS S000…773 重试（28c4393f，seq12），为提交幂等/重试产生的额外任务，不是 10 个唯一 appid 的额外分析。）

**身份头**：诊断接口必须 `X-TokenScope-Service-Instance: abf57577-…`（用 `X-TokenScope-Instance-Id` 会返回 INVALID_REQUEST）。前端 `DiscoverySession` 自动携带，非问题根因。

### 5.3 读取链逐端点核对（以 103c517b 为例）

| 端点 | 结果 |
| --- | --- |
| GET /diagnostics/tasks/{id}/report | status=partial; stages: low_hit(checked=3, partial), token_content(checked=1047, partial)；items=[]（**report 不含 findings 明细**）；encoding_calls=0 |
| GET /diagnostics/tasks/{id}/recommendation-summary | availability=computed; configured_recipe_count=**0**; recommendation_count=**0**; difference_group_count=**97**; proposal_coverage={eligible:1047, checked:0, reason_codes:[**TOKEN_FRAGMENT_INCOMPLETE**]} |
| GET /diagnostics/tasks/{id}/recommendations | items=[]（空） |
| GET /diagnostics/tasks/{id}/difference-groups | items 97 组，全部 rule_id=L4（title="历史内容差异"，members 2-3/组） |
| GET /diagnostics/tasks/{id}/items/finding?limit=100 | **100 条 findings**：L4 97 + L3 3（findings 明细在此，不在 report.items） |
| GET /diagnostics/tasks/{id}/items/rule_coverage | low_hit: checked=1047/3? 见下 |

各任务 rule_coverage 汇总：

| 方向 | 代表值 | 说明 |
| --- | --- | --- |
| low_hit | 103c517b: checked=**3**, comparisons=4, partial, reason=FINDING_BUDGET_EXHAUSTED | **只检查 3 条即预算耗尽** → L1/L2 无产出 |
| token_content | 103c517b: checked=1047（全量） | 逐请求检查 |

findings 规则分布（3 个代表任务两页各 100 条上限）：

| 任务 | L4 | L3 | L2 | L1 | L5 | T2-T4 |
| --- | --- | --- | --- | --- | --- | --- |
| 103c517b (DS S000…773) | 97 | 3 | 0 | 0 | 0 | 0 |
| f67facf6 (Qwen S000…773) | 88 | 12 | 0 | 0 | 0 | 0 |
| 85c247db (Qwen meca) | 98 | 2 | 0 | 0 | 0 | 0 |
| ee4a4510 (DS newalliance) difference-groups | 98 | 0 | 0 | 0 | 0 | 0 |

**全部 10 任务 findings 恰好 100 条封顶（max_findings=100），且全部为 L3/L4**；L1/L2/L5/T2/T3/T4 无产出（规则覆盖或预算限制，见 §5.5）。

### 5.4 前端读取链（源码证据）

- `AnalysisApp.tsx`：
  - `bindings` 从 `catalog.items` 去重 `(binding_id, binding)`；`apps` = 去重 appid。
  - `defaultTask = catalog?.defaults.find(binding && direction)` → **catalog.defaults=[] → defaultTask 恒 undefined**。
  - `target = entries.find(task === (route.task || defaultTask))` → 无 task 时 target 为空 → `setLoaded(null)`。
  - 渲染空态：`entries.length ? '当前没有默认完整报告，请选择历史报告。' : '当前暂无…分析报告。'` —— **10 个 partial 任务会出现在"历史报告"下拉（entries 非空），但无默认报告**。
- `model.ts` `loadReport`：读 `report + recommendation-summary`；`readPages` 读 recommendations（kinds=['recommendation']）；`loadDifferenceCards` 读 difference-groups（**L4/L5 卡片由此生成，不依赖 recommendations**）；`BigInt(ids.size) !== BigInt(difference_group_count)` 时抛 `DIFFERENCE_COUNT_MISMATCH`。
- `Reports.tsx` `ReportCards`：`data.summary.availability==='not_computed'` 显示"尚未生成新版建议"；否则按 `['优化建议'(recommendation), '发现的差异'(difference_group)]` 两组渲染；recommendation 空时显示"当前没有达到展示条件的优化建议"，difference_group 有值时显示 L4/L5 卡片。

### 5.5 根因判定（分项）

| 假设 | 判定 | 证据 |
| --- | --- | --- |
| 未选中报告 | **是（主因之一）** | defaults=[]，全部 partial 非 ready；裸入口无默认报告 |
| 结果未发布 | **否** | report_published=true，catalog 可见全部 10 任务 |
| 分组/建议扩展失败 | **是（主因之二）** | configured_recipe_count=0 → recommendations=[]；proposal_coverage reason=TOKEN_FRAGMENT_INCOMPLETE（配方依据缺失，非预算触顶） |
| 身份/协议不匹配 | **否** | 服务端正确身份头下数据可读；前端 DiscoverySession 自动携带 |
| 前端未展示 | **部分** | L4 差异卡片按源码逻辑应显示（difference-groups 97 组），但需先选中历史报告；**页面实际 DOM 未经浏览器确认**（本调查 headless 环境无法运行 JS 提取 DOM 文本，见 §10 证据缺口） |

**关键点（对用户质疑的回应）**：

1. **"S000…773 存在动态字段问题" 成立**：该任务（DS 与 Qwen 两个）均有 97-100 条 L4 findings（difference_pointers 指向 messages content 差异），数据在后端存在。
2. **但页面看不到 L4/L5 卡片的直接原因**：默认入口无报告（partial）+ 用户未在"历史报告"下拉选中任务 + 即便选中，recommendation 区为空（配方 0）；L4 差异卡片区是否渲染依赖选中后 `loadDifferenceCards` 成功遍历全部 group 页（本调查未能在浏览器中确认最终 DOM，标注为待验证）。
3. **partial ≠ 无结果**：findings 与 difference-groups 均已发布可读；partial 表示部分规则/阶段未完整完成（L1/L2 预算耗尽、token 评估配方缺失）。

**影响范围**：10 个任务的异常分析结果在 API 层可读（findings/difference-groups），但前端"异常页"默认无结果、推荐建议为空 → 用户验收不通过。

### 5.6 修复建议（本轮仅建议）

1. **默认策略扩展**：`default_policy=ready_analysis_per_binding_direction_publication_order` 目前只选 ready；对 partial 但 report_published=true 的任务，前端历史报告下拉应已可选（现状可），且可在页面上以"部分完成"徽标提示（AnalysisApp 已有 `shown.entry.status !== 'ready'` 提示逻辑）。
2. **展示已有 findings**：ReportCards 在 recommendation 为空时，仍应渲染 difference-groups 的 L4/L5 卡片（源码已支持，需确认浏览器实际渲染路径）；用户当前看不到可能因未选中报告。
3. **配方/建议生成**：configured_recipe_count=0 是 recommendations 为空的根因（TOKEN_FRAGMENT_INCOMPLETE）；需业务配方/授权依据才能生成"修改后收益"卡片。这与"L1-L3 优化卡完整评估与 >1pp 门槛"保持——不绕过校验。
4. **findings 100 条上限**：max_findings=100 已触顶（L4/L3 各 97-100/2-12）；应区分"展示上限"与"证据保留上限"，如需全量 L4 证据需提高保留上限或分批。
5. **保留 L4/L5 聚合展示**：approved 四入口与 L4/L5 展示不变；L1-L3 优化卡完整评估和严格 >1pp 门槛不改。

---

## 6. 问题C：MA 四项指标缺失

### 6.1 用户反馈

> DeepSeek-V4-Flash 全部 UUID、GLM-V5.2 部分 UUID 缺：理想命中率、真实命中率、整小时重算 Token/s、实际重算 Token。

### 6.2 全 9 规格已发布 UUID 矩阵（只读 API 实测）

9 个 ma_run（model_standard_name → ma_run_id）全部 completed、catalog_revision=1..9。逐 UUID 读取 `/monitoring/ma/runs/{run}/instances/{uuid}`，核心 coverage 与命中率：

**DeepSeek-V4-Flash（12 UUID，全部 R=0 / Q=0 / E>0，ideal_status=available）**：

| UUID(前8) | A | P | R | E | Q | ideal.hit_rate | real.sample | paired_real | paired_ideal | hour.real | hour.uncached |
|-----------|---|---|---|---|---|----------------|-------------|-------------|--------------|-----------|---------------|
| DS-32K 0a5bf216 | 740 | 730 | **0** | 345 | **0** | 0.3597 | 0 | 0 | 0 | 0 | None |
| DS-32K 14824d2a | 1060 | 1048 | **0** | 472 | **0** | 0.4472 | 0 | 0 | 0 | 0 | None |
| DS-32K 1677413e | 755 | 754 | **0** | 319 | **0** | 0.4428 | 0 | 0 | 0 | 0 | None |
| DS-32K bb80f80b | 273 | 271 | **0** | 124 | **0** | 0.4652 | 0 | 0 | 0 | 0 | None |
| DS-32K cc41fe37 | 824 | 817 | **0** | 376 | **0** | 0.4676 | 0 | 0 | 0 | 0 | None |
| DS-64K 6714c0cf | 679 | 674 | **0** | 277 | **0** | 0.5884 | 0 | 0 | 0 | 0 | None |
| DS-64K a656cbd5 | 638 | 633 | **0** | 257 | **0** | 0.5202 | 0 | 0 | 0 | 0 | None |
| DS-128K 32fa8b5c | 272 | 272 | **0** | 206 | **0** | 0.5652 | 0 | 0 | 0 | 0 | None |
| DS-128K 3d2cf678 | 555 | 552 | **0** | 391 | **0** | 0.5645 | 0 | 0 | 0 | 0 | None |
| DS-128K 5c1ca7e8 | 236 | 235 | **0** | 175 | **0** | 0.4513 | 0 | 0 | 0 | 0 | None |
| DS-128K a39a1729 | 523 | 521 | **0** | 348 | **0** | 0.5765 | 0 | 0 | 0 | 0 | None |
| DS-128K f7717738 | 607 | 604 | **0** | 415 | **0** | 0.5384 | 0 | 0 | 0 | 0 | None |

（A=assigned, P=production_input, R=real, E=encoded, Q=paired；hour.uncached=uncached_tokens，None 表示无有效 real 样本。）

**GLM-V5.2（27 UUID；32K 全正常；64K/128K 部分 UUID ideal 缺失）**：

| UUID(前8) | A | P | R | E | Q | ideal_status | ideal.hit_rate | real.sample | paired_real/ideal | hour.real | hour.uncached |
|-----------|---|---|---|---|---|--------------|----------------|-------------|-------------------|-----------|---------------|
| GLM-32K 69ea9f6e | 885 | 884 | 884 | 517 | 517 | available | 0.6473 | 884 | 517/517 | 884 | 5,839,934 |
| GLM-32K 44cee964 | 848 | 847 | 847 | 456 | 456 | available | 0.6314 | 847 | 456/456 | 847 | 6,626,980 |
| GLM-32K 58e9f7df | 852 | 850 | 850 | 447 | 447 | available | 0.6123 | 850 | 447/447 | 850 | 6,045,399 |
| GLM-32K 1c4fe41c | 800 | 797 | 797 | 470 | 470 | available | 0.6429 | 797 | 470/470 | 797 | 5,969,421 |
| GLM-32K 80ba8c29 | 847 | 844 | 844 | 488 | 488 | available | 0.5882 | 844 | 488/488 | 844 | 6,488,298 |
| GLM-32K cbaccd36 | 872 | 869 | 869 | 501 | 501 | available | 0.6475 | 869 | 501/501 | 869 | 6,218,434 |
| GLM-64K 13fe5d25 | 435 | 435 | 435 | 170 | 170 | available | 0.5480 | 435 | 170/170 | 435 | 11,461,009 |
| GLM-64K a2e15499 | 410 | 410 | 410 | 176 | 176 | available | 0.5704 | 410 | 176/176 | 410 | 11,459,789 |
| GLM-64K 2d3e3a3e | 479 | 479 | 479 | **0** | **0** | **warmup_order_conflict** | **None** | 479 | 0/0 | 479 | 11,982,924 |
| GLM-64K 6db2095f | 461 | 461 | 461 | **0** | **0** | warmup_order_conflict | **None** | 461 | 0/0 | 461 | 11,250,885 |
| GLM-64K aa5f0680 | 461 | 460 | 460 | **0** | **0** | warmup_order_conflict | **None** | 460 | 0/0 | 460 | 11,676,196 |
| GLM-64K b6024444 | 410 | 409 | 409 | **0** | **0** | warmup_order_conflict | **None** | 409 | 0/0 | 409 | 11,336,668 |
| GLM-64K da0dcd8b | 440 | 439 | 439 | **0** | **0** | warmup_order_conflict | **None** | 439 | 0/0 | 439 | 11,121,403 |
| GLM-64K e2c55516 | 475 | 475 | 475 | **0** | **0** | warmup_order_conflict | **None** | 475 | 0/0 | 475 | 11,496,060 |
| GLM-64K eb1865a4 | 424 | 423 | 423 | **0** | **0** | warmup_order_conflict | **None** | 423 | 0/0 | 423 | 11,323,141 |
| GLM-128K 123177f0 | 301 | 284 | 284 | **0** | **0** | warmup_order_conflict | **None** | 284 | 0/0 | 284 | 9,311,984 |
| GLM-128K 210d6741 | 308 | 280 | 280 | **0** | **0** | warmup_order_conflict | **None** | 280 | 0/0 | 280 | 9,480,687 |
| GLM-128K 450430ad | 245 | 232 | 232 | **0** | **0** | warmup_order_conflict | **None** | 232 | 0/0 | 232 | 8,666,892 |
| GLM-128K 76712c1a | 310 | 288 | 288 | **0** | **0** | warmup_order_conflict | **None** | 288 | 0/0 | 288 | 9,982,534 |
| GLM-128K 7b43a341 | 322 | 304 | 304 | **0** | **0** | warmup_order_conflict | **None** | 304 | 0/0 | 304 | 9,235,286 |
| GLM-128K b694602f | 2 | 0 | 0 | 0 | 0 | (A=2/P=0) | None | 0 | 0/0 | 0 | None |
| GLM-128K 16b2e0ff | 307 | 292 | 292 | 216 | 201 | available | 0.6493 | 292 | 201/201 | 292 | 9,949,473 |
| GLM-128K 5676dbfc | 300 | 286 | 286 | 229 | 215 | available | 0.6369 | 286 | 215/215 | 286 | 10,619,326 |
| GLM-128K 7d46ffc2 | 345 | 317 | 317 | 245 | 217 | available | 0.7341 | 317 | 217/217 | 317 | 9,881,410 |
| GLM-128K b4e376d1 | 301 | 282 | 282 | 221 | 202 | available | 0.7049 | 282 | 202/202 | 282 | 8,788,776 |
| GLM-128K b7b2a8c3 | 299 | 278 | 278 | 207 | 186 | available | 0.6749 | 278 | 186/186 | 278 | 9,742,107 |

（GLM-128K 另有 7d46ffc2 等 available 与 123177f0 等 conflict 各半；b694602f 仅 2 条 assigned、P=0 —— 空范围特例。）

**Qwen-V3.6-27B（48 UUID，全部正常）**：32K 26 个（real_sample≈4200-4800、hour_unc≈17-19M）、64K 9 个（real≈2300-2600、hour_unc≈81-91M）、128K 13 个（real≈400-1080、hour_unc≈27-69M）——全部 ideal_status=available、real/ideal/paired 全有值。完整逐 UUID 见 artifacts/research/ma_uuid_qwen.txt（48 行，含 UUID 前8、A/P/R/E/Q、ideal_rate、real/paired sample、hour.real/uncached）。

### 6.3 缺失原因（源码+数据双层定位）

**缺失模式 A：DeepSeek 全部 UUID 的 real/paired/小时重算缺** —— **cached_tokens 列 100% 空串**。

18 文件 cached_tokens 列逐行核对（独立脚本，`intval` 精确判定）：

| 文件 | 行数 | cached 整数行 | cached 零 | cached 正 | EMPTY |
|------|------|--------------|-----------|-----------|-------|
| DeepSeek-V4-Flash-32K-pre.csv | 3,501 | **0** | 0 | 0 | **3,501 (100%)** |
| DeepSeek-V4-Flash-32K-now.csv | 3,951 | **0** | 0 | 0 | **3,951 (100%)** |
| DeepSeek-V4-Flash-64K-pre/now | 1,691/1,388 | 0 | 0 | 0 | 100% |
| DeepSeek-V4-Flash-128K-pre/now | 2,874/2,958 | 0 | 0 | 0 | 100% |
| GLM-V5.2-32K-pre.csv | 5,377 | 5,119 | 368 | 4,751 | 258 |
| GLM-V5.2-32K-now.csv | 5,440 | 5,091 | 456 | 4,635 | 349 |
| GLM-V5.2-64K-pre/now | 4,393/4,334 | 4,056/3,991 | 151/128 | 3,905/3,863 | 337/343 |
| GLM-V5.2-128K-pre/now | 3,513/3,448 | 2,903/2,843 | 100/83 | 2,803/2,760 | 610/605 |
| Qwen-32K-pre/now | 110,292/114,838 | 110,050/114,637 | 64,763/59,077 | 45,287/55,560 | 242/201 |
| Qwen-64K-pre/now | 21,119/21,746 | 21,110/21,744 | 7,740/7,947 | 13,370/13,797 | 9/2 |
| Qwen-128K-pre/now | 12,424/11,492 | 12,317/11,357 | 5,308/5,182 | 7,009/6,175 | 107/135 |

**DS 的 cached_tokens 全部为空串**；GLM/Qwen 非空行全部为合法整数（无负数、无溢出、无字面 NULL、无 cached>prompt 的 CACHE_EXCEEDS_INPUT——该检查在 ingest 触发时会将 cached 置 None 并记 issue，本轮 18 文件未发现）。quality 报告证实：DS-32K quality total=13,103（pre+now 两文件全部字段问题），首行即 `field=cached_tokens, code=MISSING_TOKEN_VALUE`。

**产品处理链**（`ingest.py:123-128`）：`tokens[field] = token_cell(values.get(field, ""))`，空串 → ValueError → cached=None → `records.cached_tokens=NULL`。`statistics.py:128`：`r = p is not None and h is not None`（p=prompt_tokens, h=cached_tokens）→ h 恒 None → `counts["r"]=0` → `real.sample_count=0`、`paired=0`、`hour.real_count=0`、`uncached_tokens=None`。**前端 MAMonitor.tsx** 在 `real.sample_count==='0'` 时显示 "—"，Trend 的 `uncached_tokens_per_second=null` 显示 "—"。

**结论**：DS MA CSV 源数据缺 cached_tokens 观测 → 产品按 MISSING_TOKEN_VALUE 拒绝该字段 → real 统计无有效样本。**"无实测命中观测"在 DS 上属实，但对 GLM/Qwen 不成立**（旧报告该说法需勘误为"DS 缺 cached 观测"）。

**缺失模式 B：GLM 部分 UUID 的理想命中率缺** —— `warmup_order_conflict`。

`replay.py:100-109`：
```python
conflict = bounds[0] is not None and bounds[1] is not None and bounds[0] > bounds[1]
status = ("warmup_order_conflict" if conflict
          else "empty_now" if not now_count
          else "no_valid_prewarm" if not bounds[2]
          else "available")
db.execute("INSERT INTO scopes VALUES (?,?)", (uuid, status))
if conflict:
    continue   # 跳过该 UUID 的 ideal 回放
```
`bounds[0]` = 该 UUID 的 **pre 最后一条 handle_ns**，`bounds[1]` = **now 第一条 handle_ns**。GLM-64K/128K 部分 UUID 因 pre 末尾请求的 model_handle_start_time 晚于 now 首条 → 冲突 → 该 UUID 不执行理想回放 → `encoded=0`、`ideal.sample_count=0`、`ideal.hit_rate=None` → **理想命中率缺失**；但 real（依赖 now 的 cached 值）正常。GLM-32K 全部无冲突 → 正常。

（注：DS 全部 UUID ideal_status=available 且 E>0，即 DS 的 ideal 回放正常；DS 缺的是 real 而非 ideal。）

**"GLM 部分 UUID 缺"的精确范围**：GLM-64K 9 个 UUID 中 7 个 conflict（仅 13fe5d25/a2e15499 available）；GLM-128K 11 个中 5 个 conflict（仅 16b2e0ff/5676dbfc/7d46ffc2/b4e376d1/b7b2a8c3 available）+ 1 个 b694602f 空范围（A=2/P=0）。

### 6.4 前端四项展示与数据对应（源码证据）

`MAMonitor.tsx:192` 表格列：
- "配对命中率"（理想/真实）→ `i.paired_ideal.hit_rate` / `i.paired_real.hit_rate`（DS 全 null → "—" 显示 `percent(null)`；GLM conflict 的理想 null）
- "整小时重算Token/s" → `i.hour.uncached_tokens_per_second`（DS 全 null → "—"）
- "实际重算Token" → `i.real.totals.uncached_tokens`，`real.sample_count==='0'` 时显示 "—"
- 展开详情 `MACharts.tsx`：Trend 用 `hour.uncached_tokens_per_second` 与 12 桶 `bins[].pressure.uncached_tokens_per_second`（DS 桶全 null，页面显示"缺失"断点）；Distribution 用 `uncached_histograms`（依赖 cached）；"独立真实命中率" `real.hit_rate`、"独立理想命中率" `ideal.hit_rate`。

**12 桶守恒核对**：GLM-32K 69ea9f6e 的 12 桶 uncached_tokens 之和 = 5,839,934 = hour.uncached_tokens（statistics.py 的 `hour.uncached_tokens` 由桶求和计算，contracts.py:255-257 校验相等）。DS 桶全 null（无 real 样本），合法缺失（真空桶为 0，非有效观测缺失；DS 是**有请求但无有效 cached 字段** → 桶应缺失而非补 0 —— 产品行为正确）。

### 6.5 修复建议（本轮仅建议）

1. **数据层（DS 源 CSV）**：DeepSeek MA CSV 的 `cached_tokens` 列为空是**源数据问题**（真实流量网关未采集命中 token 数）。后续需上游补齐观测，或明确业务上"DeepSeek 无命中观测可报告"；**不得用模拟值填实测、不得用独立理想填配对指标、不得用 null 填 0**。
2. **产品层（可选健壮性）**：
   - `ingest.py` 对 cached_tokens 空列可在 quality 报告明确归类（现 MISSING_TOKEN_VALUE 已正确记录）；如需区分"源字段缺失"与"合法零命中"，可在 quality code 上细分（不属本轮范围）。
   - `replay.py` 的 `warmup_order_conflict` 目前 `continue` 跳过整个 UUID；建议将冲突范围收窄为"仅跳过受影响的 pre 尾部请求"而非整 UUID，或在 scopes 状态中保留部分回放（需用户/业务确认是否接受部分 ideal）。
   - `MAMonitor.tsx` 在 real.sample_count=0 时显示 "—" 且无解释；建议补充"无有效命中观测（cached_tokens 缺失）"图例，区分"空桶=0"与"无观测=缺失"（符合"有请求但无有效真实字段的桶应缺失"原则）。
3. **不做**：不把 GLM 的可用命中率外推给 DS；不改变 paired/独立指标定义；不混用模型规格。

---

## 7. tools/messages 工作负载研究（预算内分层抽样）

### 7.1 方法与预算

- 范围：仅用户指定的 10 个 appid（DS 5 + Qwen 5）；其他 appid 仅做量级清点（§3.5 全文件 appid 分布）。
- 方法：全量解析 10 appid 的 request_input（§3.5 结构表）；随后对每 appid 固定种子 `random.Random(20261103)` 分层抽样 ≤120 行，深度提取工具定义/消息/重复/ID 字段（`tools_messages_sample.jsonl` 676 行）。
- 预算登记：解析样本 676 行 + 全量结构 10 appid；RSS<1GiB；墙钟 ~5min；输出上限 676 行 JSONL。
- 留出验证：未人工标注不编准确率；未全量检查不编全量覆盖率；未获业务确认的样例标为**候选**。

### 7.2 工作负载结论（按 appid 族）

| appid | 族特征 | 每请求消息(中位) | 工具定义 | 工具Schema字节(中位) | 重复内容候选 | 最深 |
|-------|--------|-----------------|---------|----------------------|--------------|------|
| DS S000…773 | **agentic coding**（edit/glob/grep/read/skill/write 275 工具名） | 38 | 有 | 51,302 | 77/120 行 | 13 |
| DS S010320 | **agentic coding**（edit/read/write/bash/glob/grep 150 工具名） | 90 | 有 | 51,173 | 100/120 行(中位3) | 13 |
| DS ipd.tianzhou.ai | **agentic 文件/任务工具**（glob/grep/task/ls/read_file/write_file 224 工具名） | 6 | 有 | **90,751** | 6/120 | **19** |
| DS mbs.ilegal.ioc | agentic coding（edit/glob/grep/read/skill/write 153 工具名） | 23 | 有 | 41,406 | 43/120 | 13 |
| DS newalliance | agentic（memory/agent_profile/bash/edit 91 工具名） | 89 | 有 | 51,123 | 72/109 | 13 |
| Qwen app_000000030502 | **纯对话**（0 工具） | **2** | 无 | — | 0 | 3 |
| Qwen aidp_dg06 | 混合（167 工具名） | — | 有 | — | — | 13 |
| Qwen meca.admin.digital | 混合（51 工具名） | — | 有 | — | — | 13 |
| Qwen S000…773（大） | **低 tool 密度**（14611 请求含 tools 但 tool_calls 仅 15） | — | 有(部分) | — | — | 10 |
| Qwen S000…1679（大） | 低 tool 密度（119 工具名、tool_calls 2787） | — | 有 | — | — | 13 |

**核心结论**：
1. **"Qwen/DeepSeek 不是典型 agentic infra" 假设部分证伪**：DeepSeek 指定 5 appid 全部为高度 agentic（tool_calls 密度 27-51/请求、消息中位 38-90）；Qwen 的 app_000000030502 是纯对话对照，但 Qwen aidp_dg06/meca.admin.digital 也带工具。**模型品牌不决定工作负载，appid 模板族决定**。
2. **工具定义/Schema 负担显著**：DS 工具型 appid 每请求携带 41-90KB 工具定义（S010320 与 S000…773 每请求 ~51KB，ipd.tianzhou.ai 中位 90KB）。这是 L3 探测器（工具定义比较）的实际作用面；也意味着输入预算大部分被工具定义占用。
3. **同一请求内重复内容候选存在**：S010320 100/120 行、S000…773 77/120 行有 ≥2 处 sha256 相同 content（中位 2-3 处/行，max 10-15）——这些是 T3/T4 类探测器的候选输入，但**未经业务确认，不能直接当可节省 Token**（字节/LCP 差异不直接等价 Token 收益）。
4. **无可靠会话关联**：S000…773 的 97 条 L4 findings 均为 `needs_association`（无会话改写证据）——不宣称历史被改写/重试/agent loop。

### 7.3 候选探测器（研究建议，非实现）

| 候选 | 真实最小疑似正例 | 近似合法负例 | 现规则输出/未覆盖 | 适用分母 | 成本 | 误报风险 | 验证办法 |
|------|------------------|---------------|-------------------|----------|------|----------|----------|
| C1 工具定义变体 | ipd.tianzhou.ai 90KB Schema 中同名工具（如 read_file/write_file）在不同请求 parameters 微差（样例见 JSONL） | 合法版本差异（权限/租户/规格变化） | L3 检出（findings 12/任务） | 工具型 appid 全量请求 | 每请求工具 Schema 已解析 | 将合法版本差异当浪费 | 按业务确认变体是否必须 |
| C2 消息模板混杂 | S010320 中 100/120 行重复 content（固定前缀+变量） | 正常引用/few-shot/必要历史 | T3 重复组要求 ≥1 tool_result；L1 范围有限 | 该 appid 全量 | 低（sha 比对） | 删除必要历史 | 会话关联 + 业务保留约定 |
| C3 普通消息内 JSON/检索片段 | Qwen S000…773 用户消息含 JSON（非 tool 协议） | 正常业务参数 | 无对应探测器（不自动当 tool 返回） | 大 appid 全量 | 低 | 结构误判 | 仅作结构统计，不做收益结论 |
| C4 动态 ID | 各 appid 消息/请求字段（本采样 id_fields 罕见，见下） | 业务必需字段 | L1 前部动态内容 | — | 低 | 泛化删 ID | 业务确认 |
| C5 JSON 转义/嵌套序列化 | DS 行 request_input 内嵌套 JSON 字符串（如 request_input 字段含 "input_abort"） | 语义等价 | 现读取器按源 JSON 计量 | — | 低 | 语义等价无收益 | 与模板等价性对照 |

**补充事实**：
- id_fields 在本批采样中**罕见**（top 无结果）——"动态 ID"不是本批数据的主要浪费候选（L1 探测器无产出与之一致）。
- S010320 的 messages 中位 90 条、tool_results 53,627/1,067 行——**长工具链会话**典型；这类负载下重复携带（T4 历史工具结果）是比"前部动态内容"更可能的优化面。
- 现探测器覆盖缺口：L1（前部动态内容）因 FINDING_BUDGET_EXHAUSTED 只查 3 条；L2 工具排列本批无产出；L5 JSON 写法差异本批无产出。**"适配缺口/召回粒度/预算截断"比"增加探测器"更优先**（§5.6 建议 3、§7.4）。

### 7.4 优先级建议（仅研究建议）

1. **P0：低命中扫描预算**——L1/L2 因 FINDING_BUDGET_EXHAUSTED 只查 3 条即停（§5.3），先解决候选/比较预算或分批策略，再谈探测器扩展。
2. **P1：工具定义负担量化**——DS 工具型 appid 每请求 41-90KB Schema，先确认跨请求工具定义**实际差异率**（C1 候选），若有稳定复用前缀则输入预算大头可被前缀缓存覆盖（这属于缓存口径问题，非删除工具）。
3. **P2：重复内容候选**——T3/T4 类重复内容候选需会话关联与业务保留约定后才能评估；不做收益实验。
4. **不做**：不实现新探测器、不改 recipe、不删改消息/工具内容、不做改写后收益实验、不新增 L/T 编号；字节/LCP/消息差异不能直接当可节省 Token。

---

## 8. 用户验收状态与勘误

### 8.1 用户验收状态

- **第一次用户验收（2026-11-02）**：不通过（用户原话："用户监控验收不通过…URL 只显示 Qwen…"）——本轮问题A 调查证实为前端入口缺失（§4）。
- **第二次用户验收（2026-11-03）**：**不通过**。用户明确"后台已完成，异常页没有结果"（问题B，§5）与"MA 四项指标缺失"（问题C，§6）。**不能以任务完成或 HTTP 200 代替用户认可**。

### 8.2 旧报告勘误（本报告范围内）

| 旧报告表述 | 勘误 |
|-----------|------|
| "无实测命中观测"（MA） | 仅对 **DeepSeek** 成立（cached_tokens 列 100% 空）；**GLM/Qwen 有实测命中观测**（GLM-32K-pre 5119 行 int、Qwen-32K-pre 110050 行 int） |
| "150,698 有效 / 203,940 跳过" | 独立审计 151,320/203,318（口径差异：旧为索引后行数，本次为原始 CSV 严格有效性，§3.3） |
| "S000…773=1047 条" | 原始有效 1048 条（1 条越界被 scope 排除，§3.4） |
| "大 appid 30-40 分钟完成" | 无任务内计时；terminal_at 间隔 22m57s（S000…1679）与旧报告接近，S000…773 间隔含调度间隙（§3.7）；**未证实亦未否定** |
| "两方向完成" | 10 任务全部 **partial**（非 ready）；token_content 全量 checked 但 findings 100 条封顶全为 L3/L4（§5.3） |

### 8.3 未决事项

- P90 TTFT：仍需用户提供 T/W/K/τ 参数（旧报告未填示例值，本轮未改）。
- UIR-03：用户决定留 V3，**不纳入本次修复建议范围**（本报告所有修复建议均保持四入口与 L4/L5 展示）。

---

## 9. 后续建议归口与证据缺口

### 9.1 按归口

| 归口 | 建议 | 待用户决定 |
|------|------|-----------|
| 前端 | 问题A：UserMonitor 增加模型/run 切换 + localStorage 多槽展示（§4.5）；问题B：历史报告下拉中 partial 状态展示优化 + L4/L5 卡片渲染确认（§5.6）；问题C：无观测与空桶区分图例（§6.5） | 是否接受前端改动范围 |
| 用户监控 | P90 TTFT 参数（T/W/K/τ）；问题A 入口恢复 | 提供 TTFT 参数 |
| MA | DS cached_tokens 数据补齐（上游）；GLM warmup_order_conflict 部分回放策略（§6.5） | 数据补齐与产品行为取舍 |
| 公共分析 | 低命中扫描预算（FINDING_BUDGET_EXHAUSTED）；L4 证据保留上限与 100 条 findings 封顶 | 预算调整 |
| 低命中 | L1/L2 预算不足先于探测器扩展（§7.4 P0） | — |
| Token 后端 | 配方/依据缺失导致 recommendations=0（TOKEN_FRAGMENT_INCOMPLETE）；工具定义负担与 T4 历史结果重复候选（§7.4 P1/P2） | 业务配方与保留约定 |

### 9.2 本轮新增研究文件（artifacts/research/）

| 文件 | 关键逻辑 |
|------|---------|
| scan_csv_sha.py | 21 文件流式 SHA256/记录数/时间范围/appid/uuid 分布（csv.field_size_limit 1<<30） |
| csv_21_scan.json | 21 文件清单结果 |
| audit_trace_validity.py | Trace 3 文件严格有效性主因分类（BAD_JSON/NO_MODEL_FIELD/EMPTY_JSON/VALID） |
| audit_trace_validity.json | 逐模型×appid 有效/跳过/主因桶 |
| body_quantiles_and_struct.py | raw_body 字节 log2 桶分位数 + 10 appid 全量解析结构 |
| body_quantiles.json / structure_probe.jsonl | 分位数与结构结果 |
| audit_ma_tokens.py / audit_ma_tokens.json | 18 MA 文件 prompt/cached/completion 原值分类 |
| ma_cached_recheck.txt | cached_tokens 列精确核对（DS 全空 / GLM/Qwen 有值） |
| tools_messages_probe.py / tools_messages_sample.jsonl | 10 appid 分层抽样 676 行：工具名/Schema 字节/重复候选/深度 |
| catalog_diagnostics.json | 诊断 discovery catalog 13 条原始 |
| diag_task/ | 10 任务 report + recommendation-summary 原始 JSON |
| ma_uuid_ds_glm.txt（38行） | DS 12 + GLM 27 UUID 矩阵（A/P/R/E/Q/ideal_status/hit_rate/hour） |
| ma_uuid_qwen.txt（48行） | Qwen 48 UUID 矩阵（同上） |

**脚本均为只读**：只读打开原 CSV；不实例化产品 Store；不写业务库。运行中日志/WAL 自然变化（dispatcher.cursor 等）属服务自身运行，非本轮写入。

### 9.3 证据缺口

1. **浏览器 DOM 未直接取证**：本环境 firefox 115.12.0esr headless 可截图但无法提取 JS 渲染后 DOM 文本；问题B 的"页面最终是否显示 L4/L5 卡片"未在真实浏览器确认（源码逻辑支持，标注待验证）。**证据缺口**：需在用户侧或可运行 JS 的浏览器复核 #/analysis 历史报告选中后的实际 DOM。
2. **任务内分阶段计时**：无（仅 terminal_at 间隔）。
3. **单请求 >1MiB 分布**：未单独全量统计（P99≈393KB 但 max 1.18MB）。
4. **MA 完整 12 桶逐 UUID**：代表性 UUID 已验证守恒；其余 UUID 的桶求和未逐条核对（可用同一 SQL 复核）。
5. **MA 逐 UUID 的 GLM warmup 冲突明细**（哪些 pre 尾条 > now 首条）：未逐 UUID 读取原始时间戳（可从 pre/now CSV 按 UUID 取 handle 时间复核）。

### 9.4 未修改核对（产品面）

- 产品源码：4 个关键文件 SHA 与代码包一致（§1.4）；本轮未修改任何源码。
- 配置/契约/recipe：未修改（本轮未写）。
- 原 CSV 21 文件：SHA 与扫描结果一致（§3），未修改（脚本只读）。
- 已发布结果（catalog/runs/MA/诊断任务）：仅 GET 读取；未重算/未改状态。
- 未实施产品修复，暂无修复后结果。

---

## 10. 自检

| 检查项 | 结果 |
|--------|------|
| 报告为唯一交付文件 | ✅（docs/huawei/HUAWEI_V2_INVESTIGATION_REPORT_20261103.md） |
| 关键源码片段带文件/函数/行号 | ✅（ingest.py:123-128、statistics.py:128、replay.py:100-109、UserMonitor.tsx、AnalysisApp.tsx、MAMonitor.tsx:192、MACharts.tsx、catalog.ts） |
| 命令/退出码/HTTP响应嵌入 | ✅（curl 输出、docker inspect、python 脚本 stdout） |
| 表格分母定义 | ✅（§3.3 分母=原始记录数；§6.2 A/P/R/E/Q 定义；§3.5 分母=解析 OK 数） |
| 必要身份/状态/精确数值 | ✅（service_instance_id、header 类型、hit_rate 原值） |
| 未实施修复声明 | ✅（§0、§9.4） |
| 脱敏 | ✅（无凭据；敏感内容用 appid 代号，未嵌入完整请求正文） |
| 页面证据 | ⚠️ 无 DOM 截图（headless 限制，§9.3 缺口1；API/源码证据充分） |

**结论：本调查为只读调查，未实施产品修复，暂无修复后结果。三问题均已定位到根因或给出待验证假设，修复建议待开发机审查 session 复核后由用户决策。**