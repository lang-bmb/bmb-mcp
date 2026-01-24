# Chatter Roadmap

> MCP server for the BMB programming language

This document outlines the development roadmap for Chatter, organized by milestone.

**Version Policy**: All versions are v0.x. Major version (v1.0) requires community validation and manual release.

---

## Vision

Enable AI models to generate **correct, verified, performant** BMB code despite zero training data, achieving:

| Metric | Target |
|--------|--------|
| Compile success rate | >90% |
| Contract accuracy | >80% |
| Iterations to success | ≤3 rounds |
| Token efficiency | 5x better than full-spec prompting |

---

## Current Status: Pre-Alpha

```
[██░░░░░░░░░░░░░░░░░░] 10% Complete
```

---

## MCP 2025-11-25 Spec Alignment

Based on the [MCP Specification (2025-11-25)](https://modelcontextprotocol.io/specification/2025-11-25):

### Server Features (We Provide)
- **Resources**: Context and data for AI model
- **Prompts**: Templated messages and workflows
- **Tools**: Functions for AI model to execute

### Client Features (We May Request)
- **Sampling**: Server-initiated LLM interactions
- **Roots**: Filesystem/URI boundary inquiries
- **Elicitation**: Request additional info from users

### Security Requirements (Critical)
- Explicit user consent for all operations
- Clear documentation of security implications
- Appropriate access controls and data protections
- Tool descriptions treated as untrusted

---

## Milestones

### v0.1.0 — Foundation (Priority: P0)

**Goal**: Basic functionality for AI code generation feedback loop.

#### Core Tools

| Task | Description | Priority | Status |
|------|-------------|----------|--------|
| `bmb_spec_lookup` | Query language specification by topic | P0 | ⏳ |
| ├─ Spec database structure | Granular, token-efficient chunks | P0 | ⏳ |
| ├─ Topic indexing | types, contracts, operators, etc. | P0 | ⏳ |
| └─ Subtopic granularity | Fine-grained queries | P1 | ⏳ |
| `bmb_check` | Type-check code without full compilation | P0 | ⏳ |
| ├─ BMB compiler integration | CLI invocation | P0 | ⏳ |
| ├─ Error parsing | Parse compiler output | P0 | ⏳ |
| ├─ AI-friendly formatting | JSON with suggestions | P0 | ⏳ |
| └─ Common mistake detection | T?, band, return, etc. | P0 | ⏳ |
| `bmb_example` | Get example code for patterns | P1 | ⏳ |
| ├─ Example database | 30+ examples | P1 | ⏳ |
| └─ Category search | By pattern name | P1 | ⏳ |

#### Infrastructure

| Task | Description | Priority | Status |
|------|-------------|----------|--------|
| MCP server scaffold | TypeScript, JSON-RPC 2.0 | P0 | ⏳ |
| Capability negotiation | Server/client handshake | P0 | ⏳ |
| Configuration system | chatter.yaml | P1 | ⏳ |
| Logging framework | Structured logging | P1 | ⏳ |
| Basic test suite | Unit + integration tests | P1 | ⏳ |

#### Security (MCP Compliance)

| Task | Description | Priority | Status |
|------|-------------|----------|--------|
| User consent flow | Explicit approval for operations | P0 | ⏳ |
| Tool safety warnings | Document each tool's implications | P0 | ⏳ |
| Input sanitization | Prevent prompt injection | P0 | ⏳ |

---

### v0.2.0 — Verification (Priority: P0)

**Goal**: Contract verification with actionable feedback.

#### Verification Tools

| Task | Description | Priority | Status |
|------|-------------|----------|--------|
| `bmb_verify` | Verify contracts using Z3 | P0 | ⏳ |
| ├─ Z3 solver integration | SMT-LIB2 generation | P0 | ⏳ |
| ├─ Timeout handling | Configurable limits | P0 | ⏳ |
| ├─ Counterexample extraction | Failing inputs | P0 | ⏳ |
| └─ Contract fix suggestions | Actionable guidance | P0 | ⏳ |
| Enhanced error messages | Visual explanations | P1 | ⏳ |

#### Spec Database Expansion

| Task | Description | Priority | Status |
|------|-------------|----------|--------|
| Contract patterns library | Common patterns | P0 | ⏳ |
| Invariant templates | Loop invariants | P1 | ⏳ |
| Quantifier examples | forall, exists | P1 | ⏳ |

---

### v0.3.0 — Migration (Priority: P1)

**Goal**: Seamless Rust-to-BMB conversion.

#### Migration Tools

| Task | Description | Priority | Status |
|------|-------------|----------|--------|
| `bmb_from_rust` | Convert Rust code to BMB | P1 | ⏳ |
| ├─ Rust parser integration | tree-sitter-rust | P1 | ⏳ |
| ├─ Syntax transformation | Option→T?, &→band, etc. | P1 | ⏳ |
| └─ Contract inference | Auto-suggest contracts | P1 | ⏳ |

#### Contract Inference Rules

| Rust Pattern | BMB Transformation | Auto-Contract |
|--------------|-------------------|---------------|
| `Option<T>` | `T?` | — |
| `arr[idx]` | `arr[idx]` | `pre idx < arr.len()` |
| `a / b` | `a / b` | `pre b != 0` |
| `unwrap()` | `unwrap()` | `pre x.is_some()` |
| `&`/`\|`/`^` | `band`/`bor`/`bxor` | — |

---

### v0.4.0 — Testing (Priority: P1)

**Goal**: Integrated testing support.

#### Testing Tools

| Task | Description | Priority | Status |
|------|-------------|----------|--------|
| `bmb_test` | Run test cases | P1 | ⏳ |
| ├─ Test execution | Run #[test] functions | P1 | ⏳ |
| ├─ Expected output comparison | Assert results | P1 | ⏳ |
| └─ Performance measurement | vs C baseline | P2 | ⏳ |

---

### v0.5.0 — Resources & Prompts (Priority: P1)

**Goal**: Complete MCP feature set.

#### Resources

| URI | Description | Priority | Status |
|-----|-------------|----------|--------|
| `bmb://spec/full` | Complete specification | P1 | ⏳ |
| `bmb://spec/quick-reference` | Cheatsheet | P0 | ⏳ |
| `bmb://spec/rust-diff` | Rust differences | P0 | ⏳ |
| `bmb://spec/cdo-intro` | Contract-Driven Optimization intro | P1 | ⏳ |
| `bmb://examples/{category}` | Examples by category | P1 | ⏳ |
| `bmb://stdlib/{module}` | Standard library docs | P2 | ⏳ |

#### Prompts

| Prompt | Description | Priority | Status |
|--------|-------------|----------|--------|
| `bmb_implement` | Function implementation | P1 | ⏳ |
| `bmb_add_contracts` | Contract addition (CDO-aware) | P0 | ⏳ |
| `bmb_optimize` | CDO-oriented optimization | P2 | ⏳ |

---

### v0.6.0 — Compilation (Priority: P2)

**Goal**: Full compilation support.

| Task | Description | Priority | Status |
|------|-------------|----------|--------|
| `bmb_compile` | Compile to native executable | P2 | ⏳ |
| ├─ LLVM backend integration | Native binaries | P2 | ⏳ |
| ├─ Cross-compilation hints | Platform-specific | P2 | ⏳ |
| └─ Performance profiling | Benchmark results | P2 | ⏳ |

---

### v0.7.0 — Advanced Security (Priority: P1)

**Goal**: Production-grade security.

Based on [MCP security research (April 2025)](https://modelcontextprotocol.io/specification/2025-11-25):

| Task | Description | Priority | Status |
|------|-------------|----------|--------|
| Prompt injection defense | Sanitize spec/example content | P0 | ⏳ |
| Tool permission model | Granular access control | P0 | ⏳ |
| Lookalike tool detection | Prevent tool impersonation | P1 | ⏳ |
| Audit logging | All operations logged | P1 | ⏳ |
| Rate limiting | Prevent abuse | P1 | ⏳ |

---

### v0.8.0 — IDE Integration (Priority: P2)

**Goal**: Seamless editor experience.

| Task | Description | Priority | Status |
|------|-------------|----------|--------|
| VS Code deep integration | vscode-bmb extension | P2 | ⏳ |
| Real-time diagnostics | Streaming errors | P2 | ⏳ |
| Inline contract suggestions | CodeLens/hints | P2 | ⏳ |

---

### v0.9.0 — Stabilization (Priority: P0)

**Goal**: Stable release with validated effectiveness.

#### Validation

| Task | Description | Priority | Status |
|------|-------------|----------|--------|
| AI generation experiment | 30 benchmark tasks | P0 | ⏳ |
| ├─ Multiple LLM testing | Claude, GPT-4, Gemini | P0 | ⏳ |
| └─ Published results | Statistical validation | P0 | ⏳ |
| Performance benchmarks | p95 <500ms, <100MB RAM | P0 | ⏳ |
| Concurrent sessions | Multi-user support | P1 | ⏳ |

#### Production Features

| Task | Description | Priority | Status |
|------|-------------|----------|--------|
| Stable API | No breaking changes | P0 | ⏳ |
| Comprehensive error handling | All edge cases | P0 | ⏳ |
| Telemetry (opt-in) | Usage analytics | P2 | ⏳ |

#### Documentation

| Task | Description | Priority | Status |
|------|-------------|----------|--------|
| Complete API reference | All tools/resources/prompts | P0 | ⏳ |
| Integration guides | Claude Desktop, custom clients | P0 | ⏳ |
| Troubleshooting guide | Common issues | P1 | ⏳ |
| Contributing guide | Development setup | P1 | ⏳ |

---

## Future Versions (v0.10+)

### v0.10.0 — Advanced Verification

| Task | Description |
|------|-------------|
| Incremental verification | Cache proof results |
| Parallel Z3 queries | Multiple proofs concurrently |
| Proof explanation | Natural language explanations |

### v0.11.0 — Multi-Agent Support

Based on [2026 MCP trends](https://www.pento.ai/blog/a-year-of-mcp-2025-review):

| Task | Description |
|------|-------------|
| Agent-to-agent communication | Chatter↔other MCP servers |
| Sampling support | Server-initiated LLM calls |
| Workflow orchestration | Multi-step verification pipelines |

### v0.12.0 — Learning System

| Task | Description |
|------|-------------|
| Usage pattern analysis | Common error patterns |
| Personalized suggestions | User-specific hints |
| Community examples | Integration with gotgan-packages |

### v0.13.0 — Multi-Language Migration

| Task | Description |
|------|-------------|
| C to BMB conversion | `bmb_from_c` tool |
| Zig to BMB conversion | `bmb_from_zig` tool |
| Go to BMB conversion | `bmb_from_go` tool |

### v0.14.0 — CDO Awareness (Contract-Driven Optimization)

Based on [RFC-0008](https://github.com/lang-bmb/lang-bmb/blob/main/docs/rfcs/RFC-0008-contract-driven-optimization.md):

| Task | Description |
|------|-------------|
| CDO benefit awareness | AI understands contract → optimization relationship |
| Optimization-oriented contracts | Suggest contracts that enable CDO |
| `bmb_cdo_analyze` tool | Analyze CDO potential of generated code |
| Specialization hints | Suggest `pre` constraints for better extraction |

**Why CDO Awareness Matters**:

Contracts are not just safety guards—they are **optimization fuel**. AI should generate:

```bmb
// Instead of generic:
fn parse(s: &str) -> Value

// Generate CDO-friendly:
fn parse(s: &str) -> Value
  pre s.len() < 10000     // Enables: small-string optimization
  pre s.is_ascii()        // Enables: skip unicode normalization
  post ret.is_valid()     // Enables: skip validation at call sites
```

**AI Guidance Examples**:

| Scenario | Without CDO Awareness | With CDO Awareness |
|----------|----------------------|-------------------|
| Array access | Generic bounds check | `pre idx < arr.len()` (check eliminated) |
| Division | Runtime zero check | `pre divisor != 0` (check eliminated) |
| Sorting | Generic algorithm | `pre arr.len() < 1000` (specialized algorithm) |
| Pure function | Normal compilation | `pure fn` + bounds → precomputation |

**CDO-Aware Resources**:

| URI | Description |
|-----|-------------|
| `bmb://cdo/patterns` | Contract patterns that enable CDO |
| `bmb://cdo/extraction` | Minimal extraction examples |
| `bmb://cdo/specialization` | Function specialization patterns |

---

## Spec Database Structure

```
specs/
├── types/
│   ├── primitives.md
│   ├── nullable.md      # T? syntax (critical for AI)
│   ├── compound.md
│   ├── generics.md
│   ├── refinement.md
│   └── lifetimes.md
├── functions/
│   ├── declaration.md
│   ├── pure.md
│   ├── closures.md
│   └── methods.md
├── contracts/
│   ├── preconditions.md
│   ├── postconditions.md
│   ├── invariants.md
│   ├── quantifiers.md
│   └── trust.md
├── operators/
│   ├── arithmetic.md
│   ├── overflow.md      # +% +| +? (critical for AI)
│   ├── bitwise.md       # band/bor/bxor (critical for AI)
│   ├── logical.md
│   └── comparison.md
├── control_flow/
│   ├── conditionals.md
│   ├── loops.md
│   └── match.md
├── data/
│   ├── structs.md
│   ├── enums.md
│   └── impl.md
├── correctness/         # BMB-specific rules
│   ├── explicit_return.md
│   ├── no_deref_coercion.md
│   ├── no_auto_ref.md
│   └── no_ref_pattern.md
├── cdo/                 # Contract-Driven Optimization (RFC-0001)
│   ├── overview.md          # CDO philosophy and benefits
│   ├── semantic_dce.md      # Contract-based dead code elimination
│   ├── specialization.md    # Function specialization patterns
│   ├── extraction.md        # Minimal dependency extraction
│   └── patterns.md          # CDO-friendly contract patterns
└── modules/
    ├── mod.md
    ├── use.md
    └── visibility.md
```

---

## Example Database Structure

```
examples/
├── basics/
│   ├── hello_world.bmb
│   ├── variables.bmb
│   ├── functions.bmb
│   └── control_flow.bmb
├── contracts/
│   ├── preconditions.bmb
│   ├── postconditions.bmb
│   ├── invariants.bmb
│   ├── quantifiers.bmb
│   └── trust.bmb
├── ai_mistakes/         # NEW: Common AI errors
│   ├── nullable_syntax.bmb      # T? not Option<T>
│   ├── bitwise_operators.bmb    # band not &
│   ├── explicit_return.bmb      # return required
│   └── overflow_operators.bmb   # +% +| +?
├── data_structures/
│   ├── array.bmb
│   ├── linked_list.bmb
│   ├── binary_tree.bmb
│   ├── hash_map.bmb
│   └── ring_buffer.bmb
├── algorithms/
│   ├── binary_search.bmb
│   ├── quicksort.bmb
│   ├── mergesort.bmb
│   └── dijkstra.bmb
├── patterns/
│   ├── builder.bmb
│   ├── iterator.bmb
│   └── state_machine.bmb
├── cdo/                 # CDO optimization examples
│   ├── semantic_dce.bmb         # Contract-based dead code elimination
│   ├── pure_precompute.bmb      # pure fn + bounded input → table
│   ├── specialization.bmb       # Contract-specialized functions
│   └── extraction.bmb           # Minimal dependency extraction
└── real_world/
    ├── json_parser.bmb
    ├── http_parser.bmb
    ├── lexer.bmb
    └── calculator.bmb
```

---

## Success Metrics

### Quantitative

| Metric | v0.1 | v0.5 | v0.9 |
|--------|------|------|------|
| Spec topics covered | 50% | 90% | 100% |
| Example count | 30 | 70 | 100+ |
| Compile rate (AI-generated) | 70% | 85% | 90% |
| Contract accuracy | 50% | 70% | 80% |
| Avg iterations to success | 5 | 3 | 2 |
| Response latency (p95) | 1s | 700ms | 500ms |

### Qualitative

- [ ] AI can implement any benchmark task from SPECIFICATION.md
- [ ] Error messages are immediately actionable
- [ ] Rust developers can migrate code without manual spec reading
- [ ] Contract suggestions are contextually appropriate

---

## Testing Strategy

### Environment Configuration (`.env`)

테스트 환경은 `.env` 파일로 구성합니다. `.env.example`을 복사하여 사용:

```bash
cp .env.example .env
# Edit .env with your API keys and paths
```

### Test Categories

| Category | Description | Env Vars Used | Frequency |
|----------|-------------|---------------|-----------|
| **Unit** | Individual tool functions | `BMB_PATH`, `Z3_PATH` | Every commit |
| **Integration** | MCP protocol compliance | `BMB_PATH`, `Z3_PATH` | Every PR |
| **E2E** | Full workflow simulation | All | Weekly |
| **Validation** | AI code generation quality | `*_API_KEY`, `*_MODEL` | Per milestone |

### Unit Tests

```bash
# Run unit tests
npm test

# Run with coverage
npm run test:coverage

# Test specific tool
npm test -- --grep "bmb_check"
```

**Required `.env` for unit tests:**
```env
BMB_PATH=/path/to/bmb
Z3_PATH=/path/to/z3
TEST_MODE=unit
```

### Integration Tests

MCP 프로토콜 준수 및 도구 간 상호작용 테스트:

```bash
# Run integration tests
npm run test:integration

# Test MCP handshake
npm run test:integration -- --grep "capability negotiation"
```

**Test scenarios:**
1. Server initialization & capability negotiation
2. Tool invocation flow: `bmb_spec_lookup` → `bmb_check` → `bmb_verify`
3. Error handling & recovery
4. Resource URI resolution
5. Prompt template execution

### E2E Tests

실제 MCP 클라이언트와의 전체 워크플로우 테스트:

```bash
# Run E2E tests (requires running server)
npm run test:e2e

# With mock client
npm run test:e2e:mock
```

**Test scenarios:**
1. Claude Desktop 시뮬레이션
2. Binary search 구현 요청 → 검증된 코드 반환
3. Rust 코드 변환 → BMB + 계약
4. 오류 복구 루프 (최대 3회)

### AI Validation Tests (v0.9.0 필수)

실제 AI 모델로 코드 생성 품질 측정:

```bash
# Run validation with all providers
npm run test:validation

# Specific provider
VALIDATION_PROVIDER=openai npm run test:validation
VALIDATION_PROVIDER=anthropic npm run test:validation
VALIDATION_PROVIDER=google npm run test:validation
```

**Required `.env` for validation:**
```env
# At least one provider required
OPENAI_API_KEY=sk-proj-...
OPENAI_MODEL=gpt-4o

ANTHROPIC_API_KEY=sk-ant-...
ANTHROPIC_MODEL=claude-sonnet-4-20250514

GOOGLE_API_KEY=...
GOOGLE_MODEL=gemini-2.0-flash

# Test configuration
VALIDATION_ITERATIONS=5
VERIFICATION_TIMEOUT_MS=5000
```

### Validation Benchmark Tasks (30개)

| Category | Tasks | Success Criteria |
|----------|-------|------------------|
| **Basics** (5) | hello, factorial, fibonacci, max, swap | Compiles, correct output |
| **Contracts** (10) | divide, array_get, binary_search, sorted_insert, bounded_buffer, ring_buffer, safe_cast, checked_add, null_check, range_check | All contracts verified |
| **Data Structures** (5) | linked_list, binary_tree, hash_map, queue, stack | Correct operations |
| **Algorithms** (5) | quicksort, mergesort, dijkstra, bfs, dfs | Correct results, O(n) contracts |
| **Real-world** (5) | json_parse, http_parse, lexer, calculator, csv_parse | Functional implementation |

### Validation Metrics

```typescript
interface ValidationResult {
  task: string;
  provider: string;
  model: string;
  iterations: number;

  // Success metrics
  compile_success_rate: number;    // Target: >90%
  contract_accuracy: number;       // Target: >80%
  avg_iterations: number;          // Target: ≤3

  // Performance
  avg_response_time_ms: number;
  avg_token_usage: number;

  // Errors
  common_errors: ErrorCategory[];
}
```

### Test Output Directory

```
test-results/
├── unit/
│   └── results.json
├── integration/
│   └── results.json
├── e2e/
│   └── results.json
└── validation/
    ├── openai-gpt4o-2026-01-24.json
    ├── anthropic-claude-2026-01-24.json
    └── summary.json
```

### CI/CD Integration

```yaml
# .github/workflows/test.yml
name: Test
on: [push, pull_request]

jobs:
  unit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
      - run: npm ci
      - run: npm test
    env:
      BMB_PATH: ${{ secrets.BMB_PATH }}
      Z3_PATH: ${{ secrets.Z3_PATH }}

  validation:
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v4
      - run: npm run test:validation
    env:
      OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
      ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
```

### Mock Services (Development)

API 비용 절감을 위한 캐시된 응답 사용:

```env
# .env for development
DEV_MOCK_SERVICES=true
DEV_USE_CACHED_RESPONSES=true
```

캐시된 응답은 `test-fixtures/cached-responses/`에 저장.

---

## Dependencies

### External

| Dependency | Version | Purpose |
|------------|---------|---------|
| Node.js | ≥18.0 | Runtime |
| BMB compiler | ≥0.50 | Code compilation |
| Z3 | ≥4.12 | Contract verification |
| tree-sitter | ≥0.20 | Rust parsing (migration) |

### Internal (lang-bmb)

| Dependency | Status | Notes |
|------------|--------|-------|
| BMB compiler | Required | Must expose check/verify CLI |
| SPECIFICATION.md | Required | Source of truth for spec database |
| bmb-samples | Required | Source for example database |

---

## Priority Summary

### P0 (Must Have for v0.9)

1. `bmb_spec_lookup` - AI has no BMB training data
2. `bmb_check` - Compile feedback loop
3. `bmb_verify` - Contract verification
4. Security compliance - User consent, input sanitization
5. AI validation experiment - Prove effectiveness

### P1 (Should Have)

1. `bmb_example` - Reference implementations
2. `bmb_from_rust` - Migration path
3. Resources & Prompts - Complete MCP features
4. Documentation - Adoption enabler

### P2 (Nice to Have)

1. `bmb_compile` - Native compilation
2. IDE integration - Editor experience
3. Telemetry - Usage insights

---

## Timeline Summary

```
2026
│
├── Feb ────── v0.1.0 (Foundation)
│              └── spec lookup, check, examples
│
├── Mar ────── v0.2.0 (Verification)
│              └── Z3 integration, contract suggestions
│
├── Apr ────── v0.3.0 (Migration)
│              └── Rust-to-BMB conversion
│
├── Apr ────── v0.4.0 (Testing)
│              └── Test execution
│
├── May ────── v0.5.0 (Resources & Prompts)
│              └── Complete MCP primitives
│
├── May ────── v0.6.0 (Compilation)
│              └── Native binary support
│
├── Jun ────── v0.7.0 (Security)
│              └── Production-grade security
│
├── Jul ────── v0.8.0 (IDE)
│              └── VS Code integration
│
└── Aug ────── v0.9.0 (Stabilization)
               └── Validated, stable release
```

---

## Open Questions

1. **Caching strategy**: How aggressively cache verification results?
2. **Streaming**: Should `bmb_verify` stream partial results?
3. **Multi-file projects**: How to handle project-level context?
4. **Sampling**: When should Chatter initiate LLM calls itself?

---

## Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Language | TypeScript | MCP ecosystem standard |
| Spec format | Markdown | Human-readable, maintainable |
| Example format | `.bmb` files | Direct compiler compatibility |
| Error format | JSON with suggestions | AI-parseable, actionable |
| Version policy | v0.x only | Align with lang-bmb |

---

## References

- [BMB Language Specification](https://github.com/lang-bmb/lang-bmb/blob/main/docs/SPECIFICATION.md)
- [MCP Specification (2025-11-25)](https://modelcontextprotocol.io/specification/2025-11-25)
- [MCP Security Considerations](https://modelcontextprotocol.io/specification/2025-11-25)
- [A Year of MCP (2025 Review)](https://www.pento.ai/blog/a-year-of-mcp-2025-review)
- [BMB Ecosystem](https://github.com/lang-bmb/lang-bmb/blob/main/docs/ECOSYSTEM.md)
