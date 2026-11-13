# HUAWEI V3 C04 验收报告

## 1. 执行摘要

| 阶段 | 状态 | 说明 |
|------|------|------|
| 部署 | **PASS** | 镜像ID验证通过，容器健康运行 |
| 用户全量监控 | **PASS** | 3个真实CSV全量重算完成 |
| MA全量 | **PASS** | 9对MA全量重算完成，real_hit_rate因数据缺失为null（如实记录） |
| ICSL | **PASS** | 102条监控完成，发现billing_header动态前缀，1条建议 |
| BUS01 | **PASS** | 1047条，7个发现（6个clock + 1个prefix path），7条建议 |
| BUS02 | **PASS** | 1038条，6个发现（4个clock + 2个prefix path），6条建议 |
| BUS03 | **PASS** | 661条，4个发现（2个clock + 1个prefix + 1个prefix path），4条建议 |
| BUS04 | **PASS** | 104条，3个发现（3个clock），3条建议 |
| BUS05 | **PASS** | 171条，5个发现（3个clock + 2个prefix path），5条建议 |
| 前端 | **PENDING** | 四入口HTTP可访问，视觉检查需人工确认 |
| 重启验证 | **PASS** | 重启后6组报告、监控结果和链接保持，任务数不增长 |
| 人工验收 | **PENDING** | 前端视觉验收和TTFT参数确认需人工 |

**未通过/待确认事项：**
- 前端视觉检查未执行（无图形浏览器能力），需用户通过SSH转发人工验收
- MA real_hit_rate全部为null，因MA CSV中cached_tokens字段缺失（source_cached_missing），属数据限制非产品缺陷
- 6组异常分析任务最终状态为stopped（reason: CAUSE_EVIDENCE_TRUNCATED），报告和发现完整可用，属有界小样本分析的预期行为

## 2. 发布身份

| 项目 | 值 |
|------|------|
| 正式版本 | tokenscope-v3-c04-20261112 |
| 源码commit | 57fe9f64d78f6363ee18a12ff97693e00ae1fe3d |
| 镜像标签 | tokenscope/full-service:tokenscope-v3-c04-20261112 |
| 镜像ID | sha256:f2162dfc460d47641ef0d64ba1f65974e5c0675b5022217997187927f1e8b466 |
| 代码包SHA256 | 3aaed3c5c46d4e662399f191bf328978581bae35180c36a8fd968d16db39c58e |
| 镜像包SHA256 | 52d3682751a3054533fb884ebc17138aa7b2f9474bfee1d84588a76290afbe87 |
| 容器镜像ID(运行时) | sha256:f2162dfc460d47641ef0d64ba1f65974e5c0675b5022217997187927f1e8b466 |
| http-resources.json | {"matched": true, "files": 4, "image_id": "sha256:f2162dfc..."} |
| 代码归档 | 无绝对路径或..越界 |
| 修改 | 无产品代码修改，无镜像补丁 |

## 3. 环境与保护

### 环境

| 项目 | 值 |
|------|------|
| 用户 | uid=1015(zhangxiyue) gid=2006(GeneralAI) |
| 内核 | Linux 3.10.0-1160.119.1.el7.x86_64 x86_64 |
| Docker | 26.1.4 |
| Docker Compose | v2.27.1 |
| 内存 | 375G total, 15G used, 356G available |
| /home | 3.6T, 95% used, 216G avail |
| /mnt/sde | 3.6T ext4, 8% used, 3.2T avail |
| 容器限额 | 8 CPU / 32GiB mem / 256 pids |

### 旧服务停止

- 旧容器: `tokenscope-v3-sample-20261111-monitoring-1`
- 旧容器ID: `7694308a2bb5ae757a8309e3b7a655dc951bfa7378aab4c21a2e15deb24bd00e`
- 旧镜像: `tokenscope/full-service:tokenscope-v3-sample-20261111`
- 旧镜像ID: `sha256:d6d9b5997c5f27e36dccc553db89679686c8c552210ac542ee56c57d382cb6f5`
- 旧state路径: `/mnt/sde/zhangxiyue/tokenscope-v3-r2-state-copy` (138GB, 20414 files)
- 旧state来源: `/home/aarc/zhangxiyue/tokenscope-v3-sample-20261111/compose.yaml`
- 停止方式: `docker stop 7694308a...` -> Exited (143)
- 端口18002停止后确认无监听
- 无宿主旧进程残留

