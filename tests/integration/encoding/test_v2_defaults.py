import json
from pathlib import Path

from tokenscope.domain import DEFAULT_SETTINGS
from tokenscope.encoding.assets import AssetRegistry
from tokenscope.encoding.batch import EncodedRequest, EncodingBatchService
from tokenscope.encoding.models import EncodingProfile, ModelEncoder
from tokenscope.monitoring.pipeline import profile_for


def test_new_deepseek_default_preserves_raw_json_and_explicit_precedence():
    root = Path(__file__).resolve().parents[3]
    settings = DEFAULT_SETTINGS["DeepSeek-V4-Flash-0731"]
    assets = AssetRegistry(root).load(settings.model_id)
    selected = ModelEncoder(assets, settings, profile_for(settings, 8))
    legacy = ModelEncoder(
        assets,
        settings.model_copy(update={"encoding_profile": "default"}),
        EncodingProfile(default_thinking=False, cpu_budget=8),
    )
    texts = [
        json.dumps(
            {
                "model": "DeepSeek-V4-Flash-64K",
                "messages": [{"role": "user", "content": "中文  spaces"}],
                **extra,
            },
            ensure_ascii=False,
            indent=2,
        )
        for extra in ({}, {"thinking": {"type": "enabled"}}, {"thinking": {"type": "disabled"}})
    ]
    for text in texts:
        result = EncodingBatchService(selected).encode_batch([text])[0]
        previous = EncodingBatchService(legacy).encode_batch([text])[0]
        assert isinstance(result, EncodedRequest) and isinstance(previous, EncodedRequest)
        assert result.prompt_ids == previous.prompt_ids
        assert result.json_tokens == previous.json_tokens
        assert result.json_tokens == len(selected.plain.encode(text, add_special_tokens=False).ids)
    assert selected.render(texts[1]).text != selected.render(texts[2]).text
