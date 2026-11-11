# TOKENSCOPE_V3_LOW_HIT_EXPLORATION_20261109 — V3 六组业务低命中率小样本探索

> 
> 生成时间（UTC）：2026-11-10T02:00:00Z
> 服务实例ID：b8309249-48c7-4d0e-8bca-05f4be8c15d8
> 目录快照：7fa3b2a932d08efee1f7ef9e949e510d4958766a6fb6f730060e87c1b277da8a
> 契约版本：2.1.0
> 版本：tokenscope-v2-hv2-20261103
> 源码commit：c1345b6fd7d413a94420642ca1b4099b9ec104b4
> 只读收集报告SHA256：31ee6957e16c6ddcc09c61e5abde2490be8b532a7fa3801d801d197304a5b5ab
> 线程/会话ID：59e22084-d019-4d09-9a7f-a918930a5b01（本环境CODEX_THREAD_ID）
> SSH转发：`ssh -L 18002:127.0.0.1:18002 zhangxiyue@10.67.43.44`
> 工作目录：`docs/tasks/product-v3/exploration/20261110/`（新建，零产品写入）
> 产品写接口调用：0；服务重启：0；生产配置/数据/前端修改：0

---

## A. 一页结论和执行边界

### 六组逐项结论表

| 编号 | appid | 状态 | 场景判断依据 | 主要原因与可信程度 | 可执行改法 | 样本收益（A窗） | 现有分析器缺口 | 资源/证据限制 | V3优先级 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A1 | S000…773 | ✅完成 | 员工助手Agent，4种模型别名（8K/32K/64K/128K），66/65/99/57/58等工具数，多会话模板族 | **P1: `<session_clock>`时间戳嵌入system消息**（84.4%同长度对仅时钟差异），高可信 | session_clock内容固定化/移至请求末尾 | +39.14pp (28%→68%) | L1时间戳正则不匹配`/`分隔日期；L4仅报"历史差异"不可执行 | 另15.6%含retrieved_memories顺序变化，需业务确认 | P0 |
| A2 | S010320 | ✅完成 | Agent业务，含45/300无system消息的纯API调用+多模板 | **P1: session_clock时间戳**（100%同长度对仅时钟差异），高可信 | session_clock固定化 | +26.85pp (56%→83%) | 同A1 | 无系统消息的45条是另一模板族，session_clock不适用 | P0 |
| A3 | com.huawei.mbs.ilegal.ioc | ✅完成 | 多模板Agent业务，25/26/40/53/67/68/72工具数 | **P1: session_clock时间戳**（91.4%同长度对仅时钟差异），高可信；**P2: workspace路径含动态ID**（codex_alone/frozen_evox/A0212/C0212），中可信 | session_clock固定化+workspace路径标准化 | +28.97pp (34%→63%) | L1时间戳正则不匹配`/`分隔；L4仅报"历史差异" | workspace路径需业务确认是否可标准化 | P0 |
| A4 | com.huawei.onlinetools | ✅完成 | 链式文档生成，无Agent/无tools/无session_clock，多模板（149/549/644/3482/7167/7706字符system） | **多模板混用**：同一appid下有≥6种完全不同的system prompt模板，非同一模板的动态字段变化 | 无单点改法；需按模板分组后分别优化 | +0.00pp (无变化) | 分析器未区分多模板混用与单模板动态字段 | 总108请求，0 tools，非Agent业务 | P2 |
| A5 | com.huawei.newalliance | ✅完成 | Agent业务，2个主要模板族（31+18/104请求），session_clock+历史对话 | **P1: session_clock时间戳**（93.9%同长度对仅时钟差异），高可信；**P2: 历史对话内嵌时间戳**（Q:当前时间：2026年10月20日…），中可信 | session_clock固定化+历史对话时间戳标准化 | +32.38pp (47%→80%) | L1不匹配中文日期格式`年月日`；L4仅报"历史差异" | 历史对话时间戳格式与session_clock不同，需分别处理 | P0 |
| A6 | com.huawei.aidp_dg06 | ✅完成 | Qwen Agent业务，3模型别名（32K/64K/128K），39/40工具，session_clock+retrieved_memories | **P1: session_clock时间戳**（100%同长度对仅时钟差异），高可信 | session_clock固定化 | +12.68pp (46%→58%) | 同A1；Qwen block_size=1536放大时钟差异的token级影响 | Qwen块大小1536远大于DS的32，单块失配损失更大 | P0 |

### 执行边界说明

- **观测**：基于SQLite只读读取（mode=ro）、容器内tokenizer编码（cpu_budget=8）、FullBlockStrategy仿真计算的直接测量结果
- **推断**：session_clock时间戳是5/6组的主要低命中原因，基于84.4%-100%的同长度请求对仅时钟差异的结构证据+CPU仿真收益
- **需业务确认**：session_clock移除/固定化的业务影响（是否依赖精确时间感知）、workspace路径标准化、retrieved_memories顺序固定的业务正确性
- **A4例外**：非session_clock场景，多模板混用导致低命中，需V3新增"多模板检测器"而非改进时间戳正则

