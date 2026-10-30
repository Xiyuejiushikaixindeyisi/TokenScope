# 异常分析后端母会话入口

2026-10-30：待创建/登记。先由一个异常分析后端session进行调研、产品设计，完成后再按用户启动fork“低命中率分析”和“Token异常”两条详细设计/开发线。异常分析不属于Token监控功能增加；本轮未创建会话或开展业务研究。

## 角色与优先任务

首先明确角色、范围、阶段、实际ID与依赖，登记[SESSIONS](../../../memory/SESSIONS.md)。优先收敛两类诊断的问题、输入、证据/建议/收益表达及分线交接，不在母会话自动提前实现两个分析器。

低命中诊断复用监控理想命中结果/中间信息；Token异常复用编码计量和来源映射，不维护第二套Tokenizer/Template或缓存算法。报告DEMO是展示起点，不代替后端能力或契约。

## 阅读优先级

P0：AGENTS → CURRENT → SESSIONS → docs/README → 本入口。

P1：[低命中任务](../prefix-analysis/ENTRY.md)、[Token异常任务](../length-analysis/ENTRY.md)、[V1验收](../../huawei/MONITORING_V1_ACCEPTANCE_20261030.md)、[UI-01](../viewer/PROTOTYPE_V2_UI_01.md)。按需核对监控[DESIGN](../monitoring/DESIGN.md)、[CODEMAP](../monitoring/CODEMAP.md)、[S0](../monitoring/batches/B005.1/S0_CONTRACT.md)及[实际API](../../contracts/MONITORING_IMPLEMENTED_API.md)。P2按问题读PrefixLens等已有材料；P3才读历史。现场取证使用单份md与内嵌脱敏证据，不要求上传生产CSV。

## 分线与前端

调研/产品设计放本目录，后续两线沿各自任务目录维护详细设计/开发。增量记忆未来使用memory/tasks/analysis.md，未启动不预建全部文件。[异常分析前端](../../../prompts/sessions/ANOMALY_ANALYSIS_FRONTEND_START.md)统一对接两类后端；产品/后端设计及契约固定后按工作流推进。两类分析设计和代码完成后才按用户启动自进化Agent。
