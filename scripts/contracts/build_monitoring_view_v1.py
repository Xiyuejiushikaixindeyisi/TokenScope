"""Generate the S0 design contract and synthetic examples; never import or run the service."""

import copy
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "docs/contracts"
EX = OUT / "examples/monitoring-view-s0"
D = {}


def ref(n):
    return {"$ref": "#/$defs/" + n}


def enum(*v):
    return {"enum": list(v)}


def arr(s, **kw):
    return {"type": "array", "items": s, **kw}


def nullable(s):
    return {"anyOf": [s, {"type": "null"}]}


def obj(props, optional=()):
    return {
        "type": "object",
        "properties": props,
        "required": [k for k in props if k not in optional],
        "additionalProperties": False,
    }


def define(n, props, optional=()):
    D[n] = obj(props, optional)
    return ref(n)


S = {"type": "string"}
BOOL = {"type": "boolean"}
COUNT = {
    "type": "string",
    "pattern": r"^(0|[1-9][0-9]*)$(?![\s\S])",
    "description": "Nonnegative decimal integer, never a JSON number. Arithmetic is exact.",
}
POS = {"type": "string", "pattern": r"^[1-9][0-9]*$(?![\s\S])"}
SIGNED = {"type": "string", "pattern": r"^(0|-?[1-9][0-9]*)$(?![\s\S])"}
SHA = {"type": "string", "pattern": r"^[0-9a-f]{64}$"}
ID = {"type": "string", "minLength": 1}
UUID = {"type": "string", "format": "uuid"}
UTC = {
    "type": "string",
    "format": "date-time",
    "pattern": r"^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}\.[0-9]{9}Z$",
}
URL = {"type": "string", "pattern": r"^/"}
MODEL = enum("GLM-5.2", "Qwen3.6-27B", "DeepSeek-V4-Flash-0731")
STATUS = enum("queued", "running", "completed", "no_valid_rows", "failed", "interrupted")
LENGTHS = ["json_tokens", "prompt_tokens", "ideal_compute_input_tokens"]
TOTALS = [
    "json_tokens",
    "prompt_tokens",
    "ideal_cached_input_tokens",
    "ideal_compute_input_tokens",
    "completion_tokens",
]
METRICS = (
    ["request_count", "ideal_hit_rate"]
    + ["totals." + n for n in TOTALS]
    + [f"quantiles.{n}.{q}" for n in LENGTHS for q in ("p50", "p80", "p90")]
)
RATE = {"type": "number", "minimum": 0, "maximum": 1}
NUM = {"type": "number", "description": "Finite JSON number; NaN/Infinity forbidden."}
VALUE = {"oneOf": [SIGNED, NUM]}
IDENT = dict(service_instance_id=UUID, view_schema_version=enum("1"))
PAGE = dict(
    offset=COUNT,
    limit={"type": "integer", "minimum": 1, "maximum": 1000},
    total=COUNT,
    next_offset=nullable(COUNT),
)
RANGE = define("DataRange", dict(start=nullable(UTC), end=nullable(UTC)))
QUANT = define("Quantiles", {q: nullable(COUNT) for q in ("p50", "p80", "p90")})
CAP = define(
    "Capability",
    dict(
        executable=BOOL,
        status=enum("available", "disabled", "not_supported"),
        strategy=enum("full-block-mtp-v1", "no-cache-v1", "reserved_hybrid"),
        simulation_semantics=enum("full_block_rule", "chained_approximation"),
    ),
)
settings = dict(
    model_id=MODEL,
    revision=POS,
    block_size=POS,
    block_size_unit=enum("simulation_input_tokens"),
    cp_world_size=POS,
    mtp=BOOL,
    prefix_cache_enabled=BOOL,
    hybrid_enabled=BOOL,
    cache_mode=enum("full_block", "full_block_approximation", "qwen_hybrid", "deepseek_hybrid"),
    model_aliases=arr(ID, uniqueItems=True),
    encoding_profile=enum("default", "thinking_enabled", "thinking_disabled"),
)
define("Settings", settings)
for model, modes in [
    ("GLM-5.2", ["full_block"]),
    ("Qwen3.6-27B", ["full_block_approximation", "qwen_hybrid"]),
    ("DeepSeek-V4-Flash-0731", ["full_block_approximation", "deepseek_hybrid"]),
]:
    D["Settings"].setdefault("allOf", []).append(
        {
            "if": {"properties": {"model_id": {"const": model}}},
            "then": {"properties": {"cache_mode": {"enum": modes}}},
        }
    )
changes = {
    k: v for k, v in settings.items() if k not in ("model_id", "revision", "block_size_unit")
}
define("SettingsChanges", changes, tuple(changes))
D["SettingsChanges"]["minProperties"] = 1
define("SettingsUpdate", dict(expected_revision=POS, changes=ref("SettingsChanges")))
define("ModelSettingsResponse", {**IDENT, "settings": ref("Settings"), "capability": CAP})
ruleprops = dict(
    appid=ID,
    model_id=MODEL,
    rule_id=ID,
    revision=POS,
    metric=enum(*METRICS),
    comparator=enum("lt", "le", "gt", "ge"),
    threshold=VALUE,
    value_kind=enum("integer", "ratio", "number"),
    enabled=BOOL,
    route=nullable(enum("prefix_analysis", "length_analysis", "signal_only")),
    measurement_signature=SHA,
)


def numeric_branch(schema):
    schema["allOf"] = [
        {
            "if": {"properties": {"value_kind": {"const": "integer"}}},
            "then": {"properties": {"threshold": SIGNED}},
            "else": {"properties": {"threshold": NUM}},
        }
    ]


