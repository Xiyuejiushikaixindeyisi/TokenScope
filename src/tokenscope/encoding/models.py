"""Model adapters share verified tokenization assets and explicitly defined modes."""

import copy
import hashlib
import json
import os
import re
from dataclasses import dataclass
from typing import Any

from pydantic import Field

from tokenscope.domain import ModelSettings, PositiveInt, StrictModel
from tokenscope.encoding.assets import VerifiedAssets
from tokenscope.errors import TokenScopeError
from tokenscope.ingestion.csv_reader import InvalidRow, validate_request


class EncodingProfile(StrictModel):
    name: str = "default"
    cpu_budget: PositiveInt = 8
    # None means the source's native default for Qwen/GLM; DeepSeek must be explicit.
    default_thinking: bool | None = None
    template_options: dict[str, Any] = Field(default_factory=dict)


@dataclass(frozen=True)
class RenderedInput:
    text: str
    special_ranges: tuple[tuple[int, int], ...]
    special_ranges_semantics: str
    source_fields: tuple[dict[str, Any], ...]
    effective_options: dict[str, Any]


def source_fields(request: dict[str, Any]) -> tuple[dict[str, Any], ...]:
    """Small source references, not a fabricated attribution of every rendered token."""
    fields: list[dict[str, Any]] = []
    stack: list[tuple[str, Any]] = [("", request)]
    while stack:
        path, value = stack.pop()
        if isinstance(value, str):
            fields.append(
                {
                    "json_pointer": path,
                    "characters": len(value),
                    "utf8_bytes": len(value.encode()),
                    "sha256": hashlib.sha256(value.encode()).hexdigest(),
                }
            )
        elif isinstance(value, dict):
            stack.extend(
                (path + "/" + key.replace("~", "~0").replace("/", "~1"), child)
                for key, child in reversed(list(value.items()))
            )
        elif isinstance(value, list):
            stack.extend(
                (path + "/" + str(index), value[index]) for index in reversed(range(len(value)))
            )
    return tuple(fields)


