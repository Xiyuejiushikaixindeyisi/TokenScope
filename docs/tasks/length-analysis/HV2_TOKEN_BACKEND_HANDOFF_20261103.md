# HV2-R2-TOKEN 私有后端交接

2026-11-03；维护方session `01a18fcd-0464-7cf1-b435-4f394bd33e66`。角色/授权为Token私有性能优化及冻结公共消费验证。实现/小样本验证完成后交总设计师独立验收，不代签现场或前端。没有监听服务、Docker、打包部署、Git提交/push、跨会话消息或新agent。

## 来源与精确范围

派发HEAD `7cbe28621f4e46083bf47f9aa14b011b3cb250c4`；公共冻结 `9ac3e7fd5c5fea9556f957871bb03a0791e79e9404b207462a1cf8e184d7cb8e`。开工48文件摘要全部匹配。后续复核只有prefix_analysis/service.py、detection.py两项私有低命中文件随其授权R2工作发生漂移，公共机器契约/公共运行时未漂移；本线未编辑它们，不把同时变化的低命中私有模块代签为冻结旧版。环境/漂移列表见证据environment.json，最终逐文件身份见本线HV2_TOKEN_IDENTITY_20261103.json。

已读取公共交接、diagnostics-execution-2和用户2.1.0交接。Trace来源仍user_v2/user_run_id/appid/expected_index_revision/window=null；base_run仅核对，不同填；MA独立数据。本轮小样本是base测试来源，不冒称现场user_v2全规模已复验。

产品源码仅两文件：`src/tokenscope/token_content/extraction.py`、`measurements.py`。新增本线测试/辅助：`tests/unit/token_content/test_hv2_identity.py`、`profile_hv2.py`、`profile_hv2_paired.py`；`tests/integration/token_content/test_hv2_consumption.py`。文档仅本交接/身份及本线ENTRY/记忆。PREP和原始现场报告保持，不改共享总文档。

## 修复与不变项

实测提取成本包含同一结构节点两次规范序列化：measure计算display_json_utf8_bytes及add计算content_sha256。现在仅结构值同次add共用canonical字符串；字符串保持原先measure后dumps的顺序。measure原单参数调用兼容，新内部可选canonical_json；不是HTTP/插件协议变更。没有Inventory跨recipe复用、跨请求缓存、改变预算计费/停止点、删除工具库存或绕过Schema。T2–T4范围及旧T1报告兼容保持，未造任何生产recipe或可删除结论。

公共已实现空recipe免提案扫描，本线不再重复添加空返回；内容检测仍按选定方向执行。低命中全局findings与Token私有预算分离，不使用此前错误因果。缺basis仍advice/null，未知不是0。L4/L5、前端只读、两大Qwen仅low_hit边界保持。

## 实际profile及效果

原始证据根 `artifacts/reviews/hv2-token-20261103/`，所有目录保留：before（改前）、after（初版）、baseline-repeat（失败的辅助脚本运行残留）、baseline-fixed、optimized-repeat/final、final-profile（最终源码）。每完整profile含阶段.prof、results.json、fragment原文及独立SQLite写入；每阶段5次无插桩wall/process CPU，另做tracemalloc峰值、cProfile和字节计数，插桩结果不当裸耗时。内存是Python追踪峰值，不是进程RSS上限；写入含连接建表提交，不代表现场SQLite吞吐。

覆盖5种结构：普通messages重复/合法引用对照；64字段长Schema；宽内嵌JSON含完全重复及近似但非法JSON尾缀；12层嵌入结构；24工具结果链。wide按真实语义记录局部提取不完整，不把非法近似例改成完整。T2/T4没有策略时只内容观察；T3普通消息无tool_result不归为重复候选。proposal/prepare用已有明确synthetic_fixture单请求策略，不是生产授权。

| 样本 | 基线→最终递归dumps调用数 | 交错提取中位ms 基线→最终 | 判断 |
| --- | --- | --- | --- |
| 长Schema | 4705→2821 | 9.364→7.906 | 减少40%序列化调用；本机提取约15.6%改善 |
| 宽JSON | 2064→1518 | 6.297→6.294 | 降低工作量，耗时接近持平 |
| 深结构 | 624→428 | 1.107→0.886 | 本机提取约20%改善 |
| 普通messages | 59→59 | 0.297→0.312 | 约15.6微秒波动/开销，不宣称加速 |
| 工具结果链 | 171→171 | 0.666→0.647 | 工作量不变，不把微小差异外推 |

表中调用数来自baseline-fixed/final-profile，耗时来自paired-final.json：同进程30轮AB/BA交错、无插桩，仅比较extract。初版两次交错测得wide约8–9%回退，保留记录paired.json/paired-repeat.json；改为保留字符串原顺序后paired-string-preserved.json与paired-final.json分别约+1.5%和持平。Schema和深结构两轮均有收益；其他样本无全路径加速承诺。最终Schema tracemalloc约727KB→730KB，增加约0.4%，没有声称绝对零内存增长；其余样本峰值见原始JSON。

