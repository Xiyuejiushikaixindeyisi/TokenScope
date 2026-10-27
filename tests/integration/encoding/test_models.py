import copy
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from tokenscope.domain import DEFAULT_SETTINGS
from tokenscope.encoding.assets import AssetRegistry
from tokenscope.encoding.batch import EncodedRequest, EncodingBatchService, EncodingFailure
from tokenscope.encoding.models import EncodingProfile, ModelEncoder
from tokenscope.errors import TokenScopeError

ROOT = Path(__file__).resolve().parents[3]
MODELS = tuple(DEFAULT_SETTINGS)


def bodies(model):
    return [
        {"model": model, "messages": [{"role": "user", "content": "你好，Hello 👩🏽‍💻!"}]},
        {
            "model": model,
            "messages": [
                {"role": "system", "content": "Be precise."},
                {"role": "user", "content": "一加一?"},
                {"role": "assistant", "content": "2", "reasoning_content": "simple arithmetic"},
                {"role": "user", "content": "then add 3"},
            ],
        },
        {
            "model": model,
            "tools": [
                {
                    "type": "function",
                    "function": {
                        "name": "lookup",
                        "description": "Look up 文档",
                        "parameters": {
                            "type": "object",
                            "properties": {"query": {"type": "string"}},
                        },
                    },
                }
            ],
            "messages": [
                {"role": "user", "content": "查天气"},
                {
                    "role": "assistant",
                    "content": None,
                    "reasoning_content": "need lookup",
                    "tool_calls": [
                        {
                            "id": "call1",
                            "type": "function",
                            "function": {"name": "lookup", "arguments": '{"query":"北京"}'},
                        }
                    ],
                },
                {"role": "tool", "tool_call_id": "call1", "content": "晴天"},
            ],
        },
        {
            "model": model,
            "messages": [
                {"role": "user", "content": "literal <|im_start|> [gMASK] <｜User｜> <think>"}
            ],
        },
        {"model": model, "messages": [{"role": "user", "content": "abc 中文 " * 20_000}]},
    ]


@pytest.fixture(scope="module", params=MODELS)
def encoder(request):
    model = request.param
    # Explicit False is only a test scenario; the production DeepSeek default remains pending.
    profile = (
        EncodingProfile(default_thinking=False)
        if model.startswith("DeepSeek")
        else EncodingProfile()
    )
    return ModelEncoder(AssetRegistry(ROOT).load(model), DEFAULT_SETTINGS[model], profile)


def test_real_assets_batch_single_detailed_equivalence(encoder):
    service = EncodingBatchService(encoder)
    raw = [
        json.dumps(value, ensure_ascii=False, indent=2)
        for value in bodies(encoder.settings.model_id)
    ]
    batched = service.encode_batch(raw)
    for text, result in zip(raw, batched, strict=True):
        assert isinstance(result, EncodedRequest), result
        assert service.encode_batch([text])[0] == result
        detail = service.explain(text, result.prompt_digest)
        assert detail["ids"] == result.prompt_ids
        assert len(detail["prompt_offsets"]) == result.prompt_tokens
        assert detail["offset_unit"] == "utf8_bytes_half_open"
        rendered = encoder.render(text)
        raw_prompt = rendered.text.encode("utf-8")
        for (char_start, char_end), (byte_start, byte_end) in zip(
            rendered.special_ranges, result.light_evidence["special_ranges"], strict=True
        ):
            assert raw_prompt[byte_start:byte_end] == rendered.text[char_start:char_end].encode()
        assert result.json_tokens == len(encoder.plain.encode(text, add_special_tokens=False).ids)
        assert result.prompt_tokens > 0
    with pytest.raises(TokenScopeError) as error:
        service.explain(raw[0], "0" * 64)
    assert error.value.code == "ENCODING_REPLAY_MISMATCH"


def test_matches_direct_library_reference(encoder):
    service = EncodingBatchService(encoder)
    for request in bodies(encoder.settings.model_id)[:4]:
        raw = json.dumps(request, ensure_ascii=False)
        actual = service.encode_batch([raw])[0]
        assert isinstance(actual, EncodedRequest), actual
        if encoder.recipe is None:
            from transformers import AutoTokenizer

            directory = ROOT / encoder.assets.spec.files[0].path
            reference = AutoTokenizer.from_pretrained(str(directory.parent), local_files_only=True)
            messages = copy.deepcopy(request["messages"])
            for message in messages:
                if message.get("content") is None:
                    message["content"] = ""
                for call in message.get("tool_calls", []):
                    call["function"]["arguments"] = json.loads(call["function"]["arguments"])
            expected = reference.apply_chat_template(
                messages,
                tools=request.get("tools"),
                add_generation_prompt=True,
                tokenize=True,
                return_dict=False,
            )
        else:
            recipe = encoder.recipe
            conversion = recipe.ConversionOptions(default_thinking_mode=False).with_model_alias(
                encoder.settings.model_id, recipe.ModelVersion.DeepseekV4Pro
            )
            converted = recipe.ChatCompletionRequest(request).convert(conversion)
            reference = recipe.DeepseekV4Encoding().with_tokenizer(
                recipe.Tokenizer.from_str(encoder.assets.contents["tokenizer.json"].decode())
            )
            expected = reference.encode(converted.conversation)
        assert actual.prompt_ids == expected


