# DayFlow Constitution v3.0

**Document Type:** Governing Architecture Charter
**Status:** FROZEN — Immutable
**Version:** 3.0
**Date Frozen:** 2026-06-29
**Supersedes:** Constitution v2.x, Constitution v1.x
**Authority:** Supreme architectural source of truth for DayFlow

---

## How to Read This Document

### 1.1 — What This Document Is

The Constitution is the **supreme governing architecture charter** for DayFlow. It defines *what DayFlow is* and *the inviolable rules under which it is built*. It does not define *how* — that is the responsibility of the DayFlow Implementation Master Plan (DIMP v3.1), which translates every rule in this document into executable engineering specification.

### 1.2 — Hierarchy of Authority

```
Constitution v3.0            ← Supreme. Never changes during implementation.
        │
        ▼
DIMP v3.1 (Volumes 00–20)    ← Implementing. Evolves within Constitution bounds.
        │
        ▼
ADRs                          ← Decisions. Frozen once accepted.
        │
        ▼
module.yaml                   ← Module-specific. Owned by module owner.
        │
        ▼
Source Code                   ← Ultimate implementation.
```

**Rule of Supremacy:** Whenever any document, decision, code, or discussion conflicts with this Constitution, the Constitution wins. No exceptions.

### 1.3 — Immutability Clause

This Constitution is **frozen**. It may only be amended through a formal Constitutional Amendment Process (see §40.6), which requires:

1. A written amendment proposal.
2. Impact analysis across all affected DIMP volumes.
3. Architecture Review Board approval.
4. Updated DIMP cross-references.

Until amended through this process, **every word in this document is law.**

### 1.4 — Citation Format

This document is cited throughout the DIMP using the notation:

```
C{section}.{subsection}
```

Examples:
- `C3.1` → Section 3, subsection 1
- `C7.4` → Section 7, subsection 4
- `C12` → Section 12 in its entirety

Every DIMP volume's Section 05 (Constitution Mapping) cites the specific clauses it implements.

### 1.5 — Defined Terms

| Term | Definition |
|------|-----------|
| **DayFlow** | The complete system — product, platform, AI, infrastructure. |
| **Constitution** | This document, in its entirety. |
| **DIMP** | DayFlow Implementation Master Plan (Volumes 00–20 + MASTER_INDEX). |
| **ADR** | Architecture Decision Record. |
| **Module** | A unit of code with a single responsibility and a `module.yaml`. |
| **Aggregate** | A cluster of domain objects treated as a single unit (DDD). |
| **Port** | An interface defining a contract between layers. |
| **Adapter** | An implementation of a Port. |
| **Slice** | A vertical, end-to-end, production-ready increment. |
| **Gate** | A quality checkpoint that must pass before proceeding. |

---

## Section 2 — Vision

### 2.1 — What DayFlow Is

DayFlow is an **AI-native, local-first personal intelligence system** that transforms a person's thoughts, goals, habits, and reflections into a continuously learning digital mind. It is not a to-do list. It is not a notes app. It is not a calendar. It is a **thinking partner** that remembers, connects, plans, and coaches — growing more useful the longer you use it.

### 2.2 — The Core Promise

> **Every thought you capture makes DayFlow smarter. Every goal you set makes DayFlow wiser. Every day you use DayFlow makes your future clearer.**

### 2.3 — System Character

DayFlow is:

- **Personal** — Belongs to one human. Their data, their mind, their rules.
- **Intelligent** — Learns from patterns, predicts outcomes, suggests actions.
- **Calm** — Never demands attention. Earns it through value.
- **Persistent** — Remembers everything that matters, forgets nothing useful.
- **Private** — The user's mind is sacred. Privacy is architectural, not a setting.
- **Local-first** — Runs on the device whenever safe. Cloud extends, never replaces.

### 2.4 — The Digital Mind Metaphor

DayFlow models itself on human cognition:

| Cognitive Faculty | DayFlow Implementation |
|-------------------|----------------------|
| **Memory** | Captures thoughts, experiences, knowledge; retrieves by meaning. |
| **Knowledge** | Builds a graph of concepts, entities, and relationships. |
| **Reasoning** | Plans, decides, predicts, reflects, creates. |
| **Reflection** | Reviews patterns, draws insight, refines understanding. |
| **Prediction** | Forecasts outcomes, trajectories, and probabilities. |
| **Coaching** | Guides, nudges, advises — never commands. |
| **Habits** | Recognizes routines, reinforces positive patterns. |

### 2.5 — Long-Horizon Goal

DayFlow is engineered to be **usable for decades**. A user at age 25 should find DayFlow richer, wiser, and more personal at age 60. This mandates architectural choices favoring data longevity, format stability, and progressive enrichment over short-term feature velocity.

---

## Section 3 — Engineering Philosophy

### 3.1 — Architecture Before Features

No feature may be implemented before its architectural dependencies exist and are production-ready.

**Wrong:**
```
Build Memory Search → Later create Memory Repository
```

**Correct:**
```
Repository → Entity → Use Case → Events → API → UI → Tests → Production
```

### 3.2 — Domain First

Business rules belong **only** in the Application Layer. They never reside in:

- Controllers
- Repositories
- Database Models
- AI prompts
- UI components
- Infrastructure adapters

Business logic is sacred. It is isolated, tested in isolation, and never polluted by framework concerns.

### 3.3 — AI Is Not Business Logic

AI generates **suggestions**. AI **never** changes state directly.

Every mutation that an AI suggests must pass through deterministic validation:

```
AI says → "Create Task"
Application decides →
    Is user allowed?
    Is project active?
    Does task violate invariants?
→ Create event → Persist → Publish
```

AI output is treated as **untrusted input**. Always.

### 3.4 — Event First

Every significant state change becomes an event. Never mutate important state silently.

The system is fully replayable. Given the event log, the entire system state can be reconstructed.

### 3.5 — Replaceability

Every external dependency must be replaceable:

- LLM provider
- Embedding model
- Vector database
- Authentication provider
- Cloud provider
- Storage engine
- Notification service

All hidden behind interfaces. No external dependency may leak into domain or application logic.

### 3.6 — Local Before Remote

If a capability can safely execute locally, it runs locally. Cloud is used only when necessary.

**Execution priority:**
```
Device → Edge → Cloud
```

This guarantees privacy, latency, and offline operation as architectural properties, not features bolted on later.

### 3.7 — Small Vertical Slices

Never build fifty unfinished modules. Always finish one slice.

A slice is complete only when it is:

- Thought through → Structured → Stored → Searchable → Retrievable
- Exposed via UI → Covered by tests → Deployed to production

**Wrong:**
```
Task CRUD → Goal CRUD → Project CRUD → Habit CRUD → Reflection CRUD
(all half-built)
```

**Correct:**
```
Thought → Structure → Store → Search → Retrieve → UI → Tests → Production
(one complete flow)
```

### 3.8 — Boring Infrastructure, Exciting Intelligence

Infrastructure choices favor **boring, proven, well-understood technology**. PostgreSQL, Redis, standard HTTP. No novelty-seeking where reliability matters.

Intelligence choices favor **cutting-edge capability**. The latest LLMs, novel retrieval architectures, experimental reasoning.

The boring holds the exciting together. Never invert this.

### 3.9 — Privacy Is Architectural

Privacy is not a feature, a setting, or a compliance checkbox. It is a foundational architectural property:

- The user's mind data never leaves their device unless they explicitly choose cloud sync.
- All sensitive data is encrypted at rest and in transit.
- AI providers never receive data that identifies the user without explicit consent.
- The system is designed to function fully offline.

### 3.10 — Reversibility

Every decision that is hard to reverse (data formats, public APIs, event schemas) is treated with extreme care. Every decision that is easy to reverse (implementations, algorithms) is made quickly and improved iteratively.

---

## Section 4 — Architecture Principles

### 4.1 — Separation of Concerns

Each layer, module, and component has **one responsibility**. Responsibilities never overlap. When they appear to overlap, the boundaries are wrong.

### 4.2 — Dependency Inversion

