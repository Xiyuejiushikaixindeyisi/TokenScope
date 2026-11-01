# LH008 执行记录

2026-10-31，closed。diagnostics-http-1已经装配真实服务/Token插件/原worker Dispatcher；app与work-once仅新增注册，已释放共享编辑窗口。实际端点和Schema见IMPLEMENTED_API、docs/contracts/diagnostics-http-1。

提供方真实HTTP提交→worker→报告→完整两请求→显式full→只读行证据通过；实例错配、未发布、外部成员、分页越界、decimal wire错误拒绝。GET不计算。全范围优化卡片过滤与独立差异/Token成果分别可读。

Token消费方提出G1完整原文、G2T3显式授权和G3组合缺口，已逐项补齐：原fragment成员完整原文且>64KiB；Token纯authorizations从真实T3观察/单元构造候选，公共保存授权并worker再次prepare；同scope已存Plan组合独立回放，包含Token时direction=combined且不套门槛。任何冲突无after，原单项结果保留。未修改Token私有源码。

验证：最初HTTP1 passed（8.55s），真实跨方向+冲突1 passed（15.16s）；新增完整HTTP/Token授权/组合/manifest受影响4 passed（34.97s）。两线此前核心162 passed（114.69s）；消费者TA005独立87单元+7集成+公共组合1共95 passed（53.39s），其RESULT已签收G1–G3并closed。统计有交叉，不相加虚构独立测试数。

故障修复：派生评价视图含四个明确字段，消费方按四字段剥离后验证原冻结Schema，未放宽任意extra；manifest_ref修为实际相对任务路径并验证逐行读取。完整原文须报告成员和原scope/摘要核验，不接受任意base/run/record请求。

未执行前端、容器、远端、镜像构建、打包部署。资源校准和最终回归/源码身份归LH009，Token本线TA006不由公共代签。
