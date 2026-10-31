# 监控V2修复独立复审 · 2026-10-31

结论：**本轮监控V2候选复审通过，RV2-01/02/03关闭**。适用范围为已审查监控后端基线与本次前端修复；不包含共享工作区尚未纳入本轮的异常分析后端/公共入口改动。按用户本轮授权进行main提交推送，暂不交付打包。

审查session：01a1800e-80b4-7400-a78b-a84f5b6e888d，本轮环境再次核实。输入：[前端修复交接](../viewer/monitoring-v2/REVIEW_FIX_HANDOFF_20261031.md)；原[首次评审](MONITORING_V2_REVIEW_20261031.md)和原证据保持不变，本报告记录新候选复测结论。

## 候选及隔离

- 基线HEAD：5c619f80631dbd0efdcbadffa7eedbf314bb678e；前端21个修复/测试文件由工作区接收。
- 前端交接152个路径摘要全部匹配，聚合6202ff3db40686320b7ec194a855fcce5a35560abb35808fc56267387662884d；依赖锁未变。
- 本轮源码服务使用从HEAD逐文件提取的监控后端，避免把其他会话的api/app.py、cli.py及未提交analysis模块带进候选。临时Docker上下文同样以该后端逐文件摘要覆盖对应文件；未改共享工作树后台源码，未清理其他会话工作。
- S0/用户2.0.0/MA1.0.0、UI-02及实际模型资产120个不同路径摘要均匹配。接收时前端无漂移；复审仅追加1处浏览器测试时钟暂停，业务源码不变，final-candidate.json记录最终测试摘要，旧评审14项证据摘要未变。
- 证据根目录：[artifacts/reviews/monitoring-v2-rereview-20261031](../../../artifacts/reviews/monitoring-v2-rereview-20261031/)。frontend-candidate.json、backend-sha256.json、identity-verification.json、status-before.txt记录候选及背景；没有将历史应用包名dev6/F007当作充分V2身份。

## 三问题关闭证据

| 问题 | 源码核查与独立复测 | 结论 |
| --- | --- | --- |
| RV2-01 | V2Client识别两个既有身份错误码并同步取消lifetime；请求池绑定同一signal；连接代次阻断旧连接回写。真实后端409注入覆盖目录/快照/回执、在途和排队请求；无自动POST；普通断网/503仍保留历史。原审查脚本再次确认旧MA行数0、重连按钮1 | 关闭 |
| RV2-02 | Exports按identity/filter/sort隔离，顶层按user_run绑定，离开用户页卸载导出；旧回调不修改新组件，下载前检查取消。NDJSON/CSV × 下载/文件API替身 × 运行/APPID/身份/页面切换均通过；正常、摘要/行数错误、网络失败和主动取消断言保留。原脚本确认旧导出无下载、无新范围成功提示 | 关闭 |
| RV2-03 | 初始化和相同搜索不建重置timer，Enter/新生效条件清理旧timer。固定时钟先翻页后推进300ms仍第2页，原脚本请求仅0→20；快速输入、299/300ms、Enter后翻页、原20+5/大整数/null/revision/众数跨页均通过 | 关闭 |

独立原复现脚本的本轮版本为extra.cjs、ranking.cjs；仅调整目标端口、修复后的期望与重连步骤，没有更改原证据。源码和容器各有extra-observations.json/ranking-reset.json，容器记录位于docker-browser子目录。原脚本真实导出响应仍由后端生成，排名边界仍明确是严格合成DTO投影。

## 本轮实际结果

| 检查 | 结果/证据 |
| --- | --- |
| npm typecheck / lint / test / build | 全部通过；16文件173项单元/组件；checks.json、test.log及各命令日志 |
| 完整选定源码浏览器集合 | **51项一次执行通过**；browser-final.log、browser-final-results |
| 本机正式dist容器 | **39项一次执行通过**；docker-browser/browser.log、results；冷state直接运行，无旧任务依赖 |
| 原审查独立复现脚本 | 两环境均通过修复后期望；extra-observations.json、ranking-reset.json |
| 容器读取与重启 | **115个读取地址**前后响应摘要一致；控制库logical dump摘要不变，GET未创建/修改任务；container-restart.json |
| 容器静态与冻结身份 | 4个静态资源与本轮dist逐字节一致；healthz/readyz成功，120项身份匹配；environment-checks.json、identity-verification.json |

