# F004 问题闭环

- S0兼容旧客户端允许Submission省略key，新前端明确使用KeyedSubmission本地交叉类型并运行时必填检查；未改S0。
- R1测试最初把独立状态样例误作同一请求，key不同导致正确身份拒绝；构造同一事务时显式统一key/run，保留旧失败记录。
- 两处测试未使用变量lint修正；指标select采用可访问role/name定位，未减弱UI断言。
- ReceiptStore内存提交层也执行终态不回退，避免merge后异步save竞态；独立IDB不与快照LRU共享。

无阻断。故障注入/合成协议不代替后端真实事务与联合验收。
