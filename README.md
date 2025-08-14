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

## Triage CLI (Phase 1)

Install (core only):
```
pip install -e .
```
Or with BigQuery real client:
```
pip install -e .[bigquery]
```

Run offline (stub client):
```
python -m core.cli triage --title "Login 500" --body "after reset" --severity P2 --out out/plan.md
```

Run live (BigQuery):
```
set BIGQUERY_REAL=1               # Windows PowerShell example
set PROJECT_ID=bq_project_northstar
set DATASET=demo_ai
set LOCATION=US
python -m core.cli triage --title "Image upload fails" --body "content-type mismatch" --out out/plan_live.md
```

PowerShell examples:
```
# Offline stub
python -m core.cli triage --title "Login 500" --body "after reset" --out out\smoke.md

# Live BigQuery
$env:BIGQUERY_REAL = "1"
$env:PROJECT_ID = "bq_project_northstar"
$env:DATASET = "demo_ai"
$env:LOCATION = "US"
python -m core.cli triage --title "Image upload fails" --body "content-type mismatch" --out out\smoke_live.md

# Phase-0 validation (requires bigquery extras)
python scripts\validate_phase0.py
```

### Create Remote Models (Embedding + Text)

You can create the two required remote Vertex models inside your dataset via BigQuery ML.

Bash:
```
export PROJECT_ID=bq_project_northstar
export DATASET=demo_ai
export LOCATION=US            # BigQuery dataset location
export VERTEX_REGION=us-central1
# optional overrides
# export EMBED_ENDPOINT=text-embedding-004
# export TEXT_ENDPOINT=gemini-1.5-pro
make create-remote-models
```

PowerShell:
```
$env:PROJECT_ID    = "bq_project_northstar"
$env:DATASET       = "demo_ai"
$env:LOCATION      = "US"            # BigQuery dataset location
$env:VERTEX_REGION = "us-central1"
$env:EMBED_ENDPOINT = "text-embedding-004"
$env:TEXT_ENDPOINT  = "gemini-1.5-pro"

bq query --location=$env:LOCATION --use_legacy_sql=false `
	--parameter=embed_model_fqid:STRING:"$($env:PROJECT_ID).$($env:DATASET).embed_model" `
	--parameter=embed_endpoint:STRING:"$env:EMBED_ENDPOINT" `
	--parameter=text_model_fqid:STRING:"$($env:PROJECT_ID).$($env:DATASET).text_model" `
	--parameter=text_endpoint:STRING:"$env:TEXT_ENDPOINT" `
	--parameter=region:STRING:"$env:VERTEX_REGION" `
	< sql\create_remote_models.sql
```

Idempotent: Re-running `make create-remote-models` will skip any model that
already exists and only create missing ones.

After creation set (FQIDs):
```
export BQ_EMBED_MODEL=${PROJECT_ID}.${DATASET}.embed_model
export BQ_GEN_MODEL=${PROJECT_ID}.${DATASET}.text_model
```
or in PowerShell:
```
$env:BQ_EMBED_MODEL = "$env:PROJECT_ID.$env:DATASET.embed_model"
$env:BQ_GEN_MODEL   = "$env:PROJECT_ID.$env:DATASET.text_model"
```

### Teardown Remote Models

When finished (to avoid lingering remote model objects) you can drop them. This is idempotent.

Bash:
```
export PROJECT_ID=bq_project_northstar
export DATASET=demo_ai
export LOCATION=US
make destroy-remote-models
```

PowerShell (Make target also works if make is installed, otherwise run manually):
```
$env:PROJECT_ID = "bq_project_northstar"
$env:DATASET    = "demo_ai"
$env:LOCATION   = "US"
powershell -NoProfile -Command "bq query --use_legacy_sql=false \"$([IO.File]::ReadAllText('sql/drop_remote_models.sql'))\""
```

Or manually specifying FQIDs (bash):
```
export BQ_EMBED_MODEL=${PROJECT_ID}.${DATASET}.embed_model
export BQ_GEN_MODEL=${PROJECT_ID}.${DATASET}.text_model
bq query --use_legacy_sql=false "$(cat sql/drop_remote_models.sql)"
```

### Preflight (models only)

Fast check that the two remote models exist (skips dataset / table checks):

Bash:
```
export PROJECT_ID=bq_project_northstar
export DATASET=demo_ai
export LOCATION=US
export BQ_EMBED_MODEL=${PROJECT_ID}.${DATASET}.embed_model
export BQ_GEN_MODEL=${PROJECT_ID}.${DATASET}.text_model
make preflight-models
```

PowerShell:
```
$env:PROJECT_ID = "bq_project_northstar"
$env:DATASET    = "demo_ai"
$env:LOCATION   = "US"
$env:BQ_EMBED_MODEL = "$env:PROJECT_ID.$env:DATASET.embed_model"
$env:BQ_GEN_MODEL   = "$env:PROJECT_ID.$env:DATASET.text_model"
python scripts\check_bq_resources.py --models-only
```