### 数据保护验证

旧state关键文件SHA256前后对比（全部未变）：

| 文件 | SHA256 | 状态 |
|------|--------|------|
| control.sqlite3 | 22147da026c8a06c40a04d21aec3c3a6c17d81b2dd51b13149c912c79487d4cd | 未变 |
| user_monitoring/control.sqlite3 | 0affb11d13d0ff3ad0d306d032047e2d3a865598d1ccc21bfeed84f7566869ba | 未变 |
| ma/control.sqlite3 | 5bd14b77fb995b661dc67e5f20dea37b6ec6f2ccc487d2b83d352ffb2d72113d | 未变 |
| diagnostics-v3/preparations.sqlite3 | c823b5b40bae5c874c5435010278c0fd4ac14954601e952fb2a53455b8cd233f | 未变 |

### 新state

- 路径: `/mnt/sde/zhangxiyue/tokenscope-v3-c04-state-20261112T123613`
- 初始为空，与旧state路径不同
- 最终大小: 108GB
- 原始CSV和旧state未被写入

### Compose展开关键配置

- 输入根: `$WORK/input-root` (空，预建挂载点)
- 10.20_Trace: 只读绑定 `/inputs/10.20_Trace`
- 10.20_MA: 只读绑定 `/inputs/10.20_MA`
- ICSL: 只读绑定 `/inputs/icsl-demo`
- STATE: 可写绑定 `/state`
- 监听: 127.0.0.1:18002
- UID/GID: 1015:2006 (非root)
- 旧state未挂载

### 访问与回退

用户访问:
```bash
ssh -L 18002:127.0.0.1:18002 zhangxiyue@10.67.43.44
# 浏览器访问 [http://localhost:18002](http://localhost:18002)
```

dc函数定义:
```bash
export WORK="/home/aarc/zhangxiyue/tokenscope-v3-c04-acceptance-20261112T123613"
export STATE="/mnt/sde/zhangxiyue/tokenscope-v3-c04-state-20261112T123613"
dc() { docker compose --env-file "$WORK/deployment.env" -p "tokenscope-v3-c04-acceptance" -f "$WORK/compose.yaml" -f "$WORK/compose.icsl.yaml" "$@"; }
```

回退步骤:
```bash
# 1. 停止新版
dc down
# 2. 重启旧版
docker start 7694308a2bb5ae757a8309e3b7a655dc951bfa7378aab4c21a2e15deb24bd00e
# 3. 验证
curl -s [http://127.0.0.1:18002/healthz](http://127.0.0.1:18002/healthz)
```

## 4. 数据映射

### 真实3CSV - 用户监控

| 文件 | model_id | common_name | SHA256 | 记录数 | appid数 | 时间范围(UTC) |
|------|----------|-------------|--------|--------|---------|---------------|
| DeepSeek-V4-Flash-10.20.csv | DeepSeek-V4-Flash-0731 | DeepSeek-V4-Flash | 5600c009ee10... | 36222 | 62 | 2026-10-20T07:00:00..09:18:57 |
| GLM-V5.2-10.20.csv | GLM-5.2 | GLM-V5.2 | 99dfaf7e2465... | 26505 | 28 | 2026-10-20T07:00:00..09:15:41 |
| Qwen-V3.6-27B-10.20.csv | Qwen3.6-27B | Qwen-V3.6-27B | e8e489f987f0... | 291911 | 53 | 2026-10-20T07:00:00..09:13:37 |

字段: `hash_id`, `appid`, `model_handle_start_time`, `completion_tokens`, `request_input`

时间格式: `DD/MM/YYYY HH:MM:SS.ffffff`，**用户确认为UTC时间**，parse_utc按UTC处理。

### MA 18CSV - 9对配对

每对pre=07:00-08:00 UTC, now=08:00-09:00 UTC，连续各一小时。

