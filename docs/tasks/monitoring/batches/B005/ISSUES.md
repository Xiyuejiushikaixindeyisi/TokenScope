# B005 问题记录

| ID | 发现与处理 | 状态 |
| --- | --- | --- |
| B005-01 | 新故障测试预期MISSING_COLUMNS，但既有契约错误码为INVALID_CSV_HEADER；实际运行正确failed，修正测试，不改变错误码 | 已修复，141回归通过 |
| B005-02 | 首轮HTTP采样28线程，Rust8以外有数值库/HTTP辅助线程。增加独立CLI/service进程的CPU affinity上限8及BLAS/OMP单线程，Rust池8；记录实际affinity，线程总数不误称活跃CPU数 | 单测通过，最终E2E复测中 |
| B005-03 | 资源记录字段首次误插入encode_input参数，静态检查捕获Unexpected keyword；移到summary，未通过门槛前已修复 | mypy与141回归通过 |
| B005-04 | 生产CSV绝密，用户明确不能提供本机 | 按用户决定用固定种子Poisson/每模型5appid合成验收；现场数据留现场 |

首轮合成E2E真实进程已通过：GLM19.15秒/Qwen20.58秒/DeepSeek20.42秒；数据清单和结果在20261027T033513Z目录。加入CPU affinity与真实进程kill恢复后必须复跑，旧性能不代替最终门槛。Docker可执行在当前Windows/WSL PATH均未发现；本轮不安装、不构建，B006记录构建环境待准备。
