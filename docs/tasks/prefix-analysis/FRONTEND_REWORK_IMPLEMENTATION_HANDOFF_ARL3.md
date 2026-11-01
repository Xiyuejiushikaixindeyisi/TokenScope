# AR-L3 公共后端实际实施交接

2026-10-31。维护方：低命中/公共 session `01a18be2-7112-7aa2-919b-5137d1f1b1ad`。当前身份 `arpc-local-1`。ARPC000–006结果以[最终验收](../analysis/batches/ARPC006/RESULT.md)为准；本文件取代早期AR-L2构造样例作为接入入口。未修改正式前端、打包或部署，不代签前端视觉/浏览器验收。

## 机器入口与 Token 交接

- [公共契约](../../contracts/analysis-recommendations-1/README.md)：`internal.json`供Python/插件，`wire.json`供存储/内部传输；业务GET应使用`public-views.json`，不能按内部Recipe读取私有JSON字段。
- [源码及Schema身份](FRONTEND_REWORK_IMPLEMENTATION_IDENTITY_ARL3.json)、[实际HTTP与报告样例](FRONTEND_REWORK_IMPLEMENTATION_EXAMPLES_ARL3.json)。旧common/http/discovery三份manifest的13个文件保持原摘要。
- [Token适配器](../length-analysis/AUTO_ADAPTER_HANDOFF.md)、[Token实际验收](../length-analysis/batches/ARTA004/RESULT.md)、[Token配置Schema](../length-analysis/AUTO_RECIPE_SCHEMA.json)。Token四方法describe/validate_bundle/propose/prepare_proposal已经由实际适配器消费，非mock联调。
- 新任务静态装配CurrentTokenContentPlugin `token-content-2`，仅T2/T3/T4；自动提案协议 `token-auto-proposals-1`，生成器 `token-content-recipes-1`。旧T1报告读取兼容，不回填。
- 公共维护范围/归组/预算/封存/评估/API；Token维护选择器与生成规则内部DSL、具体目标和guard构造。公共不复制其策略判断，也不复制监控编码/理想命中算法。
- 后台环境变量`TOKENSCOPE_RECOMMENDATION_BUNDLE`指定RecipeBundle JSON；提交冻结依据、配置、适配器与预算，原submission_key及retry保持原快照。默认空配置会明确显示configured_recipe_count=0、NO_CONFIGURED_RECIPES；这不是所有问题均不存在。构造策略不能直接充当生产授权。

## 实际 GET

无前端发起分析/修改/评估流程。先读`GET /diagnostics/recommendations/capabilities`，取得service_instance_id，再带`x-tokenscope-service-instance`读取：

| 路由（前缀 /diagnostics/tasks/{task_id}） | 返回用途 |
| --- | --- |
| /recommendation-summary | availability、配置数、两阶段coverage、预算/消耗、原因及stop_location |
| /recommendations | 推荐列表；可用direction=low_hit或token_content筛选 |
| /recommendations/{id} | 单项推荐与完整评估引用 |
| /recommendations/{id}/examples | 最多3条局部before/after |
| /difference-groups | L4/L5差异组与成员总计 |
| /difference-groups/{id}/examples | 最多3条局部请求A/B对照 |

列表offset为规范非负十进制字符串，limit=1–100（默认50），next_offset=null结束。同一封存task稳定排序，不跨task拼页。整数wire为十进制字符串；分数为numerator/denominator，禁止JS Number直接承接大整数后再比较。完整实际响应见EXAMPLES文件。

缺实例header或非法分页422；实例不匹配409；对象不存在或不属于任务404；未封存/新契约不兼容409；存储故障503；不存在POST（405）。旧报告availability=not_computed，列表空、详情404，不能展示“无异常”。新版本不隐式重算旧成果。

## UI-04 字段映射

| 展示 | 精确来源与约束 |
| --- | --- |
| 标题/建议 | recipe.title/change_summary，primary_rule/category_rules；不将内部JSON直接铺到页面 |
| 方案依据 | recipe.basis.kind/ref/revision/digest/authority/assumptions/limitations；完整选择器/参数/依据作用域仅公开摘要 |
| 影响请求数 | impact.modified_requests / total_requests，即完整原scope实际raw改变N/M；不是Finding数，不是3个样例数，不跨卡相加 |
| 匹配覆盖 | matched_requests、matched_checked_requests、match_complete；matched是可执行目标去重请求数，缺依据建议不冒充可执行匹配；未知为null |
| 低命中主卡 | display_qualification=low_hit_optimization；完整full/direct_full严格提升>1个百分点；metrics.gain_percentage_points是百分点，不能再乘100 |
| Token结果 | token_evaluated不等于获益；metrics.input_tokens_delta/compute_tokens_delta=after-before，ratio是相对before，前值0则null；零收益、负收益以及P降C升都保留 |
| 未评估建议 | token_advice及status/reason_codes，metrics=null，不能补0或伪造after |
| L4/L5差异 | difference_group独立展示，不套收益门槛；成员RequestKey并集全计，≤3例只是展示上限 |
| 局部证据 | before/after或comparison；raw/decoded codepoint span、request_key/raw_sha256、pointer、截断标记；按Unicode码点解释，不按JS UTF-16直接切片 |
| 调查引用 | support_refs、prepared_plan_ref、execution_plan_ref、evaluation_ref；复用执行仍保留每项独立依据与prepared Plan，按task_id隔离 |

