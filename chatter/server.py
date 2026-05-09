"""Chatter MCP server entry point.

Implements Track N Phase 2 tools, resources, and prompts per README.md:

  - tools:     bmb_check, bmb_verify, bmb_spec_lookup, bmb_lint, bmb_example,
               bmb_lint_explain (Track Q: AI-friendly lint explanations),
               bmb_compile, bmb_test, bmb_from_rust (Track N Phase 2d)
  - resources: bmb://spec/full, bmb://spec/quick-reference, bmb://spec/rust-diff
  - prompts:   bmb_implement, bmb_add_contracts, bmb_optimize
"""

from __future__ import annotations

import re
import subprocess
import sys
import tempfile
from pathlib import Path

from mcp.server.fastmcp import FastMCP

from .bmb_cli import (
    BmbBinaryNotFound,
    find_bmb_binary,
    find_repo_root,
    run_bmb,
    run_context_pack,
)


mcp = FastMCP("bmb-chatter")

# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------


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


@mcp.tool()
def bmb_verify(source: str, filename: str = "snippet.bmb") -> dict:
    """Verify contracts in a BMB source snippet using the Z3 SMT solver.

    Checks that all pre/post conditions and invariants are satisfiable and
    consistent. Requires Z3 to be installed and reachable by the bmb binary.

    Args:
        source: BMB source code containing @pre/@post annotations.
        filename: Display name for diagnostics (default: snippet.bmb).

    Returns a dict with keys:
        ok: bool — True if all contracts verified successfully
        diagnostics: structured JSON verification results from bmb
        stderr: any error stream content
        returncode: bmb exit code
    """
    with tempfile.TemporaryDirectory(prefix="chatter-verify-") as tmp:
        tmp_path = Path(tmp) / filename
        tmp_path.write_text(source, encoding="utf-8")
        result = run_bmb(["verify", str(tmp_path)], timeout=60.0)
    return {
        "ok": result.ok,
        "diagnostics": result.stdout,
        "stderr": result.stderr,
        "returncode": result.returncode,
    }


@mcp.tool()
def bmb_spec_lookup(topic: str, max_sections: int = 3) -> dict:
    """Search the BMB language specification for sections relevant to a topic.

    Splits docs/SPECIFICATION.md by level-2 headings and returns sections
    whose text contains the query keyword (case-insensitive).

    Args:
        topic: Keyword or phrase to search for (e.g. "contracts", "generics").
        max_sections: Maximum number of sections to return (default: 3).

    Returns a dict with:
        ok: bool
        sections: list of matching section strings (heading + content)
        total_matches: total number of spec sections containing the topic
    """
    root = find_repo_root()
    if root is None:
        return {"ok": False, "sections": [], "total_matches": 0,
                "error": "BMB repository root not found"}
    spec = root / "docs" / "SPECIFICATION.md"
    if not spec.exists():
        return {"ok": False, "sections": [], "total_matches": 0,
                "error": f"{spec} not found"}

    content = spec.read_text(encoding="utf-8")
    # Split at newlines immediately followed by a level-2+ heading marker
    parts = re.split(r"\n(?=##)", content)
    query = topic.lower()
    matches = [p.strip() for p in parts if query in p.lower()]

    return {
        "ok": True,
        "sections": matches[:max_sections],
        "total_matches": len(matches),
    }


@mcp.tool()
def bmb_lint(source: str, filename: str = "snippet.bmb") -> dict:
    """Run the BMB linter on a source snippet to check style and conventions.

    Reports warnings such as missing pre/post contracts, long lines, and
    other style issues. Complements bmb_check (which does type-checking).

    Args:
        source: BMB source code as a string.
        filename: Display name for diagnostics (default: snippet.bmb).

    Returns a dict with keys:
        ok: bool — True if lint succeeds (exit 0), regardless of warning count
        diagnostics: machine-format JSON warnings from bmb lint
        stderr: any error stream content
        returncode: bmb exit code
    """
    with tempfile.TemporaryDirectory(prefix="chatter-lint-") as tmp:
        tmp_path = Path(tmp) / filename
        tmp_path.write_text(source, encoding="utf-8")
        result = run_bmb(["lint", str(tmp_path)])
    return {
        "ok": result.ok,
        "diagnostics": result.stdout,
        "stderr": result.stderr,
        "returncode": result.returncode,
    }


