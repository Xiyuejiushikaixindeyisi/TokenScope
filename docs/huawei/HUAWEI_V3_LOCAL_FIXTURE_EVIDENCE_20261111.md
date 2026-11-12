# 华为五组业务取证说明：用于本地小样本重建与页面验收

2026-11-11。用途：由华为执行者对已有真实数据和已有诊断产物做定向探索，回传足以构造本地合成样本的结构与代码证据。此文已准备，尚未发送或现场执行；不是部署、产品修复、重跑全量或打包指令。

## 版本与范围

| 字段 | 值 |
| --- | --- |
| V3包版本 | tokenscope-v3-sample-20261111 |
| source_commit | cabf2c68d4d63eaeb24531b51ba4b3a2e2ad1ee0 |
| image_id | sha256:d6d9b5997c5f27e36dccc553db89679686c8c552210ac542ee56c57d382cb6f5 |
| bounded-runtime版本 | bounded-runtime-3.1 |
| 诊断API版本 | diagnostics-sampling-3 |
| 诊断报告版本 | diagnostics-report-3 |
| state隔离副本路径 | /mnt/sde/zhangxiyue/tokenscope-v3-r2-state-copy/ |
| 容器端口 | 127.0.0.1:18002->8000 |

### 五组诊断任务总览

| 编号 | 模型 | appid | base_run_id | 时间窗口(UTC) | parent_count | admitted | members | findings | comparisons | checked_requests | complete | stop_reason |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| BUS01 | DeepSeek-V4-Flash-0731 | S00000000000000000000000000000773 | cff76d1f | 07:00:00..08:00:00 | 569 | 569 | 512 | 32 | 8025 | 512 | False | PHASE_DEADLINE_EXHAUSTED |
| BUS02 | DeepSeek-V4-Flash-0731 | S010320 | cff76d1f | 07:40:00..08:10:00 | 397 | 397 | 397 | 23 | 6216 | 397 | False | PHASE_DEADLINE_EXHAUSTED |
| BUS03 | DeepSeek-V4-Flash-0731 | com.huawei.mbs.ilegal.ioc | cff76d1f | 07:00:00..08:00:00 | 400 | 400 | 400 | 16 | 5964 | 400 | False | PHASE_DEADLINE_EXHAUSTED |
| BUS04 | DeepSeek-V4-Flash-0731 | com.huawei.newalliance | cff76d1f | 07:00:20..08:43:44(无window) | 104 | 104 | 104 | 3 | 1392 | 104 | False | PHASE_DEADLINE_EXHAUSTED |
| BUS05 | Qwen3.6-27B | com.huawei.aidp_dg06 | ecd0d032 | 07:03:52..08:59:55(无window) | 171 | 171 | 171 | 7 | 2600 | 171 | False | PHASE_DEADLINE_EXHAUSTED |

reason_codes: BUS01-04=`EVIDENCE_BYTE_LIMIT`；BUS05=`CLOCK_TIME_UNSUPPORTED, EVIDENCE_BYTE_LIMIT`

### 发现统计

| 编号 | L1 clock (session-clock-normalize-3.1) | L1 dynamic (prefix-transform-3.2) | L3 prefix (prefix-transform-3.2) | L4 cause_groups | L5 cause_groups |
| --- | --- | --- | --- | --- | --- |
| BUS01 | 28 | 0 | 3 | 是(135 groups) | 未单独标注 |
| BUS02 | 19 | 0 | 3 | 是(13 groups) | 未单独标注 |
| BUS03 | 13 | 1 | 2 | 是(26 groups) | 未单独标注 |
| BUS04 | 3 | 0 | 0 | 是(17 groups) | 未单独标注 |
| BUS05 | 4 | 0 | 2 | 是(30 groups) | 未单独标注 |

### 评估状态

全部5组在 evaluation 阶段（model phase之后的逐finding评估循环）均因 `PHASE_DEADLINE_EXHAUSTED` 被强制终止（exit_code=-15, forced_termination=True）。evaluation-0001/discovery/ 目录下存在 before.sqlite3 和 after.sqlite3（部分组after为空或与before相同），但 **无 rows.json、plan.json 或 WindowEvaluation3 完整结果**。因此：

- **before/after P/H/C 聚合值缺失**
- **improvement_pp（收益百分点）缺失**
- **status 字段为 budget_exhausted（非 positive/negative/zero）**
- **recommendations 列表为空**（report 中 recommendations=[] ）

peak RSS / elapsed 统计：

| 编号 | supervisor_peak_rss_bytes | supervisor_elapsed_ms |
| --- | --- | --- |
| BUS01 | 1,655,382,016 (~1.54 GiB) | 400,604 ms |
| BUS02 | 1,669,599,232 (~1.56 GiB) | 300,017 ms |
| BUS03 | 1,078,902,784 (~1.00 GiB) | 240,855 ms |
| BUS04 | 383,184,896 (~365 MiB) | 108,282 ms |
| BUS05 | 612,102,144 (~584 MiB) | 142,827 ms |

---

## 五组证据

### BUS01: S00000000000000000000000000000773 × DeepSeek-V4-Flash-0731

#### 可追溯来源

- **base_run_id**: cff76d1f-24f5-481e-8efe-b93aa826b3fa
- **diag task_id**: diag-5385d0d92e8f41db985f6d9c39327076
- **prep_id**: prep-3fada9d730fd4f57941fb1944746c1af
- **submission_key**: bus01-1hr
- **时间窗口**: 2026-10-20 07:00:00..08:00:00 UTC (start_ns=1792479600000000000, end_ns=1792483200000000000)
- **sample_id**: sample:a616fc7c2af92c8c4f7fa9caa66c668ade57d1e6aeddb2b66ec186fabc1078ed
- **选择算法**: first-prefix-last-suffix-1
- **来自真实请求**: 是，原始请求存储于 prep job sample-1/discovery/ 目录，文件名 `{source_record_index}.raw`

#### 业务请求结构

代表性请求 idx=2409（L1 finding[0] 的 left）：

