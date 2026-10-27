# F001 开发方案：契约与前端工程基础

状态：closed，2026-10-27。F001门槛已通过，证据见TESTS/RESULT；原计划保留。

## 代码与行为

固定B005.1修订协议/OpenAPI、完整成功与错误样例；生成DTO并为字符串整数、nullable、cursor和scope提供运行时校验。建立React/TypeScript/Vite入口、hash路由壳、CSS变量、离线静态资源和测试环境。锁定Node/npm/依赖/浏览器版本。只做工程与契约，不提前实现后续业务。

拟维护路径（apps/viewer内）：src/api/{types,client,validate}.ts；src/domain/{integer,time,identity}.ts；package.json/package-lock.json；tsconfig/vite/test配置；src/app.tsx；tests/fixtures。禁止修改监控计量算法或后端共享文件；遇到契约缺口写ISSUES并协商。

## 验证和退出门槛

- 字符串整数0/2^53−1/2^53/64位边界/负delta及null，禁止Number先舍入。
- 错误码、未知schema、跨scope/实例、UTF8时间原串、bin_width/limit枚举。
- 构建输出无CDN/远程字体，根API地址与hash路由正确。
- R1回执/终态和R2结束校验样例齐全，边界已由后端确认。

关闭要求：契约对照表、锁文件、构建与静态/DTO检查证据；F001接口问题无阻断。测试命令和实际结果写TESTS；问题复现/根因/修复/复测写ISSUES；RESULT逐项对照后才进入下一批。

## 回退

撤回本批工程/类型变动，保留原型和后端；锁文件与源码成套回退。留存源码/依赖锁/配置摘要与失败证据，不全局reset或删其他会话产物。

2026-10-27 最新：用户允许修正F001-I02并继续；F001实施中。S0固定1.0.0，后端真实服务尚未验收。
