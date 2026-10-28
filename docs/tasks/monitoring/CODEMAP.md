# Token监控代码地图

更新2026-10-27：B001–B005原后端本机closed，dev5/schema2；B005.1仅方案，V1前后端完整服务未完成。B006准备已归档/pending。研究段落保留当时验证范围，不代表当前开发状态。

## 当前实现与本批修改点

| 已有文件/符号 | 现状及B005.1增量 | 相关测试 |
| --- | --- | --- |
| [storage.py](../../../src/tokenscope/monitoring/storage.py) ControlStore.complete/enqueue/fail | 完成/outbox同事务；拟加schema3、发布/目录/幂等 | [存储](../../../tests/unit/monitoring/test_storage.py)、拟test_publications/test_submission_idempotency |
| [pipeline.py](../../../src/tokenscope/monitoring/pipeline.py) execute/recover | 原封存/恢复；拟加视图投影、数值时间边界 | [pipeline](../../../tests/integration/monitoring/test_pipeline.py)、[健壮性](../../../tests/integration/monitoring/test_robustness.py) |
| [statistics.py](../../../src/tokenscope/monitoring/statistics.py) aggregate | 已存facts/groups/三宽度；本批不另建统计算法 | [统计规则](../../../tests/unit/monitoring/test_statistics_rules.py) |
| [service.py](../../../src/tokenscope/monitoring/service.py)、[API](../../../src/tokenscope/api/app.py) | 旧GET保持，新增展示服务/安全DTO/SSE/详情/导出 | [旧接口](../../../tests/integration/monitoring/test_interfaces.py)、拟test_view_api/test_view_export |
| [stage.py](../../../src/tokenscope/encoding/stage.py) | 已有原JSON/轻证据/事实连接，不调用GET重编码 | [stage](../../../tests/integration/encoding/test_stage.py) |
| [simulation.py](../../../src/tokenscope/monitoring/simulation.py) | 普通链式DES、增强占位，本批不改算法 | [差分](../../../tests/unit/monitoring/test_simulation.py) |
| [check_batch.py](../../../scripts/validation/check_batch.py)、[E2E](../../../scripts/validation/run_monitoring_e2e.py) | 旧145项基线；实施时增加B005.1及SSE真实进程E2E | [B005最终记录](../../../achieve/2026-10-28/docs/tasks/monitoring/batches/B005/TESTS.md) |

拟建view_models/view_projection/publications/events/views及测试详见[B005.1 PLAN](batches/B005.1/PLAN.md)，当前尚无对应代码，不能当已实现路径。验收映射见[TESTS](batches/B005.1/TESTS.md)。前端两份只读依赖及所读源码SHA见[输入清单](batches/B005.1/INPUT_MANIFEST.json)。共享接口唯一草案见[MONITORING_VIEW](../../contracts/MONITORING_VIEW_V1_DRAFT.md)。

B006历史准备：[归档](../../archive/monitoring/B006-backend-preparation-2026-10-27/README.md)；原scripts/release/env/docker/prompt不再是当前执行入口。目标机[环境核对](../../huawei/MONITORING_V100_DESIGN_REVIEW_2026-10-26.md)仍适用，兼容性/现场性能待验证。

## 历史研究阅读记录

下文“本轮”“尚未实现/下载/运行”等保留研究当时状态；实际源码与最新验证以本页顶部、batch结果及ENTRY为准。固定来源身份见[sources.lock](../../../env/sources.lock.json)，不全量重读上游。

## 本次补充的输入处理入口

Recipe 固定 revision `935817c66f5d6e64838f419692545f06787e485f`，以下四文件已补入来源锁；核对结论见 [输入与环境记录](../../research/implementations/MONITORING_V1_INPUT_ENV_REVIEW_2026-10-26.md)。

