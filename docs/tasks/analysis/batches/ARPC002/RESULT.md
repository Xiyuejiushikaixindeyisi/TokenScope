# ARPC002 局部证据

2026-10-31，公共提供方核心实现/测试完成，后续ARPC004/006验证同任务封存和失败终态。

evidence_locator.py按JSON词法定位，保留数字原文，重复key不给假高亮；Unicode codepoint范围、外层转义/内嵌JSON边界映射和text_range已实现。截断不切开选中字符串的转义/代理对；不能定位返回显式原因，原文摘要不符拒绝。每组最多3例，局部例子字节超限报预算失败而非静默少报；删除值用VALUE_REMOVED，不把数组后继元素冒作删除后内容。

recommendation_evidence.py生成请求A/B与同请求修改前后两类对象；原文和Plan不内联到业务例子，成员统计独立于采样。结果写入同ResultWriter，GET不会生成例子。

单元覆盖重复文本、重复key/缺字段、大整数、非BMP、内嵌JSON、64k字段、decoded text_range、转义安全截断/越界；公共与低命中82 passed / 0.72s。真实GLM任务的局部前后证据由test_recommendation_publication验证。最终API字段/manifest由后续批次交付，当前不改正式前端/打包部署。


## 最终联合闭环

2026-10-31：本批实现已纳入ARPC006当前源码联合验证与实际HTTP交接，详见[最终验收](../ARPC006/RESULT.md)。上文阶段性待项由最终记录覆盖，不将早期测试当新功能签收。
