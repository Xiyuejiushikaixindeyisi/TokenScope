# TA005 真实公共服务接入

> 最新：G1–G3已由公共方补齐并经本线真实消费，TA005 closed。2026-10-31联合执行本线unit87+本线integration7+公共跨方向组合1，**95 passed / 53.39s**，ruff/mypy通过。下文早期缺口状态保留为过程记录，由本段覆盖。

G1 HTTP完整读取>64KiB原文、scope/capture、其它appid记录拒绝及GET无计算；G2新增本线纯authorize_candidate，13项成员/版本/参数/源复核测试，两类授权均通过真实HTTP→worker→封存授权→Plan→评估；G3多Token组合通过真实HTTP独立回放，公共test_diagnostic_combinations验证跨方向组合与冲突无after。引用修改实际出现P下降而C增加，负面效果保留。三模型真实编码回归仍通过。字段computed身份可由fragment_index取得，冻结Schema不改。

当前authorizations.py函数签名按公共请求实现，版本token-authorization-1；只有T3 met精确观察成员能构造候选，从已存位置映射普通消息，不接受任意客户端路径。没有来源读写、工具执行或模型调用，worker再次prepare原文复核。共享公共源码只读。下一批TA006资源/恢复/交接。

2026-10-31：H3a/H3b已消费，partial / awaiting_public_gaps，未closed。新增本线真实服务2项（8.58s）与HTTP1项（5.27s）通过；无mock编码/存储替代。公共维护方提供DiagnosticService/RuntimeOptions及diagnostics-http-1，已有正常路径签收，不代签公共整批完成。

服务测试实际执行已存fragment/candidate→显式评估、零/负P效果保存、缺依据无评估、原appid隔离、低命中后Token原raw摘要、T2/T4同unit及只读查询。HTTP测试实际执行实例头校验、QPS手动原因仅Token、排队/完成查询、candidate成员校验、零变化评估仍可读、分页/外部引用拒绝，GET在禁止探测/编码/回放的断言下正常返回。源库摘要未变。

初次服务测试1失败/1通过：服务评估presentation新增四个派生字段，不是冻结EvaluationResult本体。已读取presentation.py并明确核对四字段后消费核心Schema，未放宽extra校验、未改公共代码；复跑2 passed。HTTP另有Starlette/httpx既有弃用提示，不影响1项通过。当前快照见CODE_IDENTITY.json。

仍缺G1 Token完整原文读取、G2 T3显式授权候选业务入口、G3多Token/跨方向组合评估入口；[具体接口需求](H3_CONSUMER_GAPS.md)已列输入、成员校验、原子性及验收依据。不能以当前三项通过覆盖D2-06/D2-08/E07等缺项。

已知待核对：

1. DiagnosticService submit/process_next/receipt/report/items真实版本；PluginSelection冻结，仍消费原scope，低命中终态后启动Token，中断不启动后续。
2. 从已存待参数candidate显式编译/评估；无business_basis/缺参数blocked。T3引用替换与普通消息删除在未确认协议时当前没有自动candidate，需要核对公共业务输入如何形成可审查candidate，不能擅自增加HTTP或伪造可用入口。
3. Token零/负结果、direct_full与display_eligible不混淆；同appid与子窗口、组合冲突、失败无after、源只读。
4. 完整原文/内嵌位置/同请求多位置证据、T2/T4共享单元、跨报告引用拒绝；GET零探测/编码/回放副作用。
5. 公共H2外层数字词法限制已由Token显式阻断；后续公共处理若扩展，需新版本与受影响验证，不能静默绕过。

TA006按依赖尚未进入联合资源/恢复验收。参数错配独立，不打包部署。