class ModelEncoder:
    def __init__(
        self,
        assets: VerifiedAssets,
        settings: ModelSettings,
        profile: EncodingProfile | None = None,
    ) -> None:
        self.profile = profile.model_copy(deep=True) if profile else EncodingProfile()
        self.assets = assets
        self.settings = settings
        if assets.spec.model_id != settings.model_id:
            raise TokenScopeError("ASSET_MODEL_MISMATCH", "Assets do not match the selected model")
        if self.profile.name != settings.encoding_profile:
            raise TokenScopeError("UNKNOWN_ENCODING_PROFILE", "Encoding profile is unavailable")
        # One Rust pool, no outer worker pool. Set before the first encoding call.
        current_budget = os.environ.get("RAYON_NUM_THREADS")
        if current_budget and current_budget != str(self.profile.cpu_budget):
            raise TokenScopeError("CPU_BUDGET_CONFLICT", "Run encoding with one process CPU budget")
        os.environ["RAYON_NUM_THREADS"] = str(self.profile.cpu_budget)
        os.environ["TOKENIZERS_PARALLELISM"] = "true"
        from tokenizers import AddedToken, Tokenizer

        self.full: Any = Tokenizer.from_str(assets.contents["tokenizer.json"].decode())
        self.full.no_truncation()
        self.full.no_padding()
        self.hf: Any = None
        self.recipe: Any = None
        if settings.model_id != "DeepSeek-V4-Flash-0731":
            from transformers import PreTrainedTokenizerFast

            config = json.loads(assets.contents["tokenizer_config.json"])
            config.pop("tokenizer_class", None)
            config.pop("chat_template", None)
            if "added_tokens_decoder" in config:
                config["added_tokens_decoder"] = {
                    int(index): AddedToken(**{k: v for k, v in value.items() if k != "__type"})
                    for index, value in config["added_tokens_decoder"].items()
                }
            # Load the exact tokenizer bytes; no Hub access or model weights.
            hf_constructor: Any = PreTrainedTokenizerFast
            self.hf = hf_constructor(
                tokenizer_object=self.full,
                chat_template=assets.contents["chat_template.jinja"].decode(),
                **config,
            )
            self.full = self.hf.backend_tokenizer
            self.full.no_truncation()
            self.full.no_padding()
        else:
            import deepseek_recipe as recipe

            self.recipe = recipe
            self.recipe_encoder = recipe.DeepseekV4Encoding()
        plain = json.loads(self.full.to_str())
        plain["added_tokens"] = []
        plain["post_processor"] = None
        plain["truncation"] = None
        plain["padding"] = None
        self.plain: Any = Tokenizer.from_str(json.dumps(plain, ensure_ascii=False))
        added = self.full.get_added_tokens_decoder()
        self.added_ids: dict[str, int] = {token.content: index for index, token in added.items()}
        self.special_pattern = (
            re.compile(
                "|".join(re.escape(s) for s in sorted(self.added_ids, key=len, reverse=True))
            )
            if self.added_ids
            else None
        )
        identity = {
            "asset_identity": assets.identity,
            "profile": self.profile.model_dump(exclude={"cpu_budget"}),
            "model": settings.model_id,
            "adapter": "model-encoding-v1",
        }
        self.identity = hashlib.sha256(json.dumps(identity, sort_keys=True).encode()).hexdigest()

    def prepare(self, raw: str) -> dict[str, Any]:
        validate_request(raw, self.settings)
        request: dict[str, Any] = json.loads(raw)
        return request

    def options(self, request: dict[str, Any]) -> dict[str, Any]:
        kwargs = request.get("chat_template_kwargs", {})
        if not isinstance(kwargs, dict):
            raise InvalidRow("INVALID_TEMPLATE_OPTIONS", "request_input.chat_template_kwargs")
        options = copy.deepcopy(self.profile.template_options)
        if self.profile.default_thinking is not None:
            options["enable_thinking"] = self.profile.default_thinking
        for name in (
            "enable_thinking",
            "thinking",
            "reasoning_effort",
            "clear_thinking",
            "drop_thinking",
        ):
            if name in request:
                options[name] = request[name]
        options.update(kwargs)
        if "enable_thinking" in options and not isinstance(options["enable_thinking"], bool):
            raise InvalidRow("INVALID_TEMPLATE_OPTIONS", "request_input.enable_thinking")
        if options.get("continue_final_message"):
            raise InvalidRow("UNSUPPORTED_TEMPLATE_MODE", "request_input.continue_final_message")
        return options

    def render(self, raw: str) -> RenderedInput:
        from jinja2 import TemplateError

        request = self.prepare(raw)
        options = self.options(request)
        if self.recipe is not None:
            return self.render_deepseek(request, options)
        messages = copy.deepcopy(request["messages"])
        for message in messages:
            # HF chat utilities expect structured arguments before applying these templates.
            for call in message.get("tool_calls", []):
                try:
                    call["function"]["arguments"] = json.loads(call["function"]["arguments"])
                except (ValueError, TypeError) as exc:
                    raise InvalidRow(
                        "INVALID_TOOL_ARGUMENT_JSON", "request_input.messages.tool_calls"
                    ) from exc
            if message.get("content") is None:
                message["content"] = ""
            if isinstance(message.get("content"), list):
                for part in message["content"]:
                    if part.get("type") == "input_text":
                        part["type"] = "text"
        options.setdefault("add_generation_prompt", True)
        try:
            rendered = self.hf.apply_chat_template(
                messages, tools=request.get("tools"), tokenize=False, **options
            )
        except (ValueError, TypeError, KeyError, TemplateError) as exc:
            raise InvalidRow("TEMPLATE_RENDER_FAILED", "request_input") from exc
        if not isinstance(rendered, str):
            raise TokenScopeError("ENCODER_INTERNAL_ERROR", "Template did not return text", 500)
        ranges = (
            tuple((match.start(), match.end()) for match in self.special_pattern.finditer(rendered))
            if self.special_pattern
            else ()
        )
        return RenderedInput(
            rendered,
            ranges,
            "recognized_added_token_spelling_origin_unassigned",
            source_fields(request),
            options,
        )

    def render_deepseek(self, request: dict[str, Any], options: dict[str, Any]) -> RenderedInput:
        supported = {"thinking", "enable_thinking", "reasoning_effort", "add_generation_prompt"}
        if options.keys() - supported or options.get("add_generation_prompt") is False:
            raise InvalidRow("UNSUPPORTED_TEMPLATE_MODE", "request_input.chat_template_kwargs")
        thinking = options.get(
            "thinking", options.get("enable_thinking", self.profile.default_thinking)
        )
        if thinking is None:
            raise TokenScopeError(
                "ENCODING_DEFAULT_UNRESOLVED", "DeepSeek thinking default needs confirmation", 503
            )
        recipe = self.recipe
        body = copy.deepcopy(request)
        body.setdefault("model", self.settings.model_id)
        # Explicit template selection takes precedence over the profile default.
        if isinstance(thinking, bool):
            body["thinking"] = {"type": "enabled" if thinking else "disabled"}
        elif isinstance(thinking, dict):
            body["thinking"] = thinking
        else:
            raise InvalidRow("INVALID_TEMPLATE_OPTIONS", "request_input.thinking")
        if "reasoning_effort" in options:
            body["reasoning_effort"] = options["reasoning_effort"]
        for key in ("chat_template_kwargs", "enable_thinking", "clear_thinking", "drop_thinking"):
            body.pop(key, None)
        # No implicit fallback is used: the body already carries an explicit resolved mode.
        conversion = recipe.ConversionOptions(default_thinking_mode=False)
        conversion = conversion.with_model_versions_by_name(
            {
                name: recipe.ModelVersion.DeepseekV4Pro
                for name in (self.settings.model_id, *self.settings.model_aliases)
            }
        )
        try:
            conversation = recipe.ChatCompletionRequest(body).convert(conversion).conversation
            rendered = self.recipe_encoder.render_conversation(conversation)
        except (ValueError, RuntimeError, recipe.ConversionError) as exc:
            raise InvalidRow("RECIPE_CONVERSION_FAILED", "request_input") from exc
        if rendered.image_sources:
            raise InvalidRow("NON_TEXT_CONTENT", "request_input.messages")
        return RenderedInput(
            rendered.prompt,
            tuple(rendered.special_ranges),
            "recipe_explicit_control_token",
            source_fields(request),
            options,
        )
