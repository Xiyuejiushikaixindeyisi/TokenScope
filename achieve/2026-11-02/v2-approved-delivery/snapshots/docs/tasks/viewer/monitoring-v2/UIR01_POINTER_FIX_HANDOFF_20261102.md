# UIR-01 宽窗口鼠标读数修复交接（2026-11-02）

执行角色：前端唯一维护方，实际session 01a19111-344a-75c1-84e0-14db8be08f4f。依据审查线转达的用户授权与[单项prompt](../../../../prompts/sessions/FRONTEND_UIR01_POINTER_FIX_20261102.md)，只修鼠标坐标换算；保持已批准展示、UIR-02和现有业务。P0修复与本轮自测完成，交镜像打包与审查 session 01a1800e-80b4-7400-a78b-a84f5b6e888d 重新独立复审，前端编辑窗口释放。

**本报告不是独立复审通过或用户视觉认可。未提交、合并、推送、构建Docker或生成交付包。** 原[c2交接](APPROVED_UI_REVIEW_FIX_HANDOFF_20261102.md)和[独立失败报告](../../delivery/APPROVED_UI_FIXES_INDEPENDENT_REVIEW_20261102.md)及证据不覆盖。

## 1. 候选与增量

候选 viewer-uir01-pointer-fix-20261102-c1；HEAD 9f2a3e60394327e4e6bdc41bd688497ddef21dd7 加前序未提交恢复和本轮3项增量，不能以HEAD单独认定候选。新证据根 artifacts/validation/viewer/uir01-pointer-fix-20261102。完整源码、样式、锁、契约、资产与HTTP摘要：[identity-final.json](../../../../artifacts/validation/viewer/uir01-pointer-fix-20261102/identity-final.json)；开工身份：[identity-start.json](../../../../artifacts/validation/viewer/uir01-pointer-fix-20261102/identity-start.json)。本轮只改一个业务源码文件、新增两个测试文件，其他源码及他人未提交修改保持。

| 文件 | SHA256 |
| --- | --- |
| [apps/viewer/src/features/requests/Requests.tsx](../../../../apps/viewer/src/features/requests/Requests.tsx) | 9380f329aeedfaec51ecf8d23f3b5c86d33b52960f41ad23e2c68306cddbe87b |
| [apps/viewer/tests/browser/rank-pointer.spec.ts](../../../../apps/viewer/tests/browser/rank-pointer.spec.ts) | 38e1ebd8ab7dc3ec195d32cc4b8f0d7d2dd936494525f2cbad73f7e242193d43 |
| [apps/viewer/tests/component/rank-pointer.test.tsx](../../../../apps/viewer/tests/component/rank-pointer.test.tsx) | 8d6d5cf2fd8f116f4c62cc900d7206c0c72245a5a1f1d176e1ad8704c5127ed9 |

## 2. 根因与修复

c2按SVG元素边框宽度映射到400宽viewBox；1920宽三列图因既有220px高度和默认等比居中出现左右留白，错误映射把首点选成第四条。两指标Token值重复会掩盖错选，重算则直接把418读成162。

