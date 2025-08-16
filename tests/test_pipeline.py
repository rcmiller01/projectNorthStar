#!/usr/bin/env python3
"""Complete end-to-end test for dashboard data pipeline."""

import sys
from pathlib import Path
import os
from datetime import datetime, timezone, timedelta

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from bq.bigquery_client import make_client
from config import load_env

def test_complete_pipeline():
    """Test the complete data pipeline."""
    print("🚀 Testing Complete Data Pipeline")
    print("=" * 50)
    
    # 1. Load environment
    load_env()
    
    # Check if real BigQuery is enabled
    bigquery_real = os.getenv('BIGQUERY_REAL', 'False').lower() != 'false'
    print(f"1. Environment: BIGQUERY_REAL = {bigquery_real}")
    
    # 2. Create client
    client = make_client()
    print(f"2. Client: {type(client).__name__}")
    
    if not bigquery_real:
        print("❌ BIGQUERY_REAL is not enabled - dashboard will show no data")
        print("   Please set BIGQUERY_REAL=1 in .env file")
        return False
    
    try:
        # 3. Check data exists
        result = client.run_sql_template('inline', {
            'raw_sql': "SELECT COUNT(*) as total FROM `gleaming-bus-468914-a6.demo_ai.chunks`"
        })
        total_chunks = result[0]['total'] if result else 0
        print(f"3. Data: {total_chunks} chunks in BigQuery")
        
        if total_chunks == 0:
            print("❌ No data found - need to insert sample data")
            return False
        
        # 4. Check views exist
        try:
            result = client.run_sql_template('inline', {
                'raw_sql': "SELECT COUNT(*) as count FROM `gleaming-bus-468914-a6.demo_ai.view_common_issues`"
            })
            common_issues_count = result[0]['count'] if result else 0
            print(f"4. Views: view_common_issues has {common_issues_count} rows")
        except Exception as e:
            print(f"❌ view_common_issues error: {e}")
            return False
        
        try:
            result = client.run_sql_template('inline', {
                'raw_sql': "SELECT COUNT(*) as count FROM `gleaming-bus-468914-a6.demo_ai.view_issues_by_severity`" 
            })
            severity_count = result[0]['count'] if result else 0
            print(f"   Views: view_issues_by_severity has {severity_count} rows")
        except Exception as e:
            print(f"❌ view_issues_by_severity error: {e}")
            return False
        
        # 5. Test dashboard queries with current date range
        current_time = datetime.now(timezone.utc)
        start_time = current_time - timedelta(days=30)
        
        start_ts = f"TIMESTAMP('{start_time.strftime('%Y-%m-%d')} 00:00:00 UTC')"
        end_ts = f"TIMESTAMP('{current_time.strftime('%Y-%m-%d')} 23:59:59 UTC')"
        
        print(f"5. Testing dashboard queries with date range:")
        print(f"   From: {start_time.strftime('%Y-%m-%d')}")
        print(f"   To: {current_time.strftime('%Y-%m-%d')}")
        
        # Test common issues query (like dashboard does)
        sql_common = f"""
        SELECT fingerprint, issue_example, count, last_seen
        FROM `gleaming-bus-468914-a6.demo_ai.view_common_issues`
        WHERE last_seen BETWEEN {start_ts} AND {end_ts}
        ORDER BY count DESC
        LIMIT 10
        """
        
        common_rows = client.run_sql_template('inline', {'raw_sql': sql_common})
        print(f"   Common issues query: {len(common_rows)} rows returned")
        
        if len(common_rows) > 0:
            print("   ✅ Dashboard should show common issues")
            print(f"      Top issue: {common_rows[0].get('fingerprint', 'N/A')}")
        else:
            print("   ❌ Dashboard will show empty common issues")
            print("      Likely cause: Data timestamps outside dashboard date range")
        
        # Test severity query
        sql_sev = f"""
        SELECT week, severity, count FROM `gleaming-bus-468914-a6.demo_ai.view_issues_by_severity`
        WHERE week BETWEEN DATE({start_ts}) AND DATE({end_ts})
          AND severity IN ('P0','P1','P2','P3')
        ORDER BY week, severity
        """
        
        sev_rows = client.run_sql_template('inline', {'raw_sql': sql_sev})
        print(f"   Severity trends query: {len(sev_rows)} rows returned")
        
        if len(sev_rows) > 0:
            print("   ✅ Dashboard should show severity trends")
        else:
            print("   ❌ Dashboard will show empty severity trends")
        
        # 6. Summary
        print("\n" + "=" * 50)
        print("📊 PIPELINE TEST SUMMARY:")
        
        success = True
        if total_chunks == 0:
            print("❌ No data in BigQuery")
            success = False
        elif common_issues_count == 0 or severity_count == 0:
            print("❌ Views not working")
            success = False
        elif len(common_rows) == 0 and len(sev_rows) == 0:
            print("❌ Dashboard queries return no data (date range issue)")
            success = False
        else:
            print("✅ Complete pipeline working!")
        
        return success
        
    except Exception as e:
        print(f"❌ Pipeline test failed: {e}")
        return False

def fix_data_timestamps():
    """Fix sample data to have current timestamps."""
    print("\n🔧 Fixing data timestamps...")
    
    load_env()
    client = make_client()
    
    # Update existing demo data to have recent timestamps
    current_time = datetime.now(timezone.utc)
    
    try:
        # Update timestamps for our demo data to be within last 30 days
        sql_update = f"""
        UPDATE `gleaming-bus-468914-a6.demo_ai.chunks`
        SET meta = JSON_SET(
            meta, 
            '$.ingested_at', 
            TIMESTAMP_ADD(TIMESTAMP('{(current_time - timedelta(days=15)).isoformat()}'), 
                         INTERVAL CAST(RAND() * 30 * 24 * 60 * 60 AS INT64) SECOND)
        )
        WHERE JSON_VALUE(meta, '$.source') = 'demo_data'
        """
        
        result = client.run_sql_template('inline', {'raw_sql': sql_update})
        print("✅ Updated demo data timestamps to be recent")
        return True
        
    except Exception as e:
        print(f"❌ Failed to update timestamps: {e}")
        return False

if __name__ == "__main__":
    success = test_complete_pipeline()
    
    if not success:
        print("\n🔧 Attempting to fix issues...")
        if fix_data_timestamps():
            print("\n🔄 Re-testing after fixes...")
            test_complete_pipeline()
    
    print(f"\n🎯 Final result: {'SUCCESS' if success else 'NEEDS ATTENTION'}")
