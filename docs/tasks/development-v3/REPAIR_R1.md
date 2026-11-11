# 独立验收R1修复批

2026-11-10，LOCAL_REPAIR_VERIFIED / WAITING_INDEPENDENT_REVIEW。独立验收NOT_ACCEPTED优先于先前LOCAL_VALIDATED；禁止进入打包。依据product-v3/acceptance-v3/REVIEW_20261110_R1.md与用户授权本线修复。

范围：RV3-01非clock L1（billing_header/普通时间/path）；RV3-02工具排序、description动态改法到实算及工具增删证据；RV3-03新L4/L5完整代表请求对照。复用旧槽识别/排序原语、新有界调度和A/B计量；不恢复旧无界POST、不手工指定recipe、不开发Token。

实施顺序：通用Finding/冻结Recipe和编译→新候选通道/真实对证据→统一worker/report→前端协议/展示→正常worker六场景及负例/完整对照组件→全回归相关门禁→唯一新候选冷启clock+非clock浏览器/独立核算。每次新attempt，旧验收state只读，不覆盖证据。

验收：六组独立复现输入在新state正常prepare/diagnose；CCH/普通日期/path/L2/L3分别有自动finding、guarded plan、同样本完整实算；工具增删仅证据，不强造变换。L4/L5代表请求键/hash与完整原文对照一致，有界保留/预算不足显式，不伪装全覆盖。固定值/字段不兼容/非法工具负例，无自动full；clock与旧报告不退化。

显式full：原D6仍有该项，未找到最新用户明确取消依据。保留UNIMPLEMENTED_DESIGN_ITEM，不能以“聚焦样本”代签范围变更；本修复不自行扩展该入口。待验收/用户裁定，不能宣称D0–D8全满足。

问题/测试/闭环结果在本文件增量记录，最终候选另立身份。首次B007错误闭环结论已撤销为修复中；原证据保持。

最终修复候选、全部验证与剩余边界见[batches/REPAIR_R1/CLOSE](batches/REPAIR_R1/CLOSE.md)、[TESTS](batches/REPAIR_R1/TESTS.md)、[ISSUES](batches/REPAIR_R1/ISSUES.md)。三个阻断本线已修复复验；独立验收未改签，不打包。