- **messages角色序列**: `[system, user]`（短请求）或 `[system, user, assistant, tool, assistant, tool, tool, ...]`（多轮请求）
- **system prompt位置**: messages[0].content，字符串类型，长度27,469字符
- **tools数量**: 44个工具
- **tool_names(前5)**: agent_profile, bash, edit, exa_web_fetch_exa, exa_web_search_exa
- **已有prompt Token数**: 约27,469字符的system prompt + 后续对话（LCP=9,075 tokens，即两请求在9,075个token处首次分叉）
- **clock字符位置**: 在system prompt中偏移24,156处

#### clock与其他字段

**clock标签完整内容**（idx=2409）：

```
<session_clock> ## 当前时间（本机时区：Asia/Shanghai） 2026/10/20 15:05:27 </session_clock>
```

- **clock字符区间**: start=24156, end=24220（82字符含标签）
- **日期区间**: start=24200, end=24219（19字符，即"2026/10/20 15:05:27"）
- **日期在clock标签内部**: 是
- **clock标签前80字符**: `...阮琴惠  ## 用户工号 r00812553  ## 邮箱 [ruanqinhui@huawei.com] </current_pedestal_user>  `
- **clock标签后80字符**: `<self_evolution_identity> 你是一个具有自进化能力的 AI 助手。你有跨 session 的持久记忆和技能管理系统。  ★ ★ ★ 你必`

**clock外部动态内容**（均在 `<env>` 块中，位于 clock 之前约23,000字符处）：

```
<env>
   Working directory: C:\Users\r00812553\.local\share\weclaw\workspace\default
   Workspace root folder: /
   Is directory a git repo: no
   Platform: win32
   Today's date: Tue Oct 20 2026
</env>
```

- `env` 块位置: 1233..1430
- `Today's date: Tue Oct 20 2026` 位置: 1394（**在 `<env>` 块内部，在 `<session_clock>` 之前**）
- 模型名 `内部模型-DeepSeek-V4-Flash-128K` 位置: 1045（在 `<env>` 之前）
- 路径 `C:\Users\r00812553\...` 位置: 在 `<env>` 块中

#### 现成自动发现和改法

**L1 Clock Finding[0]**：

| 字段 | 值 |
| --- | --- |
| finding_id | finding:ed09fd43511735c6e8c77c6410dfc78ae76072d6801fc3cc7c2a9e2a01d986b8 |
| rule_id | L1 |
| rule_version | clock-3.1 |
| recipe.version | session-clock-normalize-3.1 |
| recipe.discovery | automatic_l1 |
| recipe.logical_field | `["system",0,""]` |
| recipe.constant | NORMALIZED |
| recipe.business_effect | changes_time_awareness |
| comparison.left.source_record_index | 2409 |
| comparison.right.source_record_index | 2471 |
| comparison.difference_pointers | `['/messages/0/content']` |
| comparison.lcp_tokens | 9075 |
| left_locations[0].text_range | {start: 24171, end: 24220} |
| right_locations[0].text_range | {start: 24171, end: 24220} |
| left_date_ranges | [[{start: 24200, end: 24219}]] |
| right_date_ranges | [[{start: 24200, end: 24219}]] |
| before_fragments | `[" ## 当前时间（本机时区：Asia/Shanghai） 2026/10/20 15:05:46 "]` |
| after_fragments | `["NORMALIZED"]` |
| evidence_status | clock_change_and_input_difference |

- **plan/evaluation**: 缺失。report recommendations=[]，evaluation-0001/discovery/ 目录有 before/after sqlite3（52091/51199 rows），但无 rows.json/plan.json 完整评估。
- **改法说明**: recipe 将 `<session_clock>` 标签内的日期时间替换为常量 `NORMALIZED`。compile_clock_plan (clock_discovery_v3.py line 338-388) 生成 ModificationPlan，operations 列表中每个 operation 是一次 replacement（handler_version=3.1, source_operations_json={"block_indices": [...], "constant": "NORMALIZED"}）。evaluation 阶段会 encode before/after 两版请求，用 PrefixLedger 重放前缀命中，产出 before/after {p,h,c} 总数和 improvement_pp。该阶段超时未完成。

**L3 Prefix Finding[2]**：

| 字段 | 值 |
| --- | --- |
| rule_id | L3 |
| rule_version | prefix-3.2 |
| recipe.version | prefix-transform-3.2 |
| recipe.kind | dynamic_remove |
| comparison.difference_pointers | `['/tools/1/function/description']` |
| comparison.lcp_tokens | 635 |
| left source_record_index | 3534 |
| right source_record_index | 13408 |
| before_fragments | `Executes a given Windows PowerShell (5.1) command...Use \`C:\Users\w30016337\AppData\Local\Temp\opencode` for temporary work...` |
| after_fragments | `Executes a given Windows PowerShell (5.1) command...Use \`C:\Users\T30038~1\AppData\Local\Temp\opencode` for temporary work...` |

- **差异定位**: tools[1].function.description 中偏移393处的路径，`w30016337` vs `T30038~1`（用户名缩写 vs 8.3短名）
- **动态槽类型**: path（dynamic.py PATTERNS["path"] 匹配 `C:\...` 路径）
- **改法**: recipe.kind=dynamic_remove，移除该动态路径槽，保留其余文本不变

#### 关键实现证据

**日期识别**（timestamps.py line 6-13）：

```
DATE = re.compile(
    r"(?<!\d)(?P<year>\d{4})(?:-(?P<month>\d{1,2})-(?P<day>\d{1,2})"
    r"|/(?P<slash_month>\d{1,2})/(?P<slash_day>\d{1,2})"
    r"|年(?P<cn_month>\d{1,2})月(?P<cn_day>\d{1,2})日)"
    r"(?:(?:T|[ \t]+|(?<=日))(?P<hour>\d{1,2})(?::|时)(?P<minute>\d{2})"
    r"(?:(?::|分)(?P<second>\d{2})(?:\.\d{1,9})?秒?)?分?"
    r"(?P<zone>Z|[+-]\d{2}:?\d{2})?)?(?!\d)"
)
```

- 支持 `2026-10-20`、`2026/10/20`、`2026年10月20日` 三种日期格式
- 支持空格或T分隔的时间 `2026/10/20 15:05:27`
- `valid_timestamps()` (line 16-37) 验证日期合法性后返回 `(start, end, text)` 三元组

**clock定位**（session_clock_v3.py line 13-14, 39-78）：

```
OPEN, CLOSE, NORMALIZED = "<session_clock>", "</session_clock>", "NORMALIZED"
TAGS = re.compile(r"</?session_clock\b[^>]*>", re.IGNORECASE)
```

- `locate_clock_blocks(text)` (line 39): 先用 TAGS 正则找到所有开闭标签，验证配对且无嵌套 `<` `>`，再调用 `valid_timestamps(inner)` 提取内部日期。若 inner == "NORMALIZED" 则 dates=[]。若提取不到日期则返回 `CLOCK_TIME_UNSUPPORTED`。
- `clock_fields(body)` (line 98-128): 遍历 messages 中 role=system/developer 的消息，对每条 content（字符串或text parts），生成 `ClockField(logical_key, pointer, text, locate_clock_blocks(text))`。logical_key 格式为 `["system",ordinal,"relative"]`，pointer 为 `/messages/{index}/content{relative}`。

**L1/L3分类**（clock_discovery_v3.py line 153-327）：

```
# line 211-220: L1 clock finding via pair_clock()
for logical, after in fields[j].items():
    before = fields[i].get(logical)
    if before is None:
        continue
    finding = pair_clock(left, right, before, after, ids[i], ids[j])
    if finding:
        key = value_digest(finding.recipe.model_dump(mode="json"))
        if key not in findings:
            findings[key] = finding
        causes.append(("L1", finding.comparison.difference_pointers, key))

