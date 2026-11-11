# V3B003 ISSUES

I01 固定化业务影响：定位器拒绝嵌套/缺闭合/属性/额外指令，固定化保留块外文本并明确changes_time_awareness；单元和真实编码验证通过，业务影响继续披露，不标无损。

I02 自动发现与指定实验：真实worker输入仅source和已完成prepare引用，两模型变化正例自动产finding→plan；固定clock且历史不同负例不产finding。历史轮次不参与逻辑字段键。组件风险验证闭环，完整评估/前端在B005/B006继续验收。

I03 静态检查：新增集成测试有未用Path导入，已删除；ruff/mypy通过。未删除失败断言、未更改门槛。

无本批代码阻断；总体端到端未执行。B002历史测试日志损失仍见其ISSUES-I04，不因本批关闭而抹去。
## 独立验收R1补充
RV3-01：原批clock组件通过不代表非clock L1保留；通用动态槽链断点已由R1补齐。详见../REPAIR_R1/ISSUES.md与TESTS.md；当前VERIFYING。
