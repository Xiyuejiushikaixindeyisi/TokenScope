# REPAIR_R1 PLAN

IN_PROGRESS；修复计划与验收门槛见[独立验收修复计划](../../REPAIR_R1.md)。原独立验收NOT_ACCEPTED，不能以开发自验代签。

模块：prefix_findings_v3通用非clock冻结recipe/发现/守卫编译；candidates_v3给普通动态槽、工具空/不交集增加有界通道；clock_discovery_v3保留真实cause代表对/完整原文去重；evaluation/report/worker统一实算；wire_v3联合类型读取；SampleDiagnostics通用改法与完整请求对照。

资源：新增原文保留预算在retention前核，完整原文只保存一次；每规则最多128个独立原因组，达到上限明确CAUSE_EVIDENCE_TRUNCATED/complete=false，未知上下文不强并。此数是证据保留安全界，不是默认样本数/候选数或收益门槛。不改变任务总比较/编码/内存上限。

兼容：原ClockFinding结构保持，PrefixFinding为联合分支；CauseGroup comparison与evidence_requests新增可选字段，旧结果缺完整对照明确提示；旧H0不动。显式full是待裁定未实现项，不在本修复擅自实现。
