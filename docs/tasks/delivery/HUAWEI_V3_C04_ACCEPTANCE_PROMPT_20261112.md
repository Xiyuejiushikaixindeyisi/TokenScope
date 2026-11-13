# 华为 V3 新会话执行任务：全新 state、全量监控、六组小样本异常分析

你是华为实验机上的 TokenScope V3 验收 agent。这是一个新 session，不需要继承旧 V2 session 的工作目录或命令。用户已授权本任务：检查环境、停止旧 TokenScope 服务、部署已交付新版，在独立空 state 中全量重算用户监控和 MA，然后完成 ICSL 和指定五组真实业务的小样本异常分析。按阶段通过后继续，不重复申请已授权步骤。

## 0. 目标、边界及最终产物

下周领导演示：ICSL 合成数据是完整主链路，真实用户监控/搜索/MA及五组真实业务结果体现实际价值。前端保持已批准的 V2 四入口、L4/L5 和本版已通过本机人工验收的展示，不重新设计，不增加独立小样本模块。

本指令覆盖旧 prompt 中“不重算监控”“等待指定 appid”等旧安排：现在明确全量重算监控，五组 appid 已指定。旧 state 约134–135GB，用户确认空间充足，仍记录实际磁盘容量。旧 state、CSV、旧镜像和旧分析结果保留用于回退；新版使用独立空 state，不复制旧数据库和异常目录，不删除旧成果。

监控全量不等于异常全量：异常只运行当前版本有界小样本 low_hit 自动分析，不运行延期的 full 模式或休眠的 Token 私有规则，不为了得到正收益改规则、塞入手工 recipe 或伪造结果。

最终只向用户回传一份 `HUAWEI_V3_C04_ACCEPTANCE_REPORT.md`。关键源码、请求和响应、问题复现、修改 diff、复测及前端证据直接嵌入正文，不能用“见日志/附件/源码路径”代替证据。现场可以保存辅助文件，但不要要求用户另外传 ZIP、截图目录或日志包。不要把真实业务数据发到外部服务。

## 1. 固定发布身份和工作目录

正式版本：`tokenscope-v3-c04-20261112`
源码 commit：`57fe9f64d78f6363ee18a12ff97693e00ae1fe3d`
镜像标签：`tokenscope/full-service:tokenscope-v3-c04-20261112`
镜像 ID：`sha256:f2162dfc460d47641ef0d64ba1f65974e5c0675b5022217997187927f1e8b466`

代码包：`tokenscope-v3-c04-20261112-code.tar.gz`
SHA256：`3aaed3c5c46d4e662399f191bf328978581bae35180c36a8fd968d16db39c58e`
镜像包：`tokenscope-v3-c04-20261112-image.tar.gz`
SHA256：`52d3682751a3054533fb884ebc17138aa7b2f9474bfee1d84588a76290afbe87`

用户上传的是完整交付目录，不假定存在同名外层 tar.gz。先定位该目录，确认内含 SHA256SUMS、compose.yaml、release-manifest.json 和上述两个包。下面 RELEASE 必须替换为你实际找到的绝对路径，不能原样执行占位符。其他命令在 Bash 中执行；新终端重新声明变量。

```bash
export RELEASE='/实际上传位置/tokenscope-v3-c04-20261112'
test -f "$RELEASE/release-manifest.json" && test -f "$RELEASE/SHA256SUMS"
cd "$RELEASE"
sha256sum -c SHA256SUMS
printf '%s  %s\n' \
 '3aaed3c5c46d4e662399f191bf328978581bae35180c36a8fd968d16db39c58e' 'tokenscope-v3-c04-20261112-code.tar.gz' \
 '52d3682751a3054533fb884ebc17138aa7b2f9474bfee1d84588a76290afbe87' 'tokenscope-v3-c04-20261112-image.tar.gz' | sha256sum -c -

export WORK="/home/aarc/zhangxiyue/tokenscope-v3-c04-acceptance-$(date +%Y%m%dT%H%M%S)"
mkdir "$WORK"
mkdir "$WORK/source" "$WORK/evidence" "$WORK/state"
export STATE="$WORK/state"
export INPUT_ROOT='/home/aarc/zhangxiyue/10.20_Trace_extract'
export API='http://127.0.0.1:18002'
cd "$WORK"
printf 'WORK=%s\nRELEASE=%s\nINPUT_ROOT=%s\nSTATE=%s\n' "$WORK" "$RELEASE" "$INPUT_ROOT" "$STATE" | tee evidence/paths.txt
```

