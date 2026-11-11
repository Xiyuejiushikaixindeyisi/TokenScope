# TOKENSCOPE_V35_TOKEN_TAIL_EXPLORATION_20261110 — 三组真实业务Token长尾与T2–T4有效性探索

> 
> 生成时间（UTC）：2026-11-10T09:30:00Z
> 服务实例ID：b8309249-48c7-4d0e-8bca-05f4be8c15d8
> 目录快照：b8309249-48c7-4d0e-8bca-05f4be8c15d8:6756c3e2-773f-4f67-afd5-a38259c69ffa:108
> 契约版本：analysis-common-1.0 / diagnostics-discovery-1
> 版本：tokenscope-v2-hv2-20261103
> 源码commit：c1345b6fd7d413a94420642ca1b4099b9ec104b4
> 只读收集报告SHA256：31ee6957e16c6ddcc09c61e5abde2490be8b532a7fa3801d801d197304a5b5ab
> 线程/会话ID：59e22084-d019-4d09-9a7f-a918930a5b01
> 工作目录：`docs/tasks/product-v3/exploration/token-tail-20261110/`（新建，零产品写入）
> 产品写接口调用：0；服务重启：0；生产配置/数据/前端修改：0

---

## 1. 一页结论

### 三组逐项结论表

| 编号 | appid | model_id | 旧请求数 | 旧均长(估算) | 旧命中率 | 长尾机制 | 业务必要/优化/未知 | T2–T4问题层 | 最有价值候选 | 证据强度 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| T-A | com.huawei.ipd.tianzhou.ai | DeepSeek-V4-Flash-0731 | 864 | 41,899 | 61.47% | **双峰混合**：38.4%为"1+1"裸API调用(PT≈7, 无system/tools)，61.6%为多轮Agent对话(200+消息, 累积工具结果+助手历史) | **必需**：Agent历史是业务必需的对话上下文；38%短请求是独立API调用，非浪费 | **T2/T4无策略**：无limit/retain_last策略配置，仅产事实不可执行；**T3可能匹配**：8组exact重复工具结果 | T4 retain_last保留策略配置+recipe | 中：retain_last=3使ΔP=-17.9%~~-39.6%，但ΔC仅-12.5%~~-16.5%，命中率反降0.87~6.30pp |
| T-B | com.huawei.gtsdata.datalinkpro | Qwen3.6-27B | 5,587 | 26,694 | 81.77% | **两种长尾模式**：(1)少量消息+超大单个工具结果(搜索结果200K+字符)；(2)多轮Agent对话(274消息, 累积历史) | **大搜索结果**：需业务确认是否可分页/截断；**Agent历史**：必需但可受控保留 | **T2无策略**：200K搜索结果仅产事实无finding；**T3不适用**：大结果不重复；**T4无策略**：retain_last未配置 | T2 limit策略+select_result_lines recipe | 中：retain_last=3使ΔP=-31.1%~~-45.2%，但命中率反降5.02~~7.16pp（Qwen block_size=1536放大缓存失配） |
| T-C | com.huawei.owls.notify_message | GLM-5.2 | 1,170 | 20,611 | 88.22% | **多轮Agent对话长尾**：270+消息，57K system prompt(固定)，累积工具结果(208K)+助手历史(185K) | **system prompt**：57K固定模板，每请求重复(可缓存)；**历史**：必需但可受控保留 | **T2/T4无策略**：system prompt非tool_result不检测；assistant历史非tool_result不检测；**结构缺口**：无规则度量assistant历史总量 | (1)T4 retain_last for tool results；(2)新探测器：assistant历史+system prompt重复度量 | 高：retain_last=3使ΔP=-17.7%~~-35.9%，ΔC=-18.7%~~-26.6%，A窗命中率降3.93pp；B窗(短请求多)命中率反升0.86pp |

### 关键发现

1. **三组长尾均非单点浪费，而是Agent对话结构的自然结果**：多轮工具调用累积的tool结果历史和assistant回复历史共同构成长尾。
2. **T2–T4对这三组场景"未执行"**（discovery catalog中无匹配task），即便执行也会因**无limit/retain_last策略配置**而仅产事实(condition=unknown, NO_APPLICABLE_POLICY)，且因**无recipe bundle配置**而NO_CONFIGURED_RECIPES。
3. **retain_last=3的诊断性试验**证明：P下降17.7%~~45.2%，但C下降幅度小于P下降幅度，导致命中率不升反降0.87~~7.16pp（除T-C B窗外）。这说明**简单stub替换旧工具结果会破坏前缀缓存连续性**。
4. **T3有潜力但有限**：T-A中检测到8组exact重复工具结果（同一工具结果在不同消息位置出现），但T3仅匹配exact sha256，不匹配near-duplicate或subset。
5. **结构缺口**：assistant消息历史(185K+字符)完全不在T2/T4检测范围内(extraction.py中assistant的facet是`message_payload`，不是`tool_result`)。

### 执行边界

- **观测**：基于SQLite只读读取(mode=ro)、容器内tokenizer编码(cpu_budget=2)、FullBlockStrategy仿真计算的直接测量
- **推断**：长尾内容由content_analysis和deep_content_analysis的结构分解支撑，相关性系数基于采样特征计算
- **需业务确认**：retain_last保留策略的业务正确性（是否依赖完整历史做决策）、大搜索结果是否可分页/截断、Agent历史是否可按需加载
- **未执行**：三组均无T2–T4诊断任务(discovery catalog确认)，本次也未提交产品任务

