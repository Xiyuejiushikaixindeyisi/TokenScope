# S0 1.0.0 完整协议样例

全部为人工合成；独立样例可复用同一示意UUID，但不是同一次真实运行。数值旨在检查类型/协议，不证明tokenizer、缓存算法或性能。前端假服务必须标记synthetic。

[固定入口](../../../tasks/monitoring/batches/B005.1/S0_CONTRACT.md) / [机器用例清单](cases.json) / [接口映射](endpoint-examples.json) / [JSON Schema](../../schemas/monitoring-view-v1.schema.json)。

| 操作 | 完整样例文件（JSON省略扩展名） | 响应/说明 |
| --- | --- | --- |
| GET /monitoring/catalog | catalog-normal / catalog-empty / catalog-page-1 / catalog-page-2 | CatalogResponse |
| GET /monitoring/runs | runs-no-valid-rows | PublishedRunsResponse |
| GET /monitoring/events | event-completed / event-no-valid / event-failed / event-interrupted / event-reset-expired | SSE; replay.sse / reset.sse |
| GET /analysis-runs/{run_id}/view-snapshot | snapshot-normal / snapshot-qwen / snapshot-deepseek / snapshot-null-rate / snapshot-large-integer | ViewSnapshot; ETag/304 |
| GET /analysis-runs/{run_id}/requests | requests-normal / requests-duplicate-hash / requests-overflow / requests-empty | RequestsPage |
| GET /analysis-runs/{run_id}/requests/{source_record_index} | request-detail | RequestDetail |
| GET /analysis-runs/{run_id}/requests/{source_record_index}/body | request-body.txt | text/plain |
| GET /analysis-runs/{run_id}/requests/{source_record_index}/evidence | evidence-special_ranges / evidence-source_fields | EvidencePage |
| GET /analysis-runs/{run_id}/view-signals | signals-normal / signals-empty | SignalsPage |
| GET /monitoring/models/{model_id}/settings | settings-glm / settings-qwen / settings-deepseek | ModelSettingsResponse |
| PUT /monitoring/models/{model_id}/settings | settings-update → settings-glm | SettingsUpdate → ModelSettingsResponse; 示例分别独立 |
| GET /monitoring/threshold-rules | rules-page / rules-empty | RulesPage |
| PUT /monitoring/threshold-rules | rule-update → rule-response; rule-ratio / rule-fractional-count-threshold | RuleUpdate → RuleResponse |
| POST /analysis-runs | submission → submission-accepted | Submission → LegacyRunState; 202 |
| GET /analysis-runs/{run_id} | run-state | LegacyRunState |
| GET /analysis-submissions/{submission_key} | receipt-queued / receipt-running / receipt-completed / receipt-no_valid_rows / receipt-failed / receipt-interrupted | Receipt |
| GET /models | models-legacy | LegacyModelsList；旧numeric兼容 |
| GET /analysis-runs/{run_id}/requests/export | ../monitoring-view-v0.2/normal / empty (.ndjson / .csv) | 字节夹具+头见原manifest |

所有JSON完整必填字段及HTTP status/headers见cases.json。上表PUT的入参/响应为独立形状样例；要模拟同一次修改，响应revision递增并回显修改后值。无缺省阈值：90只是触发夹具，不是产品默认。

设计OpenAPI含全部查询参数、默认值/响应头；SSE用[回放原字节](replay.sse)与[reset无id](reset.sse)；[正文](request-body.txt)为原JSON UTF8。304无body，携带ETag、Cache-Control及实例头；不得将null JSON冒充空响应。

## 错误完整样例

message供人读，不用于分支；按HTTP状态与code处理。新增未知code保留通用错误显示，不当成功。请求/路径/正文不回显。400仅旧兼容入口保留；新增视图格式/校验错误使用422。终态error_code是任务错误，不等于某次GET的HTTP错误。