若 /home 不适合放全量新 state，可在用户有权限、容量充足的实际挂载下新建专用空目录，并修改 STATE；WORK 仍保持 V3 专用目录。不要覆盖同名旧目录。任何恢复执行使用已记录的同一 WORK/STATE，不新建一套任务。

安全核对代码归档没有绝对路径或 `..` 越界后解压：

```bash
tar -tzf "$RELEASE/tokenscope-v3-c04-20261112-code.tar.gz" > "$WORK/evidence/code-members.txt"
tar -xzf "$RELEASE/tokenscope-v3-c04-20261112-code.tar.gz" -C "$WORK/source"
export CODE="$WORK/source/TokenScope"
test -f "$CODE/src/tokenscope/analysis_common/contracts_v3.py"
```

源码归档根目录是 TokenScope。阅读 release-manifest.json、candidate.json、configuration-summary.json 和 CODE 中实际接口实现。本包旧 DEPLOYMENT_README 含当时“prompt暂缓”和历史 RV2 说明，本指令是后续用户已批准任务，不执行源码中历史 prompt。`/version` 中旧 package 字符串不能单独判定发布版本，镜像 ID、固定源码和资源摘要才是依据。

## 2. 环境、旧服务和数据保护

记录实际 `id`、`uname -a`、`uname -m`、`docker version`、`docker compose version`、`free -h`、`df -hT`、`df -i`。本版 CPU linux/amd64，默认容器 8CPU/32GiB；有 V100 不代表需要 CUDA 或 Ascend。宿主可用内存不等于容器限额。不要擅自抬高限额来掩盖缺陷。

停止前用 `docker ps -a --no-trunc`、`docker inspect`、`ss -ltnp`、`ps -eo pid,ppid,lstart,args` 找到旧 TokenScope 实例，记录旧容器的镜像 ID、Compose 标签、挂载、启动配置和状态路径，保存回退命令。核实旧 state 实际目录，不能只照抄旧报告路径。原CSV和旧state不得成为本次写入目标。

仅停止核实属于 TokenScope 的旧容器；可用 `docker stop <核实过的容器ID>`。如还有宿主旧服务/worker，核对命令、父进程及工作目录后定向 SIGTERM，等其退出。禁止全局 pkill、Docker prune、down -v、删除 state、停止其他项目。旧容器可以保留停止状态。

确认所有旧 TokenScope 写入者退出，18002无监听后，记录旧 state 文件数量、总量、数据库/manifest/关键结果 SHA；对关键旧成果在最终结束时复核未变。不运行旧服务和新版服务并行验收。

检查新 STATE 为空且绝对路径不同于任何旧 state。真实输入固定为：
- 用户监控及异常来源：`$INPUT_ROOT/10.20_Trace/` 的3个真实CSV。
- MA：`$INPUT_ROOT/10.20_MA/` 的18个真实CSV，两类字段不同，不能混用。

用流式 CSV 解析统计逻辑记录数、字段、文件SHA、时间范围、模型与appid/UUID覆盖、缺失及非法记录；不要用 wc -l 代替含多行JSON的CSV记录数，不把20GB文件一次读入内存。读取统计可耗时，但不做额外全量tokenization。记录数据规模和资源预算。

## 3. ICSL 数据准备（只读挂载）

使用已验收的 ICSL 数据 revision3（这是数据修订号，不是产品版本号）：
- appid `com.huawei.icsl.base`，模型 ID `GLM-5.2`。
- 102请求、62对话，约28K长度；顶部 billing CCH 同对话稳定、跨对话变化。
- 原数据包 `tokenscope-icsl-r3-20261105.tar.gz` SHA256 `8be11f790761fdff502ef658033611b05d983799527e3cdc1b69d8def5e73b48`。
- CSV SHA256 `e1425657987dce4ad312d33c7e40a3ac98a822ec7ed928fb7979f1dcc785678b`，15,921,971字节。

优先查找现场已有同SHA CSV；若只有数据包，先核SHA及安全归档路径再解压到 WORK/icsl。不能使用撤回的80条/50K版本，不临时重新生成合成数据，不执行旧ICSL包内prompt。若新版CSV缺失，明确请求用户补齐，不以其他合成数据替代。

