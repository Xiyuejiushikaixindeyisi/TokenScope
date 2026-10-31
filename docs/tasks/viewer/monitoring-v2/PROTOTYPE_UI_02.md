# 监控V2 UI-02 HTML评审稿

TTFT接入统一状态：**代码完成，性能校准待完成**。本轮用户已明确：缺少参数不展示具体命中率，不默认等待为0。三模型最小数据与batch/chunk/等待口径见[校准清单](../../monitoring/v2-user/PERFORMANCE_CALIBRATION.md)。UI-02原配色/布局认可与此前原型检查保留；此前自动显示的合成参数/截图不能当当前默认行为或真实校准证据。
日期：2026-10-30。维护会话：`01a18c49-d9b4-7a33-8c04-e5a72adfcc24`。状态：**UI-02已获用户认可，作为正式交互视觉基线**。本轮只制作独立展示原型，未开发正式前端。

用户授权：“这两个调整我认可，其他建议也按你说的做。请基于现有DEMO生成新的HTML供我评审，保持原有配色和布局，另存到docs，不覆盖UI-01，暂不开发正式代码。”其中两项为TTFT右栏改P90长度、MA展开区采用“流量趋势／长度分布”页签。

## 交付与打开方式

- [UI-02自包含HTML](prototypes/tokenscope-v2-demo-ui02.html)：用桌面浏览器直接打开，无需安装、联网或启动后端；默认进入用户监控，侧栏切换搜索排行和MA。
- [生成身份及依据摘要](prototypes/ui02-manifest.json)：UI-02 SHA256为`b50b78412fb0a47f034b0c3320879ffb4e795131921bd64a1eaddc8cad80d2d5`。
- [UI-01原稿](../prototypes/tokenscope-v2-demo-ui01.html)未覆盖，摘要保持`28518db9eae0f1f2d8921c8a02e6bc66e3d20485804508073026101b0cb916ee`。

直接继承UI-01内联基础样式、页面骨架和既有用户六卡/三图、明细及分析入口；新增样式仅用于已认可模块。深色侧栏、浅灰背景、白色卡片、蓝/青配色、用户三栏TTFT、排行筛选栏加表格、MA全部UUID表加下方两列画像保持。手机沿用窄屏堆叠和表格内部滚动。

## 本稿落实的变化

| 区域 | 本稿展示 | 对应建议 |
| --- | --- | --- |
| 用户范围 | 服务、APPID、固定快照范围与质量说明；切换组使TTFT旧值失效 | U1 |
| TTFT三栏 | 左侧目标秒数及≤/<；条件弹窗设置等待、情景与来源；中间显式评估/待重评/不可用原因；右侧模板后P90及有效请求数 | U2–U5 |
| 搜索排行 | 单服务单运行；APPID大小写敏感字面搜索；四项排序、升降序、折叠上下界条件；匹配总数及分页 | R1–R3、R5–R6 |
| 典型重算长度 | C众数箱内均值、代表箱及占比；并列峰弹窗；1K/2K/5K开放等宽箱，超过200K仍分箱 | R4 |
| MA范围和总览 | now统计1小时/pre预热1小时；三个摘要位改为UUID数、统计时长、预热时长；全部UUID稳定顺序，保留仅pre实例 | M1–M2、M9 |
| MA表格 | 配对理想/真实蓝青条；请求/Token两项覆盖；整小时请求速率、实际未命中速率与总量；输入计量差异及预热条件 | M3–M5、M8 |
| MA展开区 | “流量趋势／长度分布”切换；12个五分钟桶与整小时均值；生产输入/实际未命中两张独立分布，样本、分位数、众数、200K尾桶及零未命中数 | M6–M7 |
| 质量/状态 | 文件级质量入口；预热冲突、无有效预热、真实缺值、编码失败、仅pre；空文件/不可归属/处理中/失败的可切换评审样例 | M8、M10 |

继承的分析页用于保持原导航和视觉上下文，本轮没有重新设计其内容。

## 建议评审路径

1. 用户监控：查看TTFT三栏；修改目标后观察“待重新评估”，再点击评估；打开“设置评估条件”。T=4/W=3、≤与<分别展示100%参考和无预算。选择长APPID及“实测依据样式”可查看超适用范围。
2. 搜索与排行：查看折叠条件、四项排序、第二页长APPID；搜索`bimodal`后打开并列众数明细，搜索`long-context`查看200K以外等宽箱。进入“查看监控”再返回，筛选保持。
3. MA：五个UUID直接可见。第一行展开后切换趋势/分布，改箱宽和纵轴；第二行包含覆盖不足、真实高于理想和输入计量不一致；第三行包含缺值；第四行预热顺序冲突；第五行仅pre。GLM规格另有原文编码不可用例。“结果样例”检查空文件、不可归属、处理中和失败。

这些控制只服务于离线评审，不是正式运行状态操作或任务提交功能。

## 依据及样例限制

