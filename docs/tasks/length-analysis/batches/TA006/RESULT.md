# TA006 资源、恢复与后端交接

2026-10-31：closed，本线TA000–TA006本地后端实现与验证闭环。最终`pytest tests/unit/token_content tests/integration/token_content -q`：**112 passed / 40.03s**（103 unit、9 integration），ruff通过，mypy本线12模块通过。跨方向组合另在联合95项执行通过；公共监控广泛回归由公共维护方记录，不将其结果算本线自测。参数错配独立，未打包部署。

已执行预算小于/等于/超过需要量（请求字节、单元、比较字节、重复候选、深度）15项，提取中取消与新重试独立1项，合计16 passed/0.06s。不会把超预算未检查写成无问题，停止位置保留。

真实任务恢复新增2项5.09s通过：排队取消不执行、运行中取消无成功报告、新attempt保留旧封存报告且不重复计数；临时源fixture摘要变化在Token运行前阻断，恢复fixture后原报告仍可读。最终112项包含这些检查。

九档纯Token独立进程资源测量及固定显式配置见[BENCHMARK.json](BENCHMARK.json)、[MACHINE.json](MACHINE.json)、[资源说明](../../RESOURCE_PROFILE.md)。最大测量单请求819280字节、1000个重复单元；固定32KiB请求1/10/100条峰值RSS约34MiB，没有整appid原文积存。单次合成测量不作现场SLA，未测真实150k负载或最大8MiB编译输入的吞吐。

已补完整证据、计算身份fragment_index、available评估逐请求rows消费；实际raw修改/guard清单、P/H/C与IDs摘要可分页只读，外部evaluation引用拒绝。引用修改P下降/C增加与零效果均真实保留。最后受影响组合106 passed/14.68s，随后完整本线112 passed。

交接入口：[IMPLEMENTED_API](../../IMPLEMENTED_API.md)、[BACKEND_HANDOFF](../../BACKEND_HANDOFF.md)、[CODE_IDENTITY](CODE_IDENTITY.json)。所有结果为本机固定资产与合成fixture；前端视觉、现场、容器、打包部署未执行。共享工作树未擅自整库提交/推送，统一Git集成与审查由主线协调；本线代码与摘要已可复核。回退可禁用Token插件注册，历史源/报告不改写。
