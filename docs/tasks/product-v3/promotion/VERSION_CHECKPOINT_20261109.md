# 宣传材料与 V3 方向版本整理

后续同日用户已授权 Git 提交和探索 prompt；当前动作见[提交说明](GIT_CHECKPOINT_20261109.md)与[执行文本](../HUAWEI_LOW_HIT_EXPLORATION_PROMPT_20261109.md)。本文以下保留提交授权之前的文档整理记录；文件摘要清单已随本次提交准备刷新，源报告与 HTML 摘要不变。

2026-11-09，本次是文档检查点，不是产品发布或 Git 提交。环境 THREAD/SESSION 均为 `01a1a5d5-4baf-7a41-b5c6-14bd5f4f67c2`。工作区 HEAD 为 `4dc32d4`；本线最近 HTML、报告回填及本次文档增量仍在工作区，未 commit/push，也未纳入其他会话修改。

## 当前有效材料

| 材料版本 | 优先级/状态 | 维护入口 |
| --- | --- | --- |
| quadrant-detail-r1-20261109 | **高优先级长期文档**；77组、77张完整直方图，默认长低14组 | [HTML](quadrant-detail/dist/index.html) · [说明](quadrant-detail/README.md) |
| huawei-brief-r2-fielddata-20261109 | 当前认可的四页汇报；只读回传已填入 | [HTML](huawei-demo-r2/dist/index.html) · [数据核对](huawei-demo-r2/REPORT_INTEGRATION_20261109.md) |
| V3优先级决策20261109 | 当前研究/设计方向；尚未实施 | [低命中率优先、Token异常转V3.5](../V3_LOW_HIT_PRIORITY_20261109.md) |
| TokenScope_V2_Overview第一版 | 用户否决，退役；原字节留存，不推荐使用 | [历史HTML](TokenScope_V2_Overview.html) |
| 研究/设计/路线r0 | 作为历史研究依据保留 | 设计与路线顶部已指向最新决策，不再以旧全功能MVP覆盖新范围 |

四象限明细不是临时宣传附件，后续汇报版式改变不降低它的优先级。当前读取的是 2026-10-20 约两小时、67个appid/77组/150,698条真实请求的既有结果；50%为命中分界，10K为临时长度观察线；ICSL构造样本排除。象限用于选对象，不自动证明场景语义、根因或可改善性。

## 固定身份与桌面副本

| 文件 | 字节 | SHA256 |
| --- | ---: | --- |
| quadrant-detail/dist/index.html | 1,639,153 | 8d76928147dd8a4f274fd0e160a916a493e7878d4ba14c7c339683877ba2a354 |
| huawei-demo-r2/dist/index.html | 114,866 | 600d6a6bdc925c29fdfc31a83a194021d82eeb700cbd945bcf241f98467f5a3d |
| TokenScope_V2_Overview.html（退役） | 48,274 | 853efec47df3a0f6c9a793094b787a5e0fa422519c649ae632e66c68cb538c40 |

桌面副本为 `C:\Users\ALIENWARE\Desktop\TokenScope_四象限明细_20261109.html` 和 `C:\Users\ALIENWARE\Desktop\TokenScope_业务汇报_20261109.html`，与对应项目文件逐字节相同。原路径继续有效，不重复生成或改动 HTML，不移动仍被引用的文件。

[机器可读清单](VERSION_MANIFEST_20261109.json)记录有效 HTML、模板/生成脚本、关键文档、只读来源和本轮核查源码的完整 SHA256。清单中的源码只说明核对版本，不表示本轮发布产品。原始请求、state、数据库和大包不纳入文档清单。

## 本次变更与验证

- 宣传入口/版本台账消除过期“等回传”“待制作”等当前时态，将四象限明细置顶并标明高优先级。
- 新增低命中率优先决策，固定六组 appid×模型、已有指标和小样本边界；Token异常V3.5候选单列。更新本线记忆、r0设计和路线的当前状态提示。
- 对两份有效 HTML、退役 HTML、现场原报告、产品映射及桌面副本核对字节数/SHA；验证既有77组汇总、指定六组摘录与本轮 Markdown 相对路径。
- 本轮未改 HTML，不重复运行上一轮浏览器交互验收；已有桌面/窄屏、四象限计数、77张图、搜索筛选排序和日志检查见两份报告说明及各自 qa 目录。本轮不宣称新增 UI/打印验收。
- 对13份其他会话已修改文件核对前后 SHA；保留既有 Git 工作区修改和暂存区。本轮只涉及本线文档/记忆，无产品、契约、数据或服务变更。

后续报告补充时应固定新来源身份、保留旧版本与来源说明，再更新当前 HTML 和桌面副本；不能覆盖原始华为证据或把新版文件仍称作本次相同摘要。下一轮由用户发起华为探索 prompt 制作，本轮没有生成、发送或执行现场任务。