五种完整fragment序列化SHA、units/locations/observations及coverage/rules/consumed均与改前一致，final-identity-comparison.json与5项golden回归固化。profile保存loads/dumps/hash/extract调用与字节、单位/比较/候选/encoding计数、原始/fragment字节；递归dumps字节包括嵌套重复，不能当输入大小。所有此类分析样本无编码调用，但解析/序列化成本真实存在。proposal和prepare、序列化和写入阶段分别保存，不将嵌套累计时间相加。

## 消费与回归证据

- 中间源码全量私有+公共v2消费：182 passed，175.24s，regression.xml；包含公共单方向、空recipe、内部fragment不完整、保留不足、插件失败、retry和只读TestClient。不是现场E2E。
- 新增私有失败哨兵：low_hit-only analyze/propose/prepare全部禁止；EncodingContext.encode允许低命中自己的编码，但断言栈无Token私有/推荐引擎路径。通过公共DiagnosticService v2提交，结果只含low_hit、无fragment。
- 新增v2真实缺basis：匹配内容有一advice_only推荐，modified_requests与evaluation_ref为null，未生成收益；v2-consumption-final.xml，2 passed/7.00s（包含上述哨兵）。
- 最终源码私有完整回归170 passed/113.85s，final-regression.log/xml；随后v2专项2 passed/7.00s含1项重复，共171个不同私有用例。中间182项含13项公共v2消费者，不冒称最终业务源码又跑了公共全量。
- 五资源bytes/units/depth/comparison/candidates分别need-1/need/need+1，15组实际记录budget-matrix.json；规则status/coverage/reasons/consumed均保留，低于边界不完整、达到边界完整。原有取消/重试、数值词法、精确比较、防篡改、授权/角色保护、三模型编码、正零负收益测试全部纳入私有回归。
- mypy 17模块通过；ruff最终通过。唯一业务测试warning为既有Starlette/httpx弃用提示，未升级依赖消警告。

失败记录：新增哨兵最初夹具误将SourceIdentity作为SourceSelection，1 failed/3.73s，sentinel.xml原样保留；修正仅测试提交来源后1 passed/3.98s，sentinel-fixed.xml。profile基线加载最初漏替换fixture的extract别名，TypeError canonical_json，baseline-repeat残留和工具输出保留；修正辅助别名后baseline-fixed完整成功，没有改业务代码迎合基线。格式检查初轮有行长/导入/闭包绑定，已格式化与绑定参数，最终ruff通过。没有删除失败断言、覆盖原证据或把partial改ready。

## 复验命令

在项目根目录，使用未存在的新证据目录，不覆盖此次结果：

```bash
.venv/bin/python tests/unit/token_content/profile_hv2.py artifacts/reviews/hv2-token-independent/baseline --baseline
.venv/bin/python tests/unit/token_content/profile_hv2.py artifacts/reviews/hv2-token-independent/candidate
.venv/bin/python tests/unit/token_content/profile_hv2_paired.py artifacts/reviews/hv2-token-independent/paired.json
.venv/bin/pytest tests/unit/token_content tests/integration/token_content -q --basetemp=artifacts/reviews/hv2-token-independent/pytest
.venv/bin/pytest tests/integration/analysis/test_execution_v2_integration.py -q --basetemp=artifacts/reviews/hv2-token-independent/common-consumer
.venv/bin/mypy src/tokenscope/token_content
.venv/bin/ruff check src/tokenscope/token_content tests/unit/token_content tests/integration/token_content
```

--baseline只在辅助进程内从固定Git对象加载原两个模块，不写工作树、不恢复旧公共层。profiler不需监听服务或Docker；配对脚本需先创建父证据目录（前两条已创建）。新测试为真实边界和历史完整身份比较，不以优化实现自证。

## 现场量级预算方法与未决

1. 按实际appid×Trace模型规格分层，再按原始字节、消息/tool_result数、工具Schema节点数/宽度、外层及内嵌深度、重复载荷次数、表示类型分桶；记录有效/拒绝/未知及每层样本数，不按品牌或固定请求数外推。两大Qwen只low_hit，不采Token。真实最小正反例/业务授权仍缺，研究统计不替代授权。
2. 每请求记录max_units用量U、规范比较字节B、候选K、深度D、fragment+index字节F和阶段CPU/峰值。字节大小不能直接换算U/B/F；深Schema及内嵌串分别统计，负例包括few-shot、必要引用、相似非相等与重叠单位。
3. 在用户授权的有界真实样本取得分层分位/最大与停止率后再提预算：私有单请求预算覆盖目标分位但必须报告尾部未覆盖；任务fragment总保留约为各层请求数×平均F及索引/SQLite实测放大，另加旧state保留与临时峰值。独立max_fragment_bytes可拒绝少数巨型片段，总上限与磁盘/RSS不等同。不能只全局抬上限。
4. CPU估算采用各层样本阶段CPU分布加权；I/O/编码/共享竞争/worker调度独立测量，给区间和覆盖，不从终端间隔或本机5样本推现场完成时间。profile当前仅证明代码热点和局部改动；未核验现场8CPU/32GiB下的真实吞吐、磁盘峰值或全请求覆盖。
5. 尚待总设计师独立验收、低命中私有最新组合身份及整链路TestClient/浏览器验收；前端按总设计师通知接入。不需要新增公共补丁或契约版本。现场真实策略/引用服务/质量等价/Token收益仍未知；本轮不增加探测器、参数错配、工具定义精简或自进化Agent。
