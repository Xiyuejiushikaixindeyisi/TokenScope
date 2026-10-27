import random

import pytest

from tokenscope.domain import DEFAULT_SETTINGS
from tokenscope.errors import TokenScopeError
from tokenscope.monitoring.simulation import (
    DeepSeekHybridStrategy,
    FullBlockStrategy,
    NoCacheStrategy,
    PrefixLedger,
    QwenHybridStrategy,
    make_strategy,
)


@pytest.mark.parametrize("block", [1, 2, 32, 128, 1536])
@pytest.mark.parametrize("mtp", [False, True])
@pytest.mark.parametrize("cp", [1, 2])
def test_boundaries_against_history_prefix_reference(tmp_path, block, mtp, cp):
    settings = DEFAULT_SETTINGS["GLM-5.2"].model_copy(
        update=dict(block_size=block, mtp=mtp, cp_world_size=cp)
    )
    ledger = PrefixLedger(tmp_path / "ledger.sqlite3")
    strategy = FullBlockStrategy(settings, "asset", ledger)
    size = block * cp
    histories = {}
    rng = random.Random(437)
    try:
        for i in range(80):
            tenant = str(i % 3)
            length = rng.choice(
                [0, 1, size - 1, size, size + 1, 2 * size, 2 * size + 1, 4 * size + 1]
            )
            ids = ([1] * length) if i % 4 else ([1] * max(0, length - 1) + [2] if length else [])
            # Reference stores full historical sequences, compares raw prefixes, no chain hashing.
            longest = 0
            for previous in histories.get(tenant, []):
                common = 0
                for left, right in zip(previous, ids, strict=False):
                    if left != right:
                        break
                    common += 1
                longest = max(longest, min(common // size, len(previous) // size))
            matched = min(longest, max(len(ids) - 1, 0) // size)
            expected = max(matched - int(mtp), 0) * size
            result = strategy.process(tenant, ids)
            assert result.hit_tokens == expected
            assert result.compute_tokens + expected == len(ids)
            assert result.published_blocks == len(ids) // size
            histories.setdefault(tenant, []).append(ids)
    finally:
        ledger.close()


def test_namespaces_no_cache_and_reserved(tmp_path):
    settings = DEFAULT_SETTINGS["GLM-5.2"].model_copy(update=dict(block_size=2, mtp=False))
    ledger = PrefixLedger(tmp_path / "ledger.sqlite3")
    try:
        first = FullBlockStrategy(settings, "one", ledger)
        assert first.process("a", [1] * 9).hit_tokens == 0
        assert first.process("a", [1] * 9).hit_tokens == 8
        assert first.process("b", [1] * 9).hit_tokens == 0
        assert FullBlockStrategy(settings, "two", ledger).process("a", [1] * 9).hit_tokens == 0
        assert NoCacheStrategy().process("a", [1] * 9).compute_tokens == 9
        for strategy in [QwenHybridStrategy(), DeepSeekHybridStrategy()]:
            with pytest.raises(TokenScopeError, match="reserved"):
                strategy.process("a", [1])
        enhanced = DEFAULT_SETTINGS["Qwen3.6-27B"].model_copy(update={"hybrid_enabled": True})
        with pytest.raises(TokenScopeError):
            make_strategy(enhanced, "one", ledger)
    finally:
        ledger.close()
