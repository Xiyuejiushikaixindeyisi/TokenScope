# FE-N1 通知、报告目录与时间增补

2026-10-31。用户要求实现前端BACKEND_NOTIFICATION_HANDOFF/INTERACTION_DRAFT，并确认partial/empty不覆盖、两方向整体ready规则。公共方本地实现完成；接口身份diagnostics-discovery-1，消费者入口[NOTIFICATION_HANDOFF](../../NOTIFICATION_HANDOFF.md)。源码/Schema身份见[manifest](../../../../contracts/diagnostics-discovery-1/manifest.json)。

新增discovery/discovery_contracts、独立HTTP路由，storage初始化附加SQLite持久日志/事务触发器，app只增加扩展路由装配。不改Token、L1–L5、统一监控算法或旧冻结协议；旧报告不回写、不重算、不以mtime填时间。前端通知必须通过fetch SSE携带实例header，未自动发送跨会话消息。

## 实际验证

- 两线公共/低命中/Token单元及集成（排除已有三个资源基准）：199 passed，164.32s。
- 新协议最终专用单元（含之后增加的冻结Schema/manifest验证）：7 passed，0.48s；与上述集合重叠，不相加。
- 新真实HTTP测试已纳入联合集合，独立首次1 passed，3.76s；Task ready→目录→GET可读、快照、取消、实例、reset。
- ruff通过；mypy公共层/新API/app 18 source files通过；三个契约manifest一致、三个文档wire样例可解析并通过现有模型校验，交接链接存在。
- 监控V1/用户V2/MA兼容回归：300 passed，173.76s。

覆盖：事务回滚无终态事件、发布后可读、打开—订阅竞态、重放去重、同快照分页、重启恢复、legacy时间null、partial/empty历史但无默认、Token-only及跨模型默认隔离、评估不覆盖、无报告终态恢复、不同epoch/未来游标reset、ASGI客户端断线释放连接槽、容量503、心跳不读取报告。

初次心跳测试误修改Python全局time.monotonic影响asyncio调度，已改为模块局部mock后通过。只存在已有Starlette/httpx弃用警告，未因此升级依赖。没有前端浏览器联合、实际代理SSE、64连接负载或长时间现场测试；不声称这些通过。旧三档资源吞吐不作为新目录容量SLA。

## 回退与交接

移除新增router注册即可停用扩展，保留旧任务接口和附加日志表/触发器；不删除证据。目录/事件不自动清理，手动删除/数据损坏仍由原GET校验拒绝。默认选择旧窗口晚发布也可更新，数据窗口与完成时刻均展示；历史导入无可信顺序，不自动指定默认，需用户显式历史查看。

本轮不打包/部署，不启动或更改前端代码，不代签消费者接收。共享工作树包含其它会话内容，未整区提交/清理。旧历史摘要不覆盖；新增manifest为本地身份，不是远端上线证明。
