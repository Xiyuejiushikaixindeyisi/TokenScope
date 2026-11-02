# 用户监控来源跳转修复交接

2026-11-01。异常分析前端维护`01a19111-344a-75c1-84e0-14db8be08f4f`按完整服务总负责`01a1800e-80b4-7400-a78b-a84f5b6e888d`派发执行。状态：本线修复与验证完成，交总负责独立复审；未commit/push、未Docker构建、未更新冻结发布。

## 问题与改动

总负责在冻结45d9285／镜像483db762的完整服务合成E2E发现：`user_v2`来源的“查看原报告监控来源”写入`#/users?user_run_id=...`，而用户监控读取`run`。冷浏览器没有展示运行，已有最近记录时可能回落另一运行。原失败证据：`artifacts/reviews/full-service-synthetic-20261101/additional-analysis.log`及其trace。

业务源码仅`apps/viewer/src/features/analysis/SourceLink.tsx`一行，将URL键改成监控既定`run`；原APPID、receipt的base_run_id/common_name/model_id核验、AbortController和迟到保护全部保持，base来源仍为`#/overview?run=...&model=...&appid=...`。没有修改监控前端、后端、冻结接口或UI布局。

## 已验证

| 层次 | 结果 |
| --- | --- |
| 类型/静态 | typecheck、lint通过；最终浏览器选择器调整后再次通过 |
| 单元/组件 | 23文件203项通过，含新增8项：user参数与原APPID，base来源，三种来源身份错配，旧receipt迟到不可覆盖新来源，卸载后的contract/base迟到不可导航 |
| 真实浏览器 | Chrome对独立生产候选dist，代理同一18062真实后端；3项通过/9.5s：冷浏览器来源+刷新、已存在另一最近运行+来源+刷新、base来源概览回归。业务接口请求全部GET，未创建/修改后端任务 |
| 构建 | 候选dist输出独立artifacts目录；共享apps/viewer/dist逐字节未变，不重启4191或18062，不操作Docker |

实例`f99cb514-ba26-4846-9c1e-6382f0b655f1`；原用户报告`1a0727b1-5d69-4413-a24e-92c02d4afd5e`，user_run`ur-e409fc1a87ef4bcebcee168fcf20d51b`、APPID`search-long`；不同最近运行`ur-058351bac38247dbb36ae805c9d552c4`、APPID`synthetic-app-1`；base来源报告`c13f2596-9d99-4149-a7c8-e00930e38480`。完整绑定和固定证据见本线fixture，不复用旧RV1 ID冒充此轮现场。

首次新增浏览器探针出现2个strict-mode失败：成功加载后用户与隐藏排行同时存在`.filter-meta`。已将选择器精确限定到含“展示运行”的条目，保留原run、APPID、刷新、最近运行和只读断言；初次失败日志/trace不覆盖。总负责原additional-analysis第二项复测也应限定该条目。组件测试编写期类型/未使用变量问题已修正，业务源码始终只有一行变更。

## 命令与候选

在项目`apps/viewer`下，Node22.22.2/npm10.9.7：

```sh
npm run typecheck
npm run lint
npm test
npm run build -- --outDir /home/zhangxiyue/TokenScope/artifacts/validation/viewer/analysis/source-link-20261101/dist
TOKENSCOPE_BACKEND_URL=http://127.0.0.1:18062 npm run preview -- --host 127.0.0.1 --port 4196 --strictPort --outDir /home/zhangxiyue/TokenScope/artifacts/validation/viewer/analysis/source-link-20261101/dist
```

Windows Chrome真实浏览器执行使用独立4196预览，环境变量`TOKENSCOPE_BROWSER_EXECUTABLE=C:/Program Files/Google/Chrome/Application/chrome.exe`、`TOKENSCOPE_EXTERNAL_PREVIEW=1`、`TOKENSCOPE_TEST_BASE_URL=http://localhost:4196`、`TOKENSCOPE_SOURCE_LINK_FIXTURE=../../artifacts/validation/viewer/analysis/source-link-20261101/fixture.json`：

```sh
node node_modules/@playwright/test/cli.js test tests/browser/analysis-source-link.spec.ts --workers=1 --reporter=line --output ../../artifacts/validation/viewer/analysis/source-link-20261101/browser-final-results
```

本线测试以既有报告fixture为只读输入；未设fixture时显式跳过，不能将skip算作通过。完整日志/输入身份/初次失败/最终结果位于`artifacts/validation/viewer/analysis/source-link-20261101/`。

候选dist：[目录](../../../../artifacts/validation/viewer/analysis/source-link-20261101/dist/)。[精确文件/源码/测试/dist及证据SHA256](SOURCE_LINK_FIX_20261101.json)。候选不是新的已发布镜像；总负责可将它只读挂载到已验镜像复测同一state，再独立决定新源码提交和交付版本。冻结版本清单、原镜像、发布包及SHA256SUMS不改写。本线CURRENT/SESSIONS未修改。
