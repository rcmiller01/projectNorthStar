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
