# B006 准备验证

实际执行：3项release门槛测试、ruff check/format均退出0；Compose经YAML静态解析，8CPU/32GiB/linux-amd64/只读输入/无build段/pull_policy=never断言通过。报告artifacts/validation/monitoring/B006/preparation-checks.json及各日志。

`build_monitoring.py --check`只读预检成功：B005最新门槛/最终E2E源码摘要匹配、三模型资产校验通过、白名单62文件；预检清单release-preflight.json。真实调用不带approval-file，退出1并明确not authorized，未运行Docker/未创建交付目录。

本机Windows/WSL PATH均无Docker CLI，因此Dockerfile构建、Compose config执行、镜像内离线E2E、docker save、目标V100启动均未执行；静态准备不能替代这些门槛。
