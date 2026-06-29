# M0 Baseline — Repository State Before Monorepo Realization

**Document Type:** Migration Evidence (permanent)
**Date:** 2026-06-29
**Phase:** M0 Phase 0 — Repository Compliance Baseline
**Governed By:** Volume 02 §23 (Acceptance Criteria), ADR-002 (Monorepo)

> This document is a frozen snapshot of the repository state *immediately before* M0
> realization. It exists so that any future regression can be traced back to a known
> starting point. It is never edited after creation.

---

## 1. Git State

| Field | Value |
|---|---|
| Was a git repo before M0? | **No** — initialized as Phase 0 step 1 |
| Initial branch | `master` → renamed to `main` (trunk-based, ADR-002) |
| Initial commit | Contains the pre-M0 state (Flask prototype + docs) |

---

## 2. File Inventory (Pre-M0, repository root)

```
DayFlow/
├── app.py                 (252 LOC — Flask application, single file)
├── dayflow.db             (24,576 bytes — SQLite database with seed data)
├── requirements.txt       (34 bytes — Flask==2.3.2, Flask-Cors==3.0.10)
├── docs/
│   ├── constitution/
│   │   └── constitution-v3.0.md
│   └── engineering/
│       ├── volume-00-architecture-lock.md
│       ├── volume-01-engineering-principles.md
│       └── volume-02-repository-foundation.md
├── templates/             (8 Jinja2 HTML pages)
│   ├── about.html
│   ├── dashboard.html
│   ├── goal-setup.html
│   ├── login.html
│   ├── signup.html
│   ├── timetable-choice.html
│   ├── timetable-generator.html
│   └── timetable-input.html
└── static/
    ├── script.js
    └── style.css
```

**Total files at root level (excl. docs/):** 4 files + 2 directories

---

## 3. Flask Prototype Status

**Classification:** Throwaway prototype (per ADR-001). Superseded by the polyglot
monorepo. Relocated to `legacy/flask-prototype/` in Phase 1 (history preserved via
`git mv`). Not deleted — retained as reference per user decision.

### 3.1 Dependencies (declared)

`requirements.txt`:
- `Flask==2.3.2`
- `Flask-Cors==3.0.10`

### 3.2 Dependencies (drift detected)

| Declared | Actually installed (system) |
|---|---|
| Flask==2.3.2 | Flask 3.1.1 |
| Flask-Cors==3.0.10 | (not checked — drift already established) |

**Note:** The prototype's `requirements.txt` is stale relative to the installed
runtime. This is a known issue with the throwaway prototype and is **not fixed** —
the prototype is reference-only after M0 and not run.

### 3.3 Database

`dayflow.db` — SQLite, 24,576 bytes. Contains seed data from prototype usage.
Tables (from earlier analysis): `users`, `goals`, `tasks`, `sqlite_sequence`.

### 3.4 Build/Test Status

- **Import check:** Flask imports successfully (`flask 3.1.1`).
- **Test suite:** None exists (no tests in the prototype).
- **Lint/typecheck:** None configured.

---

## 4. Documentation Inventory (Preserved — Not Migrated)

These frozen DIMP documents remain in `docs/` and govern all M0 work. They are
**not** relocated to `legacy/`:

| Document | Status | Role in M0 |
|---|---|---|
| `docs/constitution/constitution-v3.0.md` | Frozen | Governing law |
| `docs/engineering/volume-00-architecture-lock.md` | Frozen | 15 ADRs — tech stack authority |
| `docs/engineering/volume-01-engineering-principles.md` | Frozen | Engineering standards |
| `docs/engineering/volume-02-repository-foundation.md` | Frozen | Directory tree + tasks + acceptance criteria |

---

## 5. Tooling Availability (Environment Probe)

| Tool | Required By | Available? | Version |
|---|---|---|---|
| Python | ADR-001 (3.12+) | ✅ | 3.13.13 (satisfies "3.12+") |
| `uv` | ADR-002 (Python workspace) | ✅ | 0.11.16 |
| Node.js | ADR-001 (TS toolchain) | ✅ | v22.15.0 |
| `npm` | ADR-002 (fallback) | ✅ | 10.9.2 |
| `pnpm` | ADR-002 (TS workspace) | ❌ | **Missing — install via corepack** |
| Docker | ADR-008 (compose) | ✅ | 29.5.3 |
| Docker Compose | ADR-008 | ✅ | v5.1.4 |
| Git | ADR-002 | ✅ | 2.54.0 |

**Action:** `pnpm` is installed via `corepack enable` + `corepack prepare pnpm@latest --activate`
(Node 22 ships corepack). Required before Phase 4 (TypeScript workspace).

---

## 6. M0 Plan Reference

- **Source of tasks:** Volume 02 §24 (TASK-001 through TASK-018)
- **Source of acceptance:** Volume 02 §23 (16 criteria)
- **Source of build order:** Volume 02 §14
- **Source of directory tree:** Volume 02 §7.1
- **Architectural refinement:** `module.yaml` is the only *handwritten module manifest*;
  the Architecture Generator (`tools/architecture-generator/`) is a first-class platform
  compiler that derives import-linter, dependency-cruiser, diagrams, CODEOWNERS,
  capability matrix, compliance report, and drift detection from the Source Layer
  (module.yaml + ADRs + contracts).

---

## 7. Baseline Acceptance

This baseline is **accepted** as the starting state for M0. All subsequent phases
execute against Volume 02 with this document as the reference point.

---

**— END OF M0 BASELINE —**
