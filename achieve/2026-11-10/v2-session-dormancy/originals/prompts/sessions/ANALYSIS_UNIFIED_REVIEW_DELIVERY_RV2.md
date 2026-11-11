# 异常分析RV2统一审查与交付打包prompt

2026-11-01最新执行授权：用户已明确认可RV2 L4/L5展示，并要求总负责主动发送本prompt；先统一审查、归口修复、独立复验，通过后打包交付，回传文件/版本/校验摘要。详见[实际执行记录](../../achieve/2026-11-02/v2-approved-delivery/docs/tasks/analysis/UNIFIED_REVIEW_DELIVERY_EXECUTION_20261101.md)。本条覆盖下方“待用户转交/尚未发送/视觉待确认”的准备阶段说明；认可范围以L4/L5原话为准，不代签现场或生产策略。

目标session：镜像打包与审查 `01a1800e-80b4-7400-a78b-a84f5b6e888d`。总负责已依用户明确要求实际发送完整文本，并收到该会话接收与启动回执。

请承接异常分析RV2统一候选，完成统一审查、归口问题闭环，以及用户实际授权范围内的完整服务交付打包。你已完成两后端独立复审，不需要假装重新启动已有审查或把原报告当新执行；重点补当前前端聚合变更、组合身份与完整服务交付一致性。

## 授权与分工

用户已指定异常分析功能总负责为`01a19111-344a-75c1-84e0-14db8be08f4f`，负责前端debug/修复、主动协调后端、联合验证、版本归档记忆及GitHub push，本次已发送这份prompt。你负责统一审查及授权后的镜像、代码包、执行prompt和版本校验材料；业务问题回原维护方，不接管其源码，不改冻结契约换测试通过。

本轮用户已明确要求总负责实际发送、先统一审查、修复复验通过后打包交付，授权原话记录在执行入口，不重复索要同一许可。用户已认可本版L4/L5展示；认可对象和工程检查分别记录，不代签现场或生产策略。任何远端操作/华为部署不在本prompt本机打包范围。

## 首读与版本

依次读AGENTS.md、memory/CURRENT.md、memory/SESSIONS.md、docs/tasks/delivery/ENTRY.md，然后：

1. `docs/tasks/analysis/COORDINATION_RV2.md`：本轮角色和最新产品决定。
2. `docs/tasks/analysis/JOINT_VALIDATION_RV2_20261101.md`：实际结果、边界与验收入口。
3. `docs/tasks/analysis/VERSION_RV2_20261101.json`：候选analysis-rv2-20261101的逐文件摘要。若已有`GIT_HANDOFF_RV2_20261101.md`，以其源码commit和实际远端核对记录定位，先核对当前工作树是否漂移，不拿HEAD代替被测源码。
4. `docs/tasks/prefix-analysis/INDEPENDENT_REVIEW_RESULT_20261101.md`、`RV2_L_HANDOFF_20261101.md`及`RV2_L_COMMIT_MANIFEST_20261101.json`：arpc-local-4，PCR-01/02已修复并独立复验关闭。
5. `docs/tasks/length-analysis/INDEPENDENT_REVIEW_RESULT_20261101.md`、`RV2_TOKEN_HANDOFF_20261101.md`及`RV2_TOKEN_SUBMISSION_MANIFEST_20261101.json`：token-review-20261101-1/arta-local-1/token-content-2，独立复审通过且无阻断修复项。
6. `docs/tasks/viewer/analysis/ENTRY.md`、`INDEPENDENT_REVIEW_20261101.md`及RV2源码/测试；此前6项独立发现已关闭，本轮L4/L5聚合是之后的新产品修正，需按当前版本审查。
7. `docs/tasks/delivery/MONITORING_V2_STATUS.md`、`docs/operations/GIT_WORKFLOW.md`、`deploy/monitoring/README.md`、`scripts/release/README.md`：监控V2已通过并已提交，本次完整服务不能漏掉原监控功能。旧V1交付身份保持，不覆盖旧发布。

前端当前viewer-analysis-ui04-local-3。批准UI-04 HTML路径`docs/tasks/viewer/analysis/prototypes/analysis-ui04/tokenscope-analysis-ui04.html`，SHA256 `779e6665985fe02e6df9e7d0483ef8111a16a49c2b61fdb27aacbef58d624f5f`；HTML中的旧T1卡以最新范围撤回，L4/L5以本轮各一张卡覆盖旧逐组实现，不生成新DEMO或恢复评估表单。

## 统一审查重点

