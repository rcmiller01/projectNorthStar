# Copilot Custom Instructions for projectNorthStar

These instructions are auto-loaded to guide AI assistance in this repository.
Update as the project evolves.

---
## 1. Project Snapshot
**Status:** Early initialization (scaffold only).  
**Primary Goal (placeholder):** Define and build the core system for Project North Star (specify domain: e.g. data platform, ML service, app backend, etc.).  
**Stack (planned):** (Add languages/frameworks here — e.g. Python 3.12 + FastAPI + PostgreSQL).  
**Open Questions:** Architecture, domain model, deployment target, CI requirements.

> ACTION: Replace placeholders once decisions are made.

---
## 2. Assistant Guidance Principles
1. Be explicit about assumptions; prefer 1–2 lightweight assumptions over blocking.  
2. Ask only when a decision materially affects architecture or irreversible work.  
3. Prefer incremental, testable changes.  
4. Surface edge cases early (performance, concurrency, failure modes, security).  
5. Favor clarity over cleverness; minimize hidden magic.

---
## 3. Code Style & Quality
| Area | Guidance (edit as needed) |
|------|---------------------------|
| Python Version | 3.12 (confirm) |
| Formatting | `ruff format` or `black` (choose one; default: ruff format) |
| Linting | `ruff` with default rules; enable complexity caps later |
| Types | Gradual typing with `mypy --strict` target (start permissive) |
| Tests | `pytest`, structure: `tests/` mirroring `src/` |
| Coverage Target | Start 60%, ratchet upward to 85%+ |
| Commits | Conventional Commits (e.g. `feat:`, `fix:`, `chore:`) |
| Imports | Standard lib → third-party → internal (grouped, separated) |

Add language/framework-specific sections once confirmed.

---
## 4. Branch & Workflow (Draft)
- `main` stays green; no direct force-push.  
- Feature branches: `feat/<short-scope>`, fixes: `fix/<issue|scope>`, hardening: `chore/`, experiments: `exp/`.  
- PR checklist: Lint clean, tests added/updated, docs touched if needed, no TODOs left un-ticketed.

---
## 5. Testing Strategy (Initial)
| Layer | Approach |
|-------|----------|
| Unit | Fast, isolated, no network/disk unless faked |
| Integration | Realistic module boundaries, ephemeral services via docker if needed |
| Property-based (optional) | For parsers / transformations using `hypothesis` |
| Performance (later) | Add lightweight benchmarks before optimizing |

---
## 6. Security & Reliability Notes
- Avoid storing secrets in repo; use environment variables + sample `.env.example`.  
- Add input validation at API boundaries.  
- Log structured JSON (no PII).  
- Fail fast on config errors; provide actionable error messages.  
- Plan for graceful degradation (timeouts, retries, circuit breakers) in service calls (future).

---
## 7. Documentation Expectations
- Keep `README.md` high-level (what/why/how to start).  
- Add `docs/` for deeper architecture once stabilized.  
- Each public module: top-of-file docstring + key function docstrings (summary, params, returns, error modes).  
- Provide ADRs (`docs/adr/`) for major architectural decisions.

---
## 8. AI Assistant Operational Rules
When responding:
- If the user asks for an implementation: produce full diff-ready code (no ellipses) unless they request a snippet.  
- If context is missing: state up to two assumptions and proceed.  
- If a feature spans multiple files: outline plan, then implement smallest vertical slice.  
- After code edits: suggest or add minimal tests.  
- Never introduce new dependencies without stating rationale + lighter alternatives.  
- Provide run / test commands (PowerShell syntax on Windows) in fenced blocks labeled `powershell`.

Example response skeleton for non-trivial change:
```
Summary
Plan
Changes Applied
Next Steps / Follow-ups
```

---
## 9. Performance & Observability (Future)
Planned additions:
- Metrics: latency, error rates per component.  
- Tracing: OpenTelemetry (if microservices emerge).  
- Structured logging fields: `timestamp, level, component, event, correlation_id`.

---
## 10. Roadmap Placeholder
| Phase | Goal | Notes |
|-------|------|-------|
| 0 | Foundational scaffold | Current step |
| 1 | Core domain model | Define entities & persistence |
| 2 | API layer / service integration | Framework TBD |
| 3 | Observability & hardening | Metrics, tracing, scaling |
| 4 | Optimization & polish | Performance passes |

---
## 11. Open Decision Log (fill in)
| Decision | Status | Owner | Date | Follow-up |
|----------|--------|-------|------|-----------|
| Python vs alt stack | Pending |  |  |  |
| Packaging tool | Pending |  |  |  |
| DB selection | Pending |  |  |  |

---
## 12. Quick Start (To Be Updated)
```powershell
# Create and activate virtual environment (adjust once stack chosen)
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e .
pytest -q
```

---
## 13. How to Update This File
- Keep sections short; archive obsolete decisions into `docs/adr/`.
- Update roadmap table as phases advance.
- Remove placeholders once values are real.

---
## 14. Assistant Self-Check Before Large Changes
Before proposing big refactors, confirm:
1. Problem statement restated.
2. Risk / rollback path noted.
3. Test impact identified.
4. Performance or security implications addressed.

---
## 15. Minimal Glossary (expand)
| Term | Meaning |
|------|---------|
| ADR | Architecture Decision Record |
| SLO | Service Level Objective |
| DRY | Don't Repeat Yourself |

---
*Last updated: initial version.*
