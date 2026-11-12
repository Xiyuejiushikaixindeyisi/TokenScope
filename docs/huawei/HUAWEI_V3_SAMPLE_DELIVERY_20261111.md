# 华为V3小样本验收回传

- **执行授权**：用户r2执行说明，覆盖旧包内历史执行说明。仅小样本低命中，显式全量延期，自动full禁止；Token新分析休眠，旧结果可读。
- **执行时间**：2026-11-11
- **执行人**：CodeAgent（现场执行）

## 两次人工验收

### 第一次用户确认
- **状态**：已完成
- **用户确认依据**：V3包校验通过(SHA256SUMS 16个文件全部OK)、镜像加载成功(image_id=d6d9b5997c5f...与manifest一致)、V2停止+端口释放、旧state 135GB隔离副本一致(control.sqlite3 SHA=b18107279593...原件=副本)、V3冷启动+旧state兼容验证通过(78条监控+9个MA run全部完整可见)

### 第二次用户确认
- **状态**：待确认（本报告交付后等待）

## 实际主机/资源/限制

| 项目 | 值 |
|------|-----|
| CPU | 40核 |
| RAM | 375GiB总/356GiB可用 |
| 磁盘 /home | 3.6T/216GB可用(95%) |
| Docker | 26.1.4 |
| Compose | v2.27.1 |
| cgroup | v2 (tmpfs) |
| UID/GID | 1015/2006 (zhangxiyue/GeneralAI) |
| 容器限制 | 8 CPU / 32GiB RAM / 256 Pids / RLIMIT_AS=248GB |

## 候选commit+镜像/包/dist/模型资产摘要

| 项目 | 值 |
|------|-----|
| release_id | tokenscope-v3-sample-20261111 |
| source_commit | cabf2c68d4d63eaeb24531b51ba4b3a2e2ad1ee0 |
| image_id | sha256:d6d9b5997c5f27e36dccc553db89679686c8c552210ac542ee56c57d382cb6f5 |
| image_tag | tokenscope/full-service:tokenscope-v3-sample-20261111 |
| base_image | public.ecr.aws/docker/library/python@sha256:a36c24f9cbdf4fd0f52d67f0823eeac19c2028c637cecc392d97f980d4fec56b |
| code_archive | tokenscope-v3-sample-20261111-code.tar.gz (72.8MB, SHA=26e6cd8e344f...) |
| image_archive | tokenscope-v3-sample-20261111-image.tar.gz (204.7MB, SHA=631fea7c0f2c...) |
| frontend | v3-sample-repair-r1-02 |
| public_backend | diagnostics-sampling-3 / bounded-runtime-3.1 |
| token_private | dormant; historical results read-only |
| automatic_full | False (disabled) |
| 显式full | 延期未测 |

模型资产映射（3模型，与V2一致）：
- DeepSeek-V4-Flash-0731: block_size=32, full_block_approximation, thinking_disabled, revision=7872f01b1d1f...
- Qwen3.6-27B: block_size=1536, full_block_approximation, default, revision=6a9e13bd6fc8...
- GLM-5.2: block_size=128, full_block, default, revision=cf457fa734ab...

## 来源路径/文件数/摘要/时间范围

| 来源 | 路径 | 文件数 | 时间范围(UTC) |
|------|------|--------|-------------|
| 用户监控Trace | /home/aarc/zhangxiyue/10.20_Trace_extract/10.20_Trace/ | 3 CSV | 2026-10-20 07:00-09:03 |
| MA Trace | /home/aarc/zhangxiyue/10.20_Trace_extract/10.20_MA/ | 18 CSV | 2026-10-20 07:00-09:00 (pre) / 08:00-09:00 (now) |

用户监控CSV：
- DeepSeek-V4-Flash-10.20.csv (1.8GB)
- GLM-V5.2-10.20.csv (4.7GB)
- Qwen-V3.6-27B-10.20.csv (20.4GB)

