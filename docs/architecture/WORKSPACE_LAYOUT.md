# 工作区结构

统一根目录为 /home/zhangxiyue/TokenScope。目录方案于 2026-10-23 获用户批准。本目录按内容用途组织，不按 session 复制工程。

## 根目录职责

| 目录 | 内容和维护规则 |
| --- | --- |
| memory | 研发当前状态、协作规则、会话分工和交接，保持精简并链接权威文档 |
| docs | 范围、设计、契约、现场核对、阶段计划、调研、决策和分享 |
| upstream | 固定版本的外部仓库或源码快照，不跟随浮动分支漂移 |
| patches | 对固定上游基准的必要补丁和应用说明 |
| models | 按模型及 revision 保存 Tokenizer、Chat Template 和来源摘要 |
| env | 源码身份、环境 profile 与依赖锁说明；实际 Python 环境将放 .venv |
| configs | 非秘密运行配置，包含模型、窗口、基线与探测器参数 |
| src/tokenscope | ingestion、encoding、monitoring、analysis、detectors、agent、adapters |
| crates | 后续 Rust 热点实现，具体职责以实现计划为准 |
| apps/viewer | 本机可访问的展示入口 |
| prompts | agent、huawei、sessions 三类版本化提示词 |
| tests | fixtures、unit、replay、conformance、integration |
| scripts | dev、import、validate、package 辅助工具 |
| deploy | 后续 Dockerfile、Compose 和部署入口 |
| evidence | 原始源码投递、现场回传、文件清单与摘要 |
| data | raw、normalized、derived 实际数据，保留来源关联 |
| artifacts | runs、agent_runs、builds、releases 运行与交付产物 |

2026-10-27：src/tokenscope与apps/viewer已有通过本机联合验收的服务实现，.venv为实际本地环境；分析/Agent等目录仍按各任务入口启动。.build保留V0.1生成脚本，生成图片/render目录只留本地，不大规模搬迁历史脚本。

## 文档结构

requirements、architecture、contracts、huawei、tasks、stages、research、decisions、operations、sharing、archive。

research 分 implementations、papers、topics；原始论文或材料可放 evidence/source_drops，阅读结论放 research。tasks 下已建立监控、展示、前缀诊断、长度诊断和自进化 Agent 的入口、设计位置及代码地图。具体 batch 在对应设计形成后创建；stages 保留早期通用模板，不重复维护另一套计划。

## 来源与维护副本

- PrefixLens 本机基础版与华为完整版本分别记录身份。原始投递保存在 evidence，可核对源码保存在 upstream，自有接入层保存在 src/tokenscope/adapters。
- PrefixLens-PPT 的既有成果作为来源材料；新说明和展示稿进入本项目的 docs/sharing。
- 兄弟项目为只读参考。引入后以本项目内的独立副本及固定身份维护，不依赖外部工作区软链接。
- 调研候选清单与已锁定源码清单分开：候选在 docs/research，实际引入的版本在 env/sources.lock.json。
- models 不默认包含完整模型权重。真实权重仅在后续任务需要时另定保存与交付范围。

## 资料流转

原始投递进入 evidence → 记录身份与摘要 → 核对结论进入 docs → 自有实现进入 src/crates/apps → 验证结果进入 artifacts 并由阶段文档总结 → 用户同意打包后冻结 artifacts/releases → 现场回传进入 evidence/huawei。

Agent 候选探测器和调查过程进入 artifacts/agent_runs；验收通过后，正式实现进入 src/tokenscope/detectors，保留验证和来源链接。

## 历史材料

根目录现有 TokenScope_设计文档_V0.1.docx 保持原路径和字节，避免旧链接失效；其历史状态由 docs/sharing 与 docs/archive 登记。.build 是该文档生成与排版核验的既有工作目录，新产品运行产物使用 artifacts。

不把归档等同删除，不覆盖已发布或已回传版本。归档文件应说明替代入口。

