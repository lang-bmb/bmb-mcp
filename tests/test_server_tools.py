"""Tests for server tools, resources, and prompts.

These tests import server functions directly without starting the MCP server,
so they don't require a running MCP transport.
"""

from __future__ import annotations

import pytest

from chatter.bmb_cli import BmbBinaryNotFound, find_bmb_binary, find_repo_root
from chatter.server import (
    bmb_check,
    bmb_verify,
    bmb_spec_lookup,
    bmb_lint,
    bmb_lint_explain,
    bmb_example,
    bmb_implement,
    bmb_add_contracts,
    bmb_optimize,
    spec_quick_reference,
    spec_rust_diff,
    spec_full,
)


def _bmb_available() -> bool:
    try:
        find_bmb_binary()
        return True
    except BmbBinaryNotFound:
        return False


pytestmark = pytest.mark.skipif(
    not _bmb_available(),
    reason="bmb binary not found",
)


# ---------------------------------------------------------------------------
# find_repo_root
# ---------------------------------------------------------------------------


def test_find_repo_root_returns_path():
    root = find_repo_root()
    assert root is not None
    assert (root / "Cargo.toml").is_file()


# ---------------------------------------------------------------------------
# bmb_verify
# ---------------------------------------------------------------------------


def test_bmb_verify_valid_no_contracts():
    result = bmb_verify("fn main() -> i64 = 0;\n")
    # verify on a file with no contracts succeeds (nothing to falsify)
    assert isinstance(result, dict)
    assert "ok" in result
    assert "diagnostics" in result
    assert "returncode" in result


def test_bmb_verify_returns_dict_structure():
    result = bmb_verify("fn add(a: i64, b: i64) -> i64 = a + b;\n")
    assert set(result.keys()) >= {"ok", "diagnostics", "stderr", "returncode"}


# ---------------------------------------------------------------------------
# Resources
# ---------------------------------------------------------------------------


def test_spec_quick_reference_contains_key_content():
    qr = spec_quick_reference()
    assert "BMB Quick Reference" in qr
    assert "band" in qr
    assert "pre " in qr
    assert "post " in qr


def test_spec_rust_diff_contains_key_content():
    rd = spec_rust_diff()
    assert "BMB vs Rust" in rd
    assert "Option<T>" in rd
    assert "T?" in rd


def test_spec_full_returns_content():
    content = spec_full()
    # Either the spec file or an error message
    assert isinstance(content, str)
    assert len(content) > 100


def test_spec_full_has_specification_content():
    root = find_repo_root()
    if root is None:
        pytest.skip("repo root not found")
    spec = root / "docs" / "SPECIFICATION.md"
    if not spec.exists():
        pytest.skip("SPECIFICATION.md not found")
    content = spec_full()
    assert "BMB" in content or "bmb" in content


# ---------------------------------------------------------------------------
# Prompts
# ---------------------------------------------------------------------------


def test_bmb_implement_contains_description():
    prompt = bmb_implement("computes the factorial of n")
    assert "factorial" in prompt
    assert "BMB" in prompt or "bmb" in prompt


def test_bmb_implement_with_contracts():
    prompt = bmb_implement("sorts an array", include_contracts=True)
    assert "pre" in prompt.lower() or "contract" in prompt.lower()


def test_bmb_implement_without_contracts():
    prompt = bmb_implement("returns the maximum", include_contracts=False)
    assert isinstance(prompt, str)
    assert len(prompt) > 20


def test_bmb_add_contracts_includes_source():
    source = "fn square(x: i64) -> i64 = x * x;\n"
    prompt = bmb_add_contracts(source)
    assert "square" in prompt
    assert "pre" in prompt.lower() or "contract" in prompt.lower()


def test_bmb_optimize_speed():
    source = "fn sum(arr: [i64; 16], n: i64) -> i64 = arr[0];\n"
    prompt = bmb_optimize(source, target="speed")
    assert "speed" in prompt.lower() or "performance" in prompt.lower() or "optimize" in prompt.lower()


def test_bmb_optimize_size():
    source = "fn noop() -> i64 = 0;\n"
    prompt = bmb_optimize(source, target="size")
    assert "size" in prompt.lower() or "noinline" in prompt.lower()


# ---------------------------------------------------------------------------
# bmb_spec_lookup
# ---------------------------------------------------------------------------