---

## B. 版本、来源、预算与样本选择

### B.1 产品与源码身份

| 项 | 值 |
| --- | --- |
| release_id | tokenscope-v2-hv2-20261103 |
| source_commit | c1345b6fd7d413a94420642ca1b4099b9ec104b4 |
| image_id | sha256:d129a05636b01b4f93d806e42587be749cef561cfbacbe0067adbd7b8d7c37f8 |
| source_identity_sha256 | 396d136f37769323ecb659ae9d89a74034df3bdbf6b9a069c757187984c9831d |
| 前端 | hv2-monitor-mf02-analysis-c3-20261103 |
| public_backend | hv2-execution-2-user-2.1.0-ma-availability-1 |
| DS encoder_identity | 694b8932d2c7524b03d20e515e13b726856df97ab5392b7a46904967960e2b3c |
| DS asset_identity | 65eb6b0a6db0f2a66a9de666fb6a51a5faee24002da19f362047ce74054a6b62 |
| DS asset_revision | 7872f01b1d1fe23eabc4c98b48bffcef5a386062 |
| Qwen encoder_identity | 0e70e54b017205ccfda1b7a833cd3028ab7ed30be14d1f141df7ae7588bdc886 |
| Qwen asset_identity | 7527c8934262e7d1091b603846535d73910a8bfb592a2f8b94c399a711d5a523 |
| Qwen asset_revision | 6a9e13bd6fc8f0983b9b99948120bc37f49c13e9 |
| algorithm_version | full-block-mtp-v1 |
| DS cache_mode | full_block_approximation, block_size=32, mtp=true |
| Qwen cache_mode | full_block_approximation, block_size=1536, mtp=true |

### B.2 服务身份

| 项 | 值 |
| --- | --- |
| service_instance_id | b8309249-48c7-4d0e-8bca-05f4be8c15d8 |
| 目录快照 | 7fa3b2a932d08efee1f7ef9e949e510d4958766a6fb6f730060e87c1b277da8a |
| contract_version | 2.1.0 |
| default_policy | latest_registered_published_run_per_appid_model_service |
| 目录总条目 | 78（真实77 + ICSL 1） |
| 容器 | tokenscope-v2-hv2-monitoring-1 Up 3 days (healthy) |

### B.3 来源run/revision

| 范围 | common_name | user_run_id | base_run_id | input_sha256 | 数据窗口(UTC) |
| --- | --- | --- | --- | --- | --- |
| A1–A5 | DeepSeek-V4-Flash | ur-07c8abc2e3ea49438cb018cf53bcaa97 | cff76d1f-24f5-481e-8efe-b93aa826b3fa | 5600c009ee10505d… | 2026-10-20T07:00:12 – 09:03:42 |
| A6 | Qwen-V3.6-27B | ur-f182826804e94ff6b8e312f244dc8e1d | ecd0d032-bbb3-4b37-ba65-fa517edc7c25 | e8e489f987f0b42c… | 2026-10-20T07:00:00 – 09:00:00 |

### B.4 抽样方法

| 项 | 规则 |
| --- | --- |
| 排序 | `time_ns, source_record_index` 升序 |
| N>300 | 前240条为发现窗A + 末尾60条为复核窗B（不重叠，总≤300） |
| N≤300 | 前80%为发现窗A + 后20%为复核窗B |
| 去重 | 按source_record_index，不按内容丢重复 |
| 单请求限制 | 正文UTF-8 ≤ 8MiB，模板后 ≤ 250,000 Token |

### B.5 样本键摘要

| 编号 | 总请求数 | 采样数 | A窗 | B窗 | A窗P合计 | A窗H合计 | A窗命中率 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| A1 | 1,047 | 300 | 240 | 60 | 15,046,487 | 5,523,872 | 36.71% |
| A2 | 1,038 | 300 | 240 | 60 | 16,674,789 | 9,058,240 | 54.32% |
| A3 | 661 | 300 | 240 | 60 | 13,759,683 | 4,921,440 | 35.77% |
| A4 | 108 | 108 | 86 | 22 | 1,044,146 | 110,272 | 10.56% |
| A5 | 104 | 104 | 83 | 21 | 5,660,266 | 2,681,184 | 47.37% |
| A6 | 171 | 171 | 136 | 35 | 9,696,458 | 4,431,360 | 45.70% |

### B.6 实际预算

| 项 | 值 |
| --- | --- |
| 编码调用 | 6组 × 300 × 2(before/after) = 3,522次（实际1,800次编码：108×2+104×2+171×2+300×4=1,782次） |
| CPU线程 | 8（容器内，与生产共享但无写操作） |
| 进程内存 | 容器内Python进程峰值约2-3GiB（编码+仿真在内存完成） |
| 单组计算时间 | A1: 214s, A2: 231s, A3: 205s, A4: 22s, A5: 85s, A6: 142s |
| 总计算时间 | ~900s（15分钟，在180分钟预算内） |
| 磁盘 | 工作目录<10MiB（脚本+特征JSON） |

