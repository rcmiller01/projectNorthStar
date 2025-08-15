# Project NorthStar v1.0.0 – Multimodal Triage + BigQuery AI + Dashboard

[![CI](https://github.com/rcmiller01/projectNorthStar/actions/workflows/ci.yml/badge.svg)](https://github.com/rcmiller01/projectNorthStar/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](../LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)

## Highlights

| Feature | Description |
|---------|-------------|
| **BigQuery AI** | Embeddings + vector search; idempotent remote model creation & checks |
| **Multimodal Ingest** | PDFs, images → OCR, logs → normalized chunks & embeddings refresh loop |
| **Triage** | Freeform or ticket-based with provenance & verifier gating |
| **Dashboard** | Common issues, severity trends, duplicate clusters (read‑only) |
| **Safety** | PII masking, 200‑char truncation, CI secret & public sweeps |

## Quickstart
```bash
export PROJECT_ID=bq_project_northstar
export DATASET=demo_ai
export LOCATION=US
export BIGQUERY_REAL=1
pip install -e .[bigquery,ingest,dashboard,dev]
make create-remote-models
make create-views
python -m core.cli ingest --path samples --type auto --max-tokens 512 --refresh-loop
python -m core.cli triage --title "500 after reset" --body "android camera" --severity P1 --out out/plan.md
```

Dashboard:
```bash
pip install -e .[dashboard]
make dashboard
```

Eval & Demo:
```bash
make demo
make eval
```

Screenshot:
![Dashboard Preview](dashboard.png)

Install directly from tag:
```bash
pip install "git+https://github.com/rcmiller01/projectNorthStar@v1.0.0"
```

## Assets
- `docs/dashboard.png` synthetic screenshot
- `samples_demo_bundle.zip` (synthetic PDF, PNG, logs)
- `notebooks/Submission_Demo.ipynb` walkthrough

## Safety & Limits
- Duplicate detection approximate (thresholded neighbor graph)
- OCR optional (pytesseract); degrades gracefully if missing
- BigQuery query cost depends on your project usage

## Security
- CI secret scanning + public artifact sweep
- Output truncation + basic PII pattern masking
- MIT License

---
Changelog entries aggregated in `CHANGELOG.md`.