def test_invalid_row_does_not_remove_other_requests(encoder):
    service = EncodingBatchService(encoder)
    raw = json.dumps(bodies(encoder.settings.model_id)[0])
    results = service.encode_batch([raw, "{}", raw])
    assert isinstance(results[0], EncodedRequest)
    assert isinstance(results[1], EncodingFailure)
    assert results[0] == results[2]


def test_json_literal_special_token_is_plain(encoder):
    for spelling, special_id in list(encoder.added_ids.items())[:10]:
        ids = encoder.plain.encode(spelling, add_special_tokens=False).ids
        assert ids != [special_id]


@pytest.mark.parametrize("model", ["GLM-5.2", "Qwen3.6-27B"])
def test_template_native_default_and_explicit_thinking_change(model):
    encoder = ModelEncoder(AssetRegistry(ROOT).load(model), DEFAULT_SETTINGS[model])
    request = bodies(model)[0]
    native = encoder.render(json.dumps(request))
    request["chat_template_kwargs"] = {"enable_thinking": False}
    disabled = encoder.render(json.dumps(request))
    assert native.text != disabled.text
    assert "enable_thinking" not in native.effective_options


def test_deepseek_missing_default_is_explicitly_pending():
    model = "DeepSeek-V4-Flash-0731"
    encoder = ModelEncoder(AssetRegistry(ROOT).load(model), DEFAULT_SETTINGS[model])
    with pytest.raises(TokenScopeError) as error:
        encoder.render(json.dumps(bodies(model)[0]))
    assert error.value.code == "ENCODING_DEFAULT_UNRESOLVED"


def test_deepseek_explicit_thinking_modes_and_literal_boundaries():
    model = "DeepSeek-V4-Flash-0731"
    assets = AssetRegistry(ROOT).load(model)
    on = ModelEncoder(assets, DEFAULT_SETTINGS[model], EncodingProfile(default_thinking=True))
    off = ModelEncoder(assets, DEFAULT_SETTINGS[model], EncodingProfile(default_thinking=False))
    raw = json.dumps(bodies(model)[3])
    rendered = on.render(raw)
    assert rendered.text != off.render(raw).text
    # Template controls are explicit; the user's literal User marker must remain plain.
    spans = [rendered.text[a:b] for a, b in rendered.special_ranges]
    assert spans.count("<｜User｜>") == 1
    assert rendered.text.count("<｜User｜>") == 2
    result = EncodingBatchService(on).encode_batch([raw])[0]
    assert isinstance(result, EncodedRequest)
    token_id = on.added_ids["<｜User｜>"]
    assert result.prompt_ids.count(token_id) == 1


def test_deepseek_explicit_request_needs_no_missing_default():
    model = "DeepSeek-V4-Flash-0731"
    encoder = ModelEncoder(AssetRegistry(ROOT).load(model), DEFAULT_SETTINGS[model])
    request = bodies(model)[0]
    request["thinking"] = {"type": "disabled"}
    assert isinstance(
        EncodingBatchService(encoder).encode_batch([json.dumps(request)])[0], EncodedRequest
    )
    request["chat_template_kwargs"] = {"drop_thinking": False}
    assert isinstance(
        EncodingBatchService(encoder).encode_batch([json.dumps(request)])[0], EncodingFailure
    )


def test_source_references_do_not_invent_missing_model_field():
    model = "GLM-5.2"
    encoder = ModelEncoder(AssetRegistry(ROOT).load(model), DEFAULT_SETTINGS[model])
    rendered = encoder.render(json.dumps({"messages": [{"role": "user", "content": "hello"}]}))
    assert "/model" not in [item["json_pointer"] for item in rendered.source_fields]


def test_serial_and_parallel_rust_pools_are_identical():
    script = """
import json,sys
from pathlib import Path
from tokenscope.domain import DEFAULT_SETTINGS
from tokenscope.encoding.assets import AssetRegistry
from tokenscope.encoding.models import ModelEncoder,EncodingProfile
from tokenscope.encoding.batch import EncodingBatchService,EncodedRequest
root=Path.cwd()
results={}
for model,settings in DEFAULT_SETTINGS.items():
    default=False if model.startswith('DeepSeek') else None
    profile=EncodingProfile(cpu_budget=int(sys.argv[1]),default_thinking=default)
    encoder=ModelEncoder(AssetRegistry(root).load(model),settings,profile)
    inputs=['a 中文', '你好 '*4096, '<｜User｜> <|im_start|>']
    requests=[{'model':model,'messages':[{'role':'user','content':x}]} for x in inputs]
    texts=[json.dumps(value,ensure_ascii=False) for value in requests]
    values=EncodingBatchService(encoder).encode_batch(texts)
    assert all(isinstance(v,EncodedRequest) for v in values)
    results[model]=[(v.json_tokens,v.prompt_digest,v.encoder_identity) for v in values]
print(json.dumps(results,sort_keys=True))
"""
    results = []
    for workers in (1, 4):
        env = dict(os.environ, RAYON_NUM_THREADS=str(workers))
        result = subprocess.run(
            [sys.executable, "-c", script, str(workers)],
            cwd=ROOT,
            env=env,
            text=True,
            capture_output=True,
            check=True,
            timeout=120,
        )
        results.append(json.loads(result.stdout))
    assert results[0] == results[1]