# line 230-241: L3 prefix finding via pair_prefix()
for prefix_finding in pair_prefix(left, right, x, y, comparison, input_changed=changed):
    ...
    causes.append((prefix_finding.rule_id, ..., signature))

# line 242-246: L3 tool map difference
xm = {} if x.get("tools") in (None, []) else tool_map(x)
ym = {} if y.get("tools") in (None, []) else tool_map(y)
if xm is not None and ym is not None:
    if xm != ym:
        causes.append(("L3", ("/tools",), value_digest([xm, ym])))
```

- L1 (ClockFinding3): rule_id=L1, rule_version=clock-3.1, recipe.version=session-clock-normalize-3.1
- L1 (PrefixFinding3): rule_id=L1, rule_version=prefix-3.2, recipe.version=prefix-transform-3.2 — 这是通过 `pair_prefix()` 发现的动态槽（在 clock_field 对应的 system prompt 中，但差异在 clock 块外部），规则标签 L1: 取自 `dynamic_fields()` 返回的 key[:2]
- L3 (PrefixFinding3): rule_id=L3, rule_version=prefix-3.2 — 包括 `pair_prefix()` 返回的 L3 动态槽差异，以及 clock_discovery_v3.py line 242-246 的 tool_map 差异

**评估阶段与超时**（clock_worker_v3.py line 99-153, evaluation_v3.py line 106-212, runtime_v3.py line 77-83）：

```
# clock_worker_v3.py line 99: 进入 model phase
atomic_json(root / "phase.json", {"phase": "model", "deadline": control.enter("model")})

# line 100-146: 逐 finding 循环，对每个 finding 做 discovery + review 两个角色的评估
for number, finding in enumerate(discovery.findings, 1):
    control.reserve("checkpoints", 8)
    item = {"finding": ..., "windows": []}
    for role in ("discovery", "review"):
        result = evaluate_window(window, finding, folder, control)  # 可能超时
        item["windows"].append(entry)
        publish(number * 2 + role_index)

# runtime_v3.py line 82-83: BudgetLedger.checkpoint() 检查 phase deadline
if self.stage_deadline is not None and time.monotonic() >= self.stage_deadline:
    raise TaskStopped("PHASE_DEADLINE_EXHAUSTED")
```

- model phase deadline 硬编码为 60,000ms（execution_v3.py line 84: `"model": 60000`）
- supervisor_v3.py line 128-129: out-of-process 监控也检查 phase.json 的 deadline
- 所有5组的 model phase deadline 均在约300秒处（phase.json中 deadline 值），但 supervisor 在 elapsed_ms 达到该值时强制 SIGTERM

**after_fragments="NORMALIZED"**（clock_discovery_v3.py line 149）：

```
after_fragments=tuple("NORMALIZED" for i in changed),
```

- before_fragments 是 clock 内部的原始日期文本（如 `" ## 当前时间（本机时区：Asia/Shanghai） 2026/10/20 15:05:46 "`）
- after_fragments 固定为 `"NORMALIZED"`，表示改法将日期替换为常量

#### 本地重建规格

**保持一致的部分**：

- system prompt 前2,344字符（`<env>` 块之前）：包含 agent 指令、工具使用说明、AGENTS.md 引用等
- `<env>` 块内的固定字段：`Workspace root folder: /`、`Is directory a git repo: no`、`Platform: win32`
- `<session_clock>` 标签结构及其内的 `## 当前时间（本机时区：Asia/Shanghai）` 前缀
- clock 块之后的全部内容（agent_identity、技能管理说明等）

**唯一变化字段**：

- `<session_clock>` 内部的日期时间：`2026/10/20 15:05:27` → `2026/10/20 15:05:46`（秒级变化）
- 每对请求的唯一变化是这个19字符的日期时间戳

**允许同时变化的无关历史**：

- 多轮请求的对话历史（assistant/tool 消息内容）不同，但不在 system prompt 中
- `<env>` 块中的 `Working directory` 路径和 `Today's date` 在不同用户间不同，但同一 base_run_id 内的同类请求通常使用同一用户的同一 session

**脱敏JSON骨架**（可直接解析）：