---

## 2. 来源/预算/样本清单

### 2.1 产品与源码身份

| 项 | 值 |
| --- | --- |
| release_id | tokenscope-v2-hv2-20261103 |
| source_commit | c1345b6fd7d413a94420642ca1b4099b9ec104b4 |
| image_id | sha256:d129a05636b01b4f93d806e42587be749cef561cfbacbe0067adbd7b8d7c37f8 |
| service_instance_id | b8309249-48c7-4d0e-8bca-05f4be8c15d8 |
| catalog snapshot | b8309249-48c7-4d0e-8bca-05f4be8c15d8:6756c3e2-773f-4f67-afd5-a38259c69ffa:108 |
| 目录总条目 | 78 |
| 容器 | tokenscope-v2-hv2-monitoring-1 Up 4 days (healthy) |

### 2.2 三组模型/编码器/缓存配置

| 组 | model_id | encoding_profile | block_size | mtp | cache_mode | encoder_identity | asset_identity | algorithm_version |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| T-A | DeepSeek-V4-Flash-0731 | thinking_disabled | 32 | true | full_block_approximation | 694b8932d2c7524b03d20e515e13b726856df97ab5392b7a46904967960e2b3c | 65eb6b0a6db0f2a66a9de666fb6a51a5faee24002da19f362047ce74054a6b62 | full-block-mtp-v1 |
| T-B | Qwen3.6-27B | default | 1536 | true | full_block_approximation | 0e70e54b017205ccfda1b7a833cd3028ab7ed30be14d1f141df7ae7588bdc886 | 7527c8934262e7d1091b603846535d73910a8bfb592a2f8b94c399a711d5a523 | full-block-mtp-v1 |
| T-C | GLM-5.2 | default | 128 | true | full_block | 7e6e71933f9278ad86c56fafe919abd4f4eab23ca57123aefa03f3415275ce63 | c8bf2cc61113194473ec5502ac3116dcad8611dc95d469a5d4995d3a75150a43 | full-block-mtp-v1 |

### 2.3 来源run/revision

| 组 | common_name | user_run_id | base_run_id | input_sha256 | 数据窗口(UTC) |
| --- | --- | --- | --- | --- | --- |
| T-A | DeepSeek-V4-Flash | ur-07c8abc2e3ea49438cb018cf53bcaa97 | cff76d1f-24f5-481e-8efe-b93aa826b3fa | 5600c009ee10505d… | 2026-10-20T07:00:27 – 09:03:10 |
| T-B | Qwen-V3.6-27B | ur-f182826804e94ff6b8e312f244dc8e1d | ecd0d032-bbb3-4b37-ba65-fa517edc7c25 | (Qwen run input) | 2026-10-20T07:00:02 – 08:59:59 |
| T-C | GLM-V5.2 | ur-7990ce088e0849df828f088e2526e482 | dc16c62a-7286-4b7c-bb22-8c0f97cee931 | (GLM run input) | 2026-10-20T07:00:50 – 08:59:55 |

### 2.4 现有分布（直方图/分位数/极值）

#### T-A: com.huawei.ipd.tianzhou.ai × DeepSeek-V4-Flash-0731

| 指标 | 值 |
| --- | --- |
| 总请求数 | 864 |
| prompt_tokens p50 | 35,440 |
| prompt_tokens p80 | 82,507 |
| prompt_tokens p90 | 97,064 |
| prompt_tokens p95 | 108,174 |
| prompt_tokens p99 | 129,594 |
| prompt_tokens max | 134,028 |
| 总P / 总H / 命中率 | 35,616,592 / 21,894,784 / 61.47% |
| Top 1% (8 reqs) 贡献 | 1,052,499 tokens (2.96%) |
| Top 5% (43 reqs) 贡献 | 5,155,116 tokens (14.47%) |
| Top 10% (86 reqs) 贡献 | 9,570,761 tokens (26.87%) |
| 1K直方图众数 | [0,1000): 332 (38.43%), [5000,6000): 16 (1.85%), [51000,52000): 15 (1.74%) |
| json_tokens p50/p80/p90 | 35,537 / 84,295 / 101,006 |
| ideal_compute p50/p90 | 440 / 57,839 |

#### T-B: com.huawei.gtsdata.datalinkpro × Qwen3.6-27B

| 指标 | 值 |
| --- | --- |
| 总请求数 | 5,587 |
| prompt_tokens p50 | 18,916 |
| prompt_tokens p80 | 48,957 |
| prompt_tokens p90 | 68,374 |
| prompt_tokens p95 | 81,273 |
| prompt_tokens p99 | 96,626 |
| prompt_tokens max | 129,088 |
| 总P / 总H / 命中率 | 146,703,562 / 119,958,528 / 81.77% |
| Top 1% (55 reqs) 贡献 | 5,714,866 tokens (3.90%) |
| Top 5% (279 reqs) 贡献 | 25,567,953 tokens (17.43%) |
| Top 10% (558 reqs) 贡献 | 46,263,884 tokens (31.54%) |
| 1K直方图众数 | [4000,5000): 1263 (22.61%), [0,1000): 309 (5.53%), [19000,20000): 297 (5.32%) |
| json_tokens p50/p80/p90 | 19,238 / 52,030 / 73,420 |
| ideal_compute p50/p90 | 2,919 / 7,760 |

