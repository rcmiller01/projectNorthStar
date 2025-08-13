# Product Requirements Document – BigQuery AI Hackathon

(Imported baseline PRD content; evolve as implementation progresses.)

## 1. Context & Goal
[Refer to initial PRD in conversation; maintain a single source here for edits.]

## 2. Scope & Constraints
- In scope: BigQuery AI embedding, retrieval, classification; multi-dataset integration; CLI + Notebook parity.
- Out of scope: non-essential modules.
- Constraints: Cost efficiency, Kaggle runtime limits, reproducibility.

## 3. Technical Approach (Snapshot)
- Architecture pillars: HRM (modular memory), GraphRAG (semantic + relational retrieval), MoE routing.
- Key components (planned):
  - `src/core/bq_client.py` – BigQuery + BigQuery AI helper
  - `src/pipeline/classifier.py` – ticket intent + category classification
  - `src/pipeline/retriever.py` – hybrid semantic + SQL retrieval
  - `src/pipeline/article_generator.py` – knowledge article synthesis
  - `src/eval/metrics.py` – local scorer aligning with Kaggle metric

## 4. Phases
- Phase 1: Baseline single-dataset pipeline & local metric
- Phase 2: Multi-dataset + GraphRAG context linking
- Phase 3: Optimization + submission packaging

## 5. Testing Strategy
| Level | Focus |
|-------|-------|
| Unit | BQ client wrappers, classification heuristics, SQL template rendering |
| Integration | End-to-end sample ticket → article pipeline |
| Performance | Query cost/time sampling (Phase 3) |
| Compliance | BigQuery AI usage verification script |

## 6. Deliverables
- Public notebook, README architecture, reproducible CLI, verification script.

## 7. Open Decisions
| Topic | Question | Status |
|-------|----------|--------|
| Embeddings | Use BQ AI embedding model vs external? | Pending |
| Graph layer | Native BQ graph pattern vs external pre-process? | Pending |
| Cost control | Sampling strategy & caching policy | Pending |

---
*(Update this file as decisions solidify.)*
