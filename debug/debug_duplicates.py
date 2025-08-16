#!/usr/bin/env python3
"""Debug duplicate chunks data."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from bq.bigquery_client import make_client
from config import load_env

load_env()
client = make_client()

print("🔍 Testing duplicate chunks query...")

# Test the exact query the dashboard uses
result = client.run_sql_template('inline', {
    'raw_sql': 'SELECT * FROM `${PROJECT_ID}.${DATASET}.view_duplicate_chunks` LIMIT 10'
})

print(f"📊 Duplicate chunks result: {len(result)} rows")
for i, row in enumerate(result[:3]):
    print(f"  Row {i+1}: {row}")
    print(f"    Keys: {list(row.keys())}")
