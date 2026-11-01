# ARTA000 结果：公共推荐协议文档对齐完成

> 2026-10-31最新批准范围：[TA-S1](SCOPE_REVISION_T234.md)移除Token T1，保留T2–T4编号；工具定义归低命中现有一致性/漂移职责，不增长度精简。当前新设计/计划/推荐/视觉验收仅T2–T4；旧源码及TA000–006历史仍含T1，不冒称已删除。当前实施计划见[BATCH_PLAN_ARTA](BATCH_PLAN_ARTA.md)，三卡样例见[AR-T3](FRONTEND_REWORK_EXAMPLES_ART3.json)。本轮仅文档同步，暂不编码打包部署。

2026-10-31，状态 **closed（文档阶段）**。用户要求先对齐、列清最少业务策略，暂不编码打包部署；本批未启动ARTA001或其他实施批次。

## 完成依据

- Token侧[对齐稿及第8节精确接纳](ARTA000_ALIGNMENT.md)。
- 公共侧[ARTA000_PUBLIC_ACK](../prefix-analysis/ARTA000_PUBLIC_ACK.md)：逐项确认版本/适配器、支持引用、分组/执行复用、N/M及null、依据/发布状态、预算与分页。公共方结论为文档语义已签收、无待业务选择的工程分歧。
- 权威工程设计[AR-C1](../analysis/RECOMMENDATION_CONTRACT_ALIGNMENT_AR1.md)，后续公共实施[ARPC000–006](../analysis/RECOMMENDATION_IMPLEMENTATION_PLAN_AR1.md)。Token ARTA001–004依赖对应公共批次交付；本批完成不代表它们已获本轮编码授权。

## 已确定

对外统一analysis-recommendations-1；内部token-auto-proposals-1、recommendation-group-1、evidence-locator-1、recommendation-budget-1。旧冻结协议保持。推荐ID由公共层生成，内容ID不含task，读取/缓存绑定实例+task+scope+版本。T3支持Observation，无需假Finding；同次报告保存推荐/准备Plan/执行Plan/Evaluation的准确关联。

M是scope.request_count；N只取完整available评估的raw修改请求子集，modified_before.n=modified_after.n。匹配/观察/操作数不冒充N；noop为0，未完整评估为null。输入Token和计算Token分别展示全scope前后值、带符号差值及精确比例，零/负/P降C升均保留。

缺真实业务依据且资格检查完整可advice_only/ready，但明确无可评估方案；缺模块、坏配置、非法依据、预算停止和应执行步骤失败不能伪ready。准备或评估不完整无after，partial不替换旧默认。所有推荐关联及例子封存验证后再发布通知；前端只GET、无参数/授权/评估表单。

公共适配器输入补齐scope_id/fragment_id/capabilities；basis来源采用authority.source_kind/source_ref/source_digest，不另加平行source字段。具体阶段枚举、reason、分页和预算以公共AR-C1为唯一工程基线。

## 仍需用户提供或确认的最小业务内容

首批按完整后台配置驱动，工程协议无需用户再选。可给一份现有配置/规范入口统一解决以下资料，不必逐条填写前端：

| 规则 | 真实业务收益所需最少资料 | 未提供时 |
| --- | --- | --- |
| T2 | 哪些返回字段允许省略及作用层级；或保留头/尾/具体行条目范围 | 检测limit不能代替修改规则，暂不自动裁剪 |
| T3 | 真实可解析引用协议及载荷映射；或允许删除哪类普通重复消息、保留哪份的约定 | 不虚构引用、不默认删除；明确缺依据 |
| T4 | 保留K、结果容器/part单位与作用范围，以及合法替代文本/已有摘要/引用规则 | 仅K不足，不生成假摘要 |

可选决策只有一项：**没有以上业务配置时，是否本轮启用T2/T4的明确假设方案。首批默认关闭。** 若要求启用，再一次确认有限保留档位/方向及替代文本；样例K=2不自动成为默认。该选择不阻碍已确定的配置驱动设计，也不要求前端用户参与。

可按已有资料先覆盖部分规则，不能要求一次收齐三类才能开展后续获授权的工程验证；使用构造策略可验证接口，但不称真实业务已具备收益。自进化Agent、LLM改写、参数错配及线上Agent修改未扩大范围。

## 验证与未执行

本轮核对公共原文签收、相互入口与本地链接，检查本线文档格式；[验收检查点](ARTA000_ACCEPTANCE.md)规定后续真实测试预期，不是执行结果。未运行pytest/编码器/服务/回放，未修改业务源码、前端或旧冻结Schema，未打包部署或Git收口。

运行时机器Schema、新路由与自动链路仍未实现；后续批次需要独立代码/资源身份、真实回放和前后端联合验证。ARTA000关闭的是**双方文档协议对齐**，不等于自动收益功能或真实业务验收通过。
