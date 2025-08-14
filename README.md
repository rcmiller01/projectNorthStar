# projectNorthStar

AI-assisted triage & knowledge retrieval over BigQuery (embeddings + vector search + playbook verification). Minimal, idempotent, reproducible.

## Quickstart (5 steps)
1) Set env (PROJECT_ID, DATASET, LOCATION; enable real BigQuery):
```bash
export PROJECT_ID=bq_project_northstar
export DATASET=demo_ai
export LOCATION=US
export BIGQUERY_REAL=1
```

2) Install (all extras for full experience):
```bash
pip install -e .[bigquery,ingest,dashboard,dev]
```

3) Create remote models (idempotent) and views:
```bash
make create-remote-models
make create-views
```

4) Ingest samples and embed:
```bash
python -m core.cli ingest --path samples --type auto --max-tokens 512 --refresh-loop
```

5) Triage (freeform or seeded ticket):
```bash
python -m core.cli triage --title "500 after reset" --body "android camera" --severity P1 --out out/quickstart_plan.md
# or a seeded ticket (demo script seeds DEMO-1)
python -m core.cli triage --ticket-id DEMO-1 --severity P1 --out out/quickstart_ticket.md
```

PowerShell: use `$env:VAR="..."` for envs.

## Quickstart (5 steps)
1. Set env (replace if desired):
	```bash
	export PROJECT_ID=bq_project_northstar
	export DATASET=demo_ai
	export LOCATION=US
	# (after remote model creation you will set)
	# export BQ_EMBED_MODEL=${PROJECT_ID}.${DATASET}.embed_model
	# export BQ_GEN_MODEL=${PROJECT_ID}.${DATASET}.text_model
	```
2. Install (choose extras):
	```bash
	pip install -e .[dev]                 # core + tests
	pip install -e .[bigquery]            # + BigQuery real client
	pip install -e .[bigquery,ingest]     # + OCR / PDF ingest
	```
3. Create remote models (one‑time, idempotent):
	```bash
	make create-remote-models
	export BQ_EMBED_MODEL=${PROJECT_ID}.${DATASET}.embed_model
	export BQ_GEN_MODEL=${PROJECT_ID}.${DATASET}.text_model
	```
4. Ingest sample data (multimodal) + embeddings refresh:
	```bash
	make ingest-samples   # or: python -m core.cli ingest --path samples --type auto --max-tokens 512 --refresh-loop
	```
5. Triage (freeform) OR full demo (also seeds a ticket):
	```bash
	python -m core.cli triage --title "Login 500" --body "after reset" --out out/plan.md
	BIGQUERY_REAL=1 make demo   # requires steps 1-4 & remote models
	```

Optional: run micro eval
```bash
make eval
cat metrics/eval_results.json | jq .aggregate
```

## Data & Safety
Sample files in `samples/` are synthetic / minimal. No PII shipped. Snippets surfaced are truncated (≤200 chars) and basic masking (emails, bearer tokens, AWS access keys) applies in dashboard & playbooks. Attach only non-sensitive data when experimenting.

## Overview

Core pieces:
- Ingest (logs / pdf / OCR image → chunks → embeddings refresh loop)
- Hybrid retrieval (vector + simple lexical) with multi-type filtering
- Triage orchestrator (retrieve → draft plan → verifier gating)
- Optional ticket schema (writebacks: evidence links + resolutions)
- Streamlit dashboard (common issues, severity trends, duplicates)
- Micro evaluation harness (hit rate / distance / verifier score deltas in CI)

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

Placeholder screenshot (replace `docs/dashboard.png` once captured):
```
![Dashboard Overview](docs/dashboard.png)
```

PII safety: snippets truncated to 200 chars + basic masking (emails, bearer tokens, AWS access keys). No writes or full meta exposure.

## Quick Demo (end-to-end)

Requires live BigQuery (BIGQUERY_REAL=1) and existing remote models.

```bash
export PROJECT_ID=bq_project_northstar
export DATASET=demo_ai
export LOCATION=US
export BIGQUERY_REAL=1
pip install -e .[bigquery,ingest,dashboard,dev]
make demo
```

Output artifacts:
- `out/demo_freeform.md` freeform triage playbook
- `out/demo_ticket.md` ticket triage playbook (DEMO-1)

Summary line example:
```
[demo-summary] ticket_links=5 resolutions=1 k=5
```

Flags: `--no-refresh-loop`, `--max-comments N`, `--k K` (pass via `python scripts/demo_end_to_end.py ...`).

## Micro Eval

Generates a deterministic synthetic eval set (20 items) and runs retrieval + optional verifier scoring.

Stub (offline) or real depending on BIGQUERY_REAL (force stub with `--use-stub`).

```bash
make eval
cat metrics/eval_results.json | jq .aggregate
```

Files produced:
- `metrics/eval_set.jsonl` (input set)
- `metrics/eval_results.json` (per-item + aggregate metrics)

