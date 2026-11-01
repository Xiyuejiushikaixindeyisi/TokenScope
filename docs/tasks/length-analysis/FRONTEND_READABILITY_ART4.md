# AR-T4 中文具体改法与真实封存报告

2026-10-31，身份 `art4-readable-local-1`。接入修复，不重启ARTA；仅新增构造验证fixture/样例/交接，无业务源码、公共接口、生产默认配置或前端表单修改。协议仍为 `analysis-recommendations-1`；旧 arta-local-1 及其样例保持不变。

## 本地状态与身份

- task_id：`716967b3-3e69-4f58-82e8-37f5e7715b8d`。
- service_instance_id：`2fceceeb-ea9d-4d67-9c63-da25cca35c1e`。
- input_root：`/home/zhangxiyue/TokenScope/artifacts/validation/art4-readable-20261031-01/test_chinese_recipes_actual_se0/inputs`。
- state_root：`/home/zhangxiyue/TokenScope/artifacts/validation/art4-readable-20261031-01/test_chinese_recipes_actual_se0/state`。
- appid=`synthetic-orders`，GLM-5.2固定资产，原scope两请求；输入含另一appid验证隔离。
- 构造业务策略：同级 synthetic-recipes.json；真实本地构造引用映射：synthetic-reference-map.json。映射已读取核对全文，**不表示生产工具支持 fixture:// 协议**。

## 中文方案与真实结果

| 规则/方案 | 具体操作 | 原scope输入Token | N/M |
| --- | --- | --- | --- |
| T2 订单查询结果只保留订单号与状态 | 对 query_orders 返回数组的每条订单保留 order_id、status，移除 debug_log；订单条数和顺序保持不变。 | 4144 → 2388 | 2/2 |
| T3 汇总工具的重复订单全文改为快照引用 | 将 summarize_orders 参数 document 中与查询结果完全相同的订单全文，改为 document_ref=fixture://orders/snapshot-001；该引用已在本地构造映射中核对，生产消费协议未验证。 | 4144 → 3224 | 2/2 |
| T3 删除重复粘贴订单全文的普通用户消息 | 删除仅包含这份完整订单快照的重复 user 消息；保留最初的汇总指令、query_orders 工具结果和工具调用消息。 | 4144 → 3206 | 2/2 |
| T4 保留最近1份订单查询结果，替换较早结果 | 在同一请求中保留 query_orders 最近1份完整结果；较早结果替换为 {"omitted":true,"reason":"较早订单快照已省略"}，保留工具消息与调用关系。 | 4144 → 3240 | 2/2 |

四项方案分别从原scope独立评估，不能相加收益。T2保留数组条数/顺序；T4保留最近1份完整结果，仅较早结果替换为明确JSON标记；T3引用和普通副本删除是两个独立方案。工具定义仅用于身份/消费schema验证，未做工具定义精简。

## 证据与验证

- 新测试 `tests/integration/token_content/test_readability_art4.py`：真实Monitoring导入、DiagnosticService/worker、编码、完整scope回放、封存，再由实际create_app GET获取4项推荐/8条局部样例；4项均available，文案与配置一致，N/M均2/2。
- 命令：`.venv/bin/python -m pytest tests/integration/token_content/test_readability_art4.py --basetemp=artifacts/validation/art4-readable-20261031-01 -q`；**1 passed / 10.77s**；ruff通过。一个既有Starlette/httpx弃用warning。仅新增fixture，未重复整套163项或更改其历史结果。
- [实际GET响应与局部样例](FRONTEND_READABILITY_ART4_EXAMPLES.json) · [文件/报告摘要](FRONTEND_READABILITY_ART4_IDENTITY.json)。不是手写收益或伪造HTTP响应。
- 每项basis authority.source_kind=synthetic_fixture，conditions/limitations明确构造边界；生产策略依旧未提供。缺basis局部证据的公共AR-L4修复不由本线代写，本组展示的是完整授权构造方案。

## 前端本地复用

在WSL项目根目录启动只读验收服务（端口未被占用时；本次仅提供命令，未留后台服务）：

```bash
.venv/bin/tokenscope --input-root /home/zhangxiyue/TokenScope/artifacts/validation/art4-readable-20261031-01/test_chinese_recipes_actual_se0/inputs --state-root /home/zhangxiyue/TokenScope/artifacts/validation/art4-readable-20261031-01/test_chinese_recipes_actual_se0/state serve --host 127.0.0.1 --port 8013
```

先GET `/diagnostics/recommendations/capabilities` 获取当前实例ID；后续请求带 `x-tokenscope-service-instance`。不执行POST、不提交新分析、不合并其他测试数据库。无需设置TOKENSCOPE_RECOMMENDATION_BUNDLE，已封存报告直接读取，避免改变生产默认配置。
推荐入口：`/diagnostics/tasks/716967b3-3e69-4f58-82e8-37f5e7715b8d/recommendations`；逐项 `/recommendations/{recommendation_id}/examples`。

只用于本地功能/视觉验收；前端视觉结果由前端签收，不打包部署。

## 前端工程接收回执

2026-10-31，前端 session `01a19111-344a-75c1-84e0-14db8be08f4f` 实际回传：arta-local-1 23/23、ART4 7/7摘要匹配；正式UI-04已读取本组封存state，展示T2/T3/T3/T4四项具体方案、N/M、输入/计算Token变化及8条局部例子（每卡最多3条、首例展开）。前端报告Token浏览器/窄屏检查通过，无T1与评估表单，并明确构造策略及真实离线回放边界。依据见[前端验收入口](../viewer/analysis/ACCEPTANCE_UI04.md)。

此为前端工程接收/验证结果，不是用户视觉批准或独立复审通过；后两项仍待进行。本线仅登记回执，没有重复回归、修改源码、启动服务、打包或部署。前端本机服务状态以其验收入口为准，不重复启动端口。
