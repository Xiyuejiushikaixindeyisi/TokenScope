import pytest

from tokenscope.encoding.shards import TokenShardWriter, read_slice
from tokenscope.errors import TokenScopeError


def test_uint32_shards_round_trip_and_rotation(tmp_path):
    writer = TokenShardWriter(tmp_path, max_bytes=8)
    records = [[], [1, 2**32 - 1], [256], [0] * 10]
    references = [writer.append(ids) for ids in records]
    writer.close()
    assert [read_slice(tmp_path, ref) for ref in references] == records
    assert references[0].shard == references[1].shard
    assert references[2].shard != references[1].shard
    assert (tmp_path / references[1].shard).read_bytes() == b"\x01\x00\x00\x00\xff\xff\xff\xff"
    with pytest.raises(TokenScopeError):
        writer.append([1])


def test_corrupt_and_truncated_shards_fail(tmp_path):
    writer = TokenShardWriter(tmp_path)
    ref = writer.append([1, 2])
    writer.close()
    (tmp_path / ref.shard).write_bytes(b"\x00" * 8)
    with pytest.raises(TokenScopeError) as error:
        read_slice(tmp_path, ref)
    assert error.value.code == "TOKEN_SHARD_DIGEST_MISMATCH"
    (tmp_path / ref.shard).write_bytes(b"\x00" * 4)
    with pytest.raises(TokenScopeError) as error:
        read_slice(tmp_path, ref)
    assert error.value.code == "TRUNCATED_TOKEN_SHARD"


def test_existing_shard_never_overwritten(tmp_path):
    path = tmp_path / "tokens-000001.bin"
    path.write_bytes(b"existing")
    with pytest.raises(FileExistsError):
        TokenShardWriter(tmp_path).append([1])
    assert path.read_bytes() == b"existing"
