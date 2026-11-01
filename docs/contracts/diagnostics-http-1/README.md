# diagnostics-http-1

实际HTTP边界：src/tokenscope/api/diagnostics.py。依赖冻结analysis-common-1.0，不修改其Schema。wire.json给出提交/重试/显式Token修改/低命中直接全范围/已存Plan组合/T3授权的严格请求Schema。整数元数据为十进制字符串；原始JSON与parameters_json是字符串，其内部业务数字不转换。

通过scripts/export_diagnostics_schema.py再生成本层Schema及manifest；冻结后若改变字段语义应新版本。source中的模型/profile/配置摘要仍沿监控身份，不用本层版本替代。任务报告版本diagnostics-report-1、资源选项diagnostics-runtime-1。

GET /diagnostics/capabilities给当前service_instance_id和请求Schema；其它入口要求x-tokenscope-service-instance。具体状态、端点、数据引用与失败规则见[实际接口](../../tasks/prefix-analysis/IMPLEMENTED_API.md)。
