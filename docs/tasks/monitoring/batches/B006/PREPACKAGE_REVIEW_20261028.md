# Token监控打包前统一审查（2026-10-28）

结论：**当前源码候选审查通过，未发现阻断本候选的代码缺陷；可以进入具体交付方案与授权确认。** 不等于已经有可交付镜像，不关闭B006，不构成打包授权。容器及V100现场验收未执行。

审查会话：01a1800e-80b4-7400-a78b-a84f5b6e888d。用户本轮授权打包前审查与必要复测，未授权Docker构建、镜像save或代码包。F007人工验收采用前端2026-10-28记录的用户原话“F007 通过”，本会话不代签。

## 候选身份和审查范围

- HEAD：f92fc2870406ba6617a13066cd73f7420b8007c2，分支main；**HEAD加当前未提交工作树**才是本次候选，不可仅checkout HEAD复现F007。
- 后端0.1.0.dev6、前端0.1.0-f007、control schema3、view1、S0 1.0.0；源码/资源/配置/依赖锁/S0/模型文件实际SHA绑定在[candidate-manifest.json](../../../../../artifacts/reviews/prepackage-20261028/candidate-manifest.json)。这只是审查清单，不是代码交付包。
- F007 source-manifest全部70项一致；S0固定文件101项一致；encoding-assets.lock中三模型8个文件一致。旧joint清单144项中15项有差异：F007展示/版本/测试/资源替换、paths错误提示修复、Git整理时回退测试夹具路径迁移，均有来源，不存在未解释的运行源码漂移。核对见[identity-check.json](../../../../../artifacts/reviews/prepackage-20261028/identity-check.json)。
- 已逐项阅读F007六份批次文档、前端交互设计（含F007）、监控ENTRY/B005.1 PLAN/S0/TESTS/RESULT、JOINT_RESULT、B006 PLAN/DESIGN/TESTS、统一工作流、Git规则、README及V100报告/设计核对。代码重点为F007四个src差异及导出、整数、快照协调器、通知、回执、Worker、后端只读路由和相关测试；不是重新逐行审计所有历史算法或第三方仓库。
- 锁文件仅根版本号变化；API/store/cache/domain/Worker/export-controller与F007基线及旧联合清单一致。额外后端paths.py变更仅将缺失/非目录输入转为INVALID_INPUT_ROOT，未改变有效输入处理。

## 设计与代码核对

| 关注点 | 结论与证据 |
| --- | --- |
| 大整数、null、零分母 | compact使用BigInt四舍五入，精确值经formatInteger保留在title/精确总量/去向条；null显示破折号；P=0时去向宽度0。未将权威整数转Number；仅有限像素比例缩放 |
| 六卡/分布/质量 | H由去向条与精确值保留，J/P/C/O仍可查；直方图分箱及点击上下界未变，分位数读后端；文件和组范围/坏行归属分别保留 |
| 固定范围与版本 | 模型按钮仍沿用navigate/coordinator，appid仅选择目录组合；新结果整体替换、编辑/详情冻结与旧快照保留逻辑未改；浏览器覆盖切换、离线和不兼容schema |
| 通知/缓存/回执 | coordinator/publication/receipt未变，按实例/版本隔离、订阅终态与单向合并不变；本次144项回归及定向浏览器覆盖，复杂故障时序沿用旧联合证据 |
| 导出入口迁移 | 概览Exports移至标题details，以run+appid作为key；仍绑定snapshot，路由或范围卸载时abort。原控制器头失败取消body、reader/worker清理、校验后close、失败abort及16MiB降级保持；关闭details只折叠，不卸载或伪称完成 |
| GET不触发计算 | 后端展示GET调用views/既存投影；本次后端快照只读哨兵、冻结/ETag、操作/恢复/流关闭测试通过；真实浏览器用例记录零POST/PUT/DELETE |
| 视觉与人工 | 采用F007独立视觉证据和人工通过记录；本轮又查看实际1440/390截图，无发现新的遮挡/横向溢出。原型不改写，真实值不同不作逐像素相同声明 |

## 本轮实际复测

全部日志与独立重建资源在[本轮证据目录](../../../../../artifacts/reviews/prepackage-20261028)。没有覆盖F007或joint旧证据，没有替换共享apps/viewer/dist。