define("Rule", ruleprops)
numeric_branch(D["Rule"])
rp = {k: v for k, v in ruleprops.items() if k != "revision"}
rp["expected_revision"] = COUNT
define("RuleUpdate", rp)
numeric_branch(D["RuleUpdate"])
define("RuleResponse", {**IDENT, "rule": ref("Rule"), "rules_revision": COUNT})
define("RulesPage", {**IDENT, **PAGE, "rules_revision": COUNT, "items": arr(ref("Rule"))})
D["ThresholdState"] = {
    "oneOf": [
        obj(dict(status=enum("unconfigured"))),
        obj(
            dict(
                rule_id=ID,
                revision=POS,
                status=enum("clear", "needs_review", "metric_unavailable", "triggered"),
            )
        ),
    ]
}
define(
    "ThresholdComparison",
    dict(
        rule=ref("Rule"),
        observed_value=nullable(VALUE),
        state=enum("disabled", "clear", "needs_review", "metric_unavailable", "triggered"),
    ),
)
define("Totals", {k: COUNT for k in TOTALS})
define("MeasurementSignatures", {k: SHA for k in METRICS})
define(
    "GroupMetrics",
    dict(
        appid=ID,
        model_id=MODEL,
        request_count=POS,
        totals=ref("Totals"),
        quantiles=obj({k: QUANT for k in LENGTHS}),
        ideal_hit_rate=nullable(RATE),
        json_to_prompt_delta=SIGNED,
        threshold_states=arr(ref("ThresholdState"), minItems=1),
        measurement_signatures=ref("MeasurementSignatures"),
        capability=CAP,
    ),
)
define(
    "HistogramBin",
    dict(lower=COUNT, upper=nullable(COUNT), count=COUNT, share=nullable(RATE), overflow=BOOL),
)
define(
    "HistogramSummary",
    dict(
        mode_bin_indices=arr(COUNT),
        mode_count=COUNT,
        mode_share=nullable(RATE),
        under_8k_count=COUNT,
        overflow_count=COUNT,
        max_length=nullable(COUNT),
    ),
)
define(
    "Histogram",
    dict(
        bin_width=enum(1000, 2000, 5000),
        regular_domain={"const": ["0", "200000"]},
        overflow_start=enum("200000"),
        boundary=enum("left_closed_right_open"),
        sample_count=COUNT,
        quantile_algorithm=enum("nearest_rank"),
        quantiles=QUANT,
        bins=arr(ref("HistogramBin")),
        summary=ref("HistogramSummary"),
    ),
)
define(
    "Distributions",
    {m: obj({str(w): ref("Histogram") for w in (1000, 2000, 5000)}) for m in LENGTHS},
)
define(
    "FileQuality",
    dict(
        scope=enum("file"),
        records_read=COUNT,
        valid_requests=COUNT,
        skipped_rows=COUNT,
        duplicate_hash_id_rows=COUNT,
    ),
)
define(
    "GroupQuality",
    dict(
        scope=enum("appid"),
        coverage=enum("known_appid_rows_only"),
        valid_requests=POS,
        encoding_rejected_rows=COUNT,
        skipped_rows={"type": "null"},
        duplicate_scope=enum("appid"),
        duplicate_hash_id_rows_within_group=COUNT,
        unattributed_skips_available_in=enum("file_quality"),
    ),
)
define(
    "RuntimeIdentity",
    dict(
        code_version=ID,
        algorithm_version=ID,
        asset_identity=SHA,
        encoder_identity=SHA,
        asset_revision=ID,
        encoding_profile=ID,
        profile_json=S,
    ),
)
define(
    "SnapshotIdentity",
    {**IDENT, "run_id": UUID, "appid": ID, "model_id": MODEL, "publish_seq": POS},
)
define(
    "Provenance",
    dict(
        data_range_utc=RANGE,
        file_data_range_utc=RANGE,
        published_at=UTC,
        source_label=ID,
        input_sha256=SHA,
        settings=ref("Settings"),
        rules=arr(ref("Rule")),
        runtime=ref("RuntimeIdentity"),
        simulation_semantics=enum("full_block_rule", "chained_approximation"),
        metadata_origin=enum("stored_facts_projection"),
    ),
)
define("SignalSummary", dict(count=COUNT, event_ids_digest=SHA, view_signals_url=URL))
define(
    "ViewCapabilities",
    dict(
        original_json=BOOL,
        light_evidence=BOOL,
        requests=BOOL,
        export=BOOL,
        templated_text=enum(False),
    ),
)
define("ViewLinks", dict(requests=URL, view_signals=URL, export_ndjson=URL, export_csv=URL))
define(
    "ViewSnapshot",
    dict(
        identity=ref("SnapshotIdentity"),
        provenance=ref("Provenance"),
        metrics=ref("GroupMetrics"),
        distributions=ref("Distributions"),
        quality=obj(dict(file_quality=ref("FileQuality"), group_quality=ref("GroupQuality"))),
        thresholds=arr(ref("ThresholdComparison")),
        signal_summary=ref("SignalSummary"),
        capabilities=ref("ViewCapabilities"),
        links=ref("ViewLinks"),
    ),
)
define(
    "CatalogItem",
    dict(
        appid=ID,
        model_id=MODEL,
        active_run_id=UUID,
        publish_seq=POS,
        published_at=UTC,
        data_range_utc=RANGE,
        snapshot_url=URL,
    ),
)
define(
    "CatalogResponse",
    {**IDENT, **PAGE, "cursor": ID, "catalog_revision": COUNT, "items": arr(ref("CatalogItem"))},
)
define(
    "PublishedRun",
    dict(
        run_id=UUID,
        model_id=MODEL,
        publish_seq=POS,
        published_at=UTC,
        status=enum("completed", "no_valid_rows"),
        file_data_range_utc=RANGE,
        group_count=COUNT,
        input_sha256=SHA,
        source_label=ID,
    ),
)
define(
    "PublishedRunsResponse",
    {**IDENT, **PAGE, "catalog_revision": COUNT, "items": arr(ref("PublishedRun"))},
)
define(
    "ResultPublishedEvent",
    {
        **IDENT,
        "run_id": UUID,
        "model_id": MODEL,
        "publish_seq": POS,
        "published_at": UTC,
        "status": enum("completed", "no_valid_rows"),
    },
)
define(
    "RunTerminalEvent",
    {
        **IDENT,
        "run_id": UUID,
        "model_id": MODEL,
        "event_seq": POS,
        "status": enum("failed", "interrupted"),
        "error_code": ID,
        "finished_at": UTC,
    },
)
define(
    "ResetEvent",
    {
        **IDENT,
        "reason": enum("expired", "future_cursor", "instance_changed", "invalid_cursor"),
        "catalog_url": URL,
    },
)
define("RequestRef", dict(run_id=UUID, source_record_index=POS))
fact = dict(request_ref=ref("RequestRef"), hash_id=ID, time_utc=UTC, **{k: COUNT for k in TOTALS})
define("RequestFact", fact)
define("RequestRow", {**fact, "position": POS})
define(
    "LengthFilter",
    dict(
        metric=enum(*LENGTHS),
        lower=COUNT,
        upper=nullable(COUNT),
        hash_id=nullable(ID),
        hash_match=enum("exact", "prefix"),
    ),
)
define(
    "RequestSort",
    dict(
        by=enum("time_ns", "source_record_index", *TOTALS),
        order=enum("asc", "desc"),
        tie_breaker=enum("source_record_index_asc"),
    ),
)
define(
    "RequestsPage",
    {
        **IDENT,
        **PAGE,
        "run_id": UUID,
        "appid": ID,
        "model_id": MODEL,
        "filter": ref("LengthFilter"),
        "sort": ref("RequestSort"),
        "items": arr(ref("RequestRow")),
    },
)
define(
    "EvidenceSummary",
    dict(
        raw_json_sha256=SHA,
        rendered_sha256=SHA,
        rendered_characters=COUNT,
        rendered_utf8_bytes=COUNT,
        special_ranges_count=COUNT,
        source_fields_count=COUNT,
        special_ranges_unit=enum("utf8_bytes_half_open"),
        special_ranges_semantics=ID,
        effective_options_json=S,
        source_attribution=enum("references_only_not_additive_token_contributions"),
        source_attribution_status=enum("partial", "unknown"),
    ),
)
define(
    "BodyPreview", dict(text=S, total_utf8_bytes=COUNT, preview_utf8_bytes=COUNT, truncated=BOOL)
)
define(
    "RequestDetail",
    {
        **IDENT,
        "run_id": UUID,
        "appid": ID,
        "model_id": MODEL,
        "request": ref("RequestFact"),
        "body_preview": ref("BodyPreview"),
        "evidence_summary": ref("EvidenceSummary"),
        "capabilities": obj(
            dict(original_json=BOOL, light_evidence=BOOL, templated_text=enum(False))
        ),
        "links": obj(dict(body=URL, evidence=URL)),
    },
)
define("SpecialRange", dict(start=COUNT, end=COUNT))
define("SourceField", dict(json_pointer=S, characters=COUNT, utf8_bytes=COUNT, sha256=SHA))
ep = {
    **IDENT,
    **PAGE,
    "run_id": UUID,
    "appid": ID,
    "model_id": MODEL,
    "request_ref": ref("RequestRef"),
    "summary": ref("EvidenceSummary"),
}
D["EvidencePage"] = {
    "oneOf": [
        obj({**ep, "section": enum("special_ranges"), "items": arr(ref("SpecialRange"))}),
        obj({**ep, "section": enum("source_fields"), "items": arr(ref("SourceField"))}),
    ]
}
define(
    "Signal",
    dict(
        run_id=UUID,
        appid=ID,
        model_id=MODEL,
        event_id=SHA,
        metric=enum(*METRICS),
        comparator=enum("lt", "le", "gt", "ge"),
        value_kind=enum("integer", "ratio", "number"),
        observed_value=nullable(VALUE),
        threshold=VALUE,
        rule_id=ID,
        revision=POS,
        route=enum("prefix_analysis", "length_analysis", "signal_only"),
        status=enum("pending_consumer"),
        published_at=UTC,
    ),
)
numeric_branch(D["Signal"])
define(
    "SignalsPage",
    {**IDENT, **PAGE, "run_id": UUID, "appid": ID, "model_id": MODEL, "items": arr(ref("Signal"))},
)
define(
    "Submission",
    dict(
        file_ref=ID,
        model_id=MODEL,
        submission_key={"type": "string", "pattern": r"^[A-Za-z0-9._-]{1,128}$"},
    ),
    ("submission_key",),
)
define(
    "Receipt",
    {
        **IDENT,
        "submission_key": ID,
        "run_id": UUID,
        "model_id": MODEL,
        "status": STATUS,
        "created_at": UTC,
        "started_at": nullable(UTC),
        "finished_at": nullable(UTC),
        "error_code": nullable(ID),
        "run_url": URL,
    },
)
D["Receipt"]["allOf"] = [
    {
        "if": {
            "properties": {
                "status": {"enum": ["completed", "no_valid_rows", "failed", "interrupted"]}
            }
        },
        "then": {"properties": {"finished_at": UTC}},
        "else": {"properties": {"finished_at": {"type": "null"}}},
    },
    {
        "if": {"properties": {"status": {"enum": ["failed", "interrupted"]}}},
        "then": {"properties": {"error_code": ID}},
        "else": {"properties": {"error_code": {"type": "null"}}},
    },
]
define(
    "Error",
    dict(error=obj(dict(code={"type": "string", "pattern": r"^[A-Z][A-Z0-9_]*$"}, message=ID))),
)
define(
    "ExportMetadata",
    dict(
        type=enum("metadata"),
        export_schema_version=enum("1"),
        **IDENT,
        run_id=UUID,
        appid=ID,
        model_id=MODEL,
        input_sha256=SHA,
        settings_sha256=SHA,
        data_range_utc=RANGE,
        filter=ref("LengthFilter"),
        sort=ref("RequestSort"),
        export_scope=enum("group", "filtered"),
        expected_rows=COUNT,
    ),
)
define("ExportRequest", dict(type=enum("request"), **fact))
define("ExportSummary", dict(type=enum("summary"), actual_rows=COUNT, request_lines_sha256=SHA))
# Reuse the exact legacy OpenAPI shapes. Opaque snapshot/result JSON is not a view DTO.
old = json.loads((OUT / "schemas/monitoring-current.openapi.json").read_text())


