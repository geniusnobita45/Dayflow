# Volume 00 — Architecture Lock

**Document Type:** Architecture Decision Records (Frozen)
**DIMP Volume:** 00
**Status:** FROZEN — No implementation begins until this volume is approved
**Date:** 2026-06-29
**Governed By:** Constitution v3.0
**Prerequisite For:** Every subsequent DIMP volume (01–20)

---

## 01. Executive Summary

This volume freezes every **irreversible engineering decision** for DayFlow before a single line of production code is written. Each decision is recorded as an **Architecture Decision Record (ADR)** following the Michael Nygard format. Once an ADR is marked **Accepted**, it is immutable; changing it requires a superseding ADR with full impact analysis.

The Architecture Lock exists because the cost of reversing a decision grows by orders of magnitude once code, contracts, and data depend on it. By freezing these decisions now, we trade a small upfront cost for enormous downstream stability.

This volume contains **15 ADRs** covering: technology stack, repository strategy, storage, eventing, AI providers, security, deployment, coding standards, testing, versioning, API strategy, contract strategy, observability, configuration, and the modular-monolith-to-services evolution path.

---

## 02. Objectives

1. **Eliminate architectural ambiguity** before implementation begins.
2. **Make every major decision explicit, documented, and reviewable.**
3. **Establish a frozen baseline** that all DIMP volumes implement against.
4. **Define the cost of change** for each decision (so future engineers understand what reversing a decision entails).
5. **Satisfy Constitution C40.6** — decisions that are hard to reverse require an ADR.

---

## 03. Scope

**In scope:**
- Technology selection (languages, frameworks, databases, cloud).
- Architectural patterns (monorepo, layered architecture, event-driven).
- Cross-cutting strategy (security, observability, versioning, contracts).
- Deployment topology and evolution path.

**Out of scope:**
- Module-level design (handled in Volumes 04–16).
- Implementation details (handled in code).
- Operational runbooks (handled in Volume 17).
- Testing specifics per module (handled in Volume 19).

---

## 04. Out of Scope

See Section 03 above. This volume makes **decisions**; it does not specify **how those decisions are implemented**. Implementation belongs to Volumes 01–20.

---

## 05. Constitution Mapping

| ADR | Constitution Clause |
|-----|--------------------|
| ADR-001 (Tech Stack) | C3.8 (boring infrastructure), C14 (AI-first), C16 (local-first) |
| ADR-002 (Monorepo) | C18.1 (monorepo), C18.2 (why) |
| ADR-003 (Clean Architecture) | C6 (Clean Architecture), C7 (Dependency Rules) |
| ADR-004 (Storage) | C28 (Storage Strategy), C27 (Data Integrity) |
| ADR-005 (Eventing) | C13 (Event-Driven), C13.2 (Event Sourcing) |
| ADR-006 (AI Providers) | C14 (AI-First), C15 (Replaceability) |
| ADR-007 (Security) | C21 (Security), C22 (Privacy) |
| ADR-008 (Deployment) | C34 (CI/CD), C39 (Release) |
| ADR-009 (Coding Standards) | C36 (Coding Standards), C36.3–4 (size limits) |
| ADR-010 (Testing) | C23 (Testing), C23.2 (pyramid) |
| ADR-011 (Versioning) | C30 (Versioning), C9 (Contracts First) |
| ADR-012 (API Strategy) | C29 (API Design), C29.1 (API-first) |
| ADR-013 (Contracts) | C9 (Contracts First), C9.1 (single source) |
| ADR-014 (Observability) | C11 (Observability), C11.3 (never log sensitive) |
| ADR-015 (Modular Monolith) | C20.7 (start modular, evolve) |

---

## 06. Architecture

The Architecture Lock establishes the **decision spine** of DayFlow:

```
ADR-001 Tech Stack (Python + TypeScript)
    │
    ├── ADR-002 Monorepo (single repo, workspaces)
    │       └── ADR-003 Clean Architecture (layered, ports & adapters)
    │               └── ADR-013 Contracts First (OpenAPI + JSON Schema → generated)
    │
    ├── ADR-004 Storage (polyglot: PostgreSQL + pgvector + Redis + blob)
    │       └── ADR-005 Eventing (event sourcing for critical aggregates)
    │
    ├── ADR-006 AI Providers (multi-provider, local-first)
    │
    ├── ADR-015 Modular Monolith → evolve to services
    │       └── ADR-012 API Strategy (REST + streaming, API-first)
    │
    ├── ADR-007 Security (defense in depth, encrypted everywhere)
    ├── ADR-014 Observability (logs + metrics + tracing)
    ├── ADR-008 Deployment (containerized, CI/CD, feature flags)
    ├── ADR-011 Versioning (SemVer everywhere)
    ├── ADR-009 Coding Standards (ruff, mypy, eslint, prettier)
    └── ADR-010 Testing (pyramid, coverage gates)
```

