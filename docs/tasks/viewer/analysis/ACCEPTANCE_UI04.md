# UI-04 正式前端返工验收

2026-11-01：用户不认可本页旧双实例入口。当前请使用[RV1统一入口与修复验收](ACCEPTANCE_RV1.md)，4191读取同一appid两方向，4193已改跳转。下文作为此前实现/数据/测试的历史记录保留，不再用于启动两套独立验收环境。

2026-10-31，`viewer-analysis-ui04-local-1`。ARF000–004本地实现与工程验证完成，等待用户功能/视觉验收；没有代签用户验收或独立复审。原AF006验收不通过的记录保留。

## 直接打开

- [低命中率：L1优化建议、L4局部差异](http://localhost:4191/#/analysis?binding=76ef771bdc2ebabad5d823af9bf04e42ded8c6c5599f9f39e8783938323dcd28&direction=low_hit&mode=history&task=84b66f17-4362-4f88-adda-65ac7763277e)。应用`a`，6条请求，1张L1建议和1张L4差异卡；L1命中率0%→49.04%，不显示Token变化。
- [低命中率：L5表示差异](http://localhost:4191/#/analysis?binding=e230d3086085d829eb8bd056079350a78562f29813c4736e72b24a8ccf173749&direction=low_hit&mode=history&task=bdc6e4da-f17c-4e33-b85a-2b12b1096473)。应用`representation`；差异详情至多3例，不设收益门槛。
- [Token：T2–T4具体建议与量化结果](http://localhost:4193/#/analysis?binding=f860b372ec762939acba36cbffbfebab82e97836215f52df683a96900b0e2256&direction=token_content&mode=history&task=716967b3-3e69-4f58-82e8-37f5e7715b8d)。应用`synthetic-orders`，2条请求，4张建议卡：保留订单号/状态、替换重复工具文档、删除重复普通消息、保留最近1份工具结果。每卡分别展示影响数和输入/计算Token前后变化。

这些是本机Vite开发服务读取后端封存报告，不是部署或新HTML。两个端口使用独立验证状态；跨方向切换只显示该状态已有报告，不把两份数据拼接为同一生产实例。页面访问仅GET，不提交分析或评估。旧8140入口属于AF006，不作为本轮验收入口。

## 视觉与内容

沿用[批准的UI-04](prototypes/analysis-ui04/tokenscope-analysis-ui04.html)配色及布局，HTML未改，SHA256 `779e6665985fe02e6df9e7d0483ef8111a16a49c2b61fdb27aacbef58d624f5f`。深蓝208px侧栏、浅灰背景、白卡、蓝色导航及绿色收益；低命中单方案占整行，内部两列；Token/差异两列，390px窄屏单列。

卡片按具体问题、影响请求、预期变化、修改方案和局部证据组织。详情优先展示收益及改法，再看局部例子；两个请求的原文差异与同一请求修改前后明确区分。最多3例，首例展开、其余按需展开；长字段局部内容在320px区域内滚动。该适配保留原配色布局，不读取完整请求，不恢复身份JSON或单项评估操作。探测器说明默认折叠；新Token仅T2–T4。

需要人工重点确认：重点信息是否足够直观、卡片/详情与UI-04视觉是否一致、局部证据是否便于理解修改动作、返回卡片是否方便。用户尚未确认本版正式页面通过。

截图：[低命中列表](../../../../artifacts/validation/viewer/analysis/ARF004/browser/low-list-1440.png) · [低命中详情](../../../../artifacts/validation/viewer/analysis/ARF004/browser/low-detail-1440.png) · [Token列表](../../../../artifacts/validation/viewer/analysis/ARF004/browser/token-list-1440.png) · [Token详情](../../../../artifacts/validation/viewer/analysis/ARF004/browser/token-detail-0.png) · [Token窄屏](../../../../artifacts/validation/viewer/analysis/ARF004/browser/token-detail-390.png)。这些是正式React页面实际截图，不是DEMO。

## 数据身份与真实能力边界

| 读取对象 | 当前身份 | 依据 |
| --- | --- | --- |
| 公共/低命中实现 | arpc-local-3，AR-L5承接AR-L4/ARPC006 | [AR-L5交接](../../prefix-analysis/FRONTEND_COPY_HANDOFF_ARL5.md) |
| Token自动链路 | arta-local-1，token-content-2，仅T2–T4 | [自动适配器交接](../../length-analysis/AUTO_ADAPTER_HANDOFF.md) |
| Token可读业务样例 | art4-readable-local-1 | [AR-T4样例](../../length-analysis/FRONTEND_READABILITY_ART4.md) |
| 对外只读推荐接口 | analysis-recommendations-1 | [public-views](../../../contracts/analysis-recommendations-1/public-views.json) |
| 报告发现与通知 | diagnostics-discovery-1；旧公共协议保持 | [通知交接](../../prefix-analysis/NOTIFICATION_HANDOFF.md) |

本机输入和业务策略均为构造样例，模型编码与离线回放真实执行；不是生产数据或生产收益。Token生产recipe默认仍为空；业务策略需在后端配置/确认，前端不提供授权表单，也不会凭空估算缺失收益。各方案独立对照，收益不可相加。L2/L3有后端Plan映射验证，本次可视入口未新增其真实业务报告，不冒称生产验收。

低命中状态实例`0d1ae778-d813-4e2e-990a-98cd077d67e8`；Token实例`2fceceeb-ea9d-4d67-9c63-da25cca35c1e`。URL固定各自task，刷新/通知不会切走当前历史详情。

## 工程验证

- `npm run typecheck`、`npm run lint`通过；`npm test`共21文件190项通过，3.22秒。
- Chrome浏览器8个独立场景通过，41.1秒：实际低命中/Token报告、只读GET与局部证据、21秒无任务轮询、断网重连、监控路由兼容；受控传输覆盖历史读取失败、首次partial无默认、证据独立重试、完成通知保留当前详情。后4项是边界模拟，不称真实后台发布事件。
- 最后布局/折叠调整后重跑2个UI-04场景通过；接收AR-L5文案新报告后再重跑低命中场景1项通过，7.9秒。不将重跑计入独立用例总数。
- 桌面1440px与窄屏390px截图已阅读，指标、局部证据、折叠与布局可见；窄屏无横向页面溢出。`git diff --check -- apps/viewer`通过。
- 旧报告未生成新建议、零/负收益、输入减少而计算增加、缺依据不补0、大整数与原文保真、不同实例/task/scope隔离、分页及例子所属关系由前端单元/组件验证覆盖。

源码168文件摘要、相对AR02的14项新增/修改及1项删除、12张截图摘要和验证结果见[本地结果清单](../../../../artifacts/validation/viewer/analysis/ARF004/result.json)。测试计数来自实际工具输出，未冒称留存完整原始执行日志。[批次记录](FRONTEND_REWORK_EXECUTION_ARF.md)包含模块映射。

## 职责与后续

前端会话只实现`apps/viewer`及自身测试/文档；后端由低命中率会话`01a18be2-7112-7aa2-919b-5137d1f1b1ad`、Token会话`01a18fcd-0464-7cf1-b435-4f394bd33e66`分别实施。本轮发现局部定位及业务文案问题后，均发送prompt由对应后端修复，未代写后端。Token实施本来已开始，没有另起后端任务。

下一步是用户功能/视觉验收，之后进行独立复审及源码收口。生产策略资料与生产数据验收另列，不阻止当前前端视觉评审。未构建前端发布包、Docker镜像或交付包，未部署、未执行Git发布。

## 本机入口恢复

2026-11-01 13:40（北京时间）恢复记录：用户反馈4191无法访问；检查时4191/4193/8011/8013均无监听进程，封存报告仍在。已将同一输入/state对应的4个验收服务以独立后台进程启动，退出启动命令后继续运行；未配置系统开机自启。Windows端两个页面HTTP 200，目录实例与上表一致；Chrome实际加载低命中2卡、Token4卡及局部证据，无页面脚本错误。未修改业务源码、重算报告或打包部署。PID/启动命令/日志、HTTP与浏览器记录位于`artifacts/validation/viewer/analysis/preview-recovery-20261101/`。独立启动脚本只在4个端口均空闲时运行，避免覆盖已有服务。

当前低命中服务8011、Vite4191；Token服务8013、Vite4193。低命中8011已切换至AR-L5新状态，AR-L4封存数据保持。各命令在独立终端中运行；已有端口正在服务时不重复启动。

```bash
# 项目根目录：低命中只读消费
.venv/bin/tokenscope --input-root artifacts/validation/arl5-20261031-01/test_frontend_low_hit_and_diff0/inputs --state-root artifacts/validation/arl5-20261031-01/test_frontend_low_hit_and_diff0/state serve --host 127.0.0.1 --port 8011
# 项目根目录：Token只读消费
.venv/bin/tokenscope --input-root artifacts/validation/art4-readable-20261031-01/test_chinese_recipes_actual_se0/inputs --state-root artifacts/validation/art4-readable-20261031-01/test_chinese_recipes_actual_se0/state serve --host 127.0.0.1 --port 8013
# apps/viewer目录，两个独立终端
TOKENSCOPE_BACKEND_URL=http://127.0.0.1:8011 npm run dev -- --host 127.0.0.1 --port 4191 --strictPort
TOKENSCOPE_BACKEND_URL=http://127.0.0.1:8013 npm run dev -- --host 127.0.0.1 --port 4193 --strictPort
```

浏览器复现（Windows PowerShell，`apps/viewer`目录）：

```powershell
$env:TOKENSCOPE_BROWSER_EXECUTABLE='C:/Program Files/Google/Chrome/Application/chrome.exe'
$env:TOKENSCOPE_EXTERNAL_PREVIEW='1'
$env:TOKENSCOPE_ANALYSIS_REAL='1'
$env:TOKENSCOPE_TEST_BASE_URL='http://localhost:4191'
$env:TOKENSCOPE_TOKEN_TEST_URL='http://localhost:4193'
node node_modules/@playwright/test/cli.js test tests/browser/analysis.spec.ts tests/browser/analysis-boundaries.spec.ts --workers=1 --reporter=line
```