def legacy_refs(x):
    if isinstance(x, dict):
        return {
            k: ("#/$defs/Legacy" + v.rsplit("/", 1)[-1] if k == "$ref" else legacy_refs(v))
            for k, v in x.items()
        }
    if isinstance(x, list):
        return [legacy_refs(v) for v in x]
    return x


for name, body in old["components"]["schemas"].items():
    D["Legacy" + name] = legacy_refs(body)
for name in ("Rule", "RuleUpdate", "Signal"):
    D[name]["allOf"].append(
        {
            "if": {"properties": {"metric": {"const": "ideal_hit_rate"}}},
            "then": {"properties": {"value_kind": {"const": "ratio"}}},
            "else": {"properties": {"value_kind": {"enum": ["integer", "number"]}}},
        }
    )
D["Signal"]["allOf"].append(
    {
        "if": {"properties": {"metric": {"const": "ideal_hit_rate"}}},
        "then": {"properties": {"observed_value": nullable(RATE)}},
        "else": {"properties": {"observed_value": nullable(COUNT)}},
    }
)
D["LegacyModelsList"] = arr(ref("LegacyModelView"))
schema = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "title": "TokenScope monitoring view S0 contract",
    "description": (
        "S0 contract 1.0.0, view_schema=1; intended API, not implemented runtime OpenAPI."
    ),
    "x-contract-version": "1.0.0",
    "$defs": D,
}
(OUT / "schemas/monitoring-view-v1.schema.json").write_text(
    json.dumps(schema, ensure_ascii=False, indent=2) + "\n"
)

