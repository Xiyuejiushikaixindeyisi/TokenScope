# U006 ISSUES

- 已解决：Pydantic TypeAdapter构造器静态签名未表达联合类型，运行时支持；单行arg-type抑制有注释，联合解析/往返测试覆盖。未关闭全局类型检查。
- 已解决：新增生成器长行与导入排序，经ruff格式化后检查通过。
- 兼容选择：旧Scenario不加默认新字段，保留序列化形状；新BatchScenario显式tag。2.0.0独立输出，旧1.0.1冻结文件不覆盖。
