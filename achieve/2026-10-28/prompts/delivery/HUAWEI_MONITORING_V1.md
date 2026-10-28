# 给华为 V100 机器 Agent 的 TokenScope 首次验收 prompt

你负责在这台华为 V100 主机上验证交付版 TokenScope。先读随包 `release-manifest.json` 和 `code.tar.gz` 内的运行说明/API说明，再执行。当前维护仓库中的这份 prompt 是准备稿；只有旁边存在完整 release-manifest、镜像、代码包并校验通过，才代表已交付。不要把准备稿当作镜像已经生成。

目标是使用交付镜像完成 CPU 路径启动和第一次验收；不修复 GPU 驱动、不安装 CUDA、不运行模型推理、不主动采集业务数据、不把绝密 CSV 或请求正文发回其他机器。前端是否包含以 manifest.frontend_scope 为准；`monitoring_backend_only` 仅有后端 API，不宣称前端联调完成。

1. **确认交付和环境。** 记录实际工作目录、日期、Linux/架构、可用CPU affinity、内存与磁盘空间、Docker server/client、`docker compose version`。此前探测是40逻辑CPU、约376GiB内存、Docker26.1.4/Compose2.27.1，内核3.10；这些只是历史参考，核实当前可用资源。选择 `/home` 下用户有权限的专属目录，避免根分区和其他项目；不要假定开发机路径在本机存在。找不到 Docker/Compose 或权限不足时报告具体命令与错误，禁止自行升级共享宿主驱动/内核/服务。

2. **校验后加载。** 用 Python 标准库或 sha256sum 校验 manifest.files 中每个文件，拒绝缺失/不匹配项。校验代码包后解压到新的专属 release 目录，不覆盖旧服务或状态；核对 SOURCE_MANIFEST 中的代码/资产摘要。执行 `docker load -i image.tar`；用 `docker image inspect` 核对 manifest.image_id、linux/amd64。无需联网拉取镜像，Compose设置 pull_policy: never。遇到旧内核/系统调用/动态库错误保留完整错误和版本，不通过删校验或换镜像掩盖。

3. **准备专属目录和配置。** 在专属工作目录建立 inputs、state、validation；保持绝密输入仅在本机。用当前被授权的 uid/gid 为 state 提供写权限，不做递归修改其他目录。写 `.env`（这里所有路径都必须换成核实过的本机绝对路径）：

   ```dotenv
   TOKENSCOPE_IMAGE=<manifest.image_tag>
   TOKENSCOPE_UID=<运行用户的数字uid>
   TOKENSCOPE_GID=<运行用户的数字gid>
   TOKENSCOPE_INPUT_DIR=<专属inputs绝对路径>
   TOKENSCOPE_STATE_DIR=<专属state绝对路径>
   TOKENSCOPE_PORT=8000
   ```

   先确认端口空闲；使用随包 compose.yaml 和专属项目名 `tokenscope-monitoring`。8CPU/32GiB为初始限制，宿主共享资源不足时先报告，不擅自增加。输入挂载只读，状态挂载可写；没有GPU设备映射。

4. **离线镜像内验收。** 先创建专属 validation 目录并赋予运行用户写权限。执行以下逻辑（变量值从已校验的本机事实取得，不照抄占位符）：

   ```bash
   docker run --rm --network none --read-only --cpus 8 --memory 32g \
     --user "$TOKENSCOPE_UID:$TOKENSCOPE_GID" \
     --tmpfs /tmp:size=536870912,mode=1777 \
     --mount "type=bind,source=$VALIDATION_DIR,target=/app/artifacts/validation" \
     --entrypoint python "$TOKENSCOPE_IMAGE" \
     /app/scripts/validation/run_monitoring_e2e.py --mean-requests 20 --long-per-app 1
   ```

   脚本自行生成每模型5个appid的泊松合成数据，包含长请求/≥200K/工具/坏行，运行实际HTTP/CLI、独立参考检查、并发读取、重启与自身子进程强制中断恢复。只终止该验收脚本自己创建的服务进程，不操作别的服务。检查最终 report.json 的 passed=true，以及固定资产/代码版本。若失败保留日志并停止发布成功结论。

5. **启动持久服务。** `docker compose --env-file .env -f compose.yaml config` 核对展开后的专属目录/镜像/资源，然后 `docker compose --env-file .env -f compose.yaml up -d`。保存 inspect 中CPU/内存/user/mounts的实际配置；核对 healthz、version、models。服务默认仅映射本机127.0.0.1，远程展示入口由用户另行确认。

   DeepSeek 的生产缺省思考模式仍待用户确认，不能为了readyz变绿而替用户选择。默认profile下全局readyz可返回503并指出该未决项，GLM/Qwen readiness独立。合成测试显式enable_thinking=false只是测试输入；真实请求带显式选项时可正常分析。GLM/Qwen按固定模板默认。真实DeepSeek请求未显式选择时，应先请用户确认，再通过settings revision CAS选择 thinking_enabled 或 thinking_disabled，不能修改生产请求正文来绕过。

6. **第一次功能验收。** 使用 inputs 中的合成文件先提交3个模型各一个任务，或把步骤4的合成CSV复制到专属inputs后提交。POST `/analysis-runs`，file_ref为输入根内相对路径，model_id为 GLM-5.2、Qwen3.6-27B、DeepSeek-V4-Flash-0731。轮询状态；GET metrics、length-histograms、lengths、signals。核对5个appid、质量计数、J/P/H/C/O守恒、5K直方图/众数/200K尾桶、P50/P80/P90数值、分页和空阈值。Qwen/V4是普通链式近似，增强hybrid选择必须拒绝。重启专属Compose服务后结果/设置仍在，GET不触发新任务。

7. **现场真实数据和性能。** 在用户允许的专属输入路径内使用真实CSV，每文件绑定一个模型；原文件保持原样。真实数据不得离开华为机，也不写入公开日志。每个文件分别记录从运行开始到完整结果提交的耗时（排队另列）、CPU/内存/磁盘峰值、代码/资产/设置摘要、质量计数和阶段耗时；目标每文件<7200秒。若未获真实CSV使用授权，明确这项未执行，不以小样本通过替代。真实结果复核在现场用同一固定输入/设置和独立参考/第二次运行完成，不要求把CSV回传本机。

8. **回传一份脱敏验收报告。** 写一个 Markdown：环境事实、release/image/code/资产摘要、实际执行命令与退出码、离线小样本/持久服务/重启/真实三文件验收结论、耗时与资源、失败原因和未决项。只回传经过用户允许的汇总和合成样例；真实appid可匿名，不能包含原request_input、Token IDs、凭据或真实CSV。分别标明 M11（交付/兼容/启动）和M12（真实负载两小时）通过/失败/未执行。部署成功不自动等于整体业务验收通过。

回退只作用于本项目专属Compose：停止该服务，保留输入、state和失败报告；使用上一release及兼容状态备份恢复。禁止 `down -v`、`docker system prune`、清空共享目录或覆盖别的服务。需要改代码时先回报问题；常规修复先本地验证，用户确认最终变更后才重新构建镜像，不反复重构Docker。