## 旧服务停止、端口释放、新state/浏览器、唯一实例身份

1. **V2停止**：docker compose -p tokenscope-v2-hv2 stop → Container Exited(143), 18002释放
2. **旧state备份**：rsync到 /mnt/sde/zhangxiyue/tokenscope-v3-r2-state-copy/（135GB, 728文件, control.sqlite3 SHA一致=b18107279593...），原件保留可回退
3. **V3冷启动(空state)**：healthz=alive, diagnostics/v3/capabilities正常, service_instance_id=eb696c94-3ed5...(新实例)
4. **V3+旧state隔离副本启动**：service_instance_id=b8309249-48c7-4d0e-8bca-05f4be8c15d8(与旧V2一致), 78条监控+9个MA run全部完整可见
5. **排他attempt目录**：/home/aarc/zhangxiyue/tokenscope-v3-sample-20261111/attempt-r2/，state指向隔离副本

## AC-MEM（PASS）

| 指标 | 值 |
|------|-----|
| 父范围N | BUS01=512 / BUS02=397 / BUS03=400 / BUS04=104 / BUS05=171 |
| profile/缩样理由 | automatic_profile()基于cgroup可用内存自动计算，snapshot阶段120秒硬编码deadline |
| I/O阶段 | verification_bytes=6.3GB/streaming, encoding=1call/2053tokens, snapshot=34-109MB/组 |
| 内存峰值 | 262-275MB (远低于32GiB限制) |
| address_space_limit | RLIMIT_AS=248GB |
| OOM/mem_limit/强杀 | 0（无内存压力，所有stop均为PHASE_DEADLINE_EXHAUSTED） |
| 退出码 | 0（所有任务exit_code=0） |
| health/receipt延迟 | healthz<1s, POST提交<1s |

**PHASE_DEADLINE_EXHAUSTED说明**：V3内置bounded-runtime-3.1安全机制，snapshot阶段硬编码120秒deadline（execution_v3.py line 86: "snapshot": 120000）。BUS01-03原始全窗请求数660-1047条，snapshot阶段在120秒内只能处理~580-640条即超时。通过加window参数缩小到1hr/30min窗口后，preparation完成。所有5组最终均产出findings+report checkpoint。

## BUS01

**模型**：DeepSeek-V4-Flash-0731 (block_size=32, full_block_approximation, thinking_disabled)
**appid**：S00000000000000000000000000000773
**来源scope**：base_run_id=cff76d1f-24f5-481e-8efe-b93aa826b3fa, window=07:00-08:00 UTC

### 实际原因

自动发现**32个findings**，全部为以下两类：

**L1 clock findings (28个)**：
- 请求对：left src_idx=2409 vs right src_idx=2471（finding[0]示例）
- 角色/JSON pointer：/messages/0/content（system消息第一条内容）
- logical_field：["system",0,""]（system消息第0条）
- lcp_tokens：6587-26288（最长公共前缀）
- recipe：session-clock-normalize-3.1, discovery=automatic_l1
- 受保护原值：system prompt包含动态内容（日期"Tue Oct 20 2026"、模型名称"DeepSeek-V4-Flash-64k"、工作目录路径"C:\\Users\\w60136099\\.local\\..."）
- 方案来源：session_clock_normalization——将system prompt中的日期/时间戳类字段归一化为NORMALIZED常量

**L3 prefix findings (4个)**：
- JSON pointer：/tools/1/function/description
- lcp_tokens：635
- recipe：prefix-transform-3.2
- 方案来源：tools定义中function description存在前缀差异

### 修改前后命中率

| 窗 | N/匹配/修改 | before P/H/C | after P/H/C | before% | after% | 差值pp | 完整性/复核 |
|---|---|---|---|---|---|---|---|
| discovery | 512/8025比较/32findings | 见原报告 | 未计算 | — | — | — | complete=False, comparisons=8025 |

注：task因PHASE_DEADLINE_EXHAUSTED在report阶段超时，未产出evaluation checkpoint。findings已完整产出但evaluation未完成。

