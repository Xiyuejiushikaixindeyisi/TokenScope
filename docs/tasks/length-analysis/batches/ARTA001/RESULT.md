# ARTA001 — T2/T4 自动提案适配器

2026-10-31。本线私有适配器实现与消费者验证完成，进入 ARTA002。公共 HTTP/整任务自动回放未在本批验收，影响 N/M 的真实联合验证按 ARTA003 执行。

- 公共消费：analysis-recommendations-1 / token-auto-proposals-1，核对 ARPC000_CONSUMER_HANDOFF 和 manifest 三项 SHA256 全部一致。internal 3f27ebfa3bba09da35b086a18b20ee2f7c9a9ebd9f8675473843fc529d28153f；wire e618784f4a6f846aeb28663dc145d85dee1ffc6a8a58badacf218c95ce29810f。
- 新增 auto_config、auto_targets、auto_proposals：严格版本/未知字段/类型/工具身份/appid/内嵌位置；T2 字段投影、前后 K 行/条目；T4 同身份、源顺序保留最后 K 个结果，替换旧完整内容。K=0 明确表示不保留。
- omission_permitted 必须 JSON boolean true，不能用检测阈值当授权。verified business_policy 且 scope_selector 与 selector 语义一致才可执行；无依据只生成 advice_only，无执行目标。hypothesis 未启用。
- prepare_proposal 重新抽取原请求、重新生成全部位置与参数并比较，拒绝目标/参数/依据篡改。复用既有 handler，不另做编码、回放或数据库写入。
- 新 CurrentTokenContentPlugin 身份 token-content-2 仅 T2–T4；原 TokenContentPlugin/token-content-1 及 T1 历史逻辑保持。公共注册切换由公共维护方完成；此文件不声称运行中的默认注册已切换。

验证：Token 全部 unit + integration **151 passed / 40.01s**；16 个私有源码 mypy 通过，ruff 通过。包含新增 39 项及原 112 项。一个既有 Starlette/httpx 弃用 warning。首次测试修复：构造 fixture 缺 budget、现代 tool 错用 name 识别以及 TypeAdapter 类型标注；当前均通过。

所有新增策略为 synthetic fixture，并明确写入 basis.authority/limitations，不代表生产授权或真实业务收益。前端保持只读；未打包部署、未修改公共源码。
