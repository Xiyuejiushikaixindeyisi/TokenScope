# 监控输入与计量语义

历史讨论稿：当前入口为 [v0.2](MONITORING_V0_2.md)。本文件与原样例保留追溯，不代表最新决定。

版本：v0.1-discussion，2026-10-23。维护：Token 监控；消费者：前缀分析、长度分析、展示及后续 Agent。仅“已确认”部分为当前用户决定，输出字段和公式为讨论草案，尚非正式 API/Schema。

## 已确认输入

用户提供每模型一个带表头 CSV，目标为 Qwen3.6-27B、DeepSeek-V4-Flash-0731、GLM-5.2。

| 列 | 语义 |
| --- | --- |
| hash_id | 唯一请求标识 |
| appid | 租户；按 appid × 模型独立统计和缓存 |
| model_handle_start_time | 模型开始处理时间；格式及原始时区待确认 |
| completion_tokens | 输出长度；独立统计，不加入输入重算量 |
| request_input | 未套 chat template 的完整 OpenAI v1 JSON 请求体 |

已确认：原始 JSON 文本参与模板前计量，保留空白/字段顺序/标点等；CSV 容器的外层引号和转义由 CSV 解析处理。模板后从解析后的请求对象按实际模型/模式渲染。每个 CSV 空缓存开始，忽略跨 appid 命中，HBM 容量无限。

## 建议输出语义（待收敛）

| 概念名 | 语义 |
| --- | --- |
| json_tokens | 原始 request_input 字符串使用对应模型 tokenizer 的计数；不注入模板或额外 BOS/EOS |
| prompt_tokens | 模型模板/专用编码后输入 token_ids 的长度 |
| ideal_cached_input_tokens | 模型缓存规则允许复用的输入前缀 Token 数 |
| ideal_compute_input_tokens | prompt_tokens - ideal_cached_input_tokens；理想命中当作真实命中时的输入重算估计 |
| completion_tokens | 原 CSV 输出长度，来源为用户数据而非监控重编码 |
| ideal_hit_rate | sum(ideal_cached_input_tokens) / sum(prompt_tokens)，分母为 0 时不可计算 |

所有总量必须来自同一有效请求集合。请求数应同时能追溯原始行数、有效行数、拒绝/重复行，具体处理政策待确认；未知或失败不可静默填零。数值计算不把块尾 padding 当作输入 Token。

三张图分别独立按对应长度降序排序，x 为排名，y 为长度，每点关联 hash_id；均提供 P50/P80/P90 水平线。分位数定义沿通常“有 p% 样本不大于此值”的含义，不因图按降序而反转。算法尚未确认，建议线性插值并记录算法名。

结果建议关联 source_file_sha256、模型/Tokenizer/Template/模式身份、模拟规则身份、窗口、输入质量和运行状态。GDN 与压缩缓存还需要说明实际命中对齐与状态可用假设；一个裸百分比不构成完整结果。

告警信号至少需表达目标 appid/模型/窗口、触发指标及值、规则和比较方向、结果定位、路由目标。具体字段名、结构及兼容策略待设计，不用本草案提前冻结两个分析器的接口。

## 样例与兼容

[算术样例](examples/monitoring-v0.1-illustrative.json) 使用虚构长度和 full-attention B=128/MTP 规则，显式标注 illustrative；不能冒充三个目标模型任一真实结果。例中的线性分位数、阈值和事件字段仅为讨论内容。

正式契约形成前不得把本版本当作稳定输入；后续语义变更升版，并在监控 DESIGN 记录消费者影响。对应设计见 [监控 DESIGN](../tasks/monitoring/DESIGN.md)。
