# HUAWEI V3 C04 补证报告

## 1. 明确结论

### 六条 session_clock 方案

BUS01 共有 6 条 `rule_version=clock-3.1` 的方案，每条都是 `session-clock-normalize-3.1` 类型，将 `<session_clock>` 块中的实际时间值替换为常量 `NORMALIZED`。六条方案的区别来自：

1. **不同的用户身份前缀**（`field_shape[0]`）：阮琴惠(r00812553)、徐建(x30072419)、马万军(m30016376)、李泰霖(lWX1509069)、李泰霖(lWX1509069)、蔡孟儒(c00837774) — 每条方案发现的不同用户请求对，其 system 消息首部的 `<current_pedestal_user>` 用户身份段不同。
2. **不同的 agent_identity 后缀**（`field_shape[-1]`）：self_evolution_identity、agent_identity(蔡孟儒等设备资源周报生成)、agent_identity(生成PPT)、agent_identity(10月17日 会议98239528 查询) — 不同用户配置了不同 agent 身份段。
3. **不同的 clock 值**：`<session_clock>` 块中的实际时间戳值不同（如 "27"、"1:41"、"0:10"、"0:29"、"3:37"、"7:0"）。
4. 六条方案的两两请求对完全不相交（12 个唯一请求索引，零交集），每条方案独立比较不同的请求对。

### 实际样本数

- **父数据总数 ≠ 准入数量 ≠ 实际选中数量 ≠ 实际修改数量**
- BUS01: 父数据 1047 请求 → admitted 1047（0 排除）→ discovery 窗口 73 成员 → 每方案 matched/modified 各不相同（3, 2, 17, 13, 11, 7）
- 六组任务实际选中窗口成员均远小于 admitted_count（73/102/71/66/72/74 vs 102~1047）

### 各自收益

每方案独立应用一个 recipe，不叠加。同一 baseline（P=3992073, H=1274656, C=2717417），独立收益率从 +0.71pp 到 +11.34pp 不等。**组合收益未评估，单项收益不可相加。**

### stopped 原因

`stopped` 来自 **发现阶段不完整**（`discovery.complete=false`），原因是 L4 规则的原因分组达到 128 上限触发 `CAUSE_EVIDENCE_TRUNCATED`。所有 7 条方案的窗口评估均为 `complete=True, status=positive`。`forced_termination=False`。

### 上一份报告勘误

| 原结论 | 修正 |
| --- | --- |
| "evidence_refs为0" | **错误**。BUS01 evidence_refs 有 10 个条目，ICSL 有 4 个，全部六组均非空 |
| "before/after实算evidence_refs为0，sealed examples未生成" | **错误**。所有方案均有完整 sealed examples，通过 `GET /diagnostics/v3/tasks/{task_id}/evidence/{owner_id}` 可读取 |
| "admitted=1047全部纳入样本" | **误导**。admitted=1047 但 discovery 窗口仅 73 成员（max_requests=300 限制 + 算法选择） |
| "6组异常分析任务状态为stopped属有界小样本分析的预期行为" | **不准确**。stopped 因 L4 原因分组达 128 上限，发现不完整；窗口评估完整 |
| clock发现"recipe为null" | **错误**。clock recipe 非 null，含 version/discovery/logical_field/field_shape/block_indices/constant/business_effect |
| ICSL "因CAUSE_EVIDENCE_TRUNCATED导致window_evaluation阶段在生成sealed examples前停止" | **错误**。ICSL 窗口 complete=True, evidence_refs=4, 有完整 sealed example |

## 2. 版本、任务和报告身份及SHA256

### 服务身份

| 项目 | 值 |
| --- | --- |
| service_instance_id | 93ee2168-8219-403f-b35a-9039d0a5f57f |
| 镜像ID | sha256:f2162dfc460d47641ef0d64ba1f65974e5c0675b5022217997187927f1e8b466 |
| 源码commit | 57fe9f64d78f6363ee18a12ff97693e00ae1fe3d |
| 新state路径 | /mnt/sde/zhangxiyue/tokenscope-v3-c04-state-20261112T123613 |
| 容器状态 | Up 16 hours (healthy) |