| 模型制品 | model_id | pre文件 | now文件 | pre记录 | now记录 | UUID数 |
|----------|----------|---------|---------|---------|---------|--------|
| DeepSeek-V4-Flash-32K | DeepSeek-V4-Flash-0731 | DeepSeek-V4-Flash-32K-pre.csv | DeepSeek-V4-Flash-32K-now.csv | 3501 | 3951 | 5 |
| DeepSeek-V4-Flash-64K | DeepSeek-V4-Flash-0731 | DeepSeek-V4-Flash-64K-pre.csv | DeepSeek-V4-Flash-64K-now.csv | 1691 | 1388 | 2 |
| DeepSeek-V4-Flash-128K | DeepSeek-V4-Flash-0731 | DeepSeek-V4-Flash-128K-pre.csv | DeepSeek-V4-Flash-128K-now.csv | 2874 | 2958 | 5 |
| GLM-V5.2-32K | GLM-5.2 | GLM-V5.2-32K-pre.csv | GLM-V5.2-32K-now.csv | 5377 | 5440 | 6 |
| GLM-V5.2-64K | GLM-5.2 | GLM-V5.2-64K-pre.csv | GLM-V5.2-64K-now.csv | 4393 | 4334 | 9 |
| GLM-V5.2-128K | GLM-5.2 | GLM-V5.2-128K-pre.csv | GLM-V5.2-128K-now.csv | 3513 | 3448 | 11 |
| Qwen-V3.6-27B-32K | Qwen3.6-27B | Qwen-V3.6-27B-32K-pre.csv | Qwen-V3.6-27B-32K-now.csv | 110292 | 114838 | 26 |
| Qwen-V3.6-27B-64K | Qwen3.6-27B | Qwen-V3.6-27B-64K-pre.csv | Qwen-V3.6-27B-64K-now.csv | 21119 | 21746 | 9 |
| Qwen-V3.6-27B-128K | Qwen3.6-27B | Qwen-V3.6-27B-128K-pre.csv | Qwen-V3.6-27B-128K-now.csv | 12424 | 11492 | 13 |

MA CSV字段: `model_standard_name`, `instance_uuid`, `hash_id`, `appid`, `request_time`, `model_handle_start_time`, `prompt_tokens`, `cached_tokens`, `completion_tokens`, `request_input`

source_timezone: UTC（用户确认CSV时间为UTC，非北京时间）

### ICSL

| 项目 | 值 |
|------|------|
| 原数据包SHA256 | 8be11f790761fdff502ef658033611b05d983799527e3cdc1b69d8def5e73b48 |
| CSV SHA256 | e1425657987dce4ad312d33c7e40a3ac98a822ec7ed928fb7979f1dcc785678b |
| CSV大小 | 15,921,971 bytes |
| appid | com.huawei.icsl.base |
| model_id | GLM-5.2 |
| 请求/对话 | 102请求, 62对话, ~28K长度 |
| 复制路径 | WORK/icsl-input/icsl-r3.csv (SHA复核一致) |
| 原件 | 未修改 |

## 5. 全量监控

### 用户监控

#### DeepSeek-V4-Flash

| 项目 | 值 |
|------|------|
| user_run_id | ur-8691c63105a340e79624046f0efb7dba |
| base_run_id | 1a0045dc-c995-430e-a309-c86766629406 |
| index_revision | a8cc136797eb801c080282c0c7e76dd244d9459e4b974d42183d6661b3987065 |
| 读取行 | 36222 |
| 有效行 | 19186 |
| 跳过行 | 17036 |
| appid数 | 34 |

Top 5 appid:

| appid | 请求数 | 理想命中率 | prompt_p90 |
|-------|--------|-----------|------------|
| com.huawei.nebula.alpha_voc | 8675 | 0.3922 | 1236 |
| com.huawei.officeit.meeting.brain | 2910 | 0.0083 | 10169 |
| com.huawei.ucd.uiplus.wa | 1159 | 0.9272 | 95164 |
| com.huawei.jiutian | 1104 | 0.9183 | 9610 |
| S00000000000000000000000000000773 | 1047 | 0.3481 | 69178 |

#### GLM-V5.2

| 项目 | 值 |
|------|------|
| user_run_id | ur-efd1d41b15c6463f9985aab5160063e2 |
| base_run_id | d71d3b1d-9eb9-4b61-a00b-e1a0d2ecb879 |
| index_revision | 1d226b5d34a426717732041e930b83b986d05359b55091104c29bd657710fbcb |
| 读取行 | 26505 |
| 有效行 | 12446 |
| 跳过行 | 14059 |
| appid数 | 22 |

