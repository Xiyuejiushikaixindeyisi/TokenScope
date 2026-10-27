"""Append-only uint32 little-endian token shards with validated slice references."""

import hashlib
import os
import struct
from pathlib import Path
from typing import BinaryIO

from pydantic import Field

from tokenscope.domain import NonnegativeInt, StrictModel
from tokenscope.encoding.batch import ids_bytes
from tokenscope.errors import TokenScopeError


class TokenSlice(StrictModel):
    shard: str = Field(pattern=r"^tokens-[0-9]{6,}\.bin$")
    offset_bytes: NonnegativeInt
    token_count: NonnegativeInt
    sha256: str = Field(pattern=r"^[0-9a-f]{64}$")


class TokenShardWriter:
    def __init__(self, directory: Path, max_bytes: int = 64 * 1024 * 1024) -> None:
        if max_bytes <= 0:
            raise ValueError("Shard budget must be positive")
        self.directory = directory
        directory.mkdir(parents=True, exist_ok=True)
        self.max_bytes = max_bytes
        self.number = 0
        self.stream: BinaryIO | None = None
        self.closed = False

    def append(self, ids: list[int]) -> TokenSlice:
        if self.closed:
            raise TokenScopeError("SHARD_CLOSED", "Token writer has been sealed", 409)
        content = ids_bytes(ids)
        if (
            self.stream is not None
            and self.stream.tell()
            and self.stream.tell() + len(content) > self.max_bytes
        ):
            self.flush_close()
        if self.stream is None:
            self.number += 1
            self.stream = (self.directory / f"tokens-{self.number:06d}.bin").open("xb")
        offset = self.stream.tell()
        self.stream.write(content)
        return TokenSlice(
            shard=f"tokens-{self.number:06d}.bin",
            offset_bytes=offset,
            token_count=len(ids),
            sha256=hashlib.sha256(content).hexdigest(),
        )

    def flush_close(self) -> None:
        if self.stream is not None:
            try:
                self.stream.flush()
                os.fsync(self.stream.fileno())
            finally:
                self.stream.close()
                self.stream = None

    def close(self) -> None:
        self.flush_close()
        self.closed = True


def read_slice(directory: Path, reference: TokenSlice) -> list[int]:
    if reference.offset_bytes % 4:
        raise TokenScopeError("INVALID_TOKEN_SLICE", "Unaligned Token IDs reference", 409)
    size = reference.token_count * 4
    with (directory / reference.shard).open("rb") as stream:
        if reference.offset_bytes + size > os.fstat(stream.fileno()).st_size:
            raise TokenScopeError("TRUNCATED_TOKEN_SHARD", "Token IDs shard is incomplete", 409)
        stream.seek(reference.offset_bytes)
        content = stream.read(size)
    if hashlib.sha256(content).hexdigest() != reference.sha256:
        raise TokenScopeError("TOKEN_SHARD_DIGEST_MISMATCH", "Stored Token IDs have changed", 409)
    return [item[0] for item in struct.iter_unpack("<I", content)]
