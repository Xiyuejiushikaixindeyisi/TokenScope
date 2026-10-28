# TokenScope

离线 CSV Token 监控：统一编码与 Chat Template、按 appid × 模型回放理想前缀复用、统计和直方图、阈值信号，以及同源 Web 前端。

## 当前版本

监控V1本机联合验收完成：后端0.1.0.dev6、前端0.1.0-f006的联合修正版，control schema3、view1、S0契约1.0.0。Git main保存可维护源码；具体基线由Git commit和[联合报告](docs/tasks/monitoring/JOINT_RESULT_V1.md)标识。尚未进行Docker交付或V100现场验收。

## 本地运行（Linux / WSL）

要求Python3.11、uv；前端Node22.22.2/npm10.9.7。CPU运行，无需本机GPU。

```sh
uv sync --frozen --python 3.11
cd apps/viewer
npm ci
npm run generate
npm run build
cd ../..
mkdir -p data/incoming artifacts/runtime
.venv/bin/python -m tokenscope.cli --input-root data/incoming --state-root artifacts/runtime --asset-root "$PWD" serve --host 127.0.0.1 --port 8000 --viewer-root apps/viewer/dist
```

浏览器访问 http://127.0.0.1:8000 。先将CSV放入data/incoming，再在页面用相对file_ref提交。每CSV一个模型；不主动采集生产数据。`/healthz`检查服务，`/readyz`报告编码配置就绪情况；DeepSeek默认思考未确认时readiness可能503，显式请求选项仍可处理。

**首次clone必须恢复编码资产**：models不入Git；按[encoding-assets.lock.json](env/encoding-assets.lock.json)中每个文件的source_url下载到path，并逐项核对sha256，或从自己的可信本地备份恢复同摘要文件。仅需Tokenizer/模板，不需要模型权重。缺资产时不能用假编码绕过测试。upstream是调研来源，按[来源锁](env/sources.lock.json)恢复；常规服务通过uv.lock安装依赖，不从浮动源码运行。

## 本机人工验收环境（2026-10-27）

服务入口 http://127.0.0.1:8000 ，完整前端与后端同源。环境保留在项目内：`.venv`、`apps/viewer/node_modules`、`apps/viewer/dist`；输入在`data/incoming/manual-20261027`，运行状态/日志/PID在`artifacts/runtime`。没有使用`/tmp`承载环境或验收数据。当前服务由本机会话后台启动，系统重启后使用上面的启动命令恢复，已有分析结果保留。

合成CSV对应：`manual-20261027/model-1.csv`→GLM-5.2；`model-2.csv`→Qwen3.6-27B；`model-3.csv`→DeepSeek-V4-Flash-0731。每模型5个`synthetic-app-*`，请求数采用泊松采样，包含短请求、66K附近长请求及200K以上边界。DeepSeek合成请求显式关闭思考，不代表确定生产默认值。结果记录在`artifacts/runtime/manual-validation.json`。

浏览器选择appid和模型，检查概览、直方图、请求明细及导出；人工验收结论由用户确认。若启动提示`INVALID_INPUT_ROOT`，先执行`mkdir -p data/incoming artifacts/runtime`；若8000已在运行，无需重复启动。

## 验证

```sh
.venv/bin/pytest -q
.venv/bin/ruff check src tests
.venv/bin/ruff format --check src tests
.venv/bin/mypy src/tokenscope
cd apps/viewer
npm run typecheck
npm run lint
npm test
npm run build
```

完整合成E2E：项目根运行`.venv/bin/python scripts/validation/run_monitoring_e2e.py --batch B005.1`。浏览器独立合成环境/Edge命令见[前端README](apps/viewer/README.md)与[联合报告](docs/tasks/monitoring/JOINT_RESULT_V1.md)，不可连接生产状态。部分历史取证脚本读取不入Git的artifacts/upstream，主pytest的dev5回退夹具已独立保存到tests/fixtures。

## 目录和文档优先级

| 内容 | 位置 |
| --- | --- |
| 后端 / 前端 | src/tokenscope / apps/viewer |
| 测试 / 实验与运维脚本 | tests / scripts；.build中的V0.1生成脚本仅历史追溯 |
| 配置与环境锁 | configs、env、pyproject.toml、uv.lock、apps/viewer/package-lock.json |
| 设计、契约、批次计划 | docs；先读[监控入口](docs/tasks/monitoring/ENTRY.md)，最新结果读[联合报告](docs/tasks/monitoring/JOINT_RESULT_V1.md) |
| 协作记忆 | memory/CURRENT.md、AGENTS.md |
| 本地数据与产物（不上传） | data、artifacts、models、upstream、.venv和缓存 |

保留原始实验/计划/研究资料。部分文档链接指向本地证据目录，GitHub不会包含其大文件；正式结论和必要清单保存在文档中，不将缺失本地证据解释为新测试通过。

## Git与下一步

个人项目直接合并main，不使用PR，具体规则见[Git与本地交付版本约定](docs/operations/GIT_WORKFLOW.md)。未来两个功能分支建议analysis/ideal-hit-rate、analysis/token-anomaly；本次不启动它们。

尚缺：两类原因分析、自进化Agent、主动数据采集、Qwen/V4增强hybrid仿真；首版使用批准的普通链式近似128/1536/32。生产DeepSeek缺省思考、GLM CP映射、GF资产等价和V100真实性能仍待确认。Docker、代码包、镜像需单独授权，包体不上传GitHub。
