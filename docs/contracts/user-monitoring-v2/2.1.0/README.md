# 用户监控2.1.0候选契约

2026-11-03，HV2-R1-USER。状态：候选，待总设计师独立验收及冻结。旧[2.0.0](../2.0.0/README.md)不覆盖；本目录不证明前端/现场通过。

## 材料与验证
- schema.json：新DTO及其引用类型，JSON Schema 2020-12。
- runtime.openapi.json：实际用户router的14个操作及递归引用组件；不收录其他session的MA/异常接口。
- examples.json：合成sealed fixture产生的真实ASGI响应及正反例；随机ID/时间不可用于生产。5正3反。
- manifest.json：上述文件SHA。普通测试只读核验，不再生成。
- 复验：`.venv/bin/pytest -q tests/integration/monitoring/test_user_discovery_defaults.py -k candidate_contract_artifacts`。
- 仅维护时重建：同一命令前加`TOKENSCOPE_UPDATE_USER_CONTRACT=1`。OpenAPI/Schema可比较；fixture的运行UUID/时间重新生成会变化。不要运行旧生成器覆盖2.0.0。

## 新增操作（前缀/monitoring/user-v2）

| 方法/路径 | 语义 |
| --- | --- |
| GET /runs | 已发布ready/empty的appid×模型×运行目录；读现有索引，不绑定/导入/计算 |
| GET /ttft/defaults | 所有模型最新默认，或model_id+common_name成对筛选；可显式revision读历史 |
| POST /ttft/defaults | 显式CAS维护参数；expected_revision=0新建；submission_key幂等 |
| POST /ttft/evaluations | 按选定运行/appid/index_revision解析模型/P90/默认，显式W/T计算并持久快照 |
| GET /ttft/evaluations/{evaluation_id} | 读取已存自动计算快照，不重新计算 |

既有9操作URL/请求/响应结构保持；用户操作扩展x-user-contract-version=2.1.0。旧evaluation路径与新ttft/evaluations是独立命名空间，读结果必须用创建时相应路径，不能混用。全部要求X-TokenScope-Instance-Id；成功响应no-store。全局应用版本不是用户契约版本。

## 目录口径
筛选appid/common_name/model_id/user_run_id均精确匹配。默认按运行登记rowid降序，再按appid升序；同appid×model_id×common_name首项is_default=true。按登记先后，不按完成时间或mtime。未发布运行排除；空运行返回appid=null、count=0、P90=null，不替代另一个已发布运行的实际appid默认。前端不能把null当租户ID。

offset默认字符串"0"，limit默认100、范围1–1000。后页携带首响应snapshot和同一筛选，使用next_offset直到null；后页缺snapshot或匹配集合变化409 DISCOVERY_SNAPSHOT_CONFLICT，清空旧页重读。offset超末尾返回空页。快照是集合指纹，非持久MVCC；不保证被删除/损坏历史继续可读，封存或index损坏明确报错，不静默跳过。GET会校验索引、manifest及summary身份，不重新扫描原CSV/全部Token制品。当前每页扫描已发布索引元数据/分组，非原始请求回放；大规模历史目录性能尚未现场验证。

每项source含Trace的base/user run、common/model、index_revision、input/manifest/settings SHA、encoder/asset及文件观察时间。file_observed_time_range_utc是文件范围，不是appid筛选窗口。固定历史由user_run_id及index_revision定位，不能把is_default变化当历史结果改变。固定不存在run404、存在但未发布409；其他筛选无匹配正常空目录。index_revision在自动计算中必须精确匹配，错误409。

## 参数、持久性与兼容
独立user_monitoring/ttft_defaults.sqlite3 schema1，在router构造时初始化，业务GET不创建库/写数据。旧user_control及索引schema不变。初始化仅对已注册且模型匹配的三个精确别名登记revision1；存在任何版本则不覆盖（包括显式null停用）。
Qwen-V3.6-27B/Qwen3.6-27B=1s；GLM-V5.2/GLM-5.2=2.7s；DeepSeek-V4-Flash/DeepSeek-V4-Flash-0731=2.6s，均K=8192。source=user_provided、calibrated=false，源自2026-11-03用户提供，不是现场实测校准。未知别名不继承其他模型参数。缺τ或null：TTFT_DEFAULT_NOT_CONFIGURED 409，无具体比例。

DefaultUpdate需要model_id/common_name、expected_revision、submission_key、chunk_seconds（正数字符串或null）、source_description；K和tau_reference_chunk_tokens默认"8192"。这是完整版本登记，不是局部PATCH；只改K也要显式带τ。CAS过期409；同幂等键同意图返回原版本、不同意图409。显式历史revision不存在404，不自动回退最新。

自动计算必要请求：submission_key、user_run_id、appid、index_revision、target_seconds、waiting_seconds。comparator缺省le；chunk_tokens/default_revision可选。不接受调用方注入模型或O。W不默认0，显式"0"有效。缺K用模型默认，覆盖K保持τ原值，并带chunk_tokens_origin；K与τ参考K不同增加限制，不缩放τ。不传覆盖字段即恢复模型默认。当前公式/严格lt/小数等号/无P90/无预算语义复用2.0.0。

自动响应冻结request/source/defaults/evaluation和实例身份，含配置revision及reference K。同键重试返回原快照，即使默认已更新/当前索引不可用；不同意图409。改变配置后想重新计算必须用新键。更新默认与旧快照隔离。来源user_assumption，不因带用户默认就标实测；参考比例不是ΣH/ΣP阈值或生产P90保证。

备份/回退：备份整个state，保留新增默认库及旧库。旧二进制不认识新端点，不能称API可无损降级；旧2.0.0结果读取兼容已测，不将新自动结果塞回旧evaluation表。

## Trace公共层映射
SourceSelection：source_kind=user_v2、user_run_id、appid、expected_index_revision=index_revision、window=null。base_run_id只做溯源对照，不同时提交（旧公共契约互斥）。目录文件时间不能直接用作分析半开窗口；公共方继续生成自己的scope_id及request_keys_digest。用户与异常同Trace有效全集，MA独立。本线不修改公共接口。