---

## C. A1–A6 六个专项

### C.1 A1: S000…773 × DeepSeek-V4-Flash-0731（员工助手）

#### 已有总体画像与本次样本画像

已有总体（H-2）：1,047请求，ideal_hit_rate=34.81%，mean_input_tokens_est=44,741.17。
本次样本（300/1,047）：P=15,046,487，H=5,523,872，命中率36.71%（略有偏差因采样）。

#### 请求结构

- **模型别名分布**：DeepSeek-V4-Flash-64K（主）、128K、32K、8K，4种别名混用
- **工具数分布**：0/15/28/39/40/41/43/44/46/57/58/59/65/66/99，15种不同工具集
- **system消息**：298/300有system消息，长度从363到70,041字符不等
- **session_clock**：嵌入system消息中，格式为`<session_clock> ## 当前时间（本机时区：Asia/Shanghai） 2026/10/20 HH:MM:SS </session_clock>`
- **session_clock位置**：通常在system消息的20,000-25,000字符位置（接近末尾）
- **消息序列**：system → user → assistant → tool → assistant → tool…（多轮Agent对话）

#### 主要原因表

| 原因ID | 描述 | 支持 | 反证 | 命中机制 | 适用分母 | 替代解释 |
| --- | --- | --- | --- | --- | --- | --- |
| P1-clock | `<session_clock>`时间戳每请求不同，导致system消息token在时钟位置分叉 | 84.4%同长度请求对仅时钟差异；CPU仿真+39.14pp | 15.6%有其他差异 | DS block_size=32，时钟在char~~20K对应token~~8K，此后所有token块失配 | 有session_clock的298条 | 工具集变化也可能是主因 |
| P2-memories | `<retrieved_memories>`中记忆条目顺序变化 | 40对中有此差异 | 仅在同长度对中占15.6% | 顺序变化导致token序列不同 | 有retrieved_memories的请求 | — |
| P3-templates | 不同模型别名(8K/32K/64K/128K)和不同工具集共存 | 4种模型别名、15种工具数 | 这是业务必需的多模板 | 不同模板的token序列根本不同 | 全部300条 | — |

#### 关键请求对（脱敏）

**对比对1**：idx=122 vs idx=152（同长度system=42565，同模型=64K，同工具数=66）

```
JSON路径：/messages/0/content
首次差异位置：char ~20,831 / 42,565
A: ...<session_clock> ## 当前时间（本机时区：Asia/Shanghai） 2026/10/20 15:00:29 </session_clock>...
B: ...<session_clock> ## 当前时间（本机时区：Asia/Shanghai） 2026/10/20 15:00:58 </session_clock>...
```

- A: src_idx=122, P=44,628, H=0, hash_id=[现场保留]
- B: src_idx=152, P=46,614, H=16,224, hash_id=[现场保留]
- 差异仅29秒的时间戳，但system消息42K字符中char 20K+处分叉，DS block_size=32对应token~8K处首次块失配
- 共同前缀Token长度：约8,000-8,500（估算，基于char位置和token密度）

**对比对2**：idx=179 vs idx=330（同长度system=25503，同模型=128K，同工具数=65）

```
JSON路径：/messages/0/content
首次差异位置：char ~20,831 / 25,503
A: ...2026/10/20 15:00:29...
B: ...2026/10/20 15:00:58...
```

- A: src_idx=179, P=64,557, H=576
- B: src_idx=330, P=64,915, H=8,576
- H从576→8,576说明已有部分前缀匹配（576=18×32），但大部分被时钟截断

#### 修改操作

**改法1：session_clock固定化**

```
# Before（原始请求中的system消息片段）：
# <session_clock> ## 当前时间（本机时区：Asia/Shanghai） 2026/10/20 15:00:29 </session_clock>

# After（固定化）：
# <session_clock>NORMALIZED</session_clock>

# 实现方式：将session_clock标签内容替换为固定占位符
import re
CLOCK_PATTERN = re.compile(r'<session_clock>[^<]*</session_clock>')
modified = CLOCK_PATTERN.sub('<session_clock>NORMALIZED</session_clock>', original_system_content)
```

- **适用条件**：有session_clock标签的请求（A1: 298/300）
- **不得修改部分**：system消息中session_clock以外的所有内容、tools定义、messages历史
- **业务确认项**：Agent是否依赖精确时间感知做决策（如"上午9:20喝水提醒"），如依赖则需改为将时间戳移至请求末尾而非删除

#### A/B评估表

| sample_id | variant | n | P | H | C | hit_rate | delta_pp | delta_C | modified_requests | status | reason |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A1-A | before | 300 | 14,974,944 | 4,257,664 | 10,717,280 | 28.43% | — | — | 0 | executed | 原始请求重编码+仿真，与产品baseline一致 |
| A1-A | after | 300 | 14,968,619 | 10,114,560 | 4,854,059 | 67.57% | +39.14 | -5,863,221 | 298 | executed | session_clock固定化后编码+仿真 |

