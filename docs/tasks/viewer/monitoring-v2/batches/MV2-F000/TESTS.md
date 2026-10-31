# MV2-F000 TESTS

- WSL Node22.22.2：npm run typecheck、npm run lint通过。
- npm test：9文件144测试通过，日志见artifacts/validation/viewer/monitoring-v2/MV2-F000。
- Windows Edge、项目Playwright：monitoring.spec.ts/full-journey.spec.ts共3项通过（11.1s），含窄屏/详情/原子发布/缓存恢复。
- 两份后端manifest逐文件核对通过；13项输入身份见同目录baseline.json。
- 已核对实际user.py/ma.py路由及用户运行OpenAPI2.0.0交接；真实服务端到端留后续批次，不把本次模拟浏览器基线当联调。
