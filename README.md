# projectNorthStar

Initial scaffold.

## Overview

This repository has been initialized. Replace this placeholder with project details.

## Quickstart (Phase 0)
1) Set env (Kaggle or local):
```
PROJECT_ID=bq_project_northstar
DATASET=demo_ai
LOCATION=US
BQ_EMBED_MODEL=text-embedding-004
BQ_GEN_MODEL=gemini-1.5-pro  # optional
```
2) Create embeddings + search:
- Run the notebook: `notebooks/BigQueryAI_demo.ipynb`
- Or (coming Phase 1) CLI: `python -m src.cli demo`

3) Verify:
```
pytest -q
```

Phase 1 (next): Minimal triage loop (retrieve → plan → verify).

## Next Steps
- Add project source code
- Configure tooling (linting, tests, CI)
- Document setup and usage

---
Generated initial commit scaffold.
