# projectNorthStar

[![CI](https://github.com/rcmiller01/projectNorthStar/actions/workflows/ci.yml/badge.svg)](https://github.com/rcmiller01/projectNorthStar/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)

AI-assisted triage & knowledge retrieval over BigQuery (embeddings + vector search + playbook verification). Minimal, idempotent, reproducible.

## 🚀 Quick Start

### Option 1: Mock Mode (Instant Setup)
Perfect for testing and development without BigQuery setup:

```bash
# 1. Install dependencies
pip install -e .[dev]

# 2. Start dashboard with sample data
streamlit run src/dashboard/app.py --server.port 8503
# View at: http://localhost:8503

# 3. Test triage (offline)
python -m core.cli triage --title "Login 500" --body "after reset" --severity P2 --out out/plan.md

# 4. Explore utilities
python run_util.py                    # List all available utilities
python run_util.py test_mock_mode     # Test mock functionality
```

### Option 2: Real BigQuery Mode
For production use with actual BigQuery data:

```bash
# 1. Configure environment (.env file)
PROJECT_ID=your-gcp-project
BQ_PROJECT_ID=your-gcp-project  
BQ_LOCATION=US
BQ_DATASET=demo_ai
GOOGLE_APPLICATION_CREDENTIALS=path/to/service-account.json
BIGQUERY_REAL=1                       # Enable real mode

# 2. Install with BigQuery support
pip install -e .[bigquery,ingest,dashboard,dev]

# 3. Create BigQuery resources (one-time setup)
python run_util.py create_views

# 4. Start dashboard with real data
streamlit run src/dashboard/app.py --server.port 8503
```

## 📁 Project Structure

The project is organized into logical folders for easy navigation:

```
projectNorthStar/
├── 📊 tests/           # All test files (test_*.py)
├── 🔍 debug/           # Debug utilities (debug_*.py) 
├── 🛠️  utils/           # Data creation & utilities (create_*, check_*, etc.)
├── 📜 scripts/         # Setup & deployment scripts
├── src/                # Main application code
│   ├── bq/             # BigQuery client & queries
│   ├── dashboard/      # Streamlit dashboard
│   ├── pipeline/       # Data processing pipeline
│   └── ...
└── run_util.py         # Convenience script to run any utility
```

## 🛠️ Utility Runner

Use the `run_util.py` script to easily run any utility from the project root:

```bash
# List all available utilities by category
python run_util.py

# Run specific utilities
python run_util.py test_mock_mode           # Test mock mode functionality
python run_util.py create_sample_data       # Generate sample data files
python run_util.py debug_duplicates         # Debug duplicate chunk detection
python run_util.py test_real_mode_config    # Check BigQuery readiness
```

**Available utility categories:**
- **📊 Tests**: `test_mock_mode`, `test_complete_pipeline`, `test_real_mode_config`, etc.
- **🔍 Debug**: `debug_duplicates`, `debug_dates`, `debug_json` 
- **🛠️ Utils**: `create_sample_data`, `check_data`, `setup_dashboard`, etc.
- **📜 Scripts**: `create_views`, `demo_end_to_end`, `gen_eval_set`, etc.

## 🎯 Dashboard

### Mock Mode (Default)
View sample data instantly without BigQuery setup:

```bash
streamlit run src/dashboard/app.py --server.port 8503
# Dashboard shows: Common Issues, Severity Trends, Duplicate Chunks
```

### Real BigQuery Mode  
After setting up BigQuery authentication:

```bash
# 1. Check configuration
python run_util.py test_real_mode_config

# 2. Enable real mode in .env
BIGQUERY_REAL=1

# 3. Create necessary views (one-time)
python run_util.py create_views

# 4. Start dashboard
streamlit run src/dashboard/app.py --server.port 8503
```

### Dashboard Features
- **Common Issues**: Top issue fingerprints with counts and examples
- **Severity Trends**: Weekly severity distribution (P0-P3) with filtering
- **Duplicate Chunks**: Similar content detection with distance metrics
- **Interactive Filters**: Date range and severity selection
- **Data Safety**: Text truncation (≤200 chars) and PII masking
## ⚙️ Environment Configuration

### Mock Mode (No BigQuery Required)
Default mode for development and testing:

```bash
# .env file (or leave BIGQUERY_REAL commented out)
PROJECT_ID=test-project
DATASET=demo_ai
LOCATION=US
# BIGQUERY_REAL=1  # Commented out = Mock mode
```

### Real BigQuery Mode
For production use with actual BigQuery:

```bash
# .env file configuration
PROJECT_ID=your-gcp-project
BQ_PROJECT_ID=your-gcp-project
BQ_LOCATION=US
BQ_DATASET=demo_ai
DATASET=demo_ai
LOCATION=US

# Authentication (choose one method)
# Method 1: Service Account (recommended)
GOOGLE_APPLICATION_CREDENTIALS=path/to/service-account.json

# Method 2: API Key (testing only)
GOOGLE_API_KEY=your-api-key

# Enable real BigQuery mode
BIGQUERY_REAL=1
```

**PowerShell Environment Variables:**
```powershell
$env:PROJECT_ID = "your-gcp-project"
$env:BQ_PROJECT_ID = "your-gcp-project"
$env:BQ_LOCATION = "US"
$env:BQ_DATASET = "demo_ai"
$env:GOOGLE_APPLICATION_CREDENTIALS = "C:\path\to\service-account.json"
$env:BIGQUERY_REAL = "1"
```

### Configuration Validation
Check your setup before switching to real mode:

```bash
python run_util.py test_real_mode_config
# ✅ Shows if BigQuery mode is ready
# ❌ Lists missing requirements
```

## 🏗️ Installation Options

### Minimal (Mock Mode Only)
```bash
pip install -e .
```

### Development (Tests + Mock Mode)
```bash
pip install -e .[dev]
```

### BigQuery Support
```bash
pip install -e .[bigquery]                    # Real BigQuery client
pip install -e .[bigquery,ingest]             # + OCR/PDF processing
pip install -e .[bigquery,dashboard]          # + Streamlit dashboard
pip install -e .[bigquery,ingest,dashboard,dev]  # Full features
```

### External Install (Tagged Release)
```bash
pip install "git+https://github.com/rcmiller01/projectNorthStar@v1.0.0"

## 🔄 Development Workflow

### Starting Fresh (Mock Mode)
```bash
# 1. Test mock functionality
python run_util.py test_mock_mode

# 2. Start dashboard with sample data
streamlit run src/dashboard/app.py --server.port 8503

# 3. Test triage offline
python -m core.cli triage --title "Login timeout" --body "after reset" --severity P2 --out out/plan.md
```

### Moving to Real BigQuery
```bash
# 1. Check BigQuery configuration
python run_util.py test_real_mode_config

# 2. Create BigQuery resources (one-time)
python run_util.py create_views

# 3. Enable real mode in .env file
# Uncomment: BIGQUERY_REAL=1

# 4. Verify real mode connection
python run_util.py test_mock_mode  # Will show RealClient

# 5. Start dashboard with real data
streamlit run src/dashboard/app.py --server.port 8503
```

### Sample Data Recreation
Recreate the complete sample dataset for testing:

```bash
# 1. Generate sample issue files
python run_util.py create_sample_data

# 2. Insert sample data (if in real mode)
python run_util.py insert_demo_data

# 3. Validate data format
python run_util.py check_data

# 4. Verify dashboard data
python run_util.py test_mock_mode
```

## 🎯 Key Workflows

### Testing & Debugging
```bash
# Test complete pipeline
python run_util.py test_complete_pipeline

# Debug specific issues
python run_util.py debug_duplicates    # Duplicate chunk detection
python run_util.py debug_dates         # Date/time processing
python run_util.py debug_json          # JSON data validation

# Dashboard testing
python run_util.py test_dashboard_mock
```

### Data Management
```bash
# Create and manage views
python run_util.py create_views
python run_util.py create_final_views

# Data validation
python run_util.py check_data
python run_util.py check_data_format
python run_util.py check_meta

# Sample data generation
python run_util.py create_sample_data
python run_util.py insert_demo_data
```

### Integration & Setup
```bash
# Integration status
python run_util.py integration_status

# Dashboard setup
python run_util.py setup_dashboard

# Model discovery
python run_util.py discover_models

# Security checks
python run_util.py security_check
```

## Data & Safety
Sample files in `samples/` are synthetic / minimal. No PII shipped. Snippets surfaced are truncated (≤200 chars) and basic masking (emails, bearer tokens, AWS access keys) applies in dashboard & playbooks. Attach only non-sensitive data when experimenting.

### Architecture

**Dual-Mode Design:**
- **Mock Mode**: Uses `StubClient` with comprehensive sample data for development
- **Real Mode**: Uses `RealClient` with actual BigQuery for production
- **Automatic Switching**: Based on `BIGQUERY_REAL` environment variable

Mermaid source: `docs/architecture.mmd`

Generate diagrams:
```bash
# Install Mermaid CLI (one-time)
npm i -g @mermaid-js/mermaid-cli

# Generate PNG + SVG
make arch

# Verify diagram sync
make arch-verify
```

**Windows PowerShell alternative:**
```powershell
scripts/arch_verify.ps1
```

![Architecture overview](docs/architecture.png)

**Component Mapping:**
- **Ingest** → `bq/load.py`, `bq/refresh.py`, `sql/upsert_*`
- **Retrieve** → `retrieval/hybrid.py`, `sql/chunk_vector_search.sql`
- **Dashboard** → `src/dashboard/app.py`, `sql/views_*.sql`
- **Triage** → `core/orchestrator.py`, `experts/kb_writer.py`
- **Testing** → `tests/`, Mock data via `StubClient`
- **Utilities** → `utils/`, `debug/`, accessed via `run_util.py`

## 📋 Project Organization

The project has been reorganized for clarity and ease of use:

### 📁 Directory Structure
```
projectNorthStar/
├── 📊 tests/           # All test files organized by functionality
│   ├── test_mock_mode.py
│   ├── test_real_mode_config.py
│   ├── test_complete_pipeline.py
│   └── test_*.py
├── 🔍 debug/           # Debug utilities for troubleshooting
│   ├── debug_duplicates.py
│   ├── debug_dates.py
│   └── debug_json.py
├── 🛠️  utils/           # Data creation and utility scripts
│   ├── create_sample_data.py
│   ├── insert_demo_data.py
│   ├── check_data.py
│   └── create_*.py, check_*.py
├── 📜 scripts/         # Setup and deployment automation
├── src/                # Core application code
│   ├── bq/             # BigQuery client (Mock + Real)
│   ├── dashboard/      # Streamlit dashboard
│   ├── pipeline/       # Data processing
│   └── ...
└── run_util.py         # Universal utility runner
```

### 🎯 Benefits of Reorganization
- **✅ Clean Root**: Essential files only in project root
- **✅ Logical Grouping**: Related functionality organized together  
- **✅ Easy Discovery**: `run_util.py` lists all available utilities
- **✅ Maintained Links**: All import paths updated automatically
- **✅ Better Testing**: Separate test organization by functionality

### 🚀 Migration Guide
The reorganization maintains backward compatibility:

**Old Way:**
```bash
python test_mock_mode.py           # ❌ File not found
python debug_duplicates.py         # ❌ File not found  
python create_sample_data.py       # ❌ File not found
```

**New Way:**
```bash
python run_util.py test_mock_mode           # ✅ Works
python run_util.py debug_duplicates         # ✅ Works
python run_util.py create_sample_data       # ✅ Works
```

## Overview

**Core Features:**
- **Dual-Mode Operation**: Mock mode for development, Real BigQuery mode for production
- **Intelligent Triage**: AI-assisted issue analysis with vector search and verification
- **Interactive Dashboard**: Real-time analytics over issue data with filtering
- **Multimodal Ingest**: Process logs, PDFs, images with OCR support
- **Smart Routing**: Adaptive retrieval strategies based on query characteristics
- **Comprehensive Testing**: Mock data for reliable testing and development

**Core Components:**
- **Ingest**: logs / pdf / OCR image → chunks → embeddings refresh loop
- **Hybrid Retrieval**: vector + simple lexical with multi-type filtering
- **Triage Orchestrator**: retrieve → draft plan → verifier gating
- **Dashboard Analytics**: common issues, severity trends, duplicate detection
- **Ticket Management**: optional schema with evidence links and resolutions
- **Evaluation Framework**: hit rate / distance / verifier score metrics

## Triage CLI

### Mock Mode (Offline)
Perfect for testing and development:

```bash
# Basic triage
python -m core.cli triage --title "Login 500" --body "after reset" --severity P2 --out out/plan.md

# With routing options
python -m core.cli triage --title "PDF export fails" --body "error message" --router auto --out out/plan.md
```

### Real BigQuery Mode
With live data and embeddings:

```bash
# Set environment (PowerShell example)
$env:BIGQUERY_REAL = "1"
$env:PROJECT_ID = "your-gcp-project"
$env:DATASET = "demo_ai"
$env:LOCATION = "US"

# Run triage with live data
python -m core.cli triage --title "Image upload fails" --body "content-type mismatch" --out out/plan_live.md

# Ticket-based triage
python -m core.cli triage --ticket-id DEMO-1 --severity P1 --out out/DEMO-1.md
```

### Routing Options
The system includes intelligent routing for optimal retrieval:

- **`auto`** (default): Use learned model if available, fallback to heuristics
- **`heuristic`**: Rule-based routing using keyword matching  
- **`learned`**: BigQuery ML model only (requires training)

**Routing Strategies:**
- `logs_only`: Types=['log'], k=8 - for error messages, stack traces
- `pdf_image`: Types=['pdf','image','image_ocr'], k=6 - for documents, manuals
- `mixed`: Types=[], k=10 - for complex queries needing all content types

### Severity Levels
Supported severity annotations (case-insensitive):
- **P0, P1, P2, P3**: Priority levels
- **High, Medium, Low**: Descriptive levels  
- **Unknown**: Default/unclassified

```bash
python -m core.cli triage --title "Database timeout" --severity P1 --out out/critical.md
```

### Triage Sequence (Ticket Flow)

Mermaid source: `docs/triage_sequence.mmd`

Render to PNG (optional):
```bash
mmdc -i docs/triage_sequence.mmd -o docs/triage_sequence.png -b transparent
```

![Triage sequence](docs/triage_sequence.png)

Key mapping:
- Orchestrator logic: `core/orchestrator.py`
- Ticket repo + schema: `bq/tickets.py`, `sql/ddl_tickets.sql`, `sql/insert_*`
- Retrieval: `retrieval/hybrid.py`, `sql/chunk_vector_search.sql`
- Embedding & search: BigQuery `ML.GENERATE_EMBEDDING`, `ML.VECTOR_SEARCH`
- Draft: `experts/kb_writer.py`
- Verify: `verify/kb_verifier.py`
- Writebacks: `ticket_chunk_links`, `resolutions` tables

### Smart Routing with BigQuery ML

The system includes an intelligent router that adapts retrieval strategy based on query characteristics.

**Router Training:**
```bash
# Train BQML logistic regression model for routing
export PROJECT_ID=bq_project_northstar DATASET=demo_ai BIGQUERY_REAL=1
make train-router

# Or directly
python -m core.cli train-router
```

**Router Modes:**
- `auto` (default): Use learned model if available, fallback to heuristics
- `heuristic`: Rule-based routing using keyword matching
- `learned`: BigQuery ML model only (fails if model missing)

**Routing Strategies:**
- `logs_only`: Types=['log'], k=8 - for error messages, stack traces, timeouts
- `pdf_image`: Types=['pdf','image','image_ocr'], k=6 - for documents, diagrams, manuals
- `mixed`: Types=[], k=10 - for complex queries needing all content types

**Example Usage:**
```bash
# Auto routing (recommended)
python -m core.cli triage --title "Database timeout error" --router auto

# Force heuristic routing
python -m core.cli triage --title "PDF export broken" --router heuristic

# Use learned model (requires training)
python -m core.cli triage --title "Documentation missing" --router learned
```

### Graph-lite Expansion (Optional)

Enhance retrieval quality by expanding vector search results with graph neighbors.

**Build Neighbor Relationships:**
```bash
# Create chunk neighbor table from duplicates and co-links
export PROJECT_ID=bq_project_northstar DATASET=demo_ai
make build-neighbors
```

**Usage:**
```bash
# Enable graph expansion with default boost (0.2)
python -m core.cli triage --title "Database error" --graph-boost 0.2

# Custom boost factor and neighbor limit
python -m core.cli triage --title "Upload failure" --graph-boost 0.3
```

**Scoring Formula:**
- `final_score = (1 - graph_boost) * vector_score + graph_boost * neighbor_weight`
- Default: 80% vector similarity + 20% graph boost
- Safe fallback to vector-only if neighbor table missing

### Enhanced Evaluation Metrics

Comprehensive metrics for retrieval quality assessment and performance monitoring.

**Core Metrics (CI-gated):**
- `hit_rate`: Fraction of queries with at least one matching expected term
- `mean_min_distance`: Average minimum distance across retrieved results
- `mean_verifier_score`: Average verification score for generated playbooks

**Ranking Quality Metrics (Informational):**
- `ndcg@5`: Normalized Discounted Cumulative Gain at rank 5
- `mrr`: Mean Reciprocal Rank of first relevant result
- `semantic_cosine`: Cosine similarity between query and chunk embeddings

**Performance Metrics (Informational):**
- `mean_total_ms/p95_total_ms`: Timing statistics from orchestrator telemetry
- `cost_estimates`: ML API calls and bytes processed tracking

**Usage:**
```bash
# Run evaluation with enhanced metrics
make eval
cat metrics/eval_results.json | jq .aggregate

# CI trend analysis with deltas
python scripts/metrics_trend.py
```

**Metrics Output:**
```json
{
  "aggregate": {
    "hit_rate": 0.85,
    "ndcg@5": 0.721,
    "mrr": 0.650,
    "semantic_cosine": {"mean": 0.823, "p25": 0.701, "p50": 0.834, "p75": 0.901},
    "timings": {"mean_total_ms": 45.2, "p95_total_ms": 89.1},
    "cost_estimates": {"total_ml_calls": 125, "avg_ml_calls_per_query": 6.25}
  }
}
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

## Dashboard (Analytics & Visualization)

Real-time analytics dashboard built with Streamlit, supporting both mock and real BigQuery modes.

### Quick Start
```bash
# Mock mode (instant - uses sample data)
streamlit run src/dashboard/app.py --server.port 8503

# Real BigQuery mode (after configuration)
# 1. Enable real mode in .env: BIGQUERY_REAL=1
# 2. Create views: python run_util.py create_views
streamlit run src/dashboard/app.py --server.port 8503
```

### Dashboard Sections

**📊 Common Issues**
- Top issue fingerprints by frequency
- Example text and occurrence counts
- Last seen timestamps
- Interactive date filtering

**📈 Severity Trends** 
- Weekly severity distribution (P0-P3)
- Interactive area charts
- Severity filtering controls
- Trend analysis over time

**🔄 Duplicate Chunks**
- Approximate duplicate detection
- Similarity distance metrics
- Cluster size information
- Expandable detail views

### Installation Options
```bash
# Minimal (mock mode only)
pip install streamlit

# With BigQuery support
pip install -e .[dashboard]

# Full features
pip install -e .[bigquery,dashboard,dev]
```

### Environment Setup
```bash
# Mock mode (default)
# No special configuration needed

# Real BigQuery mode
$env:BIGQUERY_REAL = "1"          # PowerShell
$env:PROJECT_ID = "your-project"
$env:DATASET = "demo_ai"
$env:LOCATION = "US"
```

### Views and Data
The dashboard creates and uses these BigQuery views (auto-created):

- **`view_common_issues`**: Issue fingerprint aggregation with frequency counts
- **`view_issues_by_severity`**: Weekly severity trend data (P0-P3, Unknown)  
- **`view_duplicate_chunks`**: Approximate duplicate clusters via vector search

**Data Safety Features:**
- Text truncation (≤200 characters)
- PII masking (emails, tokens, AWS keys)
- Read-only access (no data modification)
- Configurable row limits

### Development & Testing
```bash
# Test dashboard functionality
python run_util.py test_dashboard_mock

# Debug dashboard data
python run_util.py debug_duplicates

# Check dashboard configuration  
python run_util.py setup_dashboard
```

## 🎮 Demo & Testing

### Quick Demo (Mock Mode)
Instant demonstration without BigQuery setup:

```bash
# 1. Test core functionality
python run_util.py test_mock_mode

# 2. Start dashboard
streamlit run src/dashboard/app.py --server.port 8503

# 3. Run triage examples
python -m core.cli triage --title "Database timeout" --body "connection lost" --severity P1 --out out/demo.md
```

### Full Demo (Real BigQuery)
Complete end-to-end demonstration with live data:

```bash
# Prerequisites: BigQuery configured, BIGQUERY_REAL=1
# 1. Check readiness
python run_util.py test_real_mode_config

# 2. Run comprehensive demo
python run_util.py demo_end_to_end

# 3. Check outputs
# - out/demo_freeform.md (freeform triage)
# - out/demo_ticket.md (ticket-based triage)
```

### Testing Infrastructure

**Mock Mode Testing:**
```bash
# Core functionality tests
python run_util.py test_mock_mode
python run_util.py test_dashboard_mock
python run_util.py test_complete_pipeline

# Specific component tests  
python run_util.py test_embedding
python run_util.py test_pipeline
python run_util.py test_retrieval
```

**Real Mode Validation:**
```bash
# Configuration check
python run_util.py test_real_mode_config

# Connection testing
python run_util.py test_bigquery_client
python run_util.py test_models

# Data validation
python run_util.py check_data
python run_util.py integration_status
```

**Debug Tools:**
```bash
# Issue debugging
python run_util.py debug_duplicates
python run_util.py debug_dates
python run_util.py debug_json

# Data format checking
python run_util.py check_data_format
python run_util.py check_meta
```

## 🏗️ BigQuery Setup

### One-Time Setup
Create necessary BigQuery resources:

```bash
# Method 1: Using utility runner
python run_util.py create_views

# Method 2: Using Make (if available)
make create-views

# Method 3: Direct script execution
python scripts/create_views.py
```

### Remote Models (Advanced)
For full AI-powered features:

```bash
# Create Vertex AI remote models in BigQuery
make create-remote-models

# Set model environment variables
export BQ_EMBED_MODEL=${PROJECT_ID}.${DATASET}.embed_model
export BQ_GEN_MODEL=${PROJECT_ID}.${DATASET}.text_model
```

### Validation
Verify your BigQuery setup:

```bash
# Check all resources
python run_util.py check_bq_resources

# Test model access
python run_util.py test_models

# Validate configuration
python run_util.py test_real_mode_config
```

## Micro Eval

Generates a deterministic synthetic eval set (20 items) and runs comprehensive retrieval metrics.

Stub (offline) or real depending on BIGQUERY_REAL (force stub with `--use-stub`).

```bash
make eval
cat metrics/eval_results.json | jq .aggregate
```

Files produced:
- `metrics/eval_set.jsonl` (input set)
- `metrics/eval_results.json` (per-item + aggregate metrics)

### Metrics Definitions

Core metrics (used for CI gating):
- `hit_rate`: fraction of queries with at least one relevant chunk (substring match)
- `mean_min_distance`: average minimum vector distance across queries
- `mean_verifier_score`: average playbook verification success (may be null if skipped)
- `ndcg_at_k`: normalized Discounted Cumulative Gain at k (ranking quality)
- `mrr`: Mean Reciprocal Rank of first relevant result

Extended metrics (informational):
- `semantic_cosine`: cosine similarity between query and chunk embeddings (p25/p50/p75/mean)
- `timings`: step timing breakdowns in milliseconds (mean/p95)
- `cost_estimates`: ML API calls and bytes processed per query

All metrics are available in `metrics/eval_results.json` under the `aggregate` key.

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
