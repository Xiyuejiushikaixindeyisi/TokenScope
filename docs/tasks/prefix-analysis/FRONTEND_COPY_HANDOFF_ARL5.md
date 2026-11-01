# AR-L5 具体修改建议文案修复

2026-10-31，公共/低命中session 01a18be2-7112-7aa2-919b-5137d1f1b1ad。身份arpc-local-3，接续arpc-local-2。前端已回执AR-L4摘要和浏览器验证通过，本轮只处理其随后指出的标题/建议描述问题；不代签其全部页面验收。

## 实现与边界

recommendation_projection中新增recipe_copy，读取该规则独立Plan的handler_id、public_primitive及实际target.source_pointer，输出已有recipe.title/change_summary。

- L1：请求前部动态内容影响相同指令复用；对low_hit.dynamic_remove实际Plan指明删除位置与时间戳/路径/动态计费头片段，保留其余消息和指令，并注明业务不依赖该内容、由业务决定采用。
- L2：相同工具集合的排列变化影响前缀复用；对low_hit.sort_tools实际Plan说明按工具名称固定排序，保留全部工具定义，条件是完整集合相同且仅排列变化。
- L3：工具定义中的动态内容影响前缀复用；指明工具定义的实际JSON pointer和动态片段类型，保留其余工具定义，不擅自称为精简整个工具说明。
- 最多列3个不同实际pointer，更多位置标总数并通过局部证据/保存Plan追溯。未完成Plan明确尚无完整修改方案；未知handler/primitive不猜删除或排序。没有把“评估”作为已完成方案的修改动作，也不把离线结果解释为业务授权。

Schema/路由/评估算法/收益门槛/证据字段不变。title/change_summary属于recipe内容，因此新task中的recipe_key/recommendation_id可变化，前端应继续按实例+task+scope绑定；不能拿旧ID串读。旧AR-L3/AR-L4样例、身份与封存报告均不改写。

## 验证

10 passed / 17.25s，覆盖L1/L2/L3实际Plan动作/位置/条件映射、未知handler和无Plan不虚构删除、归组/Schema冻结，以及真实GLM低命中回放与发布。真实生成L1卡片断言具体删除位置、条件与新标题，AR-L4动态片段/A-B断言保持。修改源码mypy和相关源码/测试ruff通过。

```bash
.venv/bin/pytest tests/unit/prefix_analysis/test_recommendation_copy.py tests/unit/prefix_analysis/test_recommendation_groups.py tests/unit/analysis_common/test_recommendation_freeze.py tests/integration/analysis/test_recommendation_frontend_reports.py tests/integration/analysis/test_recommendation_publication.py --basetemp=artifacts/validation/arl5-20261031-01 -q
```

日志artifacts/validation/arl5-tests-20261031.txt。未改计量、任务和Token私有代码，不重复监控/Token全套。L2/L3文案映射有针对性Plan单测，本次新增真实HTTP报告为L1/L4/L5，不声称新增L2/L3真实业务收益验证。

## 新封存报告与实际GET

[实际HTTP样例](FRONTEND_REWORK_COPY_EXAMPLES_ARL5.json) · [增量身份与Schema摘要](FRONTEND_COPY_IDENTITY_ARL5.json)。同一持久状态2份报告，真实create_app(start_worker=False)读取，构造请求和固定模型资产回放。

- task `84b66f17-4362-4f88-adda-65ac7763277e`，scope `scope:bb792d7fa8a77fba6e18850b131e1ce331e5bc6b29d7f9ce9e22e929cb14f72d`，推荐 `rec:82f4849341191b94951421cbda16e80cad56bdf19b0290905fac9f84180f0a16`。标题：请求前部动态内容影响相同指令复用。建议：在业务不依赖该动态内容的前提下，删除/messages/0/content中下面已定位的时间戳片段，保留其余消息和指令；具体位置和删除前后内容见局部证据，是否采用由业务决定。

WSL项目根目录启动本地只读消费服务：

```bash
.venv/bin/tokenscope --input-root artifacts/validation/arl5-20261031-01/test_frontend_low_hit_and_diff0/inputs --state-root artifacts/validation/arl5-20261031-01/test_frontend_low_hit_and_diff0/state serve --host 127.0.0.1 --port 8015
```

先读取capabilities获得该状态实例ID，再读取封存GET，不重新提交分析任务；本轮提供命令，没有实际启动持久服务。重跑测试请换basetemp，保留上述前端读取数据。未改正式前端、打包部署。
