# S0完整字段字典（contract 1.0.0）

从monitoring-view-v1.schema.json生成。required列为必填；nullable显式列出。嵌套字段沿引用继续；对象默认拒绝额外字段。
Legacy类型原样复制现有运行OpenAPI；其中snapshot/result为刻意不透明JSON，前端仅消费run_id/status，不将其当新展示数据。

## DataRange

| 字段 | 必填 | 类型/约束 |
| --- | --- | --- |
| start | 是 | string / ^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}\.[0-9]{9}Z$ format=date-time OR null  |
| end | 是 | string / ^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}\.[0-9]{9}Z$ format=date-time OR null  |

## Quantiles

| 字段 | 必填 | 类型/约束 |
| --- | --- | --- |
| p50 | 是 | string / ^(0&#124;[1-9][0-9]*)$(?![\s\S])  OR null  |
| p80 | 是 | string / ^(0&#124;[1-9][0-9]*)$(?![\s\S])  OR null  |
| p90 | 是 | string / ^(0&#124;[1-9][0-9]*)$(?![\s\S])  OR null  |

## Capability

| 字段 | 必填 | 类型/约束 |
| --- | --- | --- |
| executable | 是 | boolean  |
| status | 是 | enum available/disabled/not_supported |
| strategy | 是 | enum full-block-mtp-v1/no-cache-v1/reserved_hybrid |
| simulation_semantics | 是 | enum full_block_rule/chained_approximation |

## Settings

| 字段 | 必填 | 类型/约束 |
| --- | --- | --- |
| model_id | 是 | enum GLM-5.2/Qwen3.6-27B/DeepSeek-V4-Flash-0731 |
| revision | 是 | string / ^[1-9][0-9]*$(?![\s\S])  |
| block_size | 是 | string / ^[1-9][0-9]*$(?![\s\S])  |
| block_size_unit | 是 | enum simulation_input_tokens |
| cp_world_size | 是 | string / ^[1-9][0-9]*$(?![\s\S])  |
| mtp | 是 | boolean  |
| prefix_cache_enabled | 是 | boolean  |
| hybrid_enabled | 是 | boolean  |
| cache_mode | 是 | enum full_block/full_block_approximation/qwen_hybrid/deepseek_hybrid |
| model_aliases | 是 | array<string minLength=1> |
| encoding_profile | 是 | enum default/thinking_enabled/thinking_disabled |

## SettingsChanges

| 字段 | 必填 | 类型/约束 |
| --- | --- | --- |
| block_size | 否 | string / ^[1-9][0-9]*$(?![\s\S])  |
| cp_world_size | 否 | string / ^[1-9][0-9]*$(?![\s\S])  |
| mtp | 否 | boolean  |
| prefix_cache_enabled | 否 | boolean  |
| hybrid_enabled | 否 | boolean  |
| cache_mode | 否 | enum full_block/full_block_approximation/qwen_hybrid/deepseek_hybrid |
| model_aliases | 否 | array<string minLength=1> |
| encoding_profile | 否 | enum default/thinking_enabled/thinking_disabled |

## SettingsUpdate

| 字段 | 必填 | 类型/约束 |
| --- | --- | --- |
| expected_revision | 是 | string / ^[1-9][0-9]*$(?![\s\S])  |
| changes | 是 | SettingsChanges |

## ModelSettingsResponse

| 字段 | 必填 | 类型/约束 |
| --- | --- | --- |
| service_instance_id | 是 | string format=uuid |
| view_schema_version | 是 | enum 1 |
| settings | 是 | Settings |
| capability | 是 | Capability |

## Rule

| 字段 | 必填 | 类型/约束 |
| --- | --- | --- |
| appid | 是 | string minLength=1 |
| model_id | 是 | enum GLM-5.2/Qwen3.6-27B/DeepSeek-V4-Flash-0731 |
| rule_id | 是 | string minLength=1 |
| revision | 是 | string / ^[1-9][0-9]*$(?![\s\S])  |
| metric | 是 | enum request_count/ideal_hit_rate/totals.json_tokens/totals.prompt_tokens/totals.ideal_cached_input_tokens/totals.ideal_compute_input_tokens/totals.completion_tokens/quantiles.json_tokens.p50/quantiles.json_tokens.p80/quantiles.json_tokens.p90/quantiles.prompt_tokens.p50/quantiles.prompt_tokens.p80/quantiles.prompt_tokens.p90/quantiles.ideal_compute_input_tokens.p50/quantiles.ideal_compute_input_tokens.p80/quantiles.ideal_compute_input_tokens.p90 |
| comparator | 是 | enum lt/le/gt/ge |
| threshold | 是 | oneOf(string / ^(0&#124;-?[1-9][0-9]*)$(?![\s\S]) , number ) |
| value_kind | 是 | enum integer/ratio/number |
| enabled | 是 | boolean  |
| route | 是 | enum prefix_analysis/length_analysis/signal_only OR null  |
| measurement_signature | 是 | string / ^[0-9a-f]{64}$  |

## RuleUpdate

| 字段 | 必填 | 类型/约束 |
| --- | --- | --- |
| appid | 是 | string minLength=1 |
| model_id | 是 | enum GLM-5.2/Qwen3.6-27B/DeepSeek-V4-Flash-0731 |
| rule_id | 是 | string minLength=1 |
| metric | 是 | enum request_count/ideal_hit_rate/totals.json_tokens/totals.prompt_tokens/totals.ideal_cached_input_tokens/totals.ideal_compute_input_tokens/totals.completion_tokens/quantiles.json_tokens.p50/quantiles.json_tokens.p80/quantiles.json_tokens.p90/quantiles.prompt_tokens.p50/quantiles.prompt_tokens.p80/quantiles.prompt_tokens.p90/quantiles.ideal_compute_input_tokens.p50/quantiles.ideal_compute_input_tokens.p80/quantiles.ideal_compute_input_tokens.p90 |
| comparator | 是 | enum lt/le/gt/ge |
| threshold | 是 | oneOf(string / ^(0&#124;-?[1-9][0-9]*)$(?![\s\S]) , number ) |
| value_kind | 是 | enum integer/ratio/number |
| enabled | 是 | boolean  |
| route | 是 | enum prefix_analysis/length_analysis/signal_only OR null  |
| measurement_signature | 是 | string / ^[0-9a-f]{64}$  |
| expected_revision | 是 | string / ^(0&#124;[1-9][0-9]*)$(?![\s\S])  |

## RuleResponse

| 字段 | 必填 | 类型/约束 |
| --- | --- | --- |
| service_instance_id | 是 | string format=uuid |
| view_schema_version | 是 | enum 1 |
| rule | 是 | Rule |
| rules_revision | 是 | string / ^(0&#124;[1-9][0-9]*)$(?![\s\S])  |

## RulesPage

| 字段 | 必填 | 类型/约束 |
| --- | --- | --- |
| service_instance_id | 是 | string format=uuid |
| view_schema_version | 是 | enum 1 |
| offset | 是 | string / ^(0&#124;[1-9][0-9]*)$(?![\s\S])  |
| limit | 是 | integer minimum=1 maximum=1000 |
| total | 是 | string / ^(0&#124;[1-9][0-9]*)$(?![\s\S])  |
| next_offset | 是 | string / ^(0&#124;[1-9][0-9]*)$(?![\s\S])  OR null  |
| rules_revision | 是 | string / ^(0&#124;[1-9][0-9]*)$(?![\s\S])  |
| items | 是 | array<Rule> |

## ThresholdState

分支 1

| 字段 | 必填 | 类型/约束 |
| --- | --- | --- |
| status | 是 | enum unconfigured |

分支 2

| 字段 | 必填 | 类型/约束 |
| --- | --- | --- |
| rule_id | 是 | string minLength=1 |
| revision | 是 | string / ^[1-9][0-9]*$(?![\s\S])  |
| status | 是 | enum clear/needs_review/metric_unavailable/triggered |

## ThresholdComparison

| 字段 | 必填 | 类型/约束 |
| --- | --- | --- |
| rule | 是 | Rule |
| observed_value | 是 | oneOf(string / ^(0&#124;-?[1-9][0-9]*)$(?![\s\S]) , number ) OR null  |
| state | 是 | enum disabled/clear/needs_review/metric_unavailable/triggered |

## Totals

| 字段 | 必填 | 类型/约束 |
| --- | --- | --- |
| json_tokens | 是 | string / ^(0&#124;[1-9][0-9]*)$(?![\s\S])  |
| prompt_tokens | 是 | string / ^(0&#124;[1-9][0-9]*)$(?![\s\S])  |
| ideal_cached_input_tokens | 是 | string / ^(0&#124;[1-9][0-9]*)$(?![\s\S])  |
| ideal_compute_input_tokens | 是 | string / ^(0&#124;[1-9][0-9]*)$(?![\s\S])  |
| completion_tokens | 是 | string / ^(0&#124;[1-9][0-9]*)$(?![\s\S])  |

## MeasurementSignatures

| 字段 | 必填 | 类型/约束 |
| --- | --- | --- |
| request_count | 是 | string / ^[0-9a-f]{64}$  |
| ideal_hit_rate | 是 | string / ^[0-9a-f]{64}$  |
| totals.json_tokens | 是 | string / ^[0-9a-f]{64}$  |
| totals.prompt_tokens | 是 | string / ^[0-9a-f]{64}$  |
| totals.ideal_cached_input_tokens | 是 | string / ^[0-9a-f]{64}$  |
| totals.ideal_compute_input_tokens | 是 | string / ^[0-9a-f]{64}$  |
| totals.completion_tokens | 是 | string / ^[0-9a-f]{64}$  |
| quantiles.json_tokens.p50 | 是 | string / ^[0-9a-f]{64}$  |
| quantiles.json_tokens.p80 | 是 | string / ^[0-9a-f]{64}$  |
| quantiles.json_tokens.p90 | 是 | string / ^[0-9a-f]{64}$  |
| quantiles.prompt_tokens.p50 | 是 | string / ^[0-9a-f]{64}$  |
| quantiles.prompt_tokens.p80 | 是 | string / ^[0-9a-f]{64}$  |
| quantiles.prompt_tokens.p90 | 是 | string / ^[0-9a-f]{64}$  |
| quantiles.ideal_compute_input_tokens.p50 | 是 | string / ^[0-9a-f]{64}$  |
| quantiles.ideal_compute_input_tokens.p80 | 是 | string / ^[0-9a-f]{64}$  |
| quantiles.ideal_compute_input_tokens.p90 | 是 | string / ^[0-9a-f]{64}$  |

## GroupMetrics

| 字段 | 必填 | 类型/约束 |
| --- | --- | --- |
| appid | 是 | string minLength=1 |
| model_id | 是 | enum GLM-5.2/Qwen3.6-27B/DeepSeek-V4-Flash-0731 |
| request_count | 是 | string / ^[1-9][0-9]*$(?![\s\S])  |
| totals | 是 | Totals |
| quantiles | 是 | object {json_tokens: Quantiles; prompt_tokens: Quantiles; ideal_compute_input_tokens: Quantiles}; required=json_tokens,prompt_tokens,ideal_compute_input_tokens |
| ideal_hit_rate | 是 | number minimum=0 maximum=1 OR null  |
| json_to_prompt_delta | 是 | string / ^(0&#124;-?[1-9][0-9]*)$(?![\s\S])  |
| threshold_states | 是 | array<ThresholdState> |
| measurement_signatures | 是 | MeasurementSignatures |
| capability | 是 | Capability |

## HistogramBin

| 字段 | 必填 | 类型/约束 |
| --- | --- | --- |
| lower | 是 | string / ^(0&#124;[1-9][0-9]*)$(?![\s\S])  |
| upper | 是 | string / ^(0&#124;[1-9][0-9]*)$(?![\s\S])  OR null  |
| count | 是 | string / ^(0&#124;[1-9][0-9]*)$(?![\s\S])  |
| share | 是 | number minimum=0 maximum=1 OR null  |
| overflow | 是 | boolean  |

## HistogramSummary

| 字段 | 必填 | 类型/约束 |
| --- | --- | --- |
| mode_bin_indices | 是 | array<string / ^(0&#124;[1-9][0-9]*)$(?![\s\S]) > |
| mode_count | 是 | string / ^(0&#124;[1-9][0-9]*)$(?![\s\S])  |
| mode_share | 是 | number minimum=0 maximum=1 OR null  |
| under_8k_count | 是 | string / ^(0&#124;[1-9][0-9]*)$(?![\s\S])  |
| overflow_count | 是 | string / ^(0&#124;[1-9][0-9]*)$(?![\s\S])  |
| max_length | 是 | string / ^(0&#124;[1-9][0-9]*)$(?![\s\S])  OR null  |

## Histogram

| 字段 | 必填 | 类型/约束 |
| --- | --- | --- |
| bin_width | 是 | enum 1000/2000/5000 |
| regular_domain | 是 | const ["0", "200000"] |
| overflow_start | 是 | enum 200000 |
| boundary | 是 | enum left_closed_right_open |
| sample_count | 是 | string / ^(0&#124;[1-9][0-9]*)$(?![\s\S])  |
| quantile_algorithm | 是 | enum nearest_rank |
| quantiles | 是 | Quantiles |
| bins | 是 | array<HistogramBin> |
| summary | 是 | HistogramSummary |

## Distributions

| 字段 | 必填 | 类型/约束 |
| --- | --- | --- |
| json_tokens | 是 | object {1000: Histogram; 2000: Histogram; 5000: Histogram}; required=1000,2000,5000 |
| prompt_tokens | 是 | object {1000: Histogram; 2000: Histogram; 5000: Histogram}; required=1000,2000,5000 |
| ideal_compute_input_tokens | 是 | object {1000: Histogram; 2000: Histogram; 5000: Histogram}; required=1000,2000,5000 |

## FileQuality

| 字段 | 必填 | 类型/约束 |
| --- | --- | --- |
| scope | 是 | enum file |
| records_read | 是 | string / ^(0&#124;[1-9][0-9]*)$(?![\s\S])  |
| valid_requests | 是 | string / ^(0&#124;[1-9][0-9]*)$(?![\s\S])  |
| skipped_rows | 是 | string / ^(0&#124;[1-9][0-9]*)$(?![\s\S])  |
| duplicate_hash_id_rows | 是 | string / ^(0&#124;[1-9][0-9]*)$(?![\s\S])  |

## GroupQuality

| 字段 | 必填 | 类型/约束 |
| --- | --- | --- |
| scope | 是 | enum appid |
| coverage | 是 | enum known_appid_rows_only |
| valid_requests | 是 | string / ^[1-9][0-9]*$(?![\s\S])  |
| encoding_rejected_rows | 是 | string / ^(0&#124;[1-9][0-9]*)$(?![\s\S])  |
| skipped_rows | 是 | null  |
| duplicate_scope | 是 | enum appid |
| duplicate_hash_id_rows_within_group | 是 | string / ^(0&#124;[1-9][0-9]*)$(?![\s\S])  |
| unattributed_skips_available_in | 是 | enum file_quality |

## RuntimeIdentity

| 字段 | 必填 | 类型/约束 |
| --- | --- | --- |
| code_version | 是 | string minLength=1 |
| algorithm_version | 是 | string minLength=1 |
| asset_identity | 是 | string / ^[0-9a-f]{64}$  |
| encoder_identity | 是 | string / ^[0-9a-f]{64}$  |
| asset_revision | 是 | string minLength=1 |
| encoding_profile | 是 | string minLength=1 |
| profile_json | 是 | string  |

## SnapshotIdentity

| 字段 | 必填 | 类型/约束 |
| --- | --- | --- |
| service_instance_id | 是 | string format=uuid |
| view_schema_version | 是 | enum 1 |
| run_id | 是 | string format=uuid |
| appid | 是 | string minLength=1 |
| model_id | 是 | enum GLM-5.2/Qwen3.6-27B/DeepSeek-V4-Flash-0731 |
| publish_seq | 是 | string / ^[1-9][0-9]*$(?![\s\S])  |

## Provenance

| 字段 | 必填 | 类型/约束 |
| --- | --- | --- |
| data_range_utc | 是 | DataRange |
| file_data_range_utc | 是 | DataRange |
| published_at | 是 | string / ^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}\.[0-9]{9}Z$ format=date-time |
| source_label | 是 | string minLength=1 |
| input_sha256 | 是 | string / ^[0-9a-f]{64}$  |
| settings | 是 | Settings |
| rules | 是 | array<Rule> |
| runtime | 是 | RuntimeIdentity |
| simulation_semantics | 是 | enum full_block_rule/chained_approximation |
| metadata_origin | 是 | enum stored_facts_projection |

## SignalSummary

| 字段 | 必填 | 类型/约束 |
| --- | --- | --- |
| count | 是 | string / ^(0&#124;[1-9][0-9]*)$(?![\s\S])  |
| event_ids_digest | 是 | string / ^[0-9a-f]{64}$  |
| view_signals_url | 是 | string / ^/  |

## ViewCapabilities

| 字段 | 必填 | 类型/约束 |
| --- | --- | --- |
| original_json | 是 | boolean  |
| light_evidence | 是 | boolean  |
| requests | 是 | boolean  |
| export | 是 | boolean  |
| templated_text | 是 | enum False |

## ViewLinks

| 字段 | 必填 | 类型/约束 |
| --- | --- | --- |
| requests | 是 | string / ^/  |
| view_signals | 是 | string / ^/  |
| export_ndjson | 是 | string / ^/  |
| export_csv | 是 | string / ^/  |

## ViewSnapshot

| 字段 | 必填 | 类型/约束 |
| --- | --- | --- |
| identity | 是 | SnapshotIdentity |
| provenance | 是 | Provenance |
| metrics | 是 | GroupMetrics |
| distributions | 是 | Distributions |
| quality | 是 | object {file_quality: FileQuality; group_quality: GroupQuality}; required=file_quality,group_quality |
| thresholds | 是 | array<ThresholdComparison> |
| signal_summary | 是 | SignalSummary |
| capabilities | 是 | ViewCapabilities |
| links | 是 | ViewLinks |

## CatalogItem

| 字段 | 必填 | 类型/约束 |
| --- | --- | --- |
| appid | 是 | string minLength=1 |
| model_id | 是 | enum GLM-5.2/Qwen3.6-27B/DeepSeek-V4-Flash-0731 |
| active_run_id | 是 | string format=uuid |
| publish_seq | 是 | string / ^[1-9][0-9]*$(?![\s\S])  |
| published_at | 是 | string / ^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}\.[0-9]{9}Z$ format=date-time |
| data_range_utc | 是 | DataRange |
| snapshot_url | 是 | string / ^/  |

## CatalogResponse

| 字段 | 必填 | 类型/约束 |
| --- | --- | --- |
| service_instance_id | 是 | string format=uuid |
| view_schema_version | 是 | enum 1 |
| offset | 是 | string / ^(0&#124;[1-9][0-9]*)$(?![\s\S])  |
| limit | 是 | integer minimum=1 maximum=1000 |
| total | 是 | string / ^(0&#124;[1-9][0-9]*)$(?![\s\S])  |
| next_offset | 是 | string / ^(0&#124;[1-9][0-9]*)$(?![\s\S])  OR null  |
| cursor | 是 | string minLength=1 |
| catalog_revision | 是 | string / ^(0&#124;[1-9][0-9]*)$(?![\s\S])  |
| items | 是 | array<CatalogItem> |

## PublishedRun

| 字段 | 必填 | 类型/约束 |
| --- | --- | --- |
| run_id | 是 | string format=uuid |
| model_id | 是 | enum GLM-5.2/Qwen3.6-27B/DeepSeek-V4-Flash-0731 |
| publish_seq | 是 | string / ^[1-9][0-9]*$(?![\s\S])  |
| published_at | 是 | string / ^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}\.[0-9]{9}Z$ format=date-time |
| status | 是 | enum completed/no_valid_rows |
| file_data_range_utc | 是 | DataRange |
| group_count | 是 | string / ^(0&#124;[1-9][0-9]*)$(?![\s\S])  |
| input_sha256 | 是 | string / ^[0-9a-f]{64}$  |
| source_label | 是 | string minLength=1 |

## PublishedRunsResponse

| 字段 | 必填 | 类型/约束 |
| --- | --- | --- |
| service_instance_id | 是 | string format=uuid |
| view_schema_version | 是 | enum 1 |
| offset | 是 | string / ^(0&#124;[1-9][0-9]*)$(?![\s\S])  |
| limit | 是 | integer minimum=1 maximum=1000 |
| total | 是 | string / ^(0&#124;[1-9][0-9]*)$(?![\s\S])  |
| next_offset | 是 | string / ^(0&#124;[1-9][0-9]*)$(?![\s\S])  OR null  |
| catalog_revision | 是 | string / ^(0&#124;[1-9][0-9]*)$(?![\s\S])  |
| items | 是 | array<PublishedRun> |

## ResultPublishedEvent

| 字段 | 必填 | 类型/约束 |
| --- | --- | --- |
| service_instance_id | 是 | string format=uuid |
| view_schema_version | 是 | enum 1 |
| run_id | 是 | string format=uuid |
| model_id | 是 | enum GLM-5.2/Qwen3.6-27B/DeepSeek-V4-Flash-0731 |
| publish_seq | 是 | string / ^[1-9][0-9]*$(?![\s\S])  |
| published_at | 是 | string / ^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}\.[0-9]{9}Z$ format=date-time |
| status | 是 | enum completed/no_valid_rows |

## RunTerminalEvent

| 字段 | 必填 | 类型/约束 |
| --- | --- | --- |
| service_instance_id | 是 | string format=uuid |
| view_schema_version | 是 | enum 1 |
| run_id | 是 | string format=uuid |
| model_id | 是 | enum GLM-5.2/Qwen3.6-27B/DeepSeek-V4-Flash-0731 |
| event_seq | 是 | string / ^[1-9][0-9]*$(?![\s\S])  |
| status | 是 | enum failed/interrupted |
| error_code | 是 | string minLength=1 |
| finished_at | 是 | string / ^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}\.[0-9]{9}Z$ format=date-time |

## ResetEvent

| 字段 | 必填 | 类型/约束 |
| --- | --- | --- |
| service_instance_id | 是 | string format=uuid |
| view_schema_version | 是 | enum 1 |
| reason | 是 | enum expired/future_cursor/instance_changed/invalid_cursor |
| catalog_url | 是 | string / ^/  |

## RequestRef

| 字段 | 必填 | 类型/约束 |
| --- | --- | --- |
| run_id | 是 | string format=uuid |
| source_record_index | 是 | string / ^[1-9][0-9]*$(?![\s\S])  |

## RequestFact

| 字段 | 必填 | 类型/约束 |
| --- | --- | --- |
| request_ref | 是 | RequestRef |
| hash_id | 是 | string minLength=1 |
| time_utc | 是 | string / ^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}\.[0-9]{9}Z$ format=date-time |
| json_tokens | 是 | string / ^(0&#124;[1-9][0-9]*)$(?![\s\S])  |
| prompt_tokens | 是 | string / ^(0&#124;[1-9][0-9]*)$(?![\s\S])  |
| ideal_cached_input_tokens | 是 | string / ^(0&#124;[1-9][0-9]*)$(?![\s\S])  |
| ideal_compute_input_tokens | 是 | string / ^(0&#124;[1-9][0-9]*)$(?![\s\S])  |
| completion_tokens | 是 | string / ^(0&#124;[1-9][0-9]*)$(?![\s\S])  |

## RequestRow

| 字段 | 必填 | 类型/约束 |
| --- | --- | --- |
| request_ref | 是 | RequestRef |
| hash_id | 是 | string minLength=1 |
| time_utc | 是 | string / ^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}\.[0-9]{9}Z$ format=date-time |
| json_tokens | 是 | string / ^(0&#124;[1-9][0-9]*)$(?![\s\S])  |
| prompt_tokens | 是 | string / ^(0&#124;[1-9][0-9]*)$(?![\s\S])  |
| ideal_cached_input_tokens | 是 | string / ^(0&#124;[1-9][0-9]*)$(?![\s\S])  |
| ideal_compute_input_tokens | 是 | string / ^(0&#124;[1-9][0-9]*)$(?![\s\S])  |
| completion_tokens | 是 | string / ^(0&#124;[1-9][0-9]*)$(?![\s\S])  |
| position | 是 | string / ^[1-9][0-9]*$(?![\s\S])  |

## LengthFilter

| 字段 | 必填 | 类型/约束 |
| --- | --- | --- |
| metric | 是 | enum json_tokens/prompt_tokens/ideal_compute_input_tokens |
| lower | 是 | string / ^(0&#124;[1-9][0-9]*)$(?![\s\S])  |
| upper | 是 | string / ^(0&#124;[1-9][0-9]*)$(?![\s\S])  OR null  |
| hash_id | 是 | string minLength=1 OR null  |
| hash_match | 是 | enum exact/prefix |

## RequestSort

| 字段 | 必填 | 类型/约束 |
| --- | --- | --- |
| by | 是 | enum time_ns/source_record_index/json_tokens/prompt_tokens/ideal_cached_input_tokens/ideal_compute_input_tokens/completion_tokens |
| order | 是 | enum asc/desc |
| tie_breaker | 是 | enum source_record_index_asc |

## RequestsPage

| 字段 | 必填 | 类型/约束 |
| --- | --- | --- |
| service_instance_id | 是 | string format=uuid |
| view_schema_version | 是 | enum 1 |
| offset | 是 | string / ^(0&#124;[1-9][0-9]*)$(?![\s\S])  |
| limit | 是 | integer minimum=1 maximum=1000 |
| total | 是 | string / ^(0&#124;[1-9][0-9]*)$(?![\s\S])  |
| next_offset | 是 | string / ^(0&#124;[1-9][0-9]*)$(?![\s\S])  OR null  |
| run_id | 是 | string format=uuid |
| appid | 是 | string minLength=1 |
| model_id | 是 | enum GLM-5.2/Qwen3.6-27B/DeepSeek-V4-Flash-0731 |
| filter | 是 | LengthFilter |
| sort | 是 | RequestSort |
| items | 是 | array<RequestRow> |

## EvidenceSummary

| 字段 | 必填 | 类型/约束 |
| --- | --- | --- |
| raw_json_sha256 | 是 | string / ^[0-9a-f]{64}$  |
| rendered_sha256 | 是 | string / ^[0-9a-f]{64}$  |
| rendered_characters | 是 | string / ^(0&#124;[1-9][0-9]*)$(?![\s\S])  |
| rendered_utf8_bytes | 是 | string / ^(0&#124;[1-9][0-9]*)$(?![\s\S])  |
| special_ranges_count | 是 | string / ^(0&#124;[1-9][0-9]*)$(?![\s\S])  |
| source_fields_count | 是 | string / ^(0&#124;[1-9][0-9]*)$(?![\s\S])  |
| special_ranges_unit | 是 | enum utf8_bytes_half_open |
| special_ranges_semantics | 是 | string minLength=1 |
| effective_options_json | 是 | string  |
| source_attribution | 是 | enum references_only_not_additive_token_contributions |
| source_attribution_status | 是 | enum partial/unknown |

## BodyPreview

| 字段 | 必填 | 类型/约束 |
| --- | --- | --- |
| text | 是 | string  |
| total_utf8_bytes | 是 | string / ^(0&#124;[1-9][0-9]*)$(?![\s\S])  |
| preview_utf8_bytes | 是 | string / ^(0&#124;[1-9][0-9]*)$(?![\s\S])  |
| truncated | 是 | boolean  |

## RequestDetail

| 字段 | 必填 | 类型/约束 |
| --- | --- | --- |
| service_instance_id | 是 | string format=uuid |
| view_schema_version | 是 | enum 1 |
| run_id | 是 | string format=uuid |
| appid | 是 | string minLength=1 |
| model_id | 是 | enum GLM-5.2/Qwen3.6-27B/DeepSeek-V4-Flash-0731 |
| request | 是 | RequestFact |
| body_preview | 是 | BodyPreview |
| evidence_summary | 是 | EvidenceSummary |
| capabilities | 是 | object {original_json: boolean ; light_evidence: boolean ; templated_text: enum False}; required=original_json,light_evidence,templated_text |
| links | 是 | object {body: string / ^/ ; evidence: string / ^/ }; required=body,evidence |

## SpecialRange

| 字段 | 必填 | 类型/约束 |
| --- | --- | --- |
| start | 是 | string / ^(0&#124;[1-9][0-9]*)$(?![\s\S])  |
| end | 是 | string / ^(0&#124;[1-9][0-9]*)$(?![\s\S])  |

## SourceField

| 字段 | 必填 | 类型/约束 |
| --- | --- | --- |
| json_pointer | 是 | string  |
| characters | 是 | string / ^(0&#124;[1-9][0-9]*)$(?![\s\S])  |
| utf8_bytes | 是 | string / ^(0&#124;[1-9][0-9]*)$(?![\s\S])  |
| sha256 | 是 | string / ^[0-9a-f]{64}$  |

## EvidencePage

分支 1

| 字段 | 必填 | 类型/约束 |
| --- | --- | --- |
| service_instance_id | 是 | string format=uuid |
| view_schema_version | 是 | enum 1 |
| offset | 是 | string / ^(0&#124;[1-9][0-9]*)$(?![\s\S])  |
| limit | 是 | integer minimum=1 maximum=1000 |
| total | 是 | string / ^(0&#124;[1-9][0-9]*)$(?![\s\S])  |
| next_offset | 是 | string / ^(0&#124;[1-9][0-9]*)$(?![\s\S])  OR null  |
| run_id | 是 | string format=uuid |
| appid | 是 | string minLength=1 |
| model_id | 是 | enum GLM-5.2/Qwen3.6-27B/DeepSeek-V4-Flash-0731 |
| request_ref | 是 | RequestRef |
| summary | 是 | EvidenceSummary |
| section | 是 | enum special_ranges |
| items | 是 | array<SpecialRange> |

分支 2

| 字段 | 必填 | 类型/约束 |
| --- | --- | --- |
| service_instance_id | 是 | string format=uuid |
| view_schema_version | 是 | enum 1 |
| offset | 是 | string / ^(0&#124;[1-9][0-9]*)$(?![\s\S])  |
| limit | 是 | integer minimum=1 maximum=1000 |
| total | 是 | string / ^(0&#124;[1-9][0-9]*)$(?![\s\S])  |
| next_offset | 是 | string / ^(0&#124;[1-9][0-9]*)$(?![\s\S])  OR null  |
| run_id | 是 | string format=uuid |
| appid | 是 | string minLength=1 |
| model_id | 是 | enum GLM-5.2/Qwen3.6-27B/DeepSeek-V4-Flash-0731 |
| request_ref | 是 | RequestRef |
| summary | 是 | EvidenceSummary |
| section | 是 | enum source_fields |
| items | 是 | array<SourceField> |

## Signal

| 字段 | 必填 | 类型/约束 |
| --- | --- | --- |
| run_id | 是 | string format=uuid |
| appid | 是 | string minLength=1 |
| model_id | 是 | enum GLM-5.2/Qwen3.6-27B/DeepSeek-V4-Flash-0731 |
| event_id | 是 | string / ^[0-9a-f]{64}$  |
| metric | 是 | enum request_count/ideal_hit_rate/totals.json_tokens/totals.prompt_tokens/totals.ideal_cached_input_tokens/totals.ideal_compute_input_tokens/totals.completion_tokens/quantiles.json_tokens.p50/quantiles.json_tokens.p80/quantiles.json_tokens.p90/quantiles.prompt_tokens.p50/quantiles.prompt_tokens.p80/quantiles.prompt_tokens.p90/quantiles.ideal_compute_input_tokens.p50/quantiles.ideal_compute_input_tokens.p80/quantiles.ideal_compute_input_tokens.p90 |
| comparator | 是 | enum lt/le/gt/ge |
| value_kind | 是 | enum integer/ratio/number |
| observed_value | 是 | oneOf(string / ^(0&#124;-?[1-9][0-9]*)$(?![\s\S]) , number ) OR null  |
| threshold | 是 | oneOf(string / ^(0&#124;-?[1-9][0-9]*)$(?![\s\S]) , number ) |
| rule_id | 是 | string minLength=1 |
| revision | 是 | string / ^[1-9][0-9]*$(?![\s\S])  |
| route | 是 | enum prefix_analysis/length_analysis/signal_only |
| status | 是 | enum pending_consumer |
| published_at | 是 | string / ^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}\.[0-9]{9}Z$ format=date-time |

## SignalsPage

| 字段 | 必填 | 类型/约束 |
| --- | --- | --- |
| service_instance_id | 是 | string format=uuid |
| view_schema_version | 是 | enum 1 |
| offset | 是 | string / ^(0&#124;[1-9][0-9]*)$(?![\s\S])  |
| limit | 是 | integer minimum=1 maximum=1000 |
| total | 是 | string / ^(0&#124;[1-9][0-9]*)$(?![\s\S])  |
| next_offset | 是 | string / ^(0&#124;[1-9][0-9]*)$(?![\s\S])  OR null  |
| run_id | 是 | string format=uuid |
| appid | 是 | string minLength=1 |
| model_id | 是 | enum GLM-5.2/Qwen3.6-27B/DeepSeek-V4-Flash-0731 |
| items | 是 | array<Signal> |

## Submission

| 字段 | 必填 | 类型/约束 |
| --- | --- | --- |
| file_ref | 是 | string minLength=1 |
| model_id | 是 | enum GLM-5.2/Qwen3.6-27B/DeepSeek-V4-Flash-0731 |
| submission_key | 否 | string / ^[A-Za-z0-9._-]{1,128}$  |

## Receipt

| 字段 | 必填 | 类型/约束 |
| --- | --- | --- |
| service_instance_id | 是 | string format=uuid |
| view_schema_version | 是 | enum 1 |
| submission_key | 是 | string minLength=1 |
| run_id | 是 | string format=uuid |
| model_id | 是 | enum GLM-5.2/Qwen3.6-27B/DeepSeek-V4-Flash-0731 |
| status | 是 | enum queued/running/completed/no_valid_rows/failed/interrupted |
| created_at | 是 | string / ^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}\.[0-9]{9}Z$ format=date-time |
| started_at | 是 | string / ^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}\.[0-9]{9}Z$ format=date-time OR null  |
| finished_at | 是 | string / ^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}\.[0-9]{9}Z$ format=date-time OR null  |
| error_code | 是 | string minLength=1 OR null  |
| run_url | 是 | string / ^/  |

## Error

| 字段 | 必填 | 类型/约束 |
| --- | --- | --- |
| error | 是 | object {code: string / ^[A-Z][A-Z0-9_]*$ ; message: string minLength=1}; required=code,message |

## ExportMetadata

| 字段 | 必填 | 类型/约束 |
| --- | --- | --- |
| type | 是 | enum metadata |
| export_schema_version | 是 | enum 1 |
| service_instance_id | 是 | string format=uuid |
| view_schema_version | 是 | enum 1 |
| run_id | 是 | string format=uuid |
| appid | 是 | string minLength=1 |
| model_id | 是 | enum GLM-5.2/Qwen3.6-27B/DeepSeek-V4-Flash-0731 |
| input_sha256 | 是 | string / ^[0-9a-f]{64}$  |
| settings_sha256 | 是 | string / ^[0-9a-f]{64}$  |
| data_range_utc | 是 | DataRange |
| filter | 是 | LengthFilter |
| sort | 是 | RequestSort |
| export_scope | 是 | enum group/filtered |
| expected_rows | 是 | string / ^(0&#124;[1-9][0-9]*)$(?![\s\S])  |

## ExportRequest

| 字段 | 必填 | 类型/约束 |
| --- | --- | --- |
| type | 是 | enum request |
| request_ref | 是 | RequestRef |
| hash_id | 是 | string minLength=1 |
| time_utc | 是 | string / ^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}\.[0-9]{9}Z$ format=date-time |
| json_tokens | 是 | string / ^(0&#124;[1-9][0-9]*)$(?![\s\S])  |
| prompt_tokens | 是 | string / ^(0&#124;[1-9][0-9]*)$(?![\s\S])  |
| ideal_cached_input_tokens | 是 | string / ^(0&#124;[1-9][0-9]*)$(?![\s\S])  |
| ideal_compute_input_tokens | 是 | string / ^(0&#124;[1-9][0-9]*)$(?![\s\S])  |
| completion_tokens | 是 | string / ^(0&#124;[1-9][0-9]*)$(?![\s\S])  |

## ExportSummary

| 字段 | 必填 | 类型/约束 |
| --- | --- | --- |
| type | 是 | enum summary |
| actual_rows | 是 | string / ^(0&#124;[1-9][0-9]*)$(?![\s\S])  |
| request_lines_sha256 | 是 | string / ^[0-9a-f]{64}$  |

## LegacyCapability

| 字段 | 必填 | 类型/约束 |
| --- | --- | --- |
| executable | 是 | boolean  |
| status | 是 | enum available/disabled/not_supported |
| strategy | 是 | string  |
| simulation_semantics | 是 | enum full_block_rule/chained_approximation |

## LegacyHTTPValidationError

| 字段 | 必填 | 类型/约束 |
| --- | --- | --- |
| detail | 否 | array<LegacyValidationError> |

## LegacyModelSettings

| 字段 | 必填 | 类型/约束 |
| --- | --- | --- |
| model_id | 是 | enum GLM-5.2/Qwen3.6-27B/DeepSeek-V4-Flash-0731 |
| revision | 否 | integer  |
| block_size | 是 | integer  |
| block_size_unit | 否 | const "simulation_input_tokens" |
| cp_world_size | 否 | integer  |
| mtp | 否 | boolean  |
| prefix_cache_enabled | 否 | boolean  |
| hybrid_enabled | 否 | boolean  |
| cache_mode | 是 | enum full_block/full_block_approximation/qwen_hybrid/deepseek_hybrid |
| model_aliases | 否 | array<string > |
| encoding_profile | 否 | string  |

## LegacyModelView

| 字段 | 必填 | 类型/约束 |
| --- | --- | --- |
| settings | 是 | LegacyModelSettings |
| capability | 是 | LegacyCapability |

## LegacyRuleUpdate

| 字段 | 必填 | 类型/约束 |
| --- | --- | --- |
| appid | 是 | string minLength=1 |
| model_id | 是 | enum GLM-5.2/Qwen3.6-27B/DeepSeek-V4-Flash-0731 |
| rule_id | 是 | string minLength=1 |
| expected_revision | 是 | integer minimum=0.0 maximum=9.223372036854776e+18 |
| metric | 是 | string  |
| comparator | 是 | enum lt/le/gt/ge |
| threshold | 是 | integer  OR number  |
| enabled | 否 | boolean  |
| route | 否 | enum prefix_analysis/length_analysis/signal_only OR null  |
| measurement_signature | 是 | string / ^[0-9a-f]{64}$  |

## LegacyRunState

| 字段 | 必填 | 类型/约束 |
| --- | --- | --- |
| run_id | 是 | string  |
| file_ref | 是 | string  |
| model_id | 是 | enum GLM-5.2/Qwen3.6-27B/DeepSeek-V4-Flash-0731 |
| status | 是 | enum queued/running/completed/no_valid_rows/failed/interrupted |
| created_at | 是 | string  |
| started_at | 否 | string  OR null  |
| finished_at | 否 | string  OR null  |
| settings | 否 | LegacyModelSettings OR null  |
| error_code | 否 | string  OR null  |
| snapshot | 否 | object {}; required= OR null  |
| result | 否 | object {}; required= OR null  |

## LegacyRunSubmission

| 字段 | 必填 | 类型/约束 |
| --- | --- | --- |
| file_ref | 是 | string minLength=1 |
| model_id | 是 | enum GLM-5.2/Qwen3.6-27B/DeepSeek-V4-Flash-0731 |

## LegacySettingsChanges

| 字段 | 必填 | 类型/约束 |
| --- | --- | --- |
| block_size | 否 | integer  OR null  |
| cp_world_size | 否 | integer  OR null  |
| mtp | 否 | boolean  OR null  |
| prefix_cache_enabled | 否 | boolean  OR null  |
| hybrid_enabled | 否 | boolean  OR null  |
| cache_mode | 否 | enum full_block/full_block_approximation/qwen_hybrid/deepseek_hybrid OR null  |
| model_aliases | 否 | array<string > OR null  |
| encoding_profile | 否 | string  OR null  |

## LegacySettingsUpdate

| 字段 | 必填 | 类型/约束 |
| --- | --- | --- |
| expected_revision | 是 | integer  |
| changes | 是 | LegacySettingsChanges |

## LegacyValidationError

| 字段 | 必填 | 类型/约束 |
| --- | --- | --- |
| loc | 是 | array<string  OR integer > |
| msg | 是 | string  |
| type | 是 | string  |
| input | 否 | JSON  |
| ctx | 否 | object {}; required= |

## LegacyModelsList

array<LegacyModelView>