# Deterministic fully shaped examples; semantically significant samples customized below.
U = "11111111-1111-4111-8111-111111111111"
RUN = "22222222-2222-4222-8222-222222222222"
T = "2026-10-27T00:00:00.123456789Z"
APP = "synthetic-app-1"
MOD = "GLM-5.2"


def sample(s, key=""):
    if "$ref" in s:
        return sample(D[s["$ref"].rsplit("/", 1)[-1]], key)
    if "const" in s:
        return copy.deepcopy(s["const"])
    if "enum" in s:
        return s["enum"][0]
    if "oneOf" in s:
        return sample(s["oneOf"][0], key)
    if "anyOf" in s:
        return (
            None if any(x.get("type") == "null" for x in s["anyOf"]) else sample(s["anyOf"][0], key)
        )
    typ = s.get("type")
    if typ == "object":
        return {k: sample(v, k) for k, v in s.get("properties", {}).items()}
    if typ == "array":
        return [sample(s["items"])] if s.get("minItems", 0) else []
    if typ == "boolean":
        return False
    if typ == "integer":
        return s.get("minimum", 0)
    if typ == "number":
        return 0.0
    if typ == "null":
        return None
    if typ == "string":
        if s.get("format") == "uuid":
            return RUN if key in ("run_id", "active_run_id") else U
        pat = s.get("pattern", "")
        if pat == SHA["pattern"]:
            return "a" * 64
        if pat == UTC["pattern"]:
            return T
        if pat == POS["pattern"]:
            return "1"
        if pat in (COUNT["pattern"], SIGNED["pattern"]):
            return "0"
        if pat.startswith("^/"):
            return "/sample"
        if pat.startswith("^[A-Z]"):
            return "INVALID_REQUEST"
        if key == "appid":
            return APP
        if key in ("profile_json", "effective_options_json"):
            return "{}"
        return "sample"
    return {}


EX.mkdir(parents=True, exist_ok=True)
cases = []
# Only obsolete generated error fixtures, never consumer-authored files.
for stale in EX.glob("error-*.json"):
    if not stale.name.split("-")[1].isdigit():
        stale.unlink()


def emit(name, typ, data=None, status=200, headers=None):
    data = sample(ref(typ)) if data is None else data
    path = EX / (name + ".json")
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")
    cases.append(
        dict(
            name=name,
            schema=typ,
            path=str(path.relative_to(OUT)),
            http_status=status,
            headers=headers or {},
            synthetic=True,
        )
    )
    return data


st = sample(ref("Settings"))
st.update(block_size="128", model_aliases=["glm-5.2"], mtp=True, prefix_cache_enabled=True)
cap = dict(
    executable=True,
    status="available",
    strategy="full-block-mtp-v1",
    simulation_semantics="full_block_rule",
)
sv = {**sample(ref("ModelSettingsResponse")), "settings": st, "capability": cap}
emit("settings-glm", "ModelSettingsResponse", sv)
for name, model, b, mode in [
    ("qwen", "Qwen3.6-27B", "1536", "full_block_approximation"),
    ("deepseek", "DeepSeek-V4-Flash-0731", "32", "full_block_approximation"),
]:
    value = copy.deepcopy(sv)
    value["settings"].update(model_id=model, block_size=b, cache_mode=mode, model_aliases=[model])
    value["capability"]["simulation_semantics"] = "chained_approximation"
    emit("settings-" + name, "ModelSettingsResponse", value)
