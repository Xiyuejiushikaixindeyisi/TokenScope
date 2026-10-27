# Token监控本地运行与复核

本文件针对已实现后端，真实数据只在获得授权的现场目录内处理。本机数据全部合成。Python3.11，固定uv.lock；常规修复使用本地.venv，不能每次修复都重建Docker。

```bash
cd /home/zhangxiyue/TokenScope
/home/zhangxiyue/.local/bin/uv sync --frozen --offline
mkdir -p data/raw/local-input data/derived/monitoring-local
.venv/bin/python -m tokenscope.cli --input-root data/raw/local-input --state-root data/derived/monitoring-local --asset-root . serve --host 127.0.0.1 --port 8000
```

启动服务会自动消费提交队列；单worker文件锁跨CLI/服务实例生效。独立CLI进程默认限制8个可用CPU，BLAS/OMP线程1、Rust8；容器交付另配置8CPU/32GiB。服务仅HTTP控制/读取，不主动采集请求，不调用模型推理或GPU。

将CSV放输入根内，POST /analysis-runs 显式传file_ref/model_id。只做CLI时先submit，再work-once，后run/metrics/histograms/lengths/signals；各命令共享相同input-root/state-root。CLI详细参数见--help及对应子命令--help。内部explain显式重编码并验证IDs，不随页面GET执行。

DeepSeek默认profile保持pending：合成数据显式enable_thinking=false只用于测试。真实请求若无显式思考选项，需要用户确认后通过模型settings选择thinking_enabled或thinking_disabled；不要由启动脚本代选。GLM/Qwen使用模板默认。全局readyz在DeepSeek缺省未决时503，各模型readiness独立；healthz只表示进程存活。

输入原CSV、SQLite、IDs和轻量证据保留在专属state根。完成目录必须有manifest且控制库索引提交；失败.partial不当结果，GET返回409。重启会校验已封存未提交的结果并恢复，其余running转interrupted；显式重提产生新run。同输入同规则重跑不重复创建outbox事件。无分析器时pending_consumer是正常状态。

停服务后备份专属state目录与代码/资产锁；schema2包含schema1的增量表。回退旧schema代码必须使用对应旧控制库副本，不能删除生产结果或把旧程序直接指向新库。数据不自动清理，不操作共享Docker或其他服务。

验证：`.venv/bin/python scripts/validation/check_batch.py B005`；实际进程合成E2E：`.venv/bin/python scripts/validation/run_monitoring_e2e.py`。后者生成每模型5个appid/约1万行、Poisson长度、66K/200K+场景，固定种子，输出报告到artifacts/validation/monitoring/B005。