@mcp.tool()
def bmb_example(concept: str, max_examples: int = 2) -> dict:
    """Get example BMB code for a concept or pattern.

    Searches docs/tutorials/BY_EXAMPLE.md for sections matching the concept
    keyword (case-insensitive). Returns matching sections including code blocks.

    Args:
        concept: Concept to find examples for (e.g. "contracts", "loops",
                 "struct", "string").
        max_examples: Maximum number of example sections to return (default: 2).

    Returns a dict with:
        ok: bool
        examples: list of matching section strings (heading + content + code)
        total_matches: total number of sections containing the concept
    """
    root = find_repo_root()
    if root is None:
        return {"ok": False, "examples": [], "total_matches": 0,
                "error": "BMB repository root not found"}
    tutorial = root / "docs" / "tutorials" / "BY_EXAMPLE.md"
    if not tutorial.exists():
        return {"ok": False, "examples": [], "total_matches": 0,
                "error": f"{tutorial} not found"}

    content = tutorial.read_text(encoding="utf-8")
    parts = re.split(r"\n(?=##)", content)
    query = concept.lower()
    matches = [p.strip() for p in parts if query in p.lower()]

    return {
        "ok": True,
        "examples": matches[:max_examples],
        "total_matches": len(matches),
    }


@mcp.tool()
def bmb_run(source: str, filename: str = "snippet.bmb", stdin: str = "") -> dict:
    """Run a BMB source snippet using the tree-walking interpreter.

    Faster than bmb_compile (no LLVM pass) — useful for quick evaluation,
    logic checks, and testing pure-computation snippets. Does not support
    all language features that compilation does (e.g. SIMD, certain casts).

    Args:
        source: BMB source code as a string.
        filename: Display name for diagnostics (default: snippet.bmb).
        stdin: String to supply on the interpreter's standard input (default "").

    Returns a dict with keys:
        ok: bool — True if interpreter ran successfully (exit 0)
        stdout: interpreter standard output
        stderr: any error stream content
        returncode: bmb exit code
    """
    import subprocess as _sub

    with tempfile.TemporaryDirectory(prefix="chatter-run-") as tmp:
        tmp_path = Path(tmp) / filename
        tmp_path.write_text(source, encoding="utf-8")
        binary = find_bmb_binary()
        proc = _sub.run(
            [str(binary), "run", str(tmp_path)],
            input=stdin,
            capture_output=True,
            text=True,
            timeout=30.0,
            check=False,
        )
    return {
        "ok": proc.returncode == 0,
        "stdout": proc.stdout,
        "stderr": proc.stderr,
        "returncode": proc.returncode,
    }


@mcp.tool()
def bmb_compile(source: str, filename: str = "snippet.bmb", optimize: bool = True) -> dict:
    """Compile a BMB source snippet to a native executable.

    Builds the source using 'bmb build' and reports whether compilation
    succeeded. The compiled binary is not retained after this call; use
    bmb_test to compile-and-run in a single step.

    Args:
        source: BMB source code as a string.
        filename: Display name used for the temporary source file (default: snippet.bmb).
        optimize: Whether to request an optimized build (default: True).
                  Currently passed as-is; the bmb compiler uses its default opt level.

    Returns a dict with keys:
        ok: bool — True if compilation succeeded
        diagnostics: stdout from bmb build (JSON build_success or error)
        stderr: any error stream content
        returncode: bmb exit code
    """
    exe_suffix = ".exe" if sys.platform == "win32" else ""
    stem = Path(filename).stem
    with tempfile.TemporaryDirectory(prefix="chatter-compile-") as tmp:
        src_path = Path(tmp) / filename
        out_path = Path(tmp) / (stem + exe_suffix)
        src_path.write_text(source, encoding="utf-8")
        result = run_bmb(["build", str(src_path), "-o", str(out_path)], timeout=60.0)
    return {
        "ok": result.ok,
        "diagnostics": result.stdout,
        "stderr": result.stderr,
        "returncode": result.returncode,
    }


