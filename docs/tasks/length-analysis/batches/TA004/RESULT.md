# TA004 修改编译与真实三模型编码

2026-10-31：closed（七类handler、公共原子应用及真实编码层）。公共服务/UI能否从显式业务输入创建引用替换/普通消息删除candidate属于TA005待接入项，不用本批直接调用测试冒充完整业务路径。

## 实现

transformations.py实现description替换、字段投影、条目/行范围、内嵌arguments引用替换、明确授权普通重复消息删除、保留策略结果替换。参数严格，均需业务依据；原始JSON不可变，任何目标失败返回blocked且无operations。内嵌JSON只解析一层，同外层多个目标一次编译，数值词法保留，外层保护摘要+内部操作清单完整。公共层再验证guard/重叠冲突并校验请求协议。候选未给参数不自动裁剪。实际调用/参数与限制见[IMPLEMENTED_API](../../IMPLEMENTED_API.md)。

T1/T2返回待参数候选；T4仅已有保留策略违反时返回替换候选；无策略不判超限。T3无已确认业务协议时只给事实，不自动生成删除计划。候选、观察、单元通过公共身份引用，保留源请求与位置。

## 已验证

- 本线73项单元测试+公共21项单元回归+本线3项三模型真实集成：**97 passed，14.14s**；此前本线三模型单独3 passed，14.95s。ruff通过，mypy本线11个源码模块通过。
- 三模型：GLM-5.2、Qwen3.6-27B、DeepSeek-V4-Flash-0731，沿env/encoding-assets.lock.json固定资产，enable_thinking=false，无下载/换模型/推理生成。每模型七类handler全部实际生成副本、统一批量编码与explain详细IDs/P一致；含中文与特殊Token字面值。
- 每模型实际Token direction=token_content/direct_full回放，只含目标appid两条请求，修改一条，P下降且gate不适用；源requests.sqlite3摘要前后相同。
- 单元层覆盖M01–M08/C05–C08：Schema/name不改、字段/行序、换行、数值词法、两个内层目标一次编译、引用协议不足、真实引用值占位不得自动生成、原数组多消息删除、协议消息拒绝、原值guard复验、同目标冲突、任一目标失败整体无操作、非法/缺失参数。
- 后续补充Schema子字段不能被当工具description候选的回归，结果见最新TESTS摘要；不把这项新增数量混入上述97项历史执行。

## 边界与后续

H2外层JSON通过stdlib重新序列化，会使某些原数值词法变化。本线预检并返回PUBLIC_NUMBER_LEXEME_UNSAFE，内嵌数值仍精确保留；未修改公共代码。引用支持当前明确工具Schema中的顶层无约束string字段，复杂Schema/嵌套引用不猜测兼容性。真实引用由业务提供，本线不执行外部工具验证其存在或质量。

编译硬上限目前8MiB/64层/1000目标，不是业务异常阈值；生产运行预算资源校准属于TA006。版本与工作树摘要记录于[CODE_IDENTITY](CODE_IDENTITY.json)。回退为不注册Token插件；源无改写，无数据库迁移、打包、部署或公共API修改。下一步TA005等待H3a/H3b提供方就绪后做真实任务和HTTP联调，不要求重新审批本线编码。
