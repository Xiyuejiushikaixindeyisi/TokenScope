# RV2-L 低命中/公共侧聚合展示交接

2026-11-01。维护session 01a18be2-7112-7aa2-919b-5137d1f1b1ad；承接异常分析总负责session 01a19111-344a-75c1-84e0-14db8be08f4f的RV2-L请求。已核对其最新用户授权：前端修复、后端归口验证、联合验收与统一Git收口。公共侧不自行提交/push、不改正式前端、不打包部署。

当前业务身份保持 **arpc-local-4**，本轮只增加验证脚本、交接及记忆；未变更冻结接口、Schema或业务源码。公共独立复审已通过；Token私有独立复审由其本线推进，不以本回执代签。

## 可直接实现的映射

- 固定service_instance_id、task_id、scope_id后，GET `/diagnostics/tasks/{task_id}/difference-groups?limit=100&offset=0`，按next_offset读到null。每页校验身份/availability；读取失败保留错误，不将已读页冒充全量。
- 按items[].data.rule_id归并L4、L5，有发现才生成对应的一张卡。group_id仍保留作证据寻址，不能再作为卡身份。分页顺序由display_order、id稳定排序；不要假设同rule连续。
- 影响范围是各组member_requests的并集，key为完整`[base_run_id, source_record_index]`；index为十进制字符串，不转Number。不同base_run同index不同请求。计数应称“涉及请求数”，不是经因果核验的优化影响数。不累加组人数、finding数或例子数；两类间也不能相加成独立请求总数。
- summary.difference_group_count仅是L4+L5组数，不是卡数或受影响请求数。此接口没有按rule服务端聚合，summary不能替代分页读取。
- 本类所有组members_complete=true且分页完成，才表示本类已封存发现的成员覆盖完整；false时显示已发现范围/下界，不宣称全量。空集合不能用all([])=true证明无异常；结合availability与读取完成状态区分“没有已封存发现”和“未计算”。整个task partial不自动否定某类完整性，Token可能单独预算不足。GROUPING_UNRESOLVED与members_complete是不同维度：前者表示严格上下文归组未成立，不否定已观察的差异对。
- 每类最多选择3个example_refs非空的组，调用各组examples接口，总展示最多3例。可每组取1例，不需要凑满3例；少量代表不表示全组覆盖。保留owner_id、example_id和task_id以追溯完整JSON，不制造前端诊断或收益。
- 跨组example_id含group身份，不能据此判断原始对照是否重复。可将before/comparison的source（完整request_key、raw_sha256、source_pointer、embedded、text_range）按稳定字段序列化，两侧排序组成无向指纹去重。相同请求对不同位置是不同证据；仅按request_key去重例子会误丢位置。请求计数则只按RequestKey，与例子指纹分开。
- 保留每例reason_codes、omitted标志和零宽区间。无可读例子时保留发现卡和原因，不编造片段。L4不认定同会话历史改写；L5不把表示差异自动等同于可无损修改。两类不应用收益门槛。

容量：元数据分页可降低前端保留组对象数量，但精确去重仍需O(唯一请求数)集合；每组member_requests本身不分页，服务端OFFSET查询也不是严格常量代价。当前可按页释放组元数据、仅保留两类请求key集合和最多3组引用；若有读取预算中止应明确部分范围，不能悄悄给精确数。15万请求规模未校准，本次不新增聚合端点或宣称容量通过。

## RV1实际值及代表例子

在同实例RV1复制状态，用当前代码读取history_ready、default_ready、latest_partial三份任务，三份均得下表。默认仍指第二份ready，最新partial不覆盖任何方向。

| 规则 | 组数 | 组人数之和（禁止展示为影响数） | 唯一涉及请求数 | members_complete | 代表请求对与位置 |
| --- | --- | --- | --- | --- | --- |
| L4 | 20 | 42 | 6 | true | 2↔6、1↔3、3↔4；/messages/0/content |
| L5 | 9 | 18 | 6 | true | 3↔6、3↔4、2↔5；/messages/3/content |

source_record_index均属于base_run `3e59424e-37a2-45d3-b949-1ce37dc3452a`，不能将这些构造例子宣称为现场发现。默认任务为`4f5a4bd6-c09e-4ac4-a5aa-9f5fdd832633`。两类均包含GROUPING_UNRESOLVED；L4代表是系统文本时间戳差异，属于历史内容观察，不认定会话破坏。L5代表是早期工具结果JSON表示差异。用户选择展示1例或最多3例均可。

完整组/请求key/代表局部证据见[实际聚合响应](../../../artifacts/validation/rv2-low-hit-20261101-02/aggregation.json)，完整原JSON仍按现有证据接口追溯，不复制或修改旧报告。

## 实际验证

[可复验脚本](../../../scripts/validation/validate_rv2_low_hit.py)源自独立审查只读验证，增加按rule成员去重、3组/3例上限和实际计数断言。本脚本是维护方接入验收，不冒充新增独立审查。项目根运行：

```bash
.venv/bin/python scripts/validation/validate_rv2_low_hit.py --output artifacts/validation/rv2-low-hit-new-run
```

输出目录必须不存在。复制RV1原目录后使用真实create_app/TestClient；不启动持久HTTP服务。封禁submit/process_next/encode/analyze_request；3任务215个GET路由、limit=1跨页无重漏、summary/terminal/catalog/history/default、错误实例409/非法分页422与旧实际响应一致；原84文件摘要不变。最终脚本格式/导入整理后在`rv2-low-hit-20261101-02`重新执行退出0，ruff通过；初次执行01也通过，两次不累计用例数。日志见[最终运行](../../../artifacts/validation/rv2-low-hit-20261101-02.log)、[只读结果](../../../artifacts/validation/rv2-low-hit-20261101-02/rv1-final-readonly.json)。新脚本初次静态检查报告导入/格式问题，自动整理后通过，没有放宽断言。

业务源码全套依据仍为[arpc-local-4独立复审](INDEPENDENT_REVIEW_RESULT_20261101.md)：146公共/低命中、4独立边界、6Token受影响专项、mypy/ruff通过；本轮未修改业务源码，不重复跑同一全套。

## 提交交接与未决

[精确清单及SHA256](RV2_L_COMMIT_MANIFEST_20261101.json)列源码、测试、脚本、契约、文档、历史记录及共享依赖。只交接文件，不执行git add/commit/push。共享app.py为新增诊断装配/3路由，cli.py为work-once注册同一诊断服务，当前相对HEAD共14行新增/1行删除；其余监控逻辑不改。共同装配应和Token私有源码一起提交，不能只提交公共import却遗漏插件。

源码与契约清单可提交；文档/记忆共享部分由总负责整合后重新计算摘要，不能盲目覆盖其他线。manifest自身不列自身摘要，避免自引用；真实CSV/SQLite、模型资产、artifact日志/截图/包体均不提交，只保留文档证据链接和清单。历史docs可由总负责归档，但原始证据和冻结契约身份保持。

本轮无新后端缺陷、无公共文件编辑窗口。Token审查尚在进行，若发现公共归口问题需重新登记文件/版本并复验；合入前由总负责等待其结论并重核共享依赖摘要。未决仅前端聚合实现/用户验收、Token私有复审、现场容量/真实策略；本回执不代签这些项。无打包部署。
