# AR-L4 局部证据修复交接

2026-10-31，公共session 01a18be2-7112-7aa2-919b-5137d1f1b1ad。身份arpc-local-2。本轮修复前端PROMPT_PUBLIC_READABILITY_ARL4指出的已批需求缺口，不新增探测器、收益逻辑或公开字段。arpc-local-1交付和原始状态保持不变。

## 修复内容与消费语义

1. L1修改前后、L4原请求A/B均在已验证JSON pointer上解码字符串，线性比较公共前缀/后缀，将实际差异区间写入既有source.text_range，再用lossless映射生成raw_span/excerpt及邻近context。不搜索原文第一次匹配，不重新序列化JSON。多个分离变化采用涵盖区间，仍受片段预算截断；不声称一次定位穷尽所有差异。非字符串或歧义位置沿既有明确定位/失败语义，不造高亮。
2. L1有可靠同pointer Finding且当前请求属于其A/B时，既有comparison补另一条原始请求局部；before始终是当前原请求，after始终是修改副本。comparison是另一原请求，不是另一修改版本。前后删除字符串的after可以空串、raw_span为零宽锚点且仍有上下文，不能把空串显示为无数据。
3. L4不再从大消息头部取稳定重复文本。L5组change_summary改为“对照相关工具返回的原始片段，保留 JSON 空白与数值词法差异”。excerpt/context是**原始JSON文本片段**，直接原文模式显示；不可parse/stringify，不把raw转义当失真，也不将Unicode码点offset当JS UTF-16下标。
4. Token advice_only从已通过validate_support的fragment/location引用读取原问题before例子，最多3例、不加载全部请求语料。after/comparison仍null，N仍null、evaluation/metrics仍null；不因为可展示例子而声称有授权或收益。无需修改Token私有代码。

Schema、路由、分页、最多3例、全体成员计数及严格收益门槛均不变。推荐/差异/收益身份仍按既有任务隔离；旧封存任务不会自动改变。公共新Schema manifest和http-manifest摘要完全不变；旧冻结契约文件未编辑。

## 实际验证

31 passed / 64.90s：定位/Schema冻结/归组、公共自动链和GET、真实Token自动链（三模型T3、T2/T4、零负收益与P降C升）；新增长文本末尾差异、转义/emoji、删除零宽锚点及重复key不可定位检查。加强L1实际A/B/范围/短片段和缺依据before断言。随后增加L4实际短片段/范围断言，单项补验1 passed / 8.63s（已有用例重跑，不累加独立用例数）。4个改动源码mypy、源码/测试ruff通过。既有Starlette/httpx弃用warning，无新依赖。

```bash
.venv/bin/pytest tests/unit/analysis_common/test_evidence_locator.py tests/unit/analysis_common/test_recommendation_freeze.py tests/unit/prefix_analysis/test_recommendation_groups.py tests/integration/analysis/test_recommendation_engine.py tests/integration/analysis/test_recommendation_frontend_reports.py tests/integration/analysis/test_recommendation_http.py tests/integration/token_content/test_auto_recommendations.py --basetemp=artifacts/validation/arl4-20261031-01 -q
.venv/bin/pytest tests/integration/analysis/test_recommendation_frontend_reports.py --basetemp=artifacts/validation/arl4-focus-20261031-01 -q
```

日志：artifacts/validation/arl4-tests-20261031.txt、arl4-focus-tests-20261031.txt。重跑须换新basetemp，不清掉前端正在读取的状态。本轮只改证据生成/说明，未改app/监控/评估算法，因此未重复全套监控回归。

## 新读取对象

[实际GET样例](FRONTEND_REWORK_READABILITY_EXAMPLES_ARL4.json)包含6组状态/9份报告，均由真实create_app(start_worker=False)读取。[源码/Schema/样例摘要](FRONTEND_READABILITY_IDENTITY_ARL4.json)记录相对arpc-local-1的变更。构造请求/策略、真实固定模型编码与回放，不证明生产质量或授权。

- 低命中/L4：task `070ed471-71d8-4619-8902-b7fd97b3f725`，scope `scope:be1e1540c0e82fe2ed427ec70b52256d582cb181a3fd31188ea2cdb69f332e78`。首个L1 before为`2026-10-31 09:00:00`，after为空删除锚点，comparison为另一原请求的差异字符及完整邻近上下文；L4首例为`0`对`5`及上下文，不再1024稳定字符。
- L5任务 `486eed92-2dfb-41c2-9c44-f5660296550c`，同一低命中状态目录。
- Token完整ready `aca29b83-801d-46b8-9d69-9b1122b483b7`，scope `scope:d179201ec2af7d12025cf76af50bc87688df95055273c8fb29a52df69c52810f`，recipe_id=advice现在有原始工具返回before；after=null、N=null。

WSL项目根目录本地启动：

```bash
.venv/bin/tokenscope --input-root artifacts/validation/arl4-20261031-01/test_frontend_low_hit_and_diff0/inputs --state-root artifacts/validation/arl4-20261031-01/test_frontend_low_hit_and_diff0/state serve --host 127.0.0.1 --port 8013
.venv/bin/tokenscope --input-root artifacts/validation/arl4-20261031-01/test_real_same_task_recommenda0/inputs --state-root artifacts/validation/arl4-20261031-01/test_real_same_task_recommenda0/state serve --host 127.0.0.1 --port 8014
```

两个命令分别在终端启动；capabilities取得各自实例ID，按AR-L3只读GET读取，不重新POST分析。这里给出启动方式，本轮没有启动持久服务、修改正式前端、打包部署或写回旧报告。前端仍负责其正式UI接入与浏览器验收。
