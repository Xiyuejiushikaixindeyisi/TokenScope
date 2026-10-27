# TokenScope viewer 0.1.0-f006

Token监控正式前端候选，按S0 1.0.0/view1实现；审批、测试层级与后端联合交接见 docs/tasks/viewer/ENTRY.md。无内置演示指标，不接入诊断分析器。

## 开发与构建

使用Node22.22.2/npm10.9.7（.nvmrc、package.json精确固定），在apps/viewer：

```sh
npm ci
npm run generate
npm run typecheck
npm run lint
npm test
npm run build
node scripts/check-build.mjs
TOKENSCOPE_BACKEND_URL=http://127.0.0.1:8000 npm run dev
```

生成器核对后端S0_MANIFEST所有文件摘要；不能绕过失败或直接修改生成DTO/Schema。生产dist含本地JS/CSS/Worker，无CDN或字体网络依赖。静态资源与/monitoring、/analysis-runs、/analysis-submissions、/models根API同源，路由为hash；后端负责最终挂载、联合验收及另获授权后的打包。

## 浏览器验证

`npm run test:browser`默认启动Vite开发服务器，以便缓存/导出harness直接测试真实源模块。先确保系统具备Playwright浏览器依赖；本机WSL缺libnspr4，未擅自安装系统包，实际改用已安装Windows Edge156.0.4314.42。

Windows runner使用Node24.22.1（测试工具执行环境，与构建Node不同）、本项目node_modules/@playwright/test/cli.js，配置playwright.config.ts。设置TOKENSCOPE_BROWSER_EXECUTABLE为msedge.exe，TOKENSCOPE_EXTERNAL_PREVIEW=1，TOKENSCOPE_TEST_BASE_URL指定已启动的本地前端。harness用dev；生产UI/性能用`npm run preview -- --port 4175 --strictPort`。各测试按--workers 1执行，性能测试期间固定源码，不执行generate或触发HMR。

integration.spec.ts与真实后端性能场景需显式TOKENSCOPE_REAL_BACKEND=1，只连接独立合成状态。所需inputs/model-1/2/3.csv生成说明及数据摘要在F006交接；它会提交三模型任务，不能连接生产状态。未开启时明确skip，不代表通过。

export.spec.ts用持久化临时浏览器配置、真实OPFS可写文件，选择器受控；256MiB/1GiB各3次，Windows WorkingSet64记录浏览器进程集合峰值，64MiB优化/256MiB验收。临时浏览器配置由Playwright清理，证据存项目。此脚本的整体RSS测量当前只支持Windows，其他平台不能据空采样宣称通过。固定字节夹具和真实NDJSON导出另测。

## 运行与回退

SSE只通知、读取完整固定run后原子替换；不周期轮询指标。32MiB内存软预算由快照24MiB和读取页8MiB构成；IndexedDB快照64MiB软预算，回执使用独立数据库。配额失败降级并提示，禁止随缓存清理删除回执。

完整输出无原始请求正文或Token IDs。流式文件写入要求浏览器能力及安全上下文；否则仅≤16MiB校验后Blob下载。单记录1MiB，超过明确失败；取消或失败abort，不能把不完整文件提示为成功。操作系统保存对话框仍需最终目标环境人工/受控确认。

源码恢复检查点：artifacts/validation/viewer/F006/rollback/source-checkpoint；恢复构建与当前dist逐字节一致见final/rollback.json。停止前端服务后恢复自有源码/锁并重建，不回滚后端库、不删除独立回执。此为本地研发检查点，不是代码交付归档。

Docker、镜像归档和代码交付包须用户另行同意；前端本地build不等于发布包。


2026-10-27联合修正：后端已支持serve --viewer-root apps/viewer/dist正式同源运行；export-controller响应头失败取消未读body。联合候选身份/结果由docs/tasks/monitoring/JOINT_RESULT_V1.md维护，不能只凭旧f006 manifest识别；S0不变。joint*.spec.ts为后端主持的隔离验收测试，涉及任务提交、受控故障及专用服务重启，禁止连接生产状态。