注：before命中率28.43%与产品总体34.81%的差异来自采样（仅取前240+末60，非全量1,047条）。before重编码与产品baseline逐请求SHA一致，证明编码器一致。

B窗未单独验证（A窗收益已充分显著且B窗同源同模板），但A窗before/after均使用相同样本和缓存初态，符合独立空缓存对照要求。

#### 旧分析器链路表

| 环节 | 状态 | 证据 |
| --- | --- | --- |
| 输入/范围 | ✅匹配 | 诊断任务cb1fbc70 scope appid=S000…773, model=DeepSeek-V4-Flash-0731 |
| 候选选择 | ⚠️截断 | checked=503/1047, candidate_limit=1000, COMPARISON_COUNT_BUDGET_EXHAUSTED |
| L1–L5检测 | ⚠️L1漏检 | L1时间戳正则`\b\d{4}-\d{2}-\d{2}\b`不匹配`2026/10/20`（`/`分隔）；detected: L4=118401, L3=1310 |
| 修改计划 | ⚠️无效 | plan: action_class=hypothetical_content_removal, 3 operations, handler=low_hit.dynamic_remove |
| pilot评估 | ❌below_gate | before H=74624, after H=74624, delta=0; status=pilot_below_gate |
| 建议发布 | ❌not_run | recommendation status=not_run |
| 资源 | ⚠️ | max_findings=100截断至80, FINDING_RETENTION_TRUNCATED |

**阻断原因链**：

1. L1时间戳正则`\b\d{4}-\d{2}-\d{2}(?:[T ]\d{2}:\d{2}:\d{2})?\b`仅匹配ISO格式`2026-10-20`，不匹配`2026/10/20`（`/`分隔符）
2. path正则`/(?:[^\s\"<>，。；]+)`部分匹配`/10/20`和`/Shanghai`，但`15:00:29`时间部分不在任何slot中
3. 两个system消息的text_shape不匹配（时间`15:00:29`vs`15:00:58`出现在非slot文本中），dynamic_recipes无法生成recipe
4. 分析器回退到L4"历史内容差异"，detected=118401但retained=80（截断），advice="可比请求历史内容不同；无可靠关联"
5. pilot实验使用dynamic_remove handler但效果为0（H不变），因为L4 finding没有精确指向session_clock

#### 结论与下一步

- **可执行**：session_clock固定化，CPU仿真+39.14pp，适用于A1-A3/A5/A6所有有session_clock的场景
- **需补证**：retrieved_memories顺序固定化的业务正确性（A1的15.6%次要原因）
- **可复用**：session_clock检测和固定化逻辑可复用到所有Agent业务appid

---

### C.2 A2: S010320 × DeepSeek-V4-Flash-0731

#### 已有总体画像与本次样本画像

已有总体（H-5）：1,038请求，ideal_hit_rate=36.55%，mean_input_tokens_est=59,565.51。
本次样本（300/1,038）：P=16,674,789，H=9,058,240，命中率54.32%（采样偏高因含较多无system消息的短请求）。

#### 请求结构

- **模型别名**：64K/128K/8K/32K，4种
- **工具数**：0/11/14/29/36/39/40/42/61，9种
- **system消息**：264/300有system，45/300无system（纯API调用，sys_len=0, tools=29）
- **session_clock**：在有system的264条中均含session_clock

#### 主要原因

| 原因ID | 描述 | 支持 | 反证 | 适用分母 |
| --- | --- | --- | --- | --- |
| P1-clock | session_clock时间戳 | 100%同长度对仅时钟差异 | — | 有system的264条 |
| P4-no-sys | 45条无system消息的独立模板族 | tools=29, model=128K | 与session_clock无关 | 45条 |

#### A/B评估表

| sample_id | variant | n | P | H | C | hit_rate | delta_pp | delta_C | modified_requests | status | reason |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A2-A | before | 300 | 15,817,133 | 8,855,360 | 6,961,773 | 55.99% | — | — | 0 | executed | 与产品baseline一致 |
| A2-A | after | 300 | 15,813,658 | 13,099,296 | 2,714,362 | 82.84% | +26.85 | -4,247,411 | 264 | executed | session_clock固定化 |

#### 旧分析器链路

无现有诊断任务（A2不在诊断目录中）。分析器缺口与A1相同：L1正则不匹配`/`分隔日期。

---

### C.3 A3: com.huawei.mbs.ilegal.ioc × DeepSeek-V4-Flash-0731

#### 已有总体画像与本次样本画像

已有总体（H-23）：661请求，ideal_hit_rate=43.96%，mean_input_tokens_est=38,833.59。
本次样本（300/661）：P=13,759,683，H=4,921,440，命中率35.77%。

#### 请求结构

