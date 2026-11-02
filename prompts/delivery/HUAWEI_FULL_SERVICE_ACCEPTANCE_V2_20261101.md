# TokenScope完整服务：华为实验机执行prompt

版本：full-service-onsite-v2-20261101。总负责：镜像打包与审查会话 `01a1800e-80b4-7400-a78b-a84f5b6e888d`。此文件单独版本化，替代旧prompt的验收范围和责任归属，不覆盖任何已发布包内文件。请将以下整份内容交给华为实验机Agent。

你负责在实际华为实验机完成环境核对、隔离容器启动、服务部署及完整功能验收。范围是用户监控V2、搜索排行、明细导出、TTFT参考估算、MA监控、低命中率分析、Token异常分析和跨模块恢复。不能把异常页面、healthz或HTTP200通过写成全功能通过。先执行合成数据，真实数据另列结论。

## 执行前的版本门槛

已知历史包 `tokenscope-rv2-20261101`，源码45d9285210dc0b9edeb86c599c7b6bcd942f60b5，镜像sha256:483db762852b38ef54559cff1bb23ef668ea9296a055ce02aac44a809b427ce5。本次更完整合成验收发现FS-01：异常报告跳用户监控使用了错误的user_run_id URL参数，正确参数是run。**这个历史镜像和代码包未包含后续修复，不能以本地修复候选通过为它签完整通过。**

从总负责最新交付manifest确定实际版本、源码commit、FS-01修复身份、镜像完整ID和代码包SHA。若收到的仍是上述旧包，只能做隔离预检/记录已知缺陷，回报总负责请求修复后的正式版本；不要在现场偷偷挂补丁dist或改包后继续声称旧SHA有效。本prompt本身不是新镜像或代码交付包。新包未交付时，不进入正式完整验收收口，更不切生产。

先读本版本README、release-manifest.json、candidate.json、SHA256SUMS、最新统一审查记录和FULL_SERVICE_SYNTHETIC_E2E_20261101结果。目录内原文件执行sha256sum -c SHA256SUMS；新版独立prompt和附加合成材料使用各自manifest，不能加入旧SHA256SUMS。任何身份不一致停止相关操作并报告。

## 实际环境与启动

在证据目录记录时间、主机名、uname -a、uname -m、nproc、free -h、df -h、docker version、docker info、docker compose version、Docker权限、UID/GID、目录可写性、端口占用和已运行容器。已有V100环境报告是历史快照：Huawei 2288H V5、x86_64、CentOS7内核3.10、40逻辑CPU、约375GiB内存；Docker26.1.4、Compose v2.27.1，旧docker-compose 1.26不能冒充已验证版本。历史根分区剩余约4.3GiB、/home约401GiB，当前必须实测，尤其检查Docker data-root与state增长空间。

本服务用CPU和Tokenizer/Template，不加载推理权重，不需要GPU/CUDA/NVIDIA runtime。历史驱动525/NVML550不匹配只记录，不为启动本服务修改驱动，不根据“华为机”推断Ascend。共享机器不能全局清理Docker、停其他容器、改全局代理或升级系统。

用专用绝对路径创建input/state/evidence，独立Compose项目，例如tokenscope-full-acceptance，选实际空闲端口。保留旧V1或其他部署。服务input只读、state可写、root只读、tmpfs /tmp，资源按发布compose的8CPU/32GiB核对是否容纳。无条件变更资源前先记录差异，不假设大机可以无限并发。使用宿主的实际UID/GID；默认127.0.0.1绑定，远端浏览器通过获准的SSH本地转发访问。

宿主Python可能不是3.11。检查python3版本后，用其stdlib读取manifest即可；不在宿主全局pip安装。无可用Python时用已存在的JSON工具或人工读取已校验manifest；服务和计算使用交付镜像。检查image_archive/image_tag/image_id实际字段后：

```bash
# 以下变量必须来自已校验manifest，路径和项目是本次专属实例。
docker load -i "$IMAGE_ARCHIVE"
test "$(docker image inspect "$TOKENSCOPE_IMAGE" --format '{{.Id}}')" = "$EXPECTED_ID"
docker image inspect "$TOKENSCOPE_IMAGE"
docker compose --env-file deployment.env -p tokenscope-full-acceptance -f compose.yaml config
docker compose --env-file deployment.env -p tokenscope-full-acceptance -f compose.yaml up -d --pull never
docker compose --env-file deployment.env -p tokenscope-full-acceptance -f compose.yaml ps
```

