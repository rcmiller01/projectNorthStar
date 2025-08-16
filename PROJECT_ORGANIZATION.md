# Project Organization and Usage Guide

## 📁 New Project Structure

The project has been reorganized with a clean separation of concerns:

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

## 🚀 Running Utilities

Use the new `run_util.py` script to run any utility from the project root:

```bash
# List all available utilities
python run_util.py

# Run specific utilities
python run_util.py test_mock_mode           # Test mock mode
python run_util.py create_sample_data       # Create sample data
python run_util.py debug_duplicates         # Debug duplicate chunks
python run_util.py test_real_mode_config    # Check real BQ config
```

## 📊 Dashboard Usage

### Mock Mode (Current - Default)
```bash
# Start dashboard with sample data
streamlit run src/dashboard/app.py --server.port 8503
# View at: http://localhost:8503
```

### Real BigQuery Mode
```bash
# 1. Ensure BigQuery dataset and views exist
python run_util.py create_views

# 2. Enable real mode in .env file
# Uncomment: BIGQUERY_REAL=1

# 3. Start dashboard with real data
streamlit run src/dashboard/app.py --server.port 8503
```

## 🔧 BigQuery Mode Configuration

### ✅ Current Status: READY for Real Mode

**Environment Configuration:**
- ✅ Service Account: Configured and file exists
- ✅ Project ID: `gleaming-bus-468914-a6`
- ✅ Dataset: `demo_ai` 
- ✅ Location: `US`
- ✅ Dependencies: `google-cloud-bigquery` installed

**To Switch to Real Mode:**
1. Uncomment `BIGQUERY_REAL=1` in `.env` file
2. Ensure BigQuery views exist: `python run_util.py create_views`
3. Dashboard will automatically use real BigQuery data

### Mock vs Real Mode Toggle

The system automatically switches between modes based on the `BIGQUERY_REAL` environment variable:

- **Mock Mode** (Default): Uses `StubClient` with sample data
- **Real Mode** (`BIGQUERY_REAL=1`): Uses `RealClient` with actual BigQuery

## 📋 Key Utilities by Category

### 🧪 Testing
- `test_mock_mode` - Verify mock mode functionality
- `test_real_mode_config` - Check real BigQuery readiness
- `test_complete_pipeline` - End-to-end pipeline test
- `test_dashboard_mock` - Dashboard functionality test

### 🔍 Debugging  
- `debug_duplicates` - Debug duplicate chunk detection
- `debug_dates` - Debug date/time issues
- `debug_json` - Debug JSON processing

### 🛠️ Data & Setup
- `create_sample_data` - Generate sample issue data
- `insert_demo_data` - Insert demo data into BigQuery
- `create_views` - Create BigQuery views
- `setup_dashboard` - Dashboard setup utilities

### 📊 Analysis
- `dashboard_summary` - Dashboard data summary
- `integration_status` - Check integration status
- `check_data` - Validate data format

## 🎯 Sample Data Recreation

To recreate the complete sample dataset:

```bash
# 1. Create sample files
python run_util.py create_sample_data

# 2. Insert into BigQuery (if in real mode)
python run_util.py insert_demo_data

# 3. Create necessary views
python run_util.py create_views

# 4. Verify data
python run_util.py check_data
```

## 🔄 Development Workflow

### Starting Fresh (Mock Mode)
```bash
# 1. Test mock mode
python run_util.py test_mock_mode

# 2. Start dashboard
streamlit run src/dashboard/app.py --server.port 8503
```

### Moving to Real BigQuery
```bash
# 1. Check readiness
python run_util.py test_real_mode_config

# 2. Create BigQuery resources
python run_util.py create_views

# 3. Enable real mode
# Edit .env: uncomment BIGQUERY_REAL=1

# 4. Test real connection
python run_util.py test_mock_mode  # Will show RealClient

# 5. Start dashboard with real data
streamlit run src/dashboard/app.py --server.port 8503
```

## 📁 File Movements Summary

**Moved to `tests/`:**
- All `test_*.py` files for organized testing

**Moved to `debug/`:**
- `debug_duplicates.py`, `debug_dates.py`, `debug_json.py`

**Moved to `utils/`:**
- `create_*.py` - Data and view creation scripts
- `check_*.py` - Data validation scripts  
- `insert_demo_data.py`, `setup_dashboard.py`
- `integration_status.py`, `discover_models.py`
- Other utility scripts

**Benefits:**
- ✅ Clean project root
- ✅ Logical organization
- ✅ Easy script discovery
- ✅ Maintained functionality
- ✅ Ready for both mock and real modes

## 🎯 Next Steps

1. **Dashboard Testing**: Verify all three dashboard sections display correctly
2. **Real Mode Testing**: Test with `BIGQUERY_REAL=1` when ready
3. **Data Pipeline**: Run complete pipeline with real data
4. **Production Ready**: Both mock and real modes fully functional