[Requests.tsx:35](../../../../apps/viewer/src/features/requests/Requests.tsx#L35)新增 rankPointerIndex：每次pointer事件取得SVG当前getScreenCTM，将clientX/clientY用逆矩阵转换到真实SVG用户坐标，才按既有绘图范围51–384选择当前段最近索引。不缓存窗口几何，滚动、等比缩放、留白和resize均由当前变换处理。矩阵缺失、求逆异常或转换后非有限坐标返回null、维持已有选点；空段不处理，单点和边界索引保留。

未增加固定偏移、未拉伸SVG、未改宽度/高度/CSS、未隐藏鼠标能力；坐标/颜色/精确整数/绝对排名、每段1000条、键盘、请求页辅助图与既有业务不改。没有后端、API、锁文件或模型变更。

## 3. 真实鼠标与负向回归

新增 [rank-pointer.spec.ts](../../../../apps/viewer/tests/browser/rank-pointer.spec.ts) 使用本轮新生成的真实API行作为期望，取实际circle的boundingBox中心作为鼠标目标；不使用业务实现的坐标公式生成期望。逐点核对排名、hash、source_record_index和完整Token整数，既不能只比可能重复的Token，也不根据SVG title反推期望。

四组场景：用户监控三图、S0分布深链三图、请求明细辅助图三个排序指标、1005条运行的第1001–1005条三图。每组按1440→390→1920→1440连续resize，对三个指标首/中/尾点检查，含滚动，共144检查。1920首点截图及实际API/指针坐标/读数完整保留；每次后端请求均是只读GET。

权威结果：[pointer-summary.json](../../../../artifacts/validation/viewer/uir01-pointer-fix-20261102/pointer-summary.json)，144项全部匹配。c2负向对照用同一新后端和原c2静态资源替换，仅替换浏览器静态响应、不并行启动旧服务；用户页和S0分布在1920首点按预期失败，记录在 [c2-negative.log](../../../../artifacts/validation/viewer/uir01-pointer-fix-20261102/c2-negative.log)、c2-negative-results 的trace/行数据，摘要中保留两个真实错读。这是有效失败证据，未修改旧审查记录。

[restart-browser-results/rank-pointer-pointer-uses--5a406-wport-resize-second-segment/second-segment-first-1920-2.png](../../../../artifacts/validation/viewer/uir01-pointer-fix-20261102/restart-browser-results/rank-pointer-pointer-uses--5a406-wport-resize-second-segment/second-segment-first-1920-2.png)

[restart-browser-results/rank-pointer-pointer-uses--105aa-across-viewport-resize-user/user-first-1920-2.png](../../../../artifacts/validation/viewer/uir01-pointer-fix-20261102/restart-browser-results/rank-pointer-pointer-uses--105aa-across-viewport-resize-user/user-first-1920-2.png)

[restart-browser-results/rank-pointer-pointer-uses--1aa31-ss-viewport-resize-requests/requests-first-1920-2.png](../../../../artifacts/validation/viewer/uir01-pointer-fix-20261102/restart-browser-results/rank-pointer-pointer-uses--1aa31-ss-viewport-resize-requests/requests-first-1920-2.png)

[restart-browser-results/rank-pointer-pointer-uses--d83d5-ross-viewport-resize-legacy/legacy-first-1920-2.png](../../../../artifacts/validation/viewer/uir01-pointer-fix-20261102/restart-browser-results/rank-pointer-pointer-uses--d83d5-ross-viewport-resize-legacy/legacy-first-1920-2.png)


图示确认：新候选1920用户重算首点为排名#1、synthetic-0、源记录1、418 Token；第二段首点为排名#1001、源记录1001、162 Token。已实际查看截图。完整40组UI-02/UI-04与候选对照仍在 [visual-final/summary.json](../../../../artifacts/validation/viewer/uir01-pointer-fix-20261102/visual-final/summary.json)，1440/390无脚本错误、横向溢出或非GET写请求；本轮CSS/布局未改，额外1920图用于验证留白状态下鼠标读数，不构成新设计。

## 4. 本轮验证与失败复测

| 检查 | 新候选结果 | 证据 |
| --- | --- | --- |
| typecheck/lint/build | 通过；独立新dist四资源 | [checks.log](../../../../artifacts/validation/viewer/uir01-pointer-fix-20261102/checks.log)、[final-test-checks.log](../../../../artifacts/validation/viewer/uir01-pointer-fix-20261102/final-test-checks.log) |
| 单元/组件 | 26文件226项通过，新增4项坐标/防护测试 | [checks-final.log](../../../../artifacts/validation/viewer/uir01-pointer-fix-20261102/checks-final.log) |
| 监控/MA/TTFT/取消/导出/四入口 | 42通过 | [monitoring.log](../../../../artifacts/validation/viewer/uir01-pointer-fix-20261102/monitoring.log) |
| 分析/SSE/cache/历史/partial/返回 | 18通过 | [analysis.log](../../../../artifacts/validation/viewer/uir01-pointer-fix-20261102/analysis.log) |
| FS-01两种来源/固定run | 3通过 | [source.log](../../../../artifacts/validation/viewer/uir01-pointer-fix-20261102/source.log) |
| 真实搜索与联合 | 8通过 | [joint.log](../../../../artifacts/validation/viewer/uir01-pointer-fix-20261102/joint.log) |
| 前轮UIR-01/02行为 | 10通过 | [pointer.log](../../../../artifacts/validation/viewer/uir01-pointer-fix-20261102/pointer.log) |
| 新鼠标场景 | 最终4通过，144检查 | [pointer-final.log](../../../../artifacts/validation/viewer/uir01-pointer-fix-20261102/pointer-final.log)、[pointer-summary.json](../../../../artifacts/validation/viewer/uir01-pointer-fix-20261102/pointer-summary.json) |
| 真实合成API | 15基础范围、搜索、诊断、1005请求新运行通过 | [base-acceptance.json](../../../../artifacts/validation/viewer/uir01-pointer-fix-20261102/base-acceptance.json)、[search-api.log](../../../../artifacts/validation/viewer/uir01-pointer-fix-20261102/search-api.log)、[fixture-config/actual-http.json](../../../../artifacts/validation/viewer/uir01-pointer-fix-20261102/fixture-config/actual-http.json)、[rank-segment-fixture.json](../../../../artifacts/validation/viewer/uir01-pointer-fix-20261102/rank-segment-fixture.json) |
| 同版本重启 | 118地址SHA一致，service_instance及业务表保持，GET未新增业务 | [restart-result.json](../../../../artifacts/validation/viewer/uir01-pointer-fix-20261102/restart-result.json) |
| 重启后新浏览器 | 来源3＋鼠标4，共7通过，不累加不同用例数 | [restart-browser.log](../../../../artifacts/validation/viewer/uir01-pointer-fix-20261102/restart-browser.log) |

不同浏览器用例共85（原81＋新4），没有借用前序候选通过数。鼠标/分页期望均来自真实后端；原UIR大整数/错误恢复用例仍有受控网络注入，边界与真实业务验证分开表述。

失败和复测原文保留：
1. 新防护测试初用component目录的.test.ts，现有Vitest只发现.test.tsx；首次仍为原222通过，不宣称新增已执行。改为正确扩展名后26文件226通过。
2. 鼠标首轮14用例中13通过、请求页1超时；getByLabel exact未匹配该嵌套控件。按浏览器可访问树改用combobox角色+精准“排序”名称，数据/坐标断言原封保留，最终四组全部通过；首次trace仍在pointer-results。
3. 原c2负向两项按预期失败；不把其计入新候选功能失败或通过数。
4. 最后只增加首点截图取证，未改业务；重启后四场景/来源再次通过，最终typecheck/lint通过。

既有大chunk警告保留；合成1005请求不是15万规模性能或华为现场验证。工程/视觉对照自测不代用户签字。

## 5. 原18项与已通过能力保持

| 编号 | 保持情况 |
| --- | --- |
| A01 | 设置/旧深链仍处于统一AppShell，skip不改路由 |
| A02 | 四入口名称/顺序/激活态保持 |
| A03 | SVG图标、208px侧栏、分组/间距/配色未改 |
| A04 | 窄屏四入口、键盘跳转保持 |
| U01 | 六卡、Token去向、TTFT及三图统计保持 |
| U02 | 真实运行/历史/任务/情景保持，排行恢复修复不动 |
| U03 | 仅修实际鼠标坐标；轴/颜色/刻度/读数/箱宽/分位数/众数/分页保留 |
| U04 | 信号、请求明细、导出/取消/完整性校验保留 |
| R01 | 20条排行、防抖、过滤、排序与真实搜索不动 |
| R02 | 固定run/revision与返回，已修follow保留排行路径不动 |
| M01 | 全UUID、摘要、蓝青配对条不动 |
| M02 | 真实目录规格、质量/展开/历史不动 |
| M03 | 12桶/整小时均值、0/null、蓝青刻度不动 |
| M04 | 双页签/分布/200K尾桶不动 |
| D01 | UI-04卡片/详情、缓存/SSE/历史/partial旧内容保护不动 |
| D02 | L4/L5各一卡、每类≤3例、去重与返回不动 |
| D03 | Token T2–T4，未恢复T1 |
| D04 | 分析同框架与FS-01精确run不动 |

UI-02/UI-04原HTML及前两轮交接摘要保持；c5固定历史run竞争修复不动。301项后端/锁/契约/S0/模型资产对开工摘要一致，详见manifest；不将设计目标或前轮验收当本轮能力事实。

## 6. 环境身份与独立复审交回

开工实际重新盘点 [processes-before.json](../../../../artifacts/validation/viewer/uir01-pointer-fix-20261102/processes-before.json)、[windows-before.json](../../../../artifacts/validation/viewer/uir01-pointer-fix-20261102/windows-before.json)：无旧TokenScope服务/worker/测试容器/daemon，4191/4193/8016/4175释放。审查方已停旧候选，本线未误停其他项目。新建空state、独立新dist、全新浏览器context和新合成运行，未拷贝旧state；[cold-identity.json](../../../../artifacts/validation/viewer/uir01-pointer-fix-20261102/cold-identity.json)记录空目录和HTTP身份。旧包/state/原始证据全部保留。

唯一当前服务 [http://localhost:4191/#/users](http://localhost:4191/#/users)；PID 3033544，实例 3a65b353-268b-4d85-8c6b-2c8c34a8ce60。完整argv/env/cwd在 [server-restarted.json](../../../../artifacts/validation/viewer/uir01-pointer-fix-20261102/server-restarted.json)，当前清理清单 [cleanup-final.json](../../../../artifacts/validation/viewer/uir01-pointer-fix-20261102/cleanup-final.json)；初始2972001在同版本恢复测试中正常退出、端口释放后才重启，见 [restart-old-stopped.json](../../../../artifacts/validation/viewer/uir01-pointer-fix-20261102/restart-old-stopped.json)。

| 实际HTTP资源 | SHA256 |
| --- | --- |
| index.html | e4c7e4e0969e52c39bbdc78bb6c48641742d0d75cc79605ef9aed2ae21fa46d6 |
| assets/index-BN_hqTE_.js | 1d18c395fb5aca91bc77b469e58376a087a204f46c786d5bf9502c3ad6e55072 |
| assets/export-validator-rZ4O78aZ.js | e52838c80a214d465b29b1e6049fabe887e80d8077fc5ce121061c8f109e9d41 |
| assets/index-BxqENh7v.css | 7de15a1ce92dc92d4d93a96c70425c1ea22663c5c4653c98cb4d9122ef0254a5 |

复现同版本恢复（先核实server-restarted的PID/完整命令/cwd，TERM后确认退出和端口释放，不能盲目照抄旧PID）：

    cd /home/zhangxiyue/TokenScope
    O=/home/zhangxiyue/TokenScope/artifacts/validation/viewer/uir01-pointer-fix-20261102
    TOKENSCOPE_RECOMMENDATION_BUNDLE="$O/fixture-config/synthetic-recipes.json" .venv/bin/python -m tokenscope.cli --input-root "$O/inputs" --state-root "$O/state" --asset-root /home/zhangxiyue/TokenScope --cpu-budget 2 serve --host 127.0.0.1 --port 4191 --viewer-root "$O/dist"

新测试入口 apps/viewer/tests/browser/rank-pointer.spec.ts。设TOKENSCOPE_SOURCE_LINK_FIXTURE为本轮source-link-fixture.json、TOKENSCOPE_EXTERNAL_PREVIEW=1、TOKENSCOPE_TEST_BASE_URL=http://localhost:4191及Windows Chrome路径。1005运行由同目录rank-segment-fixture.json读取，其他scope取base-acceptance.json。TOKENSCOPE_POINTER_C2=1仅供旧静态资源负向对照；正常验证必须不设该变量。测试记录鼠标目标来自circle屏幕边界中心，期望来自实时API。所有命令脚本及fixture/输入摘要均在本证据目录。

交回复审：请镜像打包与审查先核对并停止本候选、确认进程退出/端口释放，再用自己的独立新空state、新dist和新浏览器冷启动复审。不要直接把本现场当独立通过。前端编辑窗口释放，发现问题由审查方协调归口；本轮无已知未修复功能阻断，但UIR-01最终关闭仍待独立复审，不代签用户视觉认可。

本轮无Git提交/合并/push、Docker、交付包或现场部署；复审通过不自动获得上述授权。
