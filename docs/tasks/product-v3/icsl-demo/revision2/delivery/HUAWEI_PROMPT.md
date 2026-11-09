# 华为执行prompt：追加ICSL合成演示（本机验收已通过）

你在现有华为TokenScope V2环境执行一次追加合成演示。只在用户交付此prompt并授权后执行。现有真实数据和结果优先，不重新跑全量真实分析，不清空state、不替换前端、不修改源码/契约/全局配置、不停止正常业务服务。只使用已有服务API追加新输入与新任务；如版本/资源/权限不满足，记录实际原因，不自行升级或绕过。

## 输入与身份

只传本目录三份文件：icsl_glm52_cch_80.csv、manifest.json、diagnostic-submission-template.json（以及本prompt）。不要复制本机local/state、dist或含本机ID的diagnostic-submission-local.json。不要使用首轮v1 CSV。

CSV SHA256：f59ed3cee7544180e3b12627852a1517b6996b8383b565a708ea23f3ae7d7bb5，22,411,777 bytes，80条；appid `demo.synthetic.icsl.glm52.cch.v2`。GLM-5.2 / GLM-V5.2，输入约50K。此为虚构ICSL编码Agent演示，非真实业务案例，completion_tokens=0仅占位。

核对GLM资产/encoder身份、revision、模板及仿真参数与manifest一致。block128、CP1、MTP true、prefix_cache true、default encoding profile。禁止为凑36→90修改模型配置。若不一致，先报告差异，不覆盖现场资产。

## 1. 保护已有数据

查现有服务、容器挂载的input/state目录与权限，只处理TokenScope对应目录。继续使用现有服务和已批准四入口/L4/L5。先查资源空闲情况，在既有监控/MA验收任务之外串行执行这个小任务；不杀其他任务。

用GET /diagnostics/v2/capabilities取得本次service_instance_id。用户监控请求带X-TokenScope-Instance-Id，诊断请求带X-TokenScope-Service-Instance。保存分页读取的 /monitoring/user-v2/runs 和 /diagnostics/v2/catalog 完整目录、原有固定链接及报告digest；记录MA原结果身份和四入口URL。按现场现有备份机制保留一致性快照，不能在运行中把零散SQLite复制宣称成一致备份。

确认新appid未被已有业务使用。若已存在本合成数据，核对输入SHA和run/task状态后复用，禁止覆盖或盲目重跑。若同appid是其他数据，停下说明冲突。

在实际input root下新建不冲突的icsl-demo-v2目录，放CSV并再次校验SHA。保留所有既有文件，不把演示CSV并入真实数据CSV。文件引用以服务input root为基准，不能使用本机绝对路径。

## 2. 追加用户监控

POST /monitoring/user-v2/runs，JSON：
```json
{"submission_key":"icsl-synthetic-glm52-v2-monitor","file_ref":"icsl-demo-v2/icsl_glm52_cch_80.csv","common_name":"GLM-V5.2","model_id":"GLM-5.2"}
```
轮询GET /monitoring/user-v2/runs/{user_run_id}至ready。保存服务返回的user_run_id、index_revision、base_run_id。不得重用本机ID。若失败保留证据，避免重复提交。

## 3. 追加低命中分析

读取diagnostic-submission-template.json，将request.source.user_run_id和expected_index_revision替换为上一步现场值；其他字段保持，包括appid及enable_token_content=false。不要把模板中的占位符提交。POST /diagnostics/v2/tasks，保存返回task_id，轮询GET /diagnostics/tasks/{task_id}至终态。

模板任务预算：80请求、64MiB输入、candidate_limit2、pilot8、1实验、400编码次数、64MiB plan上限；建议发布层仍使用服务默认预算。不开Token方向、不注入recipe、不提高全局预算。options里的T2/T3/T4只是现有schema预算占位，selection已禁用该方向。

本机监控+诊断约50秒，仅供预算参考。现场观察CPU/内存/磁盘及任务状态，若10分钟仍不完成先检查并汇报；不能盲目循环重试，影响既有任务时仅取消本次demo任务并保留旧数据。此任务无需GPU。

## 4. 核验实际结果

读取report、items/finding、items/evaluation、recommendation-summary、recommendations?direction=low_hit，按接口分页。要求L1定位/messages/1/content中的x-anthropic-billing-header/cch；full评估checked=eligible=80、complete=true、available、display_eligible=true，且发布至少1项L1建议。不要用pilot8结果代替全量。

同身份期望before P=3999930/H=1435904/C=2564026，after P=3997580/H=3599872/C=397708。实际为35.898228%→90.051281%，展示35.90%→90.05%。结果应计算生成，不写数据库或手填前端。若不一致，保留实际值并核查版本、身份、顺序及设置，不改结果凑目标。

GET /diagnostics/tasks/{task_id}/evaluations/{evaluation_id}/rows逐页核验80条：after_raw唯一变化是/messages/1/content计费头内容清空；其余消息/tools/任务不变。第一条冷缓存命中0属于预期。

整体partial可能正常：候选查找和证据保留有限，本机同样partial，但80条full评估完整，前端1项建议有效。必须分别记录；若0建议、full不完整或修改超出计费头，则验收失败，不把后台数值算完当作可展示。

## 5. 同一前端追加展示及回归

不用新增页面或替换HTML。打开 /#/users?run={现场user_run_id}&appid=demo.synthetic.icsl.glm52.cch.v2&revision={现场revision}，确认80条、约50K直方图、35.90%。打开 /#/analysis?direction=low_hit&mode=history&task={现场task_id}，点击“查看证据与改法”，确认CCH两个请求差异、删除前后片段、80条影响、35.90%→90.05%。保留截图及固定链接。

分页再次读全部原目录：原监控run/appid/source/revision及原is_default关系保留；原诊断task/report digest不变，MA原结果身份不变。实际打开至少一个旧用户监控、旧诊断、原搜索、原MA入口，核对旧内容仍可看。新demo成为裸入口最新默认项可以接受，不能因此清空旧记录，也不需要篡改排序。原业务固定链接必须继续可用。

## 回传

只回传一份Markdown：新增合成演示段、版本/资产身份、CSV SHA、现场run/task/固定链接、实际计数与命中率、L1定位与方案、full覆盖、partial原因、资源/耗时、四入口与旧数据前后对照、通过/失败及限制。与此前真实数据结果分开，不能用合成结果替换真实结论。

如需产品修改才能继续，停止该修改并单独说明；不要删除已有分析或重建全量索引。若本次失败，保留合成任务供追查，不影响已有业务结果。无须镜像构建或Git推送。
