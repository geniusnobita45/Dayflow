# Volume 02 — Repository Foundation

**Document Type:** Monorepo Architecture & Workspace Specification
**DIMP Volume:** 02
**Status:** FROZEN — Governs all repository structure
**Date:** 2026-06-29
**Governed By:** Constitution v3.0 (§18, §19, §20)
**Builds On:** Volume 00 (ADR-002, ADR-009), Volume 01 (Engineering Principles)

---

## 01. Executive Summary

This volume specifies the **exact monorepo layout**, the **dual workspace configuration** (Python + TypeScript), the **tooling baseline**, and the **root-level governance files** that make DayFlow a coherent, buildable, governable codebase. It is the physical realization of ADR-002 (monorepo) and ADR-009 (tooling). Every developer and AI coding agent works within this structure; every CI job runs against it.

The layout is organized **by architectural layer** at the top level and **by bounded context** within each package, so that the dependency direction (C7) is visible from the folder tree alone.

---

## 02. Objectives

1. Define the **complete, authoritative directory tree** for the DayFlow monorepo.
2. Specify **dual workspace configuration** (Python `uv` workspaces + TypeScript `pnpm` workspaces).
3. Specify the **root governance files** (`.gitignore`, `.editorconfig`, `Makefile`, root configs).
4. Specify **tooling baseline** (ruff, mypy, eslint, prettier, import-linter, dependency-cruiser).
5. Establish the **package naming scheme** and inter-package reference mechanism.
6. Define the **governance hooks** (pre-commit, CI path filters) that keep the monorepo healthy at scale.

---

## 03. Scope

**In scope:**
- Repository top-level structure and every subdirectory's purpose.
- Python workspace (`pyproject.toml` hierarchy, `uv` workspace config).
- TypeScript workspace (`package.json` hierarchy, `pnpm-workspace.yaml`).
- Root-level files: `.gitignore`, `.editorconfig`, `Makefile`, `docker-compose.yml`.
- Per-language tooling configs (ruff, mypy, eslint, prettier).
- Dependency-rule enforcement configs (import-linter, dependency-cruiser).
- The `docs/` sub-structure.
- The `module.yaml` manifest convention (structure; content per-module in Volumes 04–16).

**Out of scope:**
- Developer commands, CLI, scaffolding, dev containers → Volume 03.
- Contract format and generation pipeline → Volume 05.
- Module-internal design → Volumes 04–16.
- CI pipeline stages and deployment → Volume 18.

---

## 04. Out of Scope

See Section 03. This volume defines **where things live and how the repo is wired**; it does not define **what developers type** (Volume 03) or **what modules contain** (Volumes 04–16).

---

## 05. Constitution Mapping

| Topic | Constitution Clause |
|-------|--------------------|
| Monorepo | C18.1, C18.2 |
| Organization by capability | C18.3 |
| Workspace management | C18.4 |
| Package categories & deps | C19.1, C19.2, C19.3 |
| Dependency direction | C7, C19.3 |
| Services as deployment units | C20.1, C20.2 |
| Modular monolith start | C20.7 |
| Contracts as dependency hub | C7.5, C9 |
| Configuration hierarchy | C10 |
| Coding standards tooling | C36, ADR-009 |
| Build governance | C32 |
| Documentation layers | C35.2 |

---

## 06. Architecture

### 6.1 — Top-Level Organization Principle

```
dayflow/
├── docs/              ← Knowledge (Constitution, DIMP, ADRs, runbooks)
├── packages/          ← Reusable libraries (domain, application, infra, contracts, shared)
├── apps/              ← Deployable applications (web, api, mobile, desktop)
├── services/          ← Deployment-unit services (modular monolith modules initially)
├── deployments/       ← Infrastructure-as-code & deploy manifests
├── tools/             ← Build/codegen/governance tooling
├── scripts/           ← Operational & dev scripts
├── tests/             ← Cross-cutting test suites (E2E, integration harness)
└── root config files
```

**Principle:** The top level reflects **architectural layer**, not file type. A reader sees `packages/domain/` and immediately knows this is innermost, depended-upon, pure.

### 6.2 — The Dependency Direction, Made Visible

The folder structure physically enforces the mental model:

```
apps/            → depend on packages/
services/        → depend on packages/
packages/        → depend on each other inward (infra → app → domain → contracts/shared)
                   NEVER outward
```

A Python `import-linter` contract and a TypeScript `dependency-cruiser` rule encode this so CI fails on violation (C7.3).

---

