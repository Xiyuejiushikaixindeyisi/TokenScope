# MA 聚合 OpenAPI 握手修正 · 2026-11-03

状态：本项源码修正及单元/组件自测完成，真实服务浏览器握手待总设计师独立冷启动验证；不代表 MA 整体或监控前端最终通过。

HEAD：`d55df94b6e58117a698dbd14667b7836e67cd50f`，修改未提交。由总设计师提前集成检查发现：standalone OpenAPI 的 Submit/ErrorEnvelope 引用与 create_app 聚合后的 Submit-Output/模块限定名不同，按组件名直接比较误拒绝语义相同的接口。

## 修正与完整性

- `apps/viewer/src/api/v2/openapi-equivalence.ts`：递归解析本地 schemas 引用，规范对象键顺序，比较完整展开结构；仅消除引用名差别，所有其他字段（含 title、required、additionalProperties、约束、参数及全部错误响应）保留，数组顺序也保留。
- `apps/viewer/src/api/v2/client.ts`：在指定 availability 路由的 GET operation 上比较冻结契约与实时 `/openapi.json` 的解析结果。成功握手缓存、失败可重读，身份/取消逻辑不变。
- 对循环、缺失、外部引用及带 sibling 的 `$ref` 明确 fail closed；深度100和展开节点50000上限，避免无界递归。当前契约无需递归或 sibling 支持，未来引入应单独评审，不能静默忽略。
- 未修改后端或冻结业务契约，无需另固化依赖运行时命名的签名。

## 验证及证据

`tests/fixtures/ma-availability-runtime.openapi.json` 从审查方真实 create_app 产物 `artifacts/reviews/hv2-repair-20261103/full-runtime-openapi.json` 提取 availability 完整路由及全部传递引用组件；源文件 SHA256 写在 fixture.provenance，组件未改写。该 fixture 不依赖忽略 Git 的 artifacts 路径，冷检出可运行。

新增7项：真实聚合文档通过；字段类型、additionalProperties约束、503响应、路由及路径参数漂移分别拒绝，且不发业务读取；循环/缺失/外部/sibling引用拒绝。加上既有MA回归，定点34项通过（25单元+9组件）。全量 npm test 为28文件260项通过；npm run typecheck、npm run lint、npm run build均exit0。Vite原有大chunk提示仍在。不同集合重叠，不相加。

命令在 apps/viewer 执行，WSL Node22.22.2/npm10.9.7；全量命令、退出码和日志：`artifacts/validation/viewer/HV2-MA-FE-20261103/aggregate-handshake/{checks.json,typecheck.log,lint.log,test.log,build.log}`。本项文件摘要见同目录 `candidate.json`。

验证层级：实际聚合文档是后端 create_app 生成；单元测试通过 fetch 替身将文档交给真实 V2Client。**本次未启动监听服务，未执行真实HTTP浏览器握手或Docker。** 已有 `tests/browser/hv2-ma-availability.spec.ts` 首例在真实服务读取13 UUID并等待页面 availability 展示，其客户端必须先通过实时 `/openapi.json` 握手；由总设计师在唯一干净环境执行，并保存实际 OpenAPI、浏览器和HTTP证据，不能用本次单测替代。

仅本项补充修正；用户2.1接入及完整MA交接仍按当前开发任务继续，不以历史RV2交接恢复旧Git/打包流程。未改共享CURRENT/SESSIONS、未commit/push、未构建镜像/部署/打包。
