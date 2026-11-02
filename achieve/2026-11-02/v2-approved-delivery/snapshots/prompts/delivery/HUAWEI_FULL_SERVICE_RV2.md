# 华为V100完整服务部署与验收 Agent 执行prompt

你负责在华为实验机验证本次 TokenScope 完整服务：用户监控V2、MA监控、低命中/Token异常分析及正式前端。先检查当前目录的 release-manifest.json、SHA256SUMS、candidate.json 和验证报告；版本、源码commit、镜像tag/完整ID及文件名以这些实际文件为准。此prompt不授权改动业务算法、生产删除/引用策略或其他服务。

## 1. 预检与文件身份

逐项记录 `uname -a`、`uname -m`、`nproc`、`free -h`、`df -h`、`docker version`、`docker info`、`docker compose version`、Docker权限、目标目录权限及拟用端口占用。已有2026-10-26报告为Huawei 2288H V5 / x86_64 / CentOS7内核3.10 / 40逻辑CPU / V100，Docker26.1.4、Compose v2.27.1；2026-10-29旧V1曾运行。它们是历史快照，必须重核当前条件，不据名称猜Ascend。GPU驱动当时525.105.17与NVML550.163.01不匹配；本包使用CPU，不需要CUDA/NVIDIA runtime，不为启动本包修改驱动。宿主空间特别是/home曾紧张，记录剩余量与state增长空间。

在专用目录执行 `sha256sum -c SHA256SUMS`，任何不匹配停止。用Python3读取manifest字段，不手写缩短镜像ID：

```bash
IMAGE_ARCHIVE=$(python3 -c 'import json; print(json.load(open("release-manifest.json"))["image_archive"])')
TOKENSCOPE_IMAGE=$(python3 -c 'import json; print(json.load(open("release-manifest.json"))["image_tag"])')
EXPECTED_ID=$(python3 -c 'import json; print(json.load(open("release-manifest.json"))["image_id"])')
docker load -i "$IMAGE_ARCHIVE"
test "$(docker image inspect "$TOKENSCOPE_IMAGE" --format '{{.Id}}')" = "$EXPECTED_ID"
```

检查镜像linux/amd64、revision/version labels与manifest一致。优先使用已验证镜像，不要求现场联网pip/npm、uv、编译前端或重建。代码包包含固定commit源码、正式dist、8份三模型Tokenizer/Template资产及离线Python wheelhouse；不含模型权重、生产CSV、state、凭据、测试recipe默认配置或Docker基础镜像归档。无基础镜像时不承诺仅凭代码包离线重建。三模型revision和文件SHA在candidate/encoding-assets.lock.json；不要替换成其他模型或名称近似资产。

## 2. 隔离合成验收环境

使用新的专用绝对input/state目录、独立Compose项目名`tokenscope-rv2-acceptance`和空闲宿主端口，例如18060；不覆盖旧V1生产state或停止其他服务。先创建state及input的父目录，input本身由下面生成器创建，确认实际UID/GID有写权限。复制deployment.env.example为deployment.env，填manifest image、`id -u`、`id -g`、真实绝对目录和端口。发布默认127.0.0.1绑定，8CPU/32GiB、只读root/input、可写state及/tmp、专属bridge，无GPU。

在启动服务前，显式生成小型合成输入（将INPUT替换为新input绝对路径）：

```bash
INPUT=/absolute/new/acceptance-parent/input
PARENT=$(dirname "$INPUT")
mkdir -p "$PARENT"
test ! -e "$INPUT" # 生成器要求目标input尚不存在；选新目录，不能删除已有输入
docker run --rm --network none --user "$(id -u):$(id -g)" --entrypoint python \
  -v "$PARENT:/synthetic" "$TOKENSCOPE_IMAGE" /app/scripts/validation/generate_monitoring_data.py \
  /synthetic/input --mean-requests 8 --long-per-app 0

docker compose --env-file deployment.env -p tokenscope-rv2-acceptance -f compose.yaml config
docker compose --env-file deployment.env -p tokenscope-rv2-acceptance -f compose.yaml up -d --pull never
docker compose --env-file deployment.env -p tokenscope-rv2-acceptance -f compose.yaml ps
```

`curl -f http://127.0.0.1:18060/healthz`应成功，GET `/readyz`按各模型诊断记录；DeepSeek缺省思考未决可能使其503，不能自动把生产配置改false换通过。合成请求显式关闭思考仅说明该测试模式。现场V1曾用thinking_disabled、模型别名和时间转换，均不等于所有生产配置已确认；真实CSV保持原件，数据质量和有效子集分开报告。

