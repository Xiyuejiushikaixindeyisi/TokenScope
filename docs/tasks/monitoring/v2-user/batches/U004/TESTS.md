# U004实测

pytest test_user_estimator/test_user_ranking：34 passed（含U003回归），XML artifacts/validation/user-monitoring/U004/tests.xml。独立Decimal穷举1000个边界/单调性算例，约0.054s≤2s。合成32768长度示例le=50%/lt=75%；n=0、r=0、无预算/空/0/超范围、NaN/Inf/非法参数、来源约束通过。

持久化测试：情景不可变与新revision、并发8次幂等仅一结果、模型服务冲突、缺组不可用、HTTP严格DTO、重启/缺源后旧结果可读，GET无写入。mypy50源文件及ruff通过。真实校准未执行，未提供校准准确性结论。
