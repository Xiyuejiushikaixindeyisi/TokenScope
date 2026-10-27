# 首次Git基线整理：2026-10-27

用户授权整理、检查、提交并推送main；不创建PR，不构建Docker/代码包。本地初始无Git仓库，远程origin为空，已验证SSH连接。

## 调整

- 保持src/apps/docs/configs/tests/scripts/memory等职责结构，不重构业务逻辑，不删除或移动重要实验数据。V0.1 Word和.build生成脚本保留。
- .gitignore补齐env浏览器/下载缓存、构建输出和交付归档；.gitattributes保持字节，避免跨平台换行改变S0摘要。
- README/env说明/结构说明更新到实际可运行状态，补运行、验证、资产恢复和未实现功能。
- Git工作流明确main、未来两分析分支及本地backup；pre-push阻止backup分支、历史产物与大文件上传。不要把含镜像的backup合并main。
- 回退测试原依赖被忽略artifacts，现使用tests/fixtures/dev5_control中原样最小7文件及包标识，摘要可核对；历史源未删除。
- docs/releases保存小型联合测试/源码摘要以便GitHub审阅，完整轨迹和数据仍留本地。

## 版本与验证

后端dev6/前端f006联合修正版，S0 1.0.0/schema3/view1；以首次main提交标识当前整理版本。此前联合通过166后端/143前端/30浏览器场景、30,168条有效合成请求。此次整理重新运行质量/测试/本地服务，最终结果见本页后续记录；不能把历史联合结果替代本轮运行。

本轮不生成交付包，不上传真实CSV、权重、tokenizer文件、upstream副本、运行库、镜像、缓存或完整测试产物。仅main推送，backup/20261027-init为本地源码基线；未来两个分析分支仅约定名称，未启动。


最终本轮验证：166 pytest通过（123.82s）、143前端测试通过；ruff/format/mypy/typecheck/lint/build通过。首次新hook格式检查未通过，补空行后复测通过，原日志保留。独立本地HTTP服务：首页、三模型处理、15组目录和快照均通过；测试服务已退出。推送钩子4场景通过。检查摘要在docs/releases/monitoring-v1-joint-20261027/repository-*.json，完整日志留artifacts/validation/repository-20261027。推荐并采用首次提交信息：`init: 项目首次上传`。