| 固定入口 | 用途与边界 |
| --- | --- |
| [README.zh.md](../../../upstream/deepseek-recipe/README.zh.md) | 官方模块/协议说明，不能用 V4.1 示例替代 Flash-0731 的 V4 选择 |
| [core/lib.rs](../../../upstream/deepseek-recipe/deepseek-recipe-core/src/lib.rs) | core 类型公开入口，不负责完整模板编码 |
| [core/conversation.rs](../../../upstream/deepseek-recipe/deepseek-recipe-core/src/conversation.rs) | 消息/工具/模式数据类型，默认值须由模型适配器明确 |
| [request/mod.rs](../../../upstream/deepseek-recipe/deepseek-recipe/src/request/mod.rs) | OpenAI 请求到 Conversation 的转换，输入路径参考 |

本次未运行 Recipe Rust 包或性能测试；下文编码入口和官方模板参考测试保留原执行边界。MemScope 仅作为只读环境参考，未继承其审批/部署规则。

## 当前直接源码入口

| 来源/身份 | 文件与符号 | 用途 |
| --- | --- | --- |
| PrefixLens 基础版 `fa3759d` | [chain_key.py](../../../upstream/prefixlens-local/lib/chain_key.py) `sha256_chain_tokens`；[hit_rate.py](../../../upstream/prefixlens-local/lib/hit_rate.py) `lcp`、`pooled_hit_rate` | 前缀身份与匹配参考；注意尾块和块加权口径差异 |
| PrefixLens 基础版 | [hf_tokenizer.py](../../../upstream/prefixlens-local/lib/hf_tokenizer.py) `apply_template`；[prompt_encoder.py](../../../upstream/prefixlens-local/lib/prompt_encoder.py) `HFTokenEncoder` | 基础编码边界；不直接接受完整 OpenAI 请求对象 |
| vLLM v0.23.0 `0fc695f` | [kv_cache_manager.py](../../../upstream/vllm-v0.23.0/vllm/v1/core/kv_cache_manager.py) `get_computed_blocks`；[single_type_kv_cache_manager.py](../../../upstream/vllm-v0.23.0/vllm/v1/core/single_type_kv_cache_manager.py) `FullAttentionManager`、`MambaManager`、`SlidingWindowManager` | 命中上限、MTP 退块、状态恢复与缓存保留 |
| vLLM v0.23.0 | [kv_cache_coordinator.py](../../../upstream/vllm-v0.23.0/vllm/v1/core/kv_cache_coordinator.py) `HybridKVCacheCoordinator`；[speculative.py](../../../upstream/vllm-v0.23.0/vllm/config/speculative.py) `use_eagle` | 混合组协调、MTP 归类 |
| Ascend v0.23.0 `5cb98ca` | [patch_mamba_config.py](../../../upstream/vllm-ascend-v0.23.0/vllm_ascend/patch/platform/patch_mamba_config.py) `verify_and_update_config` | Qwen/GDN 页大小及 1536 条件推导 |
| Ascend v0.23.0 | [patch_kv_cache_coordinator.py](../../../upstream/vllm-ascend-v0.23.0/vllm_ascend/patch/platform/patch_kv_cache_coordinator.py) `_get_effective_block_size`、`verify_and_split_kv_cache_groups` | 压缩比例与 LCM 命中边界 |
| Ascend v0.23.0 | [utils.py](../../../upstream/vllm-ascend-v0.23.0/vllm_ascend/utils.py) `refresh_block_size`；[attention/layer.py](../../../upstream/vllm-ascend-v0.23.0/vllm_ascend/models/layer/attention/layer.py) `get_dsv4_block_sizes`；[deepseek_v4.py](../../../upstream/vllm-ascend-v0.23.0/vllm_ascend/models/deepseek_v4.py) `get_kv_cache_spec` 相关实现 | 默认/有效块大小、DeepSeek 压缩组与状态 |
| vLLM v0.23.0 | [deepseek_v4.py](../../../upstream/vllm-v0.23.0/vllm/tokenizers/deepseek_v4.py) `get_deepseek_v4_tokenizer`；[deepseek_v4_encoding.py](../../../upstream/vllm-v0.23.0/vllm/tokenizers/deepseek_v4_encoding.py) | 目标版本服务编码的直接参考 |
| Recipe `935817c` | [tokenizer.rs](../../../upstream/deepseek-recipe/deepseek-recipe-encoding/src/tokenizer.rs) `PromptTokenizer::encode_ids`；[dsv4.rs](../../../upstream/deepseek-recipe/deepseek-recipe-encoding/src/v4/dsv4.rs) | Rust 模板及特殊 token 分段/批量编码候选 |

