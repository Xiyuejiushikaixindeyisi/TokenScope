# 异常分析前端接入方案草案

2026-10-31更新：展示意见已分两轮获用户确认，最新展示规格见[DESIGN](DESIGN.md)，新版analysis-ui02已获生成授权并待视觉评审。下方IP-0.1作为接入准备依据；与最新展示决定不一致处由DESIGN覆盖，正式交互/开发计划仍待后续审批。

2026-10-31，接收准备稿IP-0.1，待用户讨论。不是正式交互定稿或batch实施授权。契约/身份/缺口见[接收记录](BACKEND_ALIGNMENT.md)。本轮不修改源码、不生成新DEMO。

## 范围与复用

延续UI-01深色侧栏、浅灰画布、白卡、蓝/青配色、紧凑范围栏、业务卡片和详情“位置证据—修改建议—收益”结构。正式代码未来仅在apps/viewer内增量实现，沿用React/TypeScript/Vite和普通CSS；不引入UI框架、CDN或第二套数据层。现有domain整数/时间、API错误和缓存模式先按实际代码评估复用，监控S0、SSE、catalog不能直接作为诊断协议。

浏览器直接视觉阅读受阻，以下位置以UI-01设计说明和报告v0.2为依据，尚未逐屏核对；新增区域的尺寸/位置、卡片顺序/密度、窄屏行为均未冻结。不得据此擅自改变获批布局。

## 需求—接口—状态—交互—证据矩阵

| 需求 | 路由/字段 | 状态边界 | 组件/交互草案 | 证据与缺口 |
| --- | --- | --- | --- | --- |
| 人工发起分析 | GET capabilities；POST /diagnostics/tasks，request/options | 显式提交才执行；low_hit双方向顺序，长度/QPS仅Token | 范围栏关联封存来源、手动appid/原因，可选窗口；预算配置入口待定 | 模型资产随源绑定；MA不可作源；无生产预算默认 |
| 已知任务恢复 | GET /tasks/{id}，receipt | 七状态，queued/running跟踪，终态停止 | 已知task_id入口，任务状态独立于建议；可选紧凑操作抽屉待讨论 | 无目录/latest/时间/进度；跨浏览器恢复未交付 |
| 只读报告 | /report，scope/stages/runtime_options/reason_codes | report_ref可用才读；stages可空，无evaluation合法 | 固定报告上下文、历史报告保留；范围/版本辅助信息折叠 | 新失败不覆盖旧成果，读取失败不是暂无建议 |
| 低命中优化卡片 | items/optimization，evaluation、experiment | full/direct_full完整且严格>1pp | 原卡片结构；pilot与full明确范围，direct_full标明绕过pilot | 不从finding数量造影响请求数/概率置信度 |
| 低命中差异事实 | items/finding，comparisons/{finding_id} | L4/L5独立于收益门槛 | 详情保留两份全文和两端路径，LCP单独解释 | 无关联不能判断历史污染/Loop；工具位置可漂移 |
| Token事实/建议 | items/fragment、fragment_index | RuleResult/condition独立；无Finding仍可有事实 | 沿用Token卡片与证据结构，区分内容事实/策略超限/待补证据 | participation未知、无policy不判异常；T2/T4共享unit |
| Token原文多位置 | requests/{fragment_id}，locations/units/observations/index | 存储完整与采集截断分开 | 一份全文、位置列表、外/内层路径和parser；安全文本渲染 | 无offset不伪造精确文本高亮；>64KiB全文不能省略 |
| 候选评估 | POST token-evaluations | 返回新task；参数/业务依据不足不提交假值 | 根据七handler显示受限参数表单，审阅提交意图 | 不提供任意JSON路径执行器；不在线修改生产请求 |
| T3业务授权 | POST token-authorizations | 已存Observation/unit和专用handler | 事实详情独立显式授权操作，填写真实依据/引用协议 | 重复不等于可删；不预勾authorized或伪造业务依据 |
| T4保留策略 | fragment规则/策略、候选参数 | keep_last缺失与0分别表达 | 显示保留单位/容器关系，明确参数才评估 | 后续消息数不是turn/时间，多文本块不是多次调用 |
| 评估与行证据 | items/evaluation、plan、evaluations/{id}/rows | available才读行；其他状态无after | 前后n/j/p/h/c与scope，原任务回链、Plan审阅 | Token/combined零负收益保留，modified子集不加总 |
| 组合评估 | POST combination-evaluations，plan_refs | 2–8同scope非pilot，冲突阻断 | 从已存Plan选择、显式提交，单独结果 | 收益独立回放，不叠加单项；保留各task引用 |
| 取消/重试与错误 | cancel、retry，error.code/message | 取消返回running继续跟踪；重试新task/attempt | 任务区提供显式操作，错误保留原因和旧报告 | 同意图网络重发复用键；新意图/重试新键，不自动扩大预算 |

