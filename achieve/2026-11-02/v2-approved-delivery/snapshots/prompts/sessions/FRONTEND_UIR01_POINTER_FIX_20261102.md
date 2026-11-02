# UIR-01 鼠标读数继续修复 prompt

继续维护 TokenScope 已批准 UI，项目 /home/zhangxiyue/TokenScope。先读 AGENTS.md、memory/CURRENT.md、memory/SESSIONS.md，登记本人实际ID，再读 docs/tasks/delivery/APPROVED_UI_FIXES_INDEPENDENT_REVIEW_20261102.md。保留其他session修改，只改本问题，不重新设计。

当前候选 viewer-approved-ui-review-fixes-20261102-c2，HEAD 9f2a3e60394327e4e6bdc41bd688497ddef21dd7 加未提交修复。原交接 docs/tasks/viewer/monitoring-v2/APPROVED_UI_REVIEW_FIX_HANDOFF_20261102.md，SHA256 816173b4720b918adfc178522f0ee3a2c12f20dd0e4eb0d5a55f37d022c48ae9。不要覆盖该交接和c2证据。

独立复审：UIR-02键盘跳转及附带排行恢复修复已通过；UIR-01轴/颜色/刻度、键盘精确读数及1005条分段已通过，但宽窗口鼠标会选错点，因此UIR-01仍未关闭。222单元组件、81不同浏览器及120地址重启通过不能豁免这个实际缺陷。

## 复现与原因

1. 用有效新合成运行打开用户监控，将浏览器viewport设为1920×1080，选择“降序明细 · 辅助视图”。保持批准的三列图布局。
2. 把鼠标移到“输入重算长度”的第一个真实圆点。审查方30条合成运行的预期是排名#1、synthetic-0、源记录1、418 Token，实际读数变为排名#4、synthetic-3、源记录4、162 Token。前两指标也错选为#4，只是相等Token值掩盖了问题。
3. 审查方原样例路径为 /#/users?run=ur-37edc04cc5ab4d648b839fabc148c78b&appid=synthetic-app-1；仅用于报告保留的同版本state复现。新版必须新建state及运行，从新fixture获取ID，不硬编码旧ID。
4. 另一条有效深链接 /#/distributions?run=c382d269-879a-4d04-837a-7c06680f9e8c&appid=synthetic-app-1&model=GLM-5.2：第1点220,072读成第2点200,072；第12点92读成第11点535。三个指标都复现。1440/390宽对照正常。

独立证据在 artifacts/reviews/approved-ui-fixes-independent-20261102：user-pointer-1920.json、user-pointer-1920.png、pointer-regression.json、pointer-first-point-1920.png，以及可运行的user-pointer.cjs/pointer-regression.cjs。36个坐标检查中6项失败，均为1920宽三图首尾点；另有用户主页面3图首点独立失败。没有网络替身或数据改写。

源码 apps/viewer/src/features/requests/Requests.tsx 第49行 onPointerMove 按整个SVG bounding box宽度线性映射到viewBox。三图受既有CSS固定height:220px约束，1920宽时SVG元素504×220，但viewBox400×220按默认等比居中显示，左右各52px留白。绘图变换含这段平移，鼠标换算没有扣除，导致错点。不是后端排序、缓存或精度问题。

## 修复边界与要求

将客户端指针坐标准确转换到SVG实际用户坐标系后再定位本段最近数据点；可使用实际screen CTM逆变换或等价正确方法，同时考虑缩放、留白、滚动、窗口resize及转换不可用的防护。不能靠固定偏移、改成拉伸、限制窗口宽度、隐藏鼠标读数或另做图表样式来绕过问题。

保留已恢复的UI-02坐标/网格/灰蓝-蓝-青颜色、精确整数、当前段绝对排名、每段≤1000、空/0/单点/错误重读、键盘左右读数和请求明细的原辅助图。保持四入口、已通过的skip与排行恢复、c5固定历史run、FS-01、L4/L5各一卡≤3例、T2–T4、缓存/SSE/取消与导出校验。后端、契约、锁、S0、模型资产不改。

## 自测与交回

- 新增真实浏览器回归，在1440、390、1920宽核对三个指标首／中／尾实际点；补resize后复测、实际请求明细辅助图以及1005条第二段。对准实际渲染圆点，期望由该点对应的真实API行决定，不能复用实现里的错误坐标公式生成期望。排名、hash、源记录、精确Token都要匹配，不能仅比较可能重复的Token值。
- 当前c2应能使新增断言失败，保留负向证据；修复后通过。键盘/UIR-02、排行往返与范围保持的既有断言继续保留，不能删断言换通过。
- 按用户要求先盘点并停止旧TokenScope服务/worker/测试容器，核实退出与端口释放；使用新候选dist、新空state、真实合成结果及全新浏览器。审查方本轮服务结束会关闭，开工时仍需重新盘点。旧state/包/日志不删，不误停其他项目。
- 运行typecheck/lint/单元组件/build及受影响浏览器回归，保存命令、失败/复测、宽屏/窄屏截图和实际HTTP摘要。独立复审会再次冷启动，不直接复用你的现场。
- 新建候选ID、证据目录和 docs/tasks/viewer/monitoring-v2/UIR01_POINTER_FIX_HANDOFF_20261102.md，记录改动文件/SHA、复现与修复、测试与视觉结论、18项保持、服务PID/argv/env/state/HTTP资源、未决；原交接/证据保持。更新自己的入口/记忆，释放编辑窗口后交镜像打包与审查session 01a1800e-80b4-7400-a78b-a84f5b6e888d 独立复审。

**暂不提交、合并、推送，不构建Docker，不生成镜像或代码交付包。不要宣称用户视觉认可；复审通过也不自动取得发布授权。**