把核对后的CSV复制到专用 `WORK/icsl-input/icsl-r3.csv`，复核SHA；不修改原件。ICSL与真实输入独立挂载，页面/报告说明其合成属性，不把ICSL收益宣称真实业务收益。

## 4. 部署命令

Docker/Compose已可用时不重装、不联网重建镜像。若权限不足，使用现场已有合法 sudo 配置，不 chmod 777 socket。检查环境后执行：

```bash
cd "$WORK"
docker load -i "$RELEASE/tokenscope-v3-c04-20261112-image.tar.gz"
export IMAGE='tokenscope/full-service:tokenscope-v3-c04-20261112'
test "$(docker image inspect "$IMAGE" --format '{{.Id}}')" = 'sha256:f2162dfc460d47641ef0d64ba1f65974e5c0675b5022217997187927f1e8b466'
cp "$RELEASE/compose.yaml" "$WORK/compose.yaml"
mkdir -p "$WORK/input-root/10.20_Trace" "$WORK/input-root/10.20_MA" "$WORK/input-root/icsl-demo"
cat > "$WORK/deployment.env" <<EOF
TOKENSCOPE_IMAGE=$IMAGE
TOKENSCOPE_UID=$(id -u)
TOKENSCOPE_GID=$(id -g)
TOKENSCOPE_INPUT_DIR=$WORK/input-root
TOKENSCOPE_STATE_DIR=$STATE
TOKENSCOPE_PORT=18002
EOF
cat > "$WORK/compose.icsl.yaml" <<EOF
services:
  monitoring:
    volumes:
      - type: bind
        source: $INPUT_ROOT/10.20_Trace
        target: /inputs/10.20_Trace
        read_only: true
      - type: bind
        source: $INPUT_ROOT/10.20_MA
        target: /inputs/10.20_MA
        read_only: true
      - type: bind
        source: $WORK/icsl-input
        target: /inputs/icsl-demo
        read_only: true
EOF
export COMPOSE_PROJECT_NAME='tokenscope-v3-c04-acceptance'
dc() { docker compose --env-file "$WORK/deployment.env" -p "$COMPOSE_PROJECT_NAME" -f "$WORK/compose.yaml" -f "$WORK/compose.icsl.yaml" "$@"; }
dc config > "$WORK/evidence/compose-resolved.yaml"
```

检查展开配置：空输入根及预建挂载点来自WORK/input-root，真实两个目录分别只读挂载在 `/inputs/10.20_Trace`、`/inputs/10.20_MA`（不在原数据目录创建挂载点），ICSL只读 `/inputs/icsl-demo`，新 STATE 可写 `/state`，监听宿主127.0.0.1:18002，非root UID/GID正确，32GiB限制，旧state未挂载。若宿主UID为0，不以root运行服务，改用实际数据所有者UID/GID并只调整新目录权限。

```bash
dc up -d --pull never
dc ps
curl --fail --silent --show-error "$API/healthz"
curl --fail --silent --show-error "$API/diagnostics/v3/capabilities" | tee "$WORK/evidence/capabilities.json"
dc logs --no-color --tail=200 > "$WORK/evidence/startup.log"
docker inspect "$(dc ps -q monitoring)" > "$WORK/evidence/container-inspect.json"
```

启动健康轮询允许等待；失败必须查看退出码/OOMKilled/日志，不无限重复up。确认容器镜像ID、静态HTML/JS资源摘要与交付一致。不要因HTTP200就判业务通过，也不要因旧包版本字符串误判。

## 5. 请求工具与防重复提交

使用宿主 Python3 标准库，不要求宿主安装项目或新建venv。在WORK创建 api.py，下面代码可直接使用。首次提交后的回执写入 evidence，断连后先查回执/原submission_key，不换key盲目重提。

