"""Thin wrapper around the `bmb` CLI binary.

Tools that need to invoke the BMB compiler (check, verify, compile, test)
all go through this module so subprocess handling, timeout, and
machine-output parsing live in one place.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
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