### 任务报告SHA256

| 任务 | task_id | task SHA256 (前16) | report SHA256 (前16) |
| --- | --- | --- | --- |
| ICSL | diag-d659ee442be4483290cead0713694b8a | 4064fff926187b53 | e286e86c07bbc8a0 |
| BUS01 | diag-9785037f7a714c72a29624d3ba5ae74d | d73bc5e0ac1b01c2 | 80a246126432b314 |
| BUS02 | diag-f7f97501c8f44e8790f8be0428e0fa1d | ec65c01254c58ebb | 713169c2bfdc2170 |
| BUS03 | diag-1386c8fa12e54464a00dc1fb69050be9 | e9c6a15c9c4b7b67 | c7f7faa4ff715ddb |
| BUS04 | diag-028fd27c60f24e089e4fe19594c22963 | a43979bcfcae0e1d | 506be5bd00c4bbac |
| BUS05 | diag-b063efc6ff564c1288c8de08005e2942 | 674ea35d500a456b | 33c3e54876d2ae4e |

### 源码SHA256

| 文件 | SHA256 (前16) |
| --- | --- |
| prefix_analysis/clock_discovery_v3.py | 13b0d837170ea141 |
| analysis_common/clock_worker_v3.py | 54eb58775184a677 |
| analysis_common/evaluation_v3.py | 8a999e816dd5d79e |

### 只读验证

```
任务数读取前: 6 (全部 stopped)
任务数读取后: 6 (全部 stopped, 未变)
```

## 3. BUS01 六条 session_clock 方案差异与覆盖交集

### 六条方案对照表

| # | rec_idx | finding_id (前16) | lcp_tokens | left_idx | right_idx | matched | modified | 用户姓名 | agent_identity 类型 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0 | 0 | 372cbb48015ca1ba | 9075 | 2409 | 2471 | 3 | 3 | 阮琴惠 | self_evolution_identity |
| 1 | 1 | 7e2ec21c2bc25dd9 | 7163 | 3773 | 3708 | 2 | 2 | 徐建 | self_evolution_identity |
| 2 | 2 | 64553a1bb01d68ac | 16266 | 122 | 3061 | 17 | 17 | 马万军 | agent_identity(蔡孟儒等设备资源周报) |
| 3 | 3 | b52b7e9e2f206121 | 8626 | 179 | 2735 | 13 | 13 | 李泰霖 | agent_identity(生成PPT) |
| 4 | 4 | 6bc99ee1c2859e06 | 8626 | 4546 | 3988 | 11 | 11 | 李泰霖 | agent_identity(生成PPT) |
| 5 | 6 | b32b14da6a52e1c1 | 26288 | 2177 | 2838 | 7 | 7 | 蔡孟儒 | agent_identity(10月17日会议) |

### 差异来源

1. **不同用户身份前缀**：六条方案的 `field_shape[0]` 末尾分别为 `阮琴惠/r00812553`、`徐建/x30072419`、`马万军/m30016376`、`李泰霖/lWX1509069`、`李泰霖/lWX1509069`、`蔡孟儒/c00837774`。
2. **不同 agent_identity 后缀**：`field_shape[-1]` 开头分别为 `self_evolution_identity`（3条）、`agent_identity(蔡孟儒等设备资源周报生成)`、`agent_identity(生成PPT)`（2条）、`agent_identity(10月17日 会议98239528 查询)`。
3. **不同 clock 值**：`<session_clock>` 块中的时间值不同（"27"、"1:41"、"0:10"、"0:29"、"3:37"、"7:0"）。
4. **不同 LCP 长度**：9075、7163、16266、8626、8626、26288 — 因用户身份段和 agent 身份段长度不同导致前缀公共部分不同。
5. **block_indices 全部为 `["0"]`**、**constant 全部为 `"NORMALIZED"`**、**business_effect 全部为 `"changes_time_awareness"`** — 六条方案的 recipe 结构相同，差异在 field_shape 内容。