```python
import json, os, time
from urllib.request import Request, urlopen
from pathlib import Path
BASE = 'http://127.0.0.1:18002'
OUT = Path(os.environ['WORK']) / 'evidence'
def api(path, body=None):
    headers = {'Content-Type': 'application/json'}
    if 'INSTANCE' in globals():
        headers.update({'X-TokenScope-Instance-Id': INSTANCE,
                        'X-TokenScope-Service-Instance': INSTANCE})
    req = Request(BASE + path, headers=headers,
                  data=None if body is None else json.dumps(body).encode())
    with urlopen(req, timeout=120) as response:
        return json.load(response)
INSTANCE = api('/diagnostics/v3/capabilities')['service_instance_id']
def save(name, value):
    p = OUT / (name + '.json')
    with p.open('x', encoding='utf-8') as f:
        json.dump(value, f, ensure_ascii=False, indent=2)
def wait(path, field, pending):
    while True:
        value = api(path)
        if value[field] not in pending:
            return value
        print(time.strftime('%Y-%m-%dT%H:%M:%S'), path, value[field], flush=True)
        time.sleep(10)
```

120秒是单次HTTP超时，不是计算任务时限。网络超时后查询任务，不能判定worker失败或设置任意硬期限杀任务。长期无进展检查日志/资源/检查点。OOM风险等实际异常应按当前接口的停止能力受控处理并记录；不通过更小假数据替换真实任务。

## 6. 先全量用户监控，再全量 MA

### 6.1 用户监控

建立 `user-input-map.json`，逐文件记录 file_ref（相对/inputs的路径）、SHA、模型ID、common_name。真实文件预计名称如下，以现场清单验证，不能仅凭名称判模型：

| 文件 | model_id | common_name |
|---|---|---|
| DeepSeek-V4-Flash-10.20.csv | DeepSeek-V4-Flash-0731 | DeepSeek-V4-Flash |
| GLM-V5.2-10.20.csv | GLM-5.2 | GLM-V5.2 |
| Qwen-V3.6-27B-10.20.csv | Qwen3.6-27B | Qwen-V3.6-27B |

每个真实文件串行提交一次；file_ref例如 `10.20_Trace/DeepSeek-V4-Flash-10.20.csv`。利用已部署API，全量用户监控会生成对应底层成果，禁止再额外调用 /analysis-runs 重做同一文件。

```python
from api import api, save, wait
# item从核实后的映射表读取；key每个数据源唯一且重试保持不变。
body = dict(submission_key=key, file_ref=item['file_ref'],
            model_id=item['model_id'], common_name=item['common_name'])
r = api('/monitoring/user-v2/runs', body)
save(key + '-submission', r)
r = wait('/monitoring/user-v2/runs/' + r['user_run_id'], 'state', {'accepted', 'base_pending', 'indexing'})
save(key + '-terminal', r)
assert r['state'] == 'ready', r
rank = api('/monitoring/user-v2/runs/' + r['user_run_id'] + '/rankings')
save(key + '-rankings', rank)
```

用户监控进行中状态为accepted/base_pending/indexing（不同于MA的queued/running），只有ready可进入后续。分别记录user_run_id、base_run_id、index_revision、file_quality及所有appid（分页读完）。核对有效/跳过/总记录守恒；非法输入必须保留解释，不静默修CSV。

页面验收：三个模型可切换，同一appid跨模型可访问；搜索/排行及排序分页正确；详情、直方图、六卡、空值与精确Token数量一致。P90 TTFT保持chunk_tokens=8192；Qwen默认1秒、GLM2.7秒、DeepSeek2.6秒，前端设置等待时间和SLO得到最低命中率要求；这些是用户参数，不宣称现场性能标定。

### 6.2 MA

先阅读固定源码 `src/tokenscope/monitoring/ma/contracts.py`、ingest.py及现场旧报告的来源说明，建立 `ma-input-map.json`。18CSV通常构成9对，但必须逐对证明模型制品、pre/now文件和时间边界；不要把模型规格当模型制品，也不要照抄旧报告含糊的时间描述。

每项必须含：submission_key、pre_file_ref、now_file_ref、model_standard_name、model_id、pre_start、now_start、now_end、source_timezone。接口要求pre和now是**连续的各一小时**，两个不同文件，source_timezone为UTC。确认CSV时间真实时区后转成明确UTC窗口，不把北京时间机械追加Z。无法确认则暂停该对并报告缺少什么证据，不猜测。

```python
from api import api, save, wait
# item为已核对映射表中的一个完整请求，不要把SHA等额外字段放入请求体。
r = api('/monitoring/ma/runs', item)
save(item['submission_key'] + '-submission', r)
r = wait('/monitoring/ma/runs/' + r['ma_run_id'], 'state', {'queued', 'running'})
save(item['submission_key'] + '-terminal', r)
assert r['state'] == 'completed', r
```