High-level policy must not depend on low-level detail. Both depend on abstractions.

```
Presentation → Application → Domain
                              ↑
                    Infrastructure (implements interfaces defined by Application/Domain)
```

### 4.3 — Single Source of Truth

For every fact, there is exactly one authoritative source.

- **Schema** → defined once in contracts, generated to all languages.
- **Configuration** → defined once, layered (defaults → env → secrets).
- **Business rule** → defined once in the domain, never duplicated.
- **Event definition** → defined once in contracts, consumed by all.

### 4.4 — Fail Loud, Fail Early

The system never silently swallows errors. Errors are surfaced, categorized, logged, and (where appropriate) escalated. Silent failure is a defect.

### 4.5 — Idempotency

Every mutating operation is idempotent. Retrying the same operation produces the same result. This is mandatory for reliability, replay, and synchronization.

### 4.6 — Design for Observability

Every component is built to be observed. Logging, metrics, and tracing are not added later — they are designed in from the first line of code.

### 4.7 — Design for Testability

Every component is built to be tested. Dependencies are injectable. Side effects are isolated. Determinism is preferred over randomness (or randomness is injected and controllable).

### 4.8 — Progressive Enhancement

The system degrades gracefully. When the cloud is unavailable, local intelligence continues. When AI is unavailable, deterministic rules continue. When advanced features are off, core productivity continues.

---

## Section 5 — Domain-Driven Design

### 5.1 — Strategic Design

DayFlow is decomposed into **bounded contexts**, each with a single, well-defined responsibility:

| Bounded Context | Responsibility |
|----------------|---------------|
| **Identity** | Users, authentication, sessions |
| **Memory** | Thought capture, storage, retrieval |
| **Knowledge** | Concepts, relationships, the graph |
| **Productivity** | Tasks, goals, projects, habits, scheduling |
| **Reflection** | Reviews, insights, patterns |
| **Reasoning** | Planning, prediction, decision support |
| **Automation** | Rules, triggers, workflows |

### 5.2 — Ubiquitous Language

Within each bounded context, there is one ubiquitous language shared by code, docs, UI, and conversation. The term "Task" means exactly one thing in the Productivity context. The term "Memory" means exactly one thing in the Memory context. Ambiguity is a defect.

### 5.3 — Aggregates

Domain state is organized into **aggregates** — clusters of entities and value objects treated as a single consistency boundary.

Rules:
- Each aggregate has **one root entity** (the aggregate root).
- External references point **only** to the aggregate root, never to internals.
- Within an aggregate, invariants are enforced **immediately** (strong consistency).
- Across aggregates, invariants are enforced **eventually** (via events, eventual consistency).
- One transaction modifies **one aggregate**.

### 5.4 — Entities

Entities have **identity** that persists across state changes. Two entities with identical attributes but different IDs are different entities.

### 5.5 — Value Objects

Value objects have **no identity**. They are defined entirely by their attributes. Two value objects with identical attributes are interchangeable. Value objects are **immutable**.

Examples: `EmailAddress`, `TimeWindow`, `Priority`, `Streak`.

### 5.6 — Domain Events

A domain event represents **something meaningful that happened** in the domain. Events are:

- **Named in the past tense** (`TaskCompleted`, not `CompleteTask`).
- **Immutable** — once published, never changed.
- **Self-describing** — contain all data needed to understand what happened.
- **Published by aggregates** when their state changes.

### 5.7 — Repositories (Domain Contracts)

Each aggregate root has a repository contract defined in the application layer. The repository abstracts persistence. The domain never knows whether it is persisted to PostgreSQL, a file, or memory.

### 5.8 — Specifications

Complex query and validation logic is expressed as **specifications** — composable predicates that can be combined with AND, OR, NOT.

---

## Section 6 — Clean Architecture

### 6.1 — The Dependency Rule

Source code dependencies must point **only inward** toward the domain.

```
                    ┌─────────────────────────────┐
                    │       Presentation          │   (UI, API Controllers)
                    │  ┌───────────────────────┐  │
                    │  │     Application       │  │   (Use Cases, Ports)
                    │  │  ┌─────────────────┐  │  │
                    │  │  │     Domain      │  │  │   (Entities, Rules)
                    │  │  └─────────────────┘  │  │
                    │  └───────────────────────┘  │
                    │     Infrastructure         │   (DB, AI, Messaging)
                    └─────────────────────────────┘
```

The innermost circle (Domain) knows nothing about outer circles. The Application layer knows only about the Domain. Infrastructure knows about Application interfaces (which it implements) and Domain.

### 6.2 — Layer Purification

| Layer | Allowed | Forbidden |
|-------|---------|-----------|
| **Domain** | Pure logic, entities, value objects, events, invariants | Frameworks, databases, HTTP, AI, UI, logging implementations |
| **Application** | Use cases, orchestration, ports, transaction boundaries | Database details, HTTP details, UI details, AI provider details |
| **Infrastructure** | Adapters, repositories, providers, clients | Business rules, use case orchestration |
| **Presentation** | Controllers, views, serializers | Business logic, direct repository access |

### 6.3 — Ports and Adapters (Hexagonal)

The application defines **ports** (interfaces). Infrastructure provides **adapters** (implementations).

- **Driving ports** — how the application is invoked (use case interfaces).
- **Driven ports** — what the application needs (repository interfaces, service interfaces).

The application core is **isolated** from all external agencies by ports.

### 6.4 — The Application Core Is Pure

The combination of Domain + Application is called the **application core**. It contains zero external dependencies. It can be:
- Tested without a database.
- Tested without HTTP.
- Tested without AI providers.
- Run in any environment that provides adapters.

This is non-negotiable.

---

## Section 7 — Dependency Rules

### 7.1 — Permitted Dependencies

```
Presentation   → Application
Presentation   → Contracts (DTOs)
Application    → Domain
Application    → Contracts
Infrastructure → Domain
Infrastructure → Application (implements its ports)
Infrastructure → Contracts
```

### 7.2 — Forbidden Dependencies

| Forbidden | Reason |
|-----------|--------|
| Domain → Infrastructure | Domain must not know about persistence |
| Domain → Application | Domain is innermost; cannot know outer layers |
| Domain → Presentation | Domain must not know about UI/API |
| Application → Infrastructure | Application depends on abstractions (ports), not implementations |
| Application → Presentation | Application must not know how it is invoked |
| Infrastructure → Presentation | Infrastructure must not know about UI/API |
| UI → Repository | UI must not bypass application layer |
| AI → Database | AI must never mutate state directly |
| Controller → Repository | Controllers orchestrate use cases, not data access |

### 7.3 — Enforcement

Dependency rules are **enforced by automated tooling in CI**. The build fails if:
- Domain imports infrastructure.
- Controllers call repositories directly.
- Circular dependencies exist.
- Any forbidden dependency is detected.

Manual review is insufficient. Enforcement is automated and mandatory.

### 7.4 — No Circular Dependencies

No module, package, or layer may depend on itself transitively. The dependency graph is a **directed acyclic graph (DAG)**. Circular dependencies are defects.

### 7.5 — Contracts as the Dependency Hub

Contracts is the **shared dependency** that all layers may reference. It contains:
- DTOs (Data Transfer Objects)
- Event schemas
- Error contracts
- API request/response shapes

Contracts contains **no logic** — only definitions. It is the lingua franca between layers.

---

## Section 8 — Layer Responsibilities

### 8.1 — Domain Layer

**Responsibility:** Encode business rules and domain structure.

**Contains:**
- Entities and aggregate roots
- Value objects
- Domain events
- Enums
- Domain exceptions
- Invariants (enforced within aggregates)
- Specifications
- Domain services (cross-aggregate logic)

**Does not contain:**
- Persistence concerns
- HTTP concerns
- Serialization concerns
- AI concerns
- UI concerns
- Logging infrastructure (only logging interfaces, if any)

### 8.2 — Application Layer

**Responsibility:** Orchestrate use cases, enforce application-level policies, coordinate domain and infrastructure.

