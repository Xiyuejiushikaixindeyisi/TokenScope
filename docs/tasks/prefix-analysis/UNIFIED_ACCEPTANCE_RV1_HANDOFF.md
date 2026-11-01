# RV1 同实例两方向联合验收状态交接

2026-11-01，公共session 01a18be2-7112-7aa2-919b-5137d1f1b1ad。**已实际生成并验证**，不是计划或拼接旧报告。使用arpc-local-3现有业务源码/Schema/API和Token ART4策略；新身份unified-acceptance-rv1-20261101-1只标识验收数据/生成脚本，不提升业务源码版本或声明独立复审通过。

[实际响应样例](UNIFIED_ACCEPTANCE_RV1_EXAMPLES.json) · [输入/策略/运行/源码身份](UNIFIED_ACCEPTANCE_RV1_IDENTITY.json) · [生成脚本](../../../scripts/generate_unified_acceptance_rv1.py)

## 单一绑定

- input：`/home/zhangxiyue/TokenScope/artifacts/validation/unified-rv1-20261101-01/inputs`
- state：`/home/zhangxiyue/TokenScope/artifacts/validation/unified-rv1-20261101-01/state`
- service_instance_id：`0cf8b18b-224f-44f3-959d-bbfc1cfe010e`
- binding_id：`f860b372ec762939acba36cbffbfebab82e97836215f52df683a96900b0e2256`
- appid=`synthetic-orders`，model=`GLM-5.2`，source_kind=`base`，common_name=`null`（base来源没有common_name，不伪造值）。所有任务同一真实base_run与scope。
- base_run：`3e59424e-37a2-45d3-b949-1ce37dc3452a`；scope：`scope:1933454c2c53157fb810a68e7c76a3a6ca1effd1dd84db5468bb4d25524de868`。
- 新CSV含7请求，其中本appid6条，另一appid1条明确排除。原ART4请求/策略仅只读复制为新构造输入，未读取合并旧数据库。

## 历史与默认

| 标签 | task_id | 终态 | 分析完成时间（API原UTC） | 方向 |
| --- | --- | --- | --- | --- |
| history_ready | `d69ce286-8461-4b0e-bc95-83b341b9c47b` | ready | 2026-11-01T05:54:13.303Z | low_hit, token_content |
| default_ready | `4f5a4bd6-c09e-4ac4-a5aa-9f5fdd832633` | ready | 2026-11-01T05:54:28.221Z | low_hit, token_content |
| latest_partial | `11ab16c3-1ea4-4d71-b6d7-a41b828564ee` | partial | 2026-11-01T05:54:33.235Z | low_hit, token_content |

两方向defaults均指向`4f5a4bd6-c09e-4ac4-a5aa-9f5fdd832633`。第一份ready保持可固定读取的历史；最新partial用max_proposals=1明确预算耗尽，低命中成果保留、Token提案不完整，不替换任何方向默认。原算法按完整6请求运行，不缩scope、不伪造ready。此次提供partial而非empty，不宣称本次另生成empty场景。完成时间与published_at/sequence/绑定/默认引用完整值在样例terminal/catalog。

每份完整报告含1张合格L1及4张Token量化建议（T2、T4、T3引用、T3普通重复消息删除），并有L4/L5代表差异。不同上下文产生多个差异组，保留真实分组结果，不为界面演示手工合并。每组最多3例，N/M来自完整回放。

| 方案 | 推荐ID（默认ready） | N/M | 输入P | 计算C |
| --- | --- | --- | --- | --- |
| T2 / 订单查询结果只保留订单号与状态 | `rec:8560b5bf370566a7615483f72679df7c3c7d388fca701b84636bf1512bc98995` | 6/6 | 21582→16272 | 21582→16272 |
| L1 / 请求前部动态内容影响相同指令复用 | `rec:d17fdf64851377f247b3890f556127bd0ade35b5e69cc4a2369322f373dc1b2e` | 6/6 | 21582→21504 | 21582→6400 |
| T3 / 汇总工具的重复订单全文改为快照引用 | `rec:072f13ab636d1e7145f8f6d5afd55b756248c45272700ea6beff4c826d05a93b` | 6/6 | 21582→18822 | 21582→18822 |
| T3 / 删除重复粘贴订单全文的普通用户消息 | `rec:b804269a9544c0d2e68dce4d835194b5fbdfc55cfb478e271416e544d4caa569` | 6/6 | 21582→18768 | 21582→18768 |
| T4 / 保留最近1份订单查询结果，替换较早结果 | `rec:4a12f952c6d8f49ddd903247310c23cc8409c4322537d1a15e469b1332d56048` | 6/6 | 21582→18828 | 21582→18828 |

