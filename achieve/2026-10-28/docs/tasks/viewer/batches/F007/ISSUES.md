# F007 问题记录

2026-10-28：实现问题已修复，用户人工验收通过；打包前审查仍pending。

| ID | 问题/根因 | 修复与复测 | 状态 |
| --- | --- | --- | --- |
| F007-I01 | 横向导航、七卡四列偏离审批HTML | app.tsx/base.css/Overview.tsx还原左侧导航、六卡、去向条；144项回归和视觉截图核对 | resolved |
| F007-I02 | 大块“当前完整结果”阻断指标与图表 | 元信息入filter-meta，详情按需展开，导出入标题菜单；真实服务详情/校验下载通过 | resolved |
| F007-I03 | 旧功能通过不能证明视觉通过 | VISUAL_ACCEPTANCE独立维护，人工通过前不closed | resolved / 2026-10-28人工通过 |
| F007-I04 | 4175等旧预览可能混淆版本 | HTTP主页与dist/index逐字节核对；验收URL8000，资源摘要固定 | resolved |
| F007-I05 | 首轮full-journey仍定位被取消的“当前范围”文本，5通过1失败 | 改为.metadata-body内run身份断言，保留原子切换/冻结/离线/schema断言；单独复测和最终8场景通过 | resolved |
| F007-I06 | 初次独立视觉测试发现390px导航宽度0，继承原型display:none | 窄屏保留紧凑可换行导航，避免功能不可达；390px/长appid与文件名检查通过 | resolved |
| F007-I07 | 对照截图发现图形留白过多、分位数/众数位置不同、无type表单输入未统一样式 | SVG调整显示坐标与网格（数据/点击范围不变），分位值三列、众数上移、表单CSS统一；最终构建与视觉只读复测通过 | resolved |

首次失败保留于artifacts/validation/viewer/F007/functional/browser-first和visual；复测在browser-recheck/browser-final、visual-recheck/visual-final/visual-acceptance，最终补跨appid检查在visual-scope-check。没有后端契约改动，没有降低测试门槛。

后续审查提示：后端维护的joint*.spec.ts仍有旧UI定位（“当前范围”、七卡精确字符串等），本批未擅改其测试。新审查session按新可见详情/精确值适配定位，保留原断言语义；旧脚本未重跑，不宣称新UI再次通过完整联合。此项是审查交接事项，不是已知业务功能失败。
