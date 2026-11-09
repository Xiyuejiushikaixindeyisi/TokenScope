# 研究与宣传材料版本台账

最新检查点：**四象限明细 HTML 为高优先级长期文档**，当前内容版 `quadrant-detail-r1-20261109`；四页汇报为 `huawei-brief-r2-fielddata-20261109`。两份 HTML 与桌面副本已核对原字节，见[版本整理记录](VERSION_CHECKPOINT_20261109.md)和[文件摘要清单](VERSION_MANIFEST_20261109.json)。文档修订号不改变 V2 产品版本。

当前研发方向由[V3 低命中率优先决策](../V3_LOW_HIT_PRIORITY_20261109.md)确定：先六组真实小样本探索与有效改法，Token 异常冷却到 V3.5。最新用户已授权提交 Git 并生成[华为探索 prompt](../HUAWEI_LOW_HIT_EXPLORATION_PROMPT_20261109.md)，见[本轮提交说明](GIT_CHECKPOINT_20261109.md)；不操作产品或远端。前序文档整理时的“未提交”是当时事实，本轮提交身份以 Git 历史为准。

四页 HTML 已基于[只读回传报告](../../../huawei/TOKENSCOPE_PROMOTION_READONLY_20261109.md)完成，详见[核对记录](huawei-demo-r2/REPORT_INTEGRATION_20261109.md)。报告 SHA256 `31ee6957e16c6ddcc09c61e5abde2490be8b532a7fa3801d801d197304a5b5ab`；四页 HTML SHA256 `600d6a6bdc925c29fdfc31a83a194021d82eeb700cbd945bcf241f98467f5a3d`；明细 HTML SHA256 `8d76928147dd8a4f274fd0e160a916a493e7878d4ba14c7c339683877ba2a354`。

日期：2026-11-09。角色：TokenScope V3调研与产品设计，当前阶段为宣传文档整理与V3优先级收敛。环境CODEX_THREAD_ID/CODEX_SESSION_ID再次读取，均为`01a1a5d5-4baf-7a41-b5c6-14bd5f4f67c2`。

较早轮次曾授权本线整理、提交与更新记忆，对应检查点 `4dc32d4`；本次在该基线上提交本线后续材料与探索 prompt。产品源码、冻结契约、批准四入口、运行数据、其他session修改及全局入口保持。

## 当前与历史

| 材料 | 当前状态 | 使用方式 |
| --- | --- | --- |
| [四象限明细报告](quadrant-detail/dist/index.html) | **高优先级长期文档，r1**；77组/77图，默认长低14组 | 负载画像与V3探索选点入口；[桌面副本与验证](quadrant-detail/README.md)，独立维护，不随宣传稿退役 |
| [V3低命中率优先决策](../V3_LOW_HIT_PRIORITY_20261109.md) | 当前方向与下一轮探索范围 | 六组指定appid×模型；小样本原因/改法/对照；Token异常转V3.5 |
| [华为低命中探索prompt](../HUAWEI_LOW_HIT_EXPLORATION_PROMPT_20261109.md) | 已准备，可直接发送；未执行 | 六组有界样本；独立CPU探索；单Markdown关键证据嵌正文 |
| [华为风四页HTML DEMO](huawei-demo-r2/dist/index.html) | 四页方案已认可；r2已填入现场报告 | 后续用户明确授权制作；[数据与验证](huawei-demo-r2/README.md)，不替代产品前端，宣传修订号不等于产品版本 |
| [四页汇报r1](FOUR_PAGE_STORY_R1_20261109.md) | 已用于制作的内容依据 | 目标架构/案例/三大系列/四象限分类；只读收集已回传、HTML已回填 |
| [本轮初始华为业务汇报思路](HUAWEI_BRIEF_DISCUSSION_20261109.md) | 历史讨论输入 | r1覆盖仅称筛选图、P/N横轴与第四页指标范围等旧建议 |
| [第一版HTML](TokenScope_V2_Overview.html) | 用户明确不符合预期，退役 | 原路径原字节保留，只供追溯；技术检查通过不代表内容获认可 |
| [听众画像](../AUDIENCE_PROFILE_V2_20261104.md) | 基本认可，继续适用 | 大boss/领导了解业务开发与运维，AI内部机制上下文不足 |
| [旧展示大纲](../LEADERSHIP_OUTLINE_V2_20261104.md)、[旧故事讨论](../LEADERSHIP_STORY_DISCUSSION_20261104.md) | 历史讨论输入 | 内容素材可复用；不能继续视作当前页数/顺序设计 |
| [11-05演示讨论](../LEADERSHIP_DEMO_DISCUSSION_20261105.md)、[80条原方案](../SYNTHETIC_GLM52_DEMO_PLAN_20261105.md) | 规格已被后续覆盖 | 原记录不改写，当前规格转revision3 |
| [ICSL版本入口](../icsl-demo/README.md) | revision3本机通过、交付线已打包 | 102条/约28K/顶部CCH；不混用旧80条数字，不冒充生产实测 |
| [研究](../RESEARCH.md)、[证据矩阵](../EVIDENCE_MATRIX.md)、[设计](../PRODUCT_DESIGN.md)、[路线](../ROADMAP.md) | 保留r0背景，旧全功能MVP不再作为当前顺序 | 优先级由11-09低命中决策覆盖；尚未启动实施，现场边界见[11-05修订](../EVIDENCE_UPDATE_20261105.md) |

第一版HTML：48,274字节，SHA256 `853efec47df3a0f6c9a793094b787a5e0fa422519c649ae632e66c68cb538c40`。不因用户否决而删除历史文件或改写旧检查结果。

## 本轮用户输入

原文件只读保留在`docs/huawei/`，不混入本线提交，也不将表内业务数值用于TokenScope宣传业绩。本台账固定本次读取身份，后续输入变化需重新核对。

| 输入 | 字节数 | SHA256 |
| --- | ---: | --- |
| 华为风PPT参考.md | 28766 | 2fdb06cedca3e62e748f8d92c257c6107bb9857af694653e408d0a5d38e16883 |
| appid与对应产品（未去重）.md | 7137 | 90c34d86fbe8687495e076617fc27f3d18ea6685ea0f3f12ffd1f59f5097e345 |

表格机械读取：122条记录、105个不同原始ID单元格、26条产品名称缺失。未拆分复合ID、未确认大小写别名、未核验产品归属；这些只是原表质量描述，不是appid数、产品数、业务场景数或已分析覆盖数。

## 历史：较早轮次的 Git 检查点（4dc32d4）

本次将此前未纳入版本控制的本线研究/宣传文档、样本脚本、有效来源清单和小型验证摘要作一次检查点提交。仅暂存明确白名单；数据包、原始请求、state、浏览器profile、截图、模型资产和其他session改动不纳入。局部.gitignore保护本线生成目录，不修改根Git规则。

文档检查核对本地引用、HTML原字节、样本摘要和非本线已修改文件的SHA；不重跑产品/构造数据/推理。提交SHA以Git历史为准，避免将提交自身SHA循环写入其内容。按项目Git约定显式同步origin main；若失败在对话报告实际状态。

本轮检查：23份Markdown本地链接有效；49份白名单文件约330KB，无CSV/state/模型/包体；Python仅做语法解析、JSON解析通过；历史HTML和其他session已修改文件SHA不变。五层Token运营原文保留原始CRLF/空白并独立核对SHA，其余白名单通过Git空白检查；不为消除格式提示改写用户原始证据。
