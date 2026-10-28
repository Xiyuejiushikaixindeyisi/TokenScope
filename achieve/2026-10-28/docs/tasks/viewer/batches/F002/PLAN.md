# F002 开发方案：通知、目录、缓存和完整快照

状态：closed，2026-10-27；门槛及证据见TESTS/RESULT。

## 代码与行为

实现PublicationClient/目录分页/版本协调器/Store/IndexedDB，按连接epoch隔离回调；首读目录cursor→SSE，结果按目标run读取、验证和一次切换。内存及持久缓存LRU，迟到响应不覆盖目标。提供R1恢复所需连接就绪事件，暂不实现提交表单。

拟维护路径（apps/viewer内）：src/state/{publication-client,catalog,snapshot-coordinator,view-store}.ts；src/storage/{db,snapshot-cache}.ts；src/api/query-cache.ts；tests/browser/publication。禁止修改监控计量算法或后端共享文件；遇到契约缺口写ISSUES并协商。

## 验证和退出门槛

- 目录响应后订阅前发布，回放不漏；后续页409整轮重读。
- 重复/乱序/迟到、reset过期/未来cursor/实例变化、重启、两个标签。
- 无心跳GET、无定时轮询、同key并发单次读取、三宽度本地切换。
- IndexedDB拒绝/满额/损坏schema、LRU、刷新缓存恢复、旧实例撤下。
- 新包失败保留同范围旧包，不在B标题下显示A数据。

关闭要求：记录网络请求断言/事件轨迹，所有快照一致性及缓存故障测试通过。测试命令和实际结果写TESTS；问题复现/根因/修复/复测写ISSUES；RESULT逐项对照后才进入下一批。

## 回退

退回F001；隔离本批缓存schema，不碰后端数据库。留存源码/依赖锁/配置摘要与失败证据，不全局reset或删其他会话产物。