### recipe 完整字段（Clock[0] 为例）

```
{
  "version": "session-clock-normalize-3.1",
  "discovery": "automatic_l1",
  "logical_field": "[\"system\",0,\"\"]",
  "field_shape": [
    "你是我的专属助手...## 用户姓名 阮琴惠 ## 用户工号 r00812553 ## 邮箱 [ruanqinhui@huawei.com] </current_pedestal_user> <session_clock>",
    "</session_clock> <self_evolution_identity> 你是一个具有自进化能力的 AI 助手..."
  ],
  "block_indices": ["0"],
  "constant": "NORMALIZED",
  "business_effect": "changes_time_awareness"
}
```

六条 recipe 的 SHA256 各不相同（transformation_digest 不同）：

- Clock[0]: d4e36757e83f0c12...
- Clock[1]: cf872f54272bc8e9...
- Clock[2]: 296701942835224e...
- Clock[3]: d1a877d3ef20790c...
- Clock[4]: 63f98228b3a5c6b9...
- Clock[5]: b01688f4e7484f6d...

### 覆盖交集

六条方案的比较请求对两两交集均为空。去重后联合覆盖 12 个唯一请求索引：122, 179, 2177, 2409, 2471, 2735, 2838, 3061, 3708, 3773, 3988, 4546。每条方案独立修改不同请求，未修改相同位置。

### 证据样例（Clock[0]）

通过 `GET /diagnostics/v3/tasks/diag-9785037f7a714c72a29624d3ba5ae74d/evidence/finding:372cbb48...` 读取：

**before**:

```
{
  "excerpt": "27",
  "context_before": "...## 邮箱 [ruanqinhui@huawei.com] </current_pedestal_user>  <session_clock> ## 当前时间（本机时区：Asia/Shanghai） 2026/10/20 15:05:",
  "context_after": " </session_clock>  <self_evolution_identity> 你是一个具有自进化能力的 AI 助手..."
}
```

**after**:

```
{
  "excerpt": "NORMALIZED",
  "context_before": "...## 邮箱 [ruanqinhui@huawei.com] </current_pedestal_user>  <session_clock>",
  "context_after": "</session_clock>  <self_evolution_identity> 你是一个具有自进化能力的 AI 助手..."
}
```

**comparison** (来自 idx 2471):

```
{
  "excerpt": "46",
  "context_before": "...## 邮箱 [ruanqinhui@huawei.com] </current_pedestal_user>  <session_clock> ## 当前时间（本机时区：Asia/Shanghai） 2026/10/20 15:05:",
  "context_after": " </session_clock>  <self_evolution_identity> 你是一个具有自进化能力的 AI 助手..."
}
```

修改前后区别：`<session_clock>` 块中的时间值（"27" → "NORMALIZED"）被替换。comparison 请求(idx 2471)的时间值为 "46"，证明同一用户的不同请求时间不同，导致前缀缓存失效。

## 4. 六任务父集/准入/实际样本/修改数量表

| 任务 | parent_scope.request_count | decision.parent_count | admitted_count | excluded_count | discovery窗口members | discovery窗口raw_bytes | discovery窗口prompt_tokens |
| --- | --- | --- | --- | --- | --- | --- | --- |
| ICSL | 102 | 102 | 102 | 0 | 102 | 15,740,750 | 2,855,919 |
| BUS01 | 1047 | 1047 | 1047 | 0 | 73 | 14,954,480 | 3,992,073 |
| BUS02 | 1038 | 1038 | 1038 | 0 | 71 | 14,744,147 | 3,919,732 |
| BUS03 | 661 | 661 | 661 | 0 | 66 | 15,462,854 | 3,988,020 |
| BUS04 | 104 | 104 | 104 | 0 | 72 | 15,004,451 | 3,992,463 |
| BUS05 | 171 | 171 | 171 | 0 | 74 | 15,374,870 | 3,980,282 |

### 限制参数（六组相同）

