# 开发方案设计前接入核对

2026-10-31；最终接收结论：两后端已分别完成 FE-R-L1 / FE-R-T1，四项设计前置已确认，可以进入前端开发方案设计。当前只完成文档、身份和样例核对，不代表正式编码或真实联合验收通过。

## 两线回传及接收证据

- 低命中：[回执](../../prefix-analysis/FRONTEND_READONLY_RECEIPT.md)、[当前身份](../../prefix-analysis/FRONTEND_READONLY_IDENTITY.json)、[关联样例](../../prefix-analysis/FRONTEND_READONLY_EXAMPLES.json)。
- Token：[回执](../../length-analysis/FRONTEND_READONLY_RECEIPT.md)、[当前身份](../../length-analysis/FRONTEND_READONLY_IDENTITY.json)、[关联样例](../../length-analysis/FRONTEND_READONLY_EXAMPLES.json)。
- [分线prompt、实际发送及完成记录](BACKEND_RECEIPT_COORDINATION.md)。两方最终回复均为completed；前端重新核验64项公共/低命中及28项Token文件摘要，全部一致；两份样例JSON可解析。计数含各自清单交集，不称92个独立文件。

| 四项前置 | 已确认结果 | 设计时必须遵守的边界 |
| --- | --- | --- |
| 字段映射与只读能力 | 低命中finding→experiment→evaluation/optimization→plan→comparison；Token fragment/index/requests及已有评估关联均给出。已接收撤回前端评估工作台的定位 | 低命中缺title/description/影响请求数时用规则解释和真实advice，不虚构字段。Token内容清单、重复观察不自动等于异常；无量化收益就不展示收益数值 |
| 当前版本身份 | 两份当前工作树清单及冻结契约核对就绪，前端逐项复核通过 | 当前工作树不是发布commit；旧local-2/TA006身份仅作历史，资产锁摘要不等于运行时资产验证。真实联合前重核身份 |
| 完整消费样例 | 低命中ready关联链、精确1pp、L4/L5、partial/empty/legacy、方向隔离及读失败；Token完整原文/index、T3/T4、缺policy、零/负/阻断结果 | 均为明确标注的构造样例，不是生产任务或真实HTTP验收；Token片段中的scope取父报告/requests，不假造fragment.scope_id。原文整数、空字符串/null保真 |
| 返回监控身份 | base_run_id与user_run_id、appid/model/common_name及实例头已区分；原报告来源和当前监控分开导航 | base缺common_name，用户监控无按服务查询最新run接口，原user索引revision未封存。不能猜服务/未知最新run或拿旧run称当前；无已验证关联则回监控选择入口 |

## 收益展示的实际范围

低命中L1/L2/可转换L3可在后端既有自动流程留下收益，但pilot与full各有严格>1pp门槛；没有full不能显示全范围收益。L4/L5不承诺自动收益。同规则不等于同finding，不能把代表性评估复制到所有卡片。

Token初始分析不自动执行prepare/evaluate，因此初始报告通常没有修改后量化收益；T3重复字节数不能当节省Token数。已有且可准确关联的评估可显示原始结果，包括零收益和负收益；缺失时保留问题/观察与建议，说明暂无量化结果，不给提交评估入口。

两线均缺“发现→全部历史评估”反向目录。已知可信评估task_id可读取并校验父任务/plan/findings；不能扫描后端文件、猜ID或把事件重放当全量历史索引。当前只读范围不要求补此接口；若未来要求每张卡必有收益或自动收齐全部历史评估，应另行提出后端范围变更。

## 已提供的通知、目录和完成时间

[通知交接](../../prefix-analysis/NOTIFICATION_HANDOFF.md)及diagnostics-discovery-1已提供capabilities、catalog、events、terminal。完成通知后对齐目录并读取；打开/重连对齐目录，不轮询任务状态。partial/empty不替换旧默认；整体ready更新任务包含方向，Token-only不覆盖低命中。legacy时间未知且不自动选择默认；首次无默认但有历史时保留历史选择，不猜latest。

默认按发布sequence，目录每页defaults是完整集合，必须读完整快照；事件只触发对齐，不直接改指标。目录快照/event_cursor衔接、分页、实例头隔离和错误恢复须写进工程方案。现有20秒SSE心跳不等于前端轮询；连接上限64/进程，前端应复用连接。

## 用户审批与后续验证

不需要用户现在再提供policy、授权表单、业务参数、服务绑定或重复批准只读原则、UI-03、轻量缓存/历史/返回。已知限制可以按上述缺值展示和返回选择入口处理，不阻碍方案设计。

下一步形成具体前端开发方案及批次/验收安排，提交用户确认后再启动正式代码开发；不把本轮接收完成当编码授权。如果扩大为自动精确定位未知最新监控run、每卡保证量化收益或全历史评估发现，再讨论接口扩展及所需业务信息。

后续联合验证仍需实际实例/版本、可访问服务与测试数据：真实HTTP、fetch SSE与代理缓冲/断线/reset/重复乱序、分页和打开订阅竞态、读取失败保留旧报告、实例切换、原文保真、缓存失效/存储不可用、历史固定选择及返回定位。开发方案确定缓存白名单/容量/回收及深链接回退。UI-03视觉认可有效，浏览器截图欠项仍待补；本轮未运行服务、业务测试或浏览器验收。