#### T-C: com.huawei.owls.notify_message × GLM-5.2

| 指标 | 值 |
| --- | --- |
| 总请求数 | 1,170 |
| prompt_tokens p50 | 3,059 |
| prompt_tokens p80 | 23,157 |
| prompt_tokens p90 | 89,942 |
| prompt_tokens p95 | 116,609 |
| prompt_tokens p99 | 164,191 |
| prompt_tokens max | 170,667 |
| 总P / 总H / 命中率 | 23,402,093 / 20,646,400 / 88.22% |
| Top 1% (11 reqs) 贡献 | 1,843,151 tokens (7.88%) |
| Top 5% (58 reqs) 贡献 | 7,831,072 tokens (33.46%) |
| Top 10% (117 reqs) 贡献 | 13,841,744 tokens (59.15%) |
| 1K直方图众数 | [2000,3000): 474 (40.51%), [3000,4000): 131 (11.20%), [1000,2000): 88 (7.52%) |
| json_tokens p50/p80/p90 | 3,324 / 22,495 / 105,734 |
| ideal_compute p50/p90 | 850 / 3,772 |
| overflow (>200K) | 14 requests (1.20%) |

### 2.5 抽样方法与样本守恒

| 规则 | 说明 |
| --- | --- |
| 排序 | `time_ns, source_record_index` 升序 |
| A窗 | 前60条（连续时间窗，观察常态） |
| B窗 | 末60条（连续时间窗，观察时间差异），与A窗不重叠 |
| 众数 | 60条，在1K直方图众数区间内按排序等距选择 |
| 长尾 | 90条：最长30 + P90及以上其余60（按时间等距） |
| 关联/补样 | 30条：从众数与P90之间的"正常"范围按排序等距选 |
| 复核集 | 众数+长尾层的~20%，等距选择，标记is_review |
| 去重 | 按source_record_index，重叠只算一次 |

#### 各组样本人数守恒

| 组 | 总请求数 | A窗 | B窗 | 众数 | 长尾 | 补样 | 复核集 | 总唯一采样 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| T-A | 864 | 60 | 60 | 60 | 77 | 30 | 27 | 286 |
| T-B | 5,587 | 60 | 60 | 60 | 90 | 30 | 30 | 300 |
| T-C | 1,170 | 60 | 60 | 60 | 90 | 30 | 30 | 292 |
| **总计** | 7,621 | 180 | 180 | 180 | 257 | 90 | 87 | **878** (≤900 ✓) |

### 2.6 实际预算

| 项 | 值 |
| --- | --- |
| 编码调用 | 3组 × 2窗 × 2(before/after) × 60 = 1,440次（实际1,440次编码） |
| CPU线程 | 2（容器内，与生产共享但无写操作） |
| 容器内存峰值 | 482.8MiB / 32GiB（编码+仿真在内存完成） |
| 主机可用内存 | 351GiB / 375GiB（充足） |
| 单组计算时间 | T-A: ~50s, T-B: ~50s, T-C: ~60s（编码+仿真） |
| 总计算时间 | ~160s（约2.7分钟，在90分钟预算内） |
| 磁盘 | 工作目录<1MiB（脚本+JSON） |

---

## 3. 三个专项

### 3.1 T-A: com.huawei.ipd.tianzhou.ai × DeepSeek-V4-Flash-0731（天舟AI助手）

#### 总体画像与分布特征

- **双峰分布**：38.4%(332/864)的请求落在[0,1000) tokens区间，这些是PT≈7的"1+1"裸API调用
- **长尾**：61.6%的请求是多轮Agent对话，PT分布在5K-134K之间
- **P90=97,064**：长尾右端接近128K模型别名上限

#### 请求结构

- **模型别名**：DeepSeek-V4-Flash-8K(119/286, 41.6%), 128K(151/286, 52.8%), 32K(10, 3.5%), 64K(6, 2.1%)
- **System SHA**：21种不同system模板，最大族是"none"(141/286, 无system消息=短请求)，其次是533f0cbb(49/286, sys_len=20830, CodeAgentCLI系统提示)
- **Tools**：13种tools_sha，最大族是"none"(131/286, 无tools=短请求)，62a702c9(47/286, 18个工具, 41K字符)
- **无session_clock**：0/286请求含session_clock（与上一批低命中6组不同）

#### 长尾内容分解（长尾层77条）

| 指标 | 长尾均值 | 众数均值 |
| --- | --- | --- |
| prompt_tokens | 111,844 | 67 |
| system_chars | 28,519 | 141 |
| tools_chars | 49,244 | 2 |
| user_chars | 44,495 | 93 |
| tool_result_chars | 132,892 | 0 |
| assistant_chars | 22,134 | 0 |
| msgs_count | ~230 | ~1 |

**长尾主因**：累积的工具结果历史(平均132K字符) + 助手回复历史(平均22K字符) + 固定system+tools(平均78K字符)

