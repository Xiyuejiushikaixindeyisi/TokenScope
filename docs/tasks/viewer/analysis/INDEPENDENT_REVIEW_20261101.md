# 异常分析前端独立复审与修复复验

2026-11-01。独立复审执行者：子agent `/root/frontend_independent_review`；产品聊天实际ID未知，没有沿用主实现会话ID。依据用户要求独立复审并修复前端BUG。本复审者不修改前端业务源码、后端或共享记忆；修复由主实现者完成，本复审者取证、编写专项浏览器回归并复验。

当前结论：确认6项问题，修复后均已完成独立复验并关闭；统一入口实际连接同一实例，两方向及历史/partial/详情/来源回跳通过。当前复审范围内未发现剩余阻断问题。用户功能/视觉认可及两后端独立复审不由本报告代签。未打包部署。

> 后续协调补记（主前端会话，2026-11-01）：本报告下文“两后端仅交接”是复审执行时点事实。现已收到[公共实际独立复审](../../prefix-analysis/INDEPENDENT_REVIEW_RESULT_20261101.md)：arpc-local-4通过其低命中/公共范围；Token本线已实际发起私有全范围独立复审、尚待结论，见[最新交接](../../length-analysis/INDEPENDENT_REVIEW_HANDOFF.md)。此补记不更改独立审查者原始取证、测试版本或6项关闭结论，也不将旧前端测试记作新版后端重跑。

## 范围与能力事实

已阅读AGENTS/CURRENT/SESSIONS/docs入口及前端当前ENTRY，审阅AnalysisApp、报告模型与渲染、只读API客户端、SSE、缓存、来源回跳、局部证据及相关测试。使用Windows Chrome实际运行当前React页面；受控API仅用于构造慢响应/失败/无某方向目录，不生成分析任务，不改封存报告。

用户所述两后端“独立复审报告”：目前可定位的[公共交接](../../prefix-analysis/INDEPENDENT_REVIEW_HANDOFF.md)和[Token交接](../../length-analysis/INDEPENDENT_REVIEW_HANDOFF.md)均明确为复审输入、不是结论。主会话已向两归口session核对，两方确认尚未实际启动独立复审；[统一验收交接](../../prefix-analysis/UNIFIED_ACCEPTANCE_RV1_HANDOFF.md)也明确这一事实。因此只参考其契约/候选身份/历史测试，不称两后端独立复审通过。

## 初审发现

| ID | 级别 | 实际问题与复现 | 位置与建议 |
| --- | --- | --- | --- |
| RV-F1 | P1 | 4191与4193分别连接不同服务实例和数据集，同一页面的两方向不能完成连贯验收。4191的`a`实际上包含两方向报告，但Token无配置建议；4193的`synthetic-orders`目录只有Token方向，切低命中显示暂无报告。此前分别跑通过的页面测试没有验证同一入口、同一appid切换。 | 初审`tests/browser/analysis.spec.ts:5`、`:6`使用两个base URL，`ACCEPTANCE_UI04.md`给出两个状态。应由后端正常生成同一实例/绑定双方向报告，前端只连接该实例，用同入口跨方向验收；不能拼接数据库或伪装实例。 |
| RV-F2 | P2 | 报告读取中切到没有当前方向报告的目录，旧请求取消后持续显示“正在读取报告…”；503后切方向也保留旧错误，声称保留原报告但当前范围没有报告。 | 初审`AnalysisApp.tsx:40`无target分支只清loaded，旧请求finally因abort跳过。无目标时清loading/error；新目标状态独立。 |
| RV-F3 | P2 | 在`a`加载更多后切到`representation`，旧分页延迟503仍把错误写入新应用。 | 初审`AnalysisApp.tsx:56`的more无取消控制，catch/finally直接写全局状态。分页使用AbortController，切目标/实例/卸载时取消，错误和busy独立。 |
| RV-F4 | P2 | 点击`a`的原报告监控来源，在监控目录返回前切应用，迟到结果仍把页面带到旧`a`的监控概览。实际最终URL含旧appid/run。 | 初审`SourceLink.tsx:11`至`:31`缺取消及导航前检查。entry变化/卸载中止，并在每次异步边界和导航前核对有效性。 |
| RV-F5 | P2 | 浏览器拒绝localStorage getter时，卡片可显示但通知连接不断重连；1.8秒内看到3次capabilities，没有成功发起SSE订阅。 | 初审`analysis-cache.ts:38`的默认参数`storage=localStorage`在try外求值。把读取storage放到try内，存储禁用仅降级内存，不阻断目录通知。 |
| RV-F6 | P2 | 同实例实际验收中，显式partial后查看最新曾超过15秒未切换完成；主实现者的多轮方向切换后历史选择也出现5秒超时。首屏即为全部屏外卡片读取证据，主实现者通过请求记录确认这些请求占用队列、阻碍报告切换。 | 修复前`Evidence.tsx`每个EvidencePreview挂载即调用useExamples。现在以IntersectionObserver仅近可见区域读取，详情仍立即读取；不隐藏差异或删除例子。独立最终探针历史428ms、查看最新242ms通过，未放宽超时。 |