emit(
    "settings-update",
    "SettingsUpdate",
    dict(expected_revision="1", changes=dict(block_size="256", mtp=False)),
    200,
)
rule = sample(ref("Rule"))
rule.update(
    rule_id="long-p50",
    metric="quantiles.prompt_tokens.p50",
    comparator="gt",
    threshold="90",
    enabled=True,
    route="length_analysis",
)
emit(
    "rule-update",
    "RuleUpdate",
    {**{k: v for k, v in rule.items() if k != "revision"}, "expected_revision": "0"},
)
emit(
    "rule-response",
    "RuleResponse",
    {**sample(ref("RuleResponse")), "rule": rule, "rules_revision": "1"},
)
rp = sample(ref("RulesPage"))
rp.update(total="1", items=[rule], rules_revision="1", next_offset=None, limit=100)
emit("rules-page", "RulesPage", rp)
snap = sample(ref("ViewSnapshot"))
snap["identity"].update(run_id=RUN, appid=APP, model_id=MOD, publish_seq="42")
snap["provenance"].update(
    data_range_utc=dict(start=T, end=T),
    file_data_range_utc=dict(start=T, end=T),
    published_at=T,
    source_label="synthetic.csv",
    settings=st,
    rules=[rule],
)
snap["provenance"]["runtime"].update(
    code_version="synthetic-design",
    algorithm_version="full-block-mtp-v1",
    asset_revision="synthetic",
    encoding_profile="default",
)
gm = snap["metrics"]
gm.update(
    request_count="1",
    totals=dict(
        json_tokens="80",
        prompt_tokens="100",
        ideal_cached_input_tokens="0",
        ideal_compute_input_tokens="100",
        completion_tokens="5",
    ),
    ideal_hit_rate=0.0,
    json_to_prompt_delta="20",
    capability=cap,
    threshold_states=[dict(rule_id="long-p50", revision="1", status="triggered")],
)
oldexample = json.loads((OUT / "examples/monitoring-view-v1-draft.json").read_text())
snap["distributions"] = oldexample["snapshot_fragment"]["distributions"]
gm["quantiles"] = {m: copy.deepcopy(snap["distributions"][m]["5000"]["quantiles"]) for m in LENGTHS}
snap["quality"] = oldexample["snapshot_fragment"]["quality"]
snap["thresholds"] = [dict(rule=rule, observed_value="100", state="triggered")]
snap["signal_summary"].update(
    event_ids_digest=hashlib.sha256(("a" * 64 + "\n").encode()).hexdigest(),
    count="1",
    view_signals_url=f"/analysis-runs/{RUN}/view-signals?appid={APP}",
)
snap["capabilities"].update(original_json=True, light_evidence=True, requests=True, export=True)
snap["links"].update(
    requests=f"/analysis-runs/{RUN}/requests?appid={APP}",
    view_signals=f"/analysis-runs/{RUN}/view-signals?appid={APP}",
    export_ndjson=f"/analysis-runs/{RUN}/requests/export?appid={APP}&format=ndjson",
    export_csv=f"/analysis-runs/{RUN}/requests/export?appid={APP}&format=csv",
)
emit("snapshot-normal", "ViewSnapshot", snap)
for name, model, b, mode in [
    ("qwen", "Qwen3.6-27B", "1536", "full_block_approximation"),
    ("deepseek", "DeepSeek-V4-Flash-0731", "32", "full_block_approximation"),
]:
    v = copy.deepcopy(snap)
    v["identity"]["model_id"] = model
    v["metrics"]["model_id"] = model
    v["provenance"]["settings"].update(
        model_id=model,
        block_size=b,
        cache_mode=mode,
        encoding_profile="thinking_disabled" if name == "deepseek" else "default",
    )
    v["provenance"]["simulation_semantics"] = "chained_approximation"
    v["metrics"]["capability"]["simulation_semantics"] = "chained_approximation"
    v["provenance"]["rules"] = []
    v["thresholds"] = []
    v["metrics"]["threshold_states"] = [dict(status="unconfigured")]
    v["signal_summary"]["count"] = "0"
    v["signal_summary"]["event_ids_digest"] = hashlib.sha256(b"").hexdigest()
    v["provenance"]["runtime"]["encoding_profile"] = v["provenance"]["settings"]["encoding_profile"]
    emit("snapshot-" + name, "ViewSnapshot", v)
zero = copy.deepcopy(snap)
zero["metrics"].update(ideal_hit_rate=None, threshold_states=[dict(status="unconfigured")])
zero["metrics"]["totals"].update(
    prompt_tokens="0", ideal_cached_input_tokens="0", ideal_compute_input_tokens="0"
)
zero["metrics"]["json_to_prompt_delta"] = "-80"
zero["provenance"]["rules"] = []
zero["thresholds"] = []
zero["signal_summary"].update(count="0", event_ids_digest=hashlib.sha256(b"").hexdigest())
for m in ("prompt_tokens", "ideal_compute_input_tokens"):
    for h in zero["distributions"][m].values():
        h["quantiles"] = {k: "0" for k in ("p50", "p80", "p90")}
        h["summary"]["max_length"] = "0"
    zero["metrics"]["quantiles"][m] = {k: "0" for k in ("p50", "p80", "p90")}
emit("snapshot-null-rate", "ViewSnapshot", zero)
big = copy.deepcopy(snap)
big["metrics"]["totals"]["completion_tokens"] = "9007199254740993"
emit("snapshot-large-integer", "ViewSnapshot", big)
cat = sample(ref("CatalogResponse"))
item = sample(ref("CatalogItem"))
item.update(
    appid=APP,
    active_run_id=RUN,
    publish_seq="42",
    data_range_utc=dict(start=T, end=T),
    snapshot_url=f"/analysis-runs/{RUN}/view-snapshot?appid={APP}",
)
cat.update(
    cursor=U + ":42", catalog_revision="42", total="1", limit=100, next_offset=None, items=[item]
)
emit("catalog-normal", "CatalogResponse", cat)
empty = copy.deepcopy(cat)
empty.update(items=[], total="0", catalog_revision="0", cursor=U + ":0")
emit("catalog-empty", "CatalogResponse", empty)
page = copy.deepcopy(cat)
page.update(total="2", limit=1, next_offset="1")
emit("catalog-page-1", "CatalogResponse", page)
page2 = copy.deepcopy(page)
page2.update(offset="1", next_offset=None)
page2["items"][0]["appid"] = "synthetic-app-2"
emit("catalog-page-2", "CatalogResponse", page2)
pr = sample(ref("PublishedRun"))
pr.update(
    publish_seq="42",
    status="no_valid_rows",
    group_count="0",
    file_data_range_utc=dict(start=None, end=None),
)
runs = sample(ref("PublishedRunsResponse"))
runs.update(catalog_revision="42", items=[pr], total="1", limit=100, next_offset=None)
emit("runs-no-valid-rows", "PublishedRunsResponse", runs)
fact = sample(ref("RequestFact"))
fact.update(hash_id="synthetic-duplicate", time_utc=T, **snap["metrics"]["totals"])
reqs = sample(ref("RequestsPage"))
reqs.update(items=[{**fact, "position": "1"}], total="1", limit=50, next_offset=None)
reqs["filter"].update(
    metric="prompt_tokens", lower="0", upper=None, hash_id=None, hash_match="exact"
)
reqs["sort"].update(by="prompt_tokens", order="desc")
emit("requests-normal", "RequestsPage", reqs)
dups = copy.deepcopy(reqs)
second = copy.deepcopy(dups["items"][0])
second["request_ref"]["source_record_index"] = "2"
second["position"] = "2"
dups.update(items=dups["items"] + [second], total="2")
emit("requests-duplicate-hash", "RequestsPage", dups)
tail = copy.deepcopy(reqs)
tail["filter"]["lower"] = "200000"
tail["items"][0].update(prompt_tokens="220000", ideal_compute_input_tokens="220000")
emit("requests-overflow", "RequestsPage", tail)
raw = '{"messages":[{"role":"user","content":"中文🙂"}]}'
detail = sample(ref("RequestDetail"))
detail.update(request=fact)
detail["body_preview"] = dict(
    text=raw,
    total_utf8_bytes=str(len(raw.encode())),
    preview_utf8_bytes=str(len(raw.encode())),
    truncated=False,
)
detail["evidence_summary"].update(
    raw_json_sha256=hashlib.sha256(raw.encode()).hexdigest(),
    rendered_characters="3",
    rendered_utf8_bytes="10",
    special_ranges_count="1",
    source_fields_count="1",
    special_ranges_semantics="recognized_added_token_spelling_origin_unassigned",
)
detail["capabilities"].update(original_json=True, light_evidence=True)
detail["links"].update(
    body=f"/analysis-runs/{RUN}/requests/1/body?appid={APP}",
    evidence=f"/analysis-runs/{RUN}/requests/1/evidence?appid={APP}",
)
emit("request-detail", "RequestDetail", detail)
for section, items in [
    ("special_ranges", [dict(start="0", end="3")]),
    (
        "source_fields",
        [
            dict(
                json_pointer="/messages/0/content",
                characters="3",
                utf8_bytes="10",
                sha256=hashlib.sha256("中文🙂".encode()).hexdigest(),
            )
        ],
    ),
]:
    e = {
        **sample(D["EvidencePage"]["oneOf"][0]),
        "section": section,
        "items": items,
        "summary": detail["evidence_summary"],
        "limit": 256,
        "total": "1",
        "next_offset": None,
    }
    emit("evidence-" + section, "EvidencePage", e)
