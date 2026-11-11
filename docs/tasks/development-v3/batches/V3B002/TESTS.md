# V3B002 TESTS — 实际记录

候选 **v3b002-local-1**，HEAD 9a071c87b517490e497aa6cc1e53ec066bb4ede0加未提交工作树，不是新的Git提交。[40个源码/测试/新契约文件摘要](../../../../../artifacts/validation/development-v3/V3B002/attempt-06/candidate.json)。本地WSL/Python3.11/.venv，cwd /home/zhangxiyue/TokenScope；三模型本地锁定资产，无下载/华为数据/镜像。

## 门禁映射

| ID | 实际测试/证据 | 结论 |
| --- | --- | --- |
| T01 | test_real_automatic_prepare_no_memory_kill_and_responsive_api；test_initial_failed_memory_envelope_reproduced_with_smaller_cpu；B001来源/登记回归 | PASS本批prepare：HTTP无source读取；1100父记录自动有界选择、三模型完成、无OOM/内存kill。完整诊断AC-MEM待B007。 |
| T06 | test_every_budget_before_action_boundary_and_total（各预算−1/=limit/+1/原子多计费）、JSON词法、tiny_headroom、真实AS与spawn denial、cooperative_memory_release | PASS公共资源边界；after/领域操作仍由B003–B005接入并验证，不称已完成收益计算。 |
| T07 | real_blocked_worker(cancel/deadline/phase)、http_cancel_running_worker_and_shared_lock、parent_death_kills_its_worker、store发布竞态 | PASS真实子进程、API取消/停止阈值、单昂贵worker锁、父死亡无存活worker。 |
| T08 | journal_disk_full_retains_prior_committed_evidence、real_worker_file_limit、崩溃checkpoint、recovery_salvages_only_committed_checkpoint | PASS：ENOSPC故障注入+实际FSIZE限制，非灌满系统磁盘；半文件不可见，完整前缀保留。 |
| T09 | store_cancel_publish_race_retry_recovery、finished_task_ignores_late_cancel、HTTP实例/幂等、default_app_blocks_old_execution | PASS：不重跑旧working，新retry身份；旧写/Token队列不由生产调度执行，历史fixture明确legacy模式。 |

## 实测资源

最终[原始测量索引](../../../../../artifacts/validation/development-v3/V3B002/attempt-06/resource-summary.json)链接各原始延迟、profile/job、资产和样本身份；不可把不同环境样本数冻结为默认值。

| 用例 | 父/选中 | AS硬上限bytes | 监督采样RSS峰值bytes | worker总耗时 |
| --- | --- | --- | --- | --- |
| GLM-5.2自动 | 1100 / 488 | 1280270950 | 493391872 | 5.269s |
| DeepSeek自动 | 12 / 12 | 1255103283 | 276496384 | 1.088s |
| Qwen自动 | 12 / 12 | 1222206668 | 507752448 | 3.074s |
| GLM首轮失败上限复验 | 12 / 12 | 794374963 | 499277824 | 2.940s |
| Qwen首轮失败上限复验 | 12 / 12 | 789047500 | 507789312 | 2.890s |

以上均completed、exit_code=0、forced_termination=false。每组在实际model阶段开始后测20次health+20次receipt，各P95≤0.005442s、全部成功。attempt-04 HTTP取消0.02245s、停止0.56468s；attempt-06同门槛复测通过，原值在该测试job/cancel-measurements.json。受控故障用例故意取消/杀父/触发硬限制，不能与正常大源的OOM=0混为一项。

校准早期calibration-01仅原生模型加载/短编码，不能当全链内存证明。OS ru_maxrss可能含pre-exec高水位；表内为父监督25ms采样，不假称连续RSS硬限。AS硬限由真实进程setrlimit及超分配负例验证。

## 运行与修复历史

| Attempt | 实际结果 | 处理 |
| --- | --- | --- |
| 01 | 25 passed / 2 failed，22.10s；初次ruff行长/排序、mypy缺注解 | GLM/Qwen固定开销拒绝；规范和类型问题修复，保留日志。 |
| 02 | 27 passed，19.67s | 低内存线程收窄后三模型成功，但环境可用量变化，尚不足证明I03修复。 |
| 03 | 111 passed，267.46s；ruff/mypy/schema通过 | 包含B001及旧诊断/Token兼容回归。旧资源测试覆盖历史三份校准JSON，I04记录；后续修固定输出路径。 |
| 04 | 37 passed，37.11s；ruff/mypy/diff通过 | 新增阶段超时、实际model期间响应、软内存协作、HTTP取消/父死亡/恢复/文件限；固定输出改tmp_path后16条用例复测。 |
| 05 | 1 passed / 1 failed / 14 deselected，13.34s | 固定首轮AS上限重放仍有Qwen拒绝，证实仅减线程不充分；不是skip或通过。 |
| 06 | **39 passed，0 failed/skip，34.20s**；ruff/mypy132源码/schema通过 | 取消16MiB任意最小余量门槛，保持128MiB安全储备及扩张系数，支持更小样本；相同AS上限两模型均完成。 |

每轮同一FastAPI/httpx依赖弃用warning，无隐藏失败。03之后未影响历史执行逻辑；04复测输出路径修复，06复测全部当前V3资源代码和固定失败包络。无需重复耗时旧Token全集去证明无关参数变化。

确切命令记录在[commands.txt](../../../../../artifacts/validation/development-v3/V3B002/attempt-06/commands.txt)，日志分别保留attempt-01–06；每次basetemp独立。source_reports SHA及CHECK SHA与接入时相同，冻结旧契约无修改。历史校准日志损失例外见ISSUES-I04，不冒称所有旧证据均未变。

## 尚未宣称完成

这些是准备/执行与组件API测试，未启动产品浏览器E2E。自动clock、A/B实算、前端、BUS01–05与完整AC-MEM仍未通过；B007须用唯一候选冷启、新state/浏览器重新验证。
