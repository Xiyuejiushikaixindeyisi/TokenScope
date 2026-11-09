# ICSL场景构造样本：102条本机验收

2026-11-05，revision3。取代已撤回的80条版本；本文件说明来源，页面中的业务字段不添加demo、synthetic或合成数据字样。

## 结果

- 102条GLM-5.2请求，appid com.huawei.icsl.base，UUID格式hash_id，正常UTC时间源/北京时间显示，间隔7–72秒。
- 62个对话（40个两请求、22个单请求）；每对话五位随机十六进制CCH，同对话保持不变，不同对话不同。对话分组仅由构造清单说明，未伪造产品本身的会话识别能力。
- system只有一个消息，首行x-anthropic-billing-header: cc_entrypoint=sdk-py; cch=xxxxx;，随后You are a Claude agent...和共享代码/测试参考。模型字段仍GLM-5.2。指令中的Agent名称不等于模型厂商。
- 长度按固定种子正态分布生成后真实分词，均值27,999.21，标准差533.86，范围26,603–29,364；5K分箱102条均在25K–30K。5K粗分箱只呈单柱，不能据此观察细粒度正态形状；不修改既有前端分箱。
- 独立回放及产品full102结果一致：35.949479%→90.156355%（页面35.95%→90.16%），增加54.21个百分点。
- before P=2855919 H=1026688 C=1829231；after P=2853567 H=2572672 C=280895。102条逐行after_raw核对：仅删除/messages/0/content顶部billing行，所有剩余字段/指令保留。
- L1保留80条发现，发布1项建议；full checked=eligible=102、complete/available/display_eligible；固定CCH与删除CCH负对照通过。L4尾部差异仍存在。
- 整体partial来自候选比较和证据留存上限，不等于full评估未完成，也不宣称全部候选已比较。

## 前端与隔离

[监控](http://localhost:18002/#/users?run=ur-104155b7b5e947d6ac4504e5e5637fd8&appid=com.huawei.icsl.base&revision=66f89935ddcae6efdf5eea6786765ff112c21005f3e9b04c5883c6d75630dc82)

[诊断](http://localhost:18002/#/analysis?direction=low_hit&mode=history&task=e8613905-82df-45e7-9f72-fb736f40b292)

已用独立Edge打开监控、L1建议、点击证据与改法、旧用户监控及旧诊断报告，浏览器无JS错误；截图frontend-detail.png可见CCH位于system顶部。当前请求原文/UUID/时间/建议内容无demo、synthetic、合成数据。旧v1/v2试验appid保留在本机历史下拉选项里，不能把“当前内容无这些字样”扩大成“整个旧目录无这些字样”；它们不打包到华为。

追加前22条监控目录项内容不变、6个旧诊断任务保留；原final-default state 244文件SHA未变。新版未替换原产品UI/代码/配置，也未删旧数据。本机历史保留结果不等于华为现场已验证，现场仍需前后校验。

## 成本与交付

生成约32.3秒，生成峰值RSS 553888KiB；监控+诊断约69.1秒，仅本样本，不代表生产性能。CPU仿真，无GPU推理。completion_tokens=0为占位，不报告TTFT/吞吐实测收益。

CSV 15921971 bytes，SHA256 e1425657987dce4ad312d33c7e40a3ac98a822ec7ed928fb7979f1dcc785678b。

交付白名单：delivery/icsl_glm52_cch_102.csv、manifest.json、diagnostic-submission-template.json、HUAWEI_PROMPT.md；可附本说明、final-validation.json、structure-validation.json、negative-controls.json及截图。不打包含本机ID的diagnostic-submission-local.json、state、旧版本、真实数据。

证据：acceptance-backend.json、final-validation.json、structure-validation.json、negative-controls.json、frontend-validation.json及frontend-*.txt/png。构造脚本在上级build_dataset_v3.py；真实链路脚本run_acceptance_v3.py、verify_full_v3.py。
