# 监控本地开发环境

2026-10-27 / B001：WSL Ubuntu-22.04，项目独立 `.venv`，CPython 3.11.16，uv 0.12.19；系统 Python 未修改。具体依赖由根目录 uv.lock 固定，不以镜像构建作为开发循环。

```bash
cd /home/zhangxiyue/TokenScope
/home/zhangxiyue/.local/bin/uv sync --frozen --python 3.11.16
.venv/bin/python scripts/validation/check_b001.py
```

CLI 必须显式给输入目录与状态目录（目录须在本项目下创建）。示意：

```bash
.venv/bin/tokenscope --input-root data/incoming --state-root artifacts/runtime models
.venv/bin/tokenscope --input-root data/incoming --state-root artifacts/runtime validate-input glm.csv --model GLM-5.2
.venv/bin/tokenscope --input-root data/incoming --state-root artifacts/runtime serve --host 127.0.0.1 --port 8000
```

`validate-input` 保存输入副本与质量记录，是诊断入口，没有 Token 指标。B001 API ready/submit 返回未就绪；以后由对应批接通完整流水线。上述目录和服务不由文档自动创建/运行。一般错误日志不含请求正文；输入与 SQLite 暂存仍属于真实数据，保留在 Git 忽略的数据/产物目录。

CPU 实现不依赖 V100/CUDA，目标机兼容性和每文件两小时须 B006 实测。当前环境不是交付包。
