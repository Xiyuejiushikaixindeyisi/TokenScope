# F007 实现结果与后续统一审查入口

2026-10-28；状态：**closed / 用户人工验收通过**。版本0.1.0-f007，前端实现、回归、独立视觉核对及用户人工验收完成；打包前统一审查pending，未构建Docker/镜像/交付包。

## 人工验收

直接打开 http://127.0.0.1:8000/#/overview 并刷新。已验证HTTP主页与当前dist一致；旧4175预览不作为验收身份。请检查左侧导航、紧凑筛选与元信息、六卡三列、去向条、直方图、历史/详情/导出。用户审批原话：**“F007 通过”**；日期：**2026-10-28（北京时间）**。此审批关闭F007，不代表打包前统一审查已完成或已授权打包。

## 实际改动和设计对照

- C1/C2：src/app.tsx、styles/base.css还原DEMO骨架/控件/导航，集中模型/appid/时间，元信息细条和按需详情。
- C3/C4：features/overview/Overview.tsx六卡+Token去向，BigInt紧凑数字并保留精确总量；大结果面板移除，既有Exports组件移至标题菜单。
- C5：features/distributions/Distributions.tsx调整图表呈现、分位数/众数位置和显示网格，数据/bin选择算法不变；统一表单和表格样式。
- C6：component/monitoring增加六卡和精确值检查；browser/full-journey仅适配身份定位；monitoring增加长文本/空率/窄屏；visual.spec新增现有框架内的只读真实视觉验收。package及lock仅更新根版本号，无新增依赖/业务组件/类。
- 源码相对批前HEAD f92fc2870406ba6617a13066cd73f7420b8007c2；本批尚未提交，不能只checkout该HEAD得到F007。当前工作树及逐文件摘要为交接内容。不要丢弃其他session改动。

## 验证

144项单元组件、typecheck/lint/build、8个隔离浏览器场景通过；真实服务视觉用例通过，含三模型、三视口、历史/质量/请求详情、设置读取、NDJSON校验下载，零写请求。后续补跨appid检查见TESTS。原型未改、数据/API/store/cache/worker/export控制器摘要保持，功能和视觉分别记录。用户已于2026-10-28明确通过F007；本次人工结论与旧联合证据分别记录。

[PLAN](PLAN.md) · [TESTS](TESTS.md) · [ISSUES](ISSUES.md) · [独立视觉验收](VISUAL_ACCEPTANCE.md)。证据根artifacts/validation/viewer/F007；source-manifest.json固定源码/测试/构建/原型/S0。最新构建index-CoRZ0mJY.js、index-DGDynNnk.css。

## 回退

本批开始前apps/viewer源码为上述HEAD且无已有改动，baseline/source-manifest.json可核验。对本批修改的4个src文件、package/package-lock及3个现有测试文件按HEAD逐文件或逐hunk恢复；仅移除本批新增visual.spec.ts（确认之后无他人编辑），不要全局reset。重新本地构建并核对资源；8000静态服务读取apps/viewer/dist，无需重置后端或删除缓存/回执。原dist依赖版本未改，恢复前端不会改计量/运行数据。恢复前保留F007差异和证据。

## 后续审查和打包

用户倾向另建session承担统一审查和打包；也可由后端执行。本会话未创建/发送消息。直接可复制prompt：[SESSION_FRONTEND_REVIEW_AND_PACKAGING](../../../../../prompts/sessions/SESSION_FRONTEND_REVIEW_AND_PACKAGING.md)。

新session先核实用户人工通过记录及工作树，审查PLAN/交互设计、上述源码差异、TESTS/ISSUES/VISUAL_ACCEPTANCE/本结果，再读后端ENTRY/B005.1/S0/JOINT_RESULT和B006当前入口。旧联合脚本中的七卡/“当前范围”定位需按新UI适配，不删业务断言；脚本由后端维护，本批未修改或声称复跑。

本批纯展示不要求第二次完整联合review；后端或新session的打包前统一审查仍须执行，必要复测由其明确。Docker、镜像、代码包必须获得单独明确授权，人工UI通过不能自动视为授权。代码/镜像包不得上传GitHub，遵循项目交付及Git约定。审查结果与打包结果由执行session登记，本会话不代签。
