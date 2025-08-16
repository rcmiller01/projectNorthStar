#!/usr/bin/env python3
"""Quick test of the StubClient raw SQL functionality."""

import sys
import os
sys.path.insert(0, os.path.abspath('.'))
sys.path.insert(0, os.path.join(os.path.abspath('.'), 'src'))

from bq.bigquery_client import make_client

def test_raw_sql():
    client = make_client()
    
    # Test 1: Common Issues Query
    sql1 = """
    SELECT fingerprint, issue_example, count, last_seen
    FROM `test-project.test_dataset.view_common_issues`
    WHERE last_seen BETWEEN TIMESTAMP('2025-08-01 00:00:00 UTC') AND TIMESTAMP('2025-08-15 23:59:59 UTC')
    ORDER BY count DESC
    LIMIT 50
    """
    
    print("Testing Common Issues Query:")
    result1 = client.run_sql_template("_raw.sql", {"raw_sql": sql1})
    print(f"Result: {len(result1)} rows")
    if result1:
        print(f"Sample: {result1[0]}")
    
    # Test 2: Severity Trends Query
    sql2 = """
    SELECT week, severity, count FROM `test-project.test_dataset.view_issues_by_severity`
    WHERE week BETWEEN DATE_TRUNC(TIMESTAMP('2025-08-01 00:00:00 UTC'), WEEK) AND DATE_TRUNC(TIMESTAMP('2025-08-15 23:59:59 UTC'), WEEK)
    AND severity IN ('P0','P1','P2','P3','Unknown')
    ORDER BY week, severity
    """
    
    print("\nTesting Severity Trends Query:")
    result2 = client.run_sql_template("_raw.sql", {"raw_sql": sql2})
    print(f"Result: {len(result2)} rows")
    if result2:
        print(f"Sample: {result2[0]}")

if __name__ == "__main__":
    test_raw_sql()
