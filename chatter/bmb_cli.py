"""Thin wrapper around the `bmb` CLI binary and ecosystem tools.

Tools that need to invoke the BMB compiler (check, verify, compile, test)
and ecosystem binaries (context_pack) all go through this module so subprocess
handling, timeout, and machine-output parsing live in one place.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


class BmbBinaryNotFound(RuntimeError):
    """Raised when no `bmb` binary can be located."""


@dataclass(frozen=True)
class BmbResult:
    returncode: int
    stdout: str
    stderr: str

    @property
    def ok(self) -> bool:
        return self.returncode == 0

    def parse_json_stdout(self) -> object | None:
        """Best-effort parse of stdout as JSON. Returns None on parse failure."""
        try:
            return json.loads(self.stdout)
        except json.JSONDecodeError:
            return None


def find_bmb_binary() -> Path:
    """Locate the bmb binary. Honors $BMB_BINARY, then $PATH, then common
    workspace target/ paths. Raises BmbBinaryNotFound on failure."""
    explicit = os.environ.get("BMB_BINARY")
    if explicit:
        p = Path(explicit)
        if p.is_file():
            return p
        raise BmbBinaryNotFound(f"$BMB_BINARY={explicit} is not a file")

    on_path = shutil.which("bmb")
    if on_path:
        return Path(on_path)

    # Fall back to repo-local builds — useful when running from a checkout.
    here = Path(__file__).resolve()
    for ancestor in here.parents:
        if (ancestor / "Cargo.toml").is_file():
            for candidate in (
                ancestor / "target" / "release" / "bmb",
                ancestor / "target" / "release" / "bmb.exe",
                ancestor / "target" / "x86_64-pc-windows-gnu" / "release" / "bmb.exe",
            ):
                if candidate.is_file():
                    return candidate
            break

    raise BmbBinaryNotFound(
        "bmb binary not found. Set $BMB_BINARY, add bmb to PATH, "
        "or run `cargo build --release` in the workspace."
    )


def find_repo_root() -> Path | None:
    """Locate the BMB repository root (directory containing Cargo.toml).
    Returns None if not found."""
    here = Path(__file__).resolve()
    for ancestor in here.parents:
        if (ancestor / "Cargo.toml").is_file():
            return ancestor
    return None


def find_context_pack_binary() -> Path | None:
    """Locate the context_pack native binary.

    Checks {repo_root}/bootstrap/context_pack/context_pack[.exe].
    If the binary is missing, attempts to build it with 'bmb build'.
    Returns None if the binary cannot be found or built.
    """
    root = find_repo_root()
    if root is None:
        return None

    exe_suffix = ".exe" if sys.platform == "win32" else ""
    binary = root / "bootstrap" / "context_pack" / f"context_pack{exe_suffix}"
    if binary.is_file():
        return binary

    # Binary missing — attempt to build it on demand
    src = root / "bootstrap" / "context_pack" / "context_pack.bmb"
    if not src.is_file():
        return None

    try:
        bmb_binary = find_bmb_binary()
    except BmbBinaryNotFound:
        return None

    result = subprocess.run(
        [str(bmb_binary), "build", str(src), "-o", str(binary)],
        capture_output=True,
        text=True,
        timeout=120.0,
        check=False,
    )
    return binary if (result.returncode == 0 and binary.is_file()) else None


def run_context_pack(root: str, max_tokens: int = 0, timeout: float = 30.0) -> BmbResult:
    """Run the context_pack native binary against a directory.

    Args:
        root: Absolute path to the BMB project directory to scan.
        max_tokens: Token budget (0 = no limit).
        timeout: Subprocess timeout in seconds.

    Returns a BmbResult. On binary-not-found, returns returncode=-1.
    """
    binary = find_context_pack_binary()
    if binary is None:
        return BmbResult(
            returncode=-1,
            stdout="",
            stderr="context_pack binary not found and could not be built",
        )

    args = [str(binary), root]
    if max_tokens > 0:
        args += ["--max-tokens", str(max_tokens)]

    proc = subprocess.run(
        args,
        capture_output=True,
        text=True,
        timeout=timeout,
        check=False,
    )
    return BmbResult(
        returncode=proc.returncode,
        stdout=proc.stdout,
        stderr=proc.stderr,
    )


def find_lint_native_binary() -> Path | None:
    """Locate the lint native binary (bootstrap/lint/lint[.exe]).

    Checks {repo_root}/bootstrap/lint/lint[.exe].
    If missing, attempts to build it from bootstrap/lint/lint.bmb.
    Returns None if binary cannot be found or built.
    """
    root = find_repo_root()
    if root is None:
        return None

    exe_suffix = ".exe" if sys.platform == "win32" else ""
    binary = root / "bootstrap" / "lint" / f"lint{exe_suffix}"
    if binary.is_file():
        return binary

    src = root / "bootstrap" / "lint" / "lint.bmb"
    if not src.is_file():
        return None

    try:
        bmb_binary = find_bmb_binary()
    except BmbBinaryNotFound:
        return None

    result = subprocess.run(
        [str(bmb_binary), "build", str(src), "-o", str(binary)],
        capture_output=True,
        text=True,
        timeout=120.0,
        check=False,
    )
    return binary if (result.returncode == 0 and binary.is_file()) else None


def run_lint_native(path: str, timeout: float = 30.0) -> BmbResult:
    """Run the BMB-native lint binary against a single .bmb file.

    Args:
        path: Absolute path to the .bmb file to lint.
        timeout: Subprocess timeout in seconds.

    Returns a BmbResult.
    """
    binary = find_lint_native_binary()
    if binary is None:
        return BmbResult(
            returncode=-1,
            stdout="",
            stderr="lint native binary not found and could not be built",
        )

    proc = subprocess.run(
        [str(binary), path],
        capture_output=True,
        text=True,
        timeout=timeout,
        check=False,
    )
    return BmbResult(
        returncode=proc.returncode,
        stdout=proc.stdout,
        stderr=proc.stderr,
    )


def run_bmb(args: list[str], *, cwd: Path | None = None, timeout: float = 30.0) -> BmbResult:
    """Invoke `bmb <args>` and capture stdout/stderr. The default output
    format is machine-friendly (CLAUDE.md Rule 8) — callers requesting
    human output must opt in with `--human`."""
    binary = find_bmb_binary()
    proc = subprocess.run(
        [str(binary), *args],
        capture_output=True,
        text=True,
        cwd=str(cwd) if cwd else None,
        timeout=timeout,
        check=False,
    )
    return BmbResult(
        returncode=proc.returncode,
        stdout=proc.stdout,
        stderr=proc.stderr,
    )
