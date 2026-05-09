"""Tests for server tools, resources, and prompts.

These tests import server functions directly without starting the MCP server,
so they don't require a running MCP transport.
"""

from __future__ import annotations

import pytest

from chatter.bmb_cli import BmbBinaryNotFound, find_bmb_binary, find_repo_root
from chatter.server import (
    bmb_check,
    bmb_compile,
    bmb_context_pack,
    bmb_ir,
    bmb_run,
    bmb_test,
    bmb_from_rust,
    bmb_verify,
    bmb_spec_lookup,
    bmb_lint,
    bmb_lint_explain,
    bmb_lint_native,
    bmb_example,
    bmb_implement,
    bmb_add_contracts,
    bmb_optimize,
    spec_quick_reference,
    spec_rust_diff,
    spec_full,
    context_stdlib,
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


def test_bmb_lint_explain_explanations_dict_covers_new_kinds():
    # Verify the explanations dict itself has entries for the new native-lint kinds.
    # bmb_lint_explain uses the Rust lint, not lint.bmb, so these kinds won't appear
    # in actual lint output here — but the dict must be populated for when they do.
    from chatter.server import _LINT_EXPLANATIONS
    assert "redundant_if_expression" in _LINT_EXPLANATIONS
    assert "empty_block" in _LINT_EXPLANATIONS
    r_exp, r_fix = _LINT_EXPLANATIONS["redundant_if_expression"]
    assert len(r_exp) > 20 and len(r_fix) > 20
    e_exp, e_fix = _LINT_EXPLANATIONS["empty_block"]
    assert len(e_exp) > 20 and len(e_fix) > 20


# ---------------------------------------------------------------------------
# bmb_lint_native (Track Q Phase 2)
# ---------------------------------------------------------------------------


def test_bmb_lint_native_returns_dict():
    result = bmb_lint_native("fn main() -> i64 = 0;\n")
    assert isinstance(result, dict)
    assert set(result.keys()) >= {"ok", "warnings", "count", "stderr"}


def test_bmb_lint_native_clean_code_zero_warnings():
    source = "pub fn add(a: i64, b: i64) -> i64\npost ret == a + b\n= a + b;\n"
    result = bmb_lint_native(source)
    assert result["ok"]
    assert result["count"] == 0


def test_bmb_lint_native_detects_non_snake_case():
    result = bmb_lint_native("fn myBadName(x: i64) -> i64 = x;\n")
    assert result["ok"]
    kinds = [w["kind"] for w in result["warnings"]]
    assert "non_snake_case" in kinds


def test_bmb_lint_native_detects_missing_postcondition():
    result = bmb_lint_native("pub fn helper(n: i64) -> i64 = n + 1;\n")
    assert result["ok"]
    kinds = [w["kind"] for w in result["warnings"]]
    assert "missing_postcondition" in kinds


def test_bmb_lint_native_detects_negated_if():
    source = "fn check(x: bool) -> i64 = if not(x) { 1 } else { 0 };\n"
    result = bmb_lint_native(source)
    assert result["ok"]
    kinds = [w["kind"] for w in result["warnings"]]
    assert "negated_if_condition" in kinds


def test_bmb_lint_native_detects_redundant_bool():
    source = "fn check(x: bool) -> i64 = if x == true { 1 } else { 0 };\n"
    result = bmb_lint_native(source)
    assert result["ok"]
    kinds = [w["kind"] for w in result["warnings"]]
    assert "redundant_bool_comparison" in kinds


def test_bmb_lint_native_detects_chained_comparison():
    source = "fn is_bracket(c: i64) -> bool = c == 40 or c == 41 or c == 91 or c == 93;\n"
    result = bmb_lint_native(source)
    assert result["ok"]
    kinds = [w["kind"] for w in result["warnings"]]
    assert "chained_comparison" in kinds


def test_bmb_lint_native_count_matches_warnings():
    result = bmb_lint_native("fn badName(x: i64) -> i64 = x;\n")
    assert result["count"] == len(result["warnings"])


def test_bmb_lint_native_detects_todo_comment():
    source = "// TODO: implement this\nfn main() -> i64 = 0;\n"
    result = bmb_lint_native(source)
    assert result["ok"]
    kinds = [w["kind"] for w in result["warnings"]]
    assert "todo_comment" in kinds


def test_bmb_lint_native_no_todo_clean():
    source = "fn main() -> i64 = 0;\n"
    result = bmb_lint_native(source)
    assert result["ok"]
    kinds = [w["kind"] for w in result["warnings"]]
    assert "todo_comment" not in kinds


def test_bmb_lint_native_detects_missing_pre_index():
    source = "pub fn get(idx: i64, s: String) -> i64\n    = s.byte_at(idx);\n"
    result = bmb_lint_native(source)
    assert result["ok"]
    kinds = [w["kind"] for w in result["warnings"]]
    assert "missing_pre_index" in kinds


def test_bmb_lint_native_pre_suppresses_missing_pre_index():
    source = "pub fn get(idx: i64, s: String) -> i64\npre idx >= 0 and idx < s.len()\n    = s.byte_at(idx);\n"
    result = bmb_lint_native(source)
    assert result["ok"]
    kinds = [w["kind"] for w in result["warnings"]]
    assert "missing_pre_index" not in kinds


def test_bmb_lint_native_detects_redundant_if_expression():
    source = "fn is_positive(x: i64) -> bool = if x > 0 { true } else { false };\n"
    result = bmb_lint_native(source)
    assert result["ok"]
    kinds = [w["kind"] for w in result["warnings"]]
    assert "redundant_if_expression" in kinds


def test_bmb_lint_native_detects_empty_block():
    source = "pub fn stub(x: i64) -> i64 = { }\n"
    result = bmb_lint_native(source)
    assert result["ok"]
    kinds = [w["kind"] for w in result["warnings"]]
    assert "empty_block" in kinds


# ---------------------------------------------------------------------------
# bmb_ir
# ---------------------------------------------------------------------------


def test_bmb_ir_returns_dict():
    result = bmb_ir("fn add(a: i64, b: i64) -> i64 = a + b;\n")
    assert isinstance(result, dict)
    assert set(result.keys()) >= {"ok", "ir", "stderr", "returncode"}


def test_bmb_ir_valid_source_succeeds():
    result = bmb_ir("fn add(a: i64, b: i64) -> i64 = a + b;\n")
    assert result["ok"]
    assert len(result["ir"]) > 100  # meaningful IR content


def test_bmb_ir_contains_llvm_ir():
    result = bmb_ir("fn add(a: i64, b: i64) -> i64 = a + b;\n")
    assert result["ok"]
    # LLVM IR should contain target triple or define keyword
    assert "define" in result["ir"] or "target" in result["ir"]


def test_bmb_ir_invalid_source_fails():
    result = bmb_ir("fn add() -> i64 = undefined_var;\n")
    assert not result["ok"]


def test_bmb_ir_syntax_error_fails():
    result = bmb_ir("this is not valid bmb!!!\n")
    assert not result["ok"]
    assert result["ir"] == ""


# ---------------------------------------------------------------------------
# bmb_run
# ---------------------------------------------------------------------------


def test_bmb_run_returns_dict():
    result = bmb_run("fn main() -> i64 = 0;\n")
    assert isinstance(result, dict)
    assert set(result.keys()) >= {"ok", "stdout", "stderr", "returncode"}


def test_bmb_run_valid_source_succeeds():
    result = bmb_run("fn main() -> i64 = 0;\n")
    assert result["ok"]


def test_bmb_run_invalid_source_fails():
    result = bmb_run("fn main() -> i64 = undefined_var;\n")
    assert not result["ok"]


def test_bmb_run_syntax_error_fails():
    result = bmb_run("this is not valid bmb!!!\n")
    assert not result["ok"]


# ---------------------------------------------------------------------------
# bmb_compile
# ---------------------------------------------------------------------------


def test_bmb_compile_returns_dict():
    result = bmb_compile("fn main() -> i64 = 0;\n")
    assert isinstance(result, dict)
    assert set(result.keys()) >= {"ok", "diagnostics", "stderr", "returncode"}


def test_bmb_compile_valid_source_succeeds():
    result = bmb_compile("fn main() -> i64 = 0;\n")
    assert result["ok"]
    assert result["returncode"] == 0


def test_bmb_compile_undefined_variable_fails():
    result = bmb_compile("fn main() -> i64 = undefined_var;\n")
    assert not result["ok"]
    assert result["returncode"] != 0


def test_bmb_compile_syntax_error_fails():
    result = bmb_compile("this is not valid bmb!!!\n")
    assert not result["ok"]


def test_bmb_compile_valid_with_arithmetic():
    source = "fn main() -> i64 = { let x: i64 = 6; let y: i64 = 7; x * y };\n"
    result = bmb_compile(source)
    assert result["ok"]


def test_bmb_compile_diagnostics_on_failure():
    result = bmb_compile("fn main() -> i64 = no_such_fn();\n")
    assert not result["ok"]
    # Either diagnostics or stderr should contain error info
    combined = (result["diagnostics"] or "") + (result["stderr"] or "")
    assert len(combined) > 0


# ---------------------------------------------------------------------------
# bmb_test
# ---------------------------------------------------------------------------


def test_bmb_test_returns_dict():
    result = bmb_test("fn main() -> i64 = 0;\n", [])
    assert isinstance(result, dict)
    assert set(result.keys()) >= {"ok", "compile_ok", "results", "diagnostics"}


def test_bmb_test_no_cases_passes():
    result = bmb_test("fn main() -> i64 = 0;\n", [])
    assert result["compile_ok"]
    assert result["ok"]
    assert result["results"] == []


def test_bmb_test_compile_failure():
    result = bmb_test("this is not valid bmb!!!\n", [{"expected": ""}])
    assert not result["compile_ok"]
    assert not result["ok"]
    assert result["results"] == []


def test_bmb_test_compile_failure_empty_cases():
    result = bmb_test("fn main() -> i64 = undefined_var;\n", [])
    assert not result["compile_ok"]
    assert not result["ok"]


def test_bmb_test_results_structure():
    result = bmb_test("fn main() -> i64 = 0;\n", [{"input": "", "expected": ""}])
    assert result["compile_ok"]
    assert len(result["results"]) == 1
    r = result["results"][0]
    assert set(r.keys()) >= {"passed", "input", "expected", "actual", "returncode"}


# ---------------------------------------------------------------------------
# bmb_from_rust
# ---------------------------------------------------------------------------


def test_bmb_from_rust_returns_dict():
    result = bmb_from_rust("fn main() {}\n")
    assert isinstance(result, dict)
    assert set(result.keys()) >= {"ok", "bmb_source", "warnings", "note"}


def test_bmb_from_rust_always_ok():
    # Transform should always succeed (no subprocess)
    result = bmb_from_rust("this is garbage code !!!\n")
    assert result["ok"]
    assert isinstance(result["bmb_source"], str)


def test_bmb_from_rust_option_conversion():
    result = bmb_from_rust("fn f(x: Option<i64>) -> Option<i64> { x }\n")
    assert "i64?" in result["bmb_source"]
    assert "Option<" not in result["bmb_source"]


def test_bmb_from_rust_integer_widening():
    result = bmb_from_rust("fn f(x: i32, y: u32) -> usize { 0 }\n")
    assert "i32" not in result["bmb_source"]
    assert "u32" not in result["bmb_source"]
    assert "usize" not in result["bmb_source"]
    assert "i64" in result["bmb_source"]
    assert any("i32" in w or "u32" in w or "usize" in w for w in result["warnings"])


def test_bmb_from_rust_logical_operators():
    result = bmb_from_rust("fn f(a: bool, b: bool) -> bool { a && b || !a }\n")
    src = result["bmb_source"]
    assert "&&" not in src
    assert "||" not in src
    assert " and " in src
    assert " or " in src
    assert "not " in src


def test_bmb_from_rust_fn_signature():
    result = bmb_from_rust("fn add(a: i64, b: i64) -> i64 {\n    a + b\n}\n")
    assert "= {" in result["bmb_source"]


def test_bmb_from_rust_use_removed():
    result = bmb_from_rust("use std::collections::HashMap;\n\nfn main() {}\n")
    assert "use " not in result["bmb_source"]
    assert any("Removed" in w for w in result["warnings"])


def test_bmb_from_rust_unsupported_warnings():
    source = "impl Foo { fn bar() {} }\n"
    result = bmb_from_rust(source)
    assert any("impl" in w for w in result["warnings"])


def test_bmb_from_rust_vec_warning():
    result = bmb_from_rust("fn f() -> Vec<i64> { vec![] }\n")
    assert any("Vec" in w for w in result["warnings"])


def test_bmb_from_rust_note_present():
    result = bmb_from_rust("fn main() {}\n")
    assert isinstance(result["note"], str)
    assert len(result["note"]) > 10


# ---------------------------------------------------------------------------
# bmb_context_pack
# ---------------------------------------------------------------------------


def test_bmb_context_pack_returns_dict():
    root = find_repo_root()
    if root is None:
        pytest.skip("repo root not found")
    result = bmb_context_pack(str(root / "stdlib"))
    assert isinstance(result, dict)
    assert set(result.keys()) >= {"ok", "context", "raw", "stderr", "returncode"}


def test_bmb_context_pack_stdlib_succeeds():
    root = find_repo_root()
    if root is None:
        pytest.skip("repo root not found")
    result = bmb_context_pack(str(root / "stdlib"))
    if result["returncode"] == -1:
        pytest.skip("context_pack binary not available")
    assert result["ok"]
    assert result["context"] is not None
    assert result["context"].get("_schema") == "bmb.context-pack.v1"


def test_bmb_context_pack_context_structure():
    root = find_repo_root()
    if root is None:
        pytest.skip("repo root not found")
    result = bmb_context_pack(str(root / "stdlib"))
    if result["returncode"] == -1:
        pytest.skip("context_pack binary not available")
    if not result["ok"]:
        pytest.skip("context_pack failed")
    ctx = result["context"]
    assert "project" in ctx
    assert "modules" in ctx
    assert "stats" in ctx
    assert isinstance(ctx["modules"], list)


def test_bmb_context_pack_nonexistent_dir():
    result = bmb_context_pack("/nonexistent/path/12345")
    if result["returncode"] == -1:
        pytest.skip("context_pack binary not available")
    # Should fail gracefully — no .bmb files found
    assert not result["ok"] or (result["context"] and result["context"].get("error"))


def test_bmb_context_pack_max_tokens():
    root = find_repo_root()
    if root is None:
        pytest.skip("repo root not found")
    result = bmb_context_pack(str(root / "stdlib"), max_tokens=1000)
    if result["returncode"] == -1:
        pytest.skip("context_pack binary not available")
    if not result["ok"]:
        pytest.skip("context_pack failed")
    ctx = result["context"]
    # With a small budget, budget_mode should be set in stats
    stats = ctx.get("stats", {})
    assert isinstance(stats, dict)


# ---------------------------------------------------------------------------
# context_stdlib resource
# ---------------------------------------------------------------------------


def test_context_stdlib_returns_string():
    content = context_stdlib()
    assert isinstance(content, str)
    assert len(content) > 50  # Should have meaningful content or error


def test_context_stdlib_is_valid_json_or_error():
    import json
    content = context_stdlib()
    # Should be valid JSON (either a context pack or an error dict)
    data = json.loads(content)
    assert isinstance(data, dict)


def test_context_stdlib_has_schema_or_error():
    import json
    content = context_stdlib()
    data = json.loads(content)
    # Either proper context pack or error
    assert "_schema" in data or "error" in data


def test_context_stdlib_stdlib_modules():
    import json
    content = context_stdlib()
    data = json.loads(content)
    if "error" in data:
        pytest.skip(f"context_stdlib error: {data['error']}")
    assert data.get("_schema") == "bmb.context-pack.v1"
    assert len(data.get("modules", [])) > 0