```
{
  "messages": [
    {
      "role": "system",
      "content": "<固定前缀约1200字符> You are powered by the model named <MODEL_NAME>. <固定中间约200字符> <env>\n   Working directory: <WORKDIR>\n   Workspace root folder: /\n   Is directory a git repo: no\n   Platform: win32\n   Today's date: Tue Oct 20 2026\n</env> <固定中间约22700字符> <session_clock> ## 当前时间（本机时区：Asia/Shanghai） <TIMESTAMP> </session_clock>  <固定后缀>"
    },
    {
      "role": "user",
      "content": "<用户请求>"
    }
  ],
  "tools": [
    {"type": "function", "function": {"name": "agent_profile", "description": "..."}},
    {"type": "function", "function": {"name": "bash", "description": "Executes a given Windows PowerShell (5.1) command... Use `C:\\Users\\<USERNAME>\\AppData\\Local\\Temp\\opencode` for temporary work..."}},
    {"type": "function", "function": {"name": "edit", "description": "..."}},
    "..."
  ]
}
```

**确定性填充方法**：

- `MODEL_NAME`: 固定为 `内部模型-DeepSeek-V4-Flash-128K`（BUS01专用）
- `WORKDIR`: 用占位 `C:\Users\USER001\.local\share\weclaw\workspace\default`
- `TIMESTAMP`: 用种子生成 `2026/10/20 HH:MM:SS`，每对请求仅秒级不同
- `USERNAME` 在工具描述中：用占位 `USER001` vs `USER001~1`（8.3短名变体）
- 原始system prompt长度: 27,469字符；脱敏后预期: 约27,469字符（用户名占位长度一致）
- `<session_clock>` 内日期区间: 19字符

**预期页面事实**：

- V2 L1卡片应显示: 双边请求（idx=2409 vs idx=2471），差异在 `/messages/0/content`，具体改法为将 clock 内日期替换为 NORMALIZED
- LCP=9,075 tokens，说明约9,075个token的system prompt前缀在两个请求间完全共享，仅clock内日期不同
- **收益缺失**: 5组均无完整 evaluation，不得预设正值

---

### BUS02: S010320 × DeepSeek-V4-Flash-0731

#### 可追溯来源

- **diag task_id**: diag-581709eae9e941d5a2f4c247178c9ae7
- **prep_id**: prep-1f7f204303ab4673b5bba60d6d83747e
- **submission_key**: bus02-30min
- **时间窗口**: 2026-10-20 07:40:00..08:10:00 UTC (30分钟窗口)

#### 业务请求结构

代表性请求 idx=9785（L1 finding[0] left）：

- **messages角色序列**: `[system, user, assistant, tool, tool, assistant, tool, tool, ...]`
- **system prompt**: 23,268字符
- **tools数量**: 40个
- **tool_names(前5)**: agent_profile, bash, edit, glob, grep

#### clock与其他字段

**clock标签完整内容**（idx=9785）：

```
<session_clock> ## 当前时间（本机时区：Asia/Shanghai） 2026/10/20 15:44:58 </session_clock>
```

- **clock字符区间**: start=16063, end=16127
- **日期区间**: start=16107, end=16126（19字符）
- **日期在clock标签内部**: 是
- **clock前80字符**: `...媛  ## 用户工号 w00550859  ## 邮箱 [wanghaiyuan2@huawei.com] </current_pedestal_user>  `
- **clock后80字符**: `<agent_identity> ## 你的名字/岗位 RPA创建华为供应商协议全流程配置  ## 人格 -- 你是谁 （未设置） </agent_identi`

**env块** (位置1235..1432): `Working directory: C:\Users\w00550859\...  Today's date: Tue Oct 20 2026`
**模型名**: `DeepSeek-V4-Flash`（位置1045，在env之前）

#### 现成自动发现

**L1 Clock Finding[0]**: L.idx=9785, R.idx=12177, lcp_tokens=6527, diff=`/messages/0/content`, before=`" ## 当前时间（本机时区：Asia/Shanghai） 2026/10/20 15:46:55 "`, after=`"NORMALIZED"`

**L3 Prefix Finding[2]**: L.idx=9688, R.idx=18297, lcp_tokens=583, diff=`/tools/1/function/description`, kind=dynamic_remove

- **plan/evaluation**: 缺失。after.sqlite3 为空（0 rows），说明评估刚启动就被强制终止。

#### 本地重建规格

- 与BUS01结构相同，但 system prompt 更短（23,268字符），tools数量不同（40个）
- `<session_clock>` 位置偏移约16,063（在 system prompt 末尾区域）
- 变化字段: clock内日期 `2026/10/20 15:44:58` → `2026/10/20 15:46:55`
- MODEL_NAME: `DeepSeek-V4-Flash`（不带-128K后缀）
- 脱敏后预期长度: 约23,268字符

---

### BUS03: com.huawei.mbs.ilegal.ioc × DeepSeek-V4-Flash-0731

#### 可追溯来源

- **diag task_id**: diag-366a056a73194bd194b3c3b42d9914b3
- **prep_id**: prep-4beb98aa81e9498fbff3e1aadaa6cca8
- **submission_key**: bus03-1hr
- **时间窗口**: 2026-10-20 07:00:00..08:00:00 UTC

#### 业务请求结构

代表性请求 idx=13150（L1 finding[0] left）：

- **system prompt**: 37,222字符
- **tools数量**: 40个
- **tool_names(前5)**: agent_profile, bash, edit, glob, grep

#### clock与其他字段

**clock标签完整内容**（idx=13150）：

```
<session_clock> ## 当前时间（本机时区：Asia/Shanghai） 2026/10/20 15:56:41 </session_clock>
```

- **clock字符区间**: start=22348, end=22412
- **日期区间**: start=22392, end=22411

#### 现成自动发现

**L1 Clock Finding[0]**: L.idx=13150, R.idx=16369, lcp_tokens=9249, before=`" ## 当前时间（本机时区：Asia/Shanghai） 2026/10/20 15:56:54 "`, after=`"NORMALIZED"`

**L1 Dynamic Finding[3]** (关键矛盾点):

