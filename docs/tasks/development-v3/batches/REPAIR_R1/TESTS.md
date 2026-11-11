# REPAIR_R1 TESTS

证据根artifacts/validation/development-v3/REPAIR-R1，每attempt独占。旧独立验收输入只读复制到新目录；未改其state/报告。

- attempt02：新正常worker7例+候选3例，6 passed4 failed，19.06s；失败为union wire读取，原日志保留。
- attempt03：mypy/typecheck通过；旧frontend5例2 passed3 failed，缺新增可选字段默认；ruff剩行长，已修。
- attempt04：新/旧worker及候选13 passed5 failed，61.47s；clock Pointer4与CCH相同输入1，均已定位。
- attempt05：旧frontend5通过。
- attempt06：新非clock7、原clock8、候选3共18 passed，60.10s；包含实际DeepSeek/Qwen编码与正常prepare/diagnose/API，不手填recipe。新增报告wire fixture用于前端回归。
- attempt07：ruff/mypy142/typecheck/eslint通过，viewer352 passed7.34s；独占dist。
- attempt08：全Python回归正在运行，未签通过。
- B007/repair-r1-01：最终真HTTP/浏览器10场景正在运行，clock三例+独立原六CSV+专用L5；身份/截图/指标/退出记录另存，不能拿中间截图签全过。

## 最终候选已完成部分

- attempt09：20 passed7 failed22.73s；7项旧评估器单测用SimpleNamespace绕开新类型分派，测试替身错误，原断言保留；改为最小类型实例并对clock/prefix双分派覆盖。attempt10：24 passed0.43s；attempt11：38 passed63.09s（含7场景×A-only/A+B、守恒/原文/去重/有界证据/状态）。
- attempt12：旧browser12 passed18.4s；四入口/历史失败保留/断线与storage兼容。无额外跳过。
- attempt13：最终ruff/mypy142源码/两schema --check通过；H0 wire SHA原值不变。
- 最终E2E为B007/repair-r1-02，源码manifest SHA `1fb8c3dc6a03dc49ddeb4c4cbc8b260c4ebc79e1cc60cfe04dcdcc5ee2fad820`，302源码文件；与原attempt15相比10个产品文件变化，列表final-check.json。前端独占attempt07/dist，产品源码测试后hash未变。
- 三clock+六原独立CSV+专用L5合计10真HTTP/浏览器场景通过；20 POST仅显式prepare/diagnose，浏览/刷新重连0新增。独立literal-prefix oracle核9个完整窗一致；重启新浏览器10历史报告、方向切换无POST，报告SHA不变；服务/预览18002/4173释放。最终L2和L5截图已人工核完整修改/原文/人数去重。
- 同六独立CSV只读复制摘要已核一致（independent-input-copy-sha256.json）；旧输入/state不改。没有预置finding/recipe，没有开放旧无界执行。

最终大源2200自动A272+B272，两窗完整实算、无mem_limit/forced termination，诊断10.910s，监督采样RSS295075840 bytes；资源压力变化导致选择数不同，不冻结为默认。L4独立原因代表达到128，报告明确CAUSE_EVIDENCE_TRUNCATED和discovery.complete=false；A/B评估完整与证据覆盖不完整分开。10场景全部execution completed/exit0。详resource-summary.json。

合成参考（非华为）：CCH0pp且source_change_input_identical；普通日期1850/131 pp；workspace24900/2227 pp；工具排列800/403 pp；description20800/10341 pp。工具增删/L5仅差异证据、没有伪造recipe或收益；小8条窗无不重叠B明确unavailable，B实验另由attempt11验证。

## 全套Python原始结果

attempt08 `pytest tests`：**895 passed / 7 failed，853.70s**。七项全部为已定位R1-10旧SimpleNamespace评估器替身；该进程启动时已加载旧测试，修改文件不会让在途进程重新收集。不得将这次原日志标全绿。修正后的双分派状态及最终原因去重已在attempt10（24 passed）和attempt11（38 passed，含真实A+B）通过，另用attempt14完整tests/unit做最后复验。全套其余真实资源/恢复/监控/MA/旧报告集成通过；V3最终产品变动（去重）另由最终10场景/38项直接验证。原B007的历史skip/lint/证据损失仍单列，不能擦除历史。

最终attempt14完整tests/unit：**663 passed，71.56s**，只有第三方Starlette deprecation warning。最终源码摘要再次核一致，无pytest/TokenScope CLI残留，18002/4173关闭，见final-after-tests.json。
