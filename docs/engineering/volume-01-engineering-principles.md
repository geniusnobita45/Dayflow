# Volume 01 — Engineering Principles

**Document Type:** Engineering Standards & Philosophy
**DIMP Volume:** 01
**Status:** FROZEN — Governs all implementation
**Date:** 2026-06-29
**Governed By:** Constitution v3.0 (§3, §4)
**Builds On:** Volume 00 (Architecture Lock — ADR-009)

---

## 01. Executive Summary

This volume is the **engineering code of conduct** for DayFlow. Where the Constitution (§3, §4) states *principles*, this volume translates them into *concrete engineering rules* a developer or AI coding agent applies to every commit. It governs: how we think about architecture, how we organize code, how we name things, how large files and functions may grow, what a "class" may and may not do, how dependencies point, and the global Definition of Done that no module escapes.

Every subsequent DIMP volume assumes full compliance with this one. If a volume's detail conflicts with this volume, this volume wins; if this volume conflicts with the Constitution, the Constitution wins (C1.2).

---

## 02. Objectives

1. Translate Constitution §3 (Philosophy) and §4 (Architecture Principles) into **actionable engineering rules**.
2. Establish **naming, structure, and size conventions** that are uniform across Python and TypeScript.
3. Define the **global Definition of Done** (DoD) referenced by every module's acceptance criteria.
4. Codify the **discipline** that makes a multi-year, AI-assisted codebase maintainable: no half-built modules, no silent failures, no magic, no shortcut that violates the dependency rule.

---

## 03. Scope

**In scope:**
- Engineering philosophy in practice (C3).
- Architecture principles in practice (C4).
- Naming conventions (C36.1).
- File and function size limits (C36.3, C36.4) and their enforcement.
- Class responsibility rules (C36.2) and the "no Manager" smell.
- Dependency direction in practice (C7).
- Coding standards: comments, error handling, no-magic, consistency (C36.5–8).
- The global Definition of Done (C40).
- Quality gates and build governance in practice (C32, C33).

**Out of scope:**
- Repository layout details → Volume 02.
- Developer tooling/CLI/scaffolding → Volume 03.
- Contract format and generation → Volume 05.
- Domain modeling patterns → Volume 06.
- Module-specific DoD items → individual volumes (04–16).

---

## 04. Out of Scope

See Section 03. This volume is **principles and standards**, not layout or tooling. It tells you *how to think* and *how to judge code*; Volumes 02–03 tell you *how the repo is shaped* and *what commands you run*.

---

## 05. Constitution Mapping

| Principle (this volume) | Constitution Clause |
|------------------------|--------------------|
| Architecture before features | C3.1 |
| Domain first | C3.2, C8.2 |
| AI is not business logic | C3.3, C14.3 |
| Event first | C3.4, C13 |
| Replaceability | C3.5, C15 |
| Local before remote | C3.6, C16 |
| Small vertical slices | C3.7, C17 |
| Boring infra, exciting intelligence | C3.8 |
| Privacy is architectural | C3.9, C22 |
| Reversibility | C3.10 |
| Separation of concerns | C4.1 |
| Dependency inversion | C4.2, C6.1, C7 |
| Single source of truth | C4.3, C9 |
| Fail loud, fail early | C4.4 |
| Idempotency | C4.5 |
| Design for observability | C4.6, C11 |
| Design for testability | C4.7 |
| Progressive enhancement | C4.8 |
| Naming | C36.1 |
| One class, one responsibility | C36.2 |
| File size | C36.3 |
| Function size | C36.4 |
| No magic | C36.5 |
| Comments explain why | C36.6 |
| Error handling explicit | C36.7, C12 |
| Consistency over preference | C36.8 |
| Definition of Done | C40 |

---

## 06. Architecture

Engineering principles are organized into three tiers that cascade downward:

