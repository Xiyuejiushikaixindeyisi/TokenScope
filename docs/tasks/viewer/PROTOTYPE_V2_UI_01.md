# V2监控与异常分析展示原型 UI-01

日期：2026-10-30。状态：用户2026-10-30表示“初版 DEMO 设计我很喜欢”；认可初版起点，后续优化HTML另行审批；不是正式前后端实现、API契约或开发batch授权。

## HTML文档入口

[UI-01自包含HTML](prototypes/tokenscope-v2-demo-ui01.html)是风格、配色和布局的正式阅读入口，已沉淀在docs，可直接本地打开；[摘要](prototypes/ui01-manifest.json)。不要求阅读生成.py或启动HTTP服务。原有artifacts副本保留，内容完全一致。

## 本版展示选择

依据[最新MaaS参考](../../architecture/MAAS_REFERENCE.md)，保留获批HTML的深色侧栏、浅灰画布、白色卡片、蓝/青色图表及紧凑范围栏。

- 用户侧：GB、appid×模型服务common_name；保留六项指标与三组直方图，新增TTFT命中需求面板。目标切换只选预置估计，不运行时延模型；缺少校准时显示无结果，不编造阈值。展示条件说明，不以理想命中率直接判断SLO达标。
- 搜索排行：独立的用户工作台入口，可搜索appid/应用名称/模型服务，筛选服务，按J/P/C/O、理想命中率、请求数、模板后长度众数区间升降序。当前排序值明确列出；点击一行进入对应监控范围。并列众数全部显示，区间排序采用最小起点，此交互规则尚待用户认可。
- 同事侧：GF、模型规格×UUID。选择规格即列出全部UUID；没有要求先选择一个UUID才能看到命中率。每行并列理想/真实命中、请求数、请求速率、输入Token速率、模型侧P90 TTFT与对照覆盖。展开趋势仍保留全部UUID。
- 同UUID内跨appid与P共享，不跨UUID混算。没有把用户侧各租户结果相加冒充集群理想值。构造样例包括真实命中缺值、真实高于窗口内理想且初态不同；不标为缓存损失。流量快照用5分钟均值仅为可视化示例，不决定后端刷新时效或时间字段。
- 异常分析直接复用获批报告第二稿的业务建议卡片、证据、建议、例子和收益；增加最近分析时间，保留appid×模型服务与两类报告。仅有原型已经构造的分析范围，不给其他模型补造分析结果。

所有新增数字、UUID、趋势和TTFT估计都是合成样例。MA数据独立构造，未与用户侧GB样例建立同一请求集合；不能跨页面相减解释。性能校准、GB/GF正文等价、实际命中范围、采集时间与分析证据能力仍由对应session收敛。本轮未修改原始证据、旧HTML、apps/viewer、后端源码、配置或S0。

## 文件与复现

原型统一位于[monitoring-v2](../../../artifacts/prototypes/monitoring-v2/)：build_demo.py只读获批with-reports-v2.html，注入prototype.css/js并生成自包含index.html；manifest.json固定来源及输出摘要。源码与交互入口见[CODEMAP](CODEMAP.md)。异常分析已整合在同一原型，未复制维护另一份analysis-v1界面。

原型生成：`python3 artifacts/prototypes/monitoring-v2/build_demo.py`。不调用正式前端构建、不更改锁文件、不安装依赖。原型直接本地打开docs内HTML；原HTTP预览已撤下，8000和已交付V1不受影响。

## 验证与问题记录

复用本机已有Node/Playwright和Edge，执行原型check_demo.cjs。最终结果和截图在[验证目录](../../../artifacts/validation/viewer/v2-ui-01/)，[checks.json](../../../artifacts/validation/viewer/v2-ui-01/checks.json)记录浏览器版本和网络请求。

通过项：六指标/41个直方图箱；TTFT预置目标/无校准展示；搜索/筛选/空结果；七指标双向排序与范围跳转；规格下全部4个UUID、真实缺值排序、趋势展开/收起及深链接刷新；分析卡片/详情/租户隔离/时间；1440px和390px布局、移动导航、局部表格滚动；零JS错误、无外部资源或后台变更请求。

初测发现并修复：更换导航后旧报警计数节点缺失；二次render查找已更名的按钮失败；读取旧直方图样例用了不存在的bins键，应为metrics。以上仅原型适配错误，最终完整检查通过；遗留failure.json/png为此前失败，不是最终状态。人工查看了用户页、MA表格/趋势、排行和窄屏截图。用户视觉评审尚未完成，不代签通过。

下一步由用户评审信息层级、MA对照密度、TTFT面板与搜索排行位置；相应新session随后明确数据与接口。没有创建或通知其他session，没有Docker/交付包构建。

## 2026-10-30 用户反馈与交接

用户认可初版设计，要求对应后端产品/设计基本固定、接口冻结后，由监控V2前端与异常分析前端两个新session继续。流程见[工作流](../../architecture/TASK_SESSION_WORKFLOW.md)，启动入口见[前端ENTRY](ENTRY.md)。本次反馈不等于尚未产出的交互方案/开发计划审批。

另存[自包含HTML交接版](prototypes/tokenscope-v2-demo-ui01.html)，与index.html字节一致；[摘要](prototypes/ui01-manifest.json)。HTML是研究风格、配色和布局的直接入口，无需先读生成.py及全部JS；不替代后端契约阅读。上述原有文件和修改均保留，本轮未重做界面。
