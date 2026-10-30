# 监控后端维护记忆

2026-10-28整理；[旧增量日志](../../achieve/2026-10-28/snapshots/memory/tasks/monitoring.md)按需追溯。

- 当前dev6/schema3/view1/S0 1.0.0；B001–B005与B005.1后端、真实联合已完成，本机F007审查与交付也已完成。
- 后端拥有统一编码/计量/理想命中算法和公共契约；诊断复用同一实现，GET只读已有成果。
- 用户最新指派：接收华为脱敏报告，验收服务是否拉起；失败由本sessiondebug、修复并按影响复测。现场启动/功能/真实数据/性能分别记录，不冒称已通过。
- 镜像/Compose及交付问题与打包session协作；源码修复后提交候选给其统一审查，新构建仍需有效明确授权。
- DeepSeek缺省思考、GLM CP映射、GF资产等价、V100现场兼容及性能仍待确认。生产CSV不离现场。
- [当前ENTRY](../../docs/tasks/monitoring/ENTRY.md)提供交付、现场事实、代码地图、S0与测试入口。

## 2026-10-28 大文件风险与现场修复约定

- 用户真实CSV总计约26GB：Qwen19.8GB、DeepSeek4.5GB、GLM1.7GB；五列不变，生产数据不离现场。实际字节/行数/appid数未知，不能套用合成5appid。
- 用户标注北京时间10月20日15–17点；SQL以request_time的07–09点BETWEEN筛选，两端包含，需核实UTC导出口径；服务按model_handle_start_time回放，不能混同两个窗口字段。
- 本机源码核对：pipeline保存输入快照、请求库、Token文件、ledger和展示投影；批量读取不证明整体资源有界。Compose默认8CPU/32GiB、临时目录512MiB；磁盘放大/真实吞吐待实测。summary.elapsed_seconds止于统计阶段，现场另计完整发布耗时。
- 已新增[现场大文件/bug prompt](../../prompts/sessions/HUAWEI_MONITORING_LARGE_CSV_DEBUG.md)，唯一md内嵌关键源码、合成容器复现和脱敏证据；不是已收到的现场报告。
- 后端负责报告驱动的修复、patch及应用/验证/回退说明；稳定后打包session再按授权重新交付。没有故障证据前不臆造补丁，本轮无业务修改/构建/现场执行。
