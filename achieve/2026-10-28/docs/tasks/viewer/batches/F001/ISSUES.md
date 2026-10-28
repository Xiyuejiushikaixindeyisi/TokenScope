# F001 问题记录

状态：F001已闭环，I01–I04均已处置；下文保留发现、暂停及修复历史。

| ID | 复现/影响 | 根因 | 修复 | 重测证据 | 阻断/处置 |
| --- | --- | --- | --- | --- | --- |

发现问题立即登记；已知契约依赖或不可用后端写明影响，不以占位成功解除门槛。

## F001-I01：完整接口类型和样例尚未固定

- 2026-10-27 只读核对：共享 MONITORING_VIEW_V1_DRAFT.md 第9节明确样例只含响应片段，完整类型/必填验证待后端S0固定；B005.1 PLAN 的S0仍为契约固定计划，CONTEXT仍标记未编码。apps/viewer仅有.gitkeep。
- 影响：F001生成DTO和边界校验需要完整字段、必填/nullable、成功/错误及R1/R2样例。不能把片段自行补成生产契约，也不能宣称后端已经确认边界。不是已发生的测试失败；测试尚未运行。
- 建议：后端先提供S0固定的机器可读schema（可先于运行版OpenAPI）、完整样例与R1/R2边界确认；无需等待整个B005.1完成。
- 备选：经用户明确允许，先做不依赖DTO的工程壳与基础函数，契约部分等待；F001仍不能关闭。
- 状态：未解决，等待用户裁决；未安装依赖、未新增源码、未改后端文件。

## 2026-10-27 S0 接收：F001-I01解除

用户提供S0_CONTRACT并明确继续开发。S0 1.0.0已包含完整Schema、设计OpenAPI、样例及R1/R2边界；全部S0_MANIFEST文件SHA核对一致，接收证据见 artifacts/validation/viewer/F001/startup/s0-reception.json。此前缺口解除，不等同真实服务实现或联合验收通过。

## F001-I02：环境检查命令的跨shell引用错误

- 查询Node/npm与候选依赖版本时，PowerShell到WSL的bash -c参数传递未正确保护PATH；其中Windows目录的空格/括号导致bash语法错误，退出码1。
- 命令未启动Node/npm查询，未安装依赖、修改源码或运行应用测试。WSL中已只读发现Node v22.22.2/v24.14.1目录，尚未完成版本锁定。
- 拟修复：通过标准输入传递脚本，在WSL内部正确引用PATH或使用绝对可执行路径，避免多层shell展开。无设计变化、无新增组件或测试。
- 按用户“遇到问题暂停”的约定停止开发，等待用户允许修正命令后继续。

### F001-I02恢复授权

用户回复“允许”，授权修正环境命令并继续。stdin bash仍受到CRLF影响（syntax error，非应用测试）；同一已授权修复改用Python subprocess参数数组，完全绕过shell引用与换行解析，Node 22.22.2 / npm 10.9.7已确认，npm官方registry查询正常继续。不增加产品组件。

## F001-I03：目录cursor语义校验缺失（当前阻断）

- 首轮npm run test：101项中100通过、1失败，tests/unit/contract.test.ts:36，非法cursor='not-a-cursor'未被拒绝。自动停止后续命令，build与浏览器未运行。
- 根因：S0 Schema将CatalogResponse.cursor约束为非空string；行为契约第3节另规定instance UUID:event_seq格式。前端目前仅执行Schema与请求scope校验，未实现这条语义约束。不是后端实际服务错误；所有75个S0 JSON样例均通过。
- 拟修改：在前端validateDto的CatalogResponse边界补充cursor格式与同响应service_instance_id一致性检查；序号非负十进制字符串，用BigInt比较时不丢精度，cursor原文仍不透明保存和回传。补充正常/非法/跨实例/大序号用例属于F001原定cursor边界测试范围。
- 不修改S0共享契约、不删除或降低失败断言、不新增组件。得到用户意见后才修复和复测。
- 证据：artifacts/validation/viewer/F001/startup/test.log及commands.json。

当前：I01解除；I02按用户允许修复（Python subprocess参数数组替代多层shell）；I03待用户意见。

## F001-I03已解决；协作约定修正

用户澄清普通测试失败应自主修复；不改设计、不增未知组件/类、不改后端契约。已在validateDto补cursor格式与同实例校验，保持原串；增加大序号/跨实例/换行等原计划边界，102项全部通过。

## F001-I04：WSL浏览器系统库缺失（验证环境，已处理）

Linux Chromium启动因libnspr4.so缺失退出，原失败日志/trace保留；未擅自安装系统库。复用已有Windows Edge及同一Playwright测试，以外部WSL preview运行，1项浏览器检查通过（含路由刷新、390px、无外部请求、无脚本错误）。配置支持显式浏览器路径和外部preview，为既定浏览器验证入口，不是新增产品组件。已验证Edge156.0.4314.42，构建Node22.22.2、Windows测试runner Node24.22.1分别记录。

当前无F001阻断；后续重大设计/契约问题才向用户裁决，普通缺陷自主修复并保留失败/复测证据。