```
{
  "max_requests": "300",
  "max_raw_bytes": "67108864",
  "max_prompt_tokens": "4000000",
  "max_record_bytes": "8388608",
  "max_record_tokens": "500000",
  "max_metadata_bytes": "8388608",
  "max_snapshot_bytes": "111158272",
  "max_exclusion_examples": "32",
  "review_requested": false
}
```

ICSL admitted=102 且窗口 members=102（全部纳入，因 102 < 300 max_requests）。BUS01-05 admitted 远大于窗口 members（73/71/66/72/74），因 max_requests=300 限制 + first-prefix-last-suffix-1 算法选择。

### 每方案 matched/modified 统计

| 任务 | 方案 | rule_version | n | matched | modified |
| --- | --- | --- | --- | --- | --- |
| ICSL | rec[0] | prefix-3.2 | 102 | 102 | 102 |
| BUS01 | rec[0] | clock-3.1 | 73 | 3 | 3 |
| BUS01 | rec[1] | clock-3.1 | 73 | 2 | 2 |
| BUS01 | rec[2] | clock-3.1 | 73 | 17 | 17 |
| BUS01 | rec[3] | clock-3.1 | 73 | 13 | 13 |
| BUS01 | rec[4] | clock-3.1 | 73 | 11 | 11 |
| BUS01 | rec[5] | prefix-3.2 | 73 | 39 | 39 |
| BUS01 | rec[6] | clock-3.1 | 73 | 7 | 7 |
| BUS02 | rec[0] | clock-3.1 | 71 | 5 | 5 |
| BUS02 | rec[1] | clock-3.1 | 71 | 10 | 10 |
| BUS02 | rec[2] | clock-3.1 | 71 | 6 | 6 |
| BUS02 | rec[3] | clock-3.1 | 71 | 2 | 2 |
| BUS02 | rec[4] | prefix-3.2 | 71 | 21 | 21 |
| BUS02 | rec[5] | prefix-3.2 | 71 | 24 | 24 |
| BUS03 | rec[0] | clock-3.1 | 66 | 14 | 14 |
| BUS03 | rec[1] | prefix-3.2 | 66 | 9 | 9 |
| BUS03 | rec[2] | clock-3.1 | 66 | 14 | 14 |
| BUS03 | rec[3] | prefix-3.2 | 66 | 15 | 15 |
| BUS04 | rec[0] | clock-3.1 | 72 | 6 | 6 |
| BUS04 | rec[1] | clock-3.1 | 72 | 16 | 16 |
| BUS04 | rec[2] | clock-3.1 | 72 | 31 | 31 |
| BUS05 | rec[0] | clock-3.1 | 74 | 2 | 2 |
| BUS05 | rec[1] | clock-3.1 | 74 | 4 | 4 |
| BUS05 | rec[2] | prefix-3.2 | 74 | 11 | 11 |
| BUS05 | rec[3] | clock-3.1 | 74 | 3 | 3 |
| BUS05 | rec[4] | prefix-3.2 | 74 | 60 | 60 |

## 5. 独立收益原始整数与精确复核

### BUS01 逐方案收益

所有方案共用同一 baseline 和 discovery 窗口(n=73, P=3992073, H=1274656, C=2717417)。