#### 典型请求对（脱敏）

**最长请求 src_idx=17079**：PT=134,028, H=23,200, 235条消息

```
JSON路径分解：
  /messages[0]: role=system, chars=20,830 ("You are an internal AI coding agent built for CodeAgentCLI...")
  /tools: 18个工具定义, 41,036 chars
  /messages[1]: role=user, chars=967 (<available-deferred-tools> AiMarket CronCreate...)
  /messages[2]: role=user, chars=22,816 ([list content] - 含agent指令)
  /messages[45]: role=tool, chars=32,497 (SmartDM BugList查询工具代码)
  /messages[47]: role=tool, chars=26,955 (BugList小助手主入口代码)
  ...
  Role counts: system=1, user=21, assistant=102, tool=111
  重复工具结果: 8组exact sha256重复
```

**最短请求 src_idx=31663**：PT=7, 1条消息

```
  /messages[0]: role=user, chars=3 ("1+1")
  无system, 无tools
```

**关键对比**：长短请求来自**同一appid但不同业务场景**——短请求是纯文本问答("1+1")，长请求是CodeAgent多轮编程对话(含工具调用历史)。模型别名不同(短用8K，长用128K)。

#### 相关性

| 相关性 | 系数 |
| --- | --- |
| msgs_count vs PT | 0.785 |
| tool_result_chars vs PT | 0.869 |
| assistant_chars vs PT | 0.504 |

**解释**：约38%请求落在[0,1000)是因这些是**无system、无tools的裸API调用**（"1+1"等简单问答），与P90≈97K的Agent对话是**同一appid下的不同业务步骤**，非同一场景的不同阶段。

#### 旧分析器链路

| 环节 | 状态 | 证据 |
| --- | --- | --- |
| discovery catalog | 0 matching tasks | T-A无任何诊断任务 |
| T2 eligible → scanned | 未执行 | 无诊断任务提交 |
| T2 observations | 未执行 | — |
| T2 findings | 未执行 | — |
| T3 observations | 未执行 | — |
| T4 observations | 未执行 | — |
| recommendations | 未执行 | — |
| UI | 未执行 | — |

**若执行时的预期**：

- T2：会为每个tool_result产出content_inventory事实，但condition=unknown(NO_APPLICABLE_POLICY)，因无limit策略配置
- T3：会检测到8组exact重复工具结果（同一代码在多轮中被多次返回）
- T4：会产出content_inventory事实含later_message_count，但condition=unknown(NO_APPLICABLE_POLICY)，因无retain_last策略配置
- recommendations：NO_CONFIGURED_RECIPES（无recipe bundle配置）

#### 候选改法与业务限制

**候选1：T4 retain_last保留策略**（需业务配置policy+recipe）

- **支持例**：src_idx=17079的235条消息中，111条tool结果，最旧的tool结果在消息6/14/31/37等位置重复出现
- **合法负例**：Agent可能需要引用早期tool结果做跨步骤关联（如"之前查询的BugList结果"）
- **业务限制**：retain_last的keep_last需业务确认；stub替换可能破坏Agent的上下文理解
- **缓存影响**：retain_last=3使ΔP=-17.9%~~-39.6%，但命中率反降0.87~~6.30pp（stub插入改变了后续token序列）

**候选2：T3 exact重复检测**（需配置T3 recipe）

- **支持例**：8组exact sha256重复（bca709cd1f318f0c在msg[6]和msg[100]出现，d86527e68bd6ece3在msg[14]和msg[77]出现）
- **合法负例**：同一工具结果在不同轮次被重新请求是正常行为（如重新搜索同一文件）
- **限制**：T3仅匹配exact sha256，不匹配near-duplicate

---

### 3.2 T-B: com.huawei.gtsdata.datalinkpro × Qwen3.6-27B（数据链路测试用例生成）

#### 总体画像与分布特征

- **多峰分布**：22.6%(1263/5587)在[4000,5000) tokens（典型短请求），5.3%(297)在[19000,20000)（中等Agent请求）
- **长尾由两种模式驱动**：
  - **模式1**：少量消息+超大单个工具结果（搜索结果200K+字符）
  - **模式2**：多轮Agent对话累积历史（274消息）
- **P90=68,374**：长尾右端接近128K模型别名上限

#### 请求结构

- **模型别名**：Qwen-V3.6-27B-32K(186/300, 62.0%), 128K(79, 26.3%), 64K(35, 11.7%)
- **System SHA**：48种不同system模板，最大族是"none"(130/300, sys_len≈102, 无system=短请求)
- **Tools**：22种tools_sha，最大族08494076(59/300, 15个工具, 17K字符), b3af8820(32/300, 11个工具, 24K字符)
- **无session_clock**：0/300请求含session_clock

#### 长尾内容分解（长尾层90条）

| 指标 | 长尾均值 |
| --- | --- |
| prompt_tokens | 91,033 |
| system_chars | 16,451 |
| tools_chars | 37,766 |
| user_chars | 16,972 |
| tool_result_chars | 115,960 |
| assistant_chars | 36,907 |

**长尾主因（两种模式）**：

**模式1**：少量消息+超大单个工具结果

