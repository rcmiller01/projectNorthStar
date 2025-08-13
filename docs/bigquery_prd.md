# BigQuery AI Contest – Product Requirements Document

(Authoritative copy mirrored from `docs/PRD.md` – keep them in sync or deprecate one.)

## 1. Context & Goal
See baseline PRD: unified triage + knowledge generation leveraging BigQuery AI (embeddings, vector search) with public-safe artifacts (SQL + notebook + verifier) for contest submission.

## 2. Scope & Constraints
- In scope: Embedding generation, vector search, lightweight classification, retrieval assembly, verification of required BigQuery AI usage.
- Out of scope: Proprietary HRM internals (keep stubs sanitized), heavy fine-tuning, non-essential cloud infra.
- Constraints: Kaggle / contest runtime, deterministic reproducibility, cost mindfulness (favor dry-run & sample limits early).

## 3. Technical Approach (Snapshot)
- Hybrid retrieval: lexical (SQL) + semantic (VECTOR_SEARCH) + simple graph-style joins (phase 2).
- Modular design: explicit SQL templates in `sql/` surfaced in README & notebook.
- Verification script ensures presence & execution footprint of BigQuery AI functions.

## 4. Phases
1. Baseline: single dataset, embedding + simple vector search, rule classifier.
2. Enrichment: multi-dataset linking (graph edges or relational join heuristics).
3. Optimization: caching, cost sampling, packaging & polish.

## 5. Testing Strategy
| Level | Focus |
|-------|-------|
| Unit | Client wrapper, SQL template rendering, classifier rules |
| Integration | Retrieval pipeline assembling context chunks |
| Compliance | Verifier detects required BigQuery AI constructs |

## 6. Deliverables
- Public notebook (`notebooks/BigQueryAI_demo.ipynb`).
- SQL templates (`sql/*.sql`).
- CLI (`src/cli.py`).
- Verifier (`src/verifier.py`).
- Minimal tests (in `tests/`).

## 7. Open Decisions
| Topic | Question | Status |
|-------|----------|--------|
| Embeddings model | Which BigQuery AI embedding model variant? | Pending |
| Graph linking | Use intermediate table vs CTE with UNION edges? | Pending |
| Cost control | Sampling & caching approach | Pending |

---
(Iterate as design evolves.)

---
## Development Phases (Build Prompt)

This section mirrors the structured build prompt used at the start of each phase. Follow `copilot-instructions.md` and PR templates.

### Phase 0 — "Hello BigQuery AI" (Compliance Scaffold)
Goal: Minimal public-safe demo of embeddings + vector search (+ optional text generation) via notebook & SQL.
Artifacts: `sql/embeddings.sql`, `sql/create_vector_index.sql`, `sql/vector_search.sql`, notebook, thin client.
Done: Notebook executes end-to-end showing BigQuery AI usage; tests dry-run and structural checks pass.

### Phase 1 — Minimal Triage Loop
Loop: ingest (normalize) → retrieve (VECTOR_SEARCH k≤8) → plan (clarifiers) → verify.
Artifacts (new dirs): `ingest/`, `src/retrieval/hybrid.py`, `experts/`, `verify/`, `core/orchestrator.py`.

### Phase 2 — Knowledge Drafts
Produce structured agent playbook (Summary, Hypothesis, Diagnostics, Decision Table, Remediation, Rollback, Owners, References) with citations & verifier enforcement.

### Phase 3 — Multimodal Ingest
OCR & log parsing integrated; embeddings updated; retrieval cites attachment provenance.

### Phase 4 — Verification Hardening
SQL shape checks, safety constraints, repair loop.

### Phase 5 — Ticketing Dashboard
Aggregated BigQuery views + lightweight dashboard (Streamlit/FastAPI).

### Phase X — Optional Typed Extraction in SQL
Use `ML.GENERATE_TEXT` to produce structured JSON classification per ticket.

---
Hygiene: Small PRs, post-code reflection, README/PRD sync.
