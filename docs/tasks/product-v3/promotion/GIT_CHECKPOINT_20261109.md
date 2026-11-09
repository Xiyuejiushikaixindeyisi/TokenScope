# 本线 Git 检查点与华为探索 prompt

2026-11-09，用户明确授权“提交Git、生成华为探索prompt”。本次从 `main` 的 `4dc32d4` 起，将此前四页汇报回填、四象限明细、V3优先级与本次执行prompt作一个本线检查点。按项目约定精确提交并显式 `git push origin main`；最终commit SHA与远端同步状态以Git历史和本轮对话为准，文件不写自身commit SHA。

## 交付与边界

- [四象限明细HTML](quadrant-detail/dist/index.html)是高优先级长期文档，当前r1；[四页汇报](huawei-demo-r2/dist/index.html)为认可r2现场数据版。HTML与桌面副本原字节保持，未重新设计或启动浏览器验收。
- [华为探索prompt](../HUAWEI_LOW_HIT_EXPLORATION_PROMPT_20261109.md)已准备，只研究六组指定appid×模型。允许现场独立目录内有限样本结构分析/改写副本/CPU对照，保护原服务和state；不向现有前端注册结果。单份Markdown回传证据和可开发建议。
- [V3方向](../V3_LOW_HIT_PRIORITY_20261109.md)维持低命中优先、Token异常V3.5；本机只准备prompt，未发送、登录华为或启动分析/实现。

## 精确提交范围

仅 `docs/tasks/product-v3/` 内本线新材料及变更（不含共享ENTRY/任务书）和 `memory/tasks/product-v3.md`。包含静态HTML、模板、生成脚本、研究/设计状态提示、版本清单与执行文本；不包含产品源码、配置、四入口、冻结契约、原始请求、运行state、数据库、交付包、模型资产或浏览器资料。

`docs/huawei/` 用户提供的三份新材料和其他会话修改保持原状，不顺带加入提交；其来源身份在本线清单留存。HTML内含已授权汇报的聚合统计，不含原始请求正文。两个HTML均为单文件可离线打开；生成脚本重建需要本机对应只读报告和映射文件，不能把仅拉取Git仓库宣称为已包含全部现场输入。

## 检查

提交前核对：本线Markdown本地引用、Python静态语法、JSON清单、六组appid/模型/指标与既有报告一致；两份HTML/桌面副本及原报告摘要保持；白名单不含QA/样本/state/包体；其他会话文件摘要不变；Git暂存清单与白名单逐项一致、空白检查通过。既有HTML浏览器验收沿用上一轮记录，本轮未改HTML，不重跑产品测试或真实分析。

[文件摘要清单](VERSION_MANIFEST_20261109.json)固定本次文档与只读核查源码身份；它不代表产品新版本发布。验证和Git回执保留在本地忽略目录 `quadrant-detail/qa/`，实际提交/推送失败应在对话说明，不借此修改或暂存其他会话文件。