### Safe Teardown

Refuses to drop without an explicit FORCE=1 confirmation.

Bash:
```
FORCE=1 make destroy-remote-models
```

PowerShell:
```
$env:FORCE = "1"; make destroy-remote-models
```

## Next Steps
- Add project source code
- Configure tooling (linting, tests, CI)
- Document setup and usage

## Dashboard (read-only)

Lightweight analytics (Phase 5) built with Streamlit over BigQuery views.

Install (add streamlit):
```
pip install -e .[bigquery]
pip install streamlit -q
```

Extras examples:
```
# minimal dev
pip install -e .[dev]
# run dashboard
pip install -e .[dashboard]
# all-in
pip install -e .[bigquery,ingest,dashboard,dev]
```

Run (PowerShell example):
```
set BIGQUERY_REAL=1
set PROJECT_ID=bq_project_northstar
set DATASET=demo_ai
set LOCATION=US
make dashboard
```

Or offline stub (empty data but UI renders):
```
make dashboard
```

Views created (idempotent) inside your dataset:
- view_common_issues: naive fingerprint aggregation (first 8 normalized words)
- view_issues_by_severity: weekly counts by normalized severity (P0–P3, Unknown)
- view_duplicate_chunks: approximate duplicate clusters via ML.VECTOR_SEARCH

UI sections (row caps applied):
- Top common issues (snippet ≤200 chars, counts, last seen)
- Severity trends (weekly area chart)
- Potential duplicate clusters (expanders with sample members)

PII safety: snippets truncated to 200 chars + basic masking (emails, bearer tokens, AWS access keys). No writes or full meta exposure.

## Dev setup (format+lint hooks)
```
pip install -e .[dev]
make setup-dev

# run checks locally
make check
# or enforce pre-commit on all files
make pre-commit-all
```

## Create dashboard views (idempotent)
```
export PROJECT_ID=bq_project_northstar
export DATASET=demo_ai
export LOCATION=US
pip install -e .[bigquery]
make create-views

# Then run the dashboard:
pip install -e .[dashboard]
make dashboard
```


## Multimodal Ingest (Phase 3)

Install ingest extras (OCR + image support):
```
pip install -e .[ingest]
```
Or with BigQuery live features:
```
pip install -e .[bigquery,ingest]
```

Ingest sample folder (stub / offline):
```
python -m core.cli ingest --path samples --type auto --max-tokens 512 --refresh-loop
```

Make target wrapper:
```
make ingest-samples
```

Live BigQuery embedding refresh (example PowerShell):
```
$env:BIGQUERY_REAL = "1"
$env:PROJECT_ID = "bq_project_northstar"
$env:DATASET = "demo_ai"
$env:LOCATION = "US"
$env:BQ_EMBED_MODEL = "$env:PROJECT_ID.$env:DATASET.embed_model"
python -m core.cli ingest --path samples --type auto --max-tokens 512 --refresh-loop
```

Output prints counts: Docs, Chunks, NewEmbeddings (0 offline).

Token / batch controls:
- Chunk size: --max-tokens (capped internally at 4096)
- Embedding batch limit: EMBED_BATCH_LIMIT env (default 10000, <=50000)

Provenance formats rendered in References section:
```
log  -> bq.vector_search:log:{basename}:{line_no}
pdf  -> bq.vector_search:pdf:{basename}:p{page}
image_ocr -> bq.vector_search:image_ocr:{basename}:p{page}
image -> bq.vector_search:image:{basename}
```

### Severity Flag

You can annotate a ticket with an explicit severity (case-insensitive):

PowerShell:
```
python -m core.cli triage --title "Intermittent 500" --body "after reset" --severity p1 --out out\p1.md
```

Bash:
```
python -m core.cli triage --title "Intermittent 500" --body "after reset" --severity P1 --out out/p1.md
```

Accepted values: P0, P1, P2, P3, High, Medium, Low, Unknown.

### Multi-type Vector Filtering

`chunk_vector_search` automatically supports filtering by multiple types (e.g. logs + pdf). Pass a list of types in code, or ingest mixed sources: the SQL uses an array literal and filters server-side.

Example (Python):
```
from src.retrieval.hybrid import chunk_vector_search
rows = chunk_vector_search(client, query_text="login failure", types=["log","pdf"])
```

### Full Embedding Refresh (Looped Batching)

The refresh can now loop batches until no new rows are inserted.

One-off (PowerShell):
```
python -c "from bq.refresh import refresh_embeddings; from bq import make_client; print(refresh_embeddings(make_client(), loop=True))"
```

Or use the helper script / make target:
```
make refresh-all
```

Environment variable `EMBED_BATCH_LIMIT` controls per-batch size (default 10000, max 50000).

---
Generated initial commit scaffold.
