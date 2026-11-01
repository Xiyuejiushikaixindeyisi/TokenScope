# Token内容分析资源校准与限制

2026-10-31，版本token-content-calibration-1。原始记录见docs/tasks/length-analysis/batches/TA006/BENCHMARK.json及MACHINE.json；执行器为tests/integration/token_content/benchmark_content.py。每个场景独立Python进程；一次保留当前请求/当前结果，未保留整appid正文。

环境：WSL2 x86_64，Python3.11.16，Intel i7-13620H，WSL可见16逻辑CPU。以下仅纯Token提取/规则/候选，无Tokenizer或推理模型；模拟RequestView的J/P=0为无编码占位，不当作真实计量。

| 请求数 | 每个载荷字节 | 每请求载荷份数 | 耗时秒（约） | 峰值RSS KiB |
| --- | --- | --- | --- | --- |
| 1 | 16384 | 2 | 0.0021 | 34312 |
| 10 | 16384 | 2 | 0.0176 | 34780 |
| 100 | 16384 | 2 | 0.1567 | 34968 |
| 1 | 65536 | 2 | 0.0052 | 34824 |
| 1 | 262144 | 2 | 0.0165 | 36724 |
| 1 | 409600 | 2 | 0.0288 | 38220 |
| 1 | 128 | 10 | 0.0023 | 34224 |
| 1 | 128 | 100 | 0.0094 | 34608 |
| 1 | 128 | 1000 | 0.0832 | 38672 |

精确时间以JSON为准；单次测量有噪声，RSS含Python/公共类型导入，不能称增量内存或生产SLA。该范围未见随请求数成比例的内存增长，不能外推到150k真实请求。重复检测使用哈希桶后完整值复核、父子不重叠，不遍历所有字段对。

固定测量配置：max_request_bytes=1048576，max_units=10000，max_comparison_bytes=8388608，max_depth=64，max_candidates=1000，max_encoding_calls=100。HTTP仍要求显式RuntimeOptions/PluginSelection；此配置可复现测量，不自动注入为业务或生产默认值。源总量、Plan大小、实际编码/回放预算由公共运行配置控制，不改变appid/窗口，也不截断输入冒充完整。

预算刚低于/等于/超过需要量15项及提取中取消1项通过；单请求超限为未查/partial/unknown并保留停止位置。候选预算不是“大内容”异常阈值。prepare_mutation没有公共RunControl参数，沿已记录的8MiB输入+参数、64层、1000目标硬边界；不声称此最大编译边界已做生产吞吐验证。

真实模型编码/回放依赖原资产/profile，三模型测试记录见TA004。完整公共两方向任务含编码/等待的规模测量见docs/tasks/prefix-analysis/RESOURCE_PROFILE.md；本页的Token耗时不含低命中等待，不能混为总任务耗时。未构建容器、打包、部署或执行现场压测。