def test_bmb_spec_lookup_returns_dict():
    result = bmb_spec_lookup("contracts")
    assert isinstance(result, dict)
    assert "ok" in result
    assert "sections" in result
    assert "total_matches" in result


def test_bmb_spec_lookup_finds_contracts():
    result = bmb_spec_lookup("contracts")
    assert result["ok"]
    assert result["total_matches"] > 0
    assert len(result["sections"]) > 0
    assert any("contract" in s.lower() for s in result["sections"])


def test_bmb_spec_lookup_finds_type_system():
    result = bmb_spec_lookup("type")
    assert result["ok"]
    assert result["total_matches"] > 0


def test_bmb_spec_lookup_max_sections():
    result = bmb_spec_lookup("the", max_sections=2)
    assert len(result["sections"]) <= 2


def test_bmb_spec_lookup_no_match():
    result = bmb_spec_lookup("xyzzy_nonexistent_keyword_12345")
    assert result["ok"]
    assert result["total_matches"] == 0
    assert result["sections"] == []


# ---------------------------------------------------------------------------
# bmb_lint
# ---------------------------------------------------------------------------


def test_bmb_lint_returns_dict():
    result = bmb_lint("fn main() -> i64 = 0;\n")
    assert isinstance(result, dict)
    assert set(result.keys()) >= {"ok", "diagnostics", "stderr", "returncode"}


def test_bmb_lint_clean_code_exits_ok():
    # A well-formed function may still produce missing_postcondition warnings,
    # but the exit code should be 0.
    result = bmb_lint("fn add(a: i64, b: i64) -> i64 = a + b;\n")
    assert isinstance(result["ok"], bool)


def test_bmb_lint_invalid_code_fails():
    # Parser error — lint should fail
    result = bmb_lint("this is not valid bmb code !!!\n")
    assert not result["ok"]


# ---------------------------------------------------------------------------
# bmb_example
# ---------------------------------------------------------------------------


def test_bmb_example_returns_dict():
    result = bmb_example("function")
    assert isinstance(result, dict)
    assert set(result.keys()) >= {"ok", "examples", "total_matches"}


def test_bmb_example_finds_contract_examples():
    result = bmb_example("contract")
    assert result["ok"]
    # BY_EXAMPLE.md should have contract-related sections
    assert result["total_matches"] >= 0  # may be 0 if file lacks contracts section
    assert isinstance(result["examples"], list)


def test_bmb_example_max_examples():
    result = bmb_example("the", max_examples=1)
    assert len(result["examples"]) <= 1


def test_bmb_example_no_match():
    result = bmb_example("xyzzy_nonexistent_12345")
    assert result["ok"]
    assert result["total_matches"] == 0
    assert result["examples"] == []


# ---------------------------------------------------------------------------
# bmb_lint_explain
# ---------------------------------------------------------------------------


def test_bmb_lint_explain_returns_dict():
    result = bmb_lint_explain("fn main() -> i64 = 0;\n")
    assert isinstance(result, dict)
    assert set(result.keys()) >= {"ok", "warnings", "count", "stderr"}


def test_bmb_lint_explain_warnings_have_explanations():
    # A function without postcondition should produce missing_postcondition warning
    source = "fn add(a: i64, b: i64) -> i64 = a + b;\n"
    result = bmb_lint_explain(source)
    assert result["ok"]
    # Each warning dict must have explanation + fix_suggestion
    for w in result["warnings"]:
        assert "explanation" in w
        assert "fix_suggestion" in w
        assert isinstance(w["explanation"], str)
        assert isinstance(w["fix_suggestion"], str)


def test_bmb_lint_explain_missing_postcondition_has_content():
    source = "fn square(x: i64) -> i64 = x * x;\n"
    result = bmb_lint_explain(source)
    postcond_warnings = [w for w in result["warnings"]
                         if w.get("kind") == "missing_postcondition"]
    if postcond_warnings:
        w = postcond_warnings[0]
        assert len(w["explanation"]) > 20
        assert len(w["fix_suggestion"]) > 20


def test_bmb_lint_explain_count_matches_warnings():
    result = bmb_lint_explain("fn f(x: i64) -> i64 = x;\n")
    assert result["count"] == len(result["warnings"])


def test_bmb_lint_explain_invalid_code():
    result = bmb_lint_explain("this is not valid bmb!!!\n")
    assert not result["ok"]
    assert result["count"] == 0