**Contains:**
- Use cases (commands and queries)
- Application services
- Ports (interfaces for repositories and external services)
- Transaction boundaries
- Authorization checks
- Application-level validation
- Command and query handlers
- Event dispatching (application layer decides what events to publish)

**Does not contain:**
- Business rules (those are in Domain)
- Database access (that is in Infrastructure)
- HTTP routing
- UI logic

### 8.3 — Infrastructure Layer

**Responsibility:** Implement the ports defined by Application. Provide concrete adapters for external systems.

**Contains:**
- Repository implementations (PostgreSQL, etc.)
- AI provider adapters (LLM, embedding)
- Messaging adapters (event bus, message queue)
- Cache adapters
- Storage adapters (blob, file)
- External API clients
- Email/notification senders

**Does not contain:**
- Business logic
- Use case orchestration
- Knowledge of other adapters

### 8.4 — Presentation Layer

**Responsibility:** Translate external requests into use case invocations and translate responses back.

**Contains:**
- API controllers
- UI components
- Request/response serializers
- Input sanitization
- View models

**Does not contain:**
- Business logic
- Direct repository access
- Use case orchestration

### 8.5 — Contracts

**Responsibility:** Define the shared language between all layers.

**Contains:**
- DTOs
- Event schemas
- Error definitions
- API contracts (OpenAPI)
- Shared enums (where they cross layer boundaries)

**Does not contain:**
- Any logic whatsoever
- Any implementation

---

## Section 9 — Contracts First

### 9.1 — Single Source of Truth

All cross-boundary types — DTOs, event schemas, error contracts, API shapes — are defined **once** in machine-readable contracts, then **generated** into all consuming languages (Python, TypeScript).

There is no manual duplication of types across languages. Ever.

### 9.2 — Contract Formats

| Contract Type | Format |
|--------------|--------|
| API definitions | OpenAPI 3.1 |
| Event schemas | JSON Schema (Avro-compatible) |
| Shared DTOs | JSON Schema → generated |
| Error contracts | JSON Schema |

### 9.3 — Generation Pipeline

```
contracts/ (source of truth)
    ↓ generate
packages/contracts-python/   (generated, read-only)
packages/contracts-ts/        (generated, read-only)
    ↓ consume
application, infrastructure, presentation
```

Generated code is **never edited by hand**. It is regenerated from contracts.

### 9.4 — Contract Versioning

Contracts are versioned. Breaking changes require a new version. Consumers may pin to a version. See §30 (Versioning).

### 9.5 — Contracts Before Implementation

No module may be implemented before its contracts are defined, reviewed, and frozen. The contract is the agreement. Implementation is the fulfillment.

---

## Section 10 — Configuration

### 10.1 — Hierarchical Configuration

Configuration is resolved through a strict hierarchy. Later layers override earlier ones:

```
1. Code Defaults       (lowest priority)
2. Environment Variables
3. Secret Store
4. Runtime Overrides   (highest priority)
```

### 10.2 — Configuration Is Immutable Per Request

Within the scope of a single request or operation, configuration is **immutable**. Once resolved, it does not change for the duration of that operation. This guarantees consistency and predictability.

### 10.3 — Configuration Categories

| Category | Examples |
|----------|---------|
| **Runtime** | Feature flags, thresholds, model selections |
| **Build** | Compiler flags, optimization levels |
| **Secrets** | API keys, database passwords, tokens |
| **Feature Flags** | Toggles, gradual rollouts, experiments |
| **AI Models** | Which LLM, which embedding model, parameters |
| **Environment** | dev, staging, production identifiers |

### 10.4 — Secrets Never in Code

Secrets are **never** committed to source control. They live exclusively in:
- A secret manager (production).
- `.env` files (local development, git-ignored).
- Environment variables (CI/CD).

### 10.5 — Validation at Startup

Configuration is validated at startup. The application refuses to boot if required configuration is missing or invalid. Fail loud, fail early (§4.4).

---

## Section 11 — Observability

### 11.1 — The Three Pillars

DayFlow observability rests on three pillars:

1. **Structured Logging** — discrete events with context.
2. **Metrics** — numeric measurements over time.
3. **Distributed Tracing** — request flow across boundaries.

### 11.2 — Structured Logging Standard

Every log entry contains:

| Field | Description |
|-------|------------|
| `timestamp` | ISO 8601, UTC |
| `correlation_id` | Links all logs in a request flow |
| `user_id` | Hashed, never raw |
| `request_id` | Unique per request |
| `module` | Emitting module name |
| `severity` | DEBUG, INFO, WARN, ERROR, FATAL |
| `message` | Human-readable description |
| `duration` | Operation duration (where applicable) |

Logs are **structured** (JSON). Plain-text logging is forbidden in production.

### 11.3 — Never Log Sensitive Data

The following are **never** logged, under any circumstances:

- Thought content
- Memory content
- API keys
- Tokens
- Secrets
- Passwords
- Personal information (PII)
- Encryption keys

This is enforced by both convention and automated scanning.

### 11.4 — Metrics

Every significant operation emits metrics:
- Counters (how many times)
- Histograms (how long)
- Gauges (current state)
- Rates (per-second)

Metrics are named with a consistent convention: `module.operation.metric_type`.

### 11.5 — Distributed Tracing

Every request that crosses a process or service boundary carries a trace context. Spans are recorded for significant operations. The trace is reconstructable end-to-end.

### 11.6 — Observability Is Designed In

Observability is **not** added after the fact. Every component is built with logging, metrics, and tracing from its first commit. A component without observability is incomplete.

---

## Section 12 — Error Handling

### 12.1 — Error Categories

Every error falls into exactly one category:

| Category | Description |
|----------|------------|
| **Validation** | Input failed validation |
| **Business** | A business rule was violated |
| **Infrastructure** | A system resource failed (DB down, disk full) |
| **External** | An external service failed (LLM timeout, payment declined) |
| **AI** | An AI operation failed or produced invalid output |
| **Security** | A security policy was violated |
| **Timeout** | An operation exceeded its time budget |
| **Cancellation** | An operation was cancelled |

### 12.2 — Error Structure

Every error carries:

| Field | Description |
|-------|------------|
| `code` | Stable machine-readable error code |
| `message` | Human-readable message (localized where applicable) |
| `category` | One of the categories above |
| `severity` | INFO, WARN, ERROR, FATAL |
| `retryable` | Boolean — can this be retried? |
| `correlation_id` | Links to the originating request |

### 12.3 — Result Types Over Exceptions for Business Flow

For **expected** business outcomes (validation failures, business rule violations), the system uses **Result types** rather than exceptions:

```
Result.success(value)
Result.failure(error)
```

This makes error handling explicit in the type system and forces callers to handle failure cases.

Exceptions are reserved for **unexpected** failures (infrastructure crashes, programmer errors).

### 12.4 — Never Swallow Errors

Errors are never silently ignored. Every caught error is either:
- Handled (with a meaningful action).
- Logged and re-raised.
- Translated into a Result failure.

Catching an error and doing nothing is a defect.

### 12.5 — Error Propagation Across Boundaries

When an error crosses a layer or service boundary, it is **translated** into the appropriate contract for that boundary. Internal error details do not leak to external consumers.

---

## Section 13 — Event-Driven Architecture

### 13.1 — Events Represent Facts

An event is an **immutable record of something that happened**. Once published, it is never modified or deleted. The event log is the system's memory of its own history.

### 13.2 — Event Sourcing for Critical State

For aggregates whose history matters (Memory, Knowledge, Productivity), the source of truth is the **event log**. Current state is a **projection** derived by replaying events.

This guarantees:
- Full auditability
- Replayability
- Time-travel debugging
- Rebuildability from scratch

### 13.3 — Event Naming Convention

Events are named `{Aggregate}.{PastTenseVerb}`:

- `Task.Completed`
- `Memory.Stored`
- `Goal.Archived`
- `Habit.StreakBroken`
- `Thought.Captured`

### 13.4 — Event Structure

Every event contains:

