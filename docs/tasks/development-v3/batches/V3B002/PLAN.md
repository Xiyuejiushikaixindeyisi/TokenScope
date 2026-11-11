# V3B002 PLAN — 受控执行、资源profile与取消恢复

状态：**CLOSED — 本批公共执行/来源准备门禁**，2026-11-10。用户两条底线的完整诊断/前端验收仍未关闭。前置[V3B001](../V3B001/CLOSE.md)；设计r1 D3/D7；[条件授权](../../../product-v3/V3_REVIEW_DECISION_20261110.md)及两项修订已落实。实际执行ID 01a1c449-6a9b-7a83-912a-5a9ff77c703d。

## 最终代码方案与接入

| 文件/函数 | 调用与失败语义 |
| --- | --- |
| runtime_v3.RuntimeProfile3 / BudgetLedger.reserve_many / enter | 显式版本profile；全任务预算先预留、原子计数；总/阶段deadline、软RSS与取消分开。guard_json在json.loads前限制字节/深度/节点。 |
| execution_v3.automatic_profile / calibrated_sample | 当时可用内存65%作AS上限，低于512MiB判环境不足；AS<1GiB时单线程。模型VmPeak后保留128MiB安全余量，再以16/256扩张系数确定raw/P和条数；正余量自动缩窗，无固定300。 |
| source_preparation.PreparationIO / prepare_snapshot | 原两次seal保留；新增计费/阶段/词法准入callback、模型校准callback；全部选键后才读正文，所有attempt共用ledger。 |
| worker_v3.enforce / run / main | 固定模块与受控job引用；RLIMIT_AS/FSIZE/CPU/CORE，PDEATHSIG，禁止fork/命令派生；固定资产校准、有限次缩窗、封存sample checkpoint，失败只写安全原因。 |
| supervisor_v3.WorkerSupervisor.run | 单独进程组，25ms监督；取消/总及阶段超时/危险内存止损；软内存释放后允许有界重试，不能误记user_cancel；只接收小对象和完整检查点。 |
| PreparationStore.claim/cancel/finish/recover/retry | SQLite事务唯一终态、幂等/冲突、取消先于发布则stopped，发布后取消不改终态；恢复running为interrupted并仅保留验证后的checkpoint，retry新身份。 |
| service_v3.PreparationService.process_next | 持原worker.lock直到子进程退出；API线程只登记/查询/取消。目录大小估计只读文件元数据且离开HTTP路径，正文/hash在受控worker；profile/结果绑定task。 |
| api/diagnostics_v3 / diagnostics_policy_v3 / app / cli | 64KiB意图准入、实例身份、prepare/receipt/execution/cancel/retry；默认V3队列，旧POST写入口统一拒绝。Token运行插件与业务bundle不加载，旧GET保留。 |
| encoding.EncodingContext(cpu_budget=...) | 只收窄CPU并发；ModelEncoder既有身份本来排除cpu_budget，其余profile/资产/模板和基线验证不变。 |

不改冻结sampling-3/V1/V2文件。新RuntimeProfile3/Execution3为内部增量对象，未把prepare称完整诊断。capabilities明确preparation_enabled与execution_enabled=False；后续B003/B005接正常低命中链。legacy_diagnostics=True仅隔离历史回归使用，CLI/HTTP无此开关。

## 校准与门禁

本机WSL Linux、cgroup不可写，硬限制明确为**地址空间AS，不是RSS**；RSS另由监督采样及OS high-water记录，后者可能含fork/exec前继承峰值，不冒称模型独占峰值。环境/资产/profile见[TESTS](TESTS.md)和候选摘要。

首轮模型加载、三模型真实prepare、固定失败内存包络复验、真实取消/阶段超时/父死亡/文件限制和ENOSPC故障注入均已测试。详见[ISSUES](ISSUES.md)、[CLOSE](CLOSE.md)。单条不可容纳/固定开销超支持环境明确失败，正常父范围大则自动缩窗完成。完整诊断AC-MEM、五业务clock和收益尚待B003–B007。

代码问题已闭环；旧资源测试固定输出路径导致三份历史校准JSON覆盖，已修输出隔离，但历史内容未恢复，I04持续披露，不把损失写成“全部保留”。

## 下一批与回退

B003只消费有界快照、同一BudgetLedger/EncodingContext和受控worker，不回源全量读取、不新增Tokenizer/队列。B004/B005仍需把各领域操作实际接到计费/完整窗checkpoint，不拿本批通用计数测试替代最终端到端。

回退仅禁用本批V3执行注册和有归属源码，保留新样本只读能力、产物和旧结果；不恢复Token/旧自动full、不覆盖其他dirty、不删state。当前无产品服务/打包/现场动作需回退；测试临时产物保留。下一批按既有授权推进，无需再询问启动。