| 字段 | 值 |
| --- | --- |
| rule_id | L1 |
| rule_version | **prefix-3.2** (非clock-3.1) |
| recipe.version | prefix-transform-3.2 |
| recipe.kind | dynamic_remove |
| recipe.slot_key | `L1:["system",0,""]` |
| comparison.difference_pointers | `['/messages/0/content']` |
| comparison.lcp_tokens | 1016 |
| L.idx | 141 |
| R.idx | 16771 |
| before_fragments | `"You are an AI agent powered by DeepSeek Harness. You are a coding agent powered by the DeepSeek-V4-Flash model. ...Your working directory is /workspace/llm4search-runs/dsh-real-campaign/meta_workspaces/D0211/step-000003821-1."` |
| after_fragments | `"You are an AI agent powered by DeepSeek Harness. You are a coding agent powered by the DeepSeek-V4-Flash model. ...Your working directory is /workspace/llm4search-runs/dsh-real-campaign/workspaces/frozen_evox/C0212/generation-001."` |

- **这是 PrefixFinding3，不是 ClockFinding3**: rule_version=prefix-3.2，recipe.kind=dynamic_remove
- **差异位置**: system prompt 末尾的工作目录路径（`/workspace/llm4search-runs/dsh-real-campaign/meta_workspaces/D0211/step-000003821-1` vs `/workspace/llm4search-runs/dsh-real-campaign/workspaces/frozen_evox/C0212/generation-001`）
- **这两个请求没有 `<session_clock>` 标签**: idx=141 和 idx=16771 的 system prompt 仅4,567/4,572字符，是另一类 agent（DeepSeek Harness 直接编程 agent），无 clock 标签
- **动态槽类型**: path（`/workspace/llm4search-runs/...` 路径），通过 `slots_in_text()` 匹配

**L3 Prefix Finding[5]**: L.idx=6, R.idx=16151, lcp_tokens=637, diff=`/tools/1/function/description`, kind=dynamic_remove

- **plan/evaluation**: 缺失。

#### 本地重建规格

BUS03 包含两类请求：

1. **带clock的长请求**（~37,222字符，40个tools）: clock内日期变化
2. **不带clock的短请求**（~4,567字符，25个tools）: 末尾工作目录路径变化

- 变化字段类别1: clock内日期 `2026/10/20 15:56:41` → `2026/10/20 15:56:54`
- 变化字段类别2: 工作目录路径 `/workspace/llm4search-runs/.../meta_workspaces/D0211/step-000003821-1` vs `/workspace/llm4search-runs/.../workspaces/frozen_evox/C0212/generation-001`
- 短请求的 system prompt 无 `<session_clock>`、无 `<env>` 块，以 `You are an AI agent powered by DeepSeek Harness.` 开头

---

### BUS04: com.huawei.newalliance × DeepSeek-V4-Flash-0731

#### 可追溯来源

- **diag task_id**: diag-b5c2309f8935452dbaf892eeb41cf67c
- **prep_id**: prep-13877ca086c8408d8a370c674786a83e
- **submission_key**: bus04
- **时间窗口**: 无window参数（全量），members时间跨度 07:00:20..08:43:44 UTC

#### 业务请求结构

代表性请求 idx=13198（L1 finding[0] left）：

- **system prompt**: 18,892字符
- **tools数量**: 40个
- **tool_names(前5)**: agent_profile, bash, edit, glob, grep

#### clock与其他字段

**clock标签完整内容**（idx=13198）：

```
<session_clock> ## 当前时间（本机时区：Asia/Shanghai） 2026/10/20 15:49:32 </session_clock>
```

- **clock字符区间**: start=14645, end=14709
- **日期区间**: start=14689, end=14708

**env块** (位置1238..1435): `Working directory: C:\Users\w60136099\...  Today's date: Tue Oct 20 2026`
**模型名**: `DeepSeek-V4-Flash-64k`（位置1045，**在env之前，clock之外**）

#### 现成自动发现

**全部3个finding均为L1 clock** (rule_id=L1, rule_version=clock-3.1, recipe.version=session-clock-normalize-3.1):

| # | L.idx | R.idx | lcp_tokens | before_fragment |
| --- | --- | --- | --- | --- |
| 0 | 13198 | 14823 | 6019 | `## 当前时间（本机时区：Asia/Shanghai） 2026/10/20 15:52:24` |
| 1 | 9508 | 10779 | 6019 | `## 当前时间（本机时区：Asia/Shanghai） 2026/10/20 15:43:20` |
| 2 | 107 | 7592 | 6019 | `## 当前时间（本机时区：Asia/Shanghai） 2026/10/20 15:27:17` |

- **所有finding的目标均为 `/messages/0/content`，具体为 `<session_clock>` 内的日期时间**
- **无L3 finding**: BUS04仅有3个L1 clock finding，无prefix/dynamic finding
- **plan/evaluation**: 缺失。

#### 本地重建规格

- system prompt: 18,892字符
- 变化字段: 仅clock内日期 `2026/10/20 HH:MM:SS` 变化
- MODEL_NAME: `DeepSeek-V4-Flash-64k`
- tools: 40个

---

### BUS05: com.huawei.aidp_dg06 × Qwen3.6-27B

#### 可追溯来源

- **diag task_id**: diag-8ec574ef43304aef8132f6179764b7bf
- **prep_id**: prep-3fe8c6feff364c7c864b3543d7b16bed
- **submission_key**: bus05
- **base_run_id**: ecd0d032-bbb3-4b37-ba65-fa517edc7c25（Qwen run）
- **时间窗口**: 无window参数（全量），members时间跨度 07:03:52..08:59:55 UTC

#### 业务请求结构

代表性请求 idx=48744（L1 finding[0] left）：

- **system prompt**: 17,982字符
- **tools数量**: 40个
- **tool_names(前5)**: agent_profile, bash, edit, glob, grep

#### clock与其他字段

**clock标签完整内容**（idx=48744）：

```
<session_clock> ## 当前时间（本机时区：Asia/Shanghai） 2026/10/20 15:27:29 </session_clock>
```

- **clock字符区间**: start=14883, end=14947
- **日期区间**: start=14927, end=14946

**env块** (位置1236..1433): `Working directory: C:\Users\z00618554\...  Today's date: Tue Oct 20 2026`
**模型名**: `Qwen3`（位置1045）

#### 现成自动发现

**L1 Clock Finding[0]**: L.idx=48744, R.idx=52408, lcp_tokens=18855, before=`" ## 当前时间（本机时区：Asia/Shanghai） 2026/10/20 15:29:22 "`, after=`"NORMALIZED"`

