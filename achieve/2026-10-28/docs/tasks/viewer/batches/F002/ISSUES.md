# F002 问题记录

1. 首轮lint发现两处类型导入未使用import type；按既定规则修正，pass2/pass3通过。
2. 实现自查补充恢复缓存的旧实例撤下、cursor代次隔离、current包软预算保护、确认连接后的离线标签清理；未变更后端契约。
3. 浏览器用例明确区分真实IndexedDB运行和通过IDBObjectStore.put抛QuotaExceededError的故障注入，不声称耗尽机器真实磁盘。

无阻断；失败日志pass1保留。生产SSE的真实代理/后端事务验收仍归联合阶段，不以本批合成事件测试替代。
