# F004 开发方案：提交恢复与配置操作

状态：closed，2026-10-27；证据见TESTS/RESULT。

## 代码与行为

实现SubmissionCoordinator及独立ReceiptStore，持久key与最小提交信息；SSE就绪后一次性补查，4并发、按key去重、终态单向合并。参数和阈值使用新整数适配API，共用UI错误处理，CAS保留草稿。操作终态只在提交区展示。

拟维护路径（apps/viewer内）：src/features/{submissions,settings}；src/state/{receipt-store,submission-coordinator}.ts；tests/browser/submission-recovery。禁止修改监控计量算法或后端共享文件；遇到契约缺口写ISSUES并协商。

## 验证和退出门槛

- R1：首次catalog之前失败/完成/no_valid_rows，终态最终正确。
- 超过日志保留reset后查回；对齐GET期间任务终止；旧running晚到不覆盖终态。
- POST丢响应，同key查回/重试；未知key404不伪造失败；异体409。
- 服务实例变化不投递旧key；持久化失败明确限制；只读缓存清理不删待确认提交。
- 回执查回失败可见且不轮询；重复onopen只启动一次代次对齐。
- 设置/规则大整数无损写入；CAS冲突保留草稿；下一运行生效旧包不变。

关闭要求：R1所有竞态及配置冲突浏览器用例通过，网络计数证明没有周期补查。测试命令和实际结果写TESTS；问题复现/根因/修复/复测写ISSUES；RESULT逐项对照后才进入下一批。

## 回退

退回F003操作入口，保留/导出ReceiptStore供恢复，不能自动重提任务。留存源码/依赖锁/配置摘要与失败证据，不全局reset或删其他会话产物。