**L3 Prefix Finding[3]**: L.idx=207276, R.idx=291884, lcp_tokens=570, diff=`/tools/1/function/description`, kind=dynamic_remove

- 差异: 路径 `C:\Users\Z00843~1\AppData\...` vs `C:\Users\H00967~1\AppData\...`

**L3 Prefix Finding[6]**: L.idx=9783, R.idx=245692, lcp_tokens=483, diff=`/tools/1/function/description`, kind=dynamic_remove

- 差异: 路径 `C:\Users\y00584087\AppData\...` vs `C:\Users\L84291~1\AppData\...`
- **plan/evaluation**: 缺失。
- **额外 reason_code**: `CLOCK_TIME_UNSUPPORTED`（部分请求的 clock 内日期格式不被支持，可能为 `2026/10/20 15:27:29` 中的斜杠格式在某些场景下不被识别——但实际 timestamps.py 支持斜杠格式，此 code 更可能来自其他请求的异常 clock 结构）

#### 本地重建规格

- system prompt: 17,982字符
- 变化字段: clock内日期 `2026/10/20 HH:MM:SS` 变化
- MODEL_NAME: `Qwen3`
- tools: 40个
- LCP=18,855 tokens（BUS05的system prompt最短，但LCP最高，说明Qwen请求间的对话历史变化更大）

---

## 三处矛盾核验

### 矛盾1: BUS04报告称模型名/路径也被NORMALIZED

**核验结论: 不成立。**

BUS04的全部3个finding均为 `rule_id=L1, rule_version=clock-3.1, recipe.version=session-clock-normalize-3.1`，recipe.logical_field=`["system",0,""]`，difference_pointers=`['/messages/0/content']`，before_fragments 均为 clock 内日期时间（如 `" ## 当前时间（本机时区：Asia/Shanghai） 2026/10/20 15:52:24 "`），after_fragments 均为 `"NORMALIZED"`。

- **模型名** `DeepSeek-V4-Flash-64k` 位于 system prompt 偏移1045处，在 `<env>` 块之前
- **路径** `C:\Users\w60136099\...` 位于 `<env>` 块中（偏移1246附近）
- **clock块** 位于偏移14645处
- 三者均在 clock 块外部，recipe 的 block_indices 仅指向 clock 内部的日期区间

recipe.kind 为 None（ClockFinding3 没有 kind 字段），recipe.constant="NORMALIZED" 仅替换 `<session_clock>` 标签内的日期，不触及外部模型名或路径。compile_clock_plan (clock_discovery_v3.py line 349-354) 中 `normalize_clock(field, recipe)` 仅对 `field.logical_key == recipe.logical_field` 且 `clock_shape(field.text, blocks) == recipe.field_shape` 的字段生效，替换 `block.inner_start..block.inner_end` 区间。

### 矛盾2: BUS03报告把 /messages/0/content 列为L3

**核验结论: 需要区分 BUS03 中的两种 finding。**

BUS03 finding[3] 的 `rule_id=L1`，但 `rule_version=prefix-3.2`（非 clock-3.1），`recipe.version=prefix-transform-3.2`，`recipe.kind=dynamic_remove`。这是一个 **PrefixFinding3**（通过 `pair_prefix()` 发现），不是 ClockFinding3。

- `pair_prefix()` (prefix_findings_v3.py line 97-188) 返回的 finding 使用 `rule_id=cast(Literal["L1","L2","L3"], rule)`，其中 `rule = key[:2]`，key 来自 `dynamic_fields(body)` 返回的字典键
- `dynamic_fields()` (prefix_findings_v3.py line 56-64) 对 clock_fields 的结果使用 `"L1:" + f.logical_key` 作为键
- 因此 finding[3] 的 rule_id=L1 表示 **该动态槽在 system prompt（L1 = system/developer 角色）中发现**，但差异类型是 prefix-transform（路径变化），不是 clock-normalize

BUS03 finding[3] 的 difference_pointers=`['/messages/0/content']`，但 text_range=None（PrefixFinding3 的 Location 不设 text_range），before/after_fragments 展示的是 system prompt 全文（含末尾工作目录路径差异）。

**与 BUS03 finding[0] 的区别**: finding[0] rule_version=clock-3.1（ClockFinding3，clock内日期变化），finding[3] rule_version=prefix-3.2（PrefixFinding3，clock外路径变化）。两者都指向 `/messages/0/content`，但改法完全不同。

### 矛盾3: 英文日期 Tue Oct 20 2026 的归属

**核验结论: 在 clock 外部，属于 `<env>` 块内容，不是 clock 内部日期。**

所有5组BUS的 system prompt 中，`Today's date: Tue Oct 20 2026` 位于 `<env>` 块内部，偏移约1394-1414处。`<env>` 块在 system prompt 前部（偏移1233-1450），远早于 `<session_clock>` 块（偏移14,645-24,156处）。

- `Tue Oct 20 2026` 是 `<env>` 块中的英文日期格式，被 env 标签包裹
- `<session_clock>` 内部的日期是中文格式 `2026/10/20 15:05:27`（Asia/Shanghai 时区）
- 代码中 `locate_clock_blocks()` 仅扫描 `<session_clock>` 标签内部的内容，不扫描 `<env>` 块
- `valid_timestamps()` 的 DATE 正则支持 `2026/10/20 15:05:27` 格式（斜杠分隔），也支持 `2026-10-20` 和 `2026年10月20日`
- `Tue Oct 20 2026` 这种英文月份格式 **不被** `valid_timestamps()` 的 DATE 正则匹配（正则要求 `\d{4}[-/]` 开头），因此它不会出现在 date_ranges 中

**当前代码不支持识别 `<env>` 块中的英文日期作为动态字段**。`dynamic_fields()` 中的 `slots_in_text()` 会匹配 timestamp 和 path 类型的动态槽，但 `Tue Oct 20 2026` 不匹配 timestamp 正则（`r'\b\d{4}-\d{2}-\d{2}...'`），也不匹配 path 正则。因此该字段不在任何 finding 的改法目标中。

---

## 本地合成重建规格

### 通用骨架