- 同一实例/同appid两页签，不使用两套state冒充联调。当前4191→8016，4193仅跳转；运行命令与PID见本地`artifacts/validation/viewer/analysis/rv2-20261101/service.json`。先核对所有者，不终止其他session服务。
- L4/L5分别至多一张卡，有发现即展示；遍历元数据分页后按完整RequestKey去重，不相加组数/组人数/收益。每类详情总≤3个代表例子，跨组按双方定位指纹去重，A/B交换视同一对；旧group深链转所属探测器，历史刷新/返回保持。
- L1–L3只显示已满足原门槛的优化建议，突出影响请求、命中率提升、局部证据和修改建议；不展示Token收益。L4不认定同会话历史被改写，L5不给伪造收益。
- Token仅T2–T4自动建议与量化收益，旧T1只读兼容。四类实际建议T2/T3引用/T3普通副本删除/T4；缺依据不补收益，0与缺失区分，P降C升保留；不把构造策略装成生产默认配置。
- 完成通知后拉取、打开/重连对齐目录、不轮询任务状态；partial不覆盖默认ready，固定历史不随通知跳走；迟到请求不能污染或导航旧应用，缓存受限仍可用，页面访问零诊断写请求。
- 局部原文/大整数/转义/零宽删除/截断限制保持；无完整请求或技术身份JSON堆叠，不在浏览器持久存储原文。旧监控/MA路由兼容、窄屏无横向溢出。
- 身份漂移按源码影响补测；不要把独立回归文件再次执行称为又一次独立审查，不累计重复用例。测试、视觉、容器、现场各自留证。

## 已有证据及复现

前端195项单元/组件及typecheck/lint通过，18项浏览器通过（11受控API、7真实服务）；后端加载当前版本后7真实服务用例另行通过，不重复计数。公共RV2 215 GET及84原文件不变；后端独立测试分别见各报告，不能合并成“全项目一次通过”。

WSL项目`apps/viewer`下运行`npm run typecheck`、`npm run lint`、`npm test`。浏览器使用Windows Chrome与当前服务，在该目录PowerShell执行：

```powershell
$env:TOKENSCOPE_BROWSER_EXECUTABLE='C:/Program Files/Google/Chrome/Application/chrome.exe'
$env:TOKENSCOPE_EXTERNAL_PREVIEW='1'
$env:TOKENSCOPE_ANALYSIS_REAL='1'
$env:TOKENSCOPE_TEST_BASE_URL='http://localhost:4191'
node node_modules/@playwright/test/cli.js test tests/browser/analysis.spec.ts tests/browser/analysis-boundaries.spec.ts tests/browser/analysis-review-regressions.spec.ts --workers=1 --output ../../artifacts/reviews/analysis-rv2-unified/browser-results
```

测试输出目录必须独立，避免并发trace文件竞争。后端验证可运行`scripts/validation/validate_rv2_low_hit.py --output <全新目录>`（使用`.venv/bin/python`）；它复制RV1后封禁计算入口，不能重新生成或修改原state。Token全套命令及独立探针均在实际独立报告中，按影响选择补测，不反复无差别重跑。

截图/日志：`artifacts/validation/viewer/analysis/rv2-20261101/`。后台同实例的旧ready/default_ready/partial身份见RV1交接，不更换task_id解释旧测试。前端模型/真实策略/15万请求容量没有生产结论；Token`tool_calls:null`当前保守partial且拒绝自动修改，保留明确限制。

## 授权后的交付步骤与输出

1. 明确审查候选、发现/级别/归口及实际复验，给出统一通过或阻断报告。普通前端问题发总负责，低命中/公共发`01a18be2-7112-7aa2-919b-5137d1f1b1ad`，Token发`01a18fcd-0464-7cf1-b435-4f394bd33e66`。需要改变范围或冻结接口再说明影响，不静默修改。
2. 在已有明确本轮打包授权下，按现有发布工具构建新版本完整服务镜像和代码包，包含已闭环监控V2/MA及异常分析前后端；记录实际工具配置和源码commit。不以开发机Vite预览当容器交付验证。
3. 容器内验证服务/静态路由、只读报告、目录/通知、监控兼容、重启/挂载/失败恢复；构造样例可用于隔离验收，不能把本机state、生产原始CSV、私有配置或测试授权默认塞入交付包。
4. 交付代码包、镜像包、版本manifest和华为现场执行prompt，逐项SHA256；记录依赖、配置、三模型revision/Tokenizer/Template资产身份。目标是已有报告的华为V100，不按“华为”猜为Ascend；其他机器要独立核实。模型资产、离线依赖和配置来源按实际清单交代，不虚构已随包。
5. 执行prompt覆盖校验、导入/启动、端口/挂载、已支持模型与配置模式、只读验收、日志收集、回退和生产策略待配事项。不要代替业务批准删除/引用策略，不执行远端部署。
6. 新包体留`artifacts/releases/<实际新版本>/`及用户指定交付目录；backup仅本地，GitHub仅代码/文档，不上传包体或原始数据，不push --all/--mirror。若修复需要Git收口，与总负责协调候选身份，保留本轮实际SHA。

最终回传：统一审查报告、问题关闭清单、实际源码/前后端/契约身份、独立层级验证结果、包/镜像/配置摘要、现场prompt路径、回退办法及明确未决项。不得用“容器启动成功”替代用户视觉或华为现场验收。
