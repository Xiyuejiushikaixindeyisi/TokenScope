# U005 问题记录

2026-10-30。以下软件问题均closed，修复后定点回归及静态检查通过。

| ID | 发现与处理 | 验证 |
| --- | --- | --- |
| U005-I01 | GET在用户控制库丢失时原连接分支可能创建空库；readonly始终mode=ro，返回503 | test_missing_control_get_does_not_recreate |
| I02 | 恢复基础提交时先读原CSV会阻断“基础已封存、原输入已移除”的幂等恢复；先查稳定基础键 | test_response_loss_finds_base_after_input_removed |
| I03 | 冻结文字口径要求后续页带revision、计数范围为整数；补强实现和Schema（生成器原先计数误用decimal） | 排行oracle/分页测试；HTTP校验 |
| I04 | 异常长整数/十进制可能触发Python转换限制；数值文本128字符、普通文本4096字符，明确422无回显 | test_invalid_inputs_safe_errors_and_runtime_contract |
| I05 | 显式历史绑定可能抢占尚未回写base_id的用户基础任务；检查稳定基础回执及持久意图拒绝 | 响应丢失测试追加reserved绑定竞争 |
| I06 | 短暂存储故障保留重试状态且暴露STORAGE_UNAVAILABLE；成功发布清除错误，不伪装ready | 发布/权限/磁盘故障测试 |
| I07 | 用户错误码及运行OpenAPI头信息与设计不齐；只在user-v2命名空间归一404/400/422并声明必要身份头 | 真实HTTP/OpenAPI；旧S0回归 |
| I08 | 预检查CSV字段上限与基础读取器不同；统一2^31−1，不截断长正文 | 28万字符原JSON及真实编码保真 |
| I09 | 首次工具补丁上下文与格式化后的文件不符；未部分落盘，重读后应用 | 最终静态/类型/测试通过 |

契约修订为1.0.1：错误/分页规则对齐既有说明、输入长度防护与计数正则勘误。字段集合、公式、分组、Token口径及旧S0未变。

外部pending：真实TTFT性能校准及适用性、前端联调、华为现场验证与内网开放。不是本地后端软件阻断。DeepSeek生产缺省/GF资产等价/GLM CP限制继续保留。
