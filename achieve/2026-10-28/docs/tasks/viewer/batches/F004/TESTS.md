# F004 测试计划与执行记录

状态：全部待执行。本文件的场景不是通过证据。

| ID | 场景与断言 | 结果 |
| --- | --- | --- |
| F004-T01 | R1：首次catalog之前失败/完成/no_valid_rows，终态最终正确 | 未执行 |
| F004-T02 | 超过日志保留reset后查回；对齐GET期间任务终止；旧running晚到不覆盖终态 | 未执行 |
| F004-T03 | POST丢响应，同key查回/重试；未知key404不伪造失败；异体409 | 未执行 |
| F004-T04 | 服务实例变化不投递旧key；持久化失败明确限制；只读缓存清理不删待确认提交 | 未执行 |
| F004-T05 | 回执查回失败可见且不轮询；重复onopen只启动一次代次对齐 | 未执行 |
| F004-T06 | 设置/规则大整数无损写入；CAS冲突保留草稿；下一运行生效旧包不变 | 未执行 |

## 实际执行记录格式

测试ID、命令、工作目录、起止UTC、退出码、源码/契约/样例摘要、Node/浏览器/OS、假服务或实际后端身份、观测结果、日志/截图/网络/资源证据、关联ISSUE。失败与重试都保留。

计划命令由F001建立apps/viewer内npm scripts：typecheck、lint、test、test:browser、build；具体过滤参数在脚本存在后登记，不假称当前可执行。本批按变动范围测试，进入下一批前执行退出门槛；F006统一回归。

## 实际结果

T01–T05：receipts.test.ts覆盖四种终态恢复、晚running/冲突、404/丢POST/异体key、4并发/实例切换/epoch、内存终态保护；F002四种reset与连接ready事件已回归。operations.spec.ts真实IDB写入先于POST，页面刷新恢复running→failed（终态早于本次catalog），POST仍1次、GET2次。

T06：浏览器设置先409保留9007199254740993，再以新revision显式确认；规则integer阈值同值为string，冻结展示包不变。

命令npm run typecheck/lint/test/build通过，128 tests。Playwright test operations.spec.ts最终2通过；最终报告artifacts/validation/viewer/F004/final/browser-report.json，单元构建pass4。之前错误保留pass1–3。环境沿F003。测试SSE为明确合成EventTarget连接，不宣称真实服务器SSE/事务联合通过。