低命中主卡不必展示Token变化；Token卡分别展示输入与计算Token变化，不能由P减少推导C减少或模型质量不变。局部展示无法唯一定位时保留reason，不造高亮。完整原请求和完整两请求证据仍由底层既有证据接口提供，业务详情默认采用局部样例。

## 状态、预算与默认报告

queued/running未发布；ready表示请求的分析与所需阶段完整，不保证有收益；partial表示已有成果但检查/评估/证据不完整；interrupted/failed不造完整after。推荐的proposal_status、preparation_status、evaluation_status与聚合status分别展示，缺业务依据是advice_only，非法依据/guard/系统预算为blocked/failed或阶段不完整。

完整缺依据说明可以ready；缺策略不等于技术故障。proposal扫描不完整不生成缩小scope的全量收益；完整扫描后每方案独立guard，再完整原appid范围评估。不同依据相同操作仅在各自验证后复用同次执行，既有自动组合在新推荐模式关闭。

默认新预算：256 proposals、32推荐组、10000操作、单提案1MiB、单Plan16MiB/合计64MiB、8次Token评估、每组3例、片段1024码点/上下文128码点/每组24KiB。编码沿原TaskControl全任务共预算。精确配置以封存summary为准；达到边界允许，超过停止，提供coverage、reason_codes、消耗和stop_location。低命中原检测/试验受原RuntimeOptions约束，新增推荐发布预算校验已保存Plan，不把此发布校验称为前置内存限制。

目录/通知继续复用diagnostics-discovery-1：首次partial仅历史；empty不替换默认；两方向整体ready才更新其包含方向默认引用。GET只读取封存成果，不触发分析、编码或任务写入。终态与发布沿原事务/outbox机制。

## 可复现数据与本地启动

EXAMPLES.datasets逐项记录真实input_root/state_root/service_instance_id、task_id、完整scope及模型/编码/profile身份、封存report摘要、API结果及局部例子。测试输入/策略为明确构造；编码/修改/回放和GET是真实执行。包含低命中优化、L4、L5、T2/T4、T3三模型、预算partial、legacy和P降C升。

本次持久测试根目录：`artifacts/validation/arpc-final-20261031-02`。前端优先使用EXAMPLES中`test_frontend_low_hit_and_diff0`（低命中/L4/L5）及`test_real_same_task_recommenda0`（Token/历史/partial）两个独立状态目录。不要合并数据库；每个服务读取自己的实例ID。

WSL项目根目录执行（仅本地服务；不要构建viewer、不执行任何POST）：

```bash
.venv/bin/tokenscope --input-root artifacts/validation/arpc-final-20261031-02/test_frontend_low_hit_and_diff0/inputs --state-root artifacts/validation/arpc-final-20261031-02/test_frontend_low_hit_and_diff0/state serve --host 127.0.0.1 --port 8011
```

另一终端将目录替换为`test_real_same_task_recommenda0`、端口8012。CLI复用现有服务；默认worker无需补算这些已封存任务。严格禁用worker的测试读取使用`create_app(service,start_worker=False)`（本次HTTP导出采用此方式）。不需要生产策略文件即可读取已有封存结果；新分析则必须另行配置适用依据。

若重跑测试，使用**新的**basetemp目录并更新任务清单，不覆盖上述前端正在读取的状态目录。复现命令及测试数据入口见ARPC006；原始产物默认不入Git。

## 本次真实回放的代表结果

| 方案（均为构造策略/输入） | 实际完整结果 | 展示处理 |
| --- | --- | --- |
| L1，task efb6cd64-c3f7-4d42-9bbe-ef38b1dc0da3 | N/M=6/6，P=2688→2610，C=2688→1330 | 通过完整收益门槛，低命中优化卡 |
| T2 shorten，task ae3c5d14-467d-4d9d-b0cb-7eadd76b17b5 | N/M=2/2，P/C=1322→1318 | Token评估卡；不同依据同执行仍两条方案 |
| 同task的noop | N/M=0/2，P/C不变 | 保留零收益；不能写2条请求已修改 |
| 同task的T4 negative-benefit | N/M=2/2，P/C=1322→1916 | 明确Token增加，不能显示优化成功 |
| T2 boundary，task 537bc369-d784-4a2d-8546-0ca3f5bd86d3 | N/M=2/2，P=1026→1022，C=642→766 | 分开标输入减少4、计算增加124 |
| 缺依据advice | N=null、无evaluation、metrics=null | 缺依据建议，不能填零收益 |
| Plan预算失败，task 8a1c3b63-a646-4101-94dd-36dfeeb3173d | partial、blocked、无悬空Plan引用 | 展示停止原因，默认仍读旧ready |

具体规则、依据、tokenizer/模板身份、全部Plan/Evaluation引用和真实片段都在EXAMPLES中，表中数字不是UI手工构造。

## 前端会话接入 prompt

请先读本AR-L3实际交接、IDENTITY、EXAMPLES和公共public-views.json，再读Token AUTO_ADAPTER_HANDOFF及ARTA004 RESULT。核对文件摘要，以现有UI-04获批设计消费真实只读GET。低命中优化、L4/L5差异、Token评估/缺依据分别处理；N/M与3个样例分开；负收益、P降C升、partial和legacy不得伪装成功或无异常。用EXAMPLES标明的本地状态与两个端口复核实例/分页/默认报告，不提交分析任务，不自造后端字段，不将内部策略JSON公开。正式前端实施按你本线已有授权推进；本交接不代替前端验收，也不授权打包部署。若接口问题，给出task/scope/route及实际响应，通过交接文档反馈公共或Token归属方。