---

## 07. Components

Each ADR is a component of the lock. The 15 ADRs are enumerated in Sections 08–22.

---

## 08. Interfaces

The Architecture Lock defines no code interfaces. It defines **decision interfaces** — the constraints that subsequent volumes must satisfy. Each ADR's "Consequences" section enumerates the obligations it imposes on downstream volumes.

---

## 09. Data Contracts

No data contracts are defined at this level. Data contracts are authored in Volume 05 (Contracts & APIs) and must conform to ADR-013.

---

## 10. Events

No events are defined at this level. Event schemas are authored in Volume 08 (Event Platform) and must conform to ADR-005.

---

## 11. State Machines

Not applicable at the Architecture Lock level.

---

## 12. Algorithms

Not applicable. The Architecture Lock makes decisions, not algorithmic choices.

---

## 13. Folder Structure

```
docs/
  adr/
    adr-001-technology-stack.md
    adr-002-monorepo-strategy.md
    adr-003-clean-architecture.md
    adr-004-storage-strategy.md
    adr-005-event-driven-architecture.md
    adr-006-ai-provider-strategy.md
    adr-007-security-architecture.md
    adr-008-deployment-strategy.md
    adr-009-coding-standards.md
    adr-010-testing-strategy.md
    adr-011-versioning-strategy.md
    adr-012-api-strategy.md
    adr-013-contract-strategy.md
    adr-014-observability-strategy.md
    adr-015-modular-monolith-evolution.md
    README.md
  engineering/
    volume-00-architecture-lock.md   ← this document (summary of all)
```

Each ADR is also summarized inline below (Sections 14–28).

---

## 14. Build Order

The ADRs are presented in dependency order. ADR-001 (Tech Stack) is foundational; ADR-015 (Evolution) is terminal. However, all 15 are **locked simultaneously** — none enters a "proposed" state while others are accepted.

---

## 15. Public APIs

Not applicable.

---

## 16. Internal APIs

Not applicable.

---

## 17. Dependency Rules

The Architecture Lock is the highest-level dependency. Every DIMP volume **must conform** to the accepted ADRs. A volume that contradicts an accepted ADR is itself defective.

---

## 18. Performance Budget

No specific performance budgets are set here (those are per-module in Volumes 06–16). The Lock establishes that **performance budgets are mandatory** (C24) and enforced in CI (C32).

---

## 19. Security

ADR-007 establishes the security posture. All other ADRs are reviewed for security implications.

---

## 20. Failure Handling

If an ADR is found to be flawed after acceptance, the process is:
1. Author a **superseding ADR** with full context.
2. Conduct **impact analysis** across all affected code and volumes.
3. Mark the old ADR **Superseded**, the new one **Accepted**.
4. Update all dependent volumes.

---

## 21. Observability

ADR-014 establishes the observability posture.

---

## 22. Testing

ADR-010 establishes the testing strategy.

---

## 23. Acceptance Criteria

The Architecture Lock is **accepted** when:
1. All 15 ADRs are reviewed.
2. Each ADR is marked **Accepted**.
3. No open objections remain.
4. The Constitution compliance check (Section 05) passes for every ADR.

---

## 24. AI Coding Tasks

Not applicable. This volume is human-reviewed architecture decisions. AI agents implement downstream volumes.

---

## 25. Done Definition

This volume is **done** when:
- [x] All 15 ADRs are documented.
- [x] Each ADR follows the Nygard format (Context, Decision, Consequences, Status).
- [x] Constitution mapping is complete.
- [x] Every ADR is marked **Accepted**.
- [x] Downstream volume dependencies are enumerated.

---

---

# ADR-001 — Technology Stack

**Status:** Accepted
**Date:** 2026-06-29
**Supersedes:** DIMP v1.0 Flask prototype

## Context

DayFlow is an AI-native, local-first personal intelligence system intended for decades of use (C2.5). The technology stack must satisfy three competing demands:

