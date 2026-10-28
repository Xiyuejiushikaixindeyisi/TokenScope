# 前端交给后端统一端到端验收

2026-10-27：前端0.1.0-f006，frontend_ready_for_joint；用户已询问能否开始端到端验收，可以开始。用户既定分工：后端Session 1统一最终真实J01–J06/R1/R2、Docker、镜像及代码交付；打包仍单独审批。前端配合修复，不替后端签署最终联合通过。

## 先读和固定身份

- docs/tasks/viewer/ENTRY.md → batches/F006/{RESULT,TESTS} → ACCEPTANCE_V1.md。
- 设计MONITORING_INTERACTION_V1.md；固定S0 contract1.0.0/view1（后端dev6/schema3）；接口未变。
- apps/viewer/README.md：构建和浏览器命令；apps/viewer/package-lock.json固定依赖，Node22.22.2/npm10.9.7。
- artifacts/validation/viewer/F006/source-manifest.json：自有源码/锁和dist SHA；backend-identity.json、input-manifest.json；后端B005.1源码清单逐SHA未变。
- 可使用apps/viewer/dist同源挂载。hash路由，无/api前缀；API根路径/monitoring、/analysis-runs、/analysis-submissions、/models。没有CDN运行依赖。

## 已通过，但不代替联合

142单元组件与类型/lint/build；20个不同browser场景按适用环境通过。真实dev6独立合成UI提交、SSE完成、三模型15组、明细/导出通过；每模型300行，每appid60行。生产构建假/真各30次，真实首组/50行/缓存返回p95=333.7/82.9/41.0ms。证据F006 TESTS。

R1：原key先持久、回执独立IDB、连接代次一次补查、≤4并发、终态单向合并、实例隔离，无定时轮询。
R2：64KiB、最多4在途（实际顺序1）；单记录1MiB；Worker原字节摘要；结束校验后close，失败abort；无能力≤16MiB验证后Blob。CSV只校验结构/条数。真实OPFS可写文件与受控选择器通过，不假称系统对话框人工确认。

用户明确批准的新前端内存门槛：64MiB优化目标、256MiB验收上限，256MiB/1GiB各3次与非线性增长检查。六次最大154.1MiB，4倍数据中位内存增量2.214倍。检测界线明确为<3倍（32MiB基线下限），不是常数空间数学证明。不要继续把前端旧64MiB硬门槛写作现行用户要求；后端自己的服务端RSS标准不由前端修改。

## 联合执行重点

请按后端B005.1 TESTS的J01–J06及R1/R2在确定版本的完整服务上重新执行：发布原子性/历史latest、断网重启/reset/订阅前终态/回执恢复、多标签和配额、不可变统计与各直方图/筛选一致、设置规则CAS/历史不变、导出截断/坏SHA/真实文件写入及内存。复用前端tests/browser和固定S0夹具，但后端须给最终联合报告，不把前端独立通过替代J证据。

本机开发预览：127.0.0.1:4175，代理独立后端8000；此为可关闭的本地服务，不是部署。真实联调用artifacts/validation/viewer/F006/inputs与state，禁止指向生产目录。tests/browser/integration.spec.ts需TOKENSCOPE_REAL_BACKEND=1，会创建合成任务；性能同样需显式开启。可重新创建独立状态实例，以避免冒用缓存身份。

## 回退和限制

检查点artifacts/validation/viewer/F006/rollback/source-checkpoint；recovered重建与当前dist字节一致，见final/rollback.json。只恢复前端自有源码/锁及静态资源，不回滚后端控制库，不删除回执库。没有Docker、镜像归档或代码交付包。

Linux缺libnspr4，实际浏览器证据来自Windows Edge156.0.4314.42/runner Node24.22.1；Windows RSS采样脚本在其他平台明确skip。secure context、目标浏览器OS保存对话框与V100现场、生产CSV均待联合/现场确认。DeepSeek默认思考、GLM CP映射/GF资产等原后端未决项仍保留；本机合成请求显式关闭思考不替代生产决定。