| Field | Description |
|-------|------------|
| `event_id` | Unique identifier (UUID) |
| `event_type` | The event name |
| `aggregate_id` | ID of the aggregate that emitted it |
| `aggregate_type` | Type of the aggregate |
| `timestamp` | When it occurred (UTC, ISO 8601) |
| `version` | Aggregate version after this event |
| `correlation_id` | Links to the originating command |
| `causation_id` | Links to the event that caused this one |
| `payload` | The event data (schema-defined) |
| `metadata` | Provenance, source, actor |

### 13.5 — At-Least-Once Delivery

Events are delivered **at least once**. Consumers must be **idempotent** (§4.5). Duplicate events must not cause duplicate side effects.

### 13.6 — Projections

Read models are built as **projections** — derived views of the event log. Projections can be:
- Rebuilt from scratch by replaying events.
- Multiple projections can exist for the same events (different read shapes).

### 13.7 — Dead Letter Queue

Events that cannot be processed after configured retries are moved to a **dead letter queue** for inspection and manual or automated resolution. They are never silently dropped.

---

## Section 14 — AI-First Principles

### 14.1 — AI Is a First-Class Citizen

AI is not a feature bolted onto DayFlow. It is woven into the architecture from the foundation. Every subsystem is designed with the assumption that intelligence augments it.

### 14.2 — AI Augments; Humans Decide

AI suggests, predicts, organizes, and explains. The human remains the decision-maker for all consequential actions. AI never takes autonomous action on the user's behalf without explicit configuration or consent.

### 14.3 — AI Output Is Untrusted

All AI output is treated as **untrusted input**. It is validated, sanitized, and confirmed by deterministic logic before any state change occurs. See §3.3.

### 14.4 — AI Is Replaceable

The LLM, embedding model, and vector store are all behind interfaces. They can be swapped without touching domain or application logic. See §3.5.

### 14.5 — AI Governance

AI usage is governed:
- Every AI call is logged (without content, per §11.3).
- Every AI call has a cost and latency budget.
- AI can be disabled (graceful degradation to deterministic rules).
- AI model selection is configuration-driven.
- AI prompts are versioned (see §14.6).

### 14.6 — Prompt Versioning

Prompts are **versioned artifacts**, not inline strings. Each prompt has:
- A unique identifier
- A version number
- Input/output schemas
- Test cases
- Evaluation criteria

Prompt changes are tracked and reviewable.

### 14.7 — Local AI Where Possible

When a task can be performed by a local model with acceptable quality, the local model is preferred. Cloud AI is used when the capability gap justifies the cost, latency, and privacy tradeoff. See §3.6.

---

## Section 15 — Replaceability and Provider Abstraction

### 15.1 — Everything External Is Behind an Interface

Every external dependency — database, LLM, vector store, cloud provider, auth provider, notification service — is hidden behind a port (interface).

### 15.2 — Swappability

Any provider can be replaced by:
1. Implementing the same interface.
2. Updating configuration.
3. No changes to domain or application code.

### 15.3 — No Vendor Lock-In

The system never depends on a vendor-specific feature in a way that cannot be abstracted. If a vendor offers a compelling proprietary feature, the interface is designed to capture the capability, not the vendor's API shape.

### 15.4 — Multi-Provider Support

For critical AI capabilities (LLM, embedding), the architecture supports **multiple simultaneous providers** with:
- Routing (which provider for which task)
- Fallback (if provider A fails, try provider B)
- Load balancing
- A/B testing

### 15.5 — Provider Isolation

A failure in one provider does not cascade to others. Each provider has its own circuit breaker, timeout, and retry policy.

---

## Section 16 — Local-First Architecture

### 16.1 — Device Is the Primary Home

The user's device is the **primary** home for their data and computation. The cloud is an optional extension.

### 16.2 — Offline-First

DayFlow functions **fully offline**. Core operations — capture thoughts, manage tasks, review habits — work without network connectivity. Sync happens when connectivity returns.

### 16.3 — Conflict-Free Replicated Data Types (CRDTs)

For data that synchronizes across devices, the system uses **CRDTs** or equivalent merge strategies that guarantee convergence without conflicts. The user never has to manually resolve sync conflicts for routine data.

### 16.4 — Local AI Models

The system supports running **local AI models** (small LLMs, local embedding models) for privacy-sensitive operations. The architecture does not assume a network connection for intelligence.

### 16.5 — Encrypted Local Storage

All local data is **encrypted at rest** with keys derived from the user's credentials. The device being lost or stolen does not expose the user's mind data.

### 16.6 — Sync Is Opt-In

Cloud synchronization is **opt-in**, not default. A user can use DayFlow for years entirely locally and never sync.

---

## Section 17 — Vertical Slices and Incremental Delivery

### 17.1 — One Complete Slice at a Time

DayFlow is built one complete vertical slice at a time. A slice spans all layers from UI to database and is independently valuable to the user.

### 17.2 — Slice Definition

A slice is complete when:
- The feature is usable end-to-end.
- It is covered by tests (unit, integration, contract).
- It is observable.
- It is documented.
- It meets its performance budget.
- It has passed the Definition of Done (§40).

### 17.3 — No Half-Built Modules

There are no half-built modules in the codebase. A module is either complete or it does not exist. Work-in-progress lives in branches, not in the main codebase.

### 17.4 — Each Slice Ships

Every slice is **deployable and shipped**. Code that is written but not shipped is incomplete. See §39 (Release Management).

---

## Section 18 — Repository Strategy

### 18.1 — Monorepo

DayFlow is a **monorepo**. All code — backend, frontend, infrastructure, docs, tests — lives in a single version-controlled repository.

### 18.2 — Why Monorepo

- **Atomic changes:** A change spanning backend, frontend, and contracts is one commit.
- **Shared tooling:** Linting, testing, CI are unified.
- **Code visibility:** All engineers see all code.
- **Dependency coherence:** Internal packages are always compatible.
- **Single source of truth:** One repository, one history.

### 18.3 — Organization by Capability

The repository is organized **by business capability**, not by framework or file type. A feature's domain, application, infrastructure, and presentation code are organized to reflect the feature, not the technical layer (except where layer separation is enforced by package structure).

### 18.4 — Workspace Management

The monorepo uses workspace management for both Python and TypeScript:
- **Python:** Workspace tooling (e.g., uv workspaces, pip editable installs).
- **TypeScript:** npm/pnpm/yarn workspaces.

Internal packages are referenced by path, not by published version, during development.

---

## Section 19 — Package Architecture

### 19.1 — Package Categories

| Package | Contains | Depends On |
|---------|---------|------------|
| **contracts** | DTOs, schemas, generated types | (nothing) |
| **domain** | Entities, value objects, events, rules | contracts |
| **application** | Use cases, ports, services | domain, contracts |
| **infrastructure** | Adapters, repositories, providers | application (ports), domain, contracts |
| **shared** | Cross-cutting utilities (clock, logger, IDs) | (nothing or contracts) |
| **sdk** | API clients for external consumers | contracts |

### 19.2 — Packages Never Depend on Applications

Applications (web, mobile, desktop, api) depend on packages. Packages never depend on applications. The dependency direction is strictly downward.

### 19.3 — Dependency Direction Recap

```
apps (web, api, mobile, desktop)
    ↓
application package
    ↓
domain package
    ↓
contracts / shared (foundation)
```

Infrastructure sits beside application, implementing its ports.

### 19.4 — Package Cohesion

Each package is **cohesive** — it contains everything related to its responsibility and nothing unrelated. A package that tries to do two things should be split.

### 19.5 — Package Interface Stability

A package's public interface is stable. Internal implementation may change freely. Breaking changes to a package's public interface require versioning and migration.

---

## Section 20 — Service Architecture

### 20.1 — Services Are Deployment Units

A service is a **deployment unit**, not a business module. Services group related capabilities that are deployed, scaled, and operated together.

### 20.2 — Service Catalog (Initial)

| Service | Contains |
|---------|---------|
| **Platform** | Auth, user, API, audit, settings, feature flags |
| **AI Brain** | Reasoning, memory, prediction, reflection |
| **Scheduler** | Daily jobs, timers, consolidation, maintenance |
| **Notifications** | Notification dispatch |
| **Sync** | Cross-device synchronization |
| **Gateway** | API gateway, routing, rate limiting |
| **Monitoring** | Metrics, tracing aggregation |

