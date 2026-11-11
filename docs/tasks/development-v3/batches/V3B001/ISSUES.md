# V3B001 ISSUES

2026-11-10。组件批次已验证；资源硬控制/目标规模验收在B002/B007，不能由本批代替。

| ID | 类型/状态 | 发现、根因与处理 | 复测/证据 |
| --- | --- | --- | --- |
| V3B001-I01 | DESIGN_RISK / COMPONENT_VALIDATED | 旧seal全文件I/O必须保留；增加可计费/取消的digest与metadata回调，不解析全量signals，前后seal+SQLite事务核一致性；预算保护由B002落实。 | T01/T04来源变化/取消/磁盘失败/原件SHA/样本隔离通过；目标规模耗时和峰值仍归B002/B007，不冒称已测。 |
| V3B001-I02 | DESIGN_RISK / CLOSED | 时间包络、同hash或跳行不能代替精确成员。流式元数据选A首连续段/B末连续段，按time_ns+record_index排序，拒绝条目断开窗口；保留末尾拒绝前的最后合法B。 | 100000元数据行只保留6成员；同时间/同hash/拒绝缺口/无B/整个scope=A及成员引用测试通过。 |
| V3B001-I03 | STATIC_CHECK / CLOSED | 首轮ruff 5项（相邻zip与行长）、mypy 4项（Literal常量/bytes变量复用）；已更正，不放宽规则。随后全源码mypy发现ObservedSource override参数类型不同步，已同步联合类型。 | attempt-02保留override失败；attempt-03/04/05 ruff/mypy通过，最终126源码文件。 |
| V3B001-I04 | TEST_FIXTURE / CLOSED | attempt-01负例直接给tuple元素赋值，未执行到目标guard；改为构造新的重复成员tuple，仍断言overlap错误。 | 首轮1 failed/14 passed；后续完整集合46 passed。未删产品断言。 |
| V3B001-I05 | CONTRACT_COMPATIBILITY / CLOSED | 新排除计数为dict[str,int]，旧from_wire未读取additionalProperties的整数schema；补支持后仍拒绝JSON数值代替十进制字符串，旧schema不改。 | 新映射往返及非法wire负例、旧contracts/schema/http/freeze回归通过。 |
| V3B001-I06 | READ_BOUNDARY / CLOSED | SELECT整行或CAST TEXT AS BLOB可能先物化巨大字段；使用blobopen取长度/有界正文和元数据字段，目标只取数值列，不把hash_id等无界TEXT带入。 | 精确材料化仅[1,2,8,9]；超正文预算时selected_view调用=0；候选v3b001-local-1最终复测通过。 |

日志：[最终pytest](../../../../../artifacts/validation/development-v3/V3B001/attempt-05/pytest.log)、[ruff](../../../../../artifacts/validation/development-v3/V3B001/attempt-05/ruff.log)、[mypy](../../../../../artifacts/validation/development-v3/V3B001/attempt-05/mypy.log)。一次FastAPI/httpx弃用告警，无skip；未为消除告警改依赖。

当前无B001组件阻断。生产执行保持未启用；B002必须接管IO回调、profile、硬资源与真实取消，B007仍需五组真实自动L1证据。
