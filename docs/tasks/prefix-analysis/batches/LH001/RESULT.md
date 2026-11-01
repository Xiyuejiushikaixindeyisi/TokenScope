# LH001执行记录

2026-10-31，closed。新增analysis_common/source.py与encoding.py：只读scope解析、完整原文与证据/IDs、有效集合摘要、user_v2绑定及原配置编码复核。完整封存校验只在阶段入口执行，逐请求不反复校验全文件；请求和切片各自核对摘要。

验证：tests/integration/analysis/test_source.py，4 passed（18.42s），覆盖GLM/Qwen/DeepSeek真实项目资产和原profile、大于64KiB正文、两个appid隔离、重复hash/同时间稳定顺序、子窗口和空范围、源库前后摘要不变、用户绑定/revision冲突与封存变化。此前公共mypy/ruff通过；本批修复后随后续公共检查继续回归。

发现并修复：初始将control summary与seal summary整体相等比较导致4项失败。现有pipeline明确在封存后补写elapsed_seconds/elapsed_scope/timings_seconds，改为仅排除这三项后比较，其余字段必须一致；复测4项全过。未修改监控实现或测试预期。

H1实际能力为SourceResolver.resolve_scope→ResolvedSource.iter_requests/read_request/read_ids及EncodingContext.verify_baseline/encode；H0 Schema未改变。源模型算法身份不相容/原资产缺失阻断编码，不猜新配置。MA运行不在base control命名空间，非base/user_v2来源不能提交。

后续LH002复用此桥接，H1供Token独立输入接入。未增加HTTP/worker装配，未打包部署。回退移除尚未装配的新增桥接，不影响已发布源运行。
