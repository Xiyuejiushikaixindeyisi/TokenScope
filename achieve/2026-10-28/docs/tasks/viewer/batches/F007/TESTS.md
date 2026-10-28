# F007 验证与测试记录

状态：前端验证通过；2026-10-28用户人工验收通过。F007实际144项单元/组件与8个隔离浏览器场景通过，真实服务只读视觉检查通过。旧联合结果单独保留。

## 计划矩阵

| ID | 检查 | 通过标准 | 当前结果 |
| --- | --- | --- | --- |
| T01 | 范围与身份检查 | 固定HEAD/原型/S0/锁文件/改动清单；后端契约、数据层、worker无非预期变化 | pass，证据见下 |
| T02 | 静态/单元/组件/构建 | typecheck、lint、全部现有单元组件、build成功；不以删断言换通过 | pass，证据见下 |
| T03 | 布局相关浏览器回归 | shell/monitoring/full-journey/operations与受影响导出入口场景通过；按各用例既有假服务/隔离测试环境运行 | pass，证据见下 |
| T04 | 状态保真 | appid×模型切换、历史返回、完整结果切换、详情/编辑冻结、断网保留旧结果、缓存切页和无指标轮询保持原行为 | pass，证据见下 |
| T05 | 信息保真 | 六卡+去向条不丢H；精确整数/null/0；组与文件时间、配置生效范围、质量作用域可辨；导出绑定同一快照 | pass，证据见下 |
| T06 | 操作与可访问性 | tabs/表单label、键盘焦点、详情开关、导出/取消入口可用；表单提交不因布局改动重复触发 | pass，证据见下 |
| T07 | 真实数据只读核对 | 实际完整服务三模型/不同appid和历史可用范围；数值、时间与同一快照相符；无修改共享数据 | pass，证据见下 |
| V01–V06 | 独立视觉验收 | 详见VISUAL_ACCEPTANCE；不由T01–T07代替 | pass，证据见下 |

## 执行入口

在 apps/viewer 使用项目既定 Node22.22.2/npm10.9.7及锁定依赖：

```text
npm run typecheck
npm run lint
npm test
npm run build
npm run test:browser -- tests/browser/shell.spec.ts tests/browser/monitoring.spec.ts tests/browser/full-journey.spec.ts tests/browser/operations.spec.ts
```

执行前阅读上述用例的fixture/服务配置；环境使用现有TOKENSCOPE_TEST_BASE_URL、TOKENSCOPE_EXTERNAL_PREVIEW、TOKENSCOPE_BROWSER_EXECUTABLE约定，确切命令与适用环境填入实际记录。会提交/改设置的自动化只对隔离测试服务运行，不指向用户8000共享状态。导出入口验证复用已有export相关用例与有限样本，不因纯CSS变更重跑1GiB压力；若实际代码触及导出控制器/缓冲或数据逻辑，先判定超出本批范围并讨论，不能沿用旧证据声称新行为通过。

追加测试只用于新呈现行为、真实回归风险和视觉验收，使用已有框架。文字/结构变化可更新选择器，但不得放宽快照身份、精度、缓存、CAS、回执、导出正确性断言。

## 实际执行记录（待编码后填写）

每次记录日期、源码/构建身份、命令、环境、通过/失败数、日志路径；失败关联ISSUES并记录复测。只读真实服务核对和隔离假服务测试分别标识。文档链接检查不属于应用测试通过。

## 实际执行（2026-10-27）

- Node22.22.2/npm10.9.7（WSL）执行typecheck、lint、npm test、build：通过，144项。Windows Node24.22.1 + Edge156.0.4314.42执行Playwright；现有锁定版本无新依赖。
- 最终8浏览器场景：shell 1、monitoring 2（含长appid/来源、null命中率、390px）、full-journey 1、operations 3、export-fixture 1，全部通过。地址4177，写操作全部被测试fixture截获，未向8000提交任务或改设置。
- visual.spec.ts在8000执行真实服务只读验证：三模型精确总量、历史入口、元信息、请求详情、设置读取、NDJSON真实下载（SHA/记录数校验成功）；1440×900、1280×800、390×844与原型截图对照，无横向溢出、脚本异常和POST/PUT/DELETE。后续补充跨appid切换，记录在visual-scope-check。
- 静态/单元日志：artifacts/validation/viewer/F007/functional/{typecheck-final,lint-final,unit-final,build-final}.log；浏览器日志browser-final.log，视觉visual-acceptance.log/visual-scope-check.log。
- browser-final运行参数：TOKENSCOPE_TEST_BASE_URL=http://127.0.0.1:4177，TOKENSCOPE_EXTERNAL_PREVIEW=1，TOKENSCOPE_BROWSER_EXECUTABLE=C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe；Playwright CLI指定--config=apps/viewer/playwright.config.ts，五个上述spec和独立输出目录。
- 真实视觉运行参数相同，BASE_URL换8000，TOKENSCOPE_VISUAL_REAL=1，spec为visual.spec.ts。测试内/__f007-reference由Playwright本地拦截提供原HTML，不新增后端路由。
- 前端API/store/cache/domain/worker/export-controller逐文件摘要与本批baseline一致；锁文件只有根版本号改为0.1.0-f007。HTTP当前index与dist一致，证据functional/http-build-check.json。未重跑1GiB压力或后端全套联合。
- 初轮两个失败及修复见ISSUES，未删除失败证据。最后CSS表单调整后重建并重新视觉回归；业务代码未再变化。

本批截图使用原型原始合成数据与真实服务已有合成CSV结果，数据不相同，因此只对照结构、样式与信息层级，不宣称逐像素相同。用户于2026-10-28回复“F007 通过”，详见VISUAL_ACCEPTANCE。本轮只登记审批，不重复运行测试。