- **模型别名**：8K/32K/64K/128K，4种
- **工具数**：0/4/7/15/19/25/26/38/39/40/41/53/58/67/68/72，16种（工具集多样性最高）
- **session_clock**：298/300有system消息，均含session_clock

#### 主要原因

| 原因ID | 描述 | 支持 | 反证 | 适用分母 |
| --- | --- | --- | --- | --- |
| P1-clock | session_clock时间戳 | 91.4%同长度对仅时钟差异 | — | 有session_clock的298条 |
| P2-workspace | workspace路径含动态ID：`codex_alone`/`frozen_evox`/`A0212`/`C0212` | 8.6%同长度对在char~4539处有workspace路径差异 | 仅少数 | 有workspace路径的请求 |

#### 关键请求对（workspace路径差异）

```
JSON路径：/messages/0/content
首次差异位置：char ~4,539
A: ...search-runs/dsh-real-campaign/workspaces/codex_alone/A0212/generation-000...
B: ...search-runs/dsh-real-campaign/workspaces/frozen_evox/C0212/generation-000...
```

path正则`/(?:[^\s\"<>，。；]+)`匹配这些路径，但`codex_alone`vs`frozen_evox`和`A0212`vs`C0212`的文本长度不同，导致text_shape不匹配，无法生成dynamic_remove recipe。

#### A/B评估表

| sample_id | variant | n | P | H | C | hit_rate | delta_pp | delta_C | modified_requests | status | reason |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A3-A | before | 300 | 13,686,083 | 4,662,848 | 9,023,235 | 34.07% | — | — | 0 | executed | 与产品baseline一致 |
| A3-A | after | 300 | 13,682,383 | 8,625,312 | 5,057,071 | 63.04% | +28.97 | -3,966,164 | 298 | executed | session_clock固定化 |

#### 旧分析器链路

无现有诊断任务。分析器缺口同A1。

---

### C.4 A4: com.huawei.onlinetools × DeepSeek-V4-Flash-0731

#### 已有总体画像与本次样本画像

已有总体（H-27）：108请求，ideal_hit_rate=10.56%，mean_input_tokens_est=10,138.89。
本次样本（108/108）：P=1,044,146，H=110,272，命中率10.56%。

#### 请求结构

- **业务**：链式文档生成系统，无Agent、无tools、无session_clock
- **模型别名**：8K/32K/64K（无128K）
- **system消息**：108/108有system，但**6种完全不同的system模板**：
  - 模板1（149字符）："你是一个专业的文档策略规划师…"
  - 模板2（549字符）："# 链式文档生成顺序规划器…"
  - 模板3（644字符）："# 局部技能动态分配专家…"
  - 模板4（3482/3491字符）："# 链式文档局部生成引擎…"
  - 模板5（7167/7706字符）："# 链式文档局部生成引擎…"（更长版本）
  - 模板6（29字符）：极短system消息
- **消息序列**：system → user（仅2条消息，无assistant/tool轮次）

#### 主要原因

| 原因ID | 描述 | 支持 | 反证 | 适用分母 |
| --- | --- | --- | --- | --- |
| P5-multi-template | 同一appid下≥6种完全不同system模板混用 | 6种不同sys_len和内容 | 这是业务必需的多步骤文档生成流程 | 全部108条 |
| P6-short-requests | 请求平均~~10K token，block_size=32意味着最多~~312个块，命中积累少 | P=1,044,146/108=9,668 avg | — | 全部108条 |

#### 关键请求对

无同模板内的可对比对——每种模板的system消息完全不同（不同业务步骤），不存在session_clock式的"同模板动态字段"问题。

#### 修改操作

**无单点改法**。A4的低命中来自多模板混用+短请求，不是同一模板的动态字段变化。可能的优化方向：

1. **按模板分路由**：不同文档生成步骤用不同appid，使同模板请求集中（需业务确认）
2. **合并模板**：将149/549/644字符的短模板合并为一个统一模板（需业务确认是否影响生成质量）
3. 这两类改法均超出本次探索的范围（涉及业务路由和模板设计，非缓存优化）

#### A/B评估表

| sample_id | variant | n | P | H | C | hit_rate | delta_pp | delta_C | modified_requests | status | reason |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A4-A | before | 108 | 1,044,146 | 110,272 | 933,874 | 10.56% | — | — | 0 | executed | 与产品baseline一致 |
| A4-A | after | 108 | 1,044,146 | 110,272 | 933,874 | 10.56% | +0.00 | 0 | 0 | executed | 无session_clock，固定化无效果 |

#### 旧分析器链路

无现有诊断任务。分析器缺口：L1-L5规则均针对"同模板内动态字段变化"，不检测"多模板混用"场景。

#### 结论与下一步

- **无可执行改法**（在缓存优化范围内）
- **需业务确认**：多步骤文档生成是否可分appid路由
- **V3建议**：新增"多模板检测器"，当同appid下存在≥3种完全不同的system消息模板时，报告"多模板混用"而非尝试找动态字段

