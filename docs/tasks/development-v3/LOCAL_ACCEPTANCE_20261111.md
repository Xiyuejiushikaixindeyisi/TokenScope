# V3 C01–C04 本机验收

## 2026-11-12 用户人工验收通过与交付授权（最新）

用户原话：“用户验收通过，你现在可以整理 prompt，让镜像打包与审查session进行端到端测试验收、git和版本整理、记忆整理、打包。” 当前 **LOCAL_USER_ACCEPTED / DELIVERY_REVIEW_AND_PACKAGING_AUTHORIZED / ON_SITE_PENDING**。此前待本机人工验收/暂不打包为历史，不覆盖此决定。

已准备 `docs/tasks/development-v3/PACKAGING_HANDOFF_PROMPT_20261112.md` 与 `HANDOFF_CANDIDATE_20261112.json`：镜像线获准独立E2E→Git/版本→记忆→打包/容器复验及华为prompt整理；产品缺陷仍交开发修复，不改已批准布局/范围，不自行现场部署。候选源码复核无差异，HEAD a96da81152b4917f9a1fbfe65a7ddb864dee79ce加当前未提交变更，原candidate manifest SHA为2b90769d8bd85843b2aca5fc976fedf8c09aeca18544e32a7d380880321c1ed5。真实华为业务收益仍待验。此轮只记录用户通过和准备交接，未发送跨session消息、未执行独立复验/Git/打包；交接文件不等于接收回执。


## 2026-11-12 本机验收服务恢复
用户反馈原链接无法访问。核实旧PID411591已不存在、WSL端18002拒绝连接，原日志无明确退出原因，不臆断。核对候选源码/dist摘要未变，以原c04-e2e-02/state恢复服务；现PID4930、exec会话15308，仅监听127.0.0.1:18002。Windows localhost健康/首页/目标报告均HTTP200，Chrome实际clock卡片可见、任务身份正确、无脚本错误。恢复证据在本轮c04-e2e-02/health-recovery-20261112-01/CHECK.json；原报告链接有效，用户人工仍PENDING。没有重跑分析/修改产品/打包；下方旧PID为历史。


当前 **LOCAL_USER_ACCEPTED / ON_SITE_PENDING**。C01–C04技术闭环后用户已于11-12明确本机人工通过，授权镜像线独立交付复验和打包；包体尚未生成。

## 页面与身份

- 实际产品入口：http://localhost:18002/#/analysis 。独立state为项目内 `artifacts/validation/development-v3/repair-c01-c04-20261111T184136/c04-e2e-02/state`。
- 候选源码/前端dist摘要、启动命令/进程分别保存在同目录 `candidate.json` / `server.json`；前端产物在同轮 `c04-dist-01`。后续重启记录单独保存。
- 获批DEMO：[repair-demo-r1](prototypes/repair-demo-r1/index.html)，SHA256 `3441e2ea20bc47b331d602cea5010f922c24b2522bee6b628bad77f23d956619`，未修改。
- 下表为新合成CSV经真实模型编码、自动发现/plan与同样本前后重放计算的结果，**不是华为业务收益**。数值不同于DEMO示意数值是预期行为；布局、信息位置和交互以获批DEMO为准。