初审源码行号对应修复前版本；当前行号已变化。证据原位保留：`artifacts/validation/viewer/analysis/review-20261101/initial-repro-v2.json`、`race-repro.json`及`review-stuck-loading.png`。`initial-repro.json`为早期探针超时记录：起初误以为4191切Token也会“无报告”，随后读取真实目录并修正探针，最终结论以v2记录为准。

## 已完成的代码修复独立复验

专项测试：[analysis-review-regressions.spec.ts](../../../../apps/viewer/tests/browser/analysis-review-regressions.spec.ts)，由独立复审者维护。当前7/7通过，13.9秒；覆盖：

1. 读取取消且无新目标时，loading停止、无串入旧卡片。
2. 原报告读取失败后切方向，旧错误清除。
3. 旧分页失败不污染新应用报告。
4. 旧监控来源查询不能在切应用后导航。
5. 禁用storage仍发起SSE；订阅发起后的capabilities次数保持稳定。
6. 仅带direction进入时选有该方向的绑定；旧binding给清楚提示和返回目录操作。
7. 历史报告本身包含两方向时，切方向保留同task和分析时间。

第6/7项为扩大检查中的正常行为复验；没有保存修复前失败证据，不冒称初审已实复现。首轮6/7的唯一失败是测试把React StrictMode初始双connect当作重连；已改为在SSE发起后比较计数，最终7/7通过。这个修订没有掩盖RV-F5：原缺陷根本无法发起SSE，仍会被测试检出。

执行环境：现有4191 Vite页面、Windows Chrome、Playwright；诊断API全部拦截，使用AR-L4真实响应结构与受控目录/故障。不是两后端业务回归或真实通知发布验收。命令在`apps/viewer`：

```powershell
$env:TOKENSCOPE_BROWSER_EXECUTABLE='C:/Program Files/Google/Chrome/Application/chrome.exe'
$env:TOKENSCOPE_EXTERNAL_PREVIEW='1'
$env:TOKENSCOPE_TEST_BASE_URL='http://localhost:4191'
node node_modules/@playwright/test/cli.js test tests/browser/analysis-review-regressions.spec.ts --workers=1 --reporter=line
```

已检查当前修复实现：`AnalysisApp.tsx:46`按目标身份清理请求及状态，`:63`分页取消；`SourceLink.tsx:11`控制请求生命周期和导航；`analysis-cache.ts:38`在try内访问storage。验证对象SHA256、执行计数及证据范围在`artifacts/validation/viewer/analysis/review-20261101/independent-result.json`。主实现者的全量类型/静态/单元及原浏览器检查另列，不累加为本复审者执行数。

## 统一入口实际复验与关闭记录

公共后端已交付新同实例数据`unified-acceptance-rv1-20261101-1`，instance `0cf8b18b-224f-44f3-959d-bbfc1cfe010e`，同一`synthetic-orders`包含两份ready及后续partial，见[RV1交接](../../prefix-analysis/UNIFIED_ACCEPTANCE_RV1_HANDOFF.md)。此交接基于正常服务生成，不改原状态；仍为构造输入/业务策略的真实离线回放。

独立探针已核验4191实际连接该实例，完成7个链路检查：同一绑定ready默认、低命中↔Token四项建议、历史task/时间固定、详情刷新返回及最多3例、partial显式展示与查看最新回到ready、4193旧链接跳转4191 Token页、监控来源回到原base_run。诊断请求均为GET，页面脚本错误0。结果为`artifacts/validation/viewer/analysis/review-20261101/unified-independent-final.json`，截图`unified-low.png`/`unified-token.png`；两个方向使用同一origin和实例。RV-F1关闭。

第一次实际探针的partial→查看最新超时保存在`unified-independent.json`，没有抹掉失败或仅加长超时。主实现者调整屏外证据读取后，第二轮及最终独立复验都通过；最终历史切换428ms、查看最新242ms是本机观察值，不宣称生产SLA。RV-F6关闭。

RV-F2–F5由7项专项浏览器回归关闭。EvidencePreview调整后的专项重跑曾遇到同时执行Playwright共享`test-results`导致trace文件ENOENT（`reviewer-regressions-final.log`），这是输出目录竞争；后续使用独立`--output ../../artifacts/validation/viewer/analysis/review-20261101/reviewer-test-results`保存，不能把该基础设施失败当业务通过。最终隔离重跑7/7通过，17.7秒，退出0；结果保存在`reviewer-regressions-isolated.log`与身份清单。不与先前13.9秒的同7项重复累加。

新统一报告中的29个L4/L5差异组由后端正常分组产生，和旧AF006把29个成对finding当优化方案的缺陷不是同一对象；本次没有在前端合并或删去它们。页面按已批边界保留差异区及每组最多3例。生产策略/生产收益不在本次前端复审结论内。