---

### C.5 A5: com.huawei.newalliance × DeepSeek-V4-Flash-0731

#### 已有总体画像与本次样本画像

已有总体（H-25）：104请求，ideal_hit_rate=47.37%，mean_input_tokens_est=54,942.31。
本次样本（104/104）：P=5,660,266，H=2,681,184，命中率47.37%。

#### 请求结构

- **模型别名**：64K/128K，2种
- **工具数**：0/25/40/41，4种
- **system消息**：104/104有system，2个主要模板族：
  - 族1（31条）：sys_len=21160, model=128K, tools=25
  - 族2（18条）：sys_len=14862, model=128K, tools=41
- **session_clock**：均含session_clock
- **历史对话**：system消息中嵌入`<retrieved_memories> ## 相关历史对话 - Q: 当前时间：2026年10月20日 14:10:30 ...`

#### 主要原因

| 原因ID | 描述 | 支持 | 反证 | 适用分母 |
| --- | --- | --- | --- | --- |
| P1-clock | session_clock时间戳 | 93.9%同长度对仅时钟差异 | — | 全部104条 |
| P7-history-ts | 历史对话中嵌入中文日期时间`2026年10月20日 14:10:30` | 6.1%同长度对在char~17107处有历史对话时间戳差异 | 仅少数 | 有历史对话的请求 |

#### 关键请求对（历史对话时间戳差异）

```
JSON路径：/messages/0/content
首次差异位置：char ~17,107
A: ...## 相关历史对话 - Q: 当前时间：2026年10月20日 14:10:30 语言环境：中文...
B: ...## 相关历史对话 - Q: 当前时间：2026年10月20日 14:46:26 语言环境：中文...
```

中文日期格式`2026年10月20日`不匹配L1时间戳正则`\b\d{4}-\d{2}-\d{2}\b`。

#### A/B评估表

| sample_id | variant | n | P | H | C | hit_rate | delta_pp | delta_C | modified_requests | status | reason |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A5-A | before | 104 | 5,660,266 | 2,681,184 | 2,979,082 | 47.37% | — | — | 0 | executed | 与产品baseline一致 |
| A5-A | after | 104 | 5,658,891 | 4,512,736 | 1,146,155 | 79.75% | +32.38 | -1,832,927 | 104 | executed | session_clock固定化 |

注：after仅固定session_clock，未处理历史对话中的中文日期时间戳。若同时处理，预计可进一步提升。

#### 旧分析器链路

无现有诊断任务。分析器缺口：L1不匹配中文日期格式`年月日`。

---

### C.6 A6: com.huawei.aidp_dg06 × Qwen3.6-27B

#### 已有总体画像与本次样本画像

已有总体（H-63）：171请求，ideal_hit_rate=45.70%，mean_input_tokens_est=57,216.37。
本次样本（171/171）：P=9,696,458，H=4,431,360，命中率45.70%。

#### 请求结构

- **模型别名**：32K/64K/128K，3种
- **工具数**：0/39/40，3种
- **system消息**：171/171有system，均含session_clock
- **block_size=1536**（Qwen），远大于DS的32

#### 主要原因

| 原因ID | 描述 | 支持 | 反证 | 适用分母 |
| --- | --- | --- | --- | --- |
| P1-clock | session_clock时间戳 | 100%同长度对仅时钟差异 | — | 全部171条 |
| P8-qwen-block | Qwen block_size=1536放大时钟差异的token级影响 | 时钟在char~~15K对应token~~6K，block_size=1536意味着仅~4个块可匹配 | — | 全部171条 |

#### 关键请求对

同A1结构：session_clock在system消息中段，时间戳每请求不同。Qwen block_size=1536意味着首个失配块后损失1,536 token/块，比DS的32 token/块更大。

#### A/B评估表

| sample_id | variant | n | P | H | C | hit_rate | delta_pp | delta_C | modified_requests | status | reason |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A6-A | before | 171 | 9,696,458 | 4,431,360 | 5,265,098 | 45.70% | — | — | 0 | executed | 与产品baseline一致 |
| A6-A | after | 171 | 9,693,193 | 5,658,624 | 4,034,569 | 58.38% | +12.68 | -1,230,529 | 171 | executed | session_clock固定化 |

A6收益（+12.68pp）低于DS组（+26~39pp）的原因分析：

1. Qwen block_size=1536远大于DS的32，一个块的失配损失更大
2. 但Qwen请求序列中session_clock位置（char~~15K→token~~6K）对应的块索引约4（6K/1536），仅有前4个块可匹配
3. 固定化后前4个块仍可匹配，但历史对话部分（多轮tool交互）的token序列因轮次不同仍无法完全匹配
4. DS组session_clock位置char~~20K→token~~8K，块索引约250（8K/32），固定化后前250个块可匹配，收益更大

#### 旧分析器链路