L1完整命中率提升为1475/21个百分点，约70.24pp，超过严格1pp门槛。不同方案分别从同一原请求评估，不是先应用L1再算Token，更不能相加收益。局部例子来自真实GET；完整响应（含每任务全部例子）保存在`artifacts/validation/unified-rv1-20261101-01/actual-unified-rv1.json`，文档样例仅选择L1/T2/L4/L5代表项且保留原响应。

## 数据来源、验证和限制

复用`tests/integration/token_content/test_readability_art4.py`对应ART4的synthetic-recipes.json、synthetic-reference-map.json和CSV。构造每请求不同的system时间戳，增加稳定汇总指令；仅交替改变较早工具结果的JSON缩进，值不变；较新工具结果/参数/普通消息保持相同完整载荷供T3。策略仍只适用于构造订单，映射在生成前实际读回核对，不是生产授权或远程引用可达性证明。

实际执行命令：

```bash
.venv/bin/python scripts/generate_unified_acceptance_rv1.py --output artifacts/validation/unified-rv1-20261101-01
```

退出0/PASS，wall40.57秒，峰值RSS558548 KiB（开发机测量，不是SLA）。日志`artifacts/validation/unified-rv1-run-20261101.txt`与`unified-rv1-time-20261101.txt`。脚本ruff通过。保留既有Starlette/httpx弃用提示；transformers提示无PyTorch，本流程只用真实Tokenizer/配置/离线模拟，没有模型推理要求。

校验包含：两份ready各有合格L1/T2/T3/T4及L5；三任务同scope、M=6；每例组≤3；单绑定/实例两个默认引用只指第二ready；更新partial不覆盖。使用create_app(start_worker=False)实际HTTP读取capabilities、recommendations、difference-groups、examples、summary、terminal、catalog，同时将分析、编码、process_next、submit替换为抛错函数，全部GET仍成功。目录与封存由正常服务生成，没有SQL写入、实例伪装或API改动。

本轮检查独立复审候选记录的公共源码/测试/共享装配/Schema脚本/契约/Token依赖摘要均未变。只新增验收生成脚本、数据和交接记录；未改业务源码/正式前端、全局默认策略、AR-L5/ART4原始证据或旧身份。不需要重跑全套后端回归。

## 单服务读取方式

在WSL项目根目录，先确认所选端口未被其他会话使用。以下启动一份后端，前端两个方向必须共同代理此服务；不要再将两方向代理不同state。实例请通过capabilities再次核对。

```bash
.venv/bin/tokenscope --input-root artifacts/validation/unified-rv1-20261101-01/inputs --state-root artifacts/validation/unified-rv1-20261101-01/state serve --host 127.0.0.1 --port 8016
```

本轮未启动持久服务，前端可按其本线授权启动后选择一个统一页面地址。读取不需配置recipe环境变量或POST分析；已有报告已封存。不要复用上面的output生成命令：脚本遇已有目录明确拒绝，重建请换新目录，保留正在验收的state。没有打包部署。

## 独立复审事实核对

截至本次核对，低命中/公共与Token入口仍是INDEPENDENT_REVIEW_HANDOFF.md及候选身份，明确未启动独立复审；当前memory/SESSIONS和delivery入口没有本次后端复审完成登记，在相关任务目录未找到实际独立复审结果报告。本线没有可提供的“已通过”结果路径，不能将提供方自审/测试或前端消费签收称为独立复审。若用户所指报告来自其他位置/会话，应据实际报告进一步核对，不猜测其结论。

[公共复审准备](INDEPENDENT_REVIEW_HANDOFF.md) · [Token复审准备](../length-analysis/INDEPENDENT_REVIEW_HANDOFF.md)。前端已自行启动的只读独立审查属于前端范围，不等于两后端复审已完成。