### 20.3 — Service Boundaries Are Hard

Services communicate **only** through defined contracts (APIs or events). They never share databases. They never share in-memory state. A service's internals are its own.

### 20.4 — AI Brain Does Not Know Authentication Exists

The AI Brain service operates on data and intelligence. It does not authenticate users, manage sessions, or know about identity infrastructure. Authentication is the Platform service's concern. The boundary is enforced by contract.

### 20.5 — Platform Does Not Know Reasoning Internals**

The Platform service manages identity, configuration, and access. It does not know how reasoning works, what prompts are used, or how memory is retrieved. The boundary is enforced by contract.

### 20.6 — Service Independence**

Each service can be:
- Deployed independently
- Scaled independently
- Tested independently
- Replaced independently (given contract conformance)

### 20.7 — Start Modular, Evolve to Services**

DayFlow begins as a **modular monolith** — one deployment unit with strict internal module boundaries. Services are extracted when and only when scale or operational concerns demand it. Premature service decomposition is forbidden.

---

## Section 21 — Security

### 21.1 — Security by Design

Security is designed in from the first line of code, not added later. Threat modeling, secure defaults, and least privilege are foundational.

### 21.2 — Least Privilege

Every component, service, and user has the **minimum privileges** required to perform its function. Nothing more.

### 21.3 — Defense in Depth

Security is layered:
- Input validation
- Authentication
- Authorization
- Encryption (at rest and in transit)
- Audit logging
- Rate limiting
- Output encoding

No single layer is relied upon alone.

### 21.4 — Never Trust Input

All input — from users, from APIs, from AI, from external services — is **untrusted** until validated. Validation happens at every trust boundary.

### 21.5 — Encryption Everywhere

- Data is encrypted **in transit** (TLS 1.2+).
- Data is encrypted **at rest** (database, blob, local device).
- Secrets are encrypted in the secret store.
- Encryption keys are rotated per policy.

### 21.6 — Authentication

Authentication is required for all non-public endpoints. Credentials are never stored in plaintext. Passwords are hashed with a modern, slow algorithm (Argon2id or equivalent).

### 21.7 — Authorization

Authorization is enforced at the **use case** level, not just at the API level. Every use case verifies that the caller is permitted to perform the action.

### 21.8 — Audit Logging

All security-relevant actions — logins, permission changes, data exports, configuration changes — are recorded in an **append-only audit log**. The audit log is tamper-evident.

### 21.9 — AI-Specific Security

- AI providers receive the **minimum data** necessary.
- Sensitive user data is **redacted or abstracted** before being sent to cloud AI.
- AI output is validated before use (§14.3).
- Prompt injection is defended against by treating AI output as untrusted input.

---

## Section 22 — Privacy

### 22.1 — Privacy as a Human Right

The user's personal data — their thoughts, memories, reflections — is **sacred**. DayFlow treats privacy as a fundamental human right, not a compliance obligation.

### 22.2 — Data Minimization

DayFlow collects and retains the **minimum data** necessary to provide its function. No data is collected "just in case."

### 22.3 — User Owns Their Data

The user owns their data. They can:
- Export all their data at any time, in a standard format.
- Delete any piece of their data.
- Delete their entire account and all associated data.
- Know exactly what data is stored and where.

### 22.4 — No Selling of Data**

DayFlow never sells user data. DayFlow never shares user data with third parties for advertising, training, or any purpose not explicitly consented to by the user.

### 22.5 — On-Device by Default**

Personal data lives **on the user's device** by default. Cloud storage is opt-in and encrypted.

### 22.6 — AI Privacy**

When cloud AI is used:
- The user is informed what data is sent.
- Sensitive content is redacted or abstracted where possible.
- The user can disable cloud AI entirely.
- Local AI alternatives exist for sensitive operations.

### 22.7 — Right to Be Forgotten**

Account deletion permanently and irrecoverably removes all user data, including from backups (within the backup retention window). This is verified by automated checks.

---

## Section 23 — Testing

### 23.1 — Testing Is Not Optional**

Every line of production code is accompanied by tests. Untested code is incomplete code. There are no exceptions.

### 23.2 — Test Pyramid**

```
        /\
       /  \      E2E (few, slow, expensive)
      /----\
     /      \    Integration (some, medium)
    /--------\
   /          \  Unit (many, fast, cheap)
  /____________\
```

The majority of tests are **unit tests**. They are fast, deterministic, and isolated. Integration tests verify component interaction. End-to-end tests verify user flows. The pyramid is broad at the base, narrow at the top.

### 23.3 — Unit Tests**

- Test one unit (function, class) in isolation.
- Dependencies are mocked or stubbed.
- Tests are **deterministic** — no flaky tests.
- Tests are **fast** — the full unit suite runs in seconds.
- Tests are **independent** — order does not matter.

### 23.4 — Integration Tests**

- Verify that components work together.
- Use real adapters where feasible (test database, mock external services).
- Cover the happy path and key failure paths.

### 23.5 — Contract Tests**

- Verify that a service conforms to its published contract.
- Consumers test against the contract, not the implementation.
- Contract tests prevent breaking changes from shipping.

### 23.6 — Property-Based Tests**

Where applicable, invariants are tested with property-based testing — generating many inputs to verify the invariant always holds.

### 23.7 — Performance Tests**

Critical paths have performance tests that enforce the performance budget (§26). A regression beyond budget fails the build.

### 23.8 — Coverage**

Coverage is measured but is a **proxy**, not a goal. High coverage with poor assertions is worthless. The goal is **meaningful coverage** of behavior, not line coverage.

Minimum thresholds (enforced in CI):
- Domain layer: ≥ 95%
- Application layer: ≥ 90%
- Infrastructure layer: ≥ 80%
- Presentation layer: ≥ 70%

### 23.9 — Tests Are First-Class Citizens**

Tests are not an afterthought. They are written alongside (or before) production code. They are reviewed with the same rigor. They are refactored and maintained.

---

## Section 24 — Performance

### 24.1 — Performance Budgets**

Every operation has a performance budget — a maximum acceptable latency and resource cost. Exceeding the budget is a defect.

### 24.2 — Measure, Don't Guess**

Performance decisions are based on **measurement**, not intuition. Every optimization is validated by benchmarks before and after.

### 24.3 — Latency Targets (Examples)**

| Operation | Budget |
|-----------|--------|
| API response (p99) | < 200ms |
| Memory search (p99) | < 500ms |
| Task creation | < 100ms |
| LLM call (cloud) | < 10s |
| LLM call (local) | < 3s |
| Local query | < 50ms |

These are illustrative; exact budgets are set per module in DIMP volumes.

### 24.4 — Resource Efficiency**

DayFlow runs on user devices — laptops, phones. It must be **resource-efficient**:
- Minimal memory footprint
- Minimal CPU usage when idle
- Minimal disk usage
- Minimal network usage

Bloat is a defect.

### 24.5 — Scalability of Intelligence, Not Just Load**

DayFlow must scale with the user's **history**. A user with 10 years of memories and 50,000 thoughts must experience the same responsiveness as a new user. Data growth does not degrade performance.

---

## Section 25 — Scalability

### 25.1 — Scale Axes**

DayFlow scales along multiple axes:
- **Users** (for the platform service, if multi-tenant)
- **Data per user** (memories, tasks, events)
- **Time** (history grows indefinitely)
- **Devices** (per user, sync)

### 25.2 — Partitioning**

Data is partitioned by **user** (tenant). A user's data is colocated. Cross-user queries are rare and explicit.

### 25.3 — Stateless Services**

Services are **stateless** where possible. State lives in databases and caches, not in service memory. This enables horizontal scaling.

### 25.4 — Caching Strategy**

Caching is applied strategically:
- Hot paths are cached.
- Cache invalidation is explicit and event-driven.
- Stale data is acceptable where eventual consistency is tolerable.
- Caching is never the primary correctness mechanism.

