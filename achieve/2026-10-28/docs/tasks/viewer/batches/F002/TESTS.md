# F002 测试计划与执行记录

状态：全部待执行。本文件的场景不是通过证据。

| ID | 场景与断言 | 结果 |
| --- | --- | --- |
| F002-T01 | 目录响应后订阅前发布，回放不漏；后续页409整轮重读 | 未执行 |
| F002-T02 | 重复/乱序/迟到、reset过期/未来cursor/实例变化、重启、两个标签 | 未执行 |
| F002-T03 | 无心跳GET、无定时轮询、同key并发单次读取、三宽度本地切换 | 未执行 |
| F002-T04 | IndexedDB拒绝/满额/损坏schema、LRU、刷新缓存恢复、旧实例撤下 | 未执行 |
| F002-T05 | 新包失败保留同范围旧包，不在B标题下显示A数据 | 未执行 |

## 实际执行记录格式

测试ID、命令、工作目录、起止UTC、退出码、源码/契约/样例摘要、Node/浏览器/OS、假服务或实际后端身份、观测结果、日志/截图/网络/资源证据、关联ISSUE。失败与重试都保留。

计划命令由F001建立apps/viewer内npm scripts：typecheck、lint、test、test:browser、build；具体过滤参数在脚本存在后登记，不假称当前可执行。本批按变动范围测试，进入下一批前执行退出门槛；F006统一回归。

## 实际结果：全部本批门槛通过

- T01：publication.test.ts目录cursor订阅、409完整重读。
- T02：重复/迟到事件、四种reset、旧epoch失效、reopen/双client；coordinator新实例撤下。
- T03：心跳无GET、无定时器；同key单次load、完整三宽度缓存复用。
- T04：真实Edge cache.spec.ts 4项：刷新持久化、损坏/拒绝/配额注入降级、LRU、多标签、损坏schema；未使用fake-indexeddb依赖。
- T05：迟到A不盖B、失败B不显示A；同组下一版本失败保留旧包；pin保持旧版/整体接受pending。

命令：npm run typecheck/lint/test/build。最终test 115 passed；浏览器沿F001的Windows Edge/外部WSL Vite测试入口，TOKENSCOPE_TEST_BASE_URL=http://127.0.0.1:4174，Playwright test cache.spec.ts（4通过）。Browser测试使用专用harness，不进入生产dist。

证据：artifacts/validation/viewer/F002/pass1（lint失败）、pass2、pass3；浏览器pass2/browser-final-report.json含起止/结果；最终单元pass3/test-final.log。Node22.22.2/npm10.9.7，Edge156.0.4314.42/Windows Node24.22.1；S0人工样例与合成事件。
