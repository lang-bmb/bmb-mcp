# Chatter

> **MCP server for the BMB programming language**

Chatter enables AI models to generate high-quality BMB code by providing real-time access to language specifications, compilation feedback, and contract verification.

> **Implementation status (2026-05-01, Cycle 2524):** Python scaffold lives in `chatter/`. Node.js packaging in this README is the original design — superseded by the Python implementation while M2 Track N matures. Current capabilities:
> - ✅ Tool: `bmb_check` (subprocess to `bmb check`)
> - ⏳ Tools: `bmb_verify`, `bmb_compile`, `bmb_test`, `bmb_example`, `bmb_spec_lookup`, `bmb_from_rust`
> - ⏳ Resources: `bmb://spec/*`, `bmb://examples/*`, `bmb://stdlib/*`
> - ⏳ Prompts: `bmb_implement`, `bmb_add_contracts`, `bmb_optimize`
>
> Long-term (M3+) the implementation moves to BMB itself per the Rule 6 BMB-rewrite policy. The Python layer is intentionally thin to keep that port small.

---

## Why Chatter?

BMB is an AI-first programming language—designed to be written by AI and reviewed by humans. But AI models have never seen BMB in their training data:

```
LLM Training Data:
  Rust: ████████████████████████  ~2M repositories
  C:    ████████████████████████  ~3M repositories
  Go:   ████████████████          ~1M repositories
  BMB:  ▏                         ~0 repositories
```

Without Chatter, AI models:
- Confuse `T?` with `Option<T>`
- Use `&` for bitwise AND (should be `band`)
- Forget explicit `return` in block bodies
- Generate incorrect or missing contracts

**Chatter solves this by injecting BMB knowledge at runtime.**

---

## How It Works

```
┌─────────────┐     ┌─────────────────┐     ┌─────────────┐
│    LLM      │────▶│    Chatter      │────▶│    BMB      │
│  (Claude)   │◀────│   MCP Server    │◀────│  Toolchain  │
└─────────────┘     └─────────────────┘     └─────────────┘
                           │
                    ┌──────┴──────┐
                    ▼             ▼
              [Spec Database] [Examples]
```

Instead of stuffing the entire specification into every prompt (~15K tokens), Chatter provides **selective, on-demand access** to exactly what the AI needs.

---

## Features

### Tools

| Tool | Description |
|------|-------------|
| `bmb_spec_lookup` | Query language specification by topic |
| `bmb_check` | Type-check code without full compilation |
| `bmb_verify` | Verify contracts using Z3 solver |
| `bmb_compile` | Compile to native executable |
| `bmb_example` | Get example code for patterns/concepts |
| `bmb_from_rust` | Convert Rust code to BMB with contract suggestions |
| `bmb_test` | Run test cases against BMB code |

### Resources

| URI | Description |
|-----|-------------|
| `bmb://spec/full` | Complete language specification |
| `bmb://spec/quick-reference` | Cheatsheet for common patterns |
| `bmb://spec/rust-diff` | BMB vs Rust differences |
| `bmb://examples/{category}` | Example code by category |
| `bmb://stdlib/{module}` | Standard library documentation |

### Prompts

| Prompt | Description |
|--------|-------------|
| `bmb_implement` | Implement a function with contracts |
| `bmb_add_contracts` | Add contracts to existing code |
| `bmb_optimize` | Optimize code for performance |

---

## Installation (Python — current implementation)

```bash
# From source (recommended during M2)
cd ecosystem/bmb-mcp
pip install -e .

# Run the server
bmb-chatter
```

### Requirements

- Python 3.10+
- BMB compiler — set `BMB_BINARY`, add `bmb` to `PATH`, or run `cargo build --release` in the workspace
- Z3 solver (for `bmb_verify`, once that tool lands)

---

## Usage

### With Claude Desktop

Add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "bmb": {
      "command": "npx",
      "args": ["@bmb/chatter"]
    }
  }
}
```

### Standalone Server

```bash
# Start server
chatter serve

# With custom BMB path
BMB_PATH=/usr/local/bin/bmb chatter serve

# With debug logging
chatter serve --debug
```

---

## Example Session

**User**: Implement binary search in BMB

**AI's internal workflow**:

```
1. bmb_spec_lookup(topic="contracts")
   → Learn pre/post/invariant syntax