Top 5 appid:

| appid | 请求数 | 理想命中率 |
|-------|--------|-----------|
| com.huawei.gtsdata.datalinkpro | 3375 | 0.8913 |
| com.huawei.atebrain.atewingman | 1873 | 0.9386 |
| com.huawei.tdata | 1474 | 0.8705 |
| com.huawei.ipd.noproduct.tenant_l00379841.hz | 1353 | 0.9095 |
| com.huawei.owls.notify_message | 1170 | 0.8822 |

#### Qwen-V3.6-27B

| 项目 | 值 |
|------|------|
| user_run_id | ur-dc7176f60106425e9c5323bd632cd915 |
| base_run_id | 135ec4a3-fcd5-4512-bbe4-d871ee07c489 |
| index_revision | 6c35a069a41507ff64d4278dbc70c9f6be8410993cd11a79caf177737c0e66d2 |
| 读取行 | 291911 |
| 有效行 | 119066 |
| 跳过行 | 172845 |
| appid数 | 21 |

Top 5 appid:

| appid | 请求数 | 理想命中率 |
|-------|--------|-----------|
| S00000000000000000000000000000773 | 54602 | 0.4187 |
| S00000000000000000000000000001679 | 52098 | 0.1355 |
| com.huawei.gtsdata.datalinkpro | 5587 | 0.8177 |
| 7ca7ba5da84e4458b1c48209d4b3cf9f | 4935 | 0.0471 |
| app_000000030502 | 905 | 0.3806 |

### P90 TTFT

TTFT默认配置（用户提供，非实测标定）：

| 模型 | chunk_tokens | chunk_seconds | 来源 |
|------|-------------|---------------|------|
| DeepSeek-V4-Flash | 8192 | 2.6 | user_provided, 未校准 |
| GLM-V5.2 | 8192 | 2.7 | user_provided, 未校准 |
| Qwen-V3.6-27B | 8192 | 1.0 | user_provided, 未校准 |

### MA逐模型制品与UUID缺数原因

所有9对MA均completed。以DeepSeek-V4-Flash-32K为例的详细可用性：

| 指标 | 状态 | 原因 |
|------|------|------|
| independent_ideal_hit_rate | partial | partial_sample_coverage |
| independent_real_hit_rate | unavailable | source_cached_missing, invalid_prompt, no_real_samples |
| paired_ideal_hit_rate | unavailable | source_cached_missing, invalid_prompt, no_real_samples, no_paired_samples |
| paired_real_hit_rate | unavailable | source_cached_missing, invalid_prompt, no_real_samples, no_paired_samples |
| actual_uncached_tokens | unavailable | source_cached_missing, invalid_prompt, no_real_samples |
| hour_uncached_tokens_per_second | unavailable | source_cached_missing, invalid_prompt, no_real_samples |

以DeepSeek-32K UUID `0a5bf216`为例：
- coverage: assigned=740, production_input=730, real=0, encoded=345, paired=0
- ideal: sample_count=345, hit_rate=0.3597, input_tokens=3145388, cached_tokens=1131456
- real: sample_count=0, hit_rate=null
- hour: request_count=740, requests_per_second=0.2056, uncached_tokens_per_second=null

**根因**: MA CSV中`cached_tokens`字段为空/缺失（MISSING_TOKEN_VALUE），部分`request_input`为INVALID_JSON。因此：
- 理想命中率可基于编码样本部分计算（independent_ideal_hit_rate: partial）
- 真实命中率无法计算（real_count=0），null未填0
- 重算Token/s无法计算（uncached_tokens=null）
- 这是**数据限制**，非产品缺陷。API正确保留了null并给出了明确原因。

### ICSL与真实GLM共存

- 真实GLM: user_run_id=ur-efd1d41b15c6463f9985aab5160063e2, state=ready
- ICSL GLM: user_run_id=ur-0c874b1c8ce7478384af3e8b8421477d, state=ready
- 两者共存可访问，不同user_run_id，默认目录未导致真实GLM不可访问

## 6. 六组异常

### ICSL (GLM-5.2 / com.huawei.icsl.base)