## 本轮补充的固定入口

| 来源/身份 | 文件与符号 | 用途与边界 |
| --- | --- | --- |
| Ascend v0.23.0 `5cb98ca` | [single_type_kv_cache_manager.py](../../../upstream/vllm-ascend-v0.23.0/vllm_ascend/core/single_type_kv_cache_manager.py) `CompressAttentionManager.cache_blocks/find_longest_cache_hit` | 压缩组读写统一原始 Token 粒度、链式匹配/MTP/对齐 |
| Ascend v0.23.0 | [patch_mamba_manager.py](../../../upstream/vllm-ascend-v0.23.0/vllm_ascend/patch/platform/patch_mamba_manager.py) `AscendMambaManager.find_longest_cache_hit` | 只查找已保存状态；大 page 不代表所有边界状态存在 |
| Ascend 2026-10-26 主干 `86add7a` | [patch_kv_cache_coordinator.py](../../../upstream/vllm-ascend-2026-10-26/vllm_ascend/patch/platform/patch_kv_cache_coordinator.py) `_skips_eagle_block_drop`、`_cache_hit_alignment_tokens` | 当前策略与 0.23.0 的差异，不能当作现场能力 |
| Ascend #16013 合并 `f2518f9` | [固定 diff](../../../upstream/vllm-ascend-pr16013/changes.diff)，`vllm_ascend/worker/utils.py::copy_kv_cache_blocks_inplace` | 分段 page、共享视图、COW；是后续合并版本 |
| Ascend #14468 head `22ed73a` | [固定 diff](../../../upstream/vllm-ascend-pr14468/changes.diff)，`num_uncached_common_prefix_tokens` | v0.25.1rc admission 链路补写；PR 未合并 |
| vLLM #37898 合并 `dc66e01` | [固定 diff](../../../upstream/vllm-pr37898/changes.diff)，coordinator 与 `_mamba_block_aligned_split` | 共享前缀发现→物化状态参考，不直接视为 Ascend 已实现 |
| Recipe `935817c` | [lib.rs](../../../upstream/deepseek-recipe/deepseek-recipe-encoding/src/lib.rs) `RenderedPrompt/PromptEncoding`；[Cargo.toml](../../../upstream/deepseek-recipe/Cargo.toml) | special_ranges 的能力边界，依赖声明 tokenizers 0.23.2 |
| tokenizers v0.23.2 `88a4498` | [tokenizer/mod.rs](../../../upstream/tokenizers-v0.23.2/tokenizers/src/tokenizer/mod.rs) `encode_fast/encode_batch_fast/encode_batch` | 快路径不计算 offsets；详细映射需等价路径核验 |

只因比较版本而固定的文件不自动成为运行依赖。PR 状态原始材料见 [元数据快照](../../../evidence/research/monitoring-2026-10-26/github-pr-metadata.json)。用户 txt 后续已取得，见 [布局核对](../../research/implementations/MONITORING_LAYOUT_REVIEW_2026-10-26.md)。

## 用户布局材料对应的补充入口