## 07. Components

### 7.1 — Complete Repository Tree

```
dayflow/
│
├── docs/
│   ├── constitution/
│   │   └── constitution-v3.0.md
│   ├── engineering/
│   │   ├── MASTER_INDEX.md
│   │   ├── volume-00-architecture-lock.md
│   │   ├── volume-01-engineering-principles.md
│   │   ├── volume-02-repository-foundation.md
│   │   ├── ... (volumes 03–20)
│   ├── adr/
│   │   ├── README.md
│   │   └── adr-NNN-*.md
│   ├── api/                  ← generated OpenAPI reference (read-only)
│   ├── architecture/         ← diagrams, decision context
│   ├── runbooks/             ← operational runbooks (Volume 17)
│   ├── testing/              ← test strategy docs (Volume 19)
│   ├── security/             ← threat models, policies (Volume 09)
│   └── decisions/            ← non-ADR engineering decisions log
│
├── packages/
│   ├── contracts/            ← SOURCE OF TRUTH: OpenAPI + JSON Schema (hand-authored)
│   │   ├── openapi/
│   │   ├── schemas/
│   │   ├── events/
│   │   └── package.yaml
│   ├── contracts-py/         ← GENERATED Python models (read-only)
│   │   ├── src/contracts_py/
│   │   ├── tests/
│   │   └── pyproject.toml
│   ├── contracts-ts/         ← GENERATED TypeScript types + Zod (read-only)
│   │   ├── src/
│   │   ├── tests/
│   │   └── package.json
│   ├── domain/               ← Pure business model (entities, VOs, events, rules)
│   │   ├── src/dayflow_domain/
│   │   │   ├── shared/         (Entity, ValueObject, AggregateRoot bases)
│   │   │   ├── identity/
│   │   │   ├── memory/
│   │   │   ├── knowledge/
│   │   │   ├── productivity/
│   │   │   ├── reflection/
│   │   │   └── reasoning/
│   │   ├── tests/
│   │   ├── pyproject.toml
│   │   └── module.yaml
│   ├── application/          ← Use cases, ports, services
│   │   ├── src/dayflow_application/
│   │   │   ├── shared/        (UseCase base, Result, UnitOfWork)
│   │   │   ├── ports/         (repository & service interfaces)
│   │   │   ├── identity/
│   │   │   ├── memory/
│   │   │   ├── knowledge/
│   │   │   ├── productivity/
│   │   │   ├── reflection/
│   │   │   └── reasoning/
│  /domain/...
│   │   ├── tests/
│   │   ├── pyproject.toml
│   │   └── module.yaml
│   ├── infrastructure/       ← Adapters: persistence, AI providers, messaging, cache
│   │   ├── src/dayflow_infrastructure/
│   │   │   ├── persistence/   (SQLAlchemy repositories, migrations)
│   │   │   ├── ai/            (LLM, embedding, vector store adapters)
│   │   │   ├── messaging/     (event bus, DLQ)
│   │   │   ├── cache/         (Redis adapter)
│   │   │   ├── storage/       (blob adapter)
│   │   │   └── search/        (FTS adapter)
│   │   ├── tests/
│   │   ├── pyproject.toml
│   │   └── module.yaml
│   ├── shared/               ← Cross-cutting utilities (clock, ids, logger, errors, config)
│   │   ├── src/dayflow_shared/
│   │   │   ├── clock/
│   │   │   ├── ids/
│   │   │   ├── logging/
│   │   │   ├── errors/
│   │   │   ├── config/
│   │   │   ├── result/
│   │   │   └── tracing/
│   │   ├── tests/
│   │   ├── pyproject.toml
│   │   └── module.yaml
│   └── sdk/                  ← Typed API client for external consumers
│       ├── src/
│       ├── tests/
│       └── package.json
│
├── apps/
│   ├── api/                  ← FastAPI application (composition root)
│   │   ├── src/dayflow_api/
│   │   │   ├── main.py        (startup, shutdown, wiring)
│   │   │   ├── routes/
│   │   │   ├── middleware/
│   │   │   ├── dependencies/  (FastAPI dependency providers)
│   │   │   └── container.py   (DI composition root)
│   │   ├── tests/
│   │   ├── Dockerfile
│   │   └── pyproject.toml
│   ├── web/                  ← Next.js application
│   │   ├── src/
│   │   ├── public/
│   │   ├── Dockerfile
│   │   ├── next.config.js
│   │   └── package.json
│   ├── mobile/               ← React Native (future)
│   └── desktop/              ← Tauri (future)
│
├── services/                 ← Deployment units (modular monolith modules initially)
│   ├── platform/             ← Auth, user, settings, feature flags
│   ├── ai-brain/             ← Reasoning, memory ops, prediction
│   ├── scheduler/            ← Daily jobs, consolidation
│   ├── notifications/
│   ├── sync/
│   ├── gateway/
│   └── monitoring/
│   (Each service has a README, module.yaml, and (later) its own Dockerfile.
│    In Phase 1 (ADR-015), these are modules within apps/api, not separate processes.)
│
├── deployments/
│   ├── docker/
│   │   └── docker-compose.yml   (local dev: postgres, redis)
│   ├── kubernetes/              (production manifests, deferred per ADR-008)
│   ├── terraform/               (cloud IaC, deferred)
│   └── ci/                      (GitHub Actions workflow definitions)
│
├── tools/
│   ├── contract-generator/      (generates contracts-py & contracts-ts)
│   ├── dependency-checker/      (wraps import-linter / dependency-cruiser)
│   ├── size-guard/              (file/function size enforcement)
│   └── module-linter/           (validates module.yaml presence & schema)
│
├── scripts/
│   ├── setup.sh / setup.ps1     (bootstrap dev environment)
│   ├── seed.py                  (seed data for local dev)
│   └── check_compliance.py      (pre-commit compliance gate)
│
├── tests/
│   ├── e2e/                     (Playwright E2E)
│   ├── integration/             (cross-package integration harness)
│   └── contract/                (consumer-driven contract tests)
│
├── .github/
│   └── workflows/
│       ├── ci.yml               (lint → typecheck → dep-check → test → build)
│       └── docs.yml             (regenerate docs / doc validation)
│
├── .editorconfig
├── .gitignore
├── .gitattributes
├── Makefile                     (unified commands: lint, test, typecheck, format, check)
├── pyproject.toml               (Python workspace root)
├── uv.lock                      (Python lockfile)
├── package.json                 (TS workspace root)
├── pnpm-workspace.yaml
├── pnpm-lock.yaml
├── docker-compose.yml           (top-level dev services)
├── README.md
└── CHANGELOG.md
```

