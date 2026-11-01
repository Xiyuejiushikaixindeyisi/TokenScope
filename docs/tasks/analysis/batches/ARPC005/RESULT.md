# ARPC005 只读接口与应用装配

2026-10-31。公共独立router已接入create_app，bootstrap静态注册CurrentTokenContentPlugin/token-content-2及TokenProposalAdapter；旧HTTP/H0/discovery文件和枚举不改。未修改正式前端。

新增GET：/diagnostics/recommendations/capabilities；/diagnostics/tasks/{task_id}/recommendation-summary、recommendations、recommendations/{id}、recommendations/{id}/examples、difference-groups、difference-groups/{id}/examples。除capabilities外需要既有实例header。稳定封存task分页offset/limit，默认50最大100，next_offset=null结束。

新业务视图与内部模型分开：recipe选择器/参数生成规则及basis作用域的完整JSON不公开，仅公开摘要；metrics精确派生P/C delta/ratio与命中率百分点。公共视图Schema在contracts/analysis-recommendations-1/public-views.json，独立http-manifest；不会让前端使用内部Recipe模型误读脱敏字段。

实际只读集成与旧HTTP回归3 passed / 14.30s；覆盖分页不重漏、例子<=3、GET禁止propose/prepare/submit/worker、无POST、实例409、非法页422、旧报告not_computed/详情404、未封存409。扩大公共/低命中及自动链边界后98 passed / 22.18s。未知/非法新契约明确409，系统存储异常沿应用503处理。完整联合与监控兼容见ARPC006后续记录。

后台业务配置通过TOKENSCOPE_RECOMMENDATION_BUNDLE指定项目内JSON路径；未配置使用显式空bundle，配置数0并记录NO_CONFIGURED_RECIPES，不能称业务策略齐备。缺失/非法指定路径拒绝提交；配置读取上限8MiB。重试/幂等使用原快照，前端无配置表单。

app装配只新增router注册，CLI复用build_diagnostics，无需另一套服务或演示后端。共享app修改窗口已完成，后续仅限验证发现的问题修复；最终冻结与实际报告身份待ARPC006收口。


## 最终联合闭环

2026-10-31：本批实现已纳入ARPC006当前源码联合验证与实际HTTP交接，详见[最终验收](../ARPC006/RESULT.md)。上文阶段性待项由最终记录覆盖，不将早期测试当新功能签收。