sig = sample(ref("Signal"))
sig.update(
    metric=rule["metric"],
    comparator="gt",
    threshold="90",
    observed_value="100",
    rule_id=rule["rule_id"],
    route="length_analysis",
)
sp = sample(ref("SignalsPage"))
sp.update(items=[sig], total="1", limit=50, next_offset=None)
emit("signals-normal", "SignalsPage", sp)
for case in json.loads((OUT / "examples/monitoring-view-v0.2/receipts.json").read_text())[
    "examples"
]:
    emit(
        "receipt-" + case["name"],
        "Receipt" if case["http_status"] == 200 else "Error",
        case["body"],
        case["http_status"],
        case["headers"],
    )
emit(
    "submission",
    "Submission",
    dict(file_ref="synthetic.csv", model_id=MOD, submission_key="synthetic-key-1"),
)
legacy = sample(ref("LegacyRunState"))
legacy.update(
    run_id=RUN,
    file_ref="synthetic.csv",
    model_id=MOD,
    status="queued",
    created_at=T,
    started_at=None,
    finished_at=None,
    settings=None,
    snapshot=None,
    result=None,
    error_code=None,
)
emit("submission-accepted", "LegacyRunState", legacy, 202, {"X-TokenScope-Instance-Id": U})
emit("run-state", "LegacyRunState", legacy)
lm = sample(ref("LegacyModelView"))
lm["settings"].update(
    model_id=MOD,
    revision=1,
    block_size=128,
    cp_world_size=1,
    mtp=True,
    prefix_cache_enabled=True,
    cache_mode="full_block",
    encoding_profile="default",
)
lm["capability"] = cap
emit("models-legacy", "LegacyModelsList", [lm])
for n, status in [("completed", "completed"), ("no-valid", "no_valid_rows")]:
    e = sample(ref("ResultPublishedEvent"))
    e.update(run_id=RUN, publish_seq="42", status=status)
    emit("event-" + n, "ResultPublishedEvent", e)
for status in ("failed", "interrupted"):
    e = sample(ref("RunTerminalEvent"))
    e.update(
        run_id="33333333-3333-4333-8333-000000000005",
        event_seq="43",
        status=status,
        error_code="WORKER_INTERRUPTED" if status == "interrupted" else "INVALID_CSV_HEADER",
    )
    emit("event-" + status, "RunTerminalEvent", e)
for reason in ("expired", "future_cursor", "instance_changed", "invalid_cursor"):
    e = sample(ref("ResetEvent"))
    e.update(reason=reason, catalog_url="/monitoring/catalog")
    emit("event-reset-" + reason, "ResetEvent", e)
errors = {
    404: [
        "MODEL_NOT_FOUND",
        "RUN_NOT_FOUND",
        "GROUP_NOT_FOUND",
        "REQUEST_NOT_FOUND",
        "SUBMISSION_NOT_FOUND",
    ],
    409: [
        "RESULT_NOT_READY",
        "CATALOG_REVISION_CHANGED",
        "RULES_REVISION_CHANGED",
        "REVISION_CONFLICT",
        "SUBMISSION_KEY_CONFLICT",
        "SERVICE_INSTANCE_CHANGED",
    ],
    422: [
        "INVALID_REQUEST",
        "INVALID_EXPORT_QUERY",
        "INVALID_PAGINATION",
        "INVALID_LENGTH_QUERY",
        "INVALID_BIN_WIDTH",
        "INVALID_SETTINGS",
        "EMPTY_UPDATE",
        "UNSUPPORTED_CACHE_MODE",
        "UNKNOWN_ENCODING_PROFILE",
    ],
    503: [
        "VIEW_INDEX_NOT_READY",
        "VIEW_ARTIFACT_UNAVAILABLE",
        "SSE_CAPACITY_EXCEEDED",
        "STORAGE_UNAVAILABLE",
    ],
}
errors[400] = ["INVALID_FILE_REF", "INVALID_SETTINGS"]
for status, codes in errors.items():
    for code in codes:
        emit(
            "error-" + str(status) + "-" + code.lower(),
            "Error",
            dict(
                error=dict(
                    code=code,
                    message="Synthetic protocol example; reload or correct input as documented.",
                )
            ),
            status,
        )
