# 给Token监控后端会话的交接prompt

请在TokenScope项目内处理本次交接。你继续维护监控后端、共享接口和最终交付，前端由已登记fork会话维护。请先读AGENTS.md、memory/CURRENT.md及自己的任务入口，再按本prompt读取直接相关文件；不要全量阅读项目或修改前端文件。

## 一、用户已明确的责任和授权边界

1. 最终前后端联合测试、Docker构建、镜像归档和代码交付包，**全部由后端session统一完成**。前端会话提供可复现构建、源码/资源摘要、接口版本、单元/浏览器/E2E/健壮性证据、已知问题和回退信息，并配合修复。
2. 完整服务门槛必须使用真实前端+后端；B005已有后端E2E、合成HTML和前端假服务验证不能替代J01–J06。
3. 开发按batch：本批方案、问题记录、实际测试、门槛与闭环齐备才进入下一批，增量更新记忆；最后统一E2E、健壮性验证及设计逐项核对。
4. 用户已采用前端评审R1、R2的修订建议。前端最终设计已形成待审批稿；**用户审核通过最终前端方案后才开始前端代码开发**。本prompt不代替后端既有实施审批，也不授权现在构建镜像或交付归档；打包仍需有效明确同意。

## 二、直接阅读入口

- docs/tasks/viewer/MONITORING_INTERACTION_V1.md：前端v1.0最终评审稿，重点第5–9节。
- docs/tasks/viewer/batches/README.md：F001–F006计划与边界。
- docs/tasks/viewer/ACCEPTANCE_V1.md：V01–V15及R1/R2联合门槛。
- achieve/2026-10-28/docs/tasks/viewer/reviews/B005_1_REVIEW_2026-10-27.md：原评审和用户采用决定。
- 你维护的docs/tasks/monitoring/batches/B005.1/{CONTEXT,DESIGN,PLAN,TESTS}.md、docs/contracts/MONITORING_VIEW_V1_DRAFT.md。

共享API仍由你维护。请修订B005.1设计、计划、测试和共享契约中的相关规则；如实际实现已变化，先核对当前源码再做增量修订，不覆盖其他会话进展。前端依赖你确认的协议/schema/OpenAPI与完整样例。

## 三、R1：补齐未确认任务的终态恢复

问题：失败事件可能在首次catalog之前产生，catalog返回的cursor已越过它；或离线超过日志保留期收到reset。目录只含已发布完整结果，因此仅靠catalog+SSE无法恢复此前失败任务，提交界面可能永远停在已受理。

采用修订：
- 前端ReceiptStore按service_instance_id保存自身submission_key/run_id及最小规范提交信息，不保存CSV正文。
- 先安装SSE事件处理并确认连接就绪，再对尚未确认终态的回执一次性GET对齐；最多4并发，按key/连接代次去重。
- 首次订阅、重连、reset后的重新订阅、页面恢复及提交收到回执后触发；无周期轮询。
- 前端终态不被迟到queued/running覆盖；不同终态冲突当协议错误处理。旧实例回执不查新实例。
- 回执404并不等于任务失败；可能尚未受理，允许显式用同key重试。已受理key必须无条件查回原任务，不因CSV已移动而失败。
- 后端持久保存GET /analysis-submissions/{key}及run状态；failed/interrupted与run_terminal同事务；completed/no_valid_rows与result_published一致。沿用现有查询能力，不需要定时计算或新任务。

请在A04/A05/A12及J05补充：首次订阅前失败/完成、after跨过终态、过期reset、对齐GET期间终止、事件与GET响应乱序、实例变更、POST丢回执。真实浏览器最终应显示正确终态且没有周期状态/指标轮询。

## 四、R2：浏览器有界导出并保留完整性验收

用户采用方案A：保留NDJSON结束记录/摘要验证及CSV记录数/结构验证，不能退化成“普通下载链接即通过”。

前端设计：
- 支持secure context且提供showSaveFilePicker/createWritable的Edge/Chrome：用户点击选择文件后，ReadableStream分片；Worker增量解析/计数/SHA256；有界背压写入临时文件，校验通过后才close。错误/取消abort，不能显示成功。
- 应用切片64KiB，在途最多4片；单条导出记录解析上限1MiB。它不是CSV摄入限制，超出时明确中止不截断。该限制与后端实际字段体量请共同核对。
- 不支持流式写文件时，只允许总解码字节≤16MiB的完整校验后Blob下载；超限中止并提示缩小范围或换受支持浏览器，不悄悄提供未验证完整下载。上述具体数值属于最终前端稿的待审批参数。
- NDJSON按原始request行UTF8字节（包含约定换行）增量SHA256，不能parse再重序列化；检查metadata身份/预计数、唯一末尾summary/实际数/摘要。空输出也必须结束清单。
- CSV解析引号/转义/字段内换行/UTF8跨chunk，不能按换行计数；检查表头、合法EOF、X-Export-Row-Count。CSV不宣称哈希验证，精确保真用NDJSON。
- 前端不用全量text/blob/arrayBuffer读取大文件；备用小文件路径有硬限额。

后端需要：
1. 在共享契约明确NDJSON换行/摘要覆盖的字节、metadata/request/summary顺序、出错不能补成功summary；CSV计数与头、压缩/Content-Length的含义；保留流式断线资源释放。
2. 提供可独立复核的导出样例、预期摘要和CSV解析记录数，覆盖引号换行/重复hash/Unicode。
3. 向J04/J06加入真实浏览器的提前断流/缺summary/错SHA/错误行数/UTF8切点/取消/慢sink/能力不足/超限验证，不能以后端A13/RSS替代。
4. 以≥256MiB合成流验证浏览器应用缓冲上界与增量内存目标≤64MiB，前端记录队列断言与浏览器实际测量；后端原流式RSS目标独立保留。正常真实服务验证与故障注入代理/夹具证据分开标记。

这不要求后端在GET重跑统计或对全部筛选导出先全量缓存；不能为便利前端而改计量或主动截断原请求。

## 五、更新与反馈内容

请在你的文档中明确统一联合验收/交付负责人，补齐R1/R2实现/测试映射；输出实际修订路径与版本/摘要、共享字段变化、剩余问题和前端可接入条件。不要把本prompt当作新增代码或打包已获批准的证据。

F001需要稳定的修订协议和完整样例；F002–F005可以在明确标记的契约假服务上做前端层验证，但完整V1保持未完成，直到你统一执行的真实J01–J06和R1/R2门槛通过。发生接口不兼容或必须降低标准的问题交用户裁决。

不要修改apps/viewer、前端设计或HTML，也不因收到本prompt自动创建新会话/自动化。本prompt由用户粘贴用于交接；它不是要求跨会话自动回信的授权。
