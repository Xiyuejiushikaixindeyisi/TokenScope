# F006 测试记录

状态：通过，ready_for_joint；不是最终联合验收。环境：WSL Ubuntu22.04、构建Node22.22.2/npm10.9.7；Windows Node24.22.1驱动Edge156.0.4314.42/Playwright1.64.1。真实服务dev6/schema3/view1，独立合成state。

| 检查 | 实际结果/证据（artifacts/validation/viewer/F006下） |
| --- | --- |
| 142单元/组件、类型、lint、build、资源本地性、S0生成检查 | final/*.log全部exit0；67 DTO生成；源清单source-manifest.json |
| 统一浏览器回归 | regression/browser-report.json 9 passed；final-browser/browser-report.json 4 passed（shell、发布冻结、假/真性能）；cas/browser-report.json 1 passed（新增规则CAS）；没有把重复运行累加成独立用例 |
| 真实开发联调 | pass2/browser-report.json passed：3模型×5appid，每组60条，UI提交→SSE终态→范围切换→50行/正文证据→NDJSON Worker校验下载→设置/信号；input-manifest及backend-identity保留 |
| R1/R2 | F004回执恢复/乱序/实例/并发及F005六次压力/字节/失败检查通过；F006重跑字节校验和回执操作。所有9个browser spec共20个不同场景在相应服务/浏览器环境执行通过；不是同一次全套命令 |
| 性能 | final-browser/timings.json；假/真实后端各30个fresh context。真实p50/p95(ms)：首次264.1/333.7，50行49.0/82.9，缓存返回20.6/41.0；假服务280.6/437.9、37.7/97.6、18.4/45.0。均低于1000/500/100目标 |
| 视觉/安全 | regression桌面/390px截图已查看；键盘桶选择、文本注入不执行、无跨范围替换、未知schema拒绝；shell无外部资源请求 |
| 回退/构建 | final/rollback.json：源码检查点→独立恢复目录，使用固定同一依赖锁重建，与当前4个dist文件SHA逐字节一致；保留回执，不回滚后端 |
| 后端边界 | B005.1/source-manifest所有条目逐SHA一致，S0生成器核对通过；未改后端/共享接口 |

F006首次真实测试错误假定请求1在降序首页，等待超时；pass1失败留存，改点击实际第一条，pass2通过。性能第一次结果保留在performance，最终构建复测在final-browser。F005首次HMR干扰及旧门槛失败全部保留。

命令：apps/viewer下npm run generate/test/typecheck/lint/build及node scripts/check-build.mjs；浏览器使用项目Playwright CLI、--config apps/viewer/playwright.config.ts --workers 1 --reporter json。harness使用dev4174；生产UI/性能使用preview4175，显式TOKENSCOPE_EXTERNAL_PREVIEW=1、TOKENSCOPE_BROWSER_EXECUTABLE；真实场景TOKENSCOPE_REAL_BACKEND=1。具体argv、版本、时刻和失败trace在各browser-report。

未执行：后端主持最终J01–J06/R1/R2全服务验收、操作系统文件选择框人工确认、Docker/交付打包、V100生产CSV/性能。以上未计为通过。
