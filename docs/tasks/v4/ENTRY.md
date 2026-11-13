# TokenScope V4入口

2026-11-13用户已认可V3验收通过。V4核心仅两项：**汇报**、**模型演进**；优先验证小版本间Tokenizer/Chat Template能否复用。当前是入口、身份、任务及启动材料准备，不等于前端改版、产品编码、现场分析或打包已获实施批准。

## 按角色进入

| 角色 | 状态/身份 | 首读与启动 |
| --- | --- | --- |
| V4产品设计与汇报（拟定角色名） | 待启动；实际session ID未知，不继承V3 | [任务](SCOPE_TASKS.md) → [协作](COLLABORATION.md) → [产品启动prompt](START_PRODUCT.md) |
| V4模型演进与开发（拟定角色名） | 待启动；实际session ID未知，不继承V3 | [复用核查表](MODEL_REUSE_MATRIX.md) → [协作](COLLABORATION.md) → [开发启动prompt](START_DEVELOPMENT.md) |
| 镜像打包与审查 | 既有01a1800e-80b4-7400-a78b-a84f5b6e888d，持续版本职责 | [交付入口](../delivery/ENTRY.md) |
| 华为现场agent | 实际ID未知；只读取证prompt待用户转发 | [现场只读启动prompt](START_HUAWEI_READONLY.md)，不是V4部署指令 |

新会话由用户按需要创建并粘贴对应prompt，首次从自己的环境核实ID，未知写未知。本轮不自动创建/发送/唤醒；登记休眠不等于删除或归档应用chat。

## 继承上下文

- [V3用户验收收口](../delivery/V3_USER_ACCEPTANCE_20261113.md) · [补证核对与数字](../delivery/V3_C04_SUPPLEMENT_REVIEW_AND_CLOSE_20261113.md)。V3已通过，不再保留用户验收待定作为当前阻断；已知有限覆盖/业务风险仍如实表达。
- 发布tokenscope-v3-c04-20261112，源码57fe9f64d78f6363ee18a12ff97693e00ae1fe3d；[发布记录](../delivery/V3_C04_DELIVERY_20261112.md)。Git后续文档commit不改变该产品身份。
- 产品仍为用户监控、搜索与排行、异常分析、MA集群监控四入口，原V2布局/L4/L5及C04获批DEMO为基础；[批准DEMO](../development-v3/prototypes/repair-demo-r1/index.html)。不因“汇报优化”另造产品模块或擅改页面。
- [实际session登记](../../../memory/SESSIONS.md) · [V4产品记忆](../../../memory/tasks/product-v4.md) · [V4开发记忆](../../../memory/tasks/development-v4.md)。两个V3会话及V2/V1维持休眠。
- Token新探测器、组合方案收益、Agent/hybrid/路由/SSD等不纳入本次核心范围；保留历史研究，用户另行启动后再规划。

优先级：先把已有成果讲清楚；并行准备模型资产复用的证据，不以未知资产或现场取证阻塞汇报稿。新接口/计量身份先稳定，之后接入必要前端。

## 原V3会话提供的上下文补充

用户另行安排两条V3线整理交接，已生成[产品上下文](../product-v4/ENTRY.md)和[开发上下文](../development-v4/DEVELOPMENT_CONTEXT_20261113.md)。这些是经验/需求补充，不是另起两套当前任务；本目录SCOPE_TASKS及用户最新决定为V4范围依据，不继承旧会话ID。
