# projectNorthStar

[![CI](https://github.com/rcmiller01/projectNorthStar/actions/workflows/ci.yml/badge.svg)](https://github.com/rcmiller01/projectNorthStar/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)

AI-assisted triage & knowledge retrieval over BigQuery with embeddings, vector search, and playbook verification. Features dual-mode operation for both development (mock) and production (BigQuery) environments.

## 🚀 Quick Start

### Demo Mode (Instant - No Setup Required)
Perfect for evaluation and testing:

```bash
# 1. Install and start dashboard
pip install -e .[dev]
streamlit run src/dashboard/app.py --server.port 8503

# 2. View dashboard at: http://localhost:8503
# Shows: Common Issues, Severity Trends, Duplicate Chunks

# 3. Test triage functionality  
python -m core.cli triage --title "Login timeout" --body "database error" --severity P1 --out out/demo.md

# 4. Explore all utilities
python run_util.py  # Lists all available tools by category
```

### Production Mode (BigQuery Required)
For real-world deployment:

```bash
# 1. Configure .env file
PROJECT_ID=your-gcp-project
BQ_PROJECT_ID=your-gcp-project
BQ_LOCATION=US
BQ_DATASET=demo_ai
GOOGLE_APPLICATION_CREDENTIALS=path/to/service-account.json
BIGQUERY_REAL=1

# 2. Install with BigQuery support
pip install -e .[bigquery,ingest,dashboard,dev]

# 3. Create BigQuery resources
python run_util.py create_views

# 4. Start dashboard with real data
streamlit run src/dashboard/app.py --server.port 8503
```

## 🏗️ Architecture & Features

![System Architecture](docs/architecture.png)

**System Overview**: The above diagram shows the complete system architecture, illustrating the flow from local CLI operations through BigQuery storage and processing to the dashboard interface. The system supports both mock mode (for development) and production mode (with real BigQuery integration).

**Core Components:**
- **Dual-Mode Client**: Automatic switching between mock (StubClient) and real (BigQuery) modes
- **Interactive Dashboard**: Real-time analytics with filtering (Streamlit)
- **AI Triage**: Intelligent issue analysis with vector search and verification
- **Multimodal Ingest**: Process logs, PDFs, images with OCR support
- **Smart Routing**: Adaptive retrieval strategies based on query characteristics

**Key Features:**
- ✅ **Zero-Setup Demo**: Works instantly without external dependencies
- ✅ **Production Ready**: Seamless transition to BigQuery with single config change
- ✅ **Comprehensive Testing**: Mock data enables reliable development and testing
- ✅ **Organized Structure**: Clean separation of tests, utilities, and core code
- ✅ **Safety Features**: PII masking, text truncation, read-only dashboard access

## 📊 Dashboard

![Dashboard Screenshot](docs/dashboard.png)

**Interactive Analytics Interface**: The dashboard provides real-time insights into system performance and issue patterns. It operates in both mock mode (with sample data) and production mode (with live BigQuery data).

Three main analytical views:

1. **Common Issues**: Top issue fingerprints with frequency and examples
2. **Severity Trends**: Weekly P0-P3 distribution with interactive filtering  
3. **Duplicate Detection**: Similar content clusters with distance metrics

**Features**: Date range filtering, severity selection, expandable details, real-time updates.

## 🛠️ Development Tools

**Utility Runner**: Centralized access to all tools
```bash
python run_util.py                    # List all utilities
python run_util.py test_mock_mode     # Test core functionality
python run_util.py test_real_mode_config  # Validate BigQuery setup
python run_util.py create_sample_data # Generate test data
```

**Testing Categories:**
- **Core Tests**: Mock mode, pipeline, BigQuery client
- **Integration**: End-to-end testing, real mode validation
- **Debug Tools**: Duplicate detection, date processing, JSON validation
- **Data Management**: Sample creation, format validation, view setup

## 🎯 Triage CLI

**Mock Mode** (offline):
```bash
python -m core.cli triage --title "Database timeout" --body "connection failed" --severity P1 --out out/plan.md
```

**Production Mode** (with BigQuery):
```bash
# Freeform triage
python -m core.cli triage --title "API errors" --body "500 responses" --severity P2 --out out/live.md

# Ticket-based triage
python -m core.cli triage --ticket-id DEMO-1 --severity P1 --out out/ticket.md
```

**Routing Options:**
- `auto`: Learned model with heuristic fallback (default)
- `heuristic`: Rule-based keyword matching
- `learned`: BigQuery ML model only

## 📁 Project Organization

```
projectNorthStar/
├── tests/              # All test files (test_*.py)
├── debug/              # Debug utilities (debug_*.py)
├── utils/              # Data creation & utilities
├── scripts/            # Setup & deployment scripts
├── src/                # Core application code
│   ├── bq/             # BigQuery client (Mock + Real)
│   ├── dashboard/      # Streamlit analytics dashboard
│   ├── pipeline/       # Data processing pipeline
│   └── ...
└── run_util.py         # Universal utility runner
```

## ⚙️ Environment Configuration

**Mock Mode** (default):
```bash
# No configuration needed - works out of the box
```

**Production Mode**:
```bash
# .env file
PROJECT_ID=your-gcp-project
BQ_PROJECT_ID=your-gcp-project
BQ_LOCATION=US
BQ_DATASET=demo_ai
GOOGLE_APPLICATION_CREDENTIALS=path/to/service-account.json
BIGQUERY_REAL=1  # Enable production mode
```

**Validation**:
```bash
python run_util.py test_real_mode_config  # Check BigQuery readiness
```

## 🚀 Installation Options

```bash
# Minimal (demo mode only)
pip install -e .

# Development (with testing tools)
pip install -e .[dev]

# Production (with BigQuery support)
pip install -e .[bigquery,ingest,dashboard,dev]
```

## 🎮 Demo & Evaluation

**Instant Demo**:
```bash
streamlit run src/dashboard/app.py --server.port 8503
python -m core.cli triage --title "System error" --body "timeout" --severity P1 --out out/demo.md
```

**Full Pipeline Test**:
```bash
python run_util.py test_complete_pipeline
python run_util.py test_mock_mode
```

**Production Validation**:
```bash
python run_util.py test_real_mode_config
python run_util.py create_views
```

## 📋 Data & Safety

- **Sample Data**: Synthetic/minimal data for demo purposes
- **PII Protection**: Text truncation (≤200 chars) and pattern masking
- **Read-Only Access**: Dashboard provides view-only analytics
- **Dual Mode**: Mock mode for safe development, production mode for real data

## �️ Advanced Features

**Remote Models** (BigQuery ML + Vertex AI):
```bash
make create-remote-models  # One-time setup
export BQ_EMBED_MODEL=${PROJECT_ID}.${DATASET}.embed_model
export BQ_GEN_MODEL=${PROJECT_ID}.${DATASET}.text_model
```

**Multimodal Ingest**:
```bash
python -m core.cli ingest --path samples --type auto --max-tokens 512 --refresh-loop
```

**Evaluation Framework**:
```bash
make eval
cat metrics/eval_results.json | jq .aggregate
```

## 📜 License

Released under the MIT License. See `LICENSE` file for details.

## 📋 Additional Resources

- **[System Survey](docs/survey.md)**: Comprehensive analysis of system capabilities and evaluation criteria
- **[Architecture Diagram](docs/architecture.mmd)**: Rebuildable Mermaid source for system architecture visualization
- **Build Architecture**: Use `make arch` or the VS Code task "Build architecture (PNG+SVG)" to regenerate diagrams