1. **Boring infrastructure** (C3.8) — proven, reliable, well-understood for the platform/storage layers.
2. **Exciting intelligence** (C3.8) — the best available tooling for AI/reasoning/embedding.
3. **Local-first** (C3.6, C16) — must run on user devices (laptops, phones, desktops) with minimal resource footprint.

Python dominates the AI/ML ecosystem. TypeScript dominates cross-platform UI (web, mobile via React Native, desktop via Electron/Tauri). A single language cannot satisfy both demands without compromise.

The existing prototype (Flask + SQLite + vanilla JS) is a throwaway; it does not constrain this decision.

## Decision

DayFlow uses a **polyglot stack**:

| Layer | Technology | Rationale |
|-------|-----------|-----------|
| **Domain, Application, Infrastructure, Services** | **Python 3.12+** | Dominant AI ecosystem; rich typing; Clean Architecture friendly. |
| **API layer** | **FastAPI** | Async, typed (Pydantic), OpenAPI-native, high-performance. |
| **Web app** | **Next.js (React, TypeScript)** | SSR, routing, ecosystem, shared types with contracts. |
| **Mobile app** | **React Native (TypeScript)** | Code sharing with web; local-first capable. |
| **Desktop app** | **Tauri (Rust shell, TS frontend)** | Lightweight, secure, native. |
| **Data validation / contracts** | **Pydantic v2 (Python), Zod (TS)** | Schema validation at boundaries. |
| **Type-safe ORM** | **SQLAlchemy 2.0** | Mature, typed, repository-pattern friendly. |
| **Vector operations** | **NumPy / pgvector** | Standard, replaceable. |

**Frontend-backend type sharing** is achieved via **code generation from contracts** (ADR-013), never manual duplication.

## Consequences

**Positive:**
- Each language plays to its strength.
- AI ecosystem is first-class.
- Frontend can be shared across web/mobile/desktop.
- Contracts generation guarantees type parity.

**Negative:**
- Two toolchains to maintain (Python + TypeScript).
- Two sets of lint/format/test configs.
- Code generation adds a build step.
- Team must be proficient in both ecosystems.

**Obligations on downstream volumes:**
- Volume 02 (Repository Foundation) must define the dual workspace structure.
- Volume 05 (Contracts & APIs) must define the generation pipeline.
- Volume 03 (Developer Experience) must provide unified tooling for both.

---

# ADR-002 — Monorepo Strategy

**Status:** Accepted
**Date:** 2026-06-29

## Context

DayFlow spans backend (Python), frontend (TypeScript), shared contracts, infrastructure, docs, and tests. C18.1 mandates a monorepo. The question is *how* the monorepo is structured and managed across two language ecosystems.

## Decision

DayFlow is a **single Git monorepo** managed with **dual workspaces**:

- **Python workspace:** `uv` workspaces (or pip editable installs as fallback) with a root `pyproject.toml`.
- **TypeScript workspace:** `pnpm` workspaces with a root `package.json`.

The repository is organized **by architectural layer** at the top level (`packages/`, `apps/`, `services/`), and **by bounded context** within each package. See Volume 02 for the complete layout.

**Branching:** `trunk-based development` with short-lived feature branches. Long-lived branches are forbidden (C34.1).

## Consequences

**Positive:**
- Atomic cross-stack changes (one commit touches Python + TS + contracts).
- Unified CI/CD.
- Internal packages always compatible (path references, not version pins).
- Single history, single source of truth.

**Negative:**
- Larger repository; slower clones (mitigated by sparse checkout / partial clone).
- CI must be smart (only run affected paths).
- Two package managers to coordinate.

**Obligations:**
- Volume 02 must specify the complete directory tree.
- Volume 05 must specify how generated contracts land in both workspaces.

---

# ADR-003 — Clean Architecture (Layered, Ports & Adapters)

**Status:** Accepted
**Date:** 2026-06-29
**Governed By:** C6, C7, C8

## Context

C6 mandates Clean Architecture. C7 mandates strict dependency rules. The question is the concrete layering and the enforcement mechanism.

## Decision

DayFlow adopts a **5-layer architecture**:

```
Presentation → Application → Domain
                   ↑
            Infrastructure (implements Application ports)
```

Plus a cross-cutting **Contracts** package (no logic, only types/schemas) that all layers may depend on.

**Layer contents** (authoritative — see C8):

