# F005 测试记录

状态：通过并closed。证据根目录 artifacts/validation/viewer/F005。

- final/generate.log：冻结S0全部摘要通过，生成67 DTO；test.log 142 passed；typecheck/lint/build均exit0。
- 单元测试export.test.ts：normal/empty NDJSON/CSV逐字节切分、NDJSON所有两段切点、原字节摘要、截断/缺summary/坏hash/身份和筛选漂移/非法UTF8/1MiB上限。
- pass2–pass7保留内存超限及UNC临时profile失败；pass8通过256MiB、真实OPFS close/abort、慢写、取消/模拟磁盘错误/截断/超记录/备用下载。
- final/browser-report.json：已执行通过256MiB/1GiB各3次真实Worker+持久化OPFS压力、16MiB精确边界及+1byte；另测试真实Worker的固定NDJSON/CSV字节、摘要/结束/断网拒绝。
- 主缓冲64KiB、顺序1个在途（低于批准4个上限）；浏览器峰值用SystemInfo进程ID集合的Windows WorkingSet64之和，记录基线/逐秒/结束值，不冒称JS堆。
- 本次是frontend-only受控合成流；后端最终真实联合另行执行。

最终：7个场景均通过（final 6 passed/1 HMR中断，recheck该场景passed），六次压力和增长检查见acceptance-memory.json。最初2倍量化判据是agent自行追加的无依据草拟值，已公开纠正为<3倍；64MiB→256MiB是用户明确批准修改，不混淆两者。