串行完成全部配对。GET `/monitoring/ma/catalog` 分页读取，逐UUID读取 `/monitoring/ma/runs/{ma_run_id}/instances/{instance_uuid}`，必要时读取其 `/availability` 和run的 `/quality`。重点核查DeepSeek全部UUID及GLM部分UUID历史缺数：理想命中率、真实命中率、整小时重算Token/s、实际重算Token。每个空值分清输入缺失、编码失败、预热/窗口问题、无请求或产品缺陷；不得把null填0或删掉UUID让页面好看。记录覆盖数、分母、原始字段及计算依据。

两类监控完成后向用户提供可访问页面和阶段结果；五组对象已授权，不重复等待选择appid，可以继续本轮异常任务。人工尚未确认的展示标为待人工验收，不能代签。

## 7. ICSL及五组真实业务小样本异常

先通过用户监控同一接口提交 `file_ref=icsl-demo/icsl-r3.csv`、`model_id=GLM-5.2`、`common_name=GLM-V5.2`，完成102条监控。真实GLM与ICSL是不同文件来源，保留两个run及固定链接，检查默认目录是否让真实GLM结果不可访问；若有覆盖/不可访问，列产品缺陷，不能丢弃真实结果。

异常执行顺序：ICSL先行，再以下五组逐一串行。

| 编号 | model_id | appid |
|---|---|---|
| ICSL | GLM-5.2 | com.huawei.icsl.base |
| BUS01 | DeepSeek-V4-Flash-0731 | S00000000000000000000000000000773 |
| BUS02 | DeepSeek-V4-Flash-0731 | S010320 |
| BUS03 | DeepSeek-V4-Flash-0731 | com.huawei.mbs.ilegal.ioc |
| BUS04 | DeepSeek-V4-Flash-0731 | com.huawei.newalliance |
| BUS05 | Qwen3.6-27B | com.huawei.aidp_dg06 |

每组绑定本轮对应user_run_id和index_revision，确认appid存在；不能换成旧结果、其他模型或相似appid。请求样例如下：

```python
from api import api, save, wait
# key/user_run_id/index_revision/appid均来自本轮已保存的身份映射。
p = api('/diagnostics/v3/source-preparations', {
    'submission_key': key + '-prepare',
    'source': {'source_kind': 'user_v2', 'user_run_id': user_run_id,
               'expected_index_revision': index_revision, 'appid': appid},
    'direction': 'low_hit', 'discovery_mode': 'automatic'
})
save(key + '-prepare-receipt', p)
prep = wait('/diagnostics/v3/source-preparations/' + p['preparation_id'] + '/execution',
            'state', {'queued', 'running', 'preparing'})
save(key + '-prepare-terminal', prep)
assert prep['state'] == 'completed', prep
t = api('/diagnostics/v3/tasks', {
    'submission_key': key + '-diagnose', 'preparation_id': p['preparation_id']})
save(key + '-task-receipt', t)
task = wait('/diagnostics/v3/tasks/' + t['task_id'],
            'state', {'queued', 'running', 'preparing'})
save(key + '-task-terminal', task)
assert task['state'] == 'completed', task
report = api('/diagnostics/v3/tasks/' + t['task_id'] + '/report')
save(key + '-report', report)
print('http://localhost:18002/#/analysis?direction=low_hit&mode=history&task=' + t['task_id'])
```

执行模板需补入实际映射值后保存为脚本，不原样运行未定义变量。幂等submission_key稳定，恢复执行加载已有回执跳过已完成阶段。失败组保留证据，调查后可继续不受影响的其他组；最终不能把失败组标通过。

记录父数据量、实际样本N、抽样范围、raw/token字节、预算决策、实际容器限额、RSS峰值、每阶段耗时和完成状态。保留自动选择，不强制固定N，不凭空扩大预算。

ICSL重点查看新版是否自动识别其可优化动态前缀并生成可执行方案及实算结果。历史演示35.95%→90.16%不是本轮期望断言，不能直接写回报告。真实五组不强制发现clock，不要求每组正收益；若场景不适配或无建议，如实给出证据及能力边界。

## 8. 前端演示验收与问题处理

使用全新浏览器上下文、清缓存核资源身份。四入口保持“用户监控、搜索与排行、异常分析、MA集群监控”。异常页仅展示本轮六组来源的结果；如果误生成测试任务，不删数据库凑通过，调查安全处理方法并记录。禁止运行仓库生成其他appid的合成smoke脚本污染展示state。