@mcp.tool()
def bmb_test(
    source: str,
    test_cases: list,
    filename: str = "snippet.bmb",
) -> dict:
    """Compile a BMB source snippet and run test cases against it.

    Each test case is a dict with:
        input:    string to supply on stdin (optional, default "")
        expected: expected stdout output (default "")

    Compiles once, then runs the binary for each test case in sequence.
    The compiled binary is removed after the call.

    Args:
        source: BMB source code as a string.
        test_cases: List of test-case dicts (see above).
        filename: Display name for the temporary source file (default: snippet.bmb).

    Returns a dict with keys:
        ok: bool — True if all test cases passed (False if compile failed)
        compile_ok: bool
        diagnostics: compilation stdout/stderr
        results: list of per-test dicts, each with:
            passed: bool
            input: str
            expected: str
            actual: str
            returncode: int
    """
    exe_suffix = ".exe" if sys.platform == "win32" else ""
    stem = Path(filename).stem
    with tempfile.TemporaryDirectory(prefix="chatter-test-") as tmp:
        src_path = Path(tmp) / filename
        out_path = Path(tmp) / (stem + exe_suffix)
        src_path.write_text(source, encoding="utf-8")

        compile_result = run_bmb(
            ["build", str(src_path), "-o", str(out_path)], timeout=60.0
        )
        if not compile_result.ok:
            return {
                "ok": False,
                "compile_ok": False,
                "diagnostics": compile_result.stdout + compile_result.stderr,
                "results": [],
            }

        results = []
        all_passed = True
        for case in test_cases:
            input_data = case.get("input", "")
            expected = case.get("expected", "")
            try:
                proc = subprocess.run(
                    [str(out_path)],
                    input=input_data,
                    capture_output=True,
                    text=True,
                    timeout=10.0,
                )
                actual = proc.stdout
                passed = actual == expected
            except subprocess.TimeoutExpired:
                actual = ""
                passed = False
                proc = None
            all_passed = all_passed and passed
            results.append(
                {
                    "passed": passed,
                    "input": input_data,
                    "expected": expected,
                    "actual": actual,
                    "returncode": proc.returncode if proc is not None else -1,
                }
            )

    return {
        "ok": all_passed,
        "compile_ok": True,
        "diagnostics": compile_result.stdout,
        "results": results,
    }


@mcp.tool()
def bmb_context_pack(root: str, max_tokens: int = 0) -> dict:
    """Generate a context pack for a BMB project directory.

    Runs the context_pack native binary to scan all .bmb files under `root`
    and produce a structured JSON summary of public exports, contracts, and
    module structure. Suitable for feeding to an LLM as project context.

    The context-pack v1 schema:
        _schema: "bmb.context-pack.v1"
        project: {name, root}
        modules: [{path, kind, exports: [{name, kind, signature, contract}], lines}]
        stats: {total_modules, total_exports, estimated_tokens}

    When max_tokens is set and the pack exceeds the budget, contract details are
    stripped and stats gains "budget_mode" and "budget_tokens" fields.

    Args:
        root: Path to the BMB project directory to scan (absolute preferred).
        max_tokens: Token budget — strip contracts if over budget (0 = no limit).

    Returns a dict with keys:
        ok: bool
        context: parsed context-pack dict (or None on failure)
        raw: raw stdout from context_pack binary
        stderr: any error stream content
        returncode: exit code (-1 if binary not found)
    """
    import json as _json
    from pathlib import Path as _Path

    abs_root = str(_Path(root).resolve())
    result = run_context_pack(abs_root, max_tokens=max_tokens)

    context = None
    if result.ok and result.stdout:
        try:
            context = _json.loads(result.stdout)
        except _json.JSONDecodeError:
            pass

    return {
        "ok": result.ok,
        "context": context,
        "raw": result.stdout,
        "stderr": result.stderr,
        "returncode": result.returncode,
    }