env按deployment.env.example填写实际image/UID/GID/input/state/port。记录解析后的compose、image inspect、挂载和容器ID。不得自动pull近似tag或现场重建来绕过镜像身份。代码包含固定源码、dist、三模型8份编码资产及离线wheelhouse；没有生产CSV、state、权重、凭据或Docker基础镜像归档，不能承诺仅代码包离线重建镜像。

验证/healthz、/readyz以及正式SPA静态JS/CSS。readyz按模型说明：DeepSeek default思考模式未确定时可能503，不把生产配置默认为false。只允许在独立合成state显式选择thinking_disabled，并记录CAS前后revision、配置身份及合成用途；真实业务模式、别名、时区须核实。三模型资产revision与SHA按本版candidate/锁文件逐项核对。

## 合成数据准备与实际任务原则

所有输入新建在专属input内，保存CSV SHA、生成命令、行数、APPID、模型/别名和时间窗。保留原字节，不覆盖原CSV；不复制本机SQLite或旧task ID冒充本机计算。必须通过公开HTTP显式提交，由该容器真实worker完成；只读GET/页面访问不触发分析。

基础数据可用包内scripts/validation/generate_monitoring_data.py，参数--mean-requests 8 --long-per-app 0，目标目录必须不存在。该生成器仍包含固定200K/220K边界，不代表每组只有8条。可用镜像python在挂载的专用父目录运行生成器，不依赖宿主安装Tokenizer。之后运行scripts/release/verify_service.py --url <实际地址> --submit-synthetic <manifest.json> --report <本次报告>，要求三模型15范围、回执/幂等/SSE/导出校验完成。

V2小CSV和MA基础样本生成入口为代码包apps/viewer/scripts/prepare-v2-fixtures.py。不要把V1 CSV当MA全部前置；补下列专项样本。完整本机新增样本与oracle来源为artifacts/reviews/full-service-synthetic-20261101，需总负责提供其独立校验的输入/测试策略清单或按源码生成步骤重建；此目录不承诺已包含在旧代码包中。缺少专项数据时明确对应测试未执行，先请求缺失材料，不能默认为通过。

业务请求使用正确实例header：用户/MA/S0用X-TokenScope-Instance-Id；diagnostics用X-TokenScope-Service-Instance。从当前catalog/capabilities获取实际实例ID。按公开Schema使用字符串整数；提交前持久化submission_key与完整内容，丢响应重发原键原内容，异体同键应409。别使用本prompt里的本机ID作为现场目标。

## 逐项验收矩阵

每行输出：版本/输入/配置身份、动作、实际值与独立预期、通过/失败/未执行、日志/截图/响应摘要、失败归口。浏览器操作使用正式dist，与API值交叉核对；无浏览器能力时只标API通过，界面项仍待执行。受控故障与真实worker场景分别标注。

