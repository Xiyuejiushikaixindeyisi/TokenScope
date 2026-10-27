# F005 闭环

状态：closed（2026-10-27用户批准内存门槛修订后）。已实现两格式Worker增量校验、有界流式写入、结束验证后close、失败abort、单次导出和取消、16MiB完整验证后Blob备用路径。概览和明细提供固定scope全量/筛选导出，CSV不冒称SHA校验。

142项单元组件、typecheck/lint/build/67 DTO生成检查通过。真实Edge Worker+受控文件选择器返回持久化OPFS WritableFileStream验证真实写盘、字节一致、close/abort、慢写/模拟磁盘错误/断网/坏摘要/截断/空导出、16MiB精确边界和+1byte、单记录>1MiB拒绝。

256MiB/1GiB各3次内存增量分别[70656000,69140480,70246400]和[161591296,142299136,155541504]bytes；最大154.1MiB，均≤256MiB。4倍文件的中位增量比2.214，不近似等比例增长，未证明严格常数内存。初拟2倍判据未经论证且不是用户原要求，现明确采用<3倍检测界线，完整记录在ISSUES与主设计。64MiB仅优化目标。应用在途写数实际峰值1，64KiB BYOB/Worker复用缓冲。

证据artifacts/validation/viewer/F005/{final,recheck,acceptance-memory.json,source-manifest.json}；final一次因开发服务器HMR导航失败，recheck同用例通过，失败保留。底层文件选择UI为受控替身，不冒称操作系统对话框人工验收；后端真实联合另行执行。未改S0、未打包。

自主进入F006。回退可撤下导出入口，不清理回执/用户文件；保留所有失败证据。完整前端尚待F006。
