# F005 问题记录

状态：closed；普通问题自主修复，未改后端契约。

| ID | 复现/影响 | 根因与修复 | 证据/状态 |
| --- | --- | --- | --- |
| F005-I01 | 256MiB浏览器内存超64MiB | Playwright隐私上下文的OPFS与持久化目录不同；改持久化临时浏览器配置测真实文件。UNC配置目录出现InvalidStateError，改由Playwright管理本机临时运行配置并自动清理，结果仍存项目。保留失败证据。 | pass2–pass7；不以应用缓冲代替RSS |
| F005-I02 | 持久化测试仍有较高瞬时分配 | 复用Worker往返缓冲；支持BYOB的ReadableStream复用64KiB读取缓冲；CSV复用decoder和同scope前缀快路径，完整引号/UTF8/列数验证仍保留。CSV不加载JSON Schema验证器。 | pass8浏览器通过，增量65,810,432 bytes（约62.8MiB）；单次不是稳定性证明 |
| F005-I03 | strict TS不接受DTO作为Record | assertScope接收显式对象展开，保持五个身份键精确校验。 | final/typecheck.log通过 |
| F005-D01 | 原64MiB门槛缺目标终端依据 | 用户明确批准64MiB优化目标、256MiB验收上限，增加256MiB/1GiB各3次及增长检查；不改变正确性/后端契约。 | APPROVAL及主设计9.4；压力复测通过，见acceptance-memory.json |

文件选择器使用受控handle返回真实OPFS WritableFileStream；测试不是手工操作系统保存对话框。Windows Edge、Node身份及测量方法随报告保存。

F005-I04：并行generate重写Schema导致Vite HMR使一次浏览器用例导航中断；静止源码后同例复测通过。F005-D02：agent初拟增长<2倍不是用户批准条件，公开说明后明确检测界线为<3倍（4倍文件），保留全部实测，不宣称数学证明。
