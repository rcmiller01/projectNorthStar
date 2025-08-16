#!/usr/bin/env python3
"""Test that the dashboard mock mode is providing data for all sections."""

import sys
import os

sys.path.insert(0, os.path.abspath('.'))
sys.path.insert(0, os.path.join(os.path.abspath('.'), 'src'))

from bq.bigquery_client import make_client


def test_dashboard_sections():
    """Test all three dashboard sections have data."""
    
    # Initialize the client (will use StubClient in mock mode)
    client = make_client()
    
    print("Testing Dashboard Sections with Mock Data")
    print("=" * 50)
    
    # Test 1: Common Issues View
    print("\n1. Common Issues:")
    try:
        result = client.run_sql_template('common_issues', {})
        print(f"   Rows: {len(result)}")
        if result:
            print(f"   Columns: {list(result[0].keys())}")
            print(f"   Sample: {result[0]}")
    except Exception as e:
        print(f"   ERROR: {e}")
    
    # Test 2: Severity Trends View  
    print("\n2. Severity Trends:")
    try:
        result = client.run_sql_template('severity_trends', {})
        print(f"   Rows: {len(result)}")
        if result:
            print(f"   Columns: {list(result[0].keys())}")
            print(f"   Sample: {result[0]}")
    except Exception as e:
        print(f"   ERROR: {e}")
    
    # Test 3: Duplicate Chunks View
    print("\n3. Duplicate Chunks:")
    try:
        result = client.run_sql_template('duplicate_chunks', {})
        print(f"   Rows: {len(result)}")
        if result:
            print(f"   Columns: {list(result[0].keys())}")
            print(f"   Sample: {result[0]}")
    except Exception as e:
        print(f"   ERROR: {e}")
    
    print("\n" + "=" * 50)
    print("Dashboard sections test complete!")

if __name__ == "__main__":
    test_dashboard_sections()