- **Domain** — entities, value objects, domain events, enums, invariants, specifications, domain services. Zero external deps.
- **Application** — use cases (commands/queries), ports (interfaces), application services, transaction boundaries, authorization.
- **Infrastructure** — repository implementations, AI provider adapters, messaging, cache, storage, external clients.
- **Presentation** — API controllers, UI components, serializers.
- **Contracts** — DTOs, event schemas, error contracts, OpenAPI specs. No logic.

**Enforcement:** Automated dependency-rule checking in CI (import-linter for Python, dependency-cruiser for TypeScript). The build fails on any violation. See Volume 05 and C32.3.

## Consequences

**Positive:**
- The application core (Domain + Application) is pure and fully testable without infrastructure.
- Providers are swappable (C15).
- Clear ownership boundaries.

**Negative:**
- More files, more indirection than a flat structure.
- Requires discipline to keep layers pure.
- Enforcement tooling must be maintained.

**Obligations:**
- Volume 05 defines the Contracts package and generation.
- Volume 06 defines the Domain model.
- Volume 07 defines repository interfaces and storage adapters.

---

# ADR-004 — Storage Strategy (Polyglot Persistence)

**Status:** Accepted
**Date:** 2026-06-29
**Governed By:** C28, C27

## Context

DayFlow has diverse data shapes: relational (users, tasks), time-series events, high-dimensional vectors (embeddings), graph relationships (knowledge), large blobs (files). C28.1 mandates polyglot persistence. C28.2 mandates repository abstraction. C3.8 favors boring infrastructure.

## Decision

| Data Shape | Engine | Why |
|-----------|--------|-----|
| **Relational + JSON documents** | **PostgreSQL 16+** | Boring, reliable, rich (JSONB, FTS, extensions). Single primary store. |
| **Vector embeddings** | **pgvector (PostgreSQL extension)** | No separate vector DB initially; reduces operational surface. Replaceable (C15). |
| **Event store** | **PostgreSQL (event tables)** | Transactional with relational data initially; replaceable with dedicated event store later. |
| **Graph (knowledge)** | **PostgreSQL with adjacency + recursive queries** | Boring; dedicated graph DB (Neo4j) deferred until query patterns demand it. |
| **Hot cache** | **Redis** | Standard, boring, fast. |
| **Blob storage** | **Local filesystem (local-first) / S3-compatible (cloud)** | Replaceable behind blob port. |
| **Full-text search** | **PostgreSQL FTS** | Initially; replaceable with dedicated search (Meilisearch/Typesense) later. |

**Principle:** Start with PostgreSQL as the single boring engine, add dedicated stores only when query patterns or scale demand it. Every store is behind a repository interface (C28.2).

## Consequences

**Positive:**
- One database to operate initially → lower operational complexity.
- Transactional consistency between relational and event data.
- pgvector avoids a separate vector DB until needed.
- All replaceable (C15).

**Negative:**
- PostgreSQL is not the best vector engine at extreme scale — but DayFlow is per-user partitioned (C25.2), so scale is bounded per tenant.
- Graph queries in SQL are less ergonomic than a native graph DB — deferred.

**Obligations:**
- Volume 07 (Storage) specifies repository interfaces, migrations, indexing, backup, partitioning.
- Volume 11 (Memory) and Volume 12 (Knowledge) define vector/graph query patterns.

---

# ADR-005 — Event-Driven Architecture & Event Sourcing

**Status:** Accepted
**Date:** 2026-06-29
**Governed By:** C13

## Context

C13.1 mandates events as immutable facts. C13.2 mandates event sourcing for critical aggregates. C3.4 mandates "Event First." The question is the scope of event sourcing and the delivery mechanism.

## Decision

**Event sourcing** applies to aggregates whose history matters:
- Memory (every capture, consolidation, retrieval).
- Knowledge Graph (every node/edge change).
- Productivity (Tasks, Goals, Habits — progress tracking).
- Reflection (every reflection, insight).

**Event sourcing does NOT apply** to:
- Pure configuration (settings, feature flags — these are state, not history).
- Read-optimized projections.
- Ephemeral state (cache).

**Delivery:** At-least-once delivery (C13.5). Consumers are idempotent (C4.5). An in-process event bus is used initially (modular monolith, ADR-015); this evolves to a message broker (NATS or Kafka) when services are extracted.

**Projections:** Read models are projections derived from the event log. Multiple projections may exist for the same events (C13.6). Projections are rebuildable.

**Dead Letter Queue:** Unprocessable events go to a DLQ (C13.7); never silently dropped.