所有5组BUS的 system prompt 共享以下结构（位置和长度因组而异）：

```
[固定前缀 ~1000字符: agent指令、模型名声明]
<env>
   Working directory: <动态-路径>
   Workspace root folder: /
   Is directory a git repo: no
   Platform: win32
   Today's date: <动态-英文日期，但代码不识别>
</env>
[固定中间部分 ~12000-22000字符: 用户信息、agent_identity、技能管理等]
<session_clock> ## 当前时间（本机时区：Asia/Shanghai） <动态-中文日期时间> </session_clock>
[固定后缀: self_evolution_identity 等]
```

### 每组的"保持一致/唯一变化/允许同时变化"表

| 编号 | 保持一致 | 唯一变化字段 | 允许同时变化的无关历史 |
| --- | --- | --- | --- |
| BUS01 | system prompt前缀(~24156字符) + clock后缀 + tools定义(除desc中路径) | clock内日期时间(19字符) | 对话历史(assistant/tool消息) |
| BUS02 | system prompt前缀(~16063字符) + clock后缀 + tools定义(除desc中路径) | clock内日期时间(19字符) | 对话历史 |
| BUS03(长) | system prompt前缀(~22348字符) + clock后缀 + tools定义 | clock内日期时间(19字符) | 对话历史 |
| BUS03(短) | system prompt前缀(~4000字符) | 末尾工作目录路径 | 对话历史 |
| BUS04 | system prompt前缀(~14645字符) + clock后缀 + tools定义 | clock内日期时间(19字符) | 对话历史 |
| BUS05 | system prompt前缀(~14883字符) + clock后缀 + tools定义(除desc中路径) | clock内日期时间(19字符) | 对话历史 |

### 可直接解析的脱敏JSON骨架（通用版）

```
{
  "messages": [
    {
      "role": "system",
      "content": "<PREFIX_1000_CHARS> You are powered by the model named <MODEL_NAME>. <MIDDLE_200_CHARS> <env>\n   Working directory: C:\\Users\\<USER_ID>\\.local\\share\\weclaw\\workspace\\default\n   Workspace root folder: /\n   Is directory a git repo: no\n   Platform: win32\n   Today's date: Tue Oct 20 2026\n</env> <MIDDLE_12000_TO_22000_CHARS> <session_clock> ## 当前时间（本机时区：Asia/Shanghai） <DATE_2026/10/20_SPACE_TIME_HH:MM:SS> </session_clock>  <SUFFIX>"
    },
    {
      "role": "user",
      "content": "<USER_REQUEST>"
    }
  ],
  "tools": [
    {"type": "function", "function": {"name": "agent_profile", "description": "<FIXED_DESC>"}},
    {"type": "function", "function": {"name": "bash", "description": "Executes a given Windows PowerShell (5.1) command... Use `C:\\Users\\<USER_ID>\\AppData\\Local\\Temp\\opencode` for temporary work..."}},
    {"type": "function", "function": {"name": "edit", "description": "<FIXED_DESC>"}},
    {"type": "function", "function": {"name": "glob", "description": "<FIXED_DESC>"}},
    {"type": "function", "function": {"name": "grep", "description": "<FIXED_DESC>"}}
  ]
}
```

### 确定性填充方法

| 占位符 | 填充规则 | 原始长度 | 脱敏后长度 |
| --- | --- | --- | --- |
| `<MODEL_NAME>` | 按组固定: BUS01=`内部模型-DeepSeek-V4-Flash-128K`, BUS02/03=`DeepSeek-V4-Flash`, BUS04=`DeepSeek-V4-Flash-64k`, BUS05=`Qwen3` | 各组实际值 | 同长 |
| `<USER_ID>` | 用 `USER001`/`USER002` 等占位，保持8位长度 | 8-10字符 | 8字符 |
| `<DATE_2026/10/20_SPACE_TIME_HH:MM:SS>` | 种子: `2026/10/20 15:05:27` → `2026/10/20 15:05:46`（秒级变化） | 19字符 | 19字符 |
| `<PREFIX_1000_CHARS>` | 固定文本，不需脱敏 | ~1000字符 | 同长 |
| `<MIDDLE_*_CHARS>` | 固定文本，用户名/邮箱用占位 | 12000-22000字符 | 同长 |
| `<SUFFIX>` | 固定文本 | ~500字符 | 同长 |
| bash desc中的`<USER_ID>` | 同上占位 | 嵌入desc中文 | 同长 |

**区间发生变化须重算**: 脱敏替换用户名时，若占位长度与原值不同，则 clock 块位置（偏移量）和 date_range（start/end）需重新计算。建议占位长度与原始用户名长度一致（8字符）。

---

## 已知缺口

1. **evaluation 缺失**: 5组均无完整 evaluation（before/after P/H/C 聚合值、improvement_pp、status）。evaluation-0001/discovery/ 目录下有 before/after sqlite3，但无 rows.json 和 plan.json。5组均在 model phase 的 finding 评估循环中被 PHASE_DEADLINE_EXHAUSTED 终止。
2. **recommendations 为空**: 所有5组的 report-0000.json 中 recommendations=[]，因 evaluation 未完成，无 plan/evaluation 结果可附。
3. **discovery 不完整**: 所有5组 complete=False，reason_codes 包含 EVIDENCE_BYTE_LIMIT（5组均有）和 CLOCK_TIME_UNSUPPORTED（仅BUS05）。部分请求的比较和发现可能被截断。
4. **L4/L5 cause_groups 存在但无 finding**: clock_discovery_v3.py 在 line 247-260 检测 L4（history_differences）和 L5（representation_differences），这些作为 cause_groups 记录但不生成独立 finding。L4 在所有5组中均有出现，指向 `/messages/N/content`（对话历史差异）。
5. **BUS05 的 CLOCK_TIME_UNSUPPORTED**: 部分请求的 clock 内日期格式不被支持，可能导致部分比较被跳过。timestamps.py 的 DATE 正则支持 `2026/10/20`（斜杠格式），但若有其他格式（如纯中文无数字、或不完整时间戳）则会被拒绝。
6. **Tue Oct 20 2026 不在改法目标中**: `<env>` 块中的英文日期 `Today's date: Tue Oct 20 2026` 不被 valid_timestamps() 识别，不在任何 finding 的修改目标中。但它确实在每次请求中可能不同（不同日期），且位于前缀缓存的关键前部区域。
7. **模型名和路径不在改法目标中**: 模型名（如 `DeepSeek-V4-Flash-64k`）和工作目录路径（如 `C:\Users\w60136099\...`）在 system prompt 中是静态的（同一 base_run_id 内不变），因此不产生 finding。但跨 base_run_id（不同用户/不同 session）时，这些字段会不同，可能导致前缀缓存未命中——这在 L3 prefix finding 中通过 tools[1].function.description 的路径差异间接体现。
8. **BUS04 无 L3 finding**: BUS04 仅产出3个L1 clock finding，无 prefix/dynamic finding。可能原因: parent_count=104 较小，comparison 次数=1392，在 EVIDENCE_BYTE_LIMIT 前未能发现工具描述路径差异。或该 appid 的请求集工具描述路径一致。
9. **evaluation sqlite3 状态不一致**: BUS02 的 after.sqlite3 为0行（评估刚启动即被终止），BUS03 的 before/after 行数相同（55595行，可能未执行任何修改），BUS01/04/05 的 before/after 行数不同（部分执行了修改但未完成）。