集合有重叠，不相加称独立用例数。原后端381项全量回归属于首次评审，本轮后端保持同一基线，不把旧测试冒称重新执行。前端修复涉及共享Exports，因此本轮源码集合仍包含V1 Worker导出、缓存、CAS及完整旅程回归。容器39项排除依赖Vite动态/src导入的v2-api和开发harness，使用正式构建静态文件与同源真实HTTP。

源码完整集合第二轮50通过/1失败：60秒轮询用例未暂停模拟时钟，安装后实际页面操作耗时叠加59,999ms跨过截止点。审查方仅在创建待测任务前pauseAt，保留全部59,999/60,000ms、失败保留及终态停止断言，随后重新执行完整集合；原失败browser-corrected.log与trace保留。容器重新执行受影响acceptance集合，产品镜像字节未变。

初次隔离源码服务未显式传asset-root，模型资产按复制模块目录推断，返回INVALID_ASSET_LOCK，已中止该轮。修正为`--asset-root /home/zhangxiyue/TokenScope`后使用新的state-corrected重跑完整集合；未改产品、测试断言或延长超时。初次browser.log、state及environment-correction.json保留，不算通过证据。Docker从开始即显式/app资产根，无此配置错误。

## Docker身份与运行边界

- 本机测试tag：tokenscope/local-test:mv2-rereview-20261031。
- image ID：sha256:0e14131c23266e03f899871687904b543a686a1cd623be25bd740303daaf1a95。
- 固定基础镜像：public.ecr.aws/docker/library/python@sha256:a36c24f9cbdf4fd0f52d67f0823eeac19c2028c637cecc392d97f980d4fec56b。
- 构建：[artifacts/builds/monitoring-v2-rereview-20261031](../../../artifacts/builds/monitoring-v2-rereview-20261031/)；context/candidate.json包含116个上下文文件摘要、前端修复聚合摘要、用户/MA契约及local-test-only用途；backend-sha256对应已审查基线。镜像基线标签不会单独代表未提交前端修复，须联合该manifest识别。
- 复用项目Docker26.1.4/Compose2.27.1，WSL linux/amd64、离线锁定wheel、build --network=none。非root1000:1000、只读根和输入、独立state，8CPU/32GiB，回环18052。构建命令、image/container inspect、compose展开和容器日志均保留。
- 源码服务18051/Vite14193；独立合成inputs/state-corrected。Windows Node24驱动Edge156，WSL Node22.22.2/npm10.9.7运行项目检查与构建。
- 文件API路径是受控showSaveFilePicker/createWritable替身，真实HTTP/Worker与浏览器下载路径另行验证；不宣称原生系统选择器及磁盘提交验收。真实性能校准、现场CSV、华为旧内核/资源/驱动及新异常分析业务均不在本轮通过范围。
- 本轮仅临时镜像，无docker save、交付代码包、交付manifest、发布tag、华为prompt或远端部署。测试容器及本轮服务收尾后停止，state、证据和测试镜像仅留本机；原8000/4173保留，详见cleanup.json。

## Git收口

本轮只提交21项前端修复/测试、监控审查与修复交接、监控入口/记忆。三端基础源码已是main祖先，无需重复merge；当前main直接提交修复后显式push origin main。公共CURRENT/SESSIONS按本轮监控段落暂存，其他会话异常分析源码、研究及状态保留在工作区，不混入本轮提交。backup分支及代码包/镜像包不推送。

实际提交与远端校验另见本轮Git收口记录，提交前核对索引内容与已测前端/后端摘要，避免“测试工作树、提交不同源码”。复审通过不等于已批准统一交付；下一阶段仍依用户安排。
