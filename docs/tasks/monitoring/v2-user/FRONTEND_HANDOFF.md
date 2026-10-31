# 用户监控后端 → 监控V2前端交接

当前TTFT状态：**代码完成，性能校准待完成**。新最小模型已实现：W覆盖全部非计算耗时、不单列O；证据材料选填，缺必要参数不出比例、W不默认0。当前用户契约2.0.0，旧1.0.1历史兼容；[前端接入](TTFT_FRONTEND_HANDOFF.md)尚待前端实施/验收。
2026-10-31更新TTFT接口；2026-10-30既有后端交接，不表示前端已接收、实现或联合验收。本会话仅整理入口，不修改UI-01、前端讨论稿或前端代码。

## 读取顺序与版本

1. [本页](FRONTEND_HANDOFF.md) → [已实现API](IMPLEMENTED_API.md)。
2. [契约2.0.0](../../../contracts/user-monitoring-v2/2.0.0/README.md)、[Schema](../../../contracts/user-monitoring-v2/2.0.0/schema.json)、[设计OpenAPI](../../../contracts/user-monitoring-v2/2.0.0/design.openapi.json)。
3. [9份真实HTTP合成响应](../../../contracts/user-monitoring-v2/runtime.examples.json)及[26项正反例](../../../contracts/user-monitoring-v2/examples.json)。前者覆盖三模型Receipt/Ranking/Evaluation，后者覆盖各状态及Modes等；不是现场数据。
4. [验收报告](batches/U005/RESULT.md)、[验收范围](batches/U005/VALIDATION_SUMMARY.md)、[源码及验证摘要](batches/U005/VALIDATION_MANIFEST.json)。

后端开发身份u008-local-1，契约2.0.0，用户control schema1/index算法user-index-1。原V1发行身份、S0 1.0.0、control3/view1不变。设计OpenAPI仍注明设计身份，不能用其x-runtime-implemented=false判断当前未实现；实际服务/openapi.json含9个已实现操作。

前端此前按1.0.0阅读的材料需刷新：1.0.1增加数值文本128字符/普通文本4096字符防护；计数与Token总量范围只接受整数；后续页必须带index_revision；错误码与服务身份头已对齐。字段、公式及统计分组不变。后端不代替用户审批DEMO调整。

## 接入流程

- 同源统一服务地址；先读取既有GET /monitoring/catalog首屏的service_instance_id，后续user-v2请求携带X-TokenScope-Instance-Id。身份失配409时刷新服务身份并清除旧范围，不能把MA UUID当服务身份。
- POST /monitoring/user-v2/runs显式绑定file_ref、common_name、model_id、稳定submission_key；这是受控输入根文件引用，不是浏览器任意路径或文件上传API。重试保留同一key/输入；新操作使用新key。
- 保留返回的user_run_id与base_run_id；GET用户回执观察accepted/base_pending/indexing，ready后读取排行/众数。empty表示合法零有效结果；failed/interrupted显示原因。GET不触发分析。
- 旧基础run通过POST /bindings显式绑定。当前没有用户运行目录或独立用户SSE；前端不能拿旧S0目录中的base_run_id冒充user_run_id，也不能假设跨浏览器自动恢复用户任务列表。保存回执/导航状态的交互由前端阶段明确。
- 需要旧J/P/C图表或请求明细时使用base_run_id读取S0成果；新排行与估算使用user_run_id。两种ID不能互换，不能从页面访问重新编码。
- 后续分页固定user_run_id、common_name、bin_width、index_revision及筛选排序；offset>0必须携带revision。冲突后回首屏重读，不能拼接不同版本页面。
- 情景先显式POST /scenarios登记或按已知id/revision读取；当前无情景列表/自动校准API。POST /evaluations显式评估，输入变化后旧结果标待重新评估，GET只读取原快照。

## 必须保留的展示语义

| 部分 | 前端要求 |
| --- | --- |
| 范围 | GB appid×common_name，每CSV空缓存；服务潜力不是生产实例命中率，不跨CSV混榜 |
| 数据质量 | read/valid/skipped为文件口径；有效子集不称全量流量 |
| 重算 | C=模板后输入P−理想命中H；典型重算长度为众数箱内均值，不是起点或全部请求均值 |
| 众数并列 | 默认5K箱，可切1K/2K；最低并列箱为排序代表，tie_count及Modes分页保留全部峰；200K以上继续等宽 |
| 旧图 | 旧S0三图仍使用原尾桶，MA两图也不继承用户排行开放箱规则 |
| 排序搜索 | 四指标、区分大小写的appid字面子串；%/_不是通配符；范围AND且含端点；全局排序后分页 |
| 数值 | 大整数和精确分数不要先转JS Number再排序/计算；后端排序，前端只格式化。NULL不是0 |
| TTFT | 标题“P90长度请求所需参考前缀命中率”；不得用总体ΣH/ΣP与参考值比较输出达标 |
| 情景状态 | 新模型缺K/τ/W先显示参数未齐和“代码完成，性能校准待完成”，具体比例为—；禁用不完整提交。完整人工假设须显式选择并填W，仍标未校准；no_budget/out_of_scope/unavailable分别展示；0%/100%不构成SLO或可达性保证 |
| 单位 | 秒、Token与0–1比率明确；百分比展示/输入换算只做单位转换，不重算统计或公式 |

## 前端联合验收仍待完成

使用正式前端逐项验证：身份切换、任务恢复/未完成状态、空/错误/部分有效集、分页revision、全部众数峰、极大整数、人工情景与不可用原因、条件改变后的旧估算提示；视觉按最终获批DEMO。后端已完成289全量回归和最终15恢复定点、三模型真HTTP/CLI及MA后端联合；不代表前端验收或真实性能校准通过。

发布和提交范围见[Git交接记录](GIT_HANDOFF_20261030.md)。统一内网开放、部署、镜像和交付包未执行，需另外授权。

## 2026-10-31 TTFT最小方案接入优先级
新接入先读[TTFT专用交接](TTFT_FRONTEND_HANDOFF.md)及[U008结果](batches/U008/RESULT.md)。本页1.0.1刷新说明及原9份HTTP响应是历史基线；新6份ASGI响应见2.0.0目录，O只用于旧历史情景。新模型W覆盖全部非计算耗时；不修改UI-02或正式前端。本线文档交接不表示已通知或前端已签收。

## U006–U008提交交接（2026-10-31）
本轮用户授权提交/push，范围与实际Git身份见[U008 Git检查点](GIT_HANDOFF_U008_20261031.md)。优先采用[TTFT前端交接](TTFT_FRONTEND_HANDOFF.md)及契约2.0.0；前端接入支持/后端维护，性能校准待完成，不部署打包。
