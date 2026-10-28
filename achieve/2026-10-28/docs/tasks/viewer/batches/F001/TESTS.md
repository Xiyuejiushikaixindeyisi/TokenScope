# F001 测试计划与执行记录

状态：全部待执行。本文件的场景不是通过证据。

| ID | 场景与断言 | 结果 |
| --- | --- | --- |
| F001-T01 | 字符串整数0/2^53−1/2^53/64位边界/负delta及null，禁止Number先舍入 | 未执行 |
| F001-T02 | 错误码、未知schema、跨scope/实例、UTF8时间原串、bin_width/limit枚举 | 未执行 |
| F001-T03 | 构建输出无CDN/远程字体，根API地址与hash路由正确 | 未执行 |
| F001-T04 | R1回执/终态和R2结束校验样例齐全，边界已由后端确认 | 未执行 |

## 实际执行记录格式

测试ID、命令、工作目录、起止UTC、退出码、源码/契约/样例摘要、Node/浏览器/OS、假服务或实际后端身份、观测结果、日志/截图/网络/资源证据、关联ISSUE。失败与重试都保留。

计划命令由F001建立apps/viewer内npm scripts：typecheck、lint、test、test:browser、build；具体过滤参数在脚本存在后登记，不假称当前可执行。本批按变动范围测试，进入下一批前执行退出门槛；F006统一回归。

## 首轮实际执行（2026-10-27）

工作目录apps/viewer，Node22.22.2/npm10.9.7，WSL Ubuntu；S0人工合成协议样例，不是真实API。完整起止时间与退出码见artifacts/validation/viewer/F001/startup/commands.json，对应同目录generate/typecheck/lint/test.log。

| 命令 | 实际结果 |
| --- | --- |
| npm install --no-fund | 成功，锁定210个包；audit 0 vulnerabilities |
| npm run generate | 通过，全部S0摘要一致，67个DTO |
| npm run typecheck | 通过 |
| npm run lint | 通过 |
| npm run test | 100通过、1失败：F001-I03 cursor边界 |
| npm run build | 测试失败后未执行 |
| npm run test:browser | 未执行；浏览器版本尚未锁定 |

T01整数/时间基础通过；T02仍因cursor失败不通过；T03组件路由通过，但构建/浏览器待执行；T04全部75个S0 JSON样例和两份NDJSON原字节摘要通过，不代表R1竞态/R2流式导出已实现。

## 修复后最终结果（2026-10-27）

- typecheck、lint、102项单元/组件测试、production build全部通过；最终浏览器配置/用例变动后typecheck再次通过。
- node scripts/check-build.mjs通过；构建资源均本地，不引用远程CSS/字体。
- Playwright同一shell.spec.ts在Windows Edge156.0.4314.42真实通过；路由切换+刷新、390px无横向溢出、无外部请求、无页面异常；截图已人工检查。
- T01/T02/T03/T04本批门槛通过。R1/R2仅契约与样例确认，恢复/导出实现及联合验收仍由后续批负责。
- 完整证据：artifacts/validation/viewer/F001/recheck/下commands.json、各日志、edge-report.json（含浏览器身份/网络/截图）、narrow-shell.png、environment.json、source-manifest.json。
- Linux浏览器启动失败保留browser.log与apps/viewer/test-results原trace；改用Edge成功记录独立保存，不覆盖失败证据。原首轮cursor失败保留startup/test.log。
