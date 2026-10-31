# MV2-F001 TESTS

153项全量单元/组件通过，其中新增9项覆盖60秒、终态、历史保留、晚到响应、错误重试、Schema与身份/本机隔离。typecheck/lint通过。v2-api.spec.ts使用真实本地服务及浏览器加载正式V2客户端，验证用户同键重发、ID查回及MA提交键查回。合成输入位于F006/inputs，独立状态为artifacts/validation/viewer/monitoring-v2/runtime，不接现场。