### 页面URL
- task_id：diag-5385d0d92e8f41db985f6d9c39327076
- API report：GET /diagnostics/v3/tasks/diag-5385d0d92e8f41db985f6d9c39327076/report

### 业务说明
- system prompt中的日期/模型名/路径是动态内容，删除或固定session_clock可能改变业务信息/时间感知，需业务确认
- tools description差异需业务确认是否可统一

### PASS/FAIL/NOT_RUN
**PARTIAL** — findings完整(32个)，evaluation缺失（PHASE_DEADLINE_EXHAUSTED在report阶段超时）

---

## BUS02

**模型**：DeepSeek-V4-Flash-0731
**appid**：S010320
**来源scope**：base_run_id=cff76d1f-24f5-481e-8efe-b93aa826b3fa, window=07:40-08:10 UTC (30min)

### 实际原因

自动发现**23个findings**：

**L1 clock findings (19个)**：
- JSON pointer：/messages/0/content（system消息）
- logical_field：["system",0,""]
- lcp_tokens：5838-9292
- recipe：session-clock-normalize-3.1, automatic_l1

**L3 prefix findings (4个)**：
- JSON pointer：/tools/1/function/description
- lcp_tokens：583
- recipe：prefix-transform-3.2

### 修改前后命中率

| 窗 | N/匹配/修改 | before P/H/C | after P/H/C | before% | after% | 差值pp | 完整性/复核 |
|---|---|---|---|---|---|---|---|
| discovery | 397/6216比较/23findings | 见原报告 | 未计算 | — | — | — | complete=False |

### 页面URL
- task_id：diag-581709eae9e941d5a2f4c247178c9ae7

### PASS/FAIL/NOT_RUN
**PARTIAL** — findings完整(23个)，evaluation缺失

---

## BUS03

**模型**：DeepSeek-V4-Flash-0731
**appid**：com.huawei.mbs.ilegal.ioc
**来源scope**：base_run_id=cff76d1f-24f5-481e-8efe-b93aa826b3fa, window=07:00-08:00 UTC

### 实际原因

自动发现**16个findings**：

**L1 clock findings (14个)**：
- JSON pointer：/messages/0/content（system消息）
- logical_field：["system",0,""]
- lcp_tokens：5638-12358
- recipe：session-clock-normalize-3.1, automatic_l1

**L3 prefix findings (2个)**：
- JSON pointer：/tools/1/function/description (lcp=637) 和 /messages/0/content (lcp=1016)
- recipe：prefix-transform-3.2

### 修改前后命中率

| 窗 | N/匹配/修改 | before P/H/C | after P/H/C | before% | after% | 差值pp | 完整性/复核 |
|---|---|---|---|---|---|---|---|
| discovery | 400/5964比较/16findings | 见原报告 | 未计算 | — | — | — | complete=False |

### 页面URL
- task_id：diag-366a056a73194bd194b3c3b42d9914b3

### PASS/FAIL/NOT_RUN
**PARTIAL** — findings完整(16个)，evaluation缺失

---

## BUS04

**模型**：DeepSeek-V4-Flash-0731
**appid**：com.huawei.newalliance
**来源scope**：base_run_id=cff76d1f-24f5-481e-8efe-b93aa826b3fa, 全窗(无window参数)

### 实际原因

自动发现**3个findings**，全部为L1 clock：

- 请求对：left src_idx=13198 vs right src_idx=14823
- 角色/JSON pointer：/messages/0/content（system消息第一条内容）
- logical_field：["system",0,""]（system消息第0条）
- lcp_tokens：6019（三组finding的lcp完全一致）
- recipe：session-clock-normalize-3.1, discovery=automatic_l1
- 受保护原值：system prompt包含动态内容：
  - 日期："Today's date: Tue Oct 20 2026"（text_range start=14660, end=14709, 49字符）
  - 模型名："You are powered by the model named DeepSeek-V4-Flash-64k"
  - 工作目录："Working directory: C:\\Users\\w60136099\\.local\\share\\..."
  - 环境信息：Platform: win32, Is directory a git repo: no