def _transform_rust_to_bmb(source: str) -> tuple[str, list[str]]:
    """Heuristic Rust-to-BMB text transformation.

    Applies common substitutions and detects unsupported constructs.
    The output is a best-effort starting point — review before use.
    Returns (bmb_source, warnings).
    """
    warnings: list[str] = []
    result = source

    # 1. Remove `use` statements — BMB has no module imports
    def _remove_use(m: re.Match) -> str:
        warnings.append(
            f"Removed: `{m.group().strip()}` — BMB has no module imports"
        )
        return ""

    result = re.sub(r"^[ \t]*use [^;]+;\n?", _remove_use, result, flags=re.MULTILINE)

    # 2. Integer type widening → i64 (BMB primary integer type)
    _INT_TYPES = ("i32", "u32", "usize", "isize", "u64", "u8", "i8", "i16", "u16", "i128")
    for rust_type in _INT_TYPES:
        if re.search(rf"\b{rust_type}\b", result):
            result = re.sub(rf"\b{rust_type}\b", "i64", result)
            warnings.append(f"Widened `{rust_type}` → `i64` (BMB uses i64 for integers)")

    # 3. &str → String
    if re.search(r"\b&str\b", result):
        result = re.sub(r"\b&str\b", "String", result)
        warnings.append("Converted `&str` → `String`")

    # 4. Option<T> → T?
    result = re.sub(r"\bOption<([^>]+)>", lambda m: m.group(1).strip() + "?", result)

    # 5. Logical operators
    result = result.replace("&&", " and ")
    result = result.replace("||", " or ")

    # 6. Logical NOT: `!expr` → `not expr` (skip `!=`)
    result = re.sub(r"!(?!=)", "not ", result)

    # 7. Function signatures: `fn name(…) {` → `fn name(…) = {`
    #    Per-line, only on lines starting with optional ws + `fn` or `pub fn`
    result = re.sub(
        r"^([ \t]*(?:pub\s+)?(?:async\s+)?fn\s+[^{]+)\{",
        r"\1= {",
        result,
        flags=re.MULTILINE,
    )

    # 8. `return expr;` → `expr` (last-expression-is-return in BMB)
    result = re.sub(r"\breturn\s+([^;]+);", r"\1", result)

    # 9. Detect unsupported constructs (warn but don't transform)
    _unsupported = [
        (r"\bimpl\b", "Unsupported: `impl` blocks — BMB has no trait system"),
        (r"for\s+\w+\s+in\s+", "Unsupported: `for…in` loops — use `while` or recursion"),
        (r"\bVec<", "Unsupported: `Vec<T>` — use fixed arrays `[T; N]`"),
        (r"\bNone\b", "Unsupported: `None` literal — BMB uses nullable T? but no None keyword"),
        (r"\bSome\(", "Note: `Some(x)` — BMB uses `x` directly (T? is nullable, not Option<T>)"),
        (r"let\s*\(", "Unsupported: tuple destructuring `let (a, b) = …` — not in BMB"),
        (r"\|\s*\w+\s*\|", "Unsupported: closures `|x| …` — BMB has no first-class functions"),
        (r"_\s*=>", "Unsupported: `_ =>` wildcard match arm — use explicit cases in BMB"),
        (r"::", "Note: `::` static calls — not in BMB; call functions directly"),
        (r"\btrait\b", "Unsupported: `trait` definitions — BMB has no trait system"),
        (r"'[a-z]\b", "Note: Rust lifetime annotations — not needed in BMB"),
        (r"\bBox<", "Unsupported: `Box<T>` — BMB uses ownership without heap boxing"),
        (r"\bRc<|\bArc<", "Unsupported: `Rc`/`Arc` — BMB ownership model differs"),
        (r"\basync\s+fn\b|\bawait\b", "Unsupported: async/await — BMB has no async support"),
    ]
    for pattern, msg in _unsupported:
        if re.search(pattern, result):
            warnings.append(msg)

    return result, warnings


@mcp.tool()
def bmb_from_rust(rust_source: str) -> dict:
    """Convert Rust source code to idiomatic BMB (best-effort heuristic).

    Applies common syntactic transformations and flags constructs that have
    no direct BMB equivalent. The output is a starting point — it will
    almost certainly need manual review and adjustment.

    Transformations applied:
    - `use` statements removed (no module imports in BMB)
    - Integer types widened to `i64` (i32, u32, usize, …)
    - `&str` → `String`
    - `Option<T>` → `T?`
    - `&&` / `||` / `!` → `and` / `or` / `not`
    - Function bodies: `fn f() -> T {` → `fn f() -> T = {`
    - `return expr;` → `expr` (BMB uses last-expression)

    Unsupported constructs are flagged in the `warnings` list.

    Args:
        rust_source: Rust source code as a string.

    Returns a dict with keys:
        ok: bool — always True (transformation always produces output)
        bmb_source: transformed BMB source (best-effort, may not compile)
        warnings: list of transformation notes and unsupported-construct warnings
        note: reminder that output requires manual review
    """
    bmb_source, warnings = _transform_rust_to_bmb(rust_source)
    return {
        "ok": True,
        "bmb_source": bmb_source,
        "warnings": warnings,
        "note": (
            "This is a heuristic transformation. The output is a starting point "
            "and will likely require manual fixes. Use bmb_check to validate."
        ),
    }


