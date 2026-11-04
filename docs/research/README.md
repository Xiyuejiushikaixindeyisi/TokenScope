# 调研入口

2026-11-04新增：[V3研究与产品设计入口](../tasks/product-v3/ENTRY.md)及[任务书](../tasks/product-v3/RESEARCH_BRIEF_20261104.md)。专职新session立即研究，未来现场报告增量纳入；本轮不开发产品代码。

本目录保存参考实现、论文和专题研究。[候选参考清单](implementations/CATALOG.md)中的条目不自动代表已调研、采用或接入；具体状态以对应研究记录为准。

- implementations：每个项目的固定版本、关键代码路径、可借鉴部分与适用边界。
- papers：论文身份、版本、问题、方法、证据及与 TokenScope 的关系。
- topics：跨项目的专题结论，避免把某一个参考项目直接当成完整方案。

当前专题：[Agent异常分析首轮调研（2026-10-30）](topics/AGENT_ANOMALY_RESEARCH_2026-10-30.md)，覆盖工具、低命中原因、编排问题、公开trace、排队建模与infra；尚未运行数据集、定稿产品设计或接入候选工具。

现场参考：[PrefixLens报告核对与设计取舍](implementations/PREFIXLENS_HUAWEI_REVIEW_2026-10-30.md)。用户提供的原件按字节封存，设计优化至v0.3；未引入源码或计量，远端测试/历史运行未由本会话独立重跑。

研究记录至少包含来源身份、问题、证据位置、结论、限制和采用状态。正式采用后链接 decisions、contracts 或实现阶段；研究结论本身不改变产品范围。

外部源码进入 upstream，锁定身份进入 env/sources.lock.json；原始材料进入 evidence，避免研究文档与源码混放。