**Event schema versioning:** Events carry a schema version in the envelope (C30.4). Forward-compatible evolution is preferred.

## Consequences

**Positive:**
- Full auditability and replayability.
- Time-travel debugging.
- Decoupled projections and consumers.

**Negative:**
- Eventual consistency between write and read models.
- Complexity of projection management.
- Event schema evolution discipline required.

**Obligations:**
- Volume 08 (Event Platform) specifies the bus, store, projections, replay, DLQ.

---

# ADR-006 — AI Provider Strategy (Multi-Provider, Local-First)

**Status:** Accepted
**Date:** 2026-06-29
**Governed By:** C14, C15, C16

## Context

C14 mandates AI as first-class. C15 mandates replaceability. C16 mandates local-first. C14.7 prefers local AI where possible. C3.5 mandates all providers behind interfaces. The strategy must support local models (privacy, offline), cloud models (capability), and graceful fallback.

## Decision

**All AI capabilities are behind ports:**
- `LLMProvider` port — completion, chat, streaming.
- `EmbeddingProvider` port — embed text → vector.
- `VectorStore` port — similarity search (ADR-004: pgvector adapter).
- `TranscriptionProvider` port — audio → text (future).
- `ImageProvider` port — vision (future).

**Multi-provider with routing, fallback, A/B (C15.4):**
- A **router** selects the provider per task (configurable by capability, cost, latency, privacy).
- **Fallback chains:** if provider A fails/times out, try provider B.
- **A/B testing:** route a percentage of traffic to a candidate provider for evaluation.

**Local-first providers (C16.4):**
- Local LLM via **Ollama** (or llama.cpp) — for privacy-sensitive, offline tasks.
- Local embeddings via **sentence-transformers / bge models**.
- Local vector search via pgvector.

**Cloud providers (behind the same port):**
- LLM: OpenAI, Anthropic, Google (configurable).
- Embedding: OpenAI, Cohere, local.

**AI Governance (C14.5):** every call logged (no content, C11.3), cost/latency budget per call, prompt versioning (C14.6), disable-able (graceful degradation).

## Consequences

**Positive:**
- No vendor lock-in.
- Privacy-preserving local path.
- Graceful degradation when cloud is unavailable.
- Cost control via routing.

**Negative:**
- Abstraction overhead — provider-specific features must be generalized.
- Local models require significant device resources.
- Quality variance between providers must be managed.

**Obligations:**
- Volume 10 (AI Infrastructure) specifies the ports, router, registry, governance.
- Volume 03 (Developer Experience) provides mock providers for testing.

---

# ADR-007 — Security Architecture

**Status:** Accepted
**Date:** 2026-06-29
**Governed By:** C21, C22

## Context

C21 mandates security by design. C22 mandates privacy as architectural. DayFlow stores the user's most personal data (thoughts, memories). The threat model includes: credential compromise, data exfiltration, prompt injection, supply-chain attacks, lost device.

## Decision

- **Authentication:** OAuth 2.1 / OIDC for cloud; local passphrase + key derivation (Argon2id) for local-first. Session tokens are short-lived JWTs with refresh rotation.
- **Authorization:** Enforced at the **use case** level (C21.7), not just API. RBAC + ownership checks.
- **Encryption at rest:** Database (PostgreSQL TDE or volume encryption), blob, local device storage (keys derived from user passphrase).
- **Encryption in transit:** TLS 1.3 (minimum 1.2, C21.5).
- **Secrets:** Never in code (C10.4). Secret manager in prod, `.env` (gitignored) locally.
- **Input validation:** All input untrusted (C21.4). Pydantic/Zod at every boundary.
- **AI input/output:** AI output treated as untrusted input (C14.3, C21.9). Prompt injection defense via validation.
- **Audit log:** Append-only, tamper-evident (C21.8).
- **Rate limiting:** At API gateway and per-endpoint (C29.8).
- **Dependency scanning:** Automated SBOM + vulnerability scanning in CI.
- **Threat modeling:** Per significant feature, updated in ADRs.

## Consequences

**Positive:**
- Defense in depth (C21.3).
- Privacy by architecture.
- Auditability.

**Negative:**
- Higher implementation cost per feature.
- Performance overhead of encryption/validation.
- Operational overhead of key management.

**Obligations:**
- Volume 09 (Security) specifies the full threat model, controls, and testing.

---

# ADR-008 — Deployment Strategy

**Status:** Added
**Date:** 2026-06-29
**Governed By:** C34, C39

## Context

