# F002 闭环

状态：closed，2026-10-27。允许按已授权方案进入F003，无需再询问。

完成：PublicationClient（持久游标订阅、epoch、reset、重连一次对齐、ready钩子）；目录revision分页；ViewStore/SnapshotCoordinator（去重、scope、完整包原子替换、pin/pending）；SHA256+ETag校验；32MiB内存/64MiB IndexedDB软预算及LRU，独立结果库不删除回执；上次缓存恢复和缓存降级。没有指标轮询。

验证：115项单元/组件回归通过；类型/lint/build通过；4项真实Edge IndexedDB浏览器检查通过。T01–T05对应证据见TESTS。没有真实业务后端联调，不改变后端session联合验收责任。

源码摘要：artifacts/validation/viewer/F002/source-manifest.json。证据pass1失败、pass2/pass3回归、browser-final-report.json。

回退：恢复F001数据层/工程入口，隔离tokenscope-viewer-snapshots-v1结果缓存，禁止清理其他数据库或回执；后端、旧HTML保持。未做Docker/镜像/代码交付包。
