# Chatter Roadmap

> MCP server for the BMB programming language

This document outlines the development roadmap for Chatter, organized by milestone.

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

## Milestones

### v0.1.0 — Foundation (ETA: 4 weeks)

**Goal**: Basic functionality for AI code generation feedback loop.

#### Core Tools

- [ ] `bmb_spec_lookup`
  - [ ] Spec database structure
  - [ ] Topic indexing (types, contracts, operators, etc.)
  - [ ] Subtopic granularity
  - [ ] Token-efficient responses

- [ ] `bmb_check`
  - [ ] BMB compiler integration
  - [ ] Error parsing
  - [ ] AI-friendly error formatting
  - [ ] Suggestion generation for common mistakes

- [ ] `bmb_example`
  - [ ] Example database (30+ examples)
  - [ ] Category organization
  - [ ] Searchable by pattern name

#### Infrastructure

- [ ] MCP server scaffold (TypeScript)
- [ ] Configuration system
- [ ] Logging framework
- [ ] Basic test suite

#### Documentation

- [ ] Installation guide
- [ ] Tool reference
- [ ] Example sessions

---

### v0.2.0 — Verification (ETA: +4 weeks)

**Goal**: Contract verification with actionable feedback.

#### Verification Tools

- [ ] `bmb_verify`
  - [ ] Z3 solver integration
  - [ ] Timeout handling
  - [ ] Counterexample extraction
  - [ ] Contract fix suggestions

- [ ] Enhanced error messages
  - [ ] Counterexample formatting
  - [ ] Visual contract violation explanation
  - [ ] Step-by-step fix guidance

#### Spec Database Expansion

- [ ] Contract patterns library
- [ ] Invariant templates
- [ ] Quantifier examples (forall, exists)
- [ ] Common precondition/postcondition pairs

#### Examples Expansion

- [ ] Contract-critical examples (20+)
  - [ ] Bounded buffer
  - [ ] Safe divide
  - [ ] Sorted insert
  - [ ] Ring buffer
  - [ ] Memory pool

---

### v0.3.0 — Migration (ETA: +3 weeks)

**Goal**: Seamless Rust-to-BMB conversion.

#### Migration Tools

- [ ] `bmb_from_rust`
  - [ ] Rust parser integration
  - [ ] Syntax transformation rules
  - [ ] Contract inference from Rust patterns
  - [ ] Warning generation

#### Transformation Rules

| Rust Pattern | BMB Transformation | Contract Suggestion |
|--------------|-------------------|---------------------|
| `Option<T>` | `T?` | — |
| `Result<T, E>` | `Result<T, E>` | — |
| `&`/`\|`/`^` (bitwise) | `band`/`bor`/`bxor` | — |
| `arr[idx]` | `arr[idx]` | `pre idx < arr.len()` |
| `a / b` | `a / b` | `pre b != 0` |
| `Vec::push` | `vec.push` | capacity contracts |
| `unwrap()` | `unwrap()` | `pre x.is_some()` |

#### Contract Inference

- [ ] Array indexing → bounds precondition
- [ ] Division → non-zero precondition
- [ ] Nullable unwrap → is_some precondition
- [ ] Sorting → is_sorted postcondition
- [ ] Search → element exists postcondition

---

### v0.4.0 — Testing (ETA: +2 weeks)

**Goal**: Integrated testing support.

#### Testing Tools

- [ ] `bmb_test`
  - [ ] Test case execution
  - [ ] Expected output comparison
  - [ ] Edge case coverage analysis
  - [ ] Performance measurement

#### Features

- [ ] Test case generation suggestions
- [ ] Property-based testing hints
- [ ] Coverage reporting
- [ ] Benchmark comparison (vs C baseline)

---

### v0.5.0 — Resources & Prompts (ETA: +2 weeks)

**Goal**: Complete MCP feature set.

#### Resources

- [ ] `bmb://spec/full` — Complete specification
- [ ] `bmb://spec/quick-reference` — Cheatsheet
- [ ] `bmb://spec/rust-diff` — Rust differences
- [ ] `bmb://examples/{category}` — Examples by category
- [ ] `bmb://stdlib/{module}` — Standard library docs

#### Prompts

- [ ] `bmb_implement` — Function implementation template
- [ ] `bmb_add_contracts` — Contract addition workflow
- [ ] `bmb_optimize` — Performance optimization workflow

