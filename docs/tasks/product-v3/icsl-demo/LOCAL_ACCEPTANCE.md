# ICSL合成演示本机验收（2026-11-05）

结论：revision2通过本机监控→L1定位→修改方案→80条全量评估→前端证据展示验收。不是ICSL生产数据或真实推理性能测试。

## 数据与结果

- 交付数据：[CSV](revision2/delivery/icsl_glm52_cch_80.csv)，[清单](revision2/delivery/manifest.json)。使用revision2，首轮v1仅保留排障证据。
- 新appid：`demo.synthetic.icsl.glm52.cch.v2`；模型GLM-5.2，服务别名GLM-V5.2。80条虚构编码Agent请求，固定工具、代码/测试参考、变化的任务尾部。
- 请求结构：稳定system A→独立system计费头（cch逐请求变化）→稳定system B→变化user任务。用于模拟机制，不声称逐字复制ICSL/Claude Code请求结构。删除计费头的业务前提在本合成数据中成立。
- GLM模板后输入：平均49,999.125，最小47,916，最大52,017，标准差881.08；页面5K分箱众数50,000–55,000。
- 本窗口从空缓存开始，Token加权理想命中率：**35.898228% → 90.051281%**，提高54.153053个百分点。
- before：输入3,999,930、命中1,435,904、重算2,564,026。after：输入3,997,580、命中3,599,872、重算397,708。
- full评估80/80 complete、available、display_eligible；逐行核对实际after_raw，唯一变化为/messages/1/content计费头被删除。与独立计量回放逐项一致。
- L1保留80条发现；固定CCH和删除CCH两个负对照均不报L1；正对照通过。输出Token为合成占位0，不据此宣称TTFT、吞吐或业务质量改善。

## 前端及兼容验收

服务：http://localhost:18002，保留运行。

[监控页](http://localhost:18002/#/users?run=ur-9e625b7c0ad244ac89a9e1ba009227a9&appid=demo.synthetic.icsl.glm52.cch.v2&revision=93f9364a814f0f0b3db7d144bbdb497232e37e19d5f5662b6695b6ed16a645a5)

[L1报告](http://localhost:18002/#/analysis?direction=low_hit&mode=history&task=a97edd12-6731-45d5-9b36-352bede251ce)

已实际点击“查看证据与改法”，看到cch=00000/00001对照、删除前后片段与35.90%→90.05%。Edge独立浏览器无JS错误。截图和文字位于revision2/frontend-*。

报告整体partial：候选比较上限和证据保留上限导致；不表示该方案full评估未完成。仍展示L4尾部差异，不能称“只存在L1”或所有比较穷尽。

本机未发现运行服务后，从保留的final-default HV2验收state与inputs复制到本任务local目录再启动；沿用原前端dist，未修改产品。原state244文件SHA保持相同；原20条监控目录项与4个诊断任务保留，旧用户监控和旧诊断报告实测仍可打开。追加第二次还保留了首轮合成结果。此处旧数据是本机历史验收数据，不能冒称已对华为真实数据执行验证。

用户已澄清“不影响”指不删除/覆盖旧数据结果、旧入口仍可查看；新appid成为裸入口首次默认选择不再作为阻断。华为仍须现场前后对照所有旧目录项及报告摘要。

## 首轮问题及修订

首轮v1将大段上下文与CCH放在同一system消息，虽然full计算得到目标值，但完整替换方案触及建议发布层16MiB单方案预算，前端显示0建议。revision2将计费头单独放入system消息，使实际修改方案足够小；未提高产品预算、改服务配置、注入recipe或修补产品。v1不作为通过版本交付，保留供版本审查参考。此边界不代表常见真实50K场景均已适配。

## 成本与证据

生成revision2约50.8秒，生成进程峰值RSS约622MiB；服务完成监控和诊断约50.3秒（本机、本数据，不外推生产）。8 CPU预算，无模型推理/GPU。服务峰值曾观察约1.15GiB，不作完整峰值保证。

证据：revision2/acceptance-backend.json、final-validation.json、negative-controls.json、evaluation-rows.json、recommendation-summary.json、frontend-validation.json；全量原文大文件仅本地保存。修改限定本任务文件与memory/tasks/product-v3.md，没有产品修改、Git提交/推送或华为执行。

下一步使用[华为执行prompt](revision2/delivery/HUAWEI_PROMPT.md)在现场追加；不复制本机state覆盖现场。