---

## 取证脚本核心选择和提取逻辑

以下脚本仅读取已有诊断产物和原始请求数据，不写产品 state，不改服务/源码/配置。

```
#!/usr/bin/env python3
"""取证脚本：从已有 V3 诊断产物中提取五组业务证据"""
import json, os, re, sqlite3
from pathlib import Path

STATE_ROOT = "/mnt/sde/zhangxiyue/tokenscope-v3-r2-state-copy/diagnostics-v3/jobs"

BUS_MAP = {
    "BUS01": "diag-5385d0d92e8f41db985f6d9c39327076",
    "BUS02": "diag-581709eae9e941d5a2f4c247178c9ae7",
    "BUS03": "diag-366a056a73194bd194b3c3b42d9914b3",
    "BUS04": "diag-b5c2309f8935452dbaf892eeb41cf67c",
    "BUS05": "diag-8ec574ef43304aef8132f6179764b7bf",
}

def extract_finding(finding):
    """提取 finding 的关键字段"""
    comp = finding.get("comparison", {})
    recipe = finding.get("recipe", {})
    return {
        "rule_id": finding.get("rule_id"),
        "rule_version": finding.get("rule_version"),
        "recipe_version": recipe.get("version"),
        "recipe_kind": recipe.get("kind"),
        "recipe_discovery": recipe.get("discovery"),
        "recipe_logical_field": recipe.get("logical_field"),
        "diff_pointers": comp.get("difference_pointers", []),
        "lcp_tokens": comp.get("lcp_tokens"),
        "left_idx": comp.get("left", {}).get("source_record_index"),
        "right_idx": comp.get("right", {}).get("source_record_index"),
        "before_fragments": finding.get("before_fragments", []),
        "after_fragments": finding.get("after_fragments", []),
        "left_date_ranges": finding.get("left_date_ranges", []),
        "right_date_ranges": finding.get("right_date_ranges", []),
    }

def extract_request_structure(raw_path):
    """从 .raw 文件提取请求结构"""
    with open(raw_path) as f:
        body = json.load(f)
    sys_content = body["messages"][0]["content"] if body.get("messages") else ""
    cs = sys_content.find("<session_clock>")
    ce = sys_content.find("</session_clock>")
    env_match = re.search(r"<env>(.*?)</env>", sys_content, re.DOTALL)
    model_match = re.search(r"powered by the model named ([^\n.<]+)", sys_content)
    today_match = re.search(r"Today's date:?\s+(\w{3} \w{3} \d{1,2} \d{4})", sys_content)
    return {
        "sys_len": len(sys_content),
        "msg_count": len(body.get("messages", [])),
        "tool_count": len(body.get("tools", [])),
        "tool_names": [t.get("function", {}).get("name") for t in body.get("tools", []) if isinstance(t, dict) and t.get("type") == "function"][:5],
        "clock_pos": (cs, ce + 18) if cs >= 0 else None,
        "clock_content": sys_content[cs:ce+18] if cs >= 0 else None,
        "env_block": env_match.group(1) if env_match else None,
        "model_name": model_match.group(1) if model_match else None,
        "today_date": today_match.group(1) if today_match else None,
    }

for bus, diag_id in BUS_MAP.items():
    diag_dir = Path(STATE_ROOT) / diag_id
    # 读取 findings
    with open(diag_dir / "findings.json") as f:
        findings_data = json.load(f)
    findings = findings_data if isinstance(findings_data, list) else findings_data.get("findings", [])
    # 读取 job.json 获取 prep_id
    with open(diag_dir / "job.json") as f:
        job = json.load(f)
    prep_id = job.get("sample_preparation_id")
    prep_dir = Path(STATE_ROOT) / prep_id / "sample-1" / "discovery"
    # 提取前3个 finding 的详情
    for i, finding in enumerate(findings[:3]):
        info = extract_finding(finding)
        left_raw = prep_dir / f"{info['left_idx']}.raw"
        right_raw = prep_dir / f"{info['right_idx']}.raw"
        if left_raw.exists():
            info["left_structure"] = extract_request_structure(left_raw)
        if right_raw.exists():
            info["right_structure"] = extract_request_structure(right_raw)
        print(f"{bus} finding[{i}]: {json.dumps(info, ensure_ascii=False, indent=2)}")
```

**执行命令**:

```
python3 extract_evidence.py > evidence_output.txt 2>&1
```

---

*本文档基于 tokenscope-v3-sample-20261111 包的诊断产物（state隔离副本 /mnt/sde/zhangxiyue/tokenscope-v3-r2-state-copy/）和 V3 源码（source_commit cabf2c68）编写。所有 findings 数据、raw 请求文件、源码行号均来自实际产物，非推断。evaluation 缺失是 bounded-runtime-3.1 的 PHASE_DEADLINE_EXHAUSTED 机制导致的产品限制，非用户要求。*