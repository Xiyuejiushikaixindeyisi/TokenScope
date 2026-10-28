"""Input access anchored to a directory descriptor, including during actual open."""

import errno
import hashlib
import os
import stat
import tempfile
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path, PurePosixPath
from typing import BinaryIO

from tokenscope.errors import TokenScopeError


class InputRoot:
    def __init__(self, root: Path) -> None:
        try:
            self.root = root.resolve(strict=True)
        except (FileNotFoundError, NotADirectoryError) as exc:
            raise TokenScopeError(
                "INVALID_INPUT_ROOT",
                "Input root does not exist or is not a directory; "
                "create --input-root before starting",
            ) from exc
        if not self.root.is_dir():
            raise TokenScopeError("INVALID_INPUT_ROOT", "Input root must be a directory")

    @staticmethod
    def parts(file_ref: str) -> tuple[str, ...]:
        path = PurePosixPath(file_ref)
        if (
            not file_ref
            or "\x00" in file_ref
            or "\\" in file_ref
            or path.is_absolute()
            or ".." in path.parts
            or not path.parts
            or ":" in path.parts[0]
        ):
            raise TokenScopeError("INVALID_FILE_REF", "Use a relative file inside the input root")
        return path.parts

    @contextmanager
    def open(self, file_ref: str) -> Iterator[BinaryIO]:
        parts = self.parts(file_ref)
        directory = os.open(self.root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
        file_fd: int | None = None
        try:
            for part in parts[:-1]:
                next_fd = os.open(
                    part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=directory
                )
                os.close(directory)
                directory = next_fd
            file_fd = os.open(
                parts[-1], os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=directory
            )
            if not stat.S_ISREG(os.fstat(file_fd).st_mode):
                raise TokenScopeError("INVALID_INPUT_FILE", "Input must be a regular file")
            stream = os.fdopen(file_fd, "rb")
            file_fd = None
        except OSError as exc:
            if exc.errno in {errno.ELOOP, errno.ENOTDIR}:
                raise TokenScopeError(
                    "INVALID_FILE_REF", "Symbolic links are not accepted"
                ) from exc
            if exc.errno == errno.ENOENT:
                raise TokenScopeError("INPUT_NOT_FOUND", "Input file does not exist", 404) from exc
            if exc.errno == errno.EACCES:
                raise TokenScopeError(
                    "INPUT_PERMISSION_DENIED", "Input is not readable", 403
                ) from exc
            raise
        finally:
            if file_fd is not None:
                os.close(file_fd)
            os.close(directory)
        with stream:
            yield stream

    def snapshot(self, file_ref: str, destination: Path) -> str:
        """Copy to a new immutable run path, rejecting an observed concurrent writer."""
        destination.parent.mkdir(parents=True, exist_ok=True)
        fd, name = tempfile.mkstemp(prefix=".input-", suffix=".partial", dir=destination.parent)
        temporary = Path(name)
        digest = hashlib.sha256()
        try:
            with os.fdopen(fd, "wb") as target, self.open(file_ref) as source:
                before = os.fstat(source.fileno())
                while block := source.read(1024 * 1024):
                    target.write(block)
                    digest.update(block)
                target.flush()
                os.fsync(target.fileno())
                after = os.fstat(source.fileno())
                if (before.st_size, before.st_mtime_ns) != (after.st_size, after.st_mtime_ns):
                    raise TokenScopeError("INPUT_CHANGED", "Input changed while being copied", 409)
            # Link is exclusive: retries must not silently overwrite an existing snapshot.
            os.link(temporary, destination)
            temporary.unlink()
            directory = os.open(destination.parent, os.O_RDONLY | os.O_DIRECTORY)
            try:
                os.fsync(directory)
            finally:
                os.close(directory)
        except BaseException:
            temporary.unlink(missing_ok=True)
            raise
        return digest.hexdigest()