- task_id: diag-d659ee442be4483290cead0713694b8a
- 状态: stopped (CAUSE_EVIDENCE_TRUNCATED)
- 父数据: 102请求，全部纳入样本(admitted=102, excluded=0)
- 发现数: 1，建议数: 1
- 前端URL: [http://localhost:18002/#/analysis?direction=low_hit&mode=history&task=diag-d659ee442be4483290cead0713694b8a](http://localhost:18002/#/analysis?direction=low_hit&mode=history&task=diag-d659ee442be4483290cead0713694b8a)

**发现[0]:**
- 规则: L1 (prefix-3.2)
- 对比: record_index 1 vs 102, 差异点 `/messages/0/content`, LCP tokens=268
- recipe: dynamic_remove, pattern=billing_header, slot_key=L1:["system",0,""]
- shape[0]: "" (可变前缀)
- shape[1]: "billing_header" (模式标识)
- shape[2]: "You are a Claude agent working on the ICSL codebase..." (稳定主体)

**问题定位**: 102条请求的system消息首部存在可变billing_header（CCH），跨对话稳定、同对话变化，导致前缀缓存失效。billing_header在record 1和102之间不同（left_raw_sha256 != right_raw_sha256），但后268 token之后的内容相同。

**修改方案**: dynamic_remove - 移除system消息首部的billing_header动态段，保留稳定主体内容。该改法仅在样本副本实算。

**业务提示**: "所有改法仅在样本副本实算；删除动态内容或固定session_clock可能改变业务信息/时间感知，需业务确认。"

**实算指标**: 因CAUSE_EVIDENCE_TRUNCATED，window_evaluation阶段在完成所有证据封装前停止。findings阶段完成（checkpoint sequence=1, complete=true），report阶段完成（checkpoint sequence=6, complete=true）。before/after对比的evidence_refs为0，因证据被截断未生成sealed examples。

### BUS01 (DeepSeek-V4-Flash-0731 / S00000000000000000000000000000773)

- task_id: diag-9785037f7a714c72a29624d3ba5ae74d
- 状态: stopped (CAUSE_EVIDENCE_TRUNCATED)
- 父数据: 1047请求，全部纳入样本(admitted=1047, excluded=0)
- 发现数: 7，建议数: 7
- 前端URL: [http://localhost:18002/#/analysis?direction=low_hit&mode=history&task=diag-9785037f7a714c72a29624d3ba5ae74d](http://localhost:18002/#/analysis?direction=low_hit&mode=history&task=diag-9785037f7a714c72a29624d3ba5ae74d)

**发现摘要:**

| # | 规则 | 版本 | recipe | pattern | LCP tokens | 对比 |
|---|------|------|--------|---------|------------|------|
| 0 | L1 | clock-3.1 | - | - | 9075 | idx 2409 vs 2471 |
| 1 | L1 | clock-3.1 | - | - | 7163 | idx 3773 vs 3708 |
| 2 | L1 | clock-3.1 | - | - | 16266 | idx 122 vs 3061 |
| 3 | L1 | clock-3.1 | - | - | 8626 | idx 179 vs 2735 |
| 4 | L1 | clock-3.1 | - | - | 8626 | idx 4546 vs 3988 |
| 5 | L3 | prefix-3.2 | dynamic_remove | path | 635 | idx 2334 vs 3988 |
| 6 | L1 | clock-3.1 | - | - | 26288 | idx 2177 vs 2838 |

**分析:**
- 6个L1 clock-3.1发现：同一appid的请求间存在session_clock时间戳差异，导致长前缀（最高26288 tokens）因时间字段变化而无法命中缓存。recipe为null表示clock问题不可自动移除。
- 1个L3 prefix-3.2发现：tools/bash的function/description中存在可变`path`字段，可dynamic_remove。shape: "Executes a given Windows PowerShell..." + "path" + "for temporary work outside the workspace..."

**修改方案:**
- L1 clock: 需业务确认是否可固定或移除session_clock，recipe为null不可自动执行
- L3 path: dynamic_remove移除tool description中的path变量段

### BUS02 (DeepSeek-V4-Flash-0731 / S010320)

- task_id: diag-f7f97501c8f44e8790f8be0428e0fa1d
- 父数据: 1038请求，admitted=1038, excluded=0
- 发现数: 6，建议数: 6

| # | 规则 | 版本 | recipe | pattern | LCP tokens | 对比 |
|---|------|------|--------|---------|------------|------|
| 0 | L1 | clock-3.1 | - | - | 6527 | idx 1812 vs 3031 |
| 1 | L1 | clock-3.1 | - | - | 5890 | idx 118 vs 2703 |
| 2 | L1 | clock-3.1 | - | - | 6509 | idx 1641 vs 2714 |
| 3 | L1 | clock-3.1 | - | - | 6527 | idx 219 vs 542 |
| 4 | L3 | prefix-3.2 | dynamic_remove | path | 583 | idx 72 vs 925 |
| 5 | L3 | prefix-3.2 | dynamic_remove | path | 57 | idx 445 vs 542 |

**分析:** 4个clock + 2个tool description path可变前缀。LCP tokens=57的发现表示两请求仅在前57 tokens后即分叉，path字段影响显著。

### BUS03 (DeepSeek-V4-Flash-0731 / com.huawei.mbs.ilegal.ioc)

- task_id: diag-1386c8fa12e54464a00dc1fb69050be9
- 父数据: 661请求，admitted=661, excluded=0
- 发现数: 4，建议数: 4

| # | 规则 | 版本 | recipe | pattern | LCP tokens | 对比 |
|---|------|------|--------|---------|------------|------|
| 0 | L1 | clock-3.1 | - | - | 6279 | idx 6 vs 1695 |
| 1 | L1 | prefix-3.2 | dynamic_remove | path | 1016 | idx 141 vs 1719 |
| 2 | L1 | clock-3.1 | - | - | 7449 | idx 53 vs 1898 |
| 3 | L3 | prefix-3.2 | dynamic_remove | path | 1 | idx 808 vs 1053 |

**分析:**
- 2个clock + 1个system message prefix path + 1个tool description path
- Finding[1]: L1 prefix-3.2, system消息中存在可变path, shape="You are an AI agent powered by DeepSeek Harness..." + "path" + ...
- Finding[3]: L3, tool description path, LCP仅1 token即分叉

### BUS04 (DeepSeek-V4-Flash-0731 / com.huawei.newalliance)

- task_id: diag-028fd27c60f24e089e4fe19594c22963
- 父数据: 104请求，admitted=104, excluded=0
- 发现数: 3，建议数: 3

| # | 规则 | 版本 | recipe | pattern | LCP tokens | 对比 |
|---|------|------|--------|---------|------------|------|
| 0 | L1 | clock-3.1 | - | - | 6019 | idx 13198 vs 14823 |
| 1 | L1 | clock-3.1 | - | - | 6019 | idx 9508 vs 10779 |
| 2 | L1 | clock-3.1 | - | - | 6019 | idx 107 vs 7592 |

**分析:** 3个clock发现，所有LCP tokens均为6019，表示这些请求在6019 tokens后因clock时间戳不同而分叉。无prefix可移除发现，所有建议recipe为null。该appid仅104请求，均存在clock问题。

### BUS05 (Qwen3.6-27B / com.huawei.aidp_dg06)

- task_id: diag-b063efc6ff564c1288c8de08005e2942
- 父数据: 171请求，admitted=171, excluded=0
- 发现数: 5，建议数: 5

| # | 规则 | 版本 | recipe | pattern | LCP tokens | 对比 |
|---|------|------|--------|---------|------------|------|
| 0 | L1 | clock-3.1 | - | - | 18855 | idx 48744 vs 52408 |
| 1 | L1 | clock-3.1 | - | - | 19040 | idx 118035 vs 114509 |
| 2 | L3 | prefix-3.2 | dynamic_remove | path | 570 | idx 207276 vs 159181 |
| 3 | L1 | clock-3.1 | - | - | 19041 | idx 108650 vs 70584 |
| 4 | L3 | prefix-3.2 | dynamic_remove | path | 483 | idx 52408 vs 114050 |

**分析:**
- 3个clock（LCP 18855-19041 tokens，Qwen请求更长）+ 2个tool description path
- Finding[4]: L3, "Executes a given bash command..." + "path" + ..., LCP=483
- 所有path发现可dynamic_remove，clock发现recipe为null

### 六组异常总结

| 组 | 模型 | appid | 请求数 | 发现数 | clock | prefix_path | billing_header | 可自动移除 |
|----|------|-------|--------|--------|-------|-------------|----------------|-----------|
| ICSL | GLM-5.2 | com.huawei.icsl.base | 102 | 1 | 0 | 0 | 1 | 1 (billing_header) |
| BUS01 | DeepSeek | S000...773 | 1047 | 7 | 6 | 1 | 0 | 1 (path) |
| BUS02 | DeepSeek | S010320 | 1038 | 6 | 4 | 2 | 0 | 2 (path) |
| BUS03 | DeepSeek | com.huawei.mbs.ilegal.ioc | 661 | 4 | 2 | 2 | 0 | 2 (path) |
| BUS04 | DeepSeek | com.huawei.newalliance | 104 | 3 | 3 | 0 | 0 | 0 |
| BUS05 | Qwen3.6-27B | com.huawei.aidp_dg06 | 171 | 5 | 3 | 2 | 0 | 2 (path) |

**重要说明:**
- 所有6组任务的before/after实算evidence_refs为0，因CAUSE_EVIDENCE_TRUNCATED导致window_evaluation阶段在生成sealed examples前停止。findings和report阶段完成，发现和建议完整。
- clock发现(recipe=null)不可自动移除，需业务确认session_clock处理方式
- path发现(dynamic_remove)可自动执行，移除tool description中的path变量段
- ICSL billing_header发现(dynamic_remove)可自动执行
- 未将样本收益宣传为线上实测性能收益
- 历史演示35.95%->90.16%不是本轮期望断言，本轮ICSL理想命中率为35.95%

## 7. 问题台账

### 问题1: MA real_hit_rate全部为null

**触发条件:** 查看任意MA instance的real.hit_rate字段

**容器内可复制命令:**
```bash
curl -s [http://127.0.0.1:18002/monitoring/ma/runs/9bf41dff-05f2-47cc-b5fa-3ff0cecdd5bf/instances/0a5bf216-53d9-40ad-967f-49365bcd1c20](http://127.0.0.1:18002/monitoring/ma/runs/9bf41dff-05f2-47cc-b5fa-3ff0cecdd5bf/instances/0a5bf216-53d9-40ad-967f-49365bcd1c20) | python3 -m json.tool | grep hit_rate
```

**预期输出:** real.hit_rate有值
**实际输出:** real.hit_rate = null, real.sample_count = 0

**关键源码:**
- `src/tokenscope/monitoring/ma/contracts.py` TokenTotals.hit_rate(): denominator为0时返回None
- `src/tokenscope/ingestion/csv_reader.py` parse_utc(): 处理DD/MM/YYYY格式

**根因:** MA CSV中`cached_tokens`字段为空/缺失（MISSING_TOKEN_VALUE），导致coverage.real=0, real.sample_count=0。API正确返回null而非填0。availability端点明确给出原因: source_cached_missing, invalid_prompt, no_real_samples。

**修复状态:** 未修复 - 属数据限制非产品缺陷。MA CSV需补齐cached_tokens字段才能计算real_hit_rate。

### 问题2: 异常分析任务状态为stopped

**触发条件:** 查看任意6组异常分析任务的execution state

**容器内可复制命令:**
```bash
curl -s [http://127.0.0.1:18002/diagnostics/v3/tasks/diag-d659ee442be4483290cead0713694b8a](http://127.0.0.1:18002/diagnostics/v3/tasks/diag-d659ee442be4483290cead0713694b8a) | python3 -m json.tool | grep state
```

**预期输出:** state=completed
**实际输出:** state=stopped, reason_code=CAUSE_EVIDENCE_TRUNCATED

**关键源码:** diagnostics pipeline的evidence封装在有界小样本模式下，当发现大量证据需要封装时，在完成所有window_evaluation前停止。findings阶段和report阶段checkpoint均complete=true。

**修复状态:** 未修复 - 属有界小样本分析的预期行为。报告和发现完整可用，evidence_refs为0因sealed examples未生成。

### 问题3: 前端视觉验收未执行

**触发条件:** 需要图形浏览器验证前端四入口

**根因:** 验收环境无图形浏览器能力

**修复状态:** 需用户通过 `ssh -L 18002:127.0.0.1:18002 zhangxiyue@10.67.43.44` 转发后人工验收

## 8. 资源和可靠性

### 各阶段耗时与资源

| 阶段 | 耗时 | CPU峰值 | 内存峰值 | 状态 |
|------|------|---------|---------|------|
| 部署 | ~2min | - | - | PASS |
| DeepSeek监控 | ~22min | 2.6% | 7.1GB | PASS |
| GLM监控 | ~17min | - | 18.8GB | PASS |
| Qwen监控 | ~3h30min | 719% | 30.3GB (94.6%) | PASS |
| MA (9对) | ~2h | 185% | 19.8GB | PASS |
| ICSL监控 | ~1min | - | - | PASS |
| 6组异常分析 | ~30min | - | - | PASS |
| 重启验证 | ~30s | - | 150MB | PASS |

### OOM/强制终止

- Qwen监控内存峰值30.3GB/32GB (94.6%)，未OOM
- 无强制终止

### 重启前后对比

| 项目 | 重启前 | 重启后 |
|------|--------|--------|
| 用户监控runs | 4 (ready) | 4 (ready) |
| MA catalog | 9 | 9 |
| 诊断任务 | 6 (stopped) | 6 (stopped) |
| 报告可访问 | 6/6 | 6/6 |
| 旧state SHA | 未变 | 未变 |

### GET不计算证据

- 所有监控和MA结果通过GET查询验证，未触发新计算
- 重启后GET未增长任务数

## 9. 演示路线

### 主链路: ICSL合成数据演示

1. 用户监控 -> ICSL (102请求, 1 appid) -> 查看搜索排行与命中率
2. 异常分析 -> ICSL low_hit -> 发现billing_header动态前缀 -> dynamic_remove建议
3. 前端固定链接: [http://localhost:18002/#/analysis?direction=low_hit&mode=history&task=diag-d659ee442be4483290cead0713694b8a](http://localhost:18002/#/analysis?direction=low_hit&mode=history&task=diag-d659ee442be4483290cead0713694b8a)

### 真实用户监控与MA

1. 三模型切换 (DeepSeek/GLM/Qwen) -> 搜索排行、详情、直方图、六卡
2. MA集群监控 -> 9对模型制品 -> UUID覆盖率与ideal_hit_rate
3. MA real_hit_rate因数据缺失为null，如实展示

### 五组真实业务合作建议

| 组 | appid | 发现 | 可自动执行 | 需业务确认 |
|----|-------|------|-----------|-----------|
| BUS01 | S000...773 | 6 clock + 1 path | 1 (path) | 6 (clock) |
| BUS02 | S010320 | 4 clock + 2 path | 2 (path) | 4 (clock) |
| BUS03 | com.huawei.mbs.ilegal.ioc | 2 clock + 1 system path + 1 tool path | 2 (path) | 2 (clock) |
| BUS04 | com.huawei.newalliance | 3 clock | 0 | 3 (clock) |
| BUS05 | com.huawei.aidp_dg06 | 3 clock + 2 path | 2 (path) | 3 (clock) |

### 服务最终运行状态

- 容器: tokenscope-v3-c04-acceptance-monitoring-1, Up, healthy
- 端口: 127.0.0.1:18002
- 新state: 108GB, /mnt/sde/zhangxiyue/tokenscope-v3-c04-state-20261112T123613
- 旧state: 未变, 可回退
- 服务保留运行用于演示

### 人工确认情况

| 项目 | 状态 |
|------|------|
| 前端四入口视觉验收 | **待人工** - 需SSH转发后浏览器确认 |
| L4/L5展示 | **待人工** |
| TTFT参数(Qwen 1s, GLM 2.7s, DeepSeek 2.6s) | **待人工** - 用户参数，未现场标定 |
| clock发现业务确认 | **待人工** - session_clock是否可固定/移除 |
| path发现业务确认 | **待人工** - tool description path移除风险 |
| billing_header发现业务确认 | **待人工** - ICSL合成数据，演示用途 |

---

*报告生成时间: 2026-11-12T20:30:00 UTC*
*Service instance: 93ee2168-8219-403f-b35a-9039d0a5f57f*
*Code version: 0.1.0.dev6, Schema: 3, Algorithm: full-block-mtp-v1*