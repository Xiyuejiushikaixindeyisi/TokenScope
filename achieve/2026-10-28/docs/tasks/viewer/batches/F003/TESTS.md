# F003 测试计划与执行记录

状态：全部待执行。本文件的场景不是通过证据。

| ID | 场景与断言 | 结果 |
| --- | --- | --- |
| F003-T01 | 与独立样例逐值核对J/P/H/C/O、rate、nearest-rank和所有并列众数 | 未执行 |
| F003-T02 | 0/5000/200000/超长尾、空/null、字符串整数tooltip、共享纵轴 | 未执行 |
| F003-T03 | 点击柱区间、尾部无upper、J/P/C不同排名不得拼行、重复hash完整 | 未执行 |
| F003-T04 | 每段1000点排名范围清晰，多列排序次序、hash文字前缀 | 未执行 |
| F003-T05 | 详情UTF8预览/轻证据、模板能力关闭、文本不执行HTML | 未执行 |
| F003-T06 | 新包在详情/固定历史停留；390px与桌面无横向溢出、键盘可用 | 未执行 |

## 实际执行记录格式

测试ID、命令、工作目录、起止UTC、退出码、源码/契约/样例摘要、Node/浏览器/OS、假服务或实际后端身份、观测结果、日志/截图/网络/资源证据、关联ISSUE。失败与重试都保留。

计划命令由F001建立apps/viewer内npm scripts：typecheck、lint、test、test:browser、build；具体过滤参数在脚本存在后登记，不假称当前可执行。本批按变动范围测试，进入下一批前执行退出门槛；F006统一回归。

## 实际结果

T01/T02：monitoring.test.tsx核对精确总量/null、并列众数、SVG之外分位数、普通/开放尾桶键盘点击、1K=603柱。T03/T04：monitoring.spec.ts断言尾桶无upper、重复hash两行、排序query与1000点模式。T05：真实dialog预览恶意HTML以文本显示，未执行；证据/正文按需；模板入口不存在。T06：F002 pin/旧新版本原子状态回归+本批scope/history URL；390px真实Edge无页面溢出，桌面和移动截图人工检查。

最终命令npm run typecheck/lint/test/build全部通过，test=120；Playwright test monitoring.spec.ts 1条综合流程通过（多断言），snapshot GET=1，无页面错误。测试源为S0合成样例；不是后端真实联调。

证据artifacts/validation/viewer/F003/pass2失败、pass3修复日志及browser-report.json（含网络/截图/起止）。环境沿F002。