### 7.2 — Package Dependency Graph (Physical)

```
                    apps/api  apps/web
                        │        │
              ┌─────────┴────────┴─────────┐
              ▼                            ▼
        application                  infrastructure
              │                            │
              ▼                            ▼
            domain  ◄────────────────  domain
              │                            │
              └──────────┬─────────────────┘
                         ▼
              contracts-py / contracts-ts  (generated)
                         ▲
                         │
                    contracts/ (source)

          shared  (standalone; used by all Python packages)
```

Key edges (enforced):
- `apps → application, infrastructure, contracts, shared`
- `application → domain, contracts, shared`
- `infrastructure → domain, contracts, shared` (implements application ports)
- `domain → contracts, shared` (domain MAY depend on contracts for shared enums, and on shared for base classes — see C19.1 footnote)
- `contracts → (nothing)`
- `shared → (nothing)`

Forbidden edges (CI fails): any arrow pointing outward (e.g., `domain → infrastructure`).

---

## 08. Interfaces

### 8.1 — Package Public Interface Convention

Each package exposes a **single public entry point** (its `__init__.py` or `src/index.ts`), which re-exports only the intended public API. Internal modules are accessible but not "supported." Reviewers enforce that consumers import only from the package root.

### 8.2 — module.yaml Manifest

Every module (bounded context within a package, or a service) contains a `module.yaml` declaring its identity and contracts. Schema (Volume 02 specifies structure; content is filled per module in Volumes 04–16):

```yaml
# module.yaml — DayFlow module manifest (schema v1)
name: memory                  # unique module name
layer: domain | application | infrastructure | presentation | service
owner: memory-team
version: 1.0.0
constitution_references: [C13, C28, C5.3]
dimp_volume: V11

dependencies:                 # other DayFlow modules this depends on
  - domain.shared
  - contracts.events.memory

public_api:                   # what this module exports to consumers
  - MemoryRepository (port)
  - MemoryEntry (entity)
  - events: [Memory.Stored, Memory.Retrieved, Memory.Consolidated]

events_published:
  - Memory.Stored
  - Memory.Consolidated
events_consumed:
  - Thought.Captured
  - Embedding.Created

metrics:
  - memory.store.duration
  - memory.search.latency
  - memory.retrieval.hit_rate

feature_flags:
  - memory.vector_search.enabled
  - memory.consolidation.enabled

degradation:                  # C4.8 — behavior when deps fail
  on_vector_store_down: fall_back_to_fts
  on_embedding_provider_down: reject_new_stores_queue_retry

performance_budget:
  store_p99_ms: 150
  search_p99_ms: 500

status: active                # active | deprecated | experimental
```

