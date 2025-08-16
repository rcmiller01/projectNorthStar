#!/usr/bin/env python3
"""Test mock mode dashboard data."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from bq.bigquery_client import make_client
from config import load_env

def test_mock_mode():
    """Test that mock mode provides sample data for dashboard."""
    
    load_env()
    client = make_client()
    
    print(f"🔍 Client type: {type(client).__name__}")
    
    # Test common issues query
    common_issues = client.run_sql_template('inline', {
        'raw_sql': 'SELECT * FROM view_common_issues LIMIT 5'
    })
    print(f"📊 Common issues: {len(common_issues)} rows")
    for issue in common_issues[:2]:
        print(f"  - {issue.get('issue_fingerprint', 'N/A')}: {issue.get('count', 0)} occurrences")
    
    # Test severity trends query  
    severity_trends = client.run_sql_template('inline', {
        'raw_sql': 'SELECT * FROM view_issues_by_severity LIMIT 5'
    })
    print(f"📈 Severity trends: {len(severity_trends)} rows")
    for trend in severity_trends[:2]:
        print(f"  - Week {trend.get('week', 'N/A')}: {trend.get('severity', 'N/A')} = {trend.get('issue_count', 0)}")
    
    # Test duplicates query
    duplicates = client.run_sql_template('inline', {
        'raw_sql': 'SELECT * FROM view_duplicate_chunks LIMIT 5'
    })
    print(f"🔄 Duplicate chunks: {len(duplicates)} rows")
    for dup in duplicates[:2]:
        print(f"  - Group {dup.get('group_id', 'N/A')}: {dup.get('size', 0)} members")
    
    if common_issues and severity_trends:
        print("\n✅ Mock mode working! Dashboard should show sample data.")
        return True
    else:
        print("\n❌ Mock mode not working properly.")
        return False

if __name__ == "__main__":
    test_mock_mode()