### 25.5 — Asynchronous Processing**

Long-running operations (AI calls, consolidation, indexing) are processed **asynchronously**. The user is not blocked. Results are delivered when ready.

---

## Section 26 — Reliability

### 26.1 — Availability Target**

DayFlow targets **high availability** for its services. Exact SLOs are defined per service in the DIMP. The local-first architecture guarantees that the user's core experience is available even when services are down.

### 26.2 — Graceful Degradation**

When a dependency fails, the system degrades **gracefully**:
- Cloud down → local operation continues.
- AI down → deterministic rules take over.
- Vector store down → keyword search fallback.
- Cache down → direct database access (slower, but functional).

### 26.3 — Retries with Backoff**

External calls use **retry with exponential backoff and jitter**. Retries are bounded. Retry policies are configurable per dependency.

### 26.4 — Circuit Breakers**

Unhealthy dependencies are protected by **circuit breakers**. When a dependency fails repeatedly, the circuit opens and calls fail fast, preventing cascading failures.

### 26.5 — Idempotency Guarantees Retries Are Safe**

Because all operations are idempotent (§4.5), retries are safe. The same operation applied twice has the same effect as once.

### 26.6 — Bulkheads**

Resources are partitioned so that a failure in one area does not exhaust resources needed by others. Each external dependency has its own connection pool and thread budget.

---

## Section 27 — Data Integrity

### 27.1 — Integrity Is Non-Negotiable**

User data must never be lost or corrupted. Data integrity is a higher priority than availability, performance, or feature velocity.

### 27.2 — Transactional Integrity**

Operations that must be atomic are wrapped in **transactions**. Within a transaction, either all changes succeed or none do.

### 27.3 — Eventual Consistency Where Appropriate**

Across aggregates and services, **eventual consistency** is acceptable and preferred over distributed transactions. The system converges to a consistent state given enough time and no new inputs.

### 27.4 — Validation at Boundaries**

Data is validated at every trust boundary — entry to the application layer, persistence, and event publication. Invalid data never propagates.

### 27.5 — Migration Safety**

Schema migrations are **non-destructive** by default:
- Additive changes (new columns, tables) are safe.
- Destructive changes (drops, renames) require a multi-step migration with backward compatibility windows.
- Migrations are tested on copies of production data.

### 27.6 — Backups**

Data is backed up regularly. Backups are:
- Encrypted.
- Tested for restorability (not just existence).
- Stored in geographically separate locations (for cloud deployments).
- Subject to a defined retention policy.

---

## Section 28 — Storage Strategy

### 28.1 — Polyglot Persistence**

DayFlow uses **different storage engines for different data shapes**:

| Data Type | Storage Engine |
|-----------|---------------|
| Relational data (users, tasks, goals) | PostgreSQL (document store capable) |
| Time-series events (event log) | Event store (PostgreSQL or dedicated) |
| Vector embeddings | Vector database (pgvector or dedicated) |
| Graph relationships | Graph store (or graph model in PostgreSQL) |
| Large binaries (files) | Blob storage |
| Hot cache | Redis (or in-memory) |
| Full-text search | Search index (PostgreSQL FTS or dedicated) |

### 28.2 — Repository Abstraction**

All storage access goes through **repository interfaces** defined in the application layer. The domain and application never know which engine stores their data.

### 28.3 — Replaceable Storage**

Each storage engine is replaceable:
- PostgreSQL can be swapped for another relational database.
- The vector store can be pgvector, Pinecone, Weaviate, or Qdrant.
- The event store can be PostgreSQL tables or a dedicated event store.

### 28.4 — Migrations Are Code**

Schema migrations are **versioned code**, reviewed and tested. They are reversible. They run automatically in CI/CD.

### 28.5 — Indexing Strategy**

Indexes are designed deliberately, based on query patterns, not added reactively. Every index has a documented reason and is reviewed for necessity.

### 28.6 — Data Lifecycle**

Data has a lifecycle:
- **Active** — frequently accessed.
- **Archive** — rarely accessed, kept for history.
- **Consolidate** — summarized into higher-level structures.
- **Expire** — removed per retention policy (with user consent).

The system manages this lifecycle automatically where appropriate.

---

## Section 29 — API Design

### 29.1 — API-First**

APIs are designed **before** implementation. The OpenAPI specification is the contract. Implementation fulfills the contract.

### 29.2 — RESTful Conventions**

Where REST is used:
- Resources are nouns.
- HTTP methods express intent (GET, POST, PUT, PATCH, DELETE).
- Status codes are used correctly and consistently.
- URLs are predictable and hierarchical.

### 29.3 — Consistent Error Contracts**

All errors follow the error contract (§12). The error response shape is identical across all endpoints.

### 29.4 — Pagination, Filtering, Sorting**

Collection endpoints support:
- **Pagination** (cursor-based preferred for large datasets).
- **Filtering** (consistent query parameter conventions).
- **Sorting** (consistent sort parameter conventions).

### 29.5 — Versioning**

APIs are versioned. Breaking changes require a new version. Old versions are supported for a defined deprecation window. See §30.

### 29.6 — Streaming**

For long-running operations (AI responses, large result sets), **streaming** is supported. The client receives progress and partial results incrementally.

### 29.7 — Idempotency Keys**

Mutating endpoints accept an **idempotency key**. The same key with the same request returns the same result, even if retried.

### 29.8 — Rate Limiting**

APIs are rate-limited to protect the system. Rate limits are communicated via headers. Clients back off when limited.

---

## Section 30 — Versioning

### 30.1 — What Is Versioned**

| Artifact | Versioning Strategy |
|----------|---------------------|
| **Constitution** | Semantic (v3.0). Frozen, amended rarely. |
| **DIMP Volumes** | Semantic per volume. |
| **APIs** | URL versioning (`/v1/`, `/v2/`). |
| **Contracts** | Semantic. Breaking changes bump major. |
| **Events** | Schema versioning within the event envelope. |
| **Packages** | Semantic Versioning (SemVer). |
| **Database schema** | Migration version numbers. |
| **Prompts** | Semantic. Evaluated before bump. |

### 30.2 — Semantic Versioning for Packages**

`MAJOR.MINOR.PATCH`
- **MAJOR** — breaking changes.
- **MINOR** — backward-compatible new features.
- **PATCH** — backward-compatible bug fixes.

### 30.3 — Backward Compatibility**

Breaking changes are minimized. When unavoidable:
- The old version is maintained for a deprecation window.
- Consumers are given a migration path.
- The change is announced well in advance.

### 30.4 — Event Schema Evolution**

Event schemas evolve **forward-compatibly** where possible:
- New optional fields are safe.
- Removed fields require a new schema version.
- Consumers ignore unknown fields.

### 30.5 — Database Migration Versioning**

Every schema change is a numbered migration. Migrations are applied in order. The database records its current migration version. Down migrations exist for rollback (where safe).

---

## Section 31 — Feature Flags

### 31.1 — Decouple Deploy from Release**

Feature flags allow code to be deployed **without** being activated. This decouples deployment from release, reducing risk.

### 31.2 — Flag Types**

| Type | Purpose | Lifetime |
|------|---------|----------|
| **Release** | Control feature rollout | Until fully released |
| **Experiment** | A/B testing | Duration of experiment |
| **Ops** | Kill switches, circuit breakers | Permanent |
| **Permission** | Entitlement-based access | Permanent |

### 31.3 — Graceful Handling**

Every feature flag has a **defined default** (on or off). Code handles both states correctly. A flag toggle does not require redeployment.

### 31.4 — Lifecycle Management**

Flags are tracked. Expired flags are removed. A flag that has been fully rolled out and is permanently on is **dead code** and should be removed.

### 31.5 — Evaluation Consistency**

Within a single request, a flag's value is **evaluated once** and cached for the request duration. This prevents inconsistent behavior within a request.

---

## Section 32 — Build Governance

### 32.1 — The Build Is the Gatekeeper**

The build pipeline is the **enforcer** of architecture. It does not merely compile and test — it validates that the code conforms to the Constitution.