# Explanation map for bmb lint warning kinds.
# Each entry: (explanation, fix_suggestion)
_LINT_EXPLANATIONS: dict[str, tuple[str, str]] = {
    "missing_postcondition": (
        "A missing post-condition means the compiler cannot prove what this function guarantees "
        "to its callers. Post-conditions enable callers to skip redundant checks and allow the "
        "verifier to eliminate bounds checks downstream.",
        "Add `post <condition>` after the function signature. Example: "
        "`post result >= 0` for a function returning a non-negative index.",
    ),
    "chained_comparison": (
        "Three or more chained equality/inequality comparisons on the same value are often better "
        "expressed as a match expression. LLVM may aggregate them into a jump table, which can "
        "be slower than separate comparisons for sparse values.",
        "Replace `c == 91 or c == 123 or c == 125` with a match expression or split into "
        "separate conditions if the values are semantically unrelated.",
    ),
    "unused_binding": (
        "A variable was declared with `let` but never read. In BMB, unused bindings may indicate "
        "a logic error or a missing step in a computation.",
        "Either use the variable or prefix it with `_` (e.g. `let _unused = ...`) to signal "
        "intentional discard. Remove it entirely if it serves no purpose.",
    ),
    "non_snake_case": (
        "BMB uses snake_case for function and variable names by convention. "
        "Deviating from this convention reduces readability and may confuse tooling.",
        "Rename the identifier to snake_case. Example: `myFunction` → `my_function`.",
    ),
    "unused_function": (
        "A function is declared but never called within the file. It may be dead code or "
        "a function intended to be exported but missing a `pub` modifier.",
        "Remove the function if it is truly unused. Add `pub` if it is intended for external use. "
        "Check for typos in call sites.",
    ),
    "negated_if_condition": (
        "A negated condition (`if not(x)`) often indicates the if/else branches should be swapped. "
        "Positive conditions are easier to read and verify.",
        "Swap the if/else branches and remove the negation. "
        "Example: `if not(x) { a } else { b }` → `if x { b } else { a }`.",
    ),
    "redundant_bool_comparison": (
        "Comparing a boolean to `true` or `false` is redundant and adds noise. "
        "`x == true` is identical to `x`; `x == false` is identical to `not x`.",
        "Remove the comparison: replace `x == true` with `x`, and `x == false` with `not x`.",
    ),
    "redundant_if_expression": (
        "An if-expression that returns `true` in one branch and `false` in the other can be "
        "replaced by the condition itself. This eliminates unnecessary branching.",
        "Replace `if cond { true } else { false }` with `cond`, and "
        "`if cond { false } else { true }` with `not cond`.",
    ),
    "semantic_duplication": (
        "Similar or identical code patterns appear in multiple places. Duplication increases "
        "maintenance burden and the risk of inconsistent bug fixes.",
        "Extract the shared logic into a helper function and call it from both sites.",
    ),
    "shadow_binding": (
        "A `let` binding uses the same name as an outer variable, silently hiding it. "
        "This can cause subtle bugs where the wrong value is used.",
        "Rename one of the bindings to a distinct name to make scope explicit.",
    ),
    "unreachable_code": (
        "Code appears after a `break`, `return`, or other unconditional control transfer. "
        "This code will never execute and may indicate a logic error.",
        "Remove the unreachable code or restructure the control flow so all branches are reachable.",
    ),
    "unused_return_value": (
        "A function returns a value that is not captured. In BMB, every expression has a value; "
        "ignoring a return value may indicate a missing assignment or a logic error.",
        "Capture the return value with `let _name = expr;` if it is intentionally discarded, "
        "or assign it to a meaningful variable if it should be used.",
    ),
}


