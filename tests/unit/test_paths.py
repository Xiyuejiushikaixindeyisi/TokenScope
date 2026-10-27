import hashlib
from pathlib import Path

import pytest

from tokenscope.errors import TokenScopeError
from tokenscope.paths import InputRoot


@pytest.mark.parametrize(
    "file_ref", ["../private", "/etc/passwd", "sub/../../x", "", ".", "C:/a", "a\\b"]
)
def test_path_traversal_rejected(tmp_path, file_ref):
    root = InputRoot(tmp_path)
    with pytest.raises(TokenScopeError):
        with root.open(file_ref):
            pass


def test_symlinks_rejected_for_file_and_parent(tmp_path):
    inputs = tmp_path / "input"
    inputs.mkdir()
    outside = tmp_path / "secret"
    outside.write_text("SECRET")
    (inputs / "file").symlink_to(outside)
    (inputs / "directory").symlink_to(tmp_path, target_is_directory=True)
    for file_ref in ("file", "directory/secret"):
        with pytest.raises(TokenScopeError):
            with InputRoot(inputs).open(file_ref):
                pass


def test_actual_open_checks_replaced_symlink(tmp_path):
    nested = tmp_path / "nested"
    nested.mkdir()
    (nested / "a.csv").write_text("original")
    root = InputRoot(tmp_path)
    assert root.parts("nested/a.csv") == ("nested", "a.csv")
    (nested / "a.csv").unlink()
    (nested / "a.csv").symlink_to("/etc/passwd")
    with pytest.raises(TokenScopeError):
        with root.open("nested/a.csv"):
            pass


def test_snapshot_exclusive_and_checksum(tmp_path):
    (tmp_path / "a.csv").write_bytes(b"raw\r\n")
    destination = tmp_path / "runs" / "input.csv"
    root = InputRoot(tmp_path)
    assert root.snapshot("a.csv", destination) == hashlib.sha256(b"raw\r\n").hexdigest()
    with pytest.raises(FileExistsError):
        root.snapshot("a.csv", destination)
    assert destination.read_bytes() == b"raw\r\n"
    assert list(destination.parent.glob("*.partial")) == []


def test_open_does_not_relabel_caller_error(tmp_path):
    (tmp_path / "a").write_bytes(b"data")
    with pytest.raises(FileNotFoundError):
        with InputRoot(tmp_path).open("a"):
            Path("/not-a-real-path/tokenscope-sentinel").read_bytes()


def test_fifo_and_directory_not_read(tmp_path):
    import os

    os.mkfifo(tmp_path / "fifo")
    (tmp_path / "dir").mkdir()
    for file_ref in ("fifo", "dir"):
        with pytest.raises(TokenScopeError) as exc:
            with InputRoot(tmp_path).open(file_ref):
                pass
        assert exc.value.code == "INVALID_INPUT_FILE"