| 方案 | rule_version | matched | modified | before P | before H | before C | after P | after H | after C | before_rate | after_rate | pp (精确) | improvement_pp 分数验证 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| rec[0] | clock-3.1 | 3 | 3 | 3992073 | 1274656 | 2717417 | 3991998 | 1303104 | 2688894 | 31.9297% | 32.6429% | +0.7132 | 1894368198400/2656057905309 ✓ |
| rec[1] | clock-3.1 | 2 | 2 | 3992073 | 1274656 | 2717417 | 3992023 | 1319968 | 2672055 | 31.9297% | 33.0651% | +1.1355 | 18095254457600/15936447233679 ✓ |
| rec[2] | clock-3.1 | 17 | 17 | 3992073 | 1274656 | 2717417 | 3991648 | 1727232 | 2264416 | 31.9297% | 43.2712% | +11.3415 | 5647681746400/497967193947 ✓ |
| rec[3] | clock-3.1 | 13 | 13 | 3992073 | 1274656 | 2717417 | 3991748 | 1686624 | 2305124 | 31.9297% | 42.2528% | +10.3231 | 41125514821600/3983837353401 ✓ |
| rec[4] | clock-3.1 | 11 | 11 | 3992073 | 1274656 | 2717417 | 3991798 | 1471744 | 2520054 | 31.9297% | 36.8692% | +4.9395 | 39357010691200/7967774508627 ✓ |
| rec[5] | prefix-3.2 | 39 | 39 | 3992073 | 1274656 | 2717417 | 3991306 | 1274656 | 2716650 | 31.9297% | 31.9358% | +0.0061 | 48883057600/7966792458669 ✓ |
| rec[6] | clock-3.1 | 7 | 7 | 3992073 | 1274656 | 2717417 | 3991898 | 1477600 | 2514298 | 31.9297% | 37.0150% | +5.0853 | 40519516385600/7967974112277 ✓ |

P=H+C 守恒验证：所有 before/after 均通过。

**组合收益未评估，单项收益不可相加。** 每条方案使用同一 sample_id 和 discovery 窗口，每次独立应用一个 recipe，并非连续叠加。无联合方案评估存在。

### ICSL 收益

| 方案 | rule_version | matched | modified | before P | before H | before C | after P | after H | after C | before_rate | after_rate | pp |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| rec[0] | prefix-3.2 | 102 | 102 | 2855919 | 1026688 | 1829231 | 2853567 | 2572672 | 280895 | 35.9495% | 90.1564% | +54.2069 |

ICSL 有完整样本收益：102/102 matched/modified，35.95% → 90.16%，+54.21pp。

### 其他四组收益摘要

| 任务 | 方案数 | before_rate | 最高单方案 pp | 最低单方案 pp | 负收益 |
| --- | --- | --- | --- | --- | --- |
| BUS02 | 6 | 61.20% | +9.87 (rec[1]) | -0.005 (rec[4], status=negative) | 1条 |
| BUS03 | 4 | 45.43% | +13.38 (rec[2]) | +0.003 (rec[3]) | 无 |
| BUS04 | 3 | 26.36% | +20.57 (rec[2]) | +7.01 (rec[0]) | 无 |
| BUS05 | 5 | 31.53% | +1.62 (rec[1]) | +0.078 (rec[0]) | 无 |

BUS02 rec[4] (prefix-3.2, LCP=57) status=negative，pp=-0.0050，before_rate=61.20%，after_rate=61.19%。P 变化(3919732→3919318)但 H 几乎不变(2398848→2398400)，移除 path 导致少量 prompt token 增加但 hit 减少更多。

## 6. stopped 原因与发现/窗口/证据完整性判断

### 任务执行状态

| 任务 | state | phase | reason_code | forced_termination |
| --- | --- | --- | --- | --- |
| ICSL | stopped | diagnosis | CAUSE_EVIDENCE_TRUNCATED | False（字段存在） |
| BUS01 | stopped | diagnosis | CAUSE_EVIDENCE_TRUNCATED | False |
| BUS02 | stopped | diagnosis | CAUSE_EVIDENCE_TRUNCATED | False |
| BUS03 | stopped | diagnosis | CAUSE_EVIDENCE_TRUNCATED | False |
| BUS04 | stopped | diagnosis | CAUSE_EVIDENCE_TRUNCATED | False |
| BUS05 | stopped | diagnosis | CAUSE_EVIDENCE_TRUNCATED | False |

### BUS01 checkpoints (47个，全部 complete=True)

- seq=1: findings.json (complete)
- seq=2-11: evidence-000002~000011 (window_evaluation, 10个, complete)
- seq=12: report-0000.json (complete)
- seq=13-16: evaluation-0001/discovery/rows.json, plan.json, evidence-000015, window-0001 (complete)
- seq=17: report-0002.json (complete)
- ...重复模式...
- seq=47: report-0014.json (complete)