| 固定来源 | 文件/符号 | 用途 |
| --- | --- | --- |
| vLLM v0.23.0 `0fc695f` | [kv_cache_interface.py](../../../upstream/vllm-v0.23.0/vllm/v1/kv_cache_interface.py) `MLAAttentionSpec.storage_block_size` | 逻辑 Token 数到存储条目数的换算 |
| vLLM v0.23.0 | [kv_cache_utils.py](../../../upstream/vllm-v0.23.0/vllm/v1/core/kv_cache_utils.py) `make_block_hash_with_group_id`、`unify_kv_cache_spec_page_size`、`_approximate_gcd`、`_get_kv_cache_config_deepseek_v4`、`get_kv_cache_groups` | 组键、通用与 V4 特殊分组、page/slot 分配；按符号读取 |
| Ascend v0.23.0 `5cb98ca` | [patch_kv_cache_utils.py](../../../upstream/vllm-ascend-v0.23.0/vllm_ascend/patch/platform/patch_kv_cache_utils.py) `group_and_unify_kv_cache_specs`、`_get_kv_cache_groups_uniform_groups`、`_get_kv_cache_config_deepseek_v4` | 按 ratio 分桶、page padding、slot 共享、MTP 分配和非 packed 布局 |
| Ascend v0.23.0 | [test_prefix_cache_cp_patches.py](../../../upstream/vllm-ascend-v0.23.0/tests/ut/patch/platform/test_prefix_cache_cp_patches.py) `test_get_effective_block_size`、`test_ascend_mamba_manager_uses_logical_block_size_with_prefix_caching`、`test_swa_reachable_block_mask_sparse_with_lcm_alignment` | 只读未运行；原始 Token/CP、状态块和 SWA 保存边界的回归参考 |

本轮仅隔离执行 `_approximate_gcd` 的纯算术函数，验证材料中的输入 [30,61,31,60] 得到 31，输出见 [算术记录](../../../artifacts/research/monitoring-2026-10-26-layout/arithmetic-check.json)；没有运行完整 vLLM/Ascend 单元或集成测试。

## 布局之后的读写回放入口

新增 2026-10-26 固定来源，详见[回放推导](../../research/implementations/MONITORING_REPLAY_RULES_2026-10-26.md)：

| 固定来源 | 文件/符号 | 用途与执行边界 |
| --- | --- | --- |
| vLLM v0.23.0 `0fc695f` | [block_pool.py](../../../upstream/vllm-v0.23.0/vllm/v1/core/block_pool.py) `cache_full_blocks`、`free_blocks` | null/mask 不注册；请求 free 不等于立即删除缓存键；只读 |
| vLLM v0.23.0 | [scheduler.py](../../../upstream/vllm-v0.23.0/vllm/v1/core/sched/scheduler.py) `_mamba_block_aligned_split` | 每步预算、块对齐、MTP 下最后缓存位置；仅隔离执行该函数 |
| vLLM v0.23.0 | [envs.py](../../../upstream/vllm-v0.23.0/vllm/envs.py) `VLLM_PREFIX_CACHE_RETENTION_INTERVAL`；`SlidingWindowManager.reachable_block_mask/find_longest_cache_hit` | None/0/周期的 SWA 保存/查询差异；函数级 6 例 |
| Ascend v0.23.0 `5cb98ca` | 上述 `AscendMambaManager.find_longest_cache_hit`，配合上游 FullAttention 查询 | 人工 checkpoint 条件下 2 个调度敏感性案例；没有运行 worker |

[隔离检查脚本](../../../artifacts/research/monitoring-2026-10-26-replay/check_source_rules.py)与[8 例输出](../../../artifacts/research/monitoring-2026-10-26-replay/source-rule-check.json)是研究验证，不是 TokenScope 业务实现或完整上游测试。新增 3 个源码文件已验证 Git blob 与来源一致。后续仍需验证状态分配/复制/写入生命周期，以及组级回放与快速路径的差分等价性。

## 模型配置与模板

| 模型 | 固定版本与项目内入口 |
| --- | --- |
| Qwen3.6-27B | `6a9e13b`：[config](../../../upstream/model-reference/qwen36-27b/config.json)、[tokenizer 配置](../../../upstream/model-reference/qwen36-27b/tokenizer_config.json)、[chat template](../../../upstream/model-reference/qwen36-27b/chat_template.jinja) |
| GLM-5.2 | `cf457fa`：[config](../../../upstream/model-reference/glm52/config.json)、[tokenizer 配置](../../../upstream/model-reference/glm52/tokenizer_config.json)、[chat template](../../../upstream/model-reference/glm52/chat_template.jinja) |
| DeepSeek-V4-Flash-0731 | `7872f01`：[config](../../../upstream/model-reference/deepseek-v4-flash-0731/config.json)、[tokenizer 配置](../../../upstream/model-reference/deepseek-v4-flash-0731/tokenizer_config.json)、[encoding_dsv4.py](../../../upstream/model-reference/deepseek-v4-flash-0731/encoding/encoding_dsv4.py) |

