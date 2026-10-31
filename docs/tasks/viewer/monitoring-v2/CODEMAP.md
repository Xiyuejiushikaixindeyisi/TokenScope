# 正式前端源码与复现入口

## 页面与接口

| 入口 / 模块 | 职责 |
| --- | --- |
| apps/viewer/src/app.tsx | 默认进入V2；#/users、#/users/ranking、#/ma；既有V1路由保持 |
| features/v2/V2App.tsx | UI-02风格外壳、运行OpenAPI九操作2.0.0检查、服务身份变化后停止旧范围 |
| features/v2/UserMonitor.tsx | 用户运行新建/已知ID/本机最近/历史base绑定；S0六卡三图、请求、导出、信号 |
| features/v2/Ranking.tsx、numbers.ts | 后端全候选排行、20分页、300ms搜索、显式上下界、精确整数/分数、众数分页 |
| features/v2/TTFT.tsx | 条件弹窗二级情景登记、W显式输入、只读历史W+O、评估与失效、持久化原提交键 |
| features/v2/MAMonitor.tsx、MACharts.tsx | MA提交/恢复/目录、全UUID、逐行重试、配对Q/R、趋势/独立分布、质量 |
| api/v2/client.ts、generated | 用户2.0.0与MA1.0.0严格Schema验证；独立于S0；固定服务身份、no-store |
| state/v2-task.ts、v2-pool.ts | 60秒串行任务读取、终态停止/历史保留/原子切换；最多4快照并发、取消与迟到隔离 |
| storage/v2-records.ts | 服务×业务隔离的最近记录、任务意图、最后展示run元数据；不存CSV原文 |

表中源码路径均相对于apps/viewer/src，首行和脚本除外。生成入口`node apps/viewer/scripts/generate-v2.mjs`核验契约manifest后生成类型/Schema；不重新生成S0。

## 本地复现

仓库根目录执行，需既有后端虚拟环境与三模型编码资产、apps/viewer已锁定的Node依赖。测试输入为合成数据，不是生产测量。

```sh
.venv/bin/python apps/viewer/scripts/prepare-v2-fixtures.py
.venv/bin/tokenscope --input-root artifacts/validation/viewer/monitoring-v2/inputs --state-root artifacts/validation/viewer/monitoring-v2/repro-state --cpu-budget 2 serve --host 127.0.0.1 --port 8000
```

另一终端在apps/viewer运行`npm run dev -- --port 4173 --strictPort`；打开`http://127.0.0.1:4173/#/users`或`#/ma`。开发代理同源指向8000，包含/openapi.json。只服务本机回环，退出即结束本地验证，不是部署。

`npm run typecheck`、`npm run lint`、`npm test`、`npm run build`。正式测试脚本在tests/browser/v2-*.spec.ts；设置TOKENSCOPE_REAL_BACKEND=1、TOKENSCOPE_EXTERNAL_PREVIEW=1，按playwright.config.ts运行。Windows可用TOKENSCOPE_BROWSER_EXECUTABLE指定Edge绝对路径。首个全套真实执行须包含v2-ma.spec.ts，它建立后续视觉检查用的主MA运行；冷环境按先MA再全套的顺序运行。v2-acceptance亦会创建三模型用户运行。

本次实际验证复用了V1 F006已存在的model-1/2/3.csv，另增专属mv2-*合成MA文件；backend state独立为monitoring-v2/runtime。新复现脚本在自己的inputs目录生成等价目的的新样本，已有文件不覆盖；数据字节与本次证据不能混称相同。

未实现浏览器关闭后的后台监视；页面隐藏时定时器可能被浏览器延迟，重新可见时立即查询一次。没有用户/情景全服务目录接口，采用已知ID和本机最近记录；APPID下拉初次最多1000项，其他可通过排行或已知APPID打开。仅推送源码/文档，不上传数据、构建产物、镜像或交付包。