### 32.2 — Build Pipeline Stages**

```
1. Lint
2. Type Check
3. Dependency Rule Check
4. Architecture Rule Check
5. Tests
6. Coverage Gate
7. Build
8. Package
9. Deploy
```

### 32.3 — Dependency Rule Check**

The build fails if:
- Domain imports infrastructure.
- Controllers call repositories directly.
- Any forbidden dependency (§7.2) is detected.
- Circular dependencies exist.

### 32.4 — Architecture Rule Check**

The build fails if:
- File size exceeds limits (§36.3).
- Function size exceeds limits (§36.4).
- Class has multiple responsibilities (heuristic-based).
- A module lacks a `module.yaml`.

### 32.5 — Quality Gates**

Each stage is a **gate**. A failure at any gate stops the pipeline. There is no "override and continue." Quality is not optional.

### 32.6 — Fast Feedback**

The build pipeline is **fast**. Lint and type-check run first and complete in seconds. Developers get feedback before the slow stages run.

### 32.7 — Reproducibility**

Builds are **reproducible**. The same code and configuration produce the same artifact. Builds are not dependent on developer machine state.

---

## Section 33 — Quality Gates

### 33.1 — Per-Module Gates**

Every module passes through quality gates before merge:

```
Architecture Review
    ↓
Static Analysis (lint, type-check)
    ↓
Dependency Rule Check
    ↓
Circular Dependency Detection
    ↓
Contract Validation
    ↓
Unit Tests
    ↓
Integration Tests
    ↓
Contract Tests
    ↓
Performance Budget
    ↓
Security Review
    ↓
Documentation Completeness
    ↓
No TODOs / Placeholders
    ↓
MERGE
```

### 33.2 — No Skip**

Gates cannot be skipped. A module that fails a gate does not merge. Period.

### 33.3 — Architecture Review**

Significant changes undergo **architecture review** by a qualified reviewer. The review checks:
- Adherence to the Constitution.
- Adherence to DIMP specifications.
- Appropriate use of patterns.
- Separation of concerns.
- Replaceability of external dependencies.

### 33.4 — Security Review**

Security-sensitive changes undergo **security review**, including threat modeling updates and attack surface analysis.

### 33.5 — Documentation Completeness**

Code is not complete until documentation is complete:
- Public APIs are documented.
- Module manifest (`module.yaml`) is updated.
- Relevant DIMP sections are updated.
- ADRs are written for significant decisions.

---

## Section 34 — CI/CD

### 34.1 — Continuous Integration**

Every change is integrated into the main branch **continuously**, behind feature flags where necessary. Long-lived branches are avoided.

### 34.2 — Continuous Delivery**

Every change to the main branch is **deployable**. The pipeline produces a deployable artifact automatically.

### 34.3 — Automated Deployment**

Deployment is **automated**. Manual deployment steps are minimized and documented. Production deployments are triggered by the pipeline, not by a human SSHing into a server.

### 34.4 — Environment Parity**

Environments (dev, staging, production) are as **similar** as possible. Differences are explicit and documented. "Works on my machine" is not acceptable.

### 34.5 — Rollback**

Every deployment is **reversible**. The rollback procedure is documented and tested. A failed deployment is rolled back automatically (where detected) or manually (with runbooks).

### 34.6 — Observability of the Pipeline**

The CI/CD pipeline is itself observable. Build times, failure rates, and deployment frequency are tracked.

---

## Section 35 — Documentation

### 35.1 — Documentation Is Code**

Documentation is treated with the same rigor as code:
- Versioned.
- Reviewed.
- Updated when the code changes.
- Tested (where applicable — e.g., examples run).

### 35.2 — Documentation Layers**

| Layer | Audience | Location |
|-------|---------|----------|
| **Constitution** | All engineers | `docs/constitution/` |
| **DIMP Volumes** | Engineers, architects | `docs/engineering/` |
| **ADRs** | Engineers, architects | `docs/adr/` |
| **API Reference** | API consumers | `docs/api/` (generated) |
| **Runbooks** | Operations, on-call | `docs/runbooks/` |
| **READMEs** | New engineers | per-package |
| **Inline comments** | Code readers | in code |

### 35.3 — ADRs Are Mandatory for Significant Decisions**

Any decision that is **hard to reverse** or affects multiple modules requires an **Architecture Decision Record**. The ADR captures context, decision, consequences, and status.

### 35.4 — Documentation Lives With Code**

Package-level documentation (READMEs, manifests) lives **in the package**, not in a separate wiki. Documentation and code evolve together.

### 35.5 — The DIMP Is the Authoritative Spec**

When code and DIMP disagree, the DIMP is authoritative until the DIMP is updated. Undocumented behavior is a defect.

---

## Section 36 — Coding Standards

### 36.1 — Naming Conventions**

| Element | Convention | Example |
|---------|-----------|---------|
| **Directories** | snake_case | `memory_engine/` |
| **Python files** | snake_case | `memory_repository.py` |
| **TypeScript files** | camelCase or kebab-case | `memoryRepository.ts` |
| **Classes** | PascalCase | `MemoryRepository` |
| **Functions** | snake_case (Python) / camelCase (TS) | `create_thought()` / `createThought()` |
| **Constants** | UPPER_CASE | `MAX_CONTEXT_SIZE` |
| **Interfaces** | PascalCase, often `I`-prefixed (Python: Protocol) | `MemoryRepository` (Python Protocol) |
| **Enums** | PascalCase | `TaskStatus` |
| **Tests** | `test_<unit>.py` / `<unit>.test.ts` | `test_memory_repository.py` |

### 36.2 — One Class, One Responsibility**

A class does **one thing**. If a class name contains "And" or "Manager" (without clear scope), it is likely doing too much.

Forbidden:
```
MemoryRepository + EmbeddingService + Search + Ranking  (inside one class)
```

### 36.3 — File Size Limits**

| Limit | Lines |
|-------|-------|
| **Target** | < 300 |
| **Maximum** | 500 |

If a file exceeds 500 lines, it must be split. Files approaching 300 lines should be examined for splitting opportunities.

### 36.4 — Function Size Limits**

| Limit | Lines |
|-------|-------|
| **Target** | 20–40 |
| **Hard maximum** | 80 |

Functions exceeding 80 lines must be refactored.

### 36.5 — No Magic**

Code avoids "magic":
- No implicit behavior.
- No global state (except where explicitly justified).
- No surprising side effects.
- Explicit is better than implicit.

### 36.6 — Comments Explain Why, Not What**

Code explains *what* it does (by being readable). Comments explain *why* — the reasoning, the constraints, the alternatives considered.

### 36.7 — Error Handling Is Explicit**

Errors are handled explicitly. Empty catch blocks are forbidden. Swallowed errors are defects. See §12.

### 36.8 — Consistency Over Preference**

When a pattern exists in the codebase, follow it. Consistency trumps individual preference. Introduce new patterns through ADRs, not unilateral decisions.

---

## Section 37 — Dependency Injection

### 37.1 — Everything Is Injected**

Every dependency — repositories, AI providers, storage, logger, clock, configuration, embedding provider, LLM provider — is **injected**. Nothing is constructed manually inside business logic.

### 37.2 — Why**

- **Testability** — dependencies can be mocked.
- **Replaceability** — implementations can be swapped.
- **Configuration** — wiring is centralized.
- **Clarity** — dependencies are explicit.

### 37.3 — Composition Root**

There is **one** place where dependencies are wired together: the **composition root**. This is where concrete implementations are selected and injected. The composition root knows about everything; everything else knows only about abstractions.

### 37.4 — No Service Locator**

The service locator (global registry) anti-pattern is forbidden. Dependencies are passed explicitly, not fetched from a global.

### 37.5 — Injection in Tests**

In tests, dependencies are replaced with **test doubles** (mocks, stubs, fakes). The same code under test runs with real or fake dependencies, depending on the test level.

### 37.6 — Lifetime Management**

Dependencies have defined lifetimes:
- **Singleton** — one instance for the application lifetime.
- **Scoped** — one instance per request/operation.
- **Transient** — a new instance every time.