以上是公开参考 revision，不是现场文件身份。tokenizer.json 词表本轮未下载；后续固定实际词表摘要后才进行 Token IDs 对齐。

## 相关测试与实际执行状态

- [PrefixLens test_hit_rate.py](../../../upstream/prefixlens-local/tests/unit/test_hit_rate.py)：LCP 与 pooled 计量；本轮只读、未执行。
- [vLLM test_prefix_caching.py](../../../upstream/vllm-v0.23.0/tests/v1/core/test_prefix_caching.py)：`test_eagle_enabled_removes_last_block`、`test_eagle_with_partial_blocks`、`test_prefill_hybrid_model_eagle`、`test_prefill_hybrid_model_mamba_align`；本轮只读、未执行。
- [Ascend test_compressed_prefix_cache.py](../../../upstream/vllm-ascend-v0.23.0/tests/ut/test_compressed_prefix_cache.py)：逻辑块哈希、完整逻辑块命中、拒绝部分压缩块命中；本轮只读、未执行。
- [vLLM test_deepseek_v4.py](../../../upstream/vllm-v0.23.0/tests/tokenizers_/test_deepseek_v4.py)：后续服务版本 tokenizer 对齐参考；本轮未执行。
- [官方 0731 test_encoding_dsv4.py](../../../upstream/model-reference/deepseek-v4-flash-0731/encoding/test_encoding_dsv4.py)：本轮执行 4/4 通过，固定 fixtures 同目录 tests；[输出记录](../../../artifacts/research/monitoring-2026-10-23/deepseek-v4-0731-reference-test.json)。仅模板渲染/解析验证。

本轮新增登记（均只读，未在本机执行）：

