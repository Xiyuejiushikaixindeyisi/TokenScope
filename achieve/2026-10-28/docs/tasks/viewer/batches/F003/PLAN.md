# F003 开发方案：监控展示与只读交互

状态：closed，2026-10-27；具体证据与范围见RESULT/TESTS。

## 代码与行为

迁移已批准HTML监控风格；完成范围/历史、概览、三直方图、多列请求、轻证据、信号页。精确字符串显示、像素缩放、键盘/焦点/窄屏。所有组件从可见快照读取；只读明细分页不预取正文。未实现分析页不装入真实导航。

拟维护路径（apps/viewer内）：src/features/{overview,distributions,requests,signals}；src/components；src/styles；tests/component；tests/browser/monitoring。禁止修改监控计量算法或后端共享文件；遇到契约缺口写ISSUES并协商。

## 验证和退出门槛

- 与独立样例逐值核对J/P/H/C/O、rate、nearest-rank和所有并列众数。
- 0/5000/200000/超长尾、空/null、字符串整数tooltip、共享纵轴。
- 点击柱区间、尾部无upper、J/P/C不同排名不得拼行、重复hash完整。
- 每段1000点排名范围清晰，多列排序次序、hash文字前缀。
- 详情UTF8预览/轻证据、模板能力关闭、文本不执行HTML。
- 新包在详情/固定历史停留；390px与桌面无横向溢出、键盘可用。

关闭要求：组件/浏览器和视觉检查通过，网络证明缓存切换不重复读指标。测试命令和实际结果写TESTS；问题复现/根因/修复/复测写ISSUES；RESULT逐项对照后才进入下一批。

## 回退

退回F002组件入口/样式，保留数据层测试；不改冻结原型。留存源码/依赖锁/配置摘要与失败证据，不全局reset或删其他会话产物。