@mcp.tool()
def bmb_lint_explain(source: str, filename: str = "snippet.bmb") -> dict:
    """Run BMB lint and return diagnostics enriched with explanations and fix suggestions.

    Same as bmb_lint but each warning is parsed and augmented with human- and
    AI-readable context: why the warning matters and how to address it.

    Args:
        source: BMB source code as a string.
        filename: Display name for diagnostics (default: snippet.bmb).

    Returns a dict with keys:
        ok: bool — True if lint runs successfully (exit 0)
        warnings: list of dicts, each with original lint fields plus:
            explanation: why this warning matters for correctness/performance
            fix_suggestion: how to address it
        count: number of warnings
        stderr: any error stream content
    """
    import json as _json

    with tempfile.TemporaryDirectory(prefix="chatter-lint-") as tmp:
        tmp_path = Path(tmp) / filename
        tmp_path.write_text(source, encoding="utf-8")
        result = run_bmb(["lint", str(tmp_path)])

    warnings = []
    for line in result.stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            entry = _json.loads(line)
        except _json.JSONDecodeError:
            continue
        if entry.get("type") == "warning":
            kind = entry.get("kind", "")
            explanation, fix = _LINT_EXPLANATIONS.get(kind, ("", ""))
            entry["explanation"] = explanation
            entry["fix_suggestion"] = fix
            warnings.append(entry)

    return {
        "ok": result.ok,
        "warnings": warnings,
        "count": len(warnings),
        "stderr": result.stderr,
    }


# ---------------------------------------------------------------------------
# Resources
# ---------------------------------------------------------------------------

_QUICK_REFERENCE = """\
# BMB Quick Reference

## Function syntax
```
fn name(param: Type) -> ReturnType = expression;

// Block body (semicolons between statements, last expr is return value)
fn name(param: Type) -> ReturnType = {
    let x = expr;
    x + 1
};
```

## Contracts (pre/post conditions)
```
fn divide(a: i64, b: i64) -> i64 =
pre b != 0
post result * b == a
    a / b;
```

## Type system
- `i64`, `f64`, `bool`, `String`, `[T; N]` (fixed arrays), `T?` (nullable)
- `own T` — owned value (moves), `&T` — shared ref, `&mut T` — mutable ref
- No implicit coercions; use explicit `as i64`, `as f64`, etc.

## Common gotchas vs Rust
- `T?` is NOT `Option<T>` — it is a nullable pointer type
- `band`, `bor`, `bxor` for bitwise AND/OR/XOR (not `&`, `|`, `^`)
- `and`, `or`, `not` for logical operators
- No tuple destructuring: `let (a, b) = ...` is NOT supported
- No underscore patterns in match: `_ => ...` — use `else` or explicit cases
- No `::` static method calls: `Type::method()` is NOT supported
- Contracts are mandatory for performance-critical paths (enables bound-check elim)

## Stdlib highlights
- `stdlib/string/` — string operations
- `stdlib/array/` — array utilities
- `stdlib/io/` — I/O (print_str, read_file, etc.)
- `stdlib/json/` — JSON parsing and serialization

## Performance annotations
- `@inline` — force inline
- `@noinline` — prevent inlining
- `@pure` — pure function (no side effects, enables CSE/vectorization)
"""

_RUST_DIFF = """\
# BMB vs Rust: Key Differences

## Design philosophy
| Aspect | Rust | BMB |
|--------|------|-----|
| Primary goal | Memory safety | Zero-runtime overhead |
| Mechanism | Ownership + borrow checker | Compile-time contract proofs |
| Safety | First-class goal | Consequence of proofs |

## Syntax differences
| Feature | Rust | BMB |
|---------|------|-----|
| Nullable | Option<T> | T? |
| Bitwise AND | a & b | a band b |
| Bitwise OR | a | b | a bor b |
| Logical AND | a && b | a and b |
| Logical OR | a || b | a or b |
| Logical NOT | !a | not a |
| Static method | Type::method() | not supported |
| Tuple destructuring | let (a, b) = ... | not supported |

## Contracts (BMB-specific)
```
// BMB: pre/post conditions replace runtime assertions
fn sqrt(x: f64) -> f64 =
pre x >= 0.0
post result >= 0.0
    // ...implementation...

// Rust equivalent uses debug_assert! at runtime
fn sqrt(x: f64) -> f64 {
    debug_assert!(x >= 0.0);
    // ...
}
```

## Memory model
| Feature | Rust | BMB |
|---------|------|-----|
| Ownership | T (owned) | own T |
| Shared ref | &T | &T |
| Mut ref | &mut T | &mut T |
| Lifetime annotations | Explicit 'a | Inferred |

## What BMB lacks (vs Rust)
- Trait system (no impl blocks, no trait objects)
- Closures / first-class functions
- Generics with bounds (partial support)
- unsafe blocks
- Macros
- Async/await
"""


