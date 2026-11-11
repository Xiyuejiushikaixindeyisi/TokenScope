# V3B001 TESTS — 实际记录

2026-11-10，候选v3b001-local-1；源码身份见[candidate.json](../../../../../artifacts/validation/development-v3/V3B001/attempt-05/candidate.json)。本批是组件/API登记与来源测试，不是生产服务E2E/硬内存验收。

## 门禁映射

| ID | 实际用例/覆盖 | 结论 |
| --- | --- | --- |
| T01 | test_receipt_registration_does_not_resolve_source_or_load_assets；test_large_parent_does_not_expand_member_or_exclusion_lists；test_real_seal_exact_members_and_sample_only_reads | PASS_COMPONENT：HTTP只登记，100000元数据行固定6成员，封存后不读原源；真实受控执行在B002复测。 |
| T02 | test_byte_boundary_before_body_access；test_byte_admission_precedes_selected_body_materialization；真实source只物化精确4成员；同hash不同key | PASS：超过bytes时无完整正文物化；UTF-8字节通过blob长度获取。 |
| T03 | test_first_prefix_latest_suffix_with_exact_tied_timestamp_members；test_rejection_breaks_contiguity_and_trailing_bad_record_keeps_last_valid_segment；empty/whole/no-review；A适配器禁止读取B/原source | PASS：A/B不重叠/顺序稳定，不能访问范围外成员或_raw rows旁路。 |
| T04 | test_changed_source_does_not_publish_snapshot；test_invalid_token_slice_never_publishes(sha/count/path/missing)；test_cancellation_and_disk_budget_never_seal；test_user_index_revision_is_pinned_in_sample | PASS：变化/错误引用/取消/disk失败无可用快照；基线source/旧schema保持。 |
| T05 | test_automatic_request_only_and_strict_wire；test_frozen_sampling_examples_and_reference_guards；test_wire_roundtrip_preserves_exclusion_counts_and_rejects_numeric_wire_values；旧契约回归 | PASS：自动模式，不接收recipe/Token方向；新旧整数与引用校验通过。 |

实际测试文件：tests/unit/analysis_common/test_sampling_v3.py、test_contracts_v3.py；tests/integration/analysis/test_sample_source_v3.py。旧回归：test_source.py及unit的test_contracts.py、test_schema.py、test_http_schema.py、test_recommendation_freeze.py。

## 环境与命令

cwd /home/zhangxiyue/TokenScope；WSL Ubuntu-22.04，项目.venv/Python3.11；实际本地模型资产/配置身份记录在candidate.json。prepare来源使用真实监控编码生成的合成数据；元数据100000行是生成器组件用例，不能称真实15万请求/华为压力验收。API使用TestClient而非新服务/browser；未启动旧服务并行E2E。

最终确切命令（由PowerShell调用WSL，stdout/stderr分别留存）：

```bash
.venv/bin/python -m pytest tests/unit/analysis_common/test_sampling_v3.py tests/unit/analysis_common/test_contracts_v3.py tests/integration/analysis/test_sample_source_v3.py tests/integration/analysis/test_source.py tests/unit/analysis_common/test_contracts.py tests/unit/analysis_common/test_schema.py tests/unit/analysis_common/test_http_schema.py tests/unit/analysis_common/test_recommendation_freeze.py --basetemp=artifacts/validation/development-v3/V3B001/attempt-05/pytest -q
.venv/bin/ruff check src tests scripts/export_sampling_schema.py
.venv/bin/mypy src/tokenscope
.venv/bin/python scripts/export_sampling_schema.py --check
```

| Attempt | 实际结果 | 后续 |
| --- | --- | --- |
| 初次静态工具输出 | ruff 5项，mypy 4项 | I03修复，不改规则。 |
| attempt-01 | pytest 1 failed / 14 passed，13.44s；元组负例构造错误 | I04修复，保留原日志。 |
| attempt-02 | ruff通过；全源码mypy 1个override错误 | I03同步ObservedSource类型。 |
| attempt-03 | 41 passed，25.18s；ruff通过，mypy126文件通过 | 补齐四类token引用负例及user revision。 |
| attempt-04 | 46 passed，33.68s；ruff/mypy通过；schema --check通过 | 检查后补充元数据TEXT读取边界，重跑。 |
| attempt-05 | **46 passed，0 failed/skip，33.22s**；ruff通过；mypy126文件通过 | 当前候选组件门禁通过。 |

每次pytest有同一FastAPI/httpx弃用warning，无失败/skip。最终[日志目录](../../../../../artifacts/validation/development-v3/V3B001/attempt-05)保留原输出；原件与旧契约无修改，git diff --check通过。没有内存峰值/P95/真实浏览器或五组业务数值，相关项仍待后续批次。
