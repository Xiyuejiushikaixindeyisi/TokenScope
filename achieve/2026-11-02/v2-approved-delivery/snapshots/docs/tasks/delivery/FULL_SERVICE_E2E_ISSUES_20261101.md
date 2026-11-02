# 完整服务合成验收问题与复验

总负责 `01a1800e-80b4-7400-a78b-a84f5b6e888d`，2026-11-01。对应[验收矩阵](FULL_SERVICE_SYNTHETIC_E2E_20261101.md)。原证据均位于项目 `artifacts/reviews/full-service-synthetic-20261101/`，不改写失败日志或冻结发布。

## FS-01：异常报告的用户监控来源链接参数不一致（P1）

发现版本：源码 `45d9285210dc0b9edeb86c599c7b6bcd942f60b5`，镜像 `sha256:483db762852b38ef54559cff1bb23ef668ea9296a055ce02aac44a809b427ce5`。新隔离实例 `f99cb514-ba26-4846-9c1e-6382f0b655f1`，当时端口18062；真实新任务 `1a0727b1-5d69-4413-a24e-92c02d4afd5e`，来源用户运行 `ur-e409fc1a87ef4bcebcee168fcf20d51b`、APPID `search-long`。服务停止后此地址不保证可用，原状态保留。

复现：冷浏览器打开上述 user_v2 来源异常报告，点击“查看原报告监控来源”。实际跳到 `#/users?appid=search-long&user_run_id=...`，页面“展示运行 —”。`SourceLink.tsx` 写 `user_run_id`，而 `UserMonitor.tsx` 读取 `run`。已有最近记录时可能错误回落到另一运行，故不能把 URL 变化或HTTP200当成功。

预期：打开报告所绑定的精确用户运行与APPID，六卡、来源base/common_name/model一致；刷新仍保持此历史身份。保持跳转前核对、取消/迟到保护，以及 base 来源跳转 `#/overview` 的行为。

原证据：`additional-analysis.log`、`additional-analysis.json`、`additional-analysis-results/additional-analysis-real-d-ab548-igates-to-original-user-run/trace.zip`、`browser-suite/additional-analysis.spec.ts`。该用例使用真实HTTP和发布dist，没有模拟来源响应。

总负责已依据用户明确的直接协调授权通知异常前端维护会话 `01a19111-344a-75c1-84e0-14db8be08f4f`，对方已确认接收。修复限来源组件和针对性回归，禁止改冻结契约/旧包；候选dist独立输出。状态：候选修复已独立复验关闭；原冻结交付仍不含修复，不能判完整通过。最终候选源码/资源身份和复验追加于下方。

## 验证辅助修正，未判为业务缺陷

原失败证据保留，修正只影响本轮辅助脚本或fixture映射，不删业务断言：

- CSV默认字段大小不足：原生成器含固定超长样本；搜索使用独立小CSV，三模型原样本仍由真实基础验收覆盖。
- 浏览器复制用例的模块解析、工作目录和fixture路径：修正到实际Node模块和项目路径；前端单元测试须在 `apps/viewer` 工作目录运行，最终195项通过。
- 导出取消第一次对整站限速阻塞了新范围读取；第二次CDP规则未实际延迟，原导出先完成。最终只延迟真实后端导出响应，范围切换后实际请求中止且无下载。此项明确属于受控网络延迟，不称真实慢网流式吞吐测试。
- 新报告旧样式差异链接曾重复拼接 `diff:`；改为新任务实际opaque ID，原详情/返回/刷新断言全部保留。
- 三个合成建议标题相同：改用真实 recommendation ID 定位，分别保留零/未知/负收益及精确数值断言。
- MA独立oracle初稿未扣除冻结配置中启用的MTP一块，已按公开算法修正预期，实际缓存数据未改。此样本P=764，实际输入中H=640，理想单次重复H=512；实际高于理想允许且应如实展示。
- 配置快照取值路径应为S0 `provenance.settings`，不是MA `runtime.settings`；初次脚本finally已恢复设置，最终核对历史revision1、候选revision2、恢复revision3及384→512缓存差值。
- 取消的未发布诊断不属于已发布报告目录；以terminal端点验证interrupted、report_published=false，并验证目录确实不包含它，显式retry另生成任务。未放宽“不发布半成品”的断言。
- 诊断路由要求选择的原因同时启用Token分析；L2/L3辅助提交初稿关闭Token得到422。更正为已冻结路由规则后执行真实新任务，不改契约。

这些修正不消除FS-01，二者分别记录。

## FS-01最终关闭记录

归口交接：[SourceLink修复](../viewer/analysis/SOURCE_LINK_FIX_20261101.md)。总负责验证单行参数更正、203项单元组件（含新增8项）、71项完整候选容器浏览器全部通过；冷浏览器、其他最近运行、刷新、base来源、三字段身份不符及迟到保护均覆盖。原真实失败保持，复验通过记录为candidate-all-browser.json/log和candidate-unit.log。候选仅通过只读dist挂载验证，旧镜像/代码包未改；关闭的是源码候选缺陷，不是完成新版本交付。

恢复成功后用户页及隐藏排行各有filter-meta，新增测试精确定位含“展示运行”的条目，保留实际run、APPID及刷新断言。此选择器修正与原URL键错误分开，不删除原失败证据。
