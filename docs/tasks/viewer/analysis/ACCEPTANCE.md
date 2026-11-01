# 异常分析前端功能与视觉验收

> 最新状态：用户验收不通过，页面未能突出影响范围、预期提升、证据与修改方案。下文仅保留该版工程测试和历史入口，不代表交付验收通过；返工见[AR-0.1](REWORK_PLAN_AR01.md)。

2026-10-31。AF-1.0已按用户授权实施；AF000–AF005实现及批内验证完成，AF006本地联合与视觉自检完成后提交本页供用户验收。用户验收和独立复审尚未代签；暂不打包部署。

## 打开入口

- [正式前端本地验收入口](http://localhost:8140/#/analysis)：本地编译产物 + 真实诊断后端；不是新HTML DEMO。
- [Token报告](http://localhost:8140/#/analysis?direction=token_content)。应用选择a，模型GLM-5.2；内容来自本机6条合成请求，经实际分析与封存生成，不是生产数据。
- [获批UI-03](prototypes/analysis-ui03/tokenscope-analysis-ui03.html)保持原字节，供配色/布局对照。

默认完整报告task为73e1e977-84ad-4094-9fc9-8a91df746157；另有partial历史671a19f6-05e7-4ff5-8f07-a612406cf058。默认是按真实目录发布顺序读取，不把partial替换默认。ID仅为本次隔离验收状态，可重建，不作生产固定ID。

建议验收顺序：

1. 低命中列表：检查UI-03侧栏/顶栏/范围栏、两分区和双列卡片；展开5类探测器说明。查看已有收益及无收益差异，没有置信度/覆盖率或评估表单。
2. 打开一项详情：检查问题、建议、预期提升三段；完整请求A/B按需展开，技术信息折叠。返回后保留报告和卡片位置。
3. 切Token：展开4类检查，查看内容事实、单位、同请求多位置和完整原文；初始报告无量化结果如实说明，不让业务方填写参数。
4. 历史选择partial：明确部分结果，报告范围和完成时间一起切换；选择“查看最新”恢复默认。浏览历史/详情时新报告只提示，不强制跳转。
5. 刷新/浏览器后退、窄屏390px及1024px：验证报告对象恢复、单列/换行和原文局部滚动；存储禁用不阻断网络读取。
6. 返回监控：原来源链接明确是历史来源；“返回监控”进入监控选择页，不冒称旧run是当前最新运行。

## 已验证与限制

- 类型检查、lint、前端单元/组件全量回归、本地Vite构建；机器记录见[AF006验证目录](../../../../artifacts/validation/viewer/analysis/AF006)。
- 浏览器测试分真实后端与构造边界：两类真实报告/全文、实时SSE连接及21秒心跳零轮询、离线重连；构造场景覆盖读取失败保留旧内容/时间、首次partial无默认、>64KiB全文/大整数、通知到达固定详情直到显式查看最新；另有V1外壳和用户/MA入口兼容检查。
- 本轮修复：浏览器fetch接收者绑定、窄屏长位置文本溢出、范围时间start_ns/end_ns映射、完整原文摘要/关联核验，以及缓存禁用时默认参数求值问题。普通修复未改后端接口/范围。
- 视觉对照已在Windows Chrome实际截图检查，沿用UI-03作用域化CSS；真实报告数量、文本和可信时间不同，新增紧凑历史选择属于已批交互，不宣称像素相等。
- 未做生产代理/华为现场、全历史评估发现、大规模历史性能或多标签容量压测。后端能力边界保持；不把构造收益当实测。26项既有监控专用复审测试因其专用服务配置未启用而跳过，不计为本轮通过；本轮监控入口与既有单元回归另有实测。
- Vite给出主JS块超过500kB的体积提示，构建成功；没有新增依赖。本地验收不是镜像或交付包。

## 本地服务与重开

当前保留本地验收服务8140供用户打开。入口只服务项目内合成数据；启动脚本为[scripts/validation/analysis_frontend_server.py](../../../../scripts/validation/analysis_frontend_server.py)，既有状态存在时不重做分析，后台worker关闭。状态和日志/截图在artifacts/validation/viewer/analysis/AF006，本地缓存不删除服务器历史。

如会话进程退出，在项目根目录WSL中重开：

```bash
TOKENSCOPE_FRONTEND_ACCEPTANCE_PORT=8140 .venv/bin/python scripts/validation/analysis_frontend_server.py
```

前端改动后本地构建使用项目已有Node22.22.2及apps/viewer的npm run build；不需Docker。首次全新隔离状态将生成合成输入并运行本地分析，脚本不接触生产状态。

本页由用户确认功能与视觉后，再按[独立复审prompt](PROMPT_INDEPENDENT_REVIEW.md)转审查。未自动发送复审消息、未提交Git或打包部署。

截图对照：[UI-03基线](../../../../artifacts/validation/viewer/analysis/AF006/baseline-1440.png) · [正式页面1440px](../../../../artifacts/validation/viewer/analysis/AF006/actual-1440.png) · [正式页面390px](../../../../artifacts/validation/viewer/analysis/AF006/actual-390.png)。完整两类列表/详情及1024px截图见AF006/browser目录。最终本地验证：186项单元、8项编译产物浏览器测试通过；类型/lint/构建通过。
