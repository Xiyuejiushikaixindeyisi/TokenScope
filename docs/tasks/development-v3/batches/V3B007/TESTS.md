# V3B007 TESTS — 实际执行记录

2026-11-10，状态 LOCAL_VALIDATED；BUS01–05 NOT_RUN（华为机验收）。环境 WSL Ubuntu22.04 / Python3.11 / Node22.22.2；本地锁定模型资产、CPU预算2。候选 HEAD `9a071c87b517490e497aa6cc1e53ec066bb4ede0` + 未提交源码，非镜像发布。

证据根：`artifacts/validation/development-v3/V3B007/`，每次独占attempt；完整冷启动最终为attempt-15，前端attempt-14/dist。candidate.json、source-sha256.json、dist_sha256、各任务profile/manifest与逐窗plan/rows绑定身份。final-check.json确认测试后产品源码摘要未变、18002/4173关闭。旧TokenScope服务先精确核PID停止，记录在attempt-01；旧state未复用。

## 运行结果（失败记录不删除）

| 运行 | 结果及处理 |
| --- | --- |
| attempt-01 全Python pytest | 873 passed / 17 failed，837.87s。16个计费边界单测受同进程模型残留RSS污染；1个H0冻结wire摘要不符。见ISSUES，未把这次运行改标全绿。 |
| attempt-09 受影响Python复验 | 61 passed，42.94s；预算、H0、V3协议、双模型真实API评估。 |
| attempt-10 全tests/unit | 653 passed，81.11s；一条第三方Starlette deprecation warning。 |
| attempt-08 生产默认旧结果读取 | 2 passed，11.97s；低命中/Token历史读取不变，旧写入口409，Token未唤醒。 |
| attempt-13 viewer | typecheck/lint通过；36文件345 passed，7.25s。浏览器12项启动失败（遗漏项目Chromium路径），未运行产品断言。 |
| attempt-11/12/14 浏览器harness | 11：8通过4失败3跳过；12：11通过1失败；14：12 passed，16.5s，最终dist构建成功。旧能力mock修正404；懒加载证据先滚动再断言。3个source-link测试缺独立历史fixture，保持NOT_RUN，不算通过。 |
| attempt-16 静态/冻结schema | mypy141源码通过；sampling/report schema --check通过。扩展ruff src/tests/scripts首次10错（旧脚本8、当前驱动2行长）；当前驱动格式修复后src/tests及本线全部Python脚本ruff通过。旧analysis_frontend_server.py八项既有风格问题未改，广义全scripts检查仍不通过。 |
| attempt-02/03/05/07 | 02缺浏览器共享库；03三场景完成但发现旧能力展示误报；修复后05/07均三场景成功。仅15为最终源码候选。 |
| attempt-15 真后端/真浏览器 | 三场景通过，正常监控来源→页面点击→prepare→自动L1→固定化→统一编码/缓存实算→封存→页面，无预指定clock/recipe。总计6次显式POST；刷新/断线重连只GET。 |
| attempt-15 独立校核/重启 | 四个完整窗口逐行Token摘要/P/H/C/有理数一致，独立literal-prefix oracle不用生产PrefixLedger/strategy。第一次重启编排读错candidate键名退出，服务已清理；restart-02复验通过，三历史任务新浏览器读取/方向切换0 POST，报告摘要不变，端口关闭。 |

## 最终实际数值（均为合成，不是业务收益）

| 来源 | 选择 | before P/H/C | after P/H/C | 参考提升 |
| --- | --- | --- | --- | --- |
| DeepSeek16 | A16、无B | 18400/9120/9280 | 18256/16320/1936 | 1045260/26243 pp，约39.83pp |
| Qwen16 | A16、无B | 13584/0/13584 | 13312/0/13312 | 0pp；当前模型配置缓存关闭，真实零收益仍显示 |
| DeepSeek2200 | 自动A512+B512 | 每窗588800/310688/278112 | 每窗584192/555968/28224 | 每窗1271733/29992 pp，约42.40pp |

large正常诊断14.203s，监督25ms采样RSS峰321212416 bytes（约306MiB），AS硬限2479538380 bytes。DeepSeek短样本277360640 bytes/1.166s，Qwen508252160 bytes/3.236s。三者completed/exit0/forced_termination=false，mem_limit=0。AS是虚拟地址空间硬限，不把RSS采样称RSS硬限；OS继承高水位另记。样本数随可用资源变化，前轮156/265、最终512均非业务固定默认值。

## T24–T30核对

T24本地全链及重启PASS；T25复用B002真实隔离/取消/磁盘/阶段超时/父死亡门禁，加本批最终大源PASS；T26旧报告生产读取、Token休眠、浏览器四入口、全Python已执行与受影响复验PASS（source-link专用harness缺fixture单列）；T27见DESIGN_CHECK；T28全部检查已执行，失败与复验逐项如上，不宣称单次全绿；T29本地大源PASS、华为五源NOT_RUN；T30本地自动链PASS、BUS01–05 NOT_RUN。

没有任何合成数据可替代华为五业务验收；极低模型固定内存余量/超大单条仍可明确资源不足，不能保证任意输入永不触限。B002 I04三份历史scale JSON被早期测试覆盖的损失仍未恢复，本批输出预查后均隔离保存。