所有 47 个 checkpoints 均 `complete=True`。

### BUS01 discovery 状态

```
{
  "complete": false,
  "reason_codes": ["CAUSE_EVIDENCE_TRUNCATED"],
  "checked_requests": 73,
  "comparisons": 1001,
  "candidate_limit": 16,
  "channel_visits": {"L1": "557", "L2": "392", "L3": "46658", "L4": "810", "L5": "810"},
  "cause_groups": 190,
  "cause_groups_by_rule": {"L1": 6, "L4": 128, "L3": 56}
}
```

### 源码分析：CAUSE_EVIDENCE_TRUNCATED 触发条件

**文件**: `src/tokenscope/prefix_analysis/clock_discovery_v3.py:271-272`

```
# line 269: 每条规则的原因分组计数
if group_counts.get(rule, 0) >= 128:
    complete = False
    if "CAUSE_EVIDENCE_TRUNCATED" not in reasons:
        reasons.append("CAUSE_EVIDENCE_TRUNCATED")
    continue  # 跳过该原因分组，不中止整个发现
```

- **触发规则**: L4（原因分组数 = 128，达到上限）
- **行为**: 跳过该 L4 原因分组（`continue`），设置 `complete=False`，不中止整个发现阶段
- L1（6组）和 L3（56组）未达上限，正常处理

**文件**: `src/tokenscope/analysis_common/clock_worker_v3.py:216-221`

```
# line 216: 最终状态判定
"state": "stopped" if incomplete or not discovery.complete else "completed",
"reason_code": (
    incomplete[0]["reason_code"]
    if incomplete
    else discovery.reason_codes[-1]
    if not discovery.complete
    else None
),
```

- `incomplete`（未完成窗口列表）为空（所有窗口 complete=True）
- `discovery.complete = False` → state = "stopped"
- `reason_code = discovery.reason_codes[-1]` = "CAUSE_EVIDENCE_TRUNCATED"

### 三层完整性判断

| 层次 | 状态 | 证据 |
| --- | --- | --- |
| 发现完整性 | **不完整** | `discovery.complete=false`，L4 原因分组达128上限，仅检查73/1047请求 |
| 窗口评估完整性 | **完整** | 所有7条方案 `complete=True`，47个checkpoint均complete |
| 证据可用性 | **完整** | `evidence_refs` 非空（BUS01有10条），`GET /evidence/{owner_id}` 可读取sealed examples |

### evidence_refs 实际内容

| 任务 | evidence_refs 数 | 类型 |
| --- | --- | --- |
| ICSL | 4 | 3 cause + 1 finding |
| BUS01 | 10 | 3 cause + 7 finding |
| BUS02 | 9 | cause + finding |
| BUS03 | 7 | cause + finding |
| BUS04 | 6 | cause + finding |
| BUS05 | 8 | cause + finding |

`evidence_mode = "sealed_examples"` — 证据以密封样例形式存储，通过 API 可读。

### ICSL 证据样例

通过 `GET /diagnostics/v3/tasks/diag-d659ee442be4483290cead0713694b8a/evidence/finding:79b0dbbb...` 读取：

**before excerpt**: `"4201"` (billing_header 中的 cch 值片段)
**before context_before**: `"...messages":[{"role":"system","content":"x-anthropic-billing-header: cc_entrypoint=sdk-py; cch=2`
**after excerpt**: `""` (空 — billing_header 被移除)
**after context_after**: `"You are a Claude agent working on the ICSL codebase..."`

billing_header（`x-anthropic-billing-header: cc_entrypoint=sdk-py; cch=2...`）被移除，保留稳定主体。

## 7. 上一份报告勘误表

