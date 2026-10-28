# 发布脚本入口

当前完整服务入口：[部署说明](../../deploy/monitoring/README.md)、[交付session](../../docs/tasks/delivery/ENTRY.md)。

- prepare_monitoring_context.py：白名单源码/资源/锁定wheel/编码资产，固定候选身份。
- verify_service.py：显式合成提交检查，或只读恢复检查；报告不等于现场真实数据结论。
- package_monitoring.py：通过容器/恢复/浏览器检查后形成代码/镜像和清单，产物仅本地。

Docker构建/重新打包须有效明确用户授权。build_monitoring.py是旧backend_only历史脚本，为原测试保留，不作为当前发布入口；[历史快照](../../docs/archive/monitoring/B006-backend-preparation-2026-10-27/README.md)。