The `module-linter` tool (in `tools/`) validates every `module.yaml` against this schema and fails CI if a module lacks one (C32.4).

---

## 09. Data Contracts

No contracts are authored in this volume. The **contracts directory** (`packages/contracts/`) is created as an empty, structured home; its content is specified in Volume 05. The generation pipeline (ADR-013) is wired here (tool location) but specified in Volume 05.

---

## 10. Events

No events are authored here. Event schemas live in `packages/contracts/events/` and are specified in Volume 08.

---

## 11. State Machines

Not applicable at the repository level.

---

## 12. Algorithms

Not applicable.

---

## 13. Folder Structure

This volume **is** the folder structure specification (Section 07.1). It is authoritative. The `tools/module-linter` and CI path conventions enforce it.

---

## 14. Build Order

The repository is bootstrapped in this order (executed by Volume 20 tasks):

1. Root files: `.gitignore`, `.editorconfig`, `Makefile`, root `pyproject.toml`, root `package.json`, `docker-compose.yml`.
2. Workspace wiring: `uv` workspace members, `pnpm-workspace.yaml`.
3. `packages/contracts/` skeleton (empty dirs + schema).
4. `packages/shared/` (clock, ids, logging, errors, config, result, tracing).
5. `packages/domain/` skeleton (base classes + bounded-context dirs).
6. `packages/application/` skeleton (ports + use-case base).
7. `packages/infrastructure/` skeleton (adapter dirs).
8. `packages/contracts-py/` and `packages/contracts-ts/` generation wiring.
9. `apps/api/` (FastAPI composition root skeleton).
10. `apps/web/` (Next.js skeleton).
11. `tools/` (contract-generator, dependency-checker, size-guard, module-linter).
12. `deployments/docker/docker-compose.yml` (postgres, redis).
13. `scripts/setup.*` and `scripts/seed.py`.
14. `.github/workflows/ci.yml`.
15. `docs/` sub-structure.
16. `module.yaml` in every package/service.

No package is considered "started" until its skeleton + `module.yaml` exist; no package is "done" until it meets Volume 01 §23 and Constitution C40.2.

---

## 15. Public APIs

The repository exposes no external public API at this level. `apps/api` exposes the REST API (Volume 08). `packages/sdk` exposes the typed client (Volume 05).

---

## 16. Internal APIs

### 16.1 — Workspace Resolution

- **Python:** internal packages referenced by **path** via `uv` workspace (editable installs). Example: `dayflow-domain` is a workspace member; `dayflow-application`'s `pyproject.toml` lists `dayflow-domain` as a path dependency.
- **TypeScript:** internal packages referenced by **path** via `pnpm` workspace. Example: `@dayflow/contracts-ts` is resolved from `packages/contracts-ts/`.

### 16.2 — Inter-Package Reference Convention

| Consumer | References |
|----------|-----------|
| `apps/api` | `dayflow-application`, `dayflow-infrastructure`, `dayflow-contracts-py`, `dayflow-shared` |
| `application` | `dayflow-domain`, `dayflow-contracts-py`, `dayflow-shared` |
| `infrastructure` | `dayflow-domain`, `dayflow-contracts-py`, `dayflow-shared` (implements `application` ports) |
| `domain` | `dayflow-contracts-py` (shared enums only), `dayflow-shared` (base classes) |
| `contracts-py` | (nothing internal; generated) |
| `shared` | (nothing internal) |

---

## 17. Dependency Rules

This volume codifies C7 in repository terms:

| Rule | Enforcement |
|------|------------|
| Dependencies point inward only | `import-linter` contracts + `dependency-cruiser` rules in CI |
| No `domain → infrastructure` | import-linter forbidden edge |
| No `controller → repository` (bypassing application) | import-linter + code review |
| No circular dependencies | import-linter + dependency-cruiser DAG check |
| Contracts is the shared hub | all packages may depend on contracts; contracts depends on nothing internal |
| Apps cannot be depended upon | no internal package lists an app as a dependency |

Example `import-linter` contract (Python, conceptual):

