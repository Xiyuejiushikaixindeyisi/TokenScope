# 华为执行prompt：ICSL场景构造样本 revision3

本包是ICSL场景构造样本，非生产采集数据；用于完整展示用户监控→L1定位system顶部CCH→修改方案→全量离线收益。用户批准102条GLM-5.2，appid com.huawei.icsl.base，并确认目前GLM无此appid。只在现有TokenScope V2追加数据/分析，保留真实数据、结果、原四入口/L4L5，不重建镜像、不改产品、不换前端、不清空state、不自动重跑真实全量。CPU即可，无需GPU。

## 文件和来源

CSV icsl_glm52_cch_102.csv，15921971 bytes，SHA256 e1425657987dce4ad312d33c7e40a3ac98a822ec7ed928fb7979f1dcc785678b。同包manifest.json和diagnostic-submission-template.json是执行依据，不能使用旧80条数据或本机run/state。

102条、62个对话（40个双请求、22个单请求）。CCH新对话随机、同对话固定，system首行billing header；正文/请求标识/页面内容不添加demo、synthetic、合成数据等字样。来源说明仅留本文件/清单/回传，不能称生产实测。UUID格式hash_id、平均约28K、5K分箱众数25K–30K（该粗箱内102条，不为展示曲线修改产品）。

## 执行前保护

定位现有服务/容器input root与state挂载，仅本项目操作，既有真实任务优先。使用现有服务，禁止为了此样本重启正常服务或覆盖state。确认资源可用后串行执行；本机监控+诊断约69秒，生成峰值约541MiB，仅参考。

核对GLM-5.2/GLM-V5.2资产、encoder、模板hash及设置与manifest一致（block128、CP1、MTP true、default profile）。不一致先报告，不能覆盖现场配置凑结果。

GET /diagnostics/v2/capabilities获取service_instance_id；用户API带X-TokenScope-Instance-Id，诊断API带X-TokenScope-Service-Instance。

分页保存 /monitoring/user-v2/runs 和 /diagnostics/v2/catalog 的全部旧目录、scope/revision/default关系及report digest，记录原MA结果身份和四入口链接。按既有方式备份，不把运行中零散SQLite复制当一致备份。确认com.huawei.icsl.base无业务冲突；若已有同SHA样本则复用现有run/task，不重复提交，若有其他数据则先说明冲突。

在input root新建icsl-cch-v3/并放CSV，校验SHA。既有文件保留，禁止合并到真实CSV。

## 追加分析

POST /monitoring/user-v2/runs：
```json
{"submission_key":"icsl-glm52-v3-monitor","file_ref":"icsl-cch-v3/icsl_glm52_cch_102.csv","common_name":"GLM-V5.2","model_id":"GLM-5.2"}
```
轮询GET /monitoring/user-v2/runs/{user_run_id}至ready，保存现场返回user_run_id/index_revision/base_run_id。

将模板request.source.user_run_id及expected_index_revision替换为现场返回值，再POST /diagnostics/v2/tasks。不得提交占位符或本机ID。只启用low_hit，Token方向关闭，reason_note保持ICSL编码Agent前缀复用分析，不注入recipe。

保持模板预算：102条、64MiB输入、candidate2/pilot8/实验1/编码400/plan64MiB；建议发布层不改默认预算。轮询 /diagnostics/tasks/{task_id}，10分钟未完成先诊断记录，不盲目重试；有资源影响时仅取消本样本任务，不杀其他任务。

## 结果验收

读取report、分页items/finding与items/evaluation、recommendation-summary及recommendations?direction=low_hit。必须发布至少1项L1建议、定位/messages/0/content顶部billing行；full checked=eligible=102、complete=true、available、display_eligible=true。

期望before P2855919/H1026688/C1829231；after P2853567/H2572672/C280895，35.949479%→90.156355%，UI35.95%→90.16%。数字来自真实运行，不写结果表或改前端文字。差异先排查版本/身份/顺序，不凑目标。

GET /diagnostics/tasks/{task_id}/evaluations/{evaluation_id}/rows?offset=0&limit=100及offset=100，检查102条after_raw仅删除system首行计费头，其余不变。不能以pilot8代替full102。

整体partial可能与本机相同：候选比较/证据留存限制；仍须单独确认full完整、建议实际发布。0建议或full不完整视为失败。

## 前端及旧数据回归

打开 /#/users?run={现场run}&appid=com.huawei.icsl.base&revision={现场revision}，确认102条、UUID、北京时间、28K、35.95%；打开 /#/analysis?direction=low_hit&mode=history&task={现场task}，点击查看证据与改法，核对CCH顶部证据、删除前后片段、102条影响、35.95%→90.16%。新样本相关页面字段/原文不出现demo、synthetic、合成数据；不要修改全局UI或删除无关历史来遮盖旧内容。

再次分页读全部旧目录并比较：旧用户run/appid/revision/default关系保留，旧诊断task/report digest不变、MA身份不变。实际打开旧用户监控、旧诊断、搜索及MA入口核对。裸入口因新增记录选中本appid可接受；旧固定链接须有效。不能以新appid存在为由清空数据或重新建全量索引。

仅回传一份Markdown：明确ICSL场景构造样本，版本/资产/CSV SHA、现场run/task/链接、实际指标/full覆盖、L1证据、partial限制、成本、旧数据及四入口前后对照、截图与结论。与真实业务回传分开，不替换真实结论。若必须修改产品才能继续，先说明，不自行改产品。本prompt不包含上传授权；由用户在现场交付后按现有流程执行。