# Additional independent branches and empty states for consumer fixtures.
rr = copy.deepcopy(rule)
rr.update(metric="ideal_hit_rate", threshold=0.25, value_kind="ratio", route="prefix_analysis")
emit("rule-ratio", "Rule", rr)
rf = copy.deepcopy(rule)
rf.update(threshold=90.5, value_kind="number")
emit("rule-fractional-count-threshold", "Rule", rf)
for name, typ, source in [
    ("requests-empty", "RequestsPage", reqs),
    ("signals-empty", "SignalsPage", sp),
    ("rules-empty", "RulesPage", rp),
]:
    v = copy.deepcopy(source)
    v.update(items=[], total="0", next_offset=None)
    emit(name, typ, v)
(EX / "request-body.txt").write_bytes(raw.encode())
frames = []
for name, kind, seq in [
    ("event-completed", "result_published", "42"),
    ("event-failed", "run_terminal", "43"),
]:
    payload = json.loads((EX / (name + ".json")).read_text())
    frames.append(
        "id: "
        + U
        + ":"
        + seq
        + "\nevent: "
        + kind
        + "\ndata: "
        + json.dumps(payload, separators=(",", ":"))
        + "\n\n"
    )
(EX / "replay.sse").write_text("retry: 3000\n\n" + "".join(frames) + ": heartbeat\n\n")
reset = json.loads((EX / "event-reset-expired.json").read_text())
(EX / "reset.sse").write_text(
    "event: reset\ndata: " + json.dumps(reset, separators=(",", ":")) + "\n\n"
)
(EX / "cases.json").write_text(
    json.dumps(dict(synthetic=True, contract_version="1.0.0", cases=cases), indent=2) + "\n"
)


# Complete intended OpenAPI surface for frontend consumption. Legacy runtime file stays untouched.
def oasrefs(x):
    if isinstance(x, dict):
        return {
            k: (v.replace("#/$defs/", "#/components/schemas/") if k == "$ref" else oasrefs(v))
            for k, v in x.items()
        }
    if isinstance(x, list):
        return [oasrefs(v) for v in x]
    return x


P = {}


def param(n, s, required=False, where="query", default=None):
    q = dict(name=n, **{"in": where}, required=required, schema=oasrefs(s))
    if default is not None:
        q["schema"] = {**q["schema"], "default": default}
    return q


appid = [param("appid", ID, True)]
paging = [
    param("offset", COUNT, default="0"),
    param("limit", {"type": "integer", "minimum": 1, "maximum": 1000}, default=100),
]
guard = param("X-TokenScope-Instance-Id", UUID, False, "header")


def route(path, method, result, params=(), body=None, status="200", media="application/json"):
    pars = list(params)
    import re

    for name in re.findall(r"{([^}]+)}", path):
        pars.insert(
            0,
            param(
                name,
                MODEL if name == "model_id" else POS if name == "source_record_index" else ID,
                True,
                "path",
            ),
        )
    response = dict(description="Synthetic contract only; backend not yet implemented.")
    if result:
        response["content"] = {media: {"schema": oasrefs(ref(result))}}
    responses = {status: response}
    response["headers"] = {
        "X-TokenScope-Instance-Id": {"schema": UUID, "description": "Persistent instance identity"},
        "Cache-Control": {"schema": S, "description": "no-store except snapshot private,no-cache"},
    }
    for code in ("400", "404", "409", "422", "503"):
        responses[code] = dict(
            description="See Error registry and endpoint semantics.",
            content={"application/json": {"schema": oasrefs(ref("Error"))}},
        )
    op = dict(
        operationId=method + "_" + path.replace("/", "_").replace("{", "").replace("}", ""),
        parameters=pars,
        responses=responses,
    )
    if body:
        op["requestBody"] = dict(
            required=True, content={"application/json": {"schema": oasrefs(ref(body))}}
        )
    P.setdefault(path, {})[method] = op


route(
    "/monitoring/catalog",
    "get",
    "CatalogResponse",
    [param("appid", ID), param("model_id", MODEL), *paging, param("catalog_revision", COUNT)],
)
route(
    "/monitoring/runs",
    "get",
    "PublishedRunsResponse",
    [param("appid", ID), param("model_id", MODEL), *paging, param("catalog_revision", COUNT)],
)
route(
    "/monitoring/events",
    "get",
    None,
    [param("after", ID), param("Last-Event-ID", ID, False, "header")],
)
P["/monitoring/events"]["get"]["responses"]["200"]["content"] = {
    "text/event-stream": {
        "schema": {"type": "string"},
        "x-event-schemas": {
            k: oasrefs(ref(v))
            for k, v in [
                ("result_published", "ResultPublishedEvent"),
                ("run_terminal", "RunTerminalEvent"),
                ("reset", "ResetEvent"),
            ]
        },
    }
}
route(
    "/analysis-runs/{run_id}/view-snapshot",
    "get",
    "ViewSnapshot",
    [*appid, param("If-None-Match", S, False, "header")],
)
P["/analysis-runs/{run_id}/view-snapshot"]["get"]["responses"]["304"] = {
    "description": "ETag match; no response body."
}
filters = [
    param("metric", enum(*LENGTHS), default="prompt_tokens"),
    param("lower", COUNT, default="0"),
    param("upper", COUNT),
    param("hash_id", ID),
    param("hash_match", enum("exact", "prefix"), default="exact"),
    param("sort_by", D["RequestSort"]["properties"]["by"], default="prompt_tokens"),
    param("sort_order", enum("asc", "desc"), default="desc"),
]
route("/analysis-runs/{run_id}/requests", "get", "RequestsPage", [*appid, *filters, *paging])
route("/analysis-runs/{run_id}/requests/{source_record_index}", "get", "RequestDetail", appid)
route("/analysis-runs/{run_id}/requests/{source_record_index}/body", "get", None, appid)
P["/analysis-runs/{run_id}/requests/{source_record_index}/body"]["get"]["responses"]["200"][
    "content"
] = {"text/plain": {"schema": {"type": "string"}}}
route(
    "/analysis-runs/{run_id}/requests/{source_record_index}/evidence",
    "get",
    "EvidencePage",
    [
        *appid,
        param("section", enum("special_ranges", "source_fields"), default="special_ranges"),
        *paging,
    ],
)
route("/analysis-runs/{run_id}/view-signals", "get", "SignalsPage", [*appid, *paging])
route("/monitoring/models/{model_id}/settings", "get", "ModelSettingsResponse")
route(
    "/monitoring/models/{model_id}/settings", "put", "ModelSettingsResponse", body="SettingsUpdate"
)
route(
    "/monitoring/threshold-rules",
    "get",
    "RulesPage",
    [param("appid", ID), param("model_id", MODEL), *paging, param("rules_revision", COUNT)],
)
route("/monitoring/threshold-rules", "put", "RuleResponse", body="RuleUpdate")
route("/analysis-runs", "post", "LegacyRunState", [guard], body="Submission", status="202")
route("/analysis-runs/{run_id}", "get", "LegacyRunState", [guard])
route("/analysis-submissions/{submission_key}", "get", "Receipt", [guard])
route("/models", "get", "LegacyModelsList")