```
Tier 1 — Philosophy (how we decide)
    C3.1 Architecture before features
    C3.2 Domain first
    C3.3 AI is not business logic
    C3.4 Event first
    C3.5 Replaceability
    C3.6 Local before remote
    C3.7 Small vertical slices
    C3.8 Boring infra, exciting intelligence
    C3.9 Privacy is architectural
    C3.10 Reversibility
        │
        ▼
Tier 2 — Architecture Principles (how we structure)
    C4.1 Separation of concerns
    C4.2 Dependency inversion
    C4.3 Single source of truth
    C4.4 Fail loud, fail early
    C4.5 Idempotency
    C4.6 Design for observability
    C4.7 Design for testability
    C4.8 Progressive enhancement
        │
        ▼
Tier 3 — Coding Standards (how we write)
    C36.1 Naming
    C36.2 One class, one responsibility
    C36.3 File size
    C36.4 Function size
    C36.5 No magic
    C36.6 Comments
    C36.7 Error handling
    C36.8 Consistency
```

A violation at Tier 3 is usually a symptom of a Tier 1 or Tier 2 problem. Reviewers trace violations upward.

---

## 07. Components

### 7.1 — Philosophy Rules (Tier 1)

#### 7.1.1 Architecture Before Features (C3.1)

A feature ticket is **not startable** until every architectural dependency it requires is production-ready and merged. The build order in Volume 18 encodes this; the task catalog (Volume 20) enforces it via explicit `Dependencies` on every task.

**Test:** Can you name the upstream module that provides capability X, and is it merged and green? If not, the feature is blocked.

#### 7.1.2 Domain First (C3.2)

Business rules live **only** in the Domain layer. The Application layer orchestrates; it does not contain business rules. The smell to watch for: business logic leaking into a use case's orchestration. If a use case contains an `if` that encodes a business rule, that rule belongs in the domain.

**Allowed locations of business logic:** Domain entities, value objects, domain services, specifications, invariants.

**Forbidden locations:** Controllers, repositories, ORM models, AI prompts, UI components, serializers.

#### 7.1.3 AI Is Not Business Logic (C3.3)

AI output is **untrusted input** (C14.3). The pipeline for any AI-suggested mutation:

```
AI produces suggestion (untrusted)
    ↓
Application validates (auth, invariants, policies)
    ↓
Domain applies (entity method, raises event)
    ↓
Infrastructure persists + publishes
```

AI never holds a reference to a repository. AI never calls a use case directly. AI returns a structured suggestion (DTO); the application decides whether to act.

#### 7.1.4 Event First (C3.4)

Every significant state change publishes a domain event (C13). "Significant" = anything a future projection, consumer, or audit would care about. Derivative/cache updates that are fully recomputable need not be events.

**Heuristic:** If you would want to know "when did X happen and why?", it's an event.

#### 7.1.5 Replaceability (C3.5)

Every external dependency sits behind a port (C15). The test: can you swap the implementation by changing configuration only, with **zero** changes to Domain or Application code? If no, the abstraction is wrong.

#### 7.1.6 Local Before Remote (C3.6)

The execution priority is Device → Edge → Cloud (C16). A capability that can run locally without unacceptable quality loss **must** have a local path. Cloud is an enhancement, not a prerequisite.

#### 7.1.7 Small Vertical Slices (C3.7)

A slice is complete only when it is usable end-to-end, tested, observable, documented, and deployable (C17.2). Half-built modules do not exist in `main` (C17.3). Work-in-progress lives in branches.

#### 7.1.8 Boring Infrastructure, Exciting Intelligence (C3.8)

Storage, messaging, and platform choices favor **proven, boring tech** (PostgreSQL, Redis, HTTP — ADR-004, ADR-008). Intelligence choices favor **cutting-edge capability** (latest LLMs, novel retrieval — ADR-006). Never invert: do not chase novelty in infrastructure, and do not let boring choices constrain intelligence.

#### 7.1.9 Privacy Is Architectural (C3.9)

Privacy is not a setting; it is a property of the architecture (C22). Concretely:
- Mind data (thoughts, memories) never leaves the device unless sync is explicitly enabled.
- Cloud AI receives **redacted/abstracted** content where possible.
- All data is encrypted at rest and in transit (C21.5).

#### 7.1.10 Reversibility (C3.10)

Decisions are classified by reversibility:
- **Hard to reverse** (data formats, public API shapes, event schemas) → extreme care, ADR required, versioning.
- **Easy to reverse** (implementations, algorithms, internal structure) → decide quickly, iterate.

Spend effort proportional to irreversibility.

### 7.2 — Architecture Principles (Tier 2)

#### 7.2.1 Separation of Concerns (C4.1)

