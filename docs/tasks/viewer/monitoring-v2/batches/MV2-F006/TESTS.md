# MV2-F006 验证记录

2026-10-31。正式React/TypeScript前端、真实本机后端独立state、合成CSV；Windows Edge经Playwright驱动。未访问生产或华为环境。

| 验证 | 结果 / 证据 |
| --- | --- |
| typecheck / lint | 通过；日志在artifacts/validation/viewer/monitoring-v2/MV2-F006 |
| 完整Vitest | 14文件159项通过，含旧S0、状态/取消、60秒/终态/失败保留、精确数值、4并发、本机隔离/损坏记录 |
| 联合Playwright | **25项通过（56.0秒）**；14项V2与11项V1兼容；[最终日志](../../../../../../artifacts/validation/viewer/monitoring-v2/MV2-F006/browser.log) |
| 本地Vite构建 | 通过；只验证dist，不构建Docker/交付包；主包体积提示见ISSUES |
| 视觉 | 人工对照UI-02；1440×1000桌面、390×844窄屏；表格内部滚动、面板/弹窗布局、无页面横溢出 |

## 要求→接口→测试

| 要求 | 主要接口 | 验证入口与事实 |
| --- | --- | --- |
| 用户三模型、历史与新建/绑定 | user runs/bindings + S0 snapshot | v2-acceptance / v2-submission；三模型真实发布读取；独立S0历史base绑定；已由用户提交预留的base正确拒绝 |
| 60秒、终态停止与历史保留 | 两线GET runs | v2-task假时钟；v2-acceptance浏览器时钟59,999ms不查、60,000ms查、失败后不再查；真实提交完成后由周期展示；两线失败/中断后刷新仍恢复历史 |
| 同key恢复、身份隔离 | POST runs / submissions | v2-api / v2-submission；真实服务器已受理后模拟丢响应，原key恢复；v2-acceptance身份409清范围且无自动POST |
| 搜索/范围/精度/分页 | rankings / modes | v2-ranking真实后端查询；v2-boundaries合成严格DTO投影验证20+5页、大整数、NULL、revision冲突、25个并列箱跨200K；v2-numbers精确转换，不宣称前端测试重新验证后台全局统计算法 |
| 新TTFT与旧历史 | scenarios / evaluations | v2-ttft真实登记、缺W/明确0、比较符变更失效、迟到响应不覆盖；v2-boundaries真实旧W+O只读、0%/100%/无预算、O混入422、缺W422；历史W不回填新条件 |
| 全UUID与4并发 | MA catalog / instances | v2-ma真实13 UUID；模拟单行网络失败后真实重试；v2-pool严格最大4并发、取消后无新任务或旧发布 |
| MA边界与质量 | instances / quality | v2-ma + v2-ma-boundaries真实预热冲突/empty_file；仅pre、无pre、真实缺值、编码无效、零未命中、输入计量差异；趋势12桶、独立分布箱宽、质量整次运行不按UUID虚构归属 |
| V1兼容 | S0读取/设置/导出/缓存 | monitoring、full-journey、operations、export-fixture、cache；共11项，含Worker字节验证、IndexedDB/CAS/旧发布切换 |

## 截图

[用户桌面](../../../../../../artifacts/validation/viewer/monitoring-v2/MV2-F006/user-viewport.png) · [用户窄屏](../../../../../../artifacts/validation/viewer/monitoring-v2/MV2-F006/user-mobile-viewport.png) · [情景二级表单](../../../../../../artifacts/validation/viewer/monitoring-v2/MV2-F006/scenario-desktop.png) · [MA桌面](../../../../../../artifacts/validation/viewer/monitoring-v2/MV2-F006/ma-desktop.png) · [MA窄屏](../../../../../../artifacts/validation/viewer/monitoring-v2/MV2-F006/ma-mobile.png)。原UI-02截图只作为布局参考，不替代真实数据截图；长页面另存fullPage图。

复现命令与前提见[源码地图](../../CODEMAP.md)。原型、真实HTTP、模拟故障/DTO和现场证据严格区分；本批没有现场验收结论。
