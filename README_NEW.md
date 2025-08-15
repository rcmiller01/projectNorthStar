# projectNorthStar

[![CI](https://github.com/rcmiller01/projectNorthStar/actions/workflows/ci.yml/badge.svg)](https://github.com/rcmiller01/projectNorthStar/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)

AI-assisted triage & knowledge retrieval over BigQuery with Vertex AI integration, featuring embeddings, vector search, and a real-time dashboard for issue analysis.

## 🚀 Features

- **BigQuery + Vertex AI Integration**: Remote models for embeddings and text generation
- **Real-time Dashboard**: Streamlit-based analytics dashboard with issue severity tracking
- **Vector Search**: Hybrid retrieval using embeddings and traditional search
- **Issue Triage**: AI-powered automated triage with severity classification
- **Security First**: Proper credential management and data sanitization

## 📋 Prerequisites

- Google Cloud Project with BigQuery and Vertex AI enabled
- Python 3.10+
- Service Account with appropriate permissions:
  - BigQuery Admin
  - Vertex AI User
  - BigQuery Connection Admin

## ⚡ Quick Start

### 1. Environment Setup

Copy the environment template and configure your credentials:

```bash
cp .env.template .env
# Edit .env with your project details and credentials
```

Required environment variables:
```bash
PROJECT_ID=your-project-id
DATASET=demo_ai
LOCATION=US
BIGQUERY_REAL=1
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
```

### 2. Installation

Install with all features enabled:
```bash
pip install -e .[bigquery,ingest,dashboard,dev]
```

### 3. BigQuery Setup

Create remote models and views:
```bash
make create-remote-models
make create-views
```

### 4. Data Ingestion

Ingest sample data and generate embeddings:
```bash
python -m core.cli ingest --path samples --type auto --max-tokens 512 --refresh-loop
```

### 5. Launch Dashboard

Start the analytics dashboard:
```bash
streamlit run src/dashboard/app.py
```

Navigate to http://localhost:8501 to view:
- Issue severity distribution
- Common issues breakdown  
- Duplicate content detection
- Interactive filtering and analytics

### 6. AI Triage

Run automated triage analysis:
```bash
python -m core.cli triage --title "500 after reset" --body "android camera" --severity P1 --out out/triage_plan.md
```

## 🔧 Architecture

![Architecture overview](docs/architecture.png)

Core components:
- **Ingest**: OCR/PDF/logs → chunks → embeddings
- **Retrieval**: Hybrid vector + lexical search with filtering
- **Triage**: AI orchestrator with plan generation and verification
- **Dashboard**: Real-time analytics over BigQuery views
- **Tickets**: Optional ticket management with evidence linking

## 🛡️ Security & Privacy

### Data Protection
- **No Hardcoded Credentials**: All sensitive data uses environment variables
- **Text Sanitization**: Automatic masking of emails, tokens, and API keys
- **Content Truncation**: Dashboard snippets limited to 200 characters
- **Synthetic Samples**: Demo data is non-sensitive and artificially generated

### Credential Management
- **Service Account**: Recommended authentication method
- **Environment Variables**: Sensitive config via `.env` (gitignored)
- **Secure Defaults**: Generic placeholders instead of real project IDs

### Secret Scanning
Automated secret detection in CI:
```bash
make sweep-secrets         # Local secret scan
make sweep-secrets-strict  # Strict mode with lower threshold
```

### Best Practices
1. **Use `.env.template`**: Copy and customize for your environment
2. **Never commit `.env`**: Already in `.gitignore` 
3. **Synthetic Data**: Use non-sensitive test data for demos
4. **Review Changes**: Check for accidentally committed credentials

## 📊 Dashboard Features

The Streamlit dashboard provides real-time analytics:

### Issue Severity Analysis
- Distribution charts showing critical/high/medium/low issues
- Trend analysis with weekly breakdowns
- Severity-based filtering and drill-down

### Common Issues Detection
- Automatic grouping by content similarity
- Occurrence frequency tracking
- Sample content preview with masking

### Duplicate Content Analysis
- Vector-based duplicate detection
- Cluster visualization with member counts
- Content deduplication recommendations

### Interactive Features
- Date range filtering
- Severity level selection
- Real-time BigQuery integration
- Export capabilities for further analysis

## 🧪 Development

### Local Development Setup
```bash
pip install -e .[dev]
make setup-dev
```

### Code Quality
```bash
make check          # Run all checks
make pre-commit-all # Format and lint
```

### Testing
```bash
make eval           # Run evaluation suite
make demo           # End-to-end demo
```

### Release Process
```bash
make release-dry-run part=patch  # Preview changes
make release part=minor          # Create release
```

## 📁 Project Structure

```
├── src/                  # Main source code
│   ├── dashboard/        # Streamlit dashboard
│   └── bq/              # BigQuery integration
├── scripts/             # Utility scripts
├── sql/                 # SQL queries and schemas
├── samples/             # Demo data (synthetic)
├── docs/                # Documentation and diagrams
├── tests/               # Test suite
└── .env.template        # Environment template
```

## 🤝 Contributing

1. **Fork and Clone**: Create your own copy
2. **Environment Setup**: Copy `.env.template` to `.env`
3. **Install Dependencies**: `pip install -e .[dev]`
4. **Make Changes**: Follow code style guidelines
5. **Test**: Run `make check` and `make eval`
6. **Submit PR**: Include tests and documentation

## 📄 License

Released under the MIT License. See [LICENSE](LICENSE) for details.

## 🔗 Resources

- [BigQuery ML Documentation](https://cloud.google.com/bigquery/docs/ml-overview)
- [Vertex AI Documentation](https://cloud.google.com/vertex-ai/docs)
- [Streamlit Documentation](https://docs.streamlit.io/)

---

**⚠️ Security Notice**: This project uses environment variables for configuration. Never commit real credentials or API keys. Use the provided `.env.template` and ensure your `.env` file is gitignored.