| 范围 | 数据、动作与判据 | 归口 |
| --- | --- | --- |
| 用户运行 | 三模型小CSV，新建/已知运行/最近记录/绑定历史base；GB为appid×common_name，身份不串。索引未就绪只能读已完成base，ready后排行可用；失败/中断保持历史A，成功B原子替换。空范围不冒充生产零流量。 | 用户后端、监控前端 |
| 指标与详情 | 六卡及J/P/H/C守恒P=H+C、分布/分位/整文件质量、冻结配置。重复hash保留不同source_record_index；>50请求分页、hash精确/字面前缀、半开区间、J/P/C排序和每段≤1000点辅助图。详情只读；原文按需取，1MiB上限明确；特殊范围是UTF8字节位置，不作为可加Token归因。 | 用户后端、监控前端 |
| 搜索排行 | ≥29 APPID，包含Case-App、case-app、literal%_appid；大小写敏感字面子串，%/_不作通配。四指标升降排序、所有AND上下界含端点、倒置/非法值422；UI命中率百分数转换。每页20项20+9不重漏，固定index_revision；错误/缺失次页revision409。切条件回首屏、返回保留筛选页码、300ms/Enter不重复重置。 | 用户后端、监控前端 |
| 众数和精度 | 1K/2K/5K开放箱、>200K仍等宽；全部并列峰、最低起点代表、箱均值sum/count非中点。大整数不丢精度，NULL不变0；独立从CSV计数及逐请求C复核聚合/模式。 | 用户后端、监控前端 |
| 导出 | 全筛选范围导出CSV/NDJSON，不只当前页；NDJSON逐请求行原字节SHA及actual_rows验证；CSV14列/结构/数量与公式转义，不宣称CSV有NDJSON摘要。取消/换run/APPID/筛选/排序/离页/身份改变，旧导出不能提交下载。故障注入保留真实身份/数值断言；File System Access API需安全上下文，fallback上限16MiB，大文件能力另列。 | 用户后端、监控前端 |
| TTFT | 显式新建不可变情景及历史：新tag=batch_reference_total_noncompute_v1，T/W/K/τ显式，W含GF分发到首Token全部非计算，不含GB前排队；不再提交O（含0/null均不能偷带）。W缺失不当0，显式0有效；合成user_assumption不叫实测。le与lt边界、0%/100%/no_budget/out_of_scope/无正P90；条件变化/迟到使旧估算失效。旧W+O只读。现场真实校准另验。 | 用户后端、监控前端 |
| MA提交及缓存 | pre/now各连续1小时、UTC左闭右开；GF规格×完整UUID。相同UUID跨APPID共享预热，跨UUID冷缓存隔离，不能混规格。幂等/回执恢复、全UUID含仅pre、空now、缺pre、顺序冲突及pre/now质量定位，逐行失败可独立重试。 | MA后端、监控前端 |
| MA数值 | Q配对与独立R/E、coverage、prompt输入不一致数分别展示；实际高于理想不擅判错误。input/实际未命中两分布各1K/2K/5K含200K尾桶；零未命中单列。12×300s与3600s总量守恒，空桶0、有请求但无有效真实观察null，不插值。MA无原文导出/SSE，不造新能力。 | MA后端、监控前端 |
| 配置/恢复 | 设置及阈值CAS冲突保留草稿，用户明确重新保存才写新revision；历史配置/结果不变，仅后续运行生效。用户/MA活跃任务60秒串行读，终态/离页停止；错实例409清旧缓存/在途/原文/导出。 | 相应后端、监控前端 |
| 低命中 | 实际新任务覆盖L1动态前部、L2同工具集合不同顺序、L3动态工具内容；优化卡须full/direct_full完整范围且收益>1个百分点，pilot不能替代全量。L4/L5各至多一张卡，每类≤3例，完整RequestKey去重；L4不凭空认定会话历史改写，L5不伪造收益。 | 公共/低命中后端、异常前端 |
| Token异常 | 当前T2/T3/T4，无新增T1。默认空recipe说明未配置依据；显式合成recipe只读挂载至隔离服务，TOKENSCOPE_RECOMMENDATION_BUNDLE只对本验收使用，不改生产默认。覆盖真正零、无basis→未知/无evaluation、负收益、P降低C升高警告；各独立方案收益不能相加。仅基于真实新任务的范围/影响/建议/量化/局部证据作结论。tool_calls:null保守partial保留。 | Token后端、公共层、异常前端 |
| 异常目录/来源 | 同origin/instance/appid切两方向；两ready后较新partial不能替换默认ready，固定历史/详情刷新返回保留身份。base来源打开原overview，user_v2来源必须#/users?run=<实际用户运行>&appid=<实际APPID>；冷浏览器和已有其他最近运行均验证正确六卡及刷新，不只看URL。业务身份不匹配应阻断。 | 公共层、异常前端 |
| 通知/任务恢复 | 提交前catalog.event_cursor；fetch-SSE带诊断实例header，terminal后一次对齐目录，无任务周期轮询。游标当opaque，重放/去重/reset/断连重连/身份切换；未发布失败/中断不进报告catalog，查terminal端点与receipt。单worker资源边界，排队、取消、显式retry新ID，无半成品。 | 公共层、相应后端 |
| 持久性/只读 | 保存终态回执、排名/情景/评估、MA快照、报告/示例/默认与固定历史、CSV/NDJSON摘要，仅读后业务控制表不变，再只重启专属容器比较身份与不可变结果。内部sqlite_sequence重启回填可能增加；单列它，核对业务行、MAX(seq)、epoch/公开游标，不能声称整个数据库字节不变。 | 总负责、相应后端 |
| 页面布局 | 1440桌面与390窄屏，六卡/表单/搜索/MA/两类异常/详情可操作，无脚本错误、正文不整页横向溢出；表格允许自己的横向滚动。源代码模块测试和受控DTO/网络测试单列，不能代替正式浏览器真实后端。 | 两前端 |

