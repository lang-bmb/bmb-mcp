"""Chatter MCP server entry point.

Implements a minimal first slice of the design in README.md:

  - tools:     bmb_check          (others stubbed)
  - resources: (deferred)
  - prompts:   (deferred)

The remaining tools/resources/prompts are tracked under Track N
Phase 2+ and added incrementally so each MCP capability lands with
its own tests.
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

from mcp.server.fastmcp import FastMCP

from .bmb_cli import BmbBinaryNotFound, find_bmb_binary, run_bmb


mcp = FastMCP("bmb-chatter")


@mcp.tool()
def bmb_check(source: str, filename: str = "snippet.bmb") -> dict:
    """Type-check a BMB source snippet without producing a binary.

    Args:
        source: BMB source code as a string.
        filename: Display name for diagnostics (default: snippet.bmb).

    Returns a dict with keys:
        ok: bool
        diagnostics: raw bmb stdout (machine-format JSON when bmb
            emits structured output, otherwise plain text)
        stderr: any error stream content
        returncode: bmb exit code
    """
    with tempfile.TemporaryDirectory(prefix="chatter-check-") as tmp:
        tmp_path = Path(tmp) / filename
        tmp_path.write_text(source, encoding="utf-8")
        result = run_bmb(["check", str(tmp_path)])
    return {
        "ok": result.ok,
        "diagnostics": result.stdout,
        "stderr": result.stderr,
        "returncode": result.returncode,
    }


def main() -> int:
    """Console entry point — runs the MCP server on stdio transport."""
    try:
        find_bmb_binary()
    except BmbBinaryNotFound as exc:
        print(f"chatter: {exc}", file=sys.stderr)
        return 1

    mcp.run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