DayFlow has two deployment surfaces: (1) cloud services (platform, AI brain), (2) client apps (web, mobile, desktop) running on user devices. C16 makes the client the primary home. C39 governs release management.

## Decision

- **Containerization:** All cloud services packaged as **OCI containers** (Docker), described by a multi-stage Dockerfile per service.
- **Orchestration:** Initially **docker-compose** for local/dev; **Kubernetes** for production (deferred until scale demands — start with a single-node or managed offering).
- **Client apps:** Web (Next.js) deployed to edge/CDN; mobile (React Native) via app stores; desktop (Tauri) via auto-update.
- **CI/CD:** GitHub Actions (C34). Trunk-based. Every merge to main is deployable. Feature flags decouple deploy from release (C31).
- **Deployment strategies:** Blue-green for services; canary for risky changes; rolling for routine (C39.3).
- **Rollback:** Every deploy is reversible (C34.5, C39.5). Migrations are non-destructive (C27.5).
- **IaC:** Terraform for cloud infrastructure (ADR mention; detailed in Volume 18).
- **Environments:** dev → staging → production. Parity enforced (C34.4).

## Conferences

**Positive:**
- Reproducible, automated deployments.
- Low-risk releases via flags + canary.
- Reversible.

**Negative:**
- Container + K8s operational complexity (deferred to necessity).
- IaC maintenance.

**Obligations:**
- Volume 18 (Production & Release) details pipelines, environments, rollback.

---

# ADR-009 — Coding Standards & Tooling

**Status:** Accepted
**Date:** 2026-06-29
**Governed By:** C36

## Context

C36 defines naming, file/function size limits, and one-class-one-responsibility. The decision is the concrete toolchain that enforces these.

## Decision

**Python:**
- **Formatter + Linter:** `ruff` (replaces black + isort + flake8).
- **Type checker:** `mypy` in strict mode.
- **Test runner:** `pytest` + `pytest-asyncio` + `pytest-cov`.
- **Import linting:** `import-linter` (enforces layer dependency rules, C7.3).
- **Pre-commit:** `pre-commit` hooks for ruff, mypy, secrets detection.

**TypeScript:**
- **Formatter:** `prettier`.
- **Linter:** `eslint` (flat config).
- **Type checker:** `tsc` strict.
- **Test runner:** `vitest` (fast, Vite-native) or `jest`.
- **Import linting:** `dependency-cruiser` (enforces layer rules).
- **Bundler:** `tsup`/`tsc` for libraries; Next.js/Vite for apps.

**Cross-cutting:**
- `.editorconfig` for consistent formatting across editors.
- `Makefile` / `task` runner for unified commands.
- File-size guard: CI fails if any `.py`/`.ts` file exceeds 500 lines (C36.3).
- Function-size guard: CI fails if any function exceeds 80 lines (C36.4).

## Consequences

**Positive:**
- Automated enforcement of C36.
- Fast feedback (ruff, tsc are fast).
- Consistent style across the codebase.

**Negative:**
- Tooling maintenance.
- Strict mypy can slow development; mitigated by allowing escape hatches with review.

**Obligations:**
- Volume 02 (Repository Foundation) specifies configs.
- Volume 19 (Testing) specifies test structure.

---

# ADR-010 — Testing Strategy

**Status:** Accepted
**Date:** 2026-06-29
**Governed By:** C23

## Context

C23 mandates the test pyramid, meaningful coverage, determinism, and coverage gates. The decision is the concrete strategy, tools, and thresholds.

## Decision

**Pyramid (C23.2):**
- **Unit (many):** pytest (Python), vitest/jest (TS). Isolated, mocked deps. Deterministic. Fast.
- **Integration (some):** TestContainers (real PostgreSQL, Redis) for repository/adapter tests. Mock external AI providers with fakes.
- **Contract (per service boundary):** Pact-style or schema-based. Consumers test against the contract, not the implementation.
- **E2E (few):** Playwright (web). Covers critical user flows only.

**Property-based:** `hypothesis` (Python) for invariant testing of domain logic.

**Performance:** `pytest-benchmark` / `k6` for critical paths. Enforced budgets (C24).

**Coverage gates (C23.8):**
| Layer | Min Coverage |
|-------|-------------|
| Domain | ≥ 95% |
| Application | ≥ 90% |
| Infrastructure | ≥ 80% |
| Presentation | ≥ 70% |

**Determinism:** No network in unit tests. Clocks injected (C4.7). Randomness injected. No `time.sleep` in tests.