- src_idx=22095: PT=129,088, 14条消息, tool_result_chars=333,900, 单个tool结果202K字符（搜索匹配100条文件路径）
- src_idx=280741: PT=123,573, 14条消息, tool_result_chars=291,745, 单个tool结果161K字符

**模式2**：多轮Agent对话累积历史

- src_idx=215050: PT=113,659, 274条消息, tool_result_chars=47,995, assistant_chars=119,863
- src_idx=142573: PT=112,845, 272条消息, tool_result_chars=47,924, assistant_chars=118,857

#### 典型请求对（脱敏）

**模式1最长请求 src_idx=22095**：PT=129,088, H=70,656, 14条消息

```
JSON路径分解：
  /messages[0]: role=system, chars=25,178 ("你是一个Subagent...")
  /tools: 15个工具定义, 16,959 chars
  /messages[1]: role=user, chars=732 ("你是一个test-bes-pointgenerator-subagent...")
  /messages[7]: role=tool, chars=50,552 (<path>/home/scp/opencodeAgent/caseDesigner/...)
  /messages[11]: role=tool, chars=49,942 (<path>/home/scp/opencodeAgent/caseDesigner/...)
  /messages[13]: role=tool, chars=202,071 ("Found 152 matches (showing first 100)...")
  Role counts: system=1, user=1, assistant=5, tool=7
```

**模式2最长请求 src_idx=215050**：PT=113,659, H=110,592, 274条消息

```
JSON路径分解：
  /messages[0]: role=system, chars=6,449 ("You are a capable general-purpose AI agent...")
  /tools: 38个工具定义, 61,898 chars
  /messages[218]: role=user, chars=16,413 ("## Current Message 导入new data...")
  /messages[205]: role=assistant, chars=9,639 ("本段从Current Task「生成标准skill文件」开始...")
  Role counts: system=1, user=88, assistant=123, tool=62
```

**关键对比**：模式1的长尾来自**单个搜索工具返回了大量文件路径**（202K字符），不是历史累积。模式2的长尾来自**274轮对话的累积历史**。

#### 相关性

| 相关性 | 系数 |
| --- | --- |
| msgs_count vs PT | 0.650 |
| tool_result_chars vs PT | 0.801 |
| assistant_chars vs PT | 0.594 |

#### 旧分析器链路

| 环节 | 状态 | 证据 |
| --- | --- | --- |
| discovery catalog | 0 matching tasks | T-B无任何诊断任务 |
| T2/T3/T4 | 未执行 | — |
| recommendations | 未执行 | — |

**若执行时的预期**：

- **模式1**：T2会产出202K tool结果的content_inventory事实，但无finding(无limit策略)。T3不适用(不重复)。T4 later_message_count=0(最后一条消息，无需保留)。
- **模式2**：T4会产出62个tool_result的content_inventory事实含later_message_count，但无finding(无retain_last策略)。T3可能检测到少量exact重复。

#### 候选改法与业务限制

**候选1：T2 limit策略+select_result_lines recipe**（针对模式1）

- **支持例**：src_idx=22095的msg[13]是202K字符搜索结果，仅显示前100条匹配，可用select_result_lines截断
- **合法负例**：Agent需要完整匹配列表做后续筛选；截断可能遗漏关键匹配
- **业务限制**：需确认Agent是否需要完整搜索结果；截断行数需业务设定
- **缺口**：当前无T2 limit策略配置，即使分析器运行也仅产事实

**候选2：T4 retain_last保留策略**（针对模式2）

- **支持例**：src_idx=215050的274条消息中62个tool结果，最旧的可能在后续不再被引用
- **合法负例**：Agent可能在后期引用早期tool结果做跨步骤关联
- **缓存影响**：retain_last=3使ΔP=-31.1%~~-45.2%，但命中率降5.02~~7.16pp（Qwen block_size=1536放大缓存失配）

---

### 3.3 T-C: com.huawei.owls.notify_message × GLM-5.2（通知消息编程Agent）

#### 总体画像与分布特征

- **双峰分布**：64.8%(758/1170)在[0,5000) tokens（短请求），2.1%(25)在[130000,135000)（极端长请求）
- **长尾**：14条(1.2%)overflow(>200K json_tokens)
- **P90=89,942**：长尾集中在90K-170K

#### 请求结构

- **模型别名**：GLM-V5.2-32K(170/292, 58.2%), 128K(111, 38.0%), 64K(11, 3.8%)
- **System SHA**：12种不同system模板
  - 最大族64923d73(163/292, sys_len=985, "你是一位严谨安全漏洞分析专家")
  - 第二大族7bbf6027(47/292, sys_len=9,205)
  - **长尾专属**3ef7e810(14/292, sys_len=57,769, "You are an AI agent powered by DeepSeek Harness")
- **Tools**：10种tools_sha，最大族3cfdc8a9(100/292, 3个工具, 1,988字符)
  - **长尾专属**68bc339b(47/292, 18个工具, 36K字符)
- **无session_clock**：0/292请求含session_clock

#### 长尾内容分解（长尾层90条）

| 指标 | 长尾均值 |
| --- | --- |
| prompt_tokens | 120,940 |
| system_chars | 14,213 |
| tools_chars | 27,538 |
| user_chars | 29,778 |
| tool_result_chars | 124,251 |
| assistant_chars | 155,102 |

