# V3修正前端DEMO r1（待用户审批）

[打开交互HTML](index.html) · [证据核查与合成/验收方案](../../LOCAL_FIXTURE_DEMO_REVIEW_20261111.md)。无需服务或安装；在本机浏览器直接打开index.html。Windows对应路径：`\\wsl.localhost\Ubuntu-22.04\home\zhangxiyue\TokenScope\docs\tasks\development-v3\prototypes\repair-demo-r1\index.html`。

## 建议审批路径

1. 在APPID选择中逐一切换五组，模型随业务对应。BUS04只有clock主建议，BUS03额外展示无clock工作目录L1；其他有工具描述L3。
2. 点击“查看证据与改法”，核对双边高亮、精确改法、样本参考、业务风险，再返回原卡片。特别检查clock外内容保持，以及路径方案不能误写成替换成另一用户路径。
3. 报告下拉查看0.5个百分点、零/负收益、未评估、无clock变化、L4/L5兼容示例；这些是DEMO状态，不是产品新增操作入口。正式报告下拉显示真实报告历史。
4. L4/L5各一张卡，详情最多三例；L5只展示差异，不编造改法或收益。其他三主入口仅保留原位置，不在本次DEMO模拟；Token新执行不启动。

数值均为展示示意，不是运行分析器所得；正式验收在本机使用合成来源真实计算，布局和交互对照此DEMO，数值不要求等于DEMO。顶部DEMO提示是评审标识，正式合成验收标“合成数据验证”。

## 基线、允许差异与检查

- 基线UI04原件SHA见manifest.json；四份CSS逐字保持，原件未改。保留V2颜色/主导航/卡片/双边证据/详情，采用正式V2已有appid、模型和历史选择，不增加SampleDiagnostics。
- 本目录只含演示HTML/展示数据和QA记录，不是产品源码、测试fixture或真实分析产物。没有修改apps/src/tests/契约/state，也未启动服务、产品分析或构建。
- 静态DEMO以Windows Chrome headless直接打开file URL检查：5组切换、6种状态、详情深链接刷新、返回及L5≤3例；无JS错误、无HTTP请求，390px窄屏无水平溢出。截图1440px及390px，最终结果见[qa-02/checks.json](qa-02/checks.json)。手工查看了桌面与clock详情、窄屏截图。
- 首轮QA发现Windows路径反斜杠在HTML脚本字符串中被解释，已仅修DEMO并复验；原qa截图保留，最终以qa-02及manifest身份为准。此检查只证明DEMO交互，不证明分析器/收益或资源修复已通过。

当前未获“前端展示审批通过”。必须先由用户明确给出该批准，再细化batch开发方案；开发方案另行审批后才能代码开发。本次DEMO审批不自动授权实施或打包。