Lifetimes are explicit and managed by the DI container.

---

## Section 38 — Hybrid Intelligence

### 38.1 — Human-AI Collaboration**

DayFlow is a partnership between human and AI. The human provides goals, values, and judgment. The AI provides memory, analysis, prediction, and suggestion.

### 38.2 — The Hybrid Decision Model**

```
Human Intent
    ↓
AI Suggests Options (with reasoning, confidence)
    ↓
Human Decides
    ↓
System Acts
    ↓
Outcome Observed
    ↓
AI Learns
```

The loop is continuous. Each iteration refines the AI's understanding of the human.

### 38.3 — Confidence and Uncertainty**

AI output includes **confidence** and acknowledges **uncertainty**. The system never presents AI output as certain when it is not. Low-confidence suggestions are marked as such.

### 38.4 — Explainability**

AI recommendations are **explainable**. The user can ask "why?" and receive a coherent explanation of the reasoning, the data considered, and the alternatives weighed.

### 38.5 — Personalization**

The AI personalizes to the user over time. It learns:
- The user's goals and values.
- The user's patterns and preferences.
- What suggestions the user accepts and rejects.
- The user's optimal times for focus, reflection, rest.

### 38.6 — Ethics and Boundaries**

The AI operates within ethical boundaries:
- It does not manipulate the user.
- It respects the user's autonomy.
- It does not pursue goals the user did not set.
- It is transparent about its capabilities and limitations.

See §14.2 and the Ethics subsection of DIMP Volume 13.

### 38.7 — The User Can Always Override**

The user always has the final word. AI suggestions can be accepted, modified, or rejected. The system learns from rejection as much as from acceptance.

---

## Section 39 — Release Management

### 39.1 — Releases Are Deliberate**

A release is a deliberate, planned event. It is not the accidental accumulation of merged changes.

### 39.2 — Release Readiness**

A release is ready when:
- All merged changes meet the Definition of Done (§40).
- The test suite is green.
- Performance budgets are met.
- Security review is complete.
- Documentation is updated.
- Rollback plan is verified.

### 39.3 — Deployment Strategies**

| Strategy | When Used |
|----------|----------|
| **Blue-Green** | Zero-downtime releases for services |
| **Canary** | Gradual rollout to detect issues early |
| **Rolling** | Standard for stateless services |
| **Feature Flags** | Decouple deploy from release |

### 39.4 — Versioning of Releases**

Releases are versioned (SemVer for packages, dated or numbered for deployments). Each release has a **changelog** documenting what changed.

### 39.5 — Rollback**

Every release has a tested **rollback path**. If a release introduces a problem, the previous release is restored quickly.

### 39.6 — Communication**

Releases are communicated:
- Internal: release notes to the team.
- External: changelog to users (for user-facing changes).

### 39.7 — No Big Bang Releases**

Large, risky releases are avoided. Changes are broken into smaller, safer increments. Feature flags and canary deployments manage risk.

---

## Section 40 — Definition of Done

### 40.1 — Definition of Done Is Universal**

The Definition of Done (DoD) applies to every unit of work — a task, a module, a slice, a release. A unit of work is complete **only** when every applicable criterion is met.

### 40.2 — Module-Level Definition of Done**

A module is complete only when:

1. **Architecture review** passed.
2. **Public interfaces** finalized and documented.
3. **Domain model** implemented (if applicable).
4. **Application services** implemented.
5. **Infrastructure adapters** completed.
6. **Events** published and consumed correctly.
7. **APIs** documented (OpenAPI).
8. **Unit tests** passing.
9. **Integration tests** passing.
10. **Contract tests** passing.
11. **Performance budget** met.
12. **Security review** completed.
13. **Observability** implemented (logging, metrics, tracing).
14. **Documentation** updated (DIMP, README, module.yaml).
15. **No TODOs** or placeholder implementations remain.
16. **Feature flag** (if applicable) configured.
17. **CI pipeline** green.
18. **Migration** (if applicable) written and tested.
19. **Rollback plan** defined.
20. **Constitution compliance** verified.

If **any** item is incomplete, the module is **not** done.

### 40.3 — Release-Level Definition of Done**

A release is complete only when:

1. All included modules meet their DoD.
2. End-to-end tests pass.
3. Performance validated in staging.
4. Security scan clean.
5. Documentation published.
6. Changelog written.
7. Rollback verified.
8. Communication sent.

### 40.4 — No "Done" Without Verification**

"Done" means **verified**, not "I think it works." Verification is through:
- Passing tests.
- Successful pipeline.
- Peer review.
- Demonstrated functionality.

### 40.5 — Done Means Shipped**

For user-facing work, "done" includes **shipped to production** (or ready to ship, behind a feature flag). Code that sits in a branch is not done.

### 40.6 — Constitutional Amendment Process**

This Constitution is amended only through:

1. A written **amendment proposal** (like an ADR).
2. **Impact analysis** across all affected DIMP volumes and code.
3. **Architecture Review Board** review and approval.
4. **Updated DIMP** cross-references.
5. **Version bump** (e.g., v3.0 → v3.1).

Until this process is followed, the Constitution is **immutable**.

---

## Appendix A — Constitution Quick Reference

### Core Principles (Section 3)
1. Architecture before features
2. Domain first
3. AI is not business logic
4. Event first
5. Replaceability
6. Local before remote
7. Small vertical slices
8. Boring infrastructure, exciting intelligence
9. Privacy is architectural
10. Reversibility

### Dependency Rules (Section 7)
- Dependencies point **inward** only.
- Domain depends on **nothing** external.
- Contracts are the shared hub.
- No circular dependencies.
- Enforcement is **automated**.

### Layer Purposes (Section 8)
- **Domain** — business rules (pure).
- **Application** — orchestration, use cases, ports.
- **Infrastructure** — adapters, implementations.
- **Presentation** — controllers, UI.
- **Contracts** — shared types, no logic.

### Definition of Done (Section 40)
Twenty criteria. All must be met. No exceptions. No partial credit.

---

## Appendix B — Glossary

| Term | Definition |
|------|-----------|
| **Aggregate** | A consistency boundary around a cluster of domain objects. |
| **Adapter** | An implementation of a port. |
| **ADR** | Architecture Decision Record. |
| **AI Core** | The combination of AI infrastructure and intelligence services. |
| **Application Core** | The combination of Domain and Application layers; pure, no external dependencies. |
| **Bounded Context** | A boundary within which a ubiquitous language applies. |
| **CQRS** | Command Query Responsibility Segregation. |
| **CRDT** | Conflict-free Replicated Data Type. |
| **DAG** | Directed Acyclic Graph (the shape of the dependency graph). |
| **DTO** | Data Transfer Object. |
| **Event Sourcing** | Persisting state as a log of events. |
| **Eventual Consistency** | A consistency model where the system converges over time. |
| **Hexagonal Architecture** | See Ports and Adapters. |
| **Idempotency** | An operation that produces the same result when repeated. |
| **Invariant** | A rule that must always hold true. |
| **Port** | An interface defining a contract between layers. |
| **Projection** | A read model derived from the event log. |
| **SLA** | Service Level Agreement. |
| **SLO** | Service Level Objective. |
| **Specification** | A composable predicate for querying and validation. |
| **Ubiquitous Language** | A shared vocabulary within a bounded context. |
| **Value Object** | An object defined by its attributes, with no identity. |

---

## Appendix C — Document Control

| Field | Value |
|-------|-------|
| **Document** | DayFlow Constitution |
| **Version** | 3.0 |
| **Status** | FROZEN — Immutable |
| **Date Frozen** | 2026-06-29 |
| **Supersedes** | Constitution v2.x, v1.x |
| **Sections** | 40 |
| **Authority** | Supreme architectural source of truth |
| **Citation Format** | `C{section}.{subsection}` |
| **Amendment Process** | See §40.6 |

---

*This Constitution is the law of DayFlow. Every line of code, every architectural decision, and every engineering choice answers to it. When in doubt, the Constitution decides.*

**— END OF CONSTITUTION v3.0 —**