## Consequences

**Positive:**
- High confidence in correctness.
- Fast feedback from unit suite.
- Contract tests prevent breaking changes.

**Negative:**
- Test maintenance cost.
- Integration/E2E suites are slower.

**Obligations:**
- Volume 19 (Testing Master Plan) details per-module test plans.

---

# ADR-011 — Versioning Strategy

**Status:** Accepted
**Date:** 2026-06-29
**Governed By:** C30

## Context

C30 mandates versioning of Constitution, DIMP, APIs, contracts, events, packages, schema, prompts. The decision is the concrete scheme.

## Decision

| Artifact | Scheme | Detail |
|----------|--------|--------|
| **Constitution** | vMAJOR.MINOR | v3.0. Frozen. |
| **DIMP Volumes** | vMAJOR.MINOR | Per volume. |
| **APIs** | URL path | `/v1/`, `/v2/`. Old versions deprecated, not immediately removed. |
| **Contracts** | SemVer | Breaking bumps major. |
| **Events** | Schema version in envelope | `schema_version: N`. Forward-compatible preferred. |
| **Packages** | SemVer | `MAJOR.MINOR.PATCH`. |
| **DB schema** | Migration number | Sequential, ordered. Down-migrations where safe. |
| **Prompts** | SemVer | Evaluated before bump. |

**Deprecation policy:** Old API versions supported for ≥ 2 minor releases after deprecation. Breaking contract changes require migration guide.

## Consequences

**Positive:**
- Predictable evolution.
- Consumers can pin.
- Safe breaking changes with deprecation windows.

**Negative:**
- Multiple versions to support simultaneously.
- Migration effort.

**Obligations:**
- Volume 05 (Contracts) defines contract versioning.
- Volume 18 (Release) defines release versioning.

---

# ADR-012 — API Strategy (REST + Streaming, API-First)

**Status:** Accepted
**Date:** 2026-06-29
**Governed By:** C29

## Context

C29 mandates API-first design. C29.6 mandates streaming for long-running ops. The decision is the concrete API style and conventions.

## Decision

- **Style:** REST (resource-oriented). HTTP methods express intent. Standard status codes. Predictable URLs.
- **Specification:** OpenAPI 3.1. Spec is authored **before** implementation (C29.1, C9.5).
- **Streaming:** Server-Sent Events (SSE) for AI responses, partial results. WebSocket reserved for real-time bidirectional (future sync).
- **Pagination:** Cursor-based for collections (C29.4).
- **Filtering/Sorting:** Consistent query-param conventions (documented in OpenAPI).
- **Errors:** Uniform error contract (C12.2) across all endpoints.
- **Idempotency:** Mutating endpoints accept `Idempotency-Key` header (C29.7).
- **Versioning:** URL versioning (ADR-011).
- **Rate limiting:** Communicated via `X-RateLimit-*` headers (C29.8).
- **Auth:** Bearer token (JWT) per ADR-007.
- **Content negotiation:** `application/json` default; `application/x-ndjson` for streams.

## Consequences

**Positive:**
- Predictable, standards-based APIs.
- Streaming for AI UX.
- Contract-driven (consumers can be generated).

**Negative:**
- REST is not optimal for every pattern (e.g., complex actions) — mitigated with sub-resources / actions.

**Obligations:**
- Volume 05 (Contracts & APIs) defines OpenAPI specs and generation.

---

# ADR-013 — Contract Strategy (Single Source of Truth)

**Status:** Accepted
**Date:** 2026-06-29
**Governed By:** C9

## Context

C9.1 mandates a single source of truth for cross-boundary types, generated to all consuming languages. C9.3 forbids hand-editing generated code. The decision is the concrete pipeline.

## Decision

**Source of truth:** `packages/contracts/` containing:
- `openapi/` — OpenAPI 3.1 specs (API contracts).
- `schemas/` — JSON Schema (event schemas, shared DTOs).
- `events/` — event definitions (name, version, payload schema).

**Generation pipeline:**
```
packages/contracts/ (source, hand-authored)
    ↓ openapi-generator / datamodel-code-generator
packages/contracts-py/  (generated Python Pydantic models)
packages/contracts-ts/  (generated TypeScript types + Zod schemas)
    ↓ consumed by
application, infrastructure, presentation, sdk
```

