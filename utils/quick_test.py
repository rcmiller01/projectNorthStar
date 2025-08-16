#!/usr/bin/env python3
"""Quick test to verify dashboard data."""

from bq.bigquery_client import make_client
from config import load_env

def main():
    print("🔍 Testing dashboard data availability...")
    
    load_env()
    client = make_client()
    
    # Test 1: Check total chunks
    result = client.run_sql_template('inline', {
        'raw_sql': 'SELECT COUNT(*) as count FROM `gleaming-bus-468914-a6.demo_ai.chunks`'
    })
    print(f"✅ Total chunks: {result[0]['count'] if result else 0}")
    
    # Test 2: Check severity view
    result = client.run_sql_template('inline', {
        'raw_sql': 'SELECT COUNT(*) as count FROM `gleaming-bus-468914-a6.demo_ai.view_issues_by_severity`'
    })
    print(f"✅ Severity view rows: {result[0]['count'] if result else 0}")
    
    # Test 3: Check common issues view
    result = client.run_sql_template('inline', {
        'raw_sql': 'SELECT COUNT(*) as count FROM `gleaming-bus-468914-a6.demo_ai.view_common_issues`'
    })
    print(f"✅ Common issues view rows: {result[0]['count'] if result else 0}")
    
    # Test 4: Check recent data in severity view
    result = client.run_sql_template('inline', {
        'raw_sql': """
        SELECT severity, COUNT(*) as count 
        FROM `gleaming-bus-468914-a6.demo_ai.view_issues_by_severity` 
        WHERE week >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 60 DAY)
        GROUP BY severity 
        ORDER BY severity
        """
    })
    
    print("📊 Recent severity data:")
    for row in result:
        print(f"   {row['severity']}: {row['count']} issues")
    
    print("\n🎯 If counts are > 0, data exists. If dashboard shows empty, it's a query/filtering issue.")

if __name__ == "__main__":
    main()