解开代码包到专用目录，从代码包运行stdlib验收脚本，host Python3无需装依赖：

```bash
python3 TokenScope/scripts/release/verify_service.py --url http://127.0.0.1:18060 \
  --submit-synthetic "$INPUT/manifest.json" --report container-acceptance-onsite.json
```

这是明确合成提交，核对三模型15范围、回执、目录、SSE及CSV/NDJSON导出，不要指向生产数据。错误时收集仅本项目 `docker compose ... logs`、health/ready、版本和异常栈，交维护方；不得用删除state或放宽契约掩盖失败。

## 3. 完整服务及异常分析可用性

同一服务端口检查正式SPA与静态资源：`/#/users`、`/#/users/ranking`、`/#/ma`、`/#/analysis`，以及 `/monitoring/catalog`、`/diagnostics/capabilities`、`/diagnostics/recommendations/capabilities`、`/diagnostics/discovery/capabilities`。先从capabilities取得service_instance_id，诊断业务GET带 `X-TokenScope-Service-Instance`，错实例必须409。用户/MA具体接口与请求体以包内各冻结契约和当前 `/openapi.json` 为准，不套用V1 payload。

首次空state没有异常分析报告是正常的：页面不能触发计算，也不能凭空出现四项Token建议。合成基础任务完成后，仅在该验收state按包内 `docs/contracts/diagnostics-http-1/examples.json` 和capabilities公开schema提交一次明确诊断任务，source选择实际base_run_id和该run实际appid，允许低命中与Token两方向；不要沿用本机旧task/instance IDs。请求使用公开wire字符串整数格式，跟踪任务到真实终态，再只读report/recommendation-summary/discovery。也可按现场权限由对应后端Agent操作，不伪造ready报告或复制本机SQLite冒充现场生成。

默认空recipe：Token无已配置修改依据时不产生量化建议，这是预期边界。测试recipe若另行获得明确许可，仅在隔离验收目录显式设置TOKENSCOPE_RECOMMENDATION_BUNDLE并只读挂载独立文件，不装成生产默认。实际业务策略、引用服务可达性、内容质量/删除授权另行确认，verified标记不代表系统完成业务批准。旧T1仅历史兼容；当前T2–T4。tool_calls:null保守partial不算完整无异常。

浏览器使用同一实例/同appid两页签；有L4/L5发现时各至多一卡、每类≤3例，请求数不按组相加。L4不认定同会话历史被改写，L5不伪造收益。Token P下降但C上升应如实保留；缺失不当0。切历史、刷新/返回、重连与最新partial不得覆盖默认ready，浏览页面应零诊断写请求。大文件保存及浏览器安全上下文按现场许可采用SSH本地转发，不以远端普通HTTP冒充安全上下文验收。

MA需真实前/后两份连续1小时数据、GF规格与UUID映射等输入；不能拿合成V1通过代签MA实际回放或TTFT校准。部署后由MA维护会话负责服务启动/功能与MA问题，用户监控TTFT性能校准仍待完成。提供必要合成MA时须遵循包内现行契约并单独记录来源。

## 4. 重启、失败与回退

保存验收报告后只重启此Compose服务：

```bash
docker compose --env-file deployment.env -p tokenscope-rv2-acceptance -f compose.yaml restart
# 等health健康后
python3 TokenScope/scripts/release/verify_service.py --url http://127.0.0.1:18060 \
  --resume container-acceptance-onsite.json --report container-restart-onsite.json
```

实例ID、已完成回执、快照和导出摘要应一致；另比较异常报告/目录默认项和固定历史摘要。对于任务中断，使用正式retry新任务及原版本快照，不覆盖旧报告、不重写原证据。收集日志不外发生产请求正文。

生产切换前记录旧镜像ID、Compose/env和完整state备份。先停本次专属服务，回退到旧镜像和其匹配的备份state/独立端口；不让旧版本直接打开可能升级过的新state。不执行down -v、全局prune、删除旧发布或强行合并数据库。本prompt没有授权对现有生产实例自动切换，若现场上线范围未明确，先交回合成验收结果。

最终回传单份脱敏报告：实际环境/版本/文件SHA、image_id、配置模式、路径/端口/挂载、启动和四入口结果、监控/MA/异常分项、重启/失败恢复、资源实测、未决和回退位置。清楚区分本机已验证、现场已执行、合成数据与生产数据、用户视觉与工程测试。失败提供准确复现，不宣称“容器能启动”等于全部业务或现场通过。
