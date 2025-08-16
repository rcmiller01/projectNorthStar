#!/usr/bin/env python3
"""Quick check of data format."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from bq.bigquery_client import make_client
from config import load_env
import json

load_env()
client = make_client()

# Check all data
result = client.run_sql_template('inline', {
    'raw_sql': "SELECT COUNT(*) as total_chunks FROM `gleaming-bus-468914-a6.demo_ai.chunks`"
})

print('Total chunks:', result[0]['total_chunks'] if result else 0)

# Check severity view data
result = client.run_sql_template('inline', {
    'raw_sql': "SELECT * FROM `gleaming-bus-468914-a6.demo_ai.view_issues_by_severity` LIMIT 10"
})

print('Severity view data:')
if result:
    for r in result[:5]:
        print(f"  Week: {r.get('week', 'N/A')}")
        print(f"  Severity: {r.get('severity', 'N/A')}")
        print(f"  Count: {r.get('issue_count', 'N/A')}")
        print("---")
else:
    print("  No data found")

# Also check the meta format of existing data
result = client.run_sql_template('inline', {
    'raw_sql': "SELECT JSON_VALUE(meta, '$.severity') as severity_field FROM `gleaming-bus-468914-a6.demo_ai.chunks` LIMIT 3"
})
print('\nSeverity fields:')
for r in result[:3]:
    print(f"  {r.get('severity_field', 'NULL')}")
