# M005 问题记录

建档时开发/验证尚未执行；当前本批已闭环，实际问题和复测记录见下方。开批依赖：现场/前端pending单列；不可把本机失败推给现场，更不能为了验收启动部署/打包。

| 问题ID | 发现/证据 | 影响与原因 | 修复位置/版本 | 复测证据 | 状态 |
| --- | --- | --- | --- | --- | --- |
| 尚未创建 | 尚未开发/测试 | 待实际核查 | 无 | 无 | not_run |

实际问题使用M005-I001起的稳定编号，保留失败与修复轨迹。正确性、兼容、数据安全及必需测试问题未闭环不得closed；重大设计偏差先与用户确认，不降低门槛换通过。


## 最终执行记录 2026-10-30
M005 closed。本机后端最终pytest235 passed/1既有弃用warning/190.03s；ruff check、format111文件、mypy44源码及协议校验通过。真实HTTP/CLI、进程退出恢复/并发、资源及MA01–14/X01–12设计矩阵已完成。详见RESULT、DESIGN_CHECK、IMPLEMENTATION_MANIFEST；原始证据artifacts/validation/monitoring/v2-ma/M005/final-02与resource-attempt02。未部署/打包；前端、现场、用户索引三线联合单列pending。

M005-I01：Histogram原通用JSON结构不够明确，改为严格DTO并检查边界/箱计数/覆盖，最终全量235项复测通过。类型检查发现局部变量histogram复用为映射和单个对象，改名histogram_map后通过。M005-I02：前端接收样例不足，补齐16个严格验证合成样例；非业务代码变更，不代签前端验收。全部本机问题closed。