route(
    "/analysis-runs/{run_id}/requests/export",
    "get",
    None,
    [*appid, *filters, param("format", enum("ndjson", "csv"), True)],
)
ex = P["/analysis-runs/{run_id}/requests/export"]["get"]["responses"]["200"]
ex["content"] = {m: {"schema": {"type": "string"}} for m in ("application/x-ndjson", "text/csv")}
ex["headers"] = {
    n: dict(description=desc, schema={"type": "string"})
    for n, desc in {
        "X-Export-Schema-Version": "Always 1",
        "X-Export-Row-Count": "Exact decimal request row count",
        "X-TokenScope-Instance-Id": "Persistent instance UUID",
        "X-Export-Run-Id": "Fixed run UUID",
        "X-CSV-Text-Escaping": "apostrophe for CSV",
        "Content-Disposition": "Safe ASCII internal file name",
        "Cache-Control": "no-store",
    }.items()
}
ex["x-record-schemas"] = {
    n: oasrefs(ref(n)) for n in ("ExportMetadata", "ExportRequest", "ExportSummary")
}
snapop = P["/analysis-runs/{run_id}/view-snapshot"]["get"]
snapop["responses"]["200"]["headers"]["ETag"] = {
    "schema": S,
    "description": "Quoted SHA256 of exact canonical UTF8 response bytes",
}
snapop["responses"]["304"]["headers"] = copy.deepcopy(snapop["responses"]["200"]["headers"])
# Defaults specific to requests/evidence.
for path, item in P.items():
    for op in item.values():
        for par in op["parameters"]:
            if par["name"] == "limit":
                par["schema"]["default"] = (
                    256
                    if path.endswith("/evidence")
                    else 50
                    if path.endswith(("/requests", "/view-signals"))
                    else 100
                )
openapi = dict(
    openapi="3.1.0",
    info=dict(
        title="TokenScope Monitoring View S0 Design Contract",
        version="1.0.0",
        description="Frozen intended interface; not the running dev5 OpenAPI. See S0_CONTRACT.md.",
    ),
    servers=[dict(url="/")],
    paths=P,
    components=dict(schemas=oasrefs(D)),
    **{"x-runtime-implemented": False},
)
(OUT / "schemas/monitoring-view-v1.design.openapi.json").write_text(
    json.dumps(openapi, ensure_ascii=False, indent=2) + "\n"
)
# Field dictionary generated from the same schema, avoiding parallel hand-maintained lists.
lines = [
    "# S0完整字段字典（contract 1.0.0）",
    "",
    "从monitoring-view-v1.schema.json生成。required列为必填；nullable显式列出。嵌套字段沿引用继续；对象默认拒绝额外字段。",
    "Legacy类型原样复制现有运行OpenAPI；其中snapshot/result为刻意不透明JSON，前端仅消费run_id/status，不将其当新展示数据。",
    "",
]


def describe(s):
    if "$ref" in s:
        return s["$ref"].rsplit("/", 1)[-1]
    if "enum" in s:
        return "enum " + "/".join(str(v) for v in s["enum"])
    if "const" in s:
        return "const " + json.dumps(s["const"], ensure_ascii=False)
    if "anyOf" in s:
        return " OR ".join(describe(v) for v in s["anyOf"])
    if "oneOf" in s:
        return "oneOf(" + ", ".join(describe(v) for v in s["oneOf"]) + ")"
    if s.get("type") == "array":
        return "array<" + describe(s["items"]) + ">"
    if s.get("type") == "object":
        return (
            "object {"
            + "; ".join(k + ": " + describe(v) for k, v in s.get("properties", {}).items())
            + "}; required="
            + ",".join(s.get("required", []))
        )
    return (
        s.get("type", "JSON")
        + (" / " + s["pattern"] if "pattern" in s else "")
        + " "
        + " ".join(
            k + "=" + str(s[k])
            for k in (
                "format",
                "minimum",
                "maximum",
                "minLength",
                "maxLength",
                "minItems",
                "uniqueItems",
            )
            if k in s
        )
    )


for name, definition in D.items():
    lines += ["## " + name, ""]
    variants = definition.get("oneOf", [definition])
    for i, v in enumerate(variants):
        if len(variants) > 1:
            lines += ["分支 " + str(i + 1), ""]
        if "properties" not in v:
            lines += [describe(v), ""]
            continue
        lines += ["| 字段 | 必填 | 类型/约束 |", "| --- | --- | --- |"]
        for key, s in v["properties"].items():
            lines.append(
                "| "
                + key
                + " | "
                + ("是" if key in v.get("required", []) else "否")
                + " | "
                + describe(s).replace("|", "&#124;")
                + " |"
            )
        lines.append("")
(OUT / "MONITORING_VIEW_V1_FIELDS.md").write_text("\n".join(lines) + "\n")
print(
    json.dumps(
        dict(
            definitions=len(D),
            examples=len(cases),
            paths=len(P),
            operations=sum(len(x) for x in P.values()),
        )
    )
)
