# F004 闭环

状态：closed。实现独立ReceiptStore与SubmissionCoordinator：POST前保存key/最小请求、同key显式重试、最大4并发补查、每连接代次一次对齐、终态优先/冲突明确、旧实例不投递；保存失败提示刷新限制。

实现提交操作页、下一运行设置、独立appid×model阈值编辑；整数全程字符串，CAS冲突保留草稿并显式对照确认。没有预设报警阈值，未修改历史快照或后端契约。

类型/lint/build及128项单元组件通过；真实Edge2个综合操作流程通过（真实IndexedDB+合成HTTP/事件连接）：key在POST之前持久，重载恢复首次目录前终态、不重复POST；大整数设置CAS重读确认、规则字符串无损写入。

证据pass1–pass4及final/browser-report.json，源码source-manifest.json。进入F005。回退F003操作入口时保留独立回执库，禁止自动重提或清理未确认记录；无交付打包。
