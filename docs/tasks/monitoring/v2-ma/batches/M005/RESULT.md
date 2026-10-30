# M005 统一验收闭环

状态：**closed，本机后端通过**。2026-10-30；设计v1.0、MA协议1.0.0。M000–M004已按顺序闭环，本批完成统一测试、健壮性、资源及设计符合性验证。没有部署、打包或Git提交/push。

## 最终验证

- 项目固定WSL Python3.11.16，` .venv/bin/pytest -q `：**235 passed，1 warning，190.03s**。警告为现有Starlette/httpx测试客户端弃用提示，无skip/xfail。
- `ruff check src tests scripts`、`ruff format --check src tests scripts`：通过，111文件格式一致；`mypy`：44源码文件通过。
- `python scripts/contracts/validate_ma_contract.py`：Schema/真实路由签名/摘要一致，2正例4负提交样例；完整快照/跨字段/负例另由pytest覆盖。
- 真实临时loopback HTTP后台、CLI往返、真实多进程互斥/双队列推进、真正os._exit封存前后恢复、SQLite提交失败、磁盘不足、损坏seal、GET只读、输入格式/质量、三模型真实编码、公共仿真参考与V1接口回归均通过。
- 旧S0 SHA与M000基线一致；61项候选源码/测试/依赖文件在最终验收结束后复核无变化。身份见[IMPLEMENTATION_MANIFEST](IMPLEMENTATION_MANIFEST.json)。

## 证据

原始输出在项目`artifacts/validation/monitoring/v2-ma/M005/final-02/pytest.txt`；依赖版本在同目录environment.json。第一轮232项通过记录保留于final-01；随后新增真实进程退出/配置快照测试、加强Histogram DTO与来源说明，最终重跑全量235项，不拼接旧结果冒充最终候选。

固定资源场景：pre/now各500条、16UUID、含约1MiB单条长输入，CPU8，批256/16MiB，真实Qwen资产。最终resource-attempt02/report.json：两轮完整处理至控制提交分别4.1297s、3.3442s；峰值RSS均865,513,472字节，小于预先固定3GiB；句柄保持5个；两轮指标完全一致。产物各约8.68MB。仅为高重复合成样本，不证明现场性能或GB/GF源完整性。

[设计符合性矩阵](DESIGN_CHECK.md)覆盖MA01–14与X01–12；[代码地图](../../CODEMAP.md)及[已实现API](../../IMPLEMENTED_API.md)供后续Agent接入。

## 问题与边界

已闭环：测试线程预算冲突、静态类型/格式问题、CLI轮转持久性、封存子目录同步、claim后模式校验、故障安全定位、直方图严格结构与守恒。失败记录及修复/复测见各batch ISSUES/TESTS。

本机MA后端完成；正式前端联合与视觉验收、现场代表CSV/真实性能、用户索引处理器的真实三线联合仍pending，各由对应会话/现场证据完成。用户线公共U001兼容已消费并回归，但不代签其U002–U005。部署/镜像/代码包未执行，需按已有流程另行授权。

回退可移除app/CLI中MA可选接入并保留ma数据，V1库/结果/冻结契约没有被MA迁移或覆盖；不删除原CSV、运行证据或共享工作区其他会话修改。无本机后端阻塞问题。

最终交接补充：已读取前端接收记忆中的样例缺口，用真实MA管线生成并严格校验16个合成前端样例（含5类Snapshot、完整Receipt、质量、目录、错误），位于docs/contracts/ma-monitoring-v2/frontend.examples.json；生成器scripts/contracts/generate_ma_examples.py。部分回执状态显式为合成状态，均非现场或前端验收证据。未发跨会话消息，前端按入口自行接收。业务源码未改变，235项全量证据仍对应同一候选。