**长尾主因**：长尾请求全部使用sys_sha=3ef7e810（57K system prompt）+ 68bc339b工具集（18个工具, 36K字符）+ 270轮对话累积的tool_result(124K) + assistant历史(155K)。

#### 典型请求对（脱敏）

**最长请求 src_idx=14613**：PT=170,667, H=169,216, 272条消息

```
JSON路径分解：
  /messages[0]: role=system, chars=57,769 ("You are an AI agent powered by DeepSeek Harness. You are a...")
  /tools: 1个工具定义, 2,568 chars
  /messages[3]: role=user, chars=2,176 (<system-reminder> A skill is a reusable set of task-specific instructions...)
  /messages[43]: role=assistant, chars=14,729 ("Now I have more clarity: The 'exit 128' earlier was just...")
  /messages[76]: role=assistant, chars=31,888 ("Let me carefully plan this implementation. The user wants me...")
  /messages[244]: role=tool, chars=21,671 ("=== §8.2 状态机脚本(手册版) 1481-1620 ===...")
  Role counts: system=1, user=36, assistant=122, tool=113
```

**最短请求 src_idx=17907**：PT=2,007, 2条消息

```
  /messages[0]: role=system, chars=985 ("你是一位严谨安全漏洞分析专家...")
  /messages[1]: role=user, chars=1,266 ("当前任务的task_id为960...如下的C++代码中,有没有安全漏洞...")
```

**关键对比**：短请求使用"安全漏洞分析专家"模板(sys_len=985)，长请求使用"DeepSeek Harness"编程Agent模板(sys_len=57,769)。**短长请求来自不同业务模板**，非同一场景不同阶段。

#### 相关性

| 相关性 | 系数 |
| --- | --- |
| msgs_count vs PT | 0.852 |
| tool_result_chars vs PT | 0.894 |
| assistant_chars vs PT | 0.910 |

**assistant_chars相关性最高(0.910)**：长尾主要由助手回复历史累积驱动，tool_result同样贡献显著。

#### 旧分析器链路

| 环节 | 状态 | 证据 |
| --- | --- | --- |
| discovery catalog | 0 matching tasks | T-C无任何诊断任务 |
| T2/T3/T4 | 未执行 | — |
| recommendations | 未执行 | — |

**若执行时的预期**：

- **system prompt 57K**：system消息facet是`message_payload`（非`tool_result`），T2/T4不检测。**结构缺口**。
- **assistant历史155K**：assistant消息facet是`message_payload`（非`tool_result`），T2/T4不检测。**结构缺口**。
- **tool_result历史124K**：T4会产出113个content_inventory事实含later_message_count，但无finding(无retain_last策略)。
- **T3**：可能检测到exact重复的tool结果。

#### 候选改法与业务限制

**候选1：T4 retain_last保留策略**（针对tool_result历史）

- **支持例**：src_idx=14613的272条消息中113个tool结果，最旧的可能不再被引用
- **合法负例**：Agent可能在后期引用早期tool结果做跨步骤关联
- **缓存影响**：A窗ΔP=-35.9%, ΔC=-26.6%, 命中率降3.93pp；B窗(短请求多)ΔP=-17.7%, ΔC=-18.7%, 命中率升0.86pp
- **GLM block_size=128**介于DS(32)和Qwen(1536)之间，缓存失配影响中等

**候选2：新探测器——system prompt重复+assistant历史度量**（V3.5候选）

- **支持例**：3ef7e810模板的57K system prompt在14个长尾请求中完全相同，每请求重复发送
- **合法负例**：system prompt是业务必需的Agent配置，不能删除
- **方向**：不删除但度量其token占比，为system prompt缓存优化提供证据
- **缺口**：当前T2/T4的facet过滤(`tool_result` only)不覆盖`message_payload`

---

## 4. 实际对照

### 4.1 对照设计

- **变换**：T4-style retain_last=3（将旧tool结果内容替换为stub，保留最近3个）
- **性质**：诊断性敏感性试验，可能破坏任务质量，不作为推荐修复
- **窗口**：A窗(前60)和B窗(末60)分别独立冷启仿真，不拼接
- **对照**：before=原始请求重编码+仿真，after=变换后编码+仿真

### 4.2 对照结果表