| 检查 | 实际结果 |
| --- | --- |
| WSL Node22.22.2：typecheck / lint | 均exit 0 |
| npm test | 144 passed（9文件） |
| 独立目录Vite重建 | exit 0，输出到审查目录dist；4个文件与F007正式dist逐字节一致 |
| pytest定向 | 27 passed：test_paths、test_views、test_view_operations、test_view_recovery、test_viewer_host；包括INVALID_INPUT_ROOT、GET哨兵、迁移旧源码回退、流关闭和同源装配；1条既存Starlette/httpx弃用警告 |
| 隔离浏览器 | 8 passed：shell/monitoring/full-journey/operations/export-fixture；4189为本轮独立Vite，写操作由fixture截获，未连接共享8000写操作 |
| 真实服务只读浏览器 | 1 passed：8000三模型精确值、跨appid、三视口、历史/质量/详情/设置读取、真实NDJSON校验下载；零页面错误、零写请求 |
| 最终身份 | 审查冻结文件无漂移；8000首页与正式dist一致；独立重建一致，见final-identity-check.json |

Python命令、cwd、退出码和耗时见checks.json；浏览器确切spec、输出与结果见browser.log和real-browser.log。浏览器为已安装Windows Edge，runner为Windows项目Playwright；沿用F007既定方式。没有重跑全套联合、30,168条负载、1GiB压力或现场测试：计量、S0、缓存/通知/导出核心代码保持，F007纯展示变更由上述相关复测覆盖，旧压力报告仍只证明其绑定版本和环境。

## 发现与处置

| ID | 发现 | 处置 |
| --- | --- | --- |
| PKG-R01 | B006 DESIGN/TESTS仍写浏览器≤64MiB验收，与已批准前端9.4/B005.1 R2及旧联合结果冲突 | 本轮修正文档为64MiB优化、256MiB上限，256MiB/1GiB各3次、中位增量比<3（小基线32MiB）；后端RSS≤64MiB独立。不改变批准门槛、不重写历史测试 |
| PKG-R02 | B006唯一负责人仍指向Session 1，未反映用户本次指派 | 在B006 PLAN/DESIGN/TESTS同步本轮审查/交付职责，原联合报告归属不变 |
| PKG-H01 | joint*.spec保留旧UI选择器 | 已知复现维护事项，本轮不用旧选择器跑整套联合；未删断言。后续容器复用前须适配metadata/精确值并保留原身份/数值/恢复/导出断言 |
| PKG-H02 | 旧env/docker、build_monitoring.py仅backend_only准备 | 仍不可直接发布。后续具体方案须纳入前端资源、完整白名单、锁定基础镜像与离线资产后取得明确授权；本轮未启用旧脚本 |

无业务修复，未修改前后端源码/测试/S0。已修正文档与本次报告、清单共同组成审查输出；本结论不是对未知未来Dockerfile的预先批准。

## 后续交付范围、现场边界和回退

待单独确认的完整发布单元：当前源码候选+前端离线资源+Python锁定依赖/Tokenizer资产的linux/amd64 CPU镜像+Compose/配置+华为执行prompt+manifest。基础镜像digest、最终镜像ID、包SHA、端口/挂载/目标目录尚未固定，不在此伪造。构建前再次核对候选摘要与实际批准范围；任何源码变化须复审受影响部分。

V100事实来自2026-10-26报告：CentOS7、内核3.10、x86_64、Docker26.1.4、Compose2.27.1、40可调度逻辑CPU；采用CPU路径，初始预算8、单任务运行，32GiB是拟议容器限额。GPU驱动不匹配不要求本项目修驱动；不得将V100误判为Ascend。旧内核兼容、实际配额/磁盘、现场浏览器安全上下文及大文件保存能力、生产每文件<7200s均须现场实测。生产CSV留现场。

保留原未决：DeepSeek缺省思考、GLM CP映射、GF资产等价、V100真实负载性能；本机显式思考选项与合成数据不代替生产确认。≤16MiB降级不代表完整大导出现场门槛通过。

源码回退按F007 RESULT限定文件/hunk处理，先保留共享修改；不能全局reset。未来镜像回退必须使用配套前后端/schema，保留新状态与回执；控制库序号回退须隔离新实例。仅源码分支经检查合并main并显式push；包体留artifacts/releases本地，含产物backup不push、不merge main。

停止点：审查完成，未构建Docker/镜像/代码交付包，未提交/合并/push、未新建分支或跨会话发消息。共享8000服务保持运行；本轮4189测试服务独立清理。B006容器/现场门槛保持pending。
