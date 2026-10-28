# F005 开发方案：有界导出和完整性校验

状态：closed；实际结果见RESULT。

## 代码与行为

实现ExportController/Worker/NDJSON与CSV增量解析、sha256和FileSink。主路径文件选择器→流式验证/写入→EOF验证后close；错误abort。备用路径≤16MiB完整验证后Blob下载，超过中止。应用在途4×64KiB，记录上限1MiB；不将导出放普通查询缓存。

拟维护路径（apps/viewer内）：src/features/exports；src/workers/export-validator.ts；src/domain/export-protocol.ts；tests/unit/export；tests/browser/export。禁止修改监控计量算法或后端共享文件；遇到契约缺口写ISSUES并协商。

## 验证和退出门槛

- 正确/空NDJSON：metadata/request/summary顺序、原字节摘要和预计/实际行数。
- 缺summary/哈希错/附加行/UTF8非法/截断/任意chunk切点均明确失败。
- CSV嵌入换行/引号转义/CRLF跨chunk/表头/字节安全前缀，解析行数正确。
- 256MiB流、慢sink、取消/关闭、磁盘错误、超1MiB记录、并发导出限制。
- 实际保存路径close仅在验证后；失败无成功提示，检查可能空占位。
- 无文件写API：16MiB边界、未知长度、压缩长度不可冒充解码长度、内存峰值。
- 应用队列上限断言和浏览器导出增量内存优化目标64MiB、验收上限256MiB（用户2026-10-27批准）；256MiB/1GiB各3次测量及增长检查；CSV不声称摘要校验。

关闭要求：真实目标浏览器的流式/备用导出证据、内存测量方法与数据身份齐全；R2不以HTTP测试替代。测试命令和实际结果写TESTS；问题复现/根因/修复/复测写ISSUES；RESULT逐项对照后才进入下一批。

## 回退

回退F004导出入口并清理本页临时资源；不删除用户文件或回滚业务结果。留存源码/依赖锁/配置摘要与失败证据，不全局reset或删其他会话产物。