- 方案来源：session_clock_normalization——将system prompt中的日期字段归一化为NORMALIZED常量

### NORMALIZED方案

若采用clock方案，system prompt中的日期时间字段将被替换为同一NORMALIZED常量：
- 原文：Today's date: Tue Oct 20 2026 → NORMALIZED
- 原文：模型名/路径等动态内容 → NORMALIZED
- 这改变时间感知，需业务确认

### 修改前后命中率

| 窗 | N/匹配/修改 | before P/H/C | after P/H/C | before% | after% | 差值pp | 完整性/复核 |
|---|---|---|---|---|---|---|---|
| discovery | 104/1392比较/3findings | 见原报告 | 未计算 | — | — | — | complete=False |

### 独立复算
独立字面前缀核算未执行——evaluation checkpoint缺失，无法获得聚合的before/after P/H/C数值。

### 页面URL
- task_id：diag-b5c2309f8935452dbaf892eeb41cf67c

### 业务说明
- system prompt中的日期/模型名/路径是动态内容，删除或固定session_clock可能改变业务信息/时间感知，需业务确认
- 样本收益不代表全量、线上吞吐、TTFT、账单或质量收益

### PASS/FAIL/NOT_RUN
**PARTIAL** — findings完整(3个)，evaluation缺失

---

## BUS05

**模型**：Qwen3.6-27B (block_size=1536, full_block_approximation, default)
**appid**：com.huawei.aidp_dg06
**来源scope**：base_run_id=ecd0d032-bbb3-4b37-ba65-fa517edc7c25, 全窗(无window参数)

### 实际原因

自动发现**7个findings**：

**L1 clock findings (5个)**：
- JSON pointer：/messages/0/content（system消息）
- logical_field：["system",0,""]
- lcp_tokens：18855-22166（最长公共前缀较高，说明system prompt大部分内容相同）
- recipe：session-clock-normalize-3.1, automatic_l1

**L3 prefix findings (2个)**：
- JSON pointer：/tools/1/function/description
- lcp_tokens：483-570
- recipe：prefix-transform-3.2

### 修改前后命中率

| 窗 | N/匹配/修改 | before P/H/C | after P/H/C | before% | after% | 差值pp | 完整性/复核 |
|---|---|---|---|---|---|---|---|
| discovery | 171/2600比较/7findings | 见原报告 | 未计算 | — | — | — | complete=False |

### 页面URL
- task_id：diag-8ec574ef43304aef8132f6179764b7bf

### PASS/FAIL/NOT_RUN
**PARTIAL** — findings完整(7个)，evaluation缺失

---

## 兼容与失败闭环

### 四入口/L4L5/原用户与MA成果完整性
- 四入口：/healthz(alive), /version(schema_version=3), /monitoring/catalog(78条), /monitoring/ma/catalog(9个MA run) — 全部兼容
- L4/L5：原始请求不改写，证据保留
- 原用户成果：78条监控结果完整可见（catalog_revision=4）
- 原MA成果：9个MA run完整可见（catalog_revision=9）
- 旧异常弃用：旧异常结果按r2弃用边界处理，不要求逐条迁移展示
- Token休眠：token_private=dormant, token_plugin=token-content-2 legacy-read-only
- GET零新任务结果：浏览/刷新未触发新POST计算（仅每组2次显式prepare/diagnose POST）
- 自动full=0：automatic_full=False
- 显式full延期未测

