# LH007 执行记录

2026-10-31，公共后台闭环。DiagnosticService/DiagnosticStore以独立SQLite记录冻结scope、原始手动原因、插件与资源版本；同键同意图返回原任务，异意图冲突；retry新任务/递增attempt，不覆盖历史。共用worker.lock；已持锁时处理器不重复持锁排队。低命中实验结束后Token读取同原scope；局部失败/预算不足明确partial，源错误/中断不继续。

产物先写私有working目录，关闭SQLite、fsync、文件摘要封存、rename后才事务登记report_digest；GET只读已发布产物。崩溃不自动补算：持worker.lock将running标interrupted，显式retry。可保留私有中间文件，但不会暴露为收益。

实测：任务3项passed（9.43s），包含真实GLM两方向顺序、原始Token输入、幂等/重试/取消、共享锁、缺插件、源预算及封存篡改。故障注入单元2项验证rename前磁盘失败、rename后登记失败均无可读报告；重启不发布孤儿目录。HTTP及跨方向业务入口由LH008继续验收。H3a已发送Token会话，对方真实服务2项独立通过，见其TA005报告。未打包部署。