生成期间用户后端更新为U000–U005闭环、契约1.0.1。本线已复核[契约说明](../../../contracts/user-monitoring-v2/README.md)及[已实现API](../../monitoring/v2-user/IMPLEMENTED_API.md)：新版本勘误为输入长度、整数筛选、错误/分页/身份约束，四指标、TTFT公式和展示语义不变。用户设计补记及新manifest身份已记入UI-02 manifest。MA依据仍为[设计v1.0](../../monitoring/v2-ma/DESIGN.md)与[契约1.0.0](../../../contracts/ma-monitoring-v2/CONTRACT.md)。本线未重新执行后端验收。

原UI-01用户数据保留，并增加明确标识的双峰与长APPID边界组；MA为按已确认指标含义构造的确定性展示夹具。离线生成器预先产出统计和TTFT参考表，浏览器仅选择预置结果、筛选排序和绘图，不执行编码、回放或性能模型。它们是**展示投影，不是严格DTO回包或真实接口联调证据**。

- 所有数据、性能参数和“实测依据样式”均为合成，不代表真实校准。人工假设/来源样式可区分，0%/100%及无预算等均有明确说明。
- 离线TTFT只预置T=1–60整数秒、W=0–10整数秒；这是本原型交互范围，不能据此限制正式接口允许的非负精确小数和有效目标。
- 排行离线模拟全候选过滤、排序后分页；原型每页4条便于评审。未验证真实revision分页、超大精确整数、并发/恢复等正式接入行为。
- 用户运行目录和情景列表仍无对应GET列表操作。本稿显示固定样例，不暗示自动读取全服务历史。MA摘要不添加契约未提供的规格级统计，文件质量不按UUID虚构归属。
- MA请求速率按request_time分桶，未称真实到达QPS；未命中Token/s未称GPU吞吐。0/null、配对/独立集合、有限预热和计量不一致分开说明。

## 验证结果与复现

[检查结果](../../../../artifacts/validation/viewer/monitoring-v2/UI-02/checks.json)绑定当前HTML摘要。使用Edge/Playwright临时本机回环渲染，仅提供新UI-02文件，测试结束即关闭服务。正式交付仍是docs内HTML，没有启动常驻预览或后端。

- 桌面1440×1000、窄屏390×844检查通过；浏览器无脚本错误、外部资源或API请求。
- 已检查TTFT条件失效及边界、排行四排序/分页/筛选/双峰/超200K/返回保留、MA全UUID/页签/三箱宽/覆盖与缺值/质量入口，以及继承分析页导航。
- 截图人工复核了用户页、排行、TTFT弹窗、MA总表、趋势和分布、窄屏详情；已修正输入框样式、比较符宽度、双图对齐及计数轴刻度。窄屏表格在区域内滚动，无整页横向溢出。
- 首次检查脚本误等待其他路由中隐藏的TTFT面板“可见”，修正为“已挂载”后通过；保留`failure.json/png`作为初次脚本失败证据，最终以`checks.json`为准。
- [文件核对](../../../../artifacts/validation/viewer/monitoring-v2/UI-02/integrity-checks.json)：四份本线文档的79个本地链接（加入本核对链接前）可定位，9项契约文件摘要及生成文件摘要匹配，UI-01的两段内联样式均原样保留。共享CURRENT/SESSIONS有其他会话同期编辑，不把其尚未写出的链接和行尾空白算作本线全文件通过，也未代为修改。

截图：[用户页](../../../../artifacts/validation/viewer/monitoring-v2/UI-02/users-desktop.png) · [排行](../../../../artifacts/validation/viewer/monitoring-v2/UI-02/ranking-desktop.png) · [MA总览](../../../../artifacts/validation/viewer/monitoring-v2/UI-02/ma-desktop.png) · [趋势详情](../../../../artifacts/validation/viewer/monitoring-v2/UI-02/ma-trend-desktop-detail.png) · [分布详情](../../../../artifacts/validation/viewer/monitoring-v2/UI-02/ma-distribution-desktop-detail.png) · [窄屏详情](../../../../artifacts/validation/viewer/monitoring-v2/UI-02/ma-distribution-mobile-detail.png)。

原型维护入口：[生成器](../../../../artifacts/prototypes/monitoring-v2/ui02/build_demo.py)、[展示脚本](../../../../artifacts/prototypes/monitoring-v2/ui02/prototype.js)、[新增样式](../../../../artifacts/prototypes/monitoring-v2/ui02/prototype.css)、[浏览器检查](../../../../artifacts/prototypes/monitoring-v2/ui02/check_demo.cjs)。均在独立ui02目录，不运行原UI-01生成器，不占用apps/viewer或后端源码。

下一步等待本HTML评审反馈。HTML认可后再按既定流程讨论正式交互和开发方案；本次认可建议及生成HTML的授权不等于已经批准正式编码、部署或打包。

2026-10-30用户明确认可UI-02，后续见[正式交互方案](INTERACTION_V2.md)。原HTML及生成时manifest保留身份，待评审措辞为生成时点记录。

## 2026-10-30 缺参保护更新
按用户直接要求，保留布局/配色，默认等待改为空、情景改为缺参；空等待先判空再转换，不能当0；三模型默认不展示具体命中率。明确选择完整合成情景后才可显式查看未校准参考。后端38项定点测试及浏览器5组检查通过；证据artifacts/validation/monitoring/ttft-calibration-20261030。本轮未开发正式前端，原始HTML/manifest在该证据目录按字节保存，旧截图只证明更新前原型。
