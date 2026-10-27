# B005 实测与回归

代码0.1.0.dev5/schema2，CPython3.11.16，WSL本机，uv.lock/编码资产锁固定；生产CSV未提供且不索取。用户授权的合成数据：seed271027，NumPy版本记录在manifest，每模型5个appid；常规长度Poisson(512)文本单元、长请求Poisson(66000)、200K/220K边界、工具/Unicode/重复/坏行。单元是重复文本“ token”，实际Token数由各模型编码确定，不能把文本抽样值冒充实际Token数。

## 最终门槛

命令：`.venv/bin/python scripts/validation/check_batch.py B005`：**145 passed**，pytest/ruff/format/mypy退出码0；报告 `artifacts/validation/monitoring/B005/20261027T035144Z-report.json`。源码/测试/脚本/锁已在source-manifest和source-snapshot保存。

实际HTTP进程命令：`.venv/bin/python scripts/validation/run_monitoring_e2e.py`，退出码0；[最终报告](../../../../../artifacts/validation/monitoring/B005/20261027T035327Z/report.json)。同目录包含输入manifest、三份合成CSV、服务日志、逐模型metrics与状态产物。

| 模型 | CSV行数 | 有效请求 | 提交至完成墙钟 | 最大P | 完成产物磁盘 |
| --- | --- | --- | --- | --- | --- |
| GLM-5.2 | 9994 | 9972 | 19.74s | 220030 | 281.6 MiB |
| Qwen3.6-27B | 10112 | 10089 | 20.81s | 220041 | 284.0 MiB |
| DeepSeek-V4-Flash-0731 | 10131 | 10107 | 22.20s | 220352 | 286.1 MiB |

服务进程采样峰值RSS 1174.26 MiB；线程总数峰值13（含HTTP/控制线程，不能等同活跃计算并行）。实际affinity限制8个CPU，Rust8、BLAS/OMP1；CPU清单和阶段耗时在报告。提交至完成包含排队轮询误差，产物elapsed_scope注明内部计时边界。重启恢复有独立标记，不把恢复前统计阶段耗时说成完整执行耗时。

## 断言与边界

- HTTP后台实际处理三模型；每模型5个appid，质量计数与生成清单完全匹配。全部请求J/P/H/C/O守恒、全部组精确nearest-rank；每appid前30条用完整历史Token序列独立参考比较H/C。20组随机差分单测覆盖更广B/CP/MTP边界。
- 1K/2K/5K箱数量守恒、≥200K尾部、分页rank；CLI与HTTP相同；运行中并发查询上一已完成结果。
- batch1/256三模型逐请求IDs分片摘要、J/P/H/C/O、轻量证据、事件和聚合完全一致；错误模式/错资产/重复/坏行/未完成不可见。
- 双worker文件锁、封存后事务失败恢复、损坏分片拒绝恢复、模拟磁盘写失败、schema1→2迁移；真实独立服务进程在运行中SIGKILL后重启，该任务interrupted且既有结果不变。
- 原始JSON不回显到普通错误；产物GET前后mtime不变；按需详细IDs摘要匹配。

首轮139通过/1失败为测试写错既有错误码，已修正；资源字段误插入参数被mypy捕获后修复。所有失败日志保留。初轮无affinity的E2E报告仅作对比，最终结论以上述035327Z为准。本机结果不等同于目标V100性能/旧内核兼容性或真实数据验收。

最终增量：加入release_id/source manifest版本元数据与3项打包审批/白名单测试后145项通过，实际HTTP E2E重新运行并在报告绑定源码SHA。此轮仅增加版本身份，不改变J/P/H/C/O语义；全部旧失败日志保留。