- [Ascend #16013 diff 中的测试](../../../upstream/vllm-ascend-pr16013/changes.diff)：`tests/ut/worker/test_kv_cache_block_copy.py` 的 segmented storage、shared views、None entries、complete physical pages、cyclic sources 五个用例，以及 `tests/e2e/pull_request/one_card/test_qwen3_5_0_8b.py` 的细粒度冷/热一致性改动。
- [vLLM #37898 diff 中的测试](../../../upstream/vllm-pr37898/changes.diff)：`test_hybrid_cache_mamba_align_shared_prefix_detection`，验证缺 SSM 状态时仍为 miss、公共前缀提示改变调度边界。
- Ascend 0.23.0 的 `test_compressed_prefix_cache.py` 继续作为压缩读写与跨组匹配回归入口；未因本轮读过源码就改为执行通过。

未创建业务代码或性能基线；B001–B006 已作为待审批计划写入 DESIGN，尚未执行。原始主干比较快照保留在锁文件中；需要解释版本差异时按研究链接读，不全量阅读。


## B002 落盘增量

[encoding/stage.py](../../../src/tokenscope/encoding/stage.py) 维护有界编码与最终质量；[stage测试](../../../tests/integration/encoding/test_stage.py)验证拒绝行/重复/分片和失败未封存；RawRequestStore 使用 WAL。96 项回归通过，早期研究段落的“未实现”仅为历史记录。

## B003 实现

[simulation.py](../../../src/tokenscope/monitoring/simulation.py)：CacheStrategy、FullBlock/NoCache、增强占位、磁盘账本与回放。[独立参考测试](../../../tests/unit/monitoring/test_simulation.py)和stage集成测试；117项全回归通过。

## B004 实现

[statistics.py](../../../src/tokenscope/monitoring/statistics.py)、[rules.py](../../../src/tokenscope/monitoring/rules.py)、[pipeline.py](../../../src/tokenscope/monitoring/pipeline.py)；storage/service/API/CLI已衔接。测试见 [统计规则](../../../tests/unit/monitoring/test_statistics_rules.py)、[pipeline集成](../../../tests/integration/monitoring/test_pipeline.py)。131项回归通过；schema2增量建表，实际API说明见公共契约补充。

## B005实现与B006历史准备

[resources.py](../../../src/tokenscope/resources.py)与CLI entrypoint限制独立进程CPU；[健壮性测试](../../../tests/integration/monitoring/test_robustness.py)覆盖批次一致、并发、损坏/失败和迁移；[泊松生成器](../../../scripts/validation/generate_monitoring_data.py)、[实际HTTP E2E](../../../scripts/validation/run_monitoring_e2e.py)绑定源码摘要，最终145项回归通过。

[构建门槛](../../../scripts/release/build_monitoring.py)、[门槛测试](../../../tests/unit/test_release_gate.py)、env/docker和prompts/delivery/HUAWEI_MONITORING_V1.md为B006历史准备；已归档/pending，原路径只保留追溯，不能作为首版完整服务构建入口。

## B005.1评审与S0固定契约（2026-10-27）

[S0契约入口](batches/B005.1/S0_CONTRACT.md)固定字段、成功错误样例和R1/R2边界；[Schema](../../contracts/schemas/monitoring-view-v1.schema.json)、[设计OpenAPI](../../contracts/schemas/monitoring-view-v1.design.openapi.json)、[完整样例](../../contracts/examples/monitoring-view-s0/README.md)。生成工具：[build_monitoring_view_v1.py](../../../scripts/contracts/build_monitoring_view_v1.py)；独立验证：[validate_monitoring_view_v1.py](../../../scripts/contracts/validate_monitoring_view_v1.py)，94项契约检查，非业务API/浏览器测试。

S1拟新增view_models/view_projection/publications、S2 events、S3 views；接入现有[domain.py](../../../src/tokenscope/domain.py)、[API](../../../src/tokenscope/api/app.py)、[storage](../../../src/tokenscope/monitoring/storage.py)、[pipeline](../../../src/tokenscope/monitoring/pipeline.py)；目前均未实施。S0确认来源叶字段来自[encoding/models.py](../../../src/tokenscope/encoding/models.py)，原浮点规则兼容来自[rules.py](../../../src/tokenscope/monitoring/rules.py)，不复制新的计量实现。B005.1业务测试及B006联合/交付按各自PLAN/TESTS待执行。

## B005.1 展示生产方增量（dev6/schema3/view1，后端闭环）

- `src/tokenscope/monitoring/publications.py`：完整目录/latest与同事务持久事件；`view_projection.py`：worker构建不可变sidecar和组范围；storage schema3备份/回填见pipeline。
- `events.py`：SSE游标、reset/保留/容量/慢发送；同游标空尾部短周期共享读取，持久日志仍权威。
- `view_models.py`：精确十进制序列化、严格设置/规则输入；`views.py`：只读快照/多列请求/正文/证据/信号/回执。
- `view_export.py`：NDJSON摘要、CSV转义、有界输出；`api/views.py`：展示路由和断流关闭；`api/openapi.py`、`monitoring_view_openapi.json`：固定S0响应Schema挂接实际路由。
- `tests/integration/monitoring/test_{publications,events,views,view_operations,view_recovery}.py`：目录/事务/迁移/SSE/快照/操作/回退及断流检查；旧145项继续回归。
- `scripts/validation/run_monitoring_e2e.py --batch B005.1`调用`run_monitoring_view_e2e.py`，另有`stress_monitoring_view.py`、`measure_sse_overhead.py`；`scripts/contracts/validate_monitoring_view_runtime.py`独立校验实际响应和冻结清单。

批准计量设计和S0原始文件不修改；前端代码不属于本映射的实施范围。


## 联合验证增补

api/app.py、cli.py：--viewer-root同源装配；monitoring/views.py：请求独占只读流跨线程生命周期。test_viewer_host.py回归上述两项；apps/viewer/tests/browser/joint*.spec.ts为后端主持的联合脚本；scripts/validation/joint_gzip_proxy.mjs/capture_joint.mjs为本机验收工具。前端export-controller.ts失败取消body，export.test.ts对应回归。证据见JOINT_RESULT_V1.md。