Metrics:
- `hit_rate`: fraction of queries with at least one relevant chunk (substring match)
- `mean_min_distance`: average minimum vector distance across queries
- `mean_verifier_score`: average playbook verification success (may be null if skipped)

## Submission Notebook

Notebook: `notebooks/Submission_Demo.ipynb`

Run cells top-to-bottom after setting env vars. Safe to re-run; creates views, ingests samples, performs freeform & (optional) ticket triage and displays outputs. For dashboards, run `make dashboard` locally outside hosted notebook environments.

Kaggle note: if editable installs are restricted, replace `pip install -e .[extras]` with `pip install .[extras]`.

## Tickets (optional, generic schema)

### What this adds

Triage by `--ticket-id` using BigQuery tables (`tickets`, `ticket_events`,
`ticket_attachments`) plus retrieval to produce a verified playbook. Evidence
links are written to `ticket_chunk_links`; the generated plan snapshot goes to
`resolutions`. Multimodal attachments (pdf/image/log) flow through Phase-3
ingest and become searchable chunks.

### Install
```bash
pip install -e .[bigquery]            # core
# or, if you plan to ingest attachments locally:
pip install -e .[bigquery,ingest]
```
Create the schema (idempotent):
```bash
python -c "from bq.tickets import TicketsRepo; from bq.bigquery_client import RealClient; TicketsRepo(RealClient()).ensure_schema()"
```
Seed a demo ticket (optional): `make demo` seeds `DEMO-1` or see
`scripts/demo_end_to_end.py` for inline MERGE example.

### Triage a ticket
```bash
# Writebacks enabled (default)
python -m core.cli triage --ticket-id DEMO-1 --severity P1 --out out/DEMO-1.md

# Read-only (no writebacks)
python -m core.cli triage --ticket-id DEMO-1 --no-write --severity P1 --out out/DEMO-1.md

# Control comments considered from ticket history (default: 5)
python -m core.cli triage --ticket-id DEMO-1 --max-comments 3 --out out/DEMO-1.md
```

### What gets written

`ticket_chunk_links`: rows `{ticket_id, chunk_id, relation="evidence", score≈(1-distance)}`

`resolutions`: `{ticket_id, resolved_at, resolution_text, playbook_md}`

### Dashboard integration

As you ingest / triage, related chunks impact:
- Common issues (fingerprint frequency)
- Severity trends (weekly buckets)
- Duplicate clusters (approx neighbor groups)

Provenance in playbooks & dashboard renders as `(log:file:line)` or
`(pdf:name:p#)`.

### Safety & PII

Surfaced text is truncated (≤200 chars) and emails / bearer tokens / AKIA keys
masked in UI. Keep attachments non-PII in demos; prefer synthetic samples. Use
`--no-write` when exploring.

## CI Eval Metrics

CI archives eval metrics and shows trend deltas on each PR. Threshold env vars:
`MIN_HIT_RATE`, `MAX_MIN_DIST`, `MIN_VERIFIER` guard regressions. See
`scripts/metrics_trend.py` and the `eval-ci` Make target.

## License

Project is released under the MIT License. See `LICENSE`.

## Public Datasets

Sample paths and BigQuery public data used for demonstration (e.g., cloud-samples-data and BigQuery Public Datasets) are for evaluation only. Remove or replace with your own data in production.

## License

Released under the MIT License (see `LICENSE`). Sample data is synthetic. If you add third-party datasets or models, ensure their licenses are compatible and document them here.

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

## Release Process

Automated helper scripts + Make targets streamline versioned releases (SemVer).

Dry run (compute next version only):
```
make release-dry-run part=patch
```

Full release (updates version, changelog, commit + tag):
```
make release part=minor
```

Workflow:
1. Clean working tree enforced
2. Determine new version from `part=` (major|minor|patch)
3. Generate grouped changelog from commits since last tag
4. Update `pyproject.toml` + prepend `CHANGELOG.md`
5. Commit `chore(release): vX.Y.Z` and create git tag `vX.Y.Z`

Push after review:
```
git push origin main --tags
```

## Secret & Public Sweeps

Secret scan (regex + entropy) locally:
```
make sweep-secrets
```
Strict mode:
```
make sweep-secrets-strict
```
Allowlist file: `secrets_allowlist.txt` (exact matches only).

Public artifact sweep (large files, notebook outputs, internal URLs, cred file patterns):
```
make public-sweep
```

Both run in CI (see `secret_scan.yml` + `public_sweep` job in `ci.yml`). Findings summarized in PR checks.

Pre-commit hooks: `secret-sweep` (medium threshold) and `nbstripout` (removes notebook outputs on commit).

## Maintenance Checklist (Before Release)
1. `make check` passes
2. `make sweep-secrets` clean (or intentional allowlist rationale documented)
3. `make public-sweep` clean
4. CI eval metrics within thresholds
5. Docs updated for new flags/models
6. `make release-dry-run part=patch` sanity check
7. `make release part=patch` then push tag