Each module/class/function has **one reason to change**. When two concerns appear coupled, introduce a boundary (extract a service, a port, a value object).

#### 7.2.2 Dependency Inversion (C4.2)

High-level policy (Domain, Application) depends on **abstractions**, not concretions. Abstractions are owned by the high level (ports in Application); Infrastructure implements them. The composition root (Volume 04) wires concretes to abstractions.

#### 7.2.3 Single Source of Truth (C4.3)

For every fact, one authoritative source:
- **Schema/types** → contracts (Volume 05), generated to languages.
- **Configuration** → hierarchical resolver (Volume 04, C10).
- **Business rule** → defined once in Domain, never duplicated.
- **Event definition** → contracts, consumed by all.

Duplication is a defect. Code duplication across languages is eliminated by generation (ADR-013).

#### 7.2.4 Fail Loud, Fail Early (C4.4)

- Configuration is validated at startup; the app refuses to boot on invalid config (C10.5).
- Invariants raise immediately when violated.
- Errors are never swallowed (C12.4).
- Assertions guard internal assumptions; a failed assertion is a bug, not a runtime condition.

#### 7.2.5 Idempotency (C4.5)

Every mutating operation is idempotent. Operationally:
- Mutating API endpoints accept an `Idempotency-Key` (C29.7).
- Event consumers deduplicate by `event_id` (C13.5).
- Sync operations are merge-based (CRDTs) — replaying yields the same state (C16.3).
- Repository writes use upsert/conditional-update patterns where applicable.

#### 7.2.6 Design for Observability (C4.6)

Every component ships with structured logging, metrics, and tracing from its first commit (C11.6). A PR adding a component without observability is blocked. See Volume 17.

#### 7.2.7 Design for Testability (C4.7)

- All dependencies are injected (C37).
- Clocks, IDs, and randomness are injectable and mockable.
- Side effects (I/O, time, randomness) are isolated behind ports.
- Unit tests are deterministic (C23.3) — no network, no real clock, no unseeded randomness.

#### 7.2.8 Progressive Enhancement (C4.8)

Graceful degradation matrix:

| Dependency Down | Fallback |
|----------------|----------|
| Cloud | Local operation continues |
| AI | Deterministic rules take over |
| Vector store | Keyword/FTS fallback |
| Cache | Direct DB access (slower) |
| Event bus (in-proc) | Fail the operation (do not silently drop) |

A component declares its degradation behavior in its `module.yaml`.

### 7.3 — Coding Standards (Tier 3)

#### 7.3.1 Naming (C36.1)

| Element | Convention | Example |
|---------|-----------|---------|
| Directories | snake_case | `memory_engine/` |
| Python files | snake_case | `memory_repository.py` |
| TypeScript files | camelCase (logic) / kebab-case (components) | `memoryRepository.ts` / `memory-card.tsx` |
| Classes | PascalCase | `MemoryRepository` |
| Functions | snake_case (Py) / camelCase (TS) | `create_thought()` / `createThought()` |
| Constants | UPPER_CASE | `MAX_CONTEXT_SIZE` |
| Interfaces | PascalCase; Python uses `Protocol` | `MemoryRepository` (Protocol) |
| Enums | PascalCase type, UPPER_CASE members | `TaskStatus.COMPLETED` |
| Tests | `test_<unit>.py` / `<unit>.test.ts` | `test_memory_repository.py` |
| Events | `{Aggregate}.{PastTenseVerb}` | `Task.Completed` |

Names are **honest**. A name that lies (a `Repository` that also searches and ranks) is a defect (C36.2).

#### 7.3.2 One Class, One Responsibility (C36.2)

A class name containing **"And"** or an unscoped **"Manager"** is a smell. Forbidden:

```
class MemoryRepositoryAndEmbeddingServiceAndSearchRanker:  # ❌ three responsibilities
```

Required:

```
class MemoryRepository: ...       # stores/retrieves
class EmbeddingService: ...       # embeds text
class SearchRanker: ...           # ranks results
```

The reviewer question: *can you describe what this class does in one sentence without "and"?*

#### 7.3.3 File Size (C36.3)

| Limit | Lines |
|-------|-------|
| Target | < 300 |
| Maximum (hard) | 500 |

CI fails on any production `.py`/`.ts` file exceeding 500 lines (ADR-009). Files over 300 lines trigger a review comment asking whether to split.

