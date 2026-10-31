# MV2-F001 ISSUES

真实浏览器发现默认fetch作为实例方法调用触发Illegal invocation，已改成globalThis.fetch包装并复测。MA首次探针错误使用同一个pre/now引用，被422正确拒绝，改为两个现有合成文件；本探针只验证回执恢复，不宣称这对文件可形成成功MA统计。新旧Scenario联合校验需根级$defs，已修正并覆盖测试。
