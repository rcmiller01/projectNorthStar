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
python -m core.cli triage --title "Login 500" --body "after reset" --out out/plan.md
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

## Next Steps
- Add project source code
- Configure tooling (linting, tests, CI)
- Document setup and usage

---
Generated initial commit scaffold.