| HTTP | code | 完整JSON |
| --- | --- | --- |
| 404 | SUBMISSION_NOT_FOUND | [receipt-unknown_key_not_a_failed_run.json](receipt-unknown_key_not_a_failed_run.json) |
| 409 | SERVICE_INSTANCE_CHANGED | [receipt-wrong_instance_no_lookup_or_enqueue.json](receipt-wrong_instance_no_lookup_or_enqueue.json) |
| 404 | MODEL_NOT_FOUND | [error-404-model_not_found.json](error-404-model_not_found.json) |
| 404 | RUN_NOT_FOUND | [error-404-run_not_found.json](error-404-run_not_found.json) |
| 404 | GROUP_NOT_FOUND | [error-404-group_not_found.json](error-404-group_not_found.json) |
| 404 | REQUEST_NOT_FOUND | [error-404-request_not_found.json](error-404-request_not_found.json) |
| 404 | SUBMISSION_NOT_FOUND | [error-404-submission_not_found.json](error-404-submission_not_found.json) |
| 409 | RESULT_NOT_READY | [error-409-result_not_ready.json](error-409-result_not_ready.json) |
| 409 | CATALOG_REVISION_CHANGED | [error-409-catalog_revision_changed.json](error-409-catalog_revision_changed.json) |
| 409 | RULES_REVISION_CHANGED | [error-409-rules_revision_changed.json](error-409-rules_revision_changed.json) |
| 409 | REVISION_CONFLICT | [error-409-revision_conflict.json](error-409-revision_conflict.json) |
| 409 | SUBMISSION_KEY_CONFLICT | [error-409-submission_key_conflict.json](error-409-submission_key_conflict.json) |
| 409 | SERVICE_INSTANCE_CHANGED | [error-409-service_instance_changed.json](error-409-service_instance_changed.json) |
| 422 | INVALID_REQUEST | [error-422-invalid_request.json](error-422-invalid_request.json) |
| 422 | INVALID_EXPORT_QUERY | [error-422-invalid_export_query.json](error-422-invalid_export_query.json) |
| 422 | INVALID_PAGINATION | [error-422-invalid_pagination.json](error-422-invalid_pagination.json) |
| 422 | INVALID_LENGTH_QUERY | [error-422-invalid_length_query.json](error-422-invalid_length_query.json) |
| 422 | INVALID_BIN_WIDTH | [error-422-invalid_bin_width.json](error-422-invalid_bin_width.json) |
| 422 | INVALID_SETTINGS | [error-422-invalid_settings.json](error-422-invalid_settings.json) |
| 422 | EMPTY_UPDATE | [error-422-empty_update.json](error-422-empty_update.json) |
| 422 | UNSUPPORTED_CACHE_MODE | [error-422-unsupported_cache_mode.json](error-422-unsupported_cache_mode.json) |
| 422 | UNKNOWN_ENCODING_PROFILE | [error-422-unknown_encoding_profile.json](error-422-unknown_encoding_profile.json) |
| 503 | VIEW_INDEX_NOT_READY | [error-503-view_index_not_ready.json](error-503-view_index_not_ready.json) |
| 503 | VIEW_ARTIFACT_UNAVAILABLE | [error-503-view_artifact_unavailable.json](error-503-view_artifact_unavailable.json) |
| 503 | SSE_CAPACITY_EXCEEDED | [error-503-sse_capacity_exceeded.json](error-503-sse_capacity_exceeded.json) |
| 503 | STORAGE_UNAVAILABLE | [error-503-storage_unavailable.json](error-503-storage_unavailable.json) |
| 400 | INVALID_FILE_REF | [error-400-invalid_file_ref.json](error-400-invalid_file_ref.json) |
| 400 | INVALID_SETTINGS | [error-400-invalid_settings.json](error-400-invalid_settings.json) |

404缺组/缺请求显示空或不可用，SUBMISSION_NOT_FOUND必须显示未确认；409 revision/cursor类重读，幂等异体冲突显式处理，不新key重试；SERVICE_INSTANCE_CHANGED停止旧实例操作。422修正输入；503保留旧完整视图、给显式重试，不创建分析。完整R1/R2边界以S0固定入口为准。

## 复核命令

在项目根目录执行；仅依赖校验工具，不启动服务。项目运行uv.lock/.venv不修改，额外jsonschema放在项目专用缓存。

```bash
python3 scripts/contracts/build_monitoring_view_v1.py
UV_CACHE_DIR="$PWD/env/.contract-cache" /home/zhangxiyue/.local/bin/uv run --no-project --python "$PWD/.venv/bin/python" --with jsonschema==4.23.0 python scripts/contracts/validate_monitoring_view_v1.py
```

[实际契约检查](../../../../artifacts/validation/monitoring/B005.1/S0/contract-check.json)记录工具依赖版本、通过项及范围。文件SHA由S0_MANIFEST固定；重新生成后必须校验摘要，不把生成动作当成版本自动升级。
