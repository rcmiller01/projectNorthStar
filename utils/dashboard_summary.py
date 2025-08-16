#!/usr/bin/env python3
"""Dashboard data check."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from bq.bigquery_client import make_client
from config import load_env

def check_dashboard_data():
    """Check current dashboard data status."""
    load_env()
    client = make_client()
    
    print(f"🔍 Client type: {type(client).__name__}")
    
    try:
        # Check chunks count
        result = client.run_sql_template('inline', {
            'raw_sql': "SELECT COUNT(*) as total FROM `gleaming-bus-468914-a6.demo_ai.chunks`"
        })
        total = result[0]['total'] if result else 0
        print(f"📊 Total chunks: {total}")
        
        # Check severity distribution
        result = client.run_sql_template('inline', {
            'raw_sql': """
            SELECT 
                JSON_VALUE(meta, '$.severity') as severity,
                COUNT(*) as count
            FROM `gleaming-bus-468914-a6.demo_ai.chunks`
            WHERE JSON_VALUE(meta, '$.severity') IS NOT NULL
            GROUP BY JSON_VALUE(meta, '$.severity')
            ORDER BY JSON_VALUE(meta, '$.severity')
            """
        })
        
        print("📈 Severity distribution:")
        for row in result:
            print(f"  {row['severity']}: {row['count']} incidents")
        
        # Check if views exist and have data
        print("\n📋 Checking views:")
        
        # Common issues view
        try:
            result = client.run_sql_template('inline', {
                'raw_sql': "SELECT COUNT(*) as count FROM `gleaming-bus-468914-a6.demo_ai.view_common_issues`"
            })
            count = result[0]['count'] if result else 0
            print(f"  view_common_issues: {count} rows")
        except Exception as e:
            print(f"  view_common_issues: ERROR - {str(e)[:100]}")
        
        # Severity view  
        try:
            result = client.run_sql_template('inline', {
                'raw_sql': "SELECT COUNT(*) as count FROM `gleaming-bus-468914-a6.demo_ai.view_issues_by_severity`"
            })
            count = result[0]['count'] if result else 0
            print(f"  view_issues_by_severity: {count} rows")
        except Exception as e:
            print(f"  view_issues_by_severity: ERROR - {str(e)[:100]}")
            
        return True
        
    except Exception as e:
        print(f"❌ Error checking status: {e}")
        return False

if __name__ == "__main__":
    success = check_dashboard_data()
    print(f"\n✅ Dashboard data check {'completed' if success else 'failed'}")
