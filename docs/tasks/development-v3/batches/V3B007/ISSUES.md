# V3B007 ISSUES

状态：**尚未实施，无运行缺陷复现记录**。下面是设计阶段已知风险，OPEN_DESIGN_RISK不等于已实测bug。关联[PLAN](PLAN.md)、[TESTS](TESTS.md)、[CLOSE](CLOSE.md)。

| ID | 类型 / 状态 | 风险与待解决事项 | 处理与关闭证据 |
| --- | --- | --- | --- |
| V3B007-I01 | DESIGN_RISK / OPEN_DESIGN_RISK；实施退出门禁相关 | **本地与现场证据断层**：本地合成验证不是五组业务数据实测；本地结束不能伪报V3完成，分LOCAL_VALIDATED与CLOSED。 | 待实现/验证；关联T24、T25、T26、T27、T28、T29、T30，当前无修复/复测。 |
| V3B007-I02 | DESIGN_RISK / OPEN_DESIGN_RISK；实施退出门禁相关 | **旧进程/旧dist污染**：必须核退出、唯一候选/new state/new browser与HTTP身份；不能只是改端口或清浏览器页面。 | 待实现/验证；关联T24、T25、T26、T27、T28、T29、T30，当前无修复/复测。 |

新增实际问题沿用稳定编号，记录：发现批次/候选、类型（CODE_BUG / ENV_BLOCKER / EVIDENCE_GAP / BUSINESS_CONSTRAINT）、严重度/是否阻断、复现命令/输入身份、预期与实际、根因、修复文件/函数、相关设计变化、首次失败与复测证据、状态/关闭人依据。不得在关闭时删除原失败记录。

关闭需要对应测试通过或明确可核业务决定；“解释了风险”不能关闭功能/资源缺陷。仅设计风险经测试证明不存在时可写VALIDATED_NOT_REPRODUCED并给证据，不虚构修复。业务局限与bug分开，agent不能替用户接受五组底线豁免。

当前实际issue结论：**NOT_EVALUATED**；尚无产品运行或修复。


I01 ENV_BLOCKER / FIXED_PENDING_RETEST：attempt02正常生成三组监控源后，Chromium启动缺libnspr4/libnss3/libasound2，浏览器exit127，未进入产品链路；finally正常停止server并确认18002释放。通过apt-get download下载三库至项目env/browser-deps-v3，dpkg-deb仅解包本项目、不改系统；摘要manifest.json，浏览器局部LD_LIBRARY_PATH接入。复验用全新attempt03，不复用失败state或覆盖证据。

I01 FIXED_VERIFIED：attempt03 Chromium正常启动，三场景真实页面链路通过。截图发现中文字体缺失，已配置项目内字体供本地浏览器验收，不修改产品字体/系统。
I02 CODE_BUG / FIXED_PENDING_E2E：attempt03截图同时发现旧目录EXECUTION_CAPABILITY_MISMATCH。旧前端只接受directions=[low_hit,token_content]，未接受V3刻意关闭旧执行后的空列表；增加仅execution_enabled=false且directions=[]的只读兼容分支，其他版本/schema/资格校验不变。attempt04新增正负能力测试与旧页面+新样本组件共33 passed，重建独占dist。下一次完整冷启动用attempt05，不能把03整体标无缺陷。

## 最终闭环（前述“尚未实施”为原始模板历史，不是当前状态）

原设计风险I01（本地/现场）保留ONSITE_PENDING；I02（旧进程）已核退出并最终冷启通过。早期追加的同号运行问题按下面运行编号区分，不删除原记录。

| 运行问题 | 结论/证据 |
| --- | --- |
| RUN01 浏览器库/中文字体 | 项目内隔离依赖解决；attempt15截图可读，不引入产品字体/系统改动。 |
| RUN02 只读空directions能力误报 | execution.ts仅接受execution_enabled=false的空列表；启用但空/版本错仍拒绝。attempt14/15复验通过。 |
| RUN03 全pytest16个预算失败 | 父pytest模型缓存RSS超合成profile；test_every_budget_before_action_boundary_and_total仅隔离其无关current_rss，真实worker内存测试不放宽。attempt09、全unit653通过。 |
| RUN04 H0冻结wire SHA冲突 | 将typed-map扩展移到wire_v3.py，wire.py恢复原SHA 1cae6722ce0a708fbf4ac6d920cd209dbd9d9f14e00bb77c11c44dd321d2ca63；旧manifest未改，新路由/导出使用扩展。H0复验及两schema --check通过。 |
| RUN05 历史browser额外alert/懒加载 | mock为新URL错误返回H0能力；改404，产品旧服务404显示不可用。新增面板导致证据需滚动触发，测试按真实懒加载滚动；attempt14全部12通过，未删除断言。sessionStorage不可用也保留读取。 |
| RUN06 测试启动/编排错误 | attempt13漏Chromium路径；attempt15第一次restart误用service_instance_id而非candidate.instance。失败均记录，未覆盖；14及restart-02通过。 |
| RUN07 lint | 本线验证脚本2行长修复，最终范围ruff通过；旧analysis_frontend_server.py八项历史风格问题保留，不扩改旧线。 |
| GAP01 | source-link专用browser3项无fixture跳过；不冒称通过。旧生产默认报告读取2项及相关组件/浏览器已复验。 |
| GAP02 | BUS01–05真实收益由华为机验收，本地NOT_RUN；不承诺正收益/业务无损。 |
| HISTORY | B002-I04历史scale三文件原内容未恢复；此损失不可用新结果替代。B007测试预查固定输出并隔离tmp_path，未再覆盖历史证据。 |