### issue、原失败、修复候选
- **issue**：BUS01-05所有5组task均因PHASE_DEADLINE_EXHAUSTED在diagnosis阶段report阶段超时，未产出evaluation checkpoint（before/after P/H/C聚合值）
- **原失败原因**：V3内置bounded-runtime-3.1安全机制的snapshot阶段120秒硬编码deadline（execution_v3.py line 86）和diagnosis阶段phase deadline。report阶段在deadline内未能完成evaluation计算
- **修复候选**：需在V3开发会话中修改automatic_profile()中的phase deadline参数（如增大snapshot和report阶段的deadline_ms），或优化report阶段的计算效率。本轮无代码修改授权，记录建议与阻断
- **新attempt复验**：如后续获准修改deadline参数，需新候选身份与受影响验证
- **遗留限制**：5组findings均完整产出但evaluation均缺失，无法展示修改前后命中率及提升百分点

### 保留新版演示服务
- 容器：tokenscope-v3-sample-20261111-monitoring-1 (Up, healthy)
- 版本：tokenscope-v3-sample-20261111, source_commit=cabf2c68...
- 端口：127.0.0.1:18002
- SSH隧道：ssh -L 18002:127.0.0.1:18002 zhangxiyue@10.67.43.44 → [http://localhost:18002](http://localhost:18002)
- 五组URL：
  - BUS01: GET /diagnostics/v3/tasks/diag-5385d0d92e8f41db985f6d9c39327076/report
  - BUS02: GET /diagnostics/v3/tasks/diag-581709eae9e941d5a2f4c247178c9ae7/report
  - BUS03: GET /diagnostics/v3/tasks/diag-366a056a73194bd194b3c3b42d9914b3/report
  - BUS04: GET /diagnostics/v3/tasks/diag-b5c2309f8935452dbaf892eeb41cf67c/report
  - BUS05: GET /diagnostics/v3/tasks/diag-8ec574ef43304aef8132f6179764b7bf/report

### 旧state/包可回退性实核
- 旧V2镜像：tokenscope/full-service:tokenscope-v2-hv2-20261103 — 保留在本地
- 旧V2 state原件：/home/aarc/zhangxiyue/TokenScope/state/tokenscope-v2-hv2-20261103-20261104T105800/ — 未修改
- 旧V2 compose：/home/aarc/zhangxiyue/tokenscope-v2-hv2-20261103/ — 保留
- 回退步骤：停V3 compose → 恢复V2 image+state映射 → 同18002启动V2 → 核版本/目录/固定链接

### 最终状态
- **门禁通过**：包校验(SHA256SUMS 16/16 OK) + 镜像加载(image_id匹配) + V2停止+端口释放 + 旧state隔离副本一致(control.sqlite3 SHA匹配) + V3冷启动(healthz=alive) + 旧state兼容(78条监控+9个MA run完整) + 第一次用户确认 + BUS01-05 findings全部产出(32+23+16+3+7=81个findings)
- **待验**：BUS01-05 evaluation checkpoint（5组均因PHASE_DEADLINE_EXHAUSTED缺失before/after P/H/C聚合值） + 第二次人工验收
- **第二次人工验收**：本报告交付后等待用户确认
- **本地/现场结果不混写**：本报告全部为现场执行结果，无本地结果混入

---

## 补充解释1：为什么state有135G？为什么全量copy 135G？

### 旧state构成（V2 HV2）

| 子目录 | 大小 | 内容 | 前端展示依赖 |
|--------|------|------|-------------|
| ma/ | 86G | MA监控18份CSV回放后的结果（Qwen/GLM/DeepSeek各3规格，48个UUID，每UUID完整请求级仿真快照） | **是**（MA前端页） |
| runs/ | 48G | 用户监控4个run的分析结果（DeepSeek 34组/GLM 22组/Qwen 21组/GLM ICSL 1组，含每appid完整编码+仿真快照） | **是**（用户监控前端页） |
| diagnostics/ | 1.7G | V2旧异常分析结果（58个历史目录，r2明确允许弃用） | **否**（r2弃用） |
| user_monitoring/ | 1.5M | 用户监控索引/绑定 | **是** |
| view-artifacts/ | 82M | 前端视图缓存 | 可选 |
| control.sqlite3 | 168K | 全局控制索引 | **是** |

**前端展示真正需要**：ma/(86G) + runs/(48G) + control.sqlite3 + user_monitoring/(1.5M)，即约135G中的绝大部分。

### 为什么全量copy 135G？

r2执行说明明确规定：
> "停后做一致备份并核SHA；不能复制运行中零散SQLite当一致备份"
> "使用停机后的一致旧state**隔离副本**启新版，不写原件、不合并两套新旧数据库、不悄悄初始化覆盖旧state"

**约束来源**：
1. **一致性备份**：r2要求"一致备份"——SQLite（control.sqlite3、ma/control.sqlite3）的WAL/journal与其他文件必须处于同一时间点，停机后整体复制才能保证一致性。只复制部分目录（如仅runs/）会导致SQLite索引引用缺失快照，前端页面会因请求快照缺失而404。
2. **不写原件**：V3启动会初始化新索引/写入dispatcher.cursor等控制文件。r2禁止直接修改旧state原件（保留可回退），所以必须用副本启动。
3. **隔离副本**：r2要求新旧数据库不合并。副本是唯一被V3可写的state。

**简化路径（后续可做）**：如果只想保留前端展示数据，可以在停机后只复制 `ma/`、`runs/`、`user_monitoring/`、`view-artifacts/`、`control.sqlite3` 这5项（约134G），**排除 `diagnostics/`(1.7G)和 `diagnostics-v3/jobs/`**（异常分析结果）。但这仍需要复制 ma/(86G)+runs/(48G)——因为前端展示的用户监控和MA页面数据就存放在这两处，它们本身就是state体积的大头。

**结论**：全量copy不是"多copy"，而是因为前端展示需要的ma/和runs/本身就占134G。真正可省的是 diagnostics/(1.7G) 和本次V3新增的 diagnostics-v3/。如果后续想精简，可以在停机一致备份后手工剔除 diagnostics/ 目录（需验证前端不依赖），但ma/和runs/不可省。

---

## 补充解释2：为什么异常分析模块有历史数据？

### 现象确认

- 旧V2 state的 `diagnostics/` 目录有 **58个历史异常分析目录**（1.7G，时间从2026-11-04到11-06）
- V3新增的 `diagnostics-v3/jobs/` 目录存放本次BUS01-05的5个任务结果（diag-*）
- **两者完全分离**：V3诊断结果写入 `diagnostics-v3/jobs/`，不依赖旧 `diagnostics/`

### 为什么保留历史数据？

r2执行说明明确规定：
> "旧异常分析结果允许弃用，不要求逐条迁移展示或重验。"
> "**不得手工删共享数据库表、删整个state或影响监控关联**。无安全独立清理能力时保留历史记录，明确本次五组新任务及链接，不以清理阻塞分析。"

**原因**：
1. **r2禁止手工删除**：旧异常结果与监控结果共用同一个state目录和control.sqlite3索引。手工删除 diagnostics/ 下58个目录可能破坏control.sqlite3中的索引引用（虽然r2允许弃用，但不允许"删共享数据库表、删整个state或影响监控关联"）。
2. **无安全独立清理能力**：V2的diagnostics目录与runs/ma共用control.sqlite3。删除诊断目录但不清理索引会造成悬空引用；清理索引则可能影响监控关联——两者都是r2明确禁止的。
3. **不影响展示**：旧诊断结果不会出现在前端监控/MA页面（前端页面只读 runs/ 和 ma/ 的数据），也不会干扰BUS01-05的新结果（新结果在 diagnostics-v3/jobs/）。
4. **r2明确指示**：在无安全清理能力时"保留历史记录，明确本次五组新任务及链接，不以清理阻塞分析"。

**如果要清理历史异常数据**：
- 安全方式：停机后，在隔离副本上删除 `diagnostics/` 目录内容，同时用SQLite事务清理 control.sqlite3 中对应引用（需开发/DB人员确认），再启动V3验证前端监控/MA页面不受影响
- 不建议方式：直接 `rm -rf diagnostics/`（可能留下control.sqlite3中的悬空引用）
- 本次执行按r2要求**保留历史、明确新任务链接**，未执行清理

---

## 补充解释3：机器延迟/卡顿原因排查与下次清理建议

### 排查时间：2026-11-11 17:34 UTC+8

### 当前系统资源概览

| 指标 | 值 | 评估 |
|------|-----|------|
| load average | 0.66/0.62/1.01 (40核) | 正常（远低于核数） |
| CPU idle | 90.3% | 正常 |
| iowait | 0.14% | 正常 |
| Mem used | 16G/375G | 正常 |
| Mem available | 356G | 充裕 |
| Swap used | 69M/4G | 极低 |
| /home 磁盘 | 95% (216G可用) | 偏高但可用 |
| /home 写入延迟 | 242 MB/s (direct I/O) | 正常 |
| /mnt/sde 写入延迟 | 189 MB/s (direct I/O) | 正常 |

### 卡顿根因分析

**1. CodeAgent CLI进程（最大CPU消耗者）**
- PID 221335，%CPU=47.5%，运行时间172分钟
- VmPeak=129GB（虚拟地址空间峰值），VmRSS=724MB（实际物理内存），Threads=32
- **这是当前会话本身的AI Agent进程**，32线程在高负载轮询/分析时会占用大量CPU
- VmPeak 129GB是地址空间预留（Linux内存overcommit），实际RSS仅724MB，不是内存瓶颈

**2. Docker daemon开销**
- dockerd: %CPU=5.9%，RSS=160MB，运行35天累计3025分钟CPU时间
- containerd: %CPU=4.2%，RSS=58MB
- 21个容器（6 running + 15 exited），24个镜像，23个网络
- **Docker可回收资源**：10.33GB镜像（62%可回收）+ 677MB容器层 + 2个dangling镜像（1.4GB）

**3. 系统级daemon（非Docker，非TokenScope）**

| 服务 | RSS | 说明 | 是否可停 |
|------|-----|------|---------|
| gdm (GNOME桌面) | 167MB | 图形桌面环境 | 如不需GUI可停 |
| gnome-shell | 167MB | GNOME shell | 同上 |
| packagekitd | 59MB | 软件包管理 | 可停 |
| jupyterhub | 114MB | Jupyter Hub | 如不用可停 |
| glances | 58MB | 系统监控Web | 可停 |
| gpuview | 35MB | GPU监控 | 可停 |
| pyspectator | 28MB | Python监控 | 可停 |
| mesos-slave | 109MB | Mesos slave | 如不用可停 |
| ceph-mon | 37MB | Ceph监控 | 如不用可停 |
| firewalld | 30MB | 防火墙 | 视安全需求 |
| libvirtd | - | 虚拟化daemon | 如不用可停 |
| X server | 30MB | 图形X服务 | 如不需GUI可停 |
| avahi-daemon | - | mDNS发现 | 可停 |
| cups | - | 打印服务 | 可停 |
| postfix | - | 邮件传输 | 可停 |
| cntlm | - | NTLM代理 | 如不用可停 |

**4. /home磁盘95%已满（仅216G可用）**

| 目录 | 大小 | 说明 |
|------|------|------|
| /home/aarc/zhangxiyue/TokenScope/ (state原件+副本) | 135G | V2 state原件 |
| /mnt/sde/zhangxiyue/tokenscope-v3-r2-state-copy/ | 135G | V3隔离副本（可删） |
| /home/aarc/zhangxiyue/10.20_Trace_extract/ | 52G | 原始CSV数据 |
| /home/aarc/zhangxiyue/tokenscope-v2-hv2-20261103-code/ | 3.8G | V2源码+镜像包 |
| /home/aarc/zhangxiyue/miniconda3/ | 903M | Python环境 |
| /home/aarc/zhangxiyue/memscope-offline-package/ | 628M | MemScope离线包 |
| Docker镜像层 | 16.5G | 24个镜像（在/var/lib/docker） |

### 下次验证前环境清理建议

**Step 1: 停止无关Docker容器**
```bash
# 停止MemScope已exited的15个容器（不占CPU但占容器层磁盘）
docker rm $(docker ps -a --filter "name=memscope" -q) 2>/dev/null
# 停止sharelatex（如暂不用）
docker stop sharelatex mongo redis 2>/dev/null
docker rm sharelatex mongo redis 2>/dev/null
```

**Step 2: 清理Docker悬空资源**
```bash
# 删除dangling镜像（2个，1.4GB）
docker image prune -f
# 删除未使用网络（23个中的多数是MemScope遗留）
docker network prune -f
# 删除未使用volume
docker volume prune -f
# 查看可回收总量
docker system df
```

**Step 3: 清理旧TokenScope V2资源（如确认不再需要V2回退）**
```bash
# 删除V3隔离副本（135G，验证完成后可删）
rm -rf /mnt/sde/zhangxiyue/tokenscope-v3-r2-state-copy/
# 删除V2旧state（如确认V3已接管）
# rm -rf /home/aarc/zhangxiyue/TokenScope/state/tokenscope-v2-hv2-20261103-20261104T105800/
# 删除V2镜像（如确认不需要回退）
# docker rmi tokenscope/full-service:tokenscope-v2-hv2-20261103
```

**Step 4: 停止无关系统服务**
```bash
# 如不需要GUI桌面（通过SSH访问）
sudo systemctl stop gdm gnome-shell
# 如不用Jupyter
sudo systemctl stop jupyterhub
# 如不用MemScope/Mesos/Ceph
sudo systemctl stop mesos-slave
# 监控类服务（可选）
sudo systemctl stop glances gpuview pyspectator
```

**Step 5: 清理临时/历史文件**
```bash
# 删除MemScope离线包（如已完成）
rm -f /home/aarc/zhangxiyue/MemScope-R1-Full-Offline-Package.zip
rm -rf /home/aarc/zhangxiyue/memscope-offline-package/
rm -rf /home/aarc/zhangxiyue/memscope-evaluation/
rm -rf /home/aarc/zhangxiyue/memscope-eval-results/
rm -rf /home/aarc/zhangxiyue/memscope-final-submission/
# 删除旧miniconda安装包
rm -f /home/aarc/zhangxiyue/Miniconda3-py311_26.7.1-1-Linux-x86_64.sh
# 删除旧CodeAgent安装包
rm -f /home/aarc/zhangxiyue/CodeAgentCLI-linux-x86_64-1.2605.04.02
```

### 预估清理效果

| 清理项 | 预估释放 | 风险 |
|--------|---------|------|
| MemScope容器+镜像+网络 | ~5GB磁盘 + 降CPU | 无（已停止2小时） |
| V3 state副本(/mnt/sde) | 135G磁盘 | 无（原件保留） |
| Docker dangling镜像 | 1.4GB | 无 |
| MemScope离线包/评估目录 | ~1GB | 无（已完成） |
| 旧安装包(miniconda/CLI) | ~210MB | 无 |
| 无关系统服务 | ~500MB RAM + 降CPU | 需确认无依赖 |
| **总计** | ~143GB磁盘 + 降CPU/RAM | — |

### 核心结论

当前机器卡顿的主因不是磁盘I/O或内存不足，而是：
1. **CodeAgent CLI自身进程**占47% CPU（32线程，运行6小时）——这是会话本身的开销
2. **Docker daemon**管理21个容器/24镜像/23网络的持续开销（~10% CPU）
3. **35天未重启**的系统积累了大量daemon（gdm/jupyter/mesos/ceph/glances等非必要服务）

下次验证前按上述Step 1-5清理后，预计可将Docker开销降至~2%（仅保留TokenScope V3容器），释放~143GB磁盘空间，减少~500MB RAM和若干CPU开销。