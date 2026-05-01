"""Tests for the bmb CLI wrapper.

These tests don't require the `mcp` package, only that a `bmb` binary
is reachable (via $BMB_BINARY, $PATH, or workspace target/).
"""

from __future__ import annotations

import os
import subprocess
import tempfile
from pathlib import Path

import pytest

from chatter.bmb_cli import BmbBinaryNotFound, find_bmb_binary, run_bmb


def _bmb_available() -> bool:
    try:
        find_bmb_binary()
        return True
    except BmbBinaryNotFound:
        return False


pytestmark = pytest.mark.skipif(
    not _bmb_available(),
    reason="bmb binary not found — set BMB_BINARY or run cargo build --release",
)


def test_find_bmb_binary_returns_path():
    p = find_bmb_binary()
    assert p.is_file()


def test_run_bmb_help_succeeds():
    result = run_bmb(["--help"])
    assert result.ok
    assert "bmb" in result.stdout.lower() or "bmb" in result.stderr.lower()


def test_run_bmb_check_valid_snippet():
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "ok.bmb"
        path.write_text("fn main() -> i64 = 0;\n", encoding="utf-8")
        result = run_bmb(["check", str(path)])
    assert result.ok, f"bmb check failed: stderr={result.stderr!r} stdout={result.stdout!r}"


def test_run_bmb_check_invalid_snippet_returns_error():
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "broken.bmb"
        # Missing semicolon — bmb parser should reject.
        path.write_text("fn main() -> i64 = 0\n", encoding="utf-8")
        result = run_bmb(["check", str(path)])
    assert not result.ok


def test_explicit_env_var_missing_file_raises():
    os.environ["BMB_BINARY"] = "/nonexistent/path/to/bmb"
    try:
        with pytest.raises(BmbBinaryNotFound):
            find_bmb_binary()
    finally:
        del os.environ["BMB_BINARY"]