**Rules:**
- Generated packages are **read-only**. A CI check verifies no manual edits.
- Contracts are versioned (ADR-011).
- Contract changes trigger regeneration + downstream test runs.
- No DTO is hand-written in application/infrastructure/presentation. If a type crosses a boundary, it lives in contracts.

**Shared enums:** Defined in contracts, generated to both languages. Ensures value parity (e.g., `TaskStatus.COMPLETED`).

## Consequences

**Positive:**
- Zero type duplication across languages.
- Contract changes propagate automatically.
- API and event schemas are always in sync with code.

**Negative:**
- Generation adds a build step.
- Generator limitations may require custom templates.
- Slight friction for rapid iteration (must update contract first).

**Obligations:**
- Volume 05 (Contracts & APIs) defines the full pipeline and tooling.

---

# ADR-014 — Observability Strategy

**Status:** Accepted
**Date:** 2026-06-29
**Governed By:** C11

## Context

C11 mandates structured logging, metrics, distributed tracing as designed-in (not bolted on). C11.3 forbids logging sensitive data. The decision is the concrete stack.

## Decision

**Three pillars (C11.1):**

1. **Structured Logging** — `structlog` (Python) producing JSON. Every log carries the 8 mandatory fields (C11.2). Log level configurable per module. Sensitive-data redaction filter enforced.
2. **Metrics** — Prometheus exposition format. Counters, histograms, gauges. Named `module_operation_metric`. Scraped by Prometheus, visualized in Grafana.
3. **Distributed Tracing** — OpenTelemetry (OTel). Trace context propagated across service/process boundaries (W3C TraceContext). Spans for significant operations.

**Client-side observability:** Lightweight — error reporting + performance marks. Privacy-preserving (no content).

**Alerting:** Alertmanager (Prometheus). On-call rotation (Volume 17).

**Never logged (C11.3):** thought content, memory content, API keys, tokens, secrets, passwords, PII, encryption keys. Enforced by a redaction filter + automated scanning of log samples.

## Consequences

**Positive:**
- End-to-end request visibility.
- Performance and reliability insights.
- Privacy preserved.

**Negative:**
- Observability overhead per component.
- Storage cost for logs/traces (mitigated by retention policies).

**Obligations:**
- Volume 17 (Operations & Observability) details dashboards, alerts, runbooks.

---

# ADR-015 — Modular Monolith → Services Evolution

**Status:** Accepted
**Date:** 2026-06-29
**Governed By:** C20.7

## Context

C20.7 mandates starting as a modular monolith and extracting services only when operationally justified. Premature decomposition is forbidden. The decision is the evolution path.

## Decision

**Phase 1 — Modular Monolith (now):**
- Single deployment unit containing Platform, AI Brain, Scheduler as **strict modules** with hard boundaries.
- Modules communicate via in-process event bus (ADR-005) and direct port calls.
- No shared database tables across modules (logical separation within one PostgreSQL).
- Each module has its own `module.yaml`, contracts, and tests.

**Phase 2 — Selective Extraction (when justified):**
- A module is extracted to a separate service **only when**: independent scaling is needed, or failure isolation is needed, or team boundaries demand it.
- Extraction is mechanical: the in-process bus becomes a message broker (NATS/Kafka); port calls become HTTP/gRPC.
- Contracts do not change (they were already cross-module).

**Phase 3 — Full Service Mesh (if ever):**
- Multiple services, service mesh, dedicated event store, dedicated vector store.
- This is **not** a goal; it is an option if scale demands it.

**Invariant:** The Domain and Application layers **never know** whether they run in-process or as a service. This is guaranteed by ports and adapters (ADR-003).

## Consequences

**Positive:**
- Low operational complexity initially.
- Avoids distributed-system pitfalls early.
- Extraction path is clear when needed.

**Negative:**
- Risk of boundary erosion if discipline slips.
- Single deployment unit means coordinated releases initially.

**Obligations:**
- Volume 04 (Platform Core) and downstream volumes enforce module boundaries.
- Volume 18 (Production) defines the extraction procedure.

---

## Document Control

| Field | Value |
|-------|-------|
| **Document** | DIMP Volume 00 — Architecture Lock |
| **Version** | 1.0 |
| **Status** | FROZEN (pending final review) |
| **Date** | 2026-06-15 |
| **Author** | DayFlow Architecture |
| **Governed By** | Constitution v3.0 |
| **Prerequisite For** | DIMP Volumes 01–20 |
| **Amendment** | Superseding ADR required (C40.6) |

---

**— END OF VOLUME 00 —**