| 组 | APPID | 模型 | 合成clock样本参考变化 | 页面 |
|---|---|---|---|---|
| BUS01 | S00000000000000000000000000000773 | DeepSeek-V4-Flash-0731 | +12.34pp | [实际报告](http://127.0.0.1:18002/#/analysis?direction=low_hit&mode=history&task=diag-54ecb69591c64db295d72c97ad374a9e) |
| BUS02 | S010320 | DeepSeek-V4-Flash-0731 | +20.8pp | [实际报告](http://127.0.0.1:18002/#/analysis?direction=low_hit&mode=history&task=diag-baf90b097dfa456e89b9cf61b11993e9) |
| BUS03 | com.huawei.mbs.ilegal.ioc | DeepSeek-V4-Flash-0731 | +21.7pp | [实际报告](http://127.0.0.1:18002/#/analysis?direction=low_hit&mode=history&task=diag-0175bef4b09746ab96874ad7cd2b14fb) |
| BUS04 | com.huawei.newalliance | DeepSeek-V4-Flash-0731 | +18.35pp | [实际报告](http://127.0.0.1:18002/#/analysis?direction=low_hit&mode=history&task=diag-a2da6f508a664abfbd596b908d598cb1) |
| BUS05 | com.huawei.aidp_dg06 | Qwen3.6-27B | +6.04pp | [实际报告](http://127.0.0.1:18002/#/analysis?direction=low_hit&mode=history&task=diag-bbbdea4fb3f64948b0a1aa7eb0e64be0) |

## 人工检查步骤（2026-11-12用户已确认验收通过）

1. 依次打开五组报告，确认APPID/模型/样本范围一致，存在clock固定化建议及“样本命中率变化·参考”，有合成来源标识。
2. 查看双边字段、高亮与局部上下文，进入详情核对clock内部改成NORMALIZED、外部文本未扩改；固定化的业务影响必须另由业务方判断。
3. BUS03查看普通workspace路径L1；工具描述路径属于L3，不混入clock；BUS04不强造工具路径问题。
4. 详情返回、历史切换、刷新、窄屏均检查；L4/L5按各一张卡和至多3个代表例展示。没有独立“小样本诊断”入口或DEMO状态切换器。
5. 后续附受控取消的未评估和L5大整数真实报告。微小/零/负显示由组件测试另证；不人为给真实报告填入示意值。

人工结论：LOCAL_USER_ACCEPTED（2026-11-12用户明确回复），不是开发代签。五组生产结果仍交华为机验收。

## 门槛与未决事项

五组HTTP与重启后浏览器通过；190项公共层/低命中单元、42项集成、13项修复回归通过，前端363项/类型/lint与后端类型/schema通过。完整设计对照与原失败→修复/验证方法纠正→复验链见 [执行记录](REPAIR_BATCH_EXECUTION_20261111.md)，原FAIL证据均保留。


## 大数据与受限资源证据

两模型分别导入1200/12000条长请求，完整父监控产物保留，异常分析自动缩样并完成实算。实际RLIMIT_AS=1,395,864,371字节下：

| 模型 | 父N | 实际样本N | 诊断峰值MB | 编码次数 |
|---|---:|---:|---:|---:|
| DeepSeek | 1200 | 151 | 286 | 302 |
| DeepSeek | 12000 | 151 | 286 | 302 |
| Qwen | 1200 | 188 | 530 | 376 |
| Qwen | 12000 | 182 | 529 | 364 |

Qwen实测模型进程开销略不同，自动收紧后样本数不同；独立核验确认上限严格符合原校准公式，读取/编码受所选样本控制。无mem_limit、无自动full或分析硬时限。本机测量不是对任意不足内存环境的保证，也不是整机cgroup测试。

## 真实额外状态

- [无变化，无可执行clock方案](http://127.0.0.1:18002/#/analysis?direction=low_hit&mode=history&task=diag-d184ccb81cc1458e98811290cea7ab23)
- [L5大整数及JSON原文](http://127.0.0.1:18002/#/analysis?direction=low_hit&mode=history&task=diag-58796615ff974d509c6b4359f2c2e32e)
- [主动取消，尚未评估而非0](http://127.0.0.1:18002/#/analysis?direction=low_hit&mode=history&task=diag-112e9ca125a7482489af3df59a538309)

0.5/零/负值为组件测试覆盖，未将演示数值写进真实报告。旧V2/V3/Token使用隔离fixture回归，现场真实旧state未验。

## 启动与证据

- 当前服务PID **411591**，端口 **18002**；仍使用独立`c04-e2e-02/state`。重启后12份已有报告、118个本轮输入/监控文件摘要不变，固定资源只新增4任务。
- 可复现命令见本轮`c04-e2e-02/server-restart-01.json`，实际启动参数为 `.venv/bin/python -m tokenscope.cli --input-root <本轮>/c04-e2e-02/inputs --state-root <本轮>/c04-e2e-02/state --asset-root /home/zhangxiyue/TokenScope --cpu-budget 2 serve --host 0.0.0.0 --port 18002 --viewer-root <本轮>/c04-dist-01`。`<本轮>`为项目内`artifacts/validation/development-v3/repair-c01-c04-20261111T184136`绝对路径；不要同时启动第二份服务。
- `candidate.json`保存源码/dist摘要，主样本inputs manifest保存生成身份，prepare calibration保存模型asset身份，monitoring runtime保存revision/encoder配置。本轮`CLOSE.json`汇总技术状态。
- 用户本机人工已通过；五真实业务现场收益仍ON_SITE_PENDING。显式full/Token新规则未实施；镜像线打包/Git已获授权，实际执行尚待其记录。