#### 7.3.4 Function Size (C36.4)

| Limit | Lines |
|-------|-------|
| Target | 20–40 |
| Hard maximum | 80 |

CI fails on any function exceeding 80 lines. Functions over 40 lines trigger a review comment.

#### 7.3.5 No Magic (C36.5)

- No implicit behavior — every side effect is visible at the call site or documented in the interface.
- No global mutable state (except the composition root).
- No surprising auto-imports, monkey-patching, or metaclass tricks without an ADR.
- **Explicit is better than implicit.**

#### 7.3.6 Comments Explain Why (C36.6)

Code explains *what* (by being readable). Comments explain *why*:
- Why a non-obvious algorithm was chosen.
- Why a constraint exists.
- Why an alternative was rejected.
- Why a magic number has its value.

**Forbidden:** comments that restate the code (`i += 1  # increment i`).
**Required:** docstrings on every public class/function describing contract, args, returns, and errors (this is a contract, not a "why" comment).

#### 7.3.7 Error Handling (C36.7, C12)

- Expected business outcomes use **Result types** (`Result.success(v)`, `Result.failure(err)`) — never exceptions (C12.3).
- Exceptions are reserved for **unexpected** failures (infrastructure crash, programmer error).
- Empty `except`/`catch` blocks are forbidden (C12.4).
- Every caught error is handled, logged+re-raised, or translated to a Result failure.
- Every error carries: code, message, category, severity, retryable, correlation_id (C12.2).

#### 7.3.8 Consistency Over Preference (C36.8)

When a pattern exists, follow it. Introduce a new pattern only via ADR. A developer's personal preference does not override codebase consistency.

---

## 08. Interfaces

This volume defines no code interfaces. It defines the **review interface** — the checklist a reviewer (human or automated) applies. See Sections 22 and 25.

---

## 09. Data Contracts

No data contracts are authored here. All contracts live in Volume 05 and conform to ADR-013.

---

## 10. Events

No events are authored here. Event contracts live in Volume 08 and conform to ADR-005 and C13.3.

---

## 11. State Machines

Not applicable at the principles level. State machines are defined per aggregate in Volume 06.

---

## 12. Algorithms

Not applicable. This volume governs *how we decide and write*, not *how we compute*.

---

## 13. Folder Structure

This volume governs **structure principles**, not the exact tree. The exact tree is Volume 02. Principle: the structure must make the dependency direction **visible** — a reader should see, from the folder layout alone, that Domain depends on nothing external.

---

## 14. Build Order

This volume is a **dependency of every other volume**. It must be read and accepted before any implementation volume is applied. Within itself, the three tiers (Philosophy → Architecture → Standards) are consumed top-down.

---

## 15. Public APIs

Not applicable.

---

## 16. Internal APIs

Not applicable.

---

## 17. Dependency Rules

This volume *is* the statement of dependency rules (C7). In practice:

- Source dependencies point **inward** only (C6.1, C7.1).
- Forbidden dependencies (C7.2) are enforced by `import-linter` (Python) and `dependency-cruiser` (TypeScript) in CI (C7.3).
- No circular dependencies — the graph is a DAG (C7.4).
- Contracts (Volume 05) is the shared hub all layers may reference (C7.5).

---

## 18. Performance Budget

This volume sets no specific budgets (those are per-operation in Volumes 06–16, per C24). It mandates that **budgets exist and are enforced** (C32.5). The principle of resource efficiency (C24.4) — DayFlow runs on user devices — means memory, CPU, disk, and network budgets are treated as first-class.

---

## 19. Security

Security principles are governed by Constitution §21 and detailed in Volume 09. This volume reinforces:
- Never trust input (C21.4) — validation at every boundary.
- Least privilege (C21.2) — for components, services, users.
- AI output is untrusted (C14.3, C21.9).

---

## 20. Failure Handling

Governed by Constitution §12 and §26. This volume reinforces fail-loud-fail-early (C4.4) and no-swallow (C12.4). Graceful degradation is specified per component in its `module.yaml` (C4.8).

---

## 21. Observability

Governed by Constitution §11 and detailed in Volume 17. This volume reinforces: every component ships observable (C11.6); never log sensitive data (C11.3).

---

## 22. Testing