```
[importlinter]
root_package = dayflow

[importlinter:contract:layers]
name = DayFlow layer dependency rules
type = layers
layers =
    dayflow_api
    dayflow_application
    dayflow_infrastructure
    dayflow_domain
    dayflow_contracts_py
    dayflow_shared
```

Example `dependency-cruiser` rule (TypeScript, conceptual):

```json
{
  "forbidden": [
    { "name": "no-domain-to-infra", "from": { "path": "packages/domain" }, "to": { "path": "packages/infrastructure" } },
    { "name": "no-circular", "from": {}, "to": { "circular": true } }
  ]
}
```

---

## 18. Performance Budget

No operation-level budgets here. Repository-level performance concern: **CI speed**. Targets (C32.6):
- Lint + typecheck: < 60s.
- Unit tests: < 120s.
- Full pipeline (incl. integration): < 10 min.

CI uses **path filtering** (only run affected package jobs) to keep feedback fast as the monorepo grows.

---

## 19. Security

Repository-level security:
- `.gitignore` excludes secrets, `.env*`, keys, build artifacts, local DBs, node_modules, virtualenvs.
- **Pre-commit secret scanner** (e.g., `detect-secrets` / `gitleaks`) blocks accidental secret commits (C10.4).
- `README.md` documents the "never commit secrets" rule.
- Generated packages (`contracts-py`, `contracts-ts`) are marked read-only; a CI check verifies no manual edits (ADR-013).

---

## 20. Failure Handling

- **Broken main:** CI gates prevent broken code reaching `main`. If `main` breaks, the priority-1 incident is reverting (C34.5) and fixing forward.
- **Dependency resolution failure:** `uv.lock` / `pnpm-lock.yaml` are committed; reproducible installs (C32.7). A drift between lockfile and manifests fails CI.
- **Generation failure:** If contract generation fails, downstream packages are not built; the pipeline halts with a clear error.

---

## 21. Observability

The repository includes observability **scaffolding** (the `shared/logging`, `shared/tracing`, `shared/config` modules), but their content is specified in Volumes 04 and 17. At the repo level, we ensure:
- Every package has a `module.yaml` with a `metrics:` list (possibly empty until that module adds metrics).
- The `apps/api` composition root wires logging/tracing/metrics providers (Volume 04).

---

## 22. Testing

Repository-level testing conventions:
- Every package has a `tests/` directory.
- Tests follow naming: `test_<unit>.py` (Python), `<unit>.test.ts` (TypeScript) (C36.1).
- Cross-package integration tests live in `tests/integration/`.
- E2E tests live in `tests/e2e/` (Playwright).
- Contract tests live in `tests/contract/`.
- Detailed strategy and coverage gates in Volume 19 (ADR-010).

---

## 23. Acceptance Criteria

The repository foundation is **done** when:

1. The complete directory tree (Section 07.1) exists.
2. Root governance files exist and are correct: `.gitignore`, `.editorconfig`, `Makefile`, `pyproject.toml`, `package.json`, `pnpm-workspace.yaml`, `docker-compose.yml`, `README.md`, `CHANGELOG.md`.
3. Python workspace resolves: `uv sync` succeeds; all internal packages are editable-installed.
4. TypeScript workspace resolves: `pnpm install` succeeds; all internal packages resolve by path.
5. Tooling is configured and runnable: `ruff`, `mypy`, `eslint`, `prettier`, `import-linter`, `dependency-cruiser` all run from root.
6. `make lint`, `make typecheck`, `make test`, `make format`, `make check` all exist and execute (even if suites are initially near-empty).
7. Dependency-rule enforcement is active: `import-linter` and `dependency-cruiser` contracts are defined and run in CI.
8. Size guards are active: CI fails on files > 500 lines or functions > 80 lines (C36.3–4).
9. Every package and service has a `module.yaml`; `module-linter` validates them.
10. Contract generation tooling is wired (even if contracts are minimal initially).
11. `docker-compose up` brings up PostgreSQL + Redis for local dev.
12. `.github/workflows/ci.yml` runs the full build governance pipeline (C32).
13. Secret scanning pre-commit hook is active.
14. `docs/` sub-structure exists; Constitution + DIMP volumes are in place.
15. No TODOs or placeholders remain (C40.2.15).
16. `README.md` documents setup, commands, and structure.

---

## 24. AI Coding Tasks

Representative tasks (full enumeration in Volume 20):