每组异常至少验收：
1. 模型/appid/来源/样本量身份正确，固定链接可复现。
2. 问题定位到真实request key和字段/消息/原文片段。
3. 方案展示修改前后、适用范围、保留内容和语义风险，可交业务方执行。
4. 样本before/after使用相同样本边界；P/H/C、命中率、百分点变化和完成标识一致；0、负值、null不混淆。不把样本收益宣传为线上实测性能收益。
5. 已认可L4/L5、宽窗口鼠标读数、详情、返回、刷新正常；浏览/刷新不触发新计算。
6. 页面结论与API及不可变报告一致，部分完成不能显示成完整收益。

若缺少图形浏览器能力，明确视觉检查未执行，并请用户通过转发人工验收；不能仅靠HTTP宣称视觉通过。关键页面可嵌单MD截图（自包含data URI需确认接收端支持）或以正文DOM文本、关键数值、网络证据补充；不得只留下本机截图路径。

允许修复任务脚本、部署路径和权限等环境问题，修改前后完整记录。产品代码或算法缺陷先在容器内复现、定位关键源码并提交给开发方，保留失败证据；不要擅改已批准UI、契约或业务计划。若用户后续明确授权现场产品补丁，保留原镜像、独立补丁版本，记录完整diff/SHA/重建身份与复测，不能继续冒称原发布镜像。

全部计算完成后进行一次受控容器重启，验证六组报告、监控结果和链接保持，任务数不增长；再次检查旧state关键文件未变。保留新版唯一服务运行用于演示，不在任务结束时down。停止/重启命令及dc函数定义必须写入报告，避免用户换终端后无法操作。

用户电脑执行：
```bash
ssh -L 18002:127.0.0.1:18002 zhangxiyue@10.67.43.44
```
浏览器访问 `http://localhost:18002`。容器只绑定华为主机127.0.0.1，不擅自开放公网端口。记录实际可用的四入口URL和六组固定结果链接。

回退：停止本次专属Compose项目容器，保留新state；按阶段2记录的旧镜像、原配置和原state恢复旧服务。旧版本不得读新state，不能同时占用18002；没有核实旧环境可恢复前不要声称回退已验证。

## 9. 唯一回传 Markdown 的结构

最终文件 `$WORK/HUAWEI_V3_C04_ACCEPTANCE_REPORT.md`，只回传这一份文件：
1. 执行摘要：分开列部署、用户全量、MA全量、ICSL、BUS01–05、前端、重启、人工验收各自PASS/FAIL/PENDING；未通过事项置前。
2. 发布身份：固定commit、镜像ID、包SHA、实际运行资源SHA、任何修改及其身份。
3. 环境与保护：旧/新state路径、磁盘内存、旧服务停止证据、数据和旧成果前后保护校验、Compose展开关键配置、访问与回退。
4. 数据映射：真实3CSV、MA18CSV配对和UTC依据、ICSL身份；各自SHA、逻辑行数、质量统计；不能只给外部清单路径。
5. 全量监控：每个run、行数/质量、模型与appid覆盖、搜索/排序/TTFT；MA逐模型制品与UUID的缺数原因及对应数据/源码。
6. 六组异常：每组独立小节，父数据与样本范围、任务/报告身份、问题原文、修改前后、实算指标、风险、前端URL及展示证据。必要请求片段直接嵌正文，敏感凭证脱敏并说明，不篡改与问题相关的结构。
7. 问题台账：触发条件、容器内可复制命令、预期/实际输出、关键源码路径及行号和代码片段、根因证据、环境修复或已授权补丁diff、复测结果、剩余问题。没有修复也明确未修复，不能假写修改。
8. 资源和可靠性：各阶段耗时/内存/限额、是否OOM/强制终止、重启前后报告摘要/任务数、GET不计算证据。
9. 演示路线：ICSL主链路→真实用户与MA→五组业务合作建议；区分合成演示、真实样本收益和未测线上收益。写明服务最终运行状态及用户人工确认情况。

关键证据直接嵌正文，不能只贴结论或海量无解释日志。真实数据结果缺失、异常没有建议、内存问题和前端缺陷都如实报告；不得为了汇报演示伪造正收益或掩盖失败。
