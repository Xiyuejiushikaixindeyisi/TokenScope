# B005.1 / B006评审响应 v0.2

2026-10-27。依据用户提供的[交接prompt](../../../../../prompts/sessions/MONITORING_BACKEND_FRONTEND_V1_HANDOFF.md)及前端[R1/R2评审](../../../viewer/reviews/B005_1_REVIEW_2026-10-27.md)。**修订方向已采用；文档已修改，代码与验收尚未执行。** 源码仍0.1.0.dev5/schema2；拟view1/schema3/dev6不改实际版本。

| 评审项 | 修订位置 | 实施/验收映射 |
| --- | --- | --- |
| R1首次cursor/过期日志无法恢复回执 | DESIGN §6/6.1，契约 §3.1/7；持久当前回执、实例隔离、先订阅再一次GET、终态单向合并 | S0/S2/S4；A04/A05/A12、R1-01–08、J05；前端F004/V08 |
| R2保留完整性及有界浏览器方案A | DESIGN §7.1，契约 §8；LF原字节SHA/summary、CSV解析计数、响应头/压缩、错误不得伪造成功、独立完整fixture | S0/S4/S5；A13/A18、R2-01–10、J04/J06；前端F005/V09–10 |
| 最终联合/打包责任 | DESIGN §9、PLAN J1、TESTS统一负责人；B006六文档 | Session 1统一J01–J06/R1/R2、后续获批构建/镜像归档/代码包；前端F006提供交接 |
| 不扩大本轮授权 | CONTEXT/RESULT/ENTRY/记忆 | 本轮修订文档并完成S0契约生成/校验工具；未改业务代码、未构建、未发送跨会话消息 |

## 共享字段与行为变化

- 回执补齐instance/schema/key/model/四种终态及started_at/finished_at/error_code，短读事务联结当前run、no-store；不从入队快照返回陈旧状态，不因CSV移动拒绝。
- 新UI提交/回执/显式run读取带X-TokenScope-Instance-Id；跨实例409无写入。旧调用省略头兼容。目录cursor不能代替提交恢复，SSE onopen后对齐；无周期轮询。
- 导出固定X-Export-Schema-Version/Row-Count/Instance/Run头；NDJSON UTF8无BOM、LF及摘要覆盖明确，空集也metadata+summary；CSV固定列/CRLF/逻辑记录数和公式前缀规则。
- 导出参数含offset/limit明确422，拒绝把当前页称全量。Content-Length不是预先缓冲理由；压缩长度不作为解码大小保证。中途错误不能补成功summary。
- 不改J/P/H/C/O、DES、阈值算法、摄入长度和旧API数值类型；view_schema尚未发布仍拟1，文档修订号升0.2。

## 样例与前端接入条件

[完整回执/导出协议夹具](../../../../contracts/examples/monitoring-view-v0.2/README.md)附独立摘要/CSV解析记录数，覆盖Unicode、引号换行、重复hash、空集及R1时序；人工合成，非服务输出。[review-check](../../../../../artifacts/reviews/monitoring-b005-1-v0.2/review-check.json)仅证明文档/夹具内部一致，不证明API或浏览器。

用户最新要求先完成S0，现已交付[S0固定1.0.0](S0_CONTRACT.md)完整字段/设计OpenAPI/成功错误样例与摘要，可供F001契约开发；实际消费方接收确认仍由前端登记。现有v0.1 JSON只保留历史片段。R1/R2夹具现在可用于协议核对；F002–F005经契约确认后可做明确标记的前端假服务验证。真实联调须实际后端版本和前端F006交接；最终由后端统一通过J/R后才release_ready。

## 剩余问题

1. 后续核对前端APPROVAL确认最终v1.0（含64KiB×4、1MiB、16MiB）已获批；F001因完整契约依赖暂停，本轮不替其恢复。后端本批实施/最终打包授权仍独立。
2. hash_id/appid当前没有1MiB限制；长ID可能使导出记录超过UI限额，S0已复核NDJSON正常及1MiB字节边界；F001/F005仍需测量实际浏览器能力；UI明确失败，不修改摄入/计量或静默截断。
3. 后端增补、真实浏览器文件写入、≥256MiB资源测试及R1竞态全部待实现/执行；目标入口secure context、浏览器能力和现场兼容待验证。
4. 原生产DeepSeek默认思考、GLM CP映射、部署资产等价未决保持；B006无新打包授权，仍pending。

## 版本与摘要

输入身份见[REVIEW_INPUT_MANIFEST_v0.2.json](REVIEW_INPUT_MANIFEST_v0.2.json)；本次文档/fixture摘要见[revision-manifest](../../../../../artifacts/reviews/monitoring-b005-1-v0.2/revision-manifest.json)。v0.1文档原字节归档在[历史快照](../../../../archive/monitoring/B005.1-v0.1-2026-10-27/README.md)，旧B00619文件归档保持不变；批准DESIGN v1.0和计量契约摘要保持不变。