---

### v1.0.0 — Production Ready (ETA: +4 weeks)

**Goal**: Stable release with validated effectiveness.

#### Validation

- [ ] AI generation experiment
  - [ ] 30 benchmark tasks
  - [ ] Multiple LLM testing (Claude, GPT-4, Gemini)
  - [ ] Statistical significance
  - [ ] Published results

- [ ] Performance benchmarks
  - [ ] Response latency <500ms (p95)
  - [ ] Memory usage <100MB
  - [ ] Concurrent session support

#### Production Features

- [ ] Stable API (no breaking changes)
- [ ] Comprehensive error handling
- [ ] Rate limiting
- [ ] Telemetry (opt-in)

#### Documentation

- [ ] Complete API reference
- [ ] Integration guides (Claude Desktop, custom clients)
- [ ] Troubleshooting guide
- [ ] Contributing guide

---

## Post-1.0 Features

### v1.1 — IDE Integration

- [ ] VS Code extension deep integration
- [ ] Real-time diagnostics streaming
- [ ] Inline contract suggestions

### v1.2 — Advanced Verification

- [ ] Incremental verification (cache)
- [ ] Parallel Z3 queries
- [ ] Custom solver strategies
- [ ] Proof explanation in natural language

### v1.3 — Learning System

- [ ] Usage pattern analysis
- [ ] Common error database
- [ ] Personalized suggestions
- [ ] Community examples integration

### v1.4 — Multi-Language Migration

- [ ] C to BMB conversion
- [ ] Zig to BMB conversion
- [ ] Go to BMB conversion

---

## Spec Database Structure

```
specs/
├── types/
│   ├── primitives.md
│   ├── nullable.md
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
│   ├── overflow.md
│   ├── bitwise.md
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
└── real_world/
    ├── json_parser.bmb
    ├── http_parser.bmb
    ├── lexer.bmb
    └── calculator.bmb
```

---

## Success Metrics

### Quantitative

| Metric | v0.1 | v0.5 | v1.0 |
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

## Dependencies

### External

| Dependency | Version | Purpose |
|------------|---------|---------|
| Node.js | ≥18.0 | Runtime |
| BMB compiler | ≥0.50 | Code compilation |
| Z3 | ≥4.12 | Contract verification |
| tree-sitter | ≥0.20 | Rust parsing (migration) |

### Internal

| Dependency | Status | Notes |
|------------|--------|-------|
| BMB compiler | Required | Must expose check/verify CLI |
| BMB spec | Required | Source of truth for spec database |
| BMB examples | Required | Source for example database |

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup and guidelines.

### Priority Areas

1. **Spec database** — Convert SPECIFICATION.md into granular, queryable chunks
2. **Error mapping** — Map compiler errors to AI-friendly suggestions
3. **Examples** — Write idiomatic BMB examples for all patterns
4. **Testing** — Validate AI generation quality improvements

---

## Timeline Summary

```
2026
│
├── Feb ────── v0.1.0 (Foundation)
│              └── Basic spec lookup, check, examples
│
├── Mar ────── v0.2.0 (Verification)
│              └── Z3 integration, contract suggestions
│
├── Apr ────── v0.3.0 (Migration)
│              └── Rust-to-BMB conversion
│
├── Apr ────── v0.4.0 (Testing)
│              └── Test execution, coverage
│
├── May ────── v0.5.0 (Resources & Prompts)
│              └── Complete MCP feature set
│
└── Jun ────── v1.0.0 (Production)
               └── Validated, stable release
```

---

## Questions & Decisions

### Open Questions

1. **Caching strategy**: How aggressively should we cache verification results?
2. **Streaming**: Should `bmb_verify` stream partial results for long-running proofs?
3. **Multi-file projects**: How should we handle project-level context?

### Decided

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Language | TypeScript | MCP ecosystem standard |
| Spec format | Markdown | Human-readable, easy to maintain |
| Example format | `.bmb` files | Direct compiler compatibility |
| Error format | JSON with suggestions | AI-parseable, actionable |

---

## References

- [BMB Language Specification](https://github.com/lang-bmb/lang-bmb/blob/main/docs/SPECIFICATION.md)
- [MCP Specification](https://spec.modelcontextprotocol.io/)
- [BMB Ecosystem](https://github.com/lang-bmb/lang-bmb/blob/main/docs/ECOSYSTEM.md)