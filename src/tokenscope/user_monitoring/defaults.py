"""Persisted user-provided model defaults and explicit automatic TTFT evaluation."""

import hashlib
import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import UTC, datetime
from uuid import uuid4

from tokenscope.errors import TokenScopeError
from tokenscope.user_monitoring.contracts import BatchScenario, EvaluationRequest
from tokenscope.user_monitoring.discovery import Discovery
from tokenscope.user_monitoring.discovery_contracts import (
    AutoEvaluation,
    AutoEvaluationRequest,
    DefaultConfig,
    DefaultPage,
    DefaultQuery,
    DefaultUpdate,
)
from tokenscope.user_monitoring.estimator import calculate
from tokenscope.user_monitoring.service import UserRunService
from tokenscope.user_monitoring.storage import canonical

SEEDS = (
    ("Qwen3.6-27B", "Qwen-V3.6-27B", "1"),
    ("GLM-5.2", "GLM-V5.2", "2.7"),
    ("DeepSeek-V4-Flash-0731", "DeepSeek-V4-Flash", "2.6"),
)


class DefaultEstimator:
    def __init__(self, user: UserRunService) -> None:
        self.user = user
        self.path = user.root / "ttft_defaults.sqlite3"
        # Called during router/service construction, never from a business GET.
        with sqlite3.connect(self.path) as db:
            if db.execute("PRAGMA user_version").fetchone()[0] not in (0, 1):
                raise TokenScopeError("STORAGE_UNAVAILABLE", "Unknown default store version", 503)
            db.executescript("""
                CREATE TABLE IF NOT EXISTS defaults (
                    model_id TEXT, common_name TEXT, revision INTEGER, payload TEXT NOT NULL,
                    PRIMARY KEY(model_id,common_name,revision));
                CREATE TABLE IF NOT EXISTS updates (
                    submission_key TEXT PRIMARY KEY, intent TEXT NOT NULL, payload TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS evaluations (
                    id TEXT PRIMARY KEY, submission_key TEXT UNIQUE NOT NULL,
                    intent TEXT NOT NULL, payload TEXT NOT NULL);
                PRAGMA user_version=1;
            """)
            db.execute("BEGIN IMMEDIATE")
            for model_id, common_name, seconds in SEEDS:
                try:
                    user.validate_name(common_name, model_id)
                except TokenScopeError:
                    # Explicitly absent aliases must not gain another model's parameters.
                    continue
                if db.execute(
                    "SELECT 1 FROM defaults WHERE model_id=? AND common_name=?",
                    (model_id, common_name),
                ).fetchone():
                    continue
                value = DefaultConfig.model_validate(
                    dict(
                        common_name=common_name,
                        model_id=model_id,
                        revision="1",
                        chunk_tokens="8192",
                        chunk_seconds=seconds,
                        tau_reference_chunk_tokens="8192",
                        source_description="User-provided 2026-11-03 via HV2-R1-USER; "
                        "K=8192; reference assumptions, not measured calibration.",
                        recorded_at=datetime.now(UTC).isoformat(),
                    )
                )
                db.execute(
                    "INSERT INTO defaults VALUES(?,?,1,?)",
                    (model_id, common_name, value.model_dump_json()),
                )

    @contextmanager
    def connect(self, *, readonly: bool = True) -> Iterator[sqlite3.Connection]:
        db = sqlite3.connect(
            self.path.as_uri() + ("?mode=ro" if readonly else "?mode=rw"), uri=True, timeout=30
        )
        db.row_factory = sqlite3.Row
        try:
            with db:
                yield db
        finally:
            db.close()

    def get(self, query: DefaultQuery) -> DefaultPage:
        with self.connect() as db:
            if query.revision is not None:
                rows = db.execute(
                    "SELECT payload FROM defaults "
                    "WHERE model_id=? AND common_name=? AND revision=?",
                    (query.model_id, query.common_name, int(query.revision)),
                ).fetchall()
                if not rows:
                    raise TokenScopeError(
                        "DEFAULT_REVISION_NOT_FOUND", "Unknown default revision", 404
                    )
            else:
                rows = db.execute(
                    "SELECT d.payload FROM defaults d JOIN (SELECT model_id,common_name,"
                    "max(revision) revision FROM defaults GROUP BY model_id,common_name) latest "
                    "USING(model_id,common_name,revision) "
                    "WHERE (? IS NULL OR d.model_id=?) AND (? IS NULL OR d.common_name=?) "
                    "ORDER BY d.model_id,d.common_name",
                    (query.model_id, query.model_id, query.common_name, query.common_name),
                ).fetchall()
        return DefaultPage(
            service_instance_id=self.user.service_id,
            configs=[DefaultConfig.model_validate_json(row[0]) for row in rows],
        )

    def update(self, request: DefaultUpdate) -> DefaultConfig:
        self.user.validate_name(request.common_name, request.model_id)
        intent = canonical(request.model_dump(mode="json"))
        with self.connect(readonly=False) as db:
            db.execute("BEGIN IMMEDIATE")
            prior = db.execute(
                "SELECT intent,payload FROM updates WHERE submission_key=?",
                (request.submission_key,),
            ).fetchone()
            if prior:
                if prior["intent"] != intent:
                    raise TokenScopeError("SUBMISSION_KEY_CONFLICT", "Default update differs", 409)
                return DefaultConfig.model_validate_json(prior["payload"])
            latest = db.execute(
                "SELECT coalesce(max(revision),0) FROM defaults WHERE model_id=? AND common_name=?",
                (request.model_id, request.common_name),
            ).fetchone()[0]
            if latest != int(request.expected_revision):
                raise TokenScopeError("DEFAULT_REVISION_CONFLICT", "Default revision changed", 409)
            value = DefaultConfig(
                common_name=request.common_name,
                model_id=request.model_id,
                revision=str(latest + 1),
                chunk_tokens=request.chunk_tokens,
                chunk_seconds=request.chunk_seconds,
                tau_reference_chunk_tokens=request.tau_reference_chunk_tokens,
                source_description=request.source_description,
                recorded_at=datetime.now(UTC).isoformat(),
            )
            payload = value.model_dump_json()
            db.execute(
                "INSERT INTO defaults VALUES(?,?,?,?)",
                (request.model_id, request.common_name, latest + 1, payload),
            )
            db.execute(
                "INSERT INTO updates VALUES(?,?,?)", (request.submission_key, intent, payload)
            )
        return value

    def evaluate(self, request: AutoEvaluationRequest) -> AutoEvaluation:
        intent = canonical(request.model_dump(mode="json"))
        with self.connect() as db:
            prior = db.execute(
                "SELECT intent,payload FROM evaluations WHERE submission_key=?",
                (request.submission_key,),
            ).fetchone()
        if prior:
            if prior["intent"] != intent:
                raise TokenScopeError("SUBMISSION_KEY_CONFLICT", "Evaluation input differs", 409)
            return AutoEvaluation.model_validate_json(prior["payload"])
        entry = Discovery(self.user).entry(
            request.user_run_id, request.appid, request.index_revision
        )
        source = entry.source
        options = self.get(
            DefaultQuery(
                model_id=source.model_id,
                common_name=source.common_name,
                revision=request.default_revision,
            )
        ).configs
        if not options or options[0].chunk_seconds is None:
            raise TokenScopeError(
                "TTFT_DEFAULT_NOT_CONFIGURED",
                "Model chunk_seconds awaits explicit configuration",
                409,
            )
        config = options[0]
        assert config.chunk_seconds is not None
        chunk_tokens = request.chunk_tokens or config.chunk_tokens
        key = hashlib.sha256(
            canonical([source.model_id, source.common_name, config.revision, chunk_tokens]).encode()
        ).hexdigest()
        scenario = BatchScenario(
            timing_model="batch_reference_total_noncompute_v1",
            scenario_id="auto-default-" + key,
            revision=config.revision,
            model_id=source.model_id,
            common_name=source.common_name,
            deployment="Selected Trace model; user-provided reference configuration",
            source="user_assumption",
            source_description=config.source_description,
            chunk_tokens=chunk_tokens,
            chunk_seconds=config.chunk_seconds,
        )
        calculated = calculate(
            EvaluationRequest(
                submission_key=request.submission_key,
                user_run_id=request.user_run_id,
                appid=request.appid,
                scenario_id=scenario.scenario_id,
                scenario_revision=scenario.revision,
                target_seconds=request.target_seconds,
                waiting_seconds=request.waiting_seconds,
                comparator=request.comparator,
            ),
            scenario,
            count=int(entry.request_count),
            prompt_p90=int(entry.prompt_p90) if entry.prompt_p90 is not None else None,
            service_id=self.user.service_id,
            evaluation_id="ua-" + uuid4().hex,
        )
        if chunk_tokens != config.tau_reference_chunk_tokens:
            calculated.limitations.append(
                "K differs from the supplied tau reference K; tau is unchanged, "
                "not proportionally scaled or calibrated for this override."
            )
        result = AutoEvaluation(
            evaluation_id=calculated.evaluation_id,
            service_instance_id=self.user.service_id,
            request=request,
            source=source,
            defaults=config,
            chunk_tokens_origin="request_override"
            if request.chunk_tokens is not None
            else "model_default",
            evaluation=calculated,
        )
        with self.connect(readonly=False) as db:
            db.execute("BEGIN IMMEDIATE")
            prior = db.execute(
                "SELECT intent,payload FROM evaluations WHERE submission_key=?",
                (request.submission_key,),
            ).fetchone()
            if prior:
                if prior["intent"] != intent:
                    raise TokenScopeError(
                        "SUBMISSION_KEY_CONFLICT", "Evaluation input differs", 409
                    )
                return AutoEvaluation.model_validate_json(prior["payload"])
            db.execute(
                "INSERT INTO evaluations VALUES(?,?,?,?)",
                (result.evaluation_id, request.submission_key, intent, result.model_dump_json()),
            )
        return result

    def evaluation(self, evaluation_id: str) -> AutoEvaluation:
        with self.connect() as db:
            row = db.execute(
                "SELECT payload FROM evaluations WHERE id=?", (evaluation_id,)
            ).fetchone()
        if row is None:
            raise TokenScopeError("RESOURCE_NOT_FOUND", "Unknown automatic evaluation", 404)
        return AutoEvaluation.model_validate_json(row[0])