Governed by Constitution §23, ADR-010, and detailed in Volume 19. This volume reinforces:
- Tests are first-class (C23.9).
- Unit tests are deterministic and fast (C23.3).
- The application core is testable without infrastructure (C6.4).

---

## 23. Acceptance Criteria

A change complies with this volume when **all** of the following hold:

1. The feature's architectural dependencies are merged and green (C3.1).
2. No business logic exists outside the Domain (C3.2).
3. All AI output passes through deterministic validation before mutation (C3.3).
4. Every significant state change publishes an event (C3.4).
5. Every external dependency is behind a port, swappable by config (C3.5).
6. The slice is complete (usable, tested, observable, documented, deployable) or it is in a branch (C3.7).
7. Naming, file size, and function size comply with C36.1–4.
8. Every class has a single responsibility (C36.2).
9. No magic; errors handled explicitly; comments explain why (C36.5–7).
10. The change follows existing patterns or introduces a new one via ADR (C36.8).
11. Observability is present (logging, metrics, tracing) (C11.6).
12. Dependencies are injected; the unit is testable in isolation (C4.7, C37).
13. The dependency direction is correct and enforced green in CI (C7.3).
14. No TODOs or placeholders remain (C40.2.15).

---

## 24. AI Coding Tasks

Not applicable at the principles level. Tasks that implement these standards are enumerated in Volume 20.

---

## 25. Done Definition

This volume's DoD is its **Acceptance Criteria** (Section 23). For the **global** DoD that every module must satisfy, see Constitution §40.2 (twenty criteria). This volume does not weaken C40; it operationalizes it.

A module is **not done** if it violates any principle in this volume, regardless of whether tests pass. Passing tests are necessary but not sufficient.

---

## Appendix A — Reviewer Quick-Reference Card

When reviewing a PR, ask:

1. **Architecture first?** Are upstream deps merged and green?
2. **Domain pure?** Any business logic outside Domain?
3. **AI untrusted?** Is AI output validated before mutation?
4. **Event published?** Did the state change publish an event?
5. **Replaceable?** Is the external dep behind a port?
6. **Slice complete?** Usable, tested, observable, documented, deployable?
7. **Names honest?** Does the name match the responsibility?
8. **Sizes ok?** File < 500, function < 80?
9. **One responsibility?** Can you describe the class in one sentence without "and"?
10. **No magic?** Is behavior explicit?
11. **Errors handled?** No swallowed exceptions? Results for business flow?
12. **Observable?** Logs (structured), metrics, tracing present?
13. **Testable?** Deps injected? Unit tests deterministic?
14. **Dependencies correct?** Inward only? CI green on import checks?
15. **No TODOs?** No placeholder implementations?

If any answer is "no," the PR is blocked.

---

## Appendix B — Smells and Their Root Causes

| Smell | Likely Root Cause (Constitution clause) |
|-------|----------------------------------------|
| Business logic in a controller/use case | C3.2 (Domain First) violated |
| AI directly mutating state | C3.3 (AI is not logic) violated |
| State change with no event | C3.4 (Event First) violated |
| Cannot swap a provider without touching Domain | C3.5 (Replaceability) violated |
| Half-built module in `main` | C3.7 (Slices) / C17.3 violated |
| Class named `...Manager` with vague scope | C36.2 (one responsibility) violated |
| File > 500 lines | C36.3 violated |
| Function > 80 lines | C36.4 violated |
| Comment restates code | C36.6 violated |
| Empty `except` block | C12.4 / C36.7 violated |
| Duplicate type across Python and TS | C4.3 / ADR-013 violated |
| Domain imports Infrastructure | C7.2 violated |
| Flaky test | C23.3 (determinism) violated |
| Component without metrics/logs | C11.6 violated |
| Secrets in code | C10.4 violated |

---

## Document Control

| Field | Value |
|-------|-------|
| **Document** | DIMP Volume 01 — Engineering Principles |
| **Version** | 1.0 |
| **Status** | FROZEN |
| **Date** | 2026-06-29 |
| **Governed By** | Constitution v3.0 (§3, §4, §36, §40) |
| **Builds On** | Volume 00 (ADR-009) |
| **Prerequisite For** | All implementation volumes (02–20) |

---

**— END OF VOLUME 01 —**
