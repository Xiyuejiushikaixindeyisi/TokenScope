# TTFT最小参考模型：前端接入交接

2026-10-31。后端增量U006–U008；本轮只交接，不修改前端、不代签前端接收或联合验收。**代码完成，性能校准待完成**。

优先读[契约2.0.0](../../../contracts/user-monitoring-v2/2.0.0/README.md)、[Schema](../../../contracts/user-monitoring-v2/2.0.0/schema.json)、[样例](../../../contracts/user-monitoring-v2/2.0.0/runtime.examples.json)、[U008验收](batches/U008/RESULT.md)。已有运行/绑定/排行流程见[主交接](FRONTEND_HANDOFF.md)。

## 新建情景示例

以下是合成算术示例，不是某模型实测配置或默认值。所有请求携带X-TokenScope-Instance-Id；路径前缀/monitoring/user-v2。

POST /scenarios：
```json
{
  "timing_model": "batch_reference_total_noncompute_v1",
  "scenario_id": "example",
  "revision": "1",
  "model_id": "Qwen3.6-27B",
  "common_name": "Qwen-V3.6-27B",
  "deployment": "用户选定的固定配置",
  "source": "user_assumption",
  "source_description": "算术示例，非实测校准",
  "chunk_tokens": "8192",
  "chunk_seconds": "1"
}
```

POST /evaluations：
```json
{
  "submission_key": "由客户端生成并在重试时保留",
  "user_run_id": "使用真实用户运行回执ID",
  "appid": "所选租户",
  "scenario_id": "example",
  "scenario_revision": "1",
  "target_seconds": "8",
  "waiting_seconds": "5",
  "comparator": "le"
}
```

L=P90由服务读取，不在请求中额外填入；若该组L=32768，则此例n=3、Cmax=24576、参考25%。严格<8s则50%。真实响应使用已有CSV的L，不能固定为示例值。

## 表单与返回值

| 项目 | 接入要求 |
| --- | --- |
| W | 标签“首Token前非计算耗时预算（含等待等）”；含初始/中间等待及其余非计算耗时，不含GF发出前GB排队 |
| O | 新模型不展示、不提交；即使0/null也422。不要填O=0来兼容旧接口 |
| K/τ | K为明确整数Token，τ为正数秒；无自动示例值；8k不混用8000/8192 |
| 缺参 | 未填/空白/null先判缺失，禁用提交；W不默认0，明确0有效 |
| 证据 | 可折叠选填；无需伪造范围、样本或摘要。缺省范围显示“适用范围未验证” |
| 来源 | 人工W+实测τ仍显示假设情景；source不自动变verified_measurement |
| 结果 | 按后端status/reason与limitations展示；比例0–1仅转百分比，不在前端重算 |
| 不可用 | no_budget/out_of_scope/unavailable分开说明，比例为—而不是0或100% |
| 100% | 必须显示完全复用可行性未证实，不承诺可达 |
| 上下文 | 展示P90、请求数及T/W/K/τ快照；不可与聚合理想命中率直接判达标 |
| 过期结果 | 输入/运行/租户/情景版本变化后清除当前有效结果；迟到响应不得覆盖新条件 |

新情景响应会补固定measurement_boundary及选填字段null。新情景必须显式tag；通过运行OpenAPI用户操作的x-user-contract-version确认接口2.0.0，不能用全局应用版本推断。

## 历史兼容

历史scenario没有timing_model且有完整旧字段时，按“历史W+O口径”展示原W/O；新字段不可回填到旧结果。新旧结果共用Evaluation主体，按scenario形状判断。旧客户端仍可按完整旧模型读写。

情景id/revision不可变，改计算口径或τ必须用新revision；总W由用户重新确认。估算重试保持submission_key与原输入；改输入使用新key。GET只读旧快照，不重新计算。

## 留给前端的验收

接入新版后验证：最小表单与可选证据、缺W/明确0、未知版本/混入O错误、0%/100%/无预算/范围外、条件变化与迟到响应、旧历史展示、模型/服务不匹配及身份409处理。本轮后端ASGI测试不替代浏览器交互验收。保持UI-02布局，正式前端实现由其负责会话按授权开展。

## 实际源码推送身份
2026-10-31推送确认：U006–U008源码提交a4053db5789fa9460b1fae4097a8835b2554357c已push origin main，git ls-remote核实远端同一SHA；本地身份u008-local-1/契约2.0.0。仅本线44文件及共享记忆本线段落入提交，其他session未完成材料保留工作区。当前前端接入支持/后端维护；代码完成，性能校准待完成。未修改前端、部署或打包。