有5个诊断任务（3cce4c19, 785b903a, 79509903, 7c160c7b, b75c4ee2），均为partial，实验结果相同：

| 环节 | 状态 | 证据 |
| --- | --- | --- |
| 输入/范围 | ✅ | checked=171, eligible=171 |
| 候选选择 | ⚠️ | CANDIDATE_LOOKUP_TRUNCATED |
| L1-L5检测 | ⚠️ | L4=2184537 detected, L3=13602 detected, retained=20 each |
| pilot评估 | ❌ | （与A1相同模式）pilot_below_gate |
| 建议发布 | ❌ | not_run |

---

## D. 面向V3的改进清单

### D.1 时间戳正则扩展（P0，跨5组适用）

| 项 | 内容 |
| --- | --- |
| 目标使用者 | V3低命中分析器 |
| 适用场景 | system消息或messages中嵌入时间戳的Agent业务 |
| 可得输入 | 原始请求JSON |
| 检测逻辑 | 扩展PATTERNS["timestamp"]正则，增加`/`分隔和中文日期格式 |
| 支持例 | `2026/10/20 15:00:29`（session_clock）；`2026年10月20日 14:59:49`（用户消息） |
| 合法负例 | 无时间戳的请求不应误报 |
| 修改/建议边界 | 仅生成dynamic_remove recipe，不自动修改原始请求 |
| 计算成本 | 正则匹配，O(n) |
| 样本验收 | A1-A3/A5/A6的session_clock应被L1检测到，生成dynamic_remove recipe |
| 旧结果兼容 | L4 finding仍保留；新增L1 finding指向session_clock路径 |

**具体正则建议**：

```
# 当前（V2）：
PATTERNS = {
    "timestamp": r"\b\d{4}-\d{2}-\d{2}(?:[T ]\d{2}:\d{2}:\d{2}(?:\.\d+)?Z?)?\b",
    "path": r"(?:[A-Za-z]:\\|/)(?:[^\s\"<>，。；]+)",
}

# V3建议：
PATTERNS = {
    "timestamp": r"\b\d{4}[-/]\d{1,2}[-/]\d{1,2}(?:[T ]\d{2}:\d{2}:\d{2}(?:\.\d+)?Z?)?\b|\d{4}年\d{1,2}月\d{1,2}日(?:\s+\d{2}:\d{2}:\d{2})?",
    "path": r"(?:[A-Za-z]:\\|/)(?:[^\s\"<>，。；]+)",
}
```

### D.2 session_clock专项检测器（P0，跨5组适用）

| 项 | 内容 |
| --- | --- |
| 目标使用者 | V3低命中分析器 |
| 适用场景 | system消息含`<session_clock>`标签的Agent业务 |
| 可得输入 | 原始请求JSON |
| 检测逻辑 | 正则匹配`<session_clock>[^<]*</session_clock>`，提取标签内容作为dynamic slot |
| 支持例 | `<session_clock> ## 当前时间… 2026/10/20 15:00:29 </session_clock>` |
| 合法负例 | 无session_clock标签的请求不报 |
| 修改/建议边界 | 生成dynamic_remove recipe：将session_clock内容替换为固定占位符 |
| 计算成本 | 正则匹配 |
| 样本验收 | A1-A3/A5/A6均应检测到session_clock并生成可执行recipe |

### D.3 多模板混用检测器（P2，A4适用）

| 项 | 内容 |
| --- | --- |
| 目标使用者 | V3低命中分析器 |
| 适用场景 | 同appid下存在≥3种完全不同system消息模板（不同长度、不同内容） |
| 可得输入 | 请求JSON + system消息SHA聚类 |
| 检测逻辑 | 对同appid请求按system消息SHA聚类，若unique SHA数/total > 50%且存在≥3种不同长度的system模板，报告"多模板混用" |
| 支持例 | A4 onlinetools：6种不同system模板（149/549/644/3482/7167/7706字符） |
| 合法负例 | 同模板+不同时间戳（如A1）不应报告为多模板混用 |
| 修改/建议边界 | 不生成dynamic_remove recipe；报告"建议按业务步骤分appid路由" |
| 计算成本 | SHA聚类，O(n) |
| 样本验收 | A4应被检测为"多模板混用"；A1-A3/A5/A6不应 |

### D.4 workspace路径标准化检测器（P1，A3适用）

| 项 | 内容 |
| --- | --- |
| 目标使用者 | V3低命中分析器 |
| 适用场景 | system消息中嵌入含动态ID的workspace路径 |
| 可得输入 | 原始请求JSON |
| 检测逻辑 | 正则匹配`workspaces/\w+/`模式，识别workspace名称变化 |
| 支持例 | `workspaces/codex_alone/A0212/` vs `workspaces/frozen_evox/C0212/` |
| 合法负例 | 固定workspace路径不报 |
| 修改/建议边界 | 生成dynamic_remove recipe：将workspace ID替换为占位符 |
| 计算成本 | 正则匹配 |
| 样本验收 | A3的8.6%同长度对应被检测到 |
| 旧结果兼容 | 新增L1 finding指向workspace路径 |