TTFT公式核对使用实际返回P90：budget=T-W，le取floor(budget/τ)，lt取ceil(budget/τ)-1，再依契约处理边界。100%是参考边界，不证明线上可行；缺真实W/K/τ校准不得填默认值。MA真实字段、GF规格/UUID、两完整窗口，以及用户common_name/模型别名/时间语义若缺失，写具体缺口，合成值不能冒充。

异常任务从当前/diagnostics/capabilities取submission schema。source为base或user_v2二选一，使用真实run及appid；user_v2带实际index_revision。reason_codes包含low_hit才启用low_hit，已冻结路由要求所选原因启用token_content；保留T2/T3/T4及预算字符串整数。不要直接执行旧生成脚本中的process_next或改SQLite封装成“HTTP端到端”。测试reference-map只是合成全文来源，不证明远端引用服务可达；synthetic_fixture verified只是测试声明，不是生产删除/引用批准。

## 真实数据、故障和回退

合成完整通过后，按用户授权对原始真实CSV作只读来源清单及SHA，转换输出另存并记录别名/时区/模型模式；坏行比例、有效子集及缺失字段分别回报。若只拿到用户数据而没有MA两窗口/UUID，不能给MA签真实通过。无已批准业务recipe时，不为凑四张卡补授权。TTFT实际性能校准归用户后端单独完成。

只在专属合成state验证运行中断，记录准确任务和进程后才能故障注入，不能杀共享Docker daemon或其他服务。本地已测真实worker运行中SIGKILL、interrupted、显式新提交恢复；现场可按资源/权限实施并回报，未执行写未执行。无现网切换授权时到合成验收止步。

任何失败保留日志、输入摘要、instance/task/run/revision、精确HTTP/页面步骤、expected/actual、trace/截图。定位选择器失效时修正选择器但保留身份/数值/缓存/恢复/导出断言；禁止删除断言、放宽契约、把null填0、删state重来或强写ready换通过。

回退前记录旧镜像ID、compose/env、独立端口及匹配的完整state备份；先停本次专属服务，再恢复旧镜像与它匹配的state。不要用旧镜像直接打开升级后的state，不执行down -v、全局prune或删除原始证据。现场未明确生产切换时只回传结果。

## 归口与最终回传

完整服务总负责为镜像打包与审查01a1800e-80b4-7400-a78b-a84f5b6e888d，直接协调修复，不再由MA或异常前端承担启动总责。用户后端01a18bc7-cdb5-7830-a185-ad3aa6257b21；MA后端01a18ab2-2600-7ae1-8b0e-979dad9ec3be；监控前端01a18c49-d9b4-7a33-8c04-e5a72adfcc24；公共/低命中01a18be2-7112-7aa2-919b-5137d1f1b1ad；Token后端01a18fcd-0464-7cf1-b435-4f394bd33e66；异常前端01a19111-344a-75c1-84e0-14db8be08f4f。这些是本地维护会话标识，现场Agent未必可直接访问，统一把报告交总负责协调，不凭ID尝试未获准的外发。

回传一份脱敏报告及证据目录SHA清单：实际环境与资源、包/镜像/源码/编码配置身份、目录/端口/挂载、各矩阵项结果、真实与合成分列、浏览器与API/受控故障分列、重启/中断/回退、未决问题及复验建议。问题经归口修复、本机独立复验、必要新版本交付、现场复验后才关闭。本机通过不代替华为通过，工程测试不代用户视觉验收或生产策略批准。