@mcp.resource("bmb://spec/full")
def spec_full() -> str:
    """Complete BMB language specification from docs/SPECIFICATION.md."""
    root = find_repo_root()
    if root is None:
        return "Error: BMB repository root not found."
    spec = root / "docs" / "SPECIFICATION.md"
    if not spec.exists():
        return f"Error: {spec} not found."
    return spec.read_text(encoding="utf-8")


@mcp.resource("bmb://spec/quick-reference")
def spec_quick_reference() -> str:
    """Concise BMB cheatsheet — syntax, gotchas, contracts, stdlib highlights."""
    return _QUICK_REFERENCE


@mcp.resource("bmb://spec/rust-diff")
def spec_rust_diff() -> str:
    """BMB vs Rust differences — philosophy, syntax, memory model, contracts."""
    return _RUST_DIFF


@mcp.resource("bmb://context/stdlib")
def context_stdlib() -> str:
    """Context pack for the BMB standard library — all public exports and contracts.

    Returns context-pack v1 JSON listing every public function, type, and
    constant in stdlib/ with their signatures and pre/post contracts.
    Use this to find available stdlib functions before writing BMB code.
    """
    import json as _json

    root = find_repo_root()
    if root is None:
        return _json.dumps({"error": "BMB repository root not found"})
    stdlib_root = root / "stdlib"
    if not stdlib_root.is_dir():
        return _json.dumps({"error": f"{stdlib_root} directory not found"})

    result = run_context_pack(str(stdlib_root))
    if not result.ok:
        return _json.dumps({"error": result.stderr or "context_pack failed"})
    return result.stdout


# ---------------------------------------------------------------------------
# Prompts
# ---------------------------------------------------------------------------


@mcp.prompt()
def bmb_implement(
    function_description: str,
    include_contracts: bool = True,
) -> str:
    """Prompt template for implementing a BMB function with optional contracts.

    Args:
        function_description: Plain-language description of what the function does.
        include_contracts: Whether to request pre/post contract annotations.
    """
    contracts_hint = (
        "\n\nInclude pre/post contract annotations for all non-trivial invariants. "
        "Contracts enable the compiler to eliminate runtime bounds checks."
        if include_contracts
        else ""
    )
    return (
        f"Implement a BMB function that {function_description}."
        f"{contracts_hint}\n\n"
        "Requirements:\n"
        "- Use BMB syntax (not Rust): `and`/`or`/`not` for logical ops, "
        "`band`/`bor`/`bxor` for bitwise\n"
        "- No tuple destructuring, no `::` static calls, no `Option<T>` (use `T?`)\n"
        "- Return type must be explicit\n"
        "- Use `let mut` only for variables that need mutation\n"
        "- Expressions are values — no explicit `return` needed\n"
    )


@mcp.prompt()
def bmb_add_contracts(source: str) -> str:
    """Prompt template for adding pre/post contracts to existing BMB code.

    Args:
        source: Existing BMB source code to annotate.
    """
    return (
        "Add pre/post contract annotations to the following BMB code. "
        "For each function:\n"
        "1. Add `pre <condition>` lines for input invariants that allow "
        "the compiler to eliminate runtime checks\n"
        "2. Add `post <condition>` lines for output guarantees that callers can rely on\n"
        "3. Focus on: non-null pointers, array bounds, numeric ranges, "
        "non-empty strings\n\n"
        f"```bmb\n{source}\n```\n\n"
        "Return the annotated source. Do not change the function logic."
    )


@mcp.prompt()
def bmb_optimize(source: str, target: str = "speed") -> str:
    """Prompt template for optimizing BMB code for performance.

    Args:
        source: BMB source code to optimize.
        target: Optimization target — "speed" (default) or "size".
    """
    target_hint = (
        "Optimize for maximum execution speed. "
        "Add contracts to eliminate runtime checks. "
        "Consider `@inline` for hot paths. "
        "Avoid unnecessary allocations."
        if target == "speed"
        else "Optimize for binary size. Prefer `@noinline` for large functions. "
        "Share common subexpressions."
    )
    return (
        f"Optimize the following BMB code. {target_hint}\n\n"
        f"```bmb\n{source}\n```\n\n"
        "Explain each optimization and its performance impact."
    )


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


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