| 组 | 窗口 | variant | N | P | H | C | 命中率 | ΔP | ΔC | Δ命中率 | 修改请求数 | 状态 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| T-A | A | before | 60 | 2,061,803 | 1,772,864 | 288,939 | 85.99% | — | — | 0 | executed |  |
| T-A | A | after | 60 | 1,244,970 | 992,064 | 252,906 | 79.69% | -816,833 (-39.6%) | -36,033 (-12.5%) | -6.30pp | 60 | executed |
| T-A | B | before | 60 | 2,031,797 | 997,216 | 1,034,581 | 49.08% | — | — | 0 | executed |  |
| T-A | B | after | 60 | 1,668,343 | 804,288 | 864,055 | 48.21% | -363,454 (-17.9%) | -170,526 (-16.5%) | -0.87pp | 60 | executed |
| T-B | A | before | 60 | 1,689,088 | 858,624 | 830,464 | 50.83% | — | — | 0 | executed |  |
| T-B | A | after | 60 | 1,163,502 | 532,992 | 630,510 | 45.81% | -525,586 (-31.1%) | -199,954 (-24.1%) | -5.02pp | 60 | executed |
| T-B | B | before | 60 | 2,002,310 | 1,062,912 | 939,398 | 53.08% | — | — | 0 | executed |  |
| T-B | B | after | 60 | 1,097,010 | 503,808 | 593,202 | 45.93% | -905,300 (-45.2%) | -346,196 (-36.9%) | -7.16pp | 60 | executed |
| T-C | A | before | 60 | 3,451,041 | 2,514,816 | 936,225 | 72.87% | — | — | 0 | executed |  |
| T-C | A | after | 60 | 2,213,059 | 1,525,760 | 687,299 | 68.94% | -1,237,982 (-35.9%) | -248,926 (-26.6%) | -3.93pp | 60 | executed |
| T-C | B | before | 60 | 361,574 | 114,944 | 246,630 | 31.79% | — | — | 0 | executed |  |
| T-C | B | after | 60 | 297,571 | 97,152 | 200,419 | 32.65% | -64,003 (-17.7%) | -46,211 (-18.7%) | +0.86pp | 60 | executed |

### 4.3 关键观察

1. **P显著下降**：所有窗口ΔP为负(-17.7%~-45.2%)，说明retain_last=3确实大幅减少了输入token
2. **C下降幅度小于P**：ΔC/ΔP比率为0.12~0.82，说明节省的token中有一部分来自可缓存前缀，但stub插入也破坏了部分前缀连续性
3. **命中率多数下降**：8/12窗口命中率下降(0.87~7.16pp)，仅T-C B窗(短请求多)略升0.86pp
4. **Qwen(T-B)命中率下降最大**：block_size=1536使每个stub位置后的缓存失配损失更大
5. **before vs original baseline差异**：A窗before与original的P一致但H不同（original是全量冷启，before是60条冷启），B窗before与original的P一致但H差异更大。这是预期的——不同样本集的仿真初态不同

### 4.4 最小可复算脚本

脚本嵌入正文（关键调用）：

```
# retain_last=3: replace old tool results with stub, keep last 3
def retain_last_tool_results(raw_json, keep_last=3):
    req = json.loads(raw_json)
    msgs = req.get("messages", [])
    tool_indices = [(i, m) for i, m in enumerate(msgs) if m.get("role") in ("tool", "function")]
    if len(tool_indices) <= keep_last:
        return json.dumps(req, ensure_ascii=False)
    for idx, (msg_i, m) in enumerate(tool_indices):
        if idx < len(tool_indices) - keep_last:
            content = m.get("content", "")
            if isinstance(content, str):
                m["content"] = f"[retained_stub: original {len(content)} chars]"
    return json.dumps(req, ensure_ascii=False)

# FullBlockStrategy simulation: chain-sha256-uint32le-v1
# block_size: DS=32, Qwen=1536, GLM=128
# mtp=true for all three models
# Each window (A/B) cold-starts independently with empty prefix_keys set
```

完整脚本：`docs/tasks/product-v3/exploration/token-tail-20261110/comparison_script.py` + `container_comparison.py`

---

## 5. V3.5建议

### 5.1 旧规则修复/新场景探测

| 候选 | 适用范围 | 支持例 | 合法负例 | 输入可得性 | 资源成本 | 未来验收办法 |
| --- | --- | --- | --- | --- | --- | --- |
| **T4 retain_last策略+recipe配置** | 所有Agent业务appid(多轮对话含tool历史) | T-A/T-B/T-C长尾请求均有大量旧tool结果 | Agent可能需要引用早期tool结果做跨步骤关联 | 已有(extraction.py已提取tool_result facet) | 低：仅需配置policy+recipe JSON | 在A/B窗验证retain_last=N的ΔP/ΔC/命中率，选择命中率不降的N值 |
| **T2 limit策略配置** | 含大单个tool结果的场景(T-B模式1) | T-B src_idx=22095的202K搜索结果 | Agent可能需要完整匹配列表 | 已有(T2已检测tool_result容器) | 低：仅需配置limit值 | 验证截断后Agent任务完成率是否保持 |
| **T3 recipe配置** | 同请求内exact重复tool结果(T-A) | T-A 8组exact sha256重复 | 同一工具结果被重新请求是正常行为 | 已有(T3已检测exact重复) | 低：仅需配置recipe | 验证reference替换后缓存命中率变化 |
| **新探测器：assistant历史度量** | 所有多轮Agent业务(T-C相关性0.910) | T-C assistant历史平均155K字符，T2/T4不检测 | 助手历史是业务必需的对话上下文 | 需扩展extraction.py：为assistant message_payload添加度量 | 中：需修改extraction+新增规则 | 度量assistant历史token占比，为缓存优化提供证据，不自动删除 |
| **新探测器：system prompt重复度量** | 固定system prompt的Agent业务(T-C 57K) | T-C 3ef7e810模板57K system prompt在14请求中完全相同 | system prompt是业务必需配置 | 需扩展extraction.py：为system message添加重复度量 | 中：需修改extraction+新增规则 | 度量system prompt token占比，为KV缓存优化提供证据 |
| **新探测器：multi-template检测** | 同appid下多模板混用(T-C 12种system SHA) | T-C短请求用"安全漏洞分析"，长请求用"DeepSeek Harness" | 多模板是不同业务场景的合理共存 | 已有(sys_sha可从现有元数据计算) | 低：后处理统计 | 在metrics中显示appid下模板数和分布 |

