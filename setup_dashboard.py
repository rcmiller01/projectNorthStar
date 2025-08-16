#!/usr/bin/env python3
"""Complete setup script for dashboard with sample data."""

import os
import sys
import json
from pathlib import Path
from datetime import datetime, timedelta
import random

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from bq.bigquery_client import make_client
from config import load_env


def setup_sample_data():
    """Create and insert sample data for dashboard."""
    print("🚀 Setting up sample data for dashboard...")
    
    load_env()
    client = make_client()
    
    # Check if we're in real mode
    is_real = os.getenv('BIGQUERY_REAL', 'False').lower() == 'true'
    print(f"📊 BigQuery mode: {'Real' if is_real else 'Mock'}")
    
    if not is_real:
        print("⚠️  BIGQUERY_REAL is not enabled. Dashboard will show mock data.")
        return False
    
    # Sample incidents for the last 7 days (ensure they're recent)
    base_date = datetime.now() - timedelta(days=7)
    
    incidents = [
        {"content": "Authentication service down - 100% error rate", "severity": "P0"},
        {"content": "Database primary node failed", "severity": "P0"},
        {"content": "Payment API returning 500 errors", "severity": "P1"},
        {"content": "SSL certificate expires in 2 days", "severity": "P1"},
        {"content": "Memory usage high on web servers", "severity": "P2"},
        {"content": "Slow query in user dashboard", "severity": "P2"},
        {"content": "Log rotation not working", "severity": "P3"},
        {"content": "UI alignment issue on mobile", "severity": "P3"},
    ]
    
    # Insert recent data
    values_list = []
    for i, incident in enumerate(incidents * 5):  # 40 total incidents
        # Random time in last 7 days
        random_hours = random.randint(0, 7 * 24)
        incident_time = base_date + timedelta(hours=random_hours)
        
        chunk_id = f"recent_chunk_{i:03d}"
        doc_id = f"recent_doc_{i // 5:02d}"
        
        meta_obj = {
            "severity": incident["severity"],
            "ingested_at": incident_time.isoformat() + "Z",
            "source": "recent_demo",
            "category": "incident"
        }
        meta_json = json.dumps(meta_obj).replace("'", "\\'")
        embedding_str = "[" + ",".join(["0.1"] * 768) + "]"
        
        values_list.append(f"""(
            '{chunk_id}',
            '{doc_id}',
            '{incident["content"]}',
            PARSE_JSON('{meta_json}'),
            {embedding_str}
        )""")
    
    sql = f"""
    INSERT INTO `gleaming-bus-468914-a6.demo_ai.chunks`
    (chunk_id, doc_id, content, meta, embedding)
    VALUES
    {','.join(values_list)}
    """
    
    try:
        client.run_sql_template('inline', {'raw_sql': sql})
        print(f"✅ Inserted {len(values_list)} recent incidents")
        return True
    except Exception as e:
        print(f"❌ Failed to insert data: {e}")
        return False


def verify_views():
    """Verify that views exist and have data."""
    print("🔍 Verifying dashboard views...")
    
    load_env()
    client = make_client()
    
    views = [
        "view_common_issues",
        "view_issues_by_severity"
    ]
    
    for view in views:
        try:
            result = client.run_sql_template('inline', {
                'raw_sql': f'SELECT COUNT(*) as count FROM `gleaming-bus-468914-a6.demo_ai.{view}`'
            })
            count = result[0]['count'] if result else 0
            print(f"✅ {view}: {count} rows")
        except Exception as e:
            print(f"❌ {view}: Error - {e}")
    
    return True


def test_dashboard_queries():
    """Test the actual queries the dashboard uses."""
    print("🎯 Testing dashboard queries...")
    
    load_env()
    client = make_client()
    
    # Test severity query (last 30 days)
    end_time = datetime.now()
    start_time = end_time - timedelta(days=30)
    
    severity_sql = f"""
    SELECT week, severity, COUNT(*) as issue_count
    FROM `gleaming-bus-468914-a6.demo_ai.view_issues_by_severity`
    WHERE week BETWEEN TIMESTAMP('{start_time.isoformat()}') 
                   AND TIMESTAMP('{end_time.isoformat()}')
    GROUP BY week, severity
    ORDER BY week, severity
    LIMIT 10
    """
    
    try:
        result = client.run_sql_template('inline', {'raw_sql': severity_sql})
        print(f"✅ Severity query: {len(result)} rows")
        if result:
            for row in result[:3]:
                print(f"   {row['week']}: {row['severity']} = {row['issue_count']}")
    except Exception as e:
        print(f"❌ Severity query failed: {e}")
    
    # Test common issues query
    common_sql = f"""
    SELECT issue_fingerprint, count, issue_example
    FROM `gleaming-bus-468914-a6.demo_ai.view_common_issues`
    WHERE last_seen BETWEEN TIMESTAMP('{start_time.isoformat()}')
                        AND TIMESTAMP('{end_time.isoformat()}')
    ORDER BY count DESC
    LIMIT 5
    """
    
    try:
        result = client.run_sql_template('inline', {'raw_sql': common_sql})
        print(f"✅ Common issues query: {len(result)} rows")
        if result:
            for row in result[:2]:
                print(f"   {row['issue_fingerprint']}: {row['count']} times")
    except Exception as e:
        print(f"❌ Common issues query failed: {e}")


def main():
    """Run complete setup and verification."""
    print("🎬 ProjectNorthStar Dashboard Setup")
    print("=" * 50)
    
    # Step 1: Setup sample data
    if setup_sample_data():
        print()
        
        # Step 2: Verify views
        verify_views()
        print()
        
        # Step 3: Test dashboard queries
        test_dashboard_queries()
        print()
        
        print("🎉 Setup complete!")
        print("💡 Dashboard should now show data at http://localhost:8501")
        print("📝 If dashboard is empty, check date range filters")
    else:
        print("💥 Setup failed - check BigQuery configuration")


if __name__ == "__main__":
    main()
