> 归档：本文件保存历史过程，不再是执行入口。2026-11-02用户认可V2可交付，UIR-03留V3、不作V2阻断。现场只用真实数据，分两次用户验收，单份Markdown回传。当前见[交付入口](../../../../../../docs/tasks/delivery/ENTRY.md)；[逐字节原始快照](../../../snapshots/docs/tasks/analysis/JOINT_VALIDATION_RV2_20261101.md)。

# 异常分析RV2修复与联合验证报告

2026-11-01；功能总负责session `01a19111-344a-75c1-84e0-14db8be08f4f`。

结论：L4/L5重复卡片已修复，两类各一张卡、每类最多3个代表例子；前端检查及当前后端组合的真实浏览器联调通过。低命中/公共和Token私有两后端均有实际独立复审通过报告。本次用户视觉确认仍待进行；没有构建交付包、镜像或远端部署。

## 可验收入口与变化

**[统一异常分析入口](http://localhost:4191/#/analysis)**。同一应用`synthetic-orders`、同一实例、两个页签；旧4193仅302跳转。

此前把每个后端差异组当作一张业务卡，RV1的20个L4组和9个L5组形成29张重复卡。已改为按探测器汇总：无发现不造卡，有发现各一张，完整遍历已有元数据分页后按完整RequestKey去重计数；不把组数、组人数之和或例子数当影响数，不在列表继续展开所有差异组。

当前样例两类均涉及6条不同请求，而组人数相加分别是42和18，后两值不展示。每类选最多3个有例子的稳定证据组，例子按双方完整定位指纹去重（互换A/B不算新例），总展示≤3个；首例展开，其余折叠。只读取选中的局部证据，保留原引用与定位限制。所有组读取成功前不发布假全量计数；取消或失败沿用既有错误恢复。

新卡身份是前端展示身份`difference-detector:L4/L5`，不冒充后端group_id。旧差异组链接仍解析到所属探测器详情，历史task与方向保持，刷新/返回定位可用。Token四项建议及收益、L1–L3优化建议保持；未增加表单、任务轮询或写接口。

UI-04颜色和布局保持，批准HTML未修改，SHA256 `779e6665985fe02e6df9e7d0483ef8111a16a49c2b61fdb27aacbef58d624f5f`。当前正式前端身份`viewer-analysis-ui04-local-3`；本轮交付候选`analysis-rv2-20261101`。

## 依赖、责任与接口

- 低命中/公共：`arpc-local-4`，[归口回执](../../../../../../docs/tasks/prefix-analysis/RV2_L_HANDOFF_20261101.md)及[独立复审](../../../../../../docs/tasks/prefix-analysis/INDEPENDENT_REVIEW_RESULT_20261101.md)。原PCR-01/02修复已独立关闭，本轮没有新增公共业务代码改动。
- Token：`token-review-20261101-1` / `arta-local-1` / `token-content-2`，[归口回执](../../../../../../docs/tasks/length-analysis/RV2_TOKEN_HANDOFF_20261101.md)及[独立复审](../../../../../../docs/tasks/length-analysis/INDEPENDENT_REVIEW_RESULT_20261101.md)。本轮无阻断缺陷、无私有业务修复。
- API仍为analysis-common-1.0、diagnostics-http-1、diagnostics-discovery-1、analysis-recommendations-1；没有接口或Schema变更。前端复用分页与examples，不实现后端探测或收益计算。
- 当前本机8016已从原进程切换为上述现行源码，新PID与启动命令见`artifacts/validation/viewer/analysis/rv2-20261101/service.json`。4191代理不变。
- RV1源数据和报告仍为原封存：instance `0cf8b18b-224f-44f3-959d-bbfc1cfe010e`，默认ready `4f5a4bd6-c09e-4ac4-a5aa-9f5fdd832633`；旧ready与较新partial均保留。没有重建state、合并SQLite、复用旧ID生成新报告或在GET触发分析。

## 实际检查结果

| 执行方/范围 | 实际结果 | 证据 |
| --- | --- | --- |
| 本会话前端typecheck/lint | 通过 | `rv2-20261101/frontend-final-static.log` |
| 本会话单元/组件 | 22文件195项通过，4.08秒；含跨页汇总、请求去重、交换对照去重、数量不一致拒绝及旧深链 | `rv2-20261101/frontend-final-checks.log` |
| 本会话浏览器主线/边界/旧独立回归 | 18项通过，约1.3分钟；11项受控API、7项真实服务 | `rv2-20261101/browser.log` |
| 当前后端组合加载后的真实浏览器联调 | 上述7项再次通过，47.9秒；不重复累计为25项 | `rv2-20261101/current-backend-browser.log` |
| 低命中归口RV2读取及聚合核验 | 215个GET响应兼容、84原文件未变；3份任务L4/L5各唯一6请求、每类3例；零计算GET | [归口结果](../../../../../../docs/tasks/prefix-analysis/RV2_L_HANDOFF_20261101.md) |
| 低命中/公共独立复审 | 最终146公共/低命中、4独立边界、6Token受影响专项、mypy/ruff、215只读路由通过 | [独立报告](../../../../../../docs/tasks/prefix-analysis/INDEPENDENT_REVIEW_RESULT_20261101.md) |
| Token私有独立复审 | 164本线、12独立边界、mypy/ruff、ART4副本14个GET（4建议/8例）通过；35原文件未变 | [独立报告](../../../../../../docs/tasks/length-analysis/INDEPENDENT_REVIEW_RESULT_20261101.md) |

前端日志路径相对`artifacts/validation/viewer/analysis/`。各层结果分列，不将不同执行者/版本/重复执行合并成虚构全套。前端新增单元测试首轮有一项测试断言误将共享before定位视为重复，已改为验证完整对照及所属组，原194通过/1失败日志保留；业务逻辑未为过测放宽。RV2未重复运行后端全套，由当前源码摘要匹配其独立复审身份并补实际联合读取。

真实浏览器覆盖：两方向同实例往返、固定历史、partial不覆盖默认ready、详情刷新返回、旧差异深链兼容、旧4193跳转、监控/MA导航、通知后目录对齐与无轮询、桌面1440/窄屏390。局部证据可读、每类≤3例，诊断请求均GET，无脚本错误。截图已人工读取检查：[低命中列表](../../../../../../artifacts/validation/viewer/analysis/rv2-20261101/browser/low-list-1440.png)、[L4详情](../../../../../../artifacts/validation/viewer/analysis/rv2-20261101/browser/l4-detail.png)、[窄屏L5详情](../../../../../../artifacts/validation/viewer/analysis/rv2-20261101/browser/low-detail-390.png)。

## 保留边界与交付

用户视觉/功能签字、生产策略批准、真实远端引用、输出质量、华为现场容量/性能尚未由本报告验证。测试输入与策略是明确构造的，Tokenizer/回放是真实执行，不是生产收益。Token显式`tool_calls:null`当前保守partial并拒绝自动修改；L4缺会话关联不推断历史改写，L5不推算收益。精确请求去重需要O(唯一请求数)内存，15万请求容量未校准。

8份AF闭环材料/旧prompt已[归档](../../../../../2026-11-01/analysis-rv2/README.md)，3份记忆原文已快照；冻结契约、HTML和原始证据不移动。两后端精确提交清单294项核对通过（公共记忆的一处登记漂移已由归口刷新）；源码/测试/契约与报告身份核对，最终文件身份见[统一版本清单](../../../../../../docs/tasks/analysis/VERSION_RV2_20261101.json)。不把未提交HEAD当测试候选，不混入其他监控任务未收口改动。

给镜像打包与审查会话的[统一交接prompt](../../../../../../prompts/sessions/ANALYSIS_UNIFIED_REVIEW_DELIVERY_RV2.md)已准备；本会话按用户要求提供文件，不自动启动新的打包任务。审查与交付须明确区分工程通过、用户认可、包体容器验证及现场结果。