所有列表按items/offset遍历，恰满页继续，不编造total/has_more。未加载完仅标当前已加载，不做全scope总量/排行结论。列表item.id和单项data形状分别适配，身份含实例、task和scope，评估子任务保留父task_id。

缓存草案：已发布报告按实例/task/scope/契约身份隔离，轻量结果可复用，原文按需读且不默认持久缓存。切换目标取消或隔离旧响应；迟到结果不得替换当前范围。保留旧报告不等于在新范围冒用旧值。容量/持久化迁移/跨刷新恢复与轮询间隔留待HTML获批后的正式交互阶段确定。

## UI-01逐项调整意见（待认可，未改HTML）

| 原DEMO位置 | 建议改动与理由 | 后端依据 | 视觉影响 |
| --- | --- | --- | --- |
| 顶部“最近分析时间” | 无时间时显示未提供，同时可追溯task与scope；不填浏览器读取时间 | receipt无创建/完成时间 | 原紧凑位置替换文案，不扩成面板 |
| 应用/模型范围和报告入口 | 以已知task_id/封存源关联真实范围，不承诺自动最新报告 | 无任务目录/latest API | 保留范围栏；入口具体位置待讨论 |
| 卡片影响量、置信度、覆盖率 | 缺值不补数；覆盖按实际对象/单位，confidence_basis只表达pilot事实；不按旧合成百分比排序 | finding无直接影响量/概率；coverage非进度 | 保留卡片层级，删除无法提供的合成值或明确未提供 |
| 建议列表排序 | 仅对可比已知字段排序，缺值后置；无可比影响量时建议保留后端结果顺序，待用户确认 | 不同范围/单位不可混排，分页未全不可全局排序 | 不增加评分仪表；现有排序控件需最小调整 |
| 低命中卡片和详情 | 优化卡片与差异事实/实验分开展示；pilot、full、direct_full语义明确 | 严格>1pp仅低命中优化 | 复用原卡片/详情，不把未过门槛结果伪装为优化 |
| Token卡片 | 内容库存/策略结果/机会区分；参与unknown、无policy如实表达 | fragment、RuleResult、ContentUnit | 沿用配色布局，仅调整标签/文案和缺值 |
| 证据对照 | L4/L5两份全文；Token一份全文多位置，嵌套路径独立 | comparisons与requests/index | 复用详情证据区；全文折叠/滚动，不能缩成只有预览 |
| 修改建议区 | 从只读建议扩展到可选显式评估/授权入口，真实参数与依据必填 | 七handler及T3授权接口 | 表单位置与展开方式需视觉评审，不自动执行 |
| 收益区 | Token零/负值保留，P减少但C增加同时显示；blocked显示无完整评估 | evaluation与精确派生字段 | 沿用前后对照，避免单一绿色“成功”误导 |
| 任务反馈 | 在业务排序之外提供紧凑反馈；Token等待不清空旧报告 | 三层状态、report_ref | 抽屉/提示条为候选，未经认可不加大面板 |
| 调用/Loop证据 | 只展示实际请求位置与事实，不保留无证据的完整调用链承诺 | T3单请求重复，不证明执行次数 | 沿用可用结构，移除不受支持的合成表达 |

无须改变：整体主题、侧栏/顶栏、appid×模型服务业务视角、低命中/Token双类导航、证据/建议/收益层级和返回范围定位原则。任何实际长文本/极值引起的显著布局变化需另行说明并认可。

## 后续验证与讨论顺序

接收材料已足以讨论，但以下决策未定：已知task入口/跨浏览器恢复；默认排序缺值策略；任务反馈的位置；预算配置责任；候选/授权表单首期范围；报告导出是否首期需要。先讨论DEMO意见，不能将本草案当正式交互已确认。

HTML批准后才细化加载/读取、跟踪间隔、取消恢复、缓存版本、错误与重试、搜索排序、返回定位和导出。随后给出batch开发方案及具体新增组件/类/共享文件窗口，不提前占用app.tsx、全局样式、API/store或锁文件。开发方案获批后逐批CONTEXT/PLAN/ISSUES/TESTS/RESULT闭环。

未来契约fixture至少覆盖：L完整>1pp及恰1pp；Token65536字节参与未知无policy；同请求三位置未授权；T4缺失/0；P10000→8000且C2000→3000；blocked无after；等待仍保留旧报告；stages=[]无evaluation；满页分页、双路径、原文大整数和>64KiB、安全文本、父任务追溯及实例切换。fixture、真实后端、浏览器、容器、现场证据分开记录。

真实联合测试仅在后续授权阶段进行，绑定两线源码/契约/模型资产/实例，验证GET不计算及所有显式操作闭环。功能通过之外，按同视口/选中状态对照最终获批HTML保存截图，真实内容差异另列，最终用户独立视觉验收。完成后才产出INDEPENDENT_REVIEW_PROMPT.md，不能提前代填SHA或测试结论，不自动发送。后续审查方临时镜像/Git授权不扩展为本轮编码或打包授权。