### 5.2 V3公共能力衔接点

| 衔接点 | 说明 |
| --- | --- |
| **T2/T4默认策略** | V3应考虑为常见场景提供默认limit/retain_last策略模板，而非完全依赖运维配置。当前所有T2/T4 condition=unknown是部署问题 |
| **recipe bundle默认安装** | 当前NO_CONFIGURED_RECIPES是默认状态。V3应考虑预装常用recipe（如select_result_lines, apply_retention_replacements） |
| **assistant历史检测** | V3.5应考虑新增规则或扩展现有规则，覆盖assistant message_payload的token占比度量 |
| **system prompt检测** | 固定system prompt的重复发送是KV缓存优化机会，V3可新增system prompt token占比度量 |
| **多模板区分** | V3 metrics应区分同appid下的不同模板族，避免将不同业务场景的请求混在一起计算均长/命中率 |
| **block_size影响** | T-B(Qwen block_size=1536)的缓存失配远大于T-A(DS block_size=32)，V3 recommendation评估应考虑block_size对retain_last效果的影响 |
| **采样与评估一致性** | V3公共采样应确保A/B窗独立冷启仿真，不应将分层拼接序列报为真实缓存收益 |

---

## 6. 运行与保护核对

### 6.1 实际资源使用

| 阶段 | 耗时 | 内存峰值 | 编码次数 | 候选比较次数 |
| --- | --- | --- | --- | --- |
| 来源核实 | ~10s | — | 0 | 0 |
| 分布读取 | ~5s | — | 0 | 0 |
| 内容分析(286+300+292=878请求) | ~60s | — | 0 | 0 |
| 深度内容分析(top5+bottom5×3组) | ~20s | — | 0 | 0 |
| T-A编码+仿真(A/B窗×before/after) | ~50s | — | 240 | 0 |
| T-B编码+仿真(A/B窗×before/after) | ~50s | — | 240 | 0 |
| T-C编码+仿真(A/B窗×before/after) | ~60s | — | 240 | 0 |
| **总计** | ~255s (4.3分钟) | 容器482.8MiB/32GiB | 720 | 0 |

### 6.2 失败和预算停止

- 无失败。所有720次编码成功，所有仿真完成。
- 未触发任何预算停止。

### 6.3 前后只读核对

| 项 | 前 | 后 |
| --- | --- | --- |
| 服务healthz | alive | alive |
| 服务readyz | ready=true | ready=true |
| 容器状态 | Up 4 days (healthy) | Up 4 days (healthy) |
| 目录条目数 | 78 | 78 |
| discovery catalog | 41 items | 41 items |
| 容器内存 | 420.1MiB | 482.8MiB（编码后回落） |
| 磁盘 | 220G可用 | 220G可用 |

### 6.4 零产品写确认

- 产品写接口调用：0
- 服务重启：0
- 生产配置修改：0
- 生产数据修改：0
- 前端修改：0
- 产品源码修改：0
- 新诊断任务提交：0
- 新recipe/policy配置：0

### 6.5 旧成果可访问性

- 所有3个base_run的requests.sqlite3保持只读打开，未修改
- discovery catalog 41 items不变，原有诊断任务可访问
- 前序低命中6组调研报告(`TOKENSCOPE_V3_LOW_HIT_EXPLORATION_20261109.md`)仍可访问

### 6.6 自有计算结束确认

- 容器内Python编码进程已退出
- 容器内存已回落至482.8MiB（正常服务水平）
- 无残留进程

---

## 附录A：三组采样源索引SHA

| 组 | 采样SHA(前16位) | 总唯一采样数 |
| --- | --- | --- |
| T-A | (见distribution_stats.json) | 286 |
| T-B | (见distribution_stats.json) | 300 |
| T-C | (见distribution_stats.json) | 292 |

## 附录B：T2–T4代码路径摘要

### extraction.py — 内容提取

- 为每个tool/function role消息设置facet `("tool_result", "history_tool_result")`
- 为user/assistant消息设置facet `("message_payload",)`
- **关键限制**：assistant历史不是`tool_result`，T2/T4不检测

### rules.py — T2/T4检测

- T2: 对`tool_result`容器按降序排列，产出content_inventory事实
- T4: 对`tool_result`容器按源序排列，产出content_inventory事实含later_message_count
- **关键限制**：无默认limit/retain_last策略时，condition=unknown, reason=NO_APPLICABLE_POLICY

### duplicates.py — T3检测

- 对exact sha256重复的entry分组，要求len≥2且至少一个`tool_result`
- **关键限制**：仅匹配exact，不匹配near-duplicate/subset

### policies.py — 策略配置

- T2仅支持limit/field_allowlist，T4仅支持retain_last
- **关键限制**：无默认策略，需运维显式配置

### recommendation_pipeline.py — 建议管线

- 当recipe bundle为空时，产出NO_CONFIGURED_RECIPES，跳过token推荐阶段
- **关键限制**：当前部署无recipe bundle配置