2. bmb_example(category="algorithms", name="binary_search")
   → Reference implementation

3. [Generate code]

4. bmb_check(code)
   → Error: "Array access without bounds check"
   → Suggestion: "Add `pre idx < arr.len()` contract"

5. [Fix code]

6. bmb_verify(code)
   → ✓ All contracts verified

7. Return verified code to user
```

**Result**:

```bmb
pure fn is_sorted(arr: &[i32]) -> bool {
    let mut i = 1;
    while i < arr.len()
      invariant i <= arr.len()
    {
        if arr[i - 1] > arr[i] {
            return false;
        }
        i = i + 1;
    }
    return true;
}

fn binary_search(arr: &[i32], target: i32) -> usize?
  pre is_sorted(arr)
  post ret.is_none() implies forall i: 0..arr.len(). arr[i] != target
  post ret.is_some() implies arr[ret.unwrap()] == target
{
    let mut lo: usize = 0;
    let mut hi: usize = arr.len();

    while lo < hi
      invariant lo <= hi and hi <= arr.len()
    {
        let mid = lo + (hi - lo) / 2;

        if arr[mid] == target {
            return Some(mid);
        } else if arr[mid] < target {
            lo = mid + 1;
        } else {
            hi = mid;
        }
    }

    return None;
}
```

---

## AI-Friendly Error Messages

Chatter transforms compiler errors into actionable suggestions:

**Standard compiler output**:
```
error[E0421]: array index out of bounds cannot be proven safe
  --> main.bmb:3:5
```

**Chatter output**:
```json
{
  "success": false,
  "errors": [{
    "code": "E0421",
    "message": "Array index out of bounds cannot be proven safe",
    "location": { "line": 3, "column": 5 },
    "suggestion": "Add `pre idx < arr.len()` before the function body",
    "explanation": "BMB requires compile-time proof of array bounds. Add a precondition or use checked access with `arr.get(idx)`."
  }]
}
```

---

## Common Mistakes Chatter Catches

| Mistake | Wrong | Correct | Detection |
|---------|-------|---------|-----------|
| Nullable syntax | `Option<T>` | `T?` | `bmb_check` |
| Bitwise AND | `a & b` | `a band b` | `bmb_check` |
| Bitwise OR | `a \| b` | `a bor b` | `bmb_check` |
| Implicit return | `{ x }` | `{ return x; }` | `bmb_check` |
| Missing contract | `arr[idx]` | `pre idx < arr.len()` | `bmb_verify` |
| Overflow | `a + b` | `pre` or `+%`/`+\|`/`+?` | `bmb_verify` |

---

## Configuration

```yaml
# chatter.yaml
bmb:
  path: /usr/local/bin/bmb
  runtime: /usr/local/lib/bmb/runtime.c

verification:
  timeout_ms: 5000
  z3_path: /usr/local/bin/z3

examples:
  path: /usr/local/share/bmb/examples

logging:
  level: info
  file: /var/log/chatter.log
```

---

## Development

```bash
# Install dependencies
npm install

# Run tests
npm test

# Run in development mode
npm run dev

# Build for production
npm run build

# Lint
npm run lint
```

---

## Naming

**Chatter** continues the BMB naming theme:

```
BMB = Bare-Metal-Banter
                 └──────┐
                        ▼
                    Chatter
                 (friendly conversation)
```

Just as BMB enables "banter" between AI and bare metal, Chatter enables conversation between AI and the BMB toolchain.

---

## Related Projects

| Project | Description |
|---------|-------------|
| [lang-bmb](https://github.com/lang-bmb/lang-bmb) | BMB compiler and language |
| [gotgan](https://github.com/lang-bmb/gotgan) | BMB package manager |
| [tree-sitter-bmb](https://github.com/lang-bmb/tree-sitter-bmb) | Syntax highlighting |
| [vscode-bmb](https://github.com/lang-bmb/vscode-bmb) | VS Code extension |

---

## License

MIT

---

<p align="center">
  <b>Banter for AI. Bare-metal for humans.</b><br>
  <sub>Chatter makes BMB speakable.</sub>
</p>