| # | 原结论 | 原始证据 | 修正结论 | 仍未确定事项 |
| --- | --- | --- | --- | --- |
| 1 | "evidence_refs为0" | report.evidence_refs 为空对象 | **错误**。六组 evidence_refs 均非空（4~10条），含 cause 和 finding 引用 | 无 |
| 2 | "before/after实算evidence_refs为0，sealed examples未生成" | 上一份报告未读取 /evidence/{owner_id} 接口 | **错误**。所有方案有完整 sealed examples，含 before/after excerpt 和 context | 无 |
| 3 | "admitted=1047全部纳入样本" | admitted_count=1047 | **误导**。admitted=1047 但 discovery 窗口仅 73 成员（算法选择 + max_requests 限制） | 窗口选择算法的精确逻辑 |
| 4 | "属有界小样本分析的预期行为" | state=stopped | **不准确**。stopped 因 L4 原因分组达128上限导致发现不完整；窗口评估完整 | 是否有更多 L4 发现因截断未展示 |
| 5 | clock发现"recipe为null" | 上一份报告在 recommendation 层找 kind/pattern | **错误**。clock recipe 非 null，在 finding.recipe 中有完整 version/discovery/logical_field/field_shape/block_indices/constant/business_effect | 无 |
| 6 | ICSL "window_evaluation阶段在生成sealed examples前停止" | task.state=stopped | **错误**。ICSL 窗口 complete=True, evidence_refs=4, 有完整 sealed example | 无 |
| 7 | "所有6组任务的before/after实算evidence_refs为0" | 未读取 evidence API | **错误**。六组均有非空 evidence_refs 和可读 sealed examples | 无 |
| 8 | BUS02 rec[4] 未标注负收益 | 上一份报告未展示 window metrics | BUS02 rec[4] status=negative, pp=-0.0050 | 无 |
| 9 | ICSL "35.95%" 作为理想命中率 | ICSL rankings ideal_hit_rate=0.3595 | **混淆**。35.95% 是用户监控的理想命中率；异常分析窗口 before_rate 也是 35.95%（巧合）；after_rate=90.16% 是实算改进后命中率 | 无 |
| 10 | "组合收益未评估" | 正确 | 保留：组合收益未评估，单项收益不可相加 | 无 |

## 8. 本轮只读保证

- **无新任务**：任务数读取前 6（stopped）→ 读取后 6（stopped），未变
- **无服务变更**：容器未启停/重启/替换，状态 Up 16 hours (healthy)
- **无代码/配置/state修改**：仅通过 GET API 和只读文件读取
- **无 SQLite 写入**：未使用 SQLite 连接（API 返回完整数据）
- **服务保持原状**：容器、state、配置均未修改

## 9. 待开发核查项

### 项1: L4 原因分组截断上限

`clock_discovery_v3.py:269` 中 `group_counts.get(rule, 0) >= 128` 对 L4 规则生效，导致 810 次 L4 通道访问仅生成 128 个原因分组。建议开发方确认：

- 128 上限是否合理
- L4 规则的 810 次访问中未入组的 682 次是否有有价值发现
- 是否影响前端展示的完整性

**只读复现命令**:

```
curl -s [http://127.0.0.1:18002/diagnostics/v3/tasks/diag-9785037f7a714c72a29624d3ba5ae74d/report](http://127.0.0.1:18002/diagnostics/v3/tasks/diag-9785037f7a714c72a29624d3ba5ae74d/report) | python3 -c "
import sys,json
d=json.load(sys.stdin)
disc=d.get('discovery',{})
print(f'complete={disc.get(\"complete\")}')
print(f'reason_codes={disc.get(\"reason_codes\")}')
print(f'channel_visits={disc.get(\"channel_visits\")}')
cg=disc.get('cause_groups',[])
from collections import Counter
print(f'cause_groups={len(cg)}, by_rule={dict(Counter(g.get(\"rule_id\") for g in cg))}')"
```

### 项2: BUS02 rec[4] 负收益

BUS02 rec[4] (prefix-3.2, path removal) status=negative, pp=-0.0050。移除 tool description 中的 path 导致 H 减少（2398848→2398400），P 也减少（3919732→3919318）但 H 下降比例更大。建议开发方确认负收益方案的展示和提示逻辑是否正确。

---

*补证时间: 2026-11-13*
*Service instance: 93ee2168-8219-403f-b35a-9039d0a5f57f*
*只读验证，无修改*