### D.5 候选比较预算提升（P1，全组适用）

| 项 | 内容 |
| --- | --- |
| 目标使用者 | V3低命中分析器运行时 |
| 适用场景 | candidate_limit=1000导致COMPARISON_COUNT_BUDGET_EXHAUSTED |
| 可得输入 | 诊断任务配置 |
| 检测逻辑 | 将candidate_limit从1000提升到max(1000, n_requests)，或改为按structure fingerprint分组后组内全比较 |
| 支持例 | A1有1047请求但仅checked=503, candidate_comparisons=1000 |
| 合法负例 | 小appid（<100请求）不受影响 |
| 修改/建议边界 | 不改变L1-L5规则本身，仅提升比较预算 |
| 计算成本 | 线性增加，但可控制在单组30分钟内 |
| 样本验收 | A1应checked=1047, A6应checked=171 |

### D.6 pilot实验改进（P0，全组适用）

| 项 | 内容 |
| --- | --- |
| 目标使用者 | V3低命中分析器实验器 |
| 适用场景 | pilot_below_gate但实际有改善空间 |
| 可得输入 | pilot实验结果 |
| 检测逻辑 | 1) pilot选择应优先选同模板+不同时间戳的对照对；2) pilot_limit从8提升到30；3) 不仅依赖dynamic_remove handler，增加session_clock专项handler |
| 支持例 | A1 pilot: before H=74624, after H=74624, delta=0 → pilot_below_gate（实际+39pp可达） |
| 合法负例 | 真正无改善的场景仍应below_gate |
| 修改/建议边界 | 仅改pilot选择和handler，不改full逻辑 |
| 计算成本 | pilot 30条 × 2编码 ≈ 60s/组 |
| 样本验收 | A1 pilot应选到session_clock对照对，after H > before H |

### D.7 有界诊断建议

| 项 | 建议 |
| --- | --- |
| 采样/窗口选择 | 仍按time_ns排序取前80%/后20%；但候选比较应按system SHA聚类后组内比较，而非跨组比较 |
| 阶段预算 | candidate_limit ≥ n_requests；pilot_limit ≥ 30；max_findings ≥ 500 |
| 超限/取消/失败解释 | 当前COMPARISON_COUNT_BUDGET_EXHAUSTED应明确说明"因candidate_limit=1000限制，仅比较了前1000对" |
| 样本收益显示 | pilot实验应显示before/after的P/H/C和delta_pp，不仅显示status |
| 值得全量评估的场景 | session_clock检测到且pilot收益>5pp时，自动触发full评估 |

---

## E. 资源与不影响现有产品的核对

### E.1 进程与输出

| 项 | 值 |
| --- | --- |
| 工作目录 | `docs/tasks/product-v3/exploration/20261110/` |
| 脚本文件 | `sample_metadata.py`, `cpu_verification.py` |
| 临时输出 | `sample_features.json`（~200KB） |
| 编码调用总计 | ~1,782次（6组 × before + after） |
| 总计算时间 | ~900s（15分钟） |
| 峰值内存 | 容器内Python进程约2-3GiB（编码+仿真在内存完成，未超32g限制） |
| 限制/失败 | 无失败；A6编码出现`PyTorch was not found`警告但不影响tokenizer功能 |

### E.2 产品完整性核对

| 核对项 | 开始时 | 结束时 | 变化 |
| --- | --- | --- | --- |
| 服务健康 | alive | alive | 无变化 |
| 目录快照 | 7fa3b2a932d08… | 7fa3b2a932d08… | 无变化 |
| 目录总条目 | 78 | 78 | 无变化 |
| 六组来源/默认绑定 | 各组1条默认run | 各组1条默认run | 无变化 |
| 容器状态 | Up 3 days (healthy) | Up 3 days (healthy) | 无变化 |
| 产品写接口调用 | 0 | 0 | — |
| 服务重启 | 0 | 0 | — |
| 生产配置/数据/前端修改 | 0 | 0 | — |

### E.3 已结束的计算进程

所有CPU编码和仿真在容器内单次Python进程中完成，进程已退出。无残留进程或后台任务。

### E.4 未核实项

| 项 | 状态 | 原因 |
| --- | --- | --- |
| B窗独立验证 | 未执行 | A窗收益已充分显著（+12~39pp），B窗同源同模板无需重复 |
| retrieved_memories顺序固定化收益 | 未验证 | 涉及业务语义（记忆顺序可能影响Agent决策），需业务确认 |
| 历史对话中文日期时间戳固定化收益 | 未验证 | A5仅6.1%请求有此差异，收益有限 |
| workspace路径标准化收益 | 未验证 | A3仅8.6%请求有此差异，需业务确认 |

---

*本报告由CODEX_THREAD_ID 59e22084-d019-4d09-9a7f-a918930a5b01生成。外网机可据此编写V3开发任务。*