- **TASK-001** — Bootstrap root files (`.gitignore`, `.editorconfig`, `Makefile`).
- **TASK-002** — Configure Python `uv` workspace + root `pyproject.toml`.
- **TASK-003** — Configure TypeScript `pnpm` workspace + `pnpm-workspace.yaml`.
- **TASK-004** — Create `packages/contracts/` skeleton.
- **TASK-005** — Create `packages/shared/` skeleton + base utilities (clock, ids).
- **TASK-006** — Create `packages/domain/`, `application/`, `infrastructure/` skeletons.
- **TASK-007** — Wire `apps/api/` FastAPI composition root skeleton.
- **TASK-008** — Wire `apps/web/` Next.js skeleton.
- **TASK-009** — Configure ruff + mypy (Python).
- **TASK-010** — Configure eslint + prettier + tsc (TypeScript).
- **TASK-011** — Configure import-linter + dependency-cruiser contracts.
- **TASK-012** — Implement `size-guard` tool.
- **TASK-013** — Implement `module-linter` tool + `module.yaml` schema.
- **TASK-014** — Write `docker-compose.yml` (postgres + redis).
- **TASK-015** — Write `.github/workflows/ci.yml`.
- **TASK-016** — Write `scripts/setup.*` and `scripts/seed.py`.
- **TASK-017** — Add `module.yaml` to every package/service.
- **TASK-018** — Write root `README.md` documenting structure & commands.

---

## 25. Done Definition

This volume's DoD is its **Acceptance Criteria** (Section 23), plus the global DoD (Constitution §40.2). Specifically, the repository foundation is complete only when a fresh `git clone` followed by the documented setup commands yields a fully working, lint-clean, type-clean, test-green, governable monorepo.

A half-wired repository (e.g., Python workspace works but TS doesn't; or import-linter is configured but not in CI) is **not done**.

---

## Appendix A — Root File Responsibilities

| File | Responsibility |
|------|---------------|
| `.gitignore` | Exclude secrets, env, build artifacts, venvs, node_modules, local DBs |
| `.editorconfig` | Consistent indentation, line endings, final newline across editors |
| `.gitattributes` | Line-ending normalization, linguist overrides |
| `Makefile` | Unified commands: `lint`, `typecheck`, `test`, `format`, `check`, `docs` |
| `pyproject.toml` | Python workspace root: tool config (ruff, mypy), workspace members |
| `uv.lock` | Python dependency lockfile (committed) |
| `package.json` | TS workspace root: scripts, dev deps, workspace config |
| `pnpm-workspace.yaml` | TS workspace member globs |
| `pnpm-lock.yaml` | TS dependency lockfile (committed) |
| `docker-compose.yml` | Local dev services: PostgreSQL (with pgvector), Redis |
| `README.md` | Project overview, setup, commands, structure |
| `CHANGELOG.md` | Release history (per C39.4) |

---

## Appendix B — The Makefile Command Surface

```
make install      # install all deps (uv sync + pnpm install)
make lint         # ruff + eslint
make format       # ruff format + prettier --write
make typecheck    # mypy + tsc
make dep-check    # import-linter + dependency-cruiser
make test         # pytest + vitest (unit)
make test-int     # integration suite
make test-e2e     # Playwright E2E
make contracts    # regenerate contracts-py & contracts-ts
make check        # full pre-merge gate: lint+typecheck+dep-check+test+size-guard+module-lint
make docs         # build/validate docs
make compose-up   # docker-compose up -d (postgres, redis)
make compose-down # docker-compose down
make seed         # load seed data
```

`make check` is the single command that mirrors the CI quality gate (C32.2, C33.1). Developers run it before every PR.

---

## Appendix C — Why uv and pnpm

- **uv (Python):** Fast (Rust-based) resolver/installer; native workspace support; single lockfile (`uv.lock`); replaces pip+pip-tools+venv boilerplate. Aligns with C3.8 (boring, proven, fast).
- **pnpm (TypeScript):** Strict node_modules (prevents phantom dependencies — supports C7 enforcement), fast, disk-efficient, workspace-native.
- Both produce **committed lockfiles** (C32.7, reproducibility).

---

## Document Control

| Field | Value |
|-------|-------|
| **Document** | DIMP Volume 02 — Repository Foundation |
| **Version** | 1.0 |
| **Status** | FROZEN |
| **Date** | 2026-06-29 |
| **Governed By** | Constitution v3.0 (§7, §18, §19, §20) |
| **Builds On** | Volume 00 (ADR-002, ADR-009), Volume 01 |
| **Prerequisite For** | All implementation volumes (03–20) |

---

**— END OF VOLUME 02 —**
