"""Original-identity checked bridge; no diagnostic tokenizer implementation."""

import json

from tokenscope import ALGORITHM_VERSION
from tokenscope.analysis_common.contracts import RequestView
from tokenscope.analysis_common.source import ResolvedSource
from tokenscope.domain import ModelSettings
from tokenscope.encoding.batch import EncodedRequest, EncodingBatchService, EncodingFailure
from tokenscope.encoding.models import EncodingProfile, ModelEncoder
from tokenscope.encoding.shards import TokenSlice
from tokenscope.errors import TokenScopeError


class EncodingContext:
    def __init__(self, source: ResolvedSource) -> None:
        self.source = source
        identity = source.scope.source
        if identity.algorithm_version != ALGORITHM_VERSION:
            raise TokenScopeError("ALGORITHM_VERSION_MISMATCH", "Unsupported source algorithm", 409)
        settings = ModelSettings.model_validate_json(identity.settings_json)
        assets = source.service.assets.load(settings.model_id)
        if assets.identity != identity.asset_identity:
            raise TokenScopeError("ASSET_IDENTITY_MISMATCH", "Original assets unavailable", 409)
        profile = EncodingProfile.model_validate_json(identity.profile_json)
        self.batch = EncodingBatchService(ModelEncoder(assets, settings, profile))
        if self.batch.encoder.identity != identity.encoder_identity:
            raise TokenScopeError("ENCODER_IDENTITY_MISMATCH", "Original encoder differs", 409)

    def encode(self, request: RequestView, raw: str) -> EncodedRequest:
        if request.scope_id != self.source.scope.scope_id:
            raise TokenScopeError("REQUEST_NOT_IN_SCOPE", "Request is outside scope", 404)
        result = self.batch.encode_batch([raw])[0]
        if isinstance(result, EncodingFailure):
            raise TokenScopeError(result.code, "Variant encoding failed", 422)
        if result.light_evidence["effective_options"] != json.loads(request.effective_options_json):
            raise TokenScopeError(
                "ENCODING_OPTIONS_CHANGED", "Variant changed effective options", 409
            )
        return result

    def verify_baseline(self, request: RequestView) -> EncodedRequest:
        result = self.encode(request, request.raw_body)
        if request.token_slice_json is None:
            raise TokenScopeError("TOKEN_SLICE_UNAVAILABLE", "Original IDs unavailable", 503)
        reference = TokenSlice.model_validate_json(request.token_slice_json)
        if (
            result.prompt_digest != reference.sha256
            or result.prompt_tokens != request.baseline_metrics.p
            or result.json_tokens != request.baseline_metrics.j
        ):
            raise TokenScopeError("BASELINE_MISMATCH", "Original encoding did not reproduce", 409)
        if result.prompt_ids != self.source.read_ids(request):
            raise TokenScopeError("BASELINE_MISMATCH", "Original input IDs differ", 409)
        return result
