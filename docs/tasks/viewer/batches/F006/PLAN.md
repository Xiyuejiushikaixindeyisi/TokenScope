# F006 开发方案：统一前端验收、设计核对和后端交接

状态：closed；通过证据及边界见TESTS/RESULT。

## 代码与行为

汇总全部前端测试，执行统一用户旅程、网络/故障/资源/缓存/R1/R2回归；逐条ACCEPTANCE矩阵填代码与证据。用冻结契约假服务验证前端，再使用已就绪真实后端进行开发联调（若不可用明确pending）。形成前端交接manifest与可复现构建说明，不构建交付归档。

拟维护路径（apps/viewer内）：tests/browser/full-journey；apps/viewer/scripts/check-*；artifacts/validation/viewer/F006；docs/tasks/viewer/handoffs。禁止修改监控计量算法或后端共享文件；遇到契约缺口写ISSUES并协商。

## 验证和退出门槛

- 所有单元/组件/浏览器/strict type/lint/build检查通过。
- 从首次打开到发布替换/详情/设置/提交恢复/导出完整旅程。
- 断网/重启/多标签/存储不足/未知schema/读写错误/文本注入回归。
- ≥30次冷/热p50/p95：缓存100ms、首组1s、50行500ms，假/真服务分开。
- 逐条对比最终设计无未获同意偏差，源码/契约/样例/依赖摘要一致。
- 回退演练、未决问题分类、后端统一J01–J06及R1/R2数据和脚本交接。

关闭要求：前端所有必测门槛通过，达到ready_for_joint；项目release_ready仍待后端真实联合验收。测试命令和实际结果写TESTS；问题复现/根因/修复/复测写ISSUES；RESULT逐项对照后才进入下一批。

## 回退

退回最近通过前端版本和依赖锁，隔离不兼容缓存，保留回执/所有失败证据。留存源码/依赖锁/配置摘要与失败证据，不全局reset或删其他会话产物。
