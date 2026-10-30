# MA监控后端：前端接收入口

2026-10-30。后端检查点 **ma-backend-local-1**，设计1.0、MA协议1.0.0、MA控制库schema1。M000–M005本机后端已闭环；本次仅源码与文档同步，不改变V1发布身份，不部署/打包。

## 接收顺序

1. [已实现API](IMPLEMENTED_API.md)与[协议正文](../../../contracts/ma-monitoring-v2/CONTRACT.md)：以实现及实际路由为准，不把历史设计OpenAPI骨架当当前能力。
2. [严格Schema](../../../contracts/ma-monitoring-v2/schema.json)、[实际路由OpenAPI](../../../contracts/ma-monitoring-v2/design.openapi.json)、[协议摘要](../../../contracts/ma-monitoring-v2/manifest.json)。Schema与OpenAPI由后端生成，前端不自行改契约。
3. [16项合成样例](../../../contracts/ma-monitoring-v2/frontend.examples.json)：包含5类实例快照、完整回执、质量分页、目录和错误。来源为真实本地MA管线；running/failed/interrupted回执标明为合成状态。样例不是生产证据或前端验收。
4. [设计符合性](batches/M005/DESIGN_CHECK.md)、[最终验收](batches/M005/RESULT.md)、[代码地图](CODEMAP.md)。视觉仍从[获批UI-01](../../viewer/PROTOTYPE_V2_UI_01.md)及[原型](../../viewer/prototypes/tokenscope-v2-demo-ui01.html)起步，按既有前端阶段流程推进。

## 展示必须保留的口径

| 接口/字段 | 展示含义与约束 |
| --- | --- |
| model_standard_name / instance_uuid | GF模型规格×生产实例；规格下列出全部UUID，同UUID跨appid/P共享，不跨UUID合并命中分子分母 |
| binding.pre_start / now_start / now_end | 连续两个一小时半开窗口；pre从空缓存预热，只有now进入画像，每次运行独立 |
| paired_real / paired_ideal | 概览并排对照使用同一Q，各用自己的Token分母；real/ideal是各自独立有效集合，必须保留覆盖说明 |
| mismatched_input_count / limitations | 本地与生产输入计量不一致时不可把差值解释为缓存损失；长度一致也不证明Token IDs等价 |
| real.totals.uncached_tokens | 生产输入减实际cached；与用户线理想重算C分开，不套用其排行语义 |
| bins / hour | request_time轴的12个五分钟桶与整小时平均；是记录时间请求速率/未命中输入量速率，不称GF到达率或计算吞吐 |
| pressure.uncached_tokens=null / "0" | 有请求但真实字段全部无效为null；合法空桶为0，不互相替换 |
| input_histograms / uncached_histograms | 两张独立分布，各自样本数；1K/2K/5K全部预计算，默认5K；200K开放尾桶不截断实际长度 |
| ideal_status | available、no_valid_prewarm、warmup_order_conflict、empty_now须区别展示；冲突保留真实观测，不制造理想0% |
| empty_scope_reason / file_quality | 空文件与全不可归属不同；仅pre UUID仍可见；坏JSON不抹除可用生产字段 |
| runtime | 配置/资产/编码身份及模式来源；DeepSeek现场假设、GF等价和GLM CP限制不得省略 |

所有Token/计数/revision为精确十进制字符串，保留null；前端不得用Number强转大整数再计算比率。UTC原值保留，展示时转北京时间；model_handle_start_time只用于理想顺序，不替代request_time轴。

## 生命周期、缓存与错误

提交使用显式pre/now file_ref与submission_key。先把文件放受控input-root；没有HTTP上传、自动采集或热缓存续接。同键同绑定查回原任务，同键异体409；文件移走后仍可查回回执。

目录分页绑定catalog_revision；后续页revision不符时重新取得目录快照。状态/目录/实例/质量GET均只读发布成果，切UUID/图表/箱宽不得触发编码回放。service_instance_id、ma_run_id与生产instance_uuid分别管理；缓存键含服务身份/MA类型/run/UUID，不能和用户appid缓存混用。

任务未完成返回409 RESULT_NOT_READY，未知run/UUID为404，服务身份改变返回409 SERVICE_INSTANCE_CHANGED；错误不回显正文。schema定义了严格错误结构，真实路由路径见OpenAPI。

首版没有MA SSE、原文导出、最佳GF算法推荐、自动告警或路由切换。画像用于人工选择值得做策略对照实验的场景；有限预热理想值可能低于真实值。

## 本次Git范围与后续联合

MA逻辑版本不变；源码已随用户线获授权的已闭环依赖集成提交9a037466f7211126261ec2026f54b9c19c2e2151同步。本轮只追加MA版本和交接记录，边界见[Git检查点](GIT_CHECKPOINT.md)和[依赖基线](SHARED_BASELINE.md)。

用户线U005已报告本地三队列联合通过，其用户功能源码和Dispatcher.register(user)现已在已同步集成提交中。本轮另验证MA独立候选，并复核集成版本；保留该接入，不据旧“未接入”说明否定已闭环进展。

正式前端联调/视觉验收、现场代表CSV与性能、生产访问及交付仍由对应环节完成。本会话处于MA维护及交接状态，共享app/CLI编辑窗口已释放；本文件作为接收入口，不表示已向其他会话发送消息。
