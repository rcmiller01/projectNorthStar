#!/usr/bin/env python3
"""Check date ranges in data."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from bq.bigquery_client import make_client
from config import load_env

load_env()
client = make_client()

# Check date range
result = client.run_sql_template('inline', {
    'raw_sql': """
    SELECT 
        MIN(JSON_VALUE(meta, '$.ingested_at')) as min_date,
        MAX(JSON_VALUE(meta, '$.ingested_at')) as max_date,
        COUNT(*) as total_with_dates
    FROM `gleaming-bus-468914-a6.demo_ai.chunks`
    WHERE JSON_VALUE(meta, '$.ingested_at') IS NOT NULL
    """
})

print('Data date range:')
for k, v in result[0].items():
    print(f'  {k}: {v}')

# Check if views return data without date filters
result = client.run_sql_template('inline', {
    'raw_sql': "SELECT COUNT(*) as total FROM `gleaming-bus-468914-a6.demo_ai.view_common_issues`"
})
print(f"\nView data (no date filter): {result[0]['total']} rows")

# Check recent data
result = client.run_sql_template('inline', {
    'raw_sql': """
    SELECT 
        fingerprint, issue_example, count, last_seen
    FROM `gleaming-bus-468914-a6.demo_ai.view_common_issues`
    ORDER BY count DESC
    LIMIT 5
    """
})

print("\nSample view data:")
for row in result:
    print(f"  {row['fingerprint']}: {row['count']} occurrences")
    print(f"    Last seen: {row['last_seen']}")
    print(f"    Example: {row['issue_example'][:50]}...")
    print()
