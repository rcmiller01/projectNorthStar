#!/usr/bin/env python3
"""
Complete end-to-end verification of the dashboard pipeline.
This script tests all components from data generation to dashboard views.
"""

import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from bq.bigquery_client import make_client
from config import load_env
from datetime import datetime, timedelta
import json


def test_environment():
    """Test environment configuration."""
    print("🔧 Testing environment configuration...")
    
    load_env()
    
    # Check required environment variables
    required_vars = ['PROJECT_ID', 'DATASET', 'LOCATION']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing environment variables: {missing_vars}")
        return False
    
    bigquery_real = os.getenv('BIGQUERY_REAL', 'False').lower() != 'false'
    print(f"✅ Environment OK - BigQuery real mode: {bigquery_real}")
    return True


def test_bigquery_connection():
    """Test BigQuery client connection."""
    print("🔗 Testing BigQuery connection...")
    
    try:
        client = make_client()
        client_type = type(client).__name__
        print(f"✅ BigQuery client created: {client_type}")
        
        # Test a simple query
        result = client.run_sql_template('inline', {
            'raw_sql': f"SELECT COUNT(*) as total FROM `{os.getenv('PROJECT_ID')}.{os.getenv('DATASET')}.chunks`"
        })
        
        total = result[0]['total'] if result else 0
        print(f"✅ BigQuery query successful - {total} chunks in table")
        
        return True, total
        
    except Exception as e:
        print(f"❌ BigQuery connection failed: {e}")
        return False, 0


def test_sample_data():
    """Test sample data generation and insertion."""
    print("📊 Testing sample data generation...")
    
    try:
        # Import and run sample data creation
        import sys
        import os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'utils'))
        import create_sample_data
        total_created = create_sample_data.create_sample_files()
        print(f"✅ Sample data files created: {total_created} issues")
        
        # Test direct data insertion
        import insert_demo_data
        success = insert_demo_data.insert_sample_data()
        
        if success:
            print("✅ Sample data inserted successfully")
            return True
        else:
            print("❌ Sample data insertion failed")
            return False
            
    except Exception as e:
        print(f"❌ Sample data generation failed: {e}")
        return False


def test_views():
    """Test BigQuery views creation and data."""
    print("👁️ Testing BigQuery views...")
    
    try:
        client = make_client()
        project_id = os.getenv('PROJECT_ID')
        dataset = os.getenv('DATASET')
        
        # Test common issues view
        result = client.run_sql_template('inline', {
            'raw_sql': f"SELECT COUNT(*) as count FROM `{project_id}.{dataset}.view_common_issues`"
        })
        common_count = result[0]['count'] if result else 0
        print(f"✅ Common issues view: {common_count} rows")
        
        # Test severity view
        result = client.run_sql_template('inline', {
            'raw_sql': f"SELECT COUNT(*) as count FROM `{project_id}.{dataset}.view_issues_by_severity`"
        })
        severity_count = result[0]['count'] if result else 0
        print(f"✅ Severity view: {severity_count} rows")
        
        # Test severity distribution
        result = client.run_sql_template('inline', {
            'raw_sql': f"""
            SELECT severity, COUNT(*) as count 
            FROM `{project_id}.{dataset}.view_issues_by_severity`
            GROUP BY severity 
            ORDER BY severity
            """
        })
        
        print("📈 Severity distribution:")
        for row in result:
            print(f"  {row['severity']}: {row['count']} issues")
            
        return common_count > 0 and severity_count > 0
        
    except Exception as e:
        print(f"❌ Views test failed: {e}")
        return False


def test_dashboard_queries():
    """Test the actual queries used by the dashboard."""
    print("🎯 Testing dashboard queries...")
    
    try:
        client = make_client()
        project_id = os.getenv('PROJECT_ID')
        dataset = os.getenv('DATASET')
        
        # Test date range (last 30 days)
        end_time = datetime.now()
        start_time = end_time - timedelta(days=30)
        
        start_ts = f"TIMESTAMP('{start_time.isoformat()}')"
        end_ts = f"TIMESTAMP('{end_time.isoformat()}')"
        
        # Test common issues query with date filter
        query = f"""
        SELECT fingerprint, issue_example, count, last_seen FROM `{project_id}.{dataset}.view_common_issues`
        WHERE last_seen BETWEEN {start_ts} AND {end_ts}
        LIMIT 5
        """
        
        result = client.run_sql_template('inline', {'raw_sql': query})
        print(f"✅ Common issues with date filter: {len(result)} rows")
        
        # Test severity query with date filter (fix DATE/TIMESTAMP mismatch)
        # The 'week' column is TIMESTAMP, so use TIMESTAMP comparisons
        query = f"""
        SELECT severity, week, count FROM `{project_id}.{dataset}.view_issues_by_severity`
        WHERE week BETWEEN DATE_TRUNC({start_ts}, WEEK) AND DATE_TRUNC({end_ts}, WEEK)
        LIMIT 5
        """
        
        result = client.run_sql_template('inline', {'raw_sql': query})
        print(f"✅ Severity trends with date filter: {len(result)} rows")
        
        # Show sample data
        if result:
            print("📋 Sample severity data:")
            for i, row in enumerate(result[:3]):
                week = row.get('week', 'N/A')
                severity = row.get('severity', 'N/A') 
                count = row.get('count', 'N/A')
                print(f"  Row {i+1}: {week} - {severity} - {count} issues")
        
        return len(result) > 0
        
    except Exception as e:
        print(f"❌ Dashboard queries failed: {e}")
        return False


def test_data_timestamps():
    """Check if sample data has appropriate timestamps."""
    print("⏰ Testing data timestamps...")
    
    try:
        client = make_client()
        project_id = os.getenv('PROJECT_ID')
        dataset = os.getenv('DATASET')
        
        # Check timestamp range in data
        result = client.run_sql_template('inline', {
            'raw_sql': f"""
            SELECT 
                MIN(COALESCE(
                    SAFE.PARSE_TIMESTAMP('%Y-%m-%dT%H:%M:%E*S%Ez', JSON_VALUE(meta, '$.ingested_at')),
                    SAFE.PARSE_TIMESTAMP('%Y-%m-%d %H:%M:%S', JSON_VALUE(meta, '$.ingested_at')),
                    CURRENT_TIMESTAMP()
                )) as min_time,
                MAX(COALESCE(
                    SAFE.PARSE_TIMESTAMP('%Y-%m-%dT%H:%M:%E*S%Ez', JSON_VALUE(meta, '$.ingested_at')),
                    SAFE.PARSE_TIMESTAMP('%Y-%m-%d %H:%M:%S', JSON_VALUE(meta, '$.ingested_at')),
                    CURRENT_TIMESTAMP()
                )) as max_time,
                COUNT(*) as total_with_timestamps
            FROM `{project_id}.{dataset}.chunks`
            WHERE JSON_VALUE(meta, '$.ingested_at') IS NOT NULL
            """
        })
        
        if result:
            row = result[0]
            min_time = row['min_time']
            max_time = row['max_time']
            total = row['total_with_timestamps']
            
            print(f"✅ Data timestamps: {total} records")
            print(f"  Range: {min_time} to {max_time}")
            
            # Check if data is recent enough for dashboard
            now = datetime.now()
            recent_cutoff = now - timedelta(days=30)
            
            if max_time and max_time.replace(tzinfo=None) > recent_cutoff:
                print("✅ Data is recent enough for dashboard default view")
                return True
            else:
                print("⚠️ Data may be too old for dashboard default view")
                return False
        
        return False
        
    except Exception as e:
        print(f"❌ Timestamp test failed: {e}")
        return False


def run_full_test():
    """Run complete end-to-end test."""
    print("🚀 Starting comprehensive pipeline test...\n")
    
    tests = [
        ("Environment", test_environment),
        ("BigQuery Connection", test_bigquery_connection),
        ("Sample Data", test_sample_data),
        ("Views", test_views),
        ("Dashboard Queries", test_dashboard_queries),
        ("Data Timestamps", test_data_timestamps),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n{'='*50}")
        try:
            if test_name == "BigQuery Connection":
                success, chunk_count = test_func()
                results[test_name] = success
                results["chunk_count"] = chunk_count
            else:
                results[test_name] = test_func()
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results[test_name] = False
    
    # Summary
    print(f"\n{'='*50}")
    print("📊 TEST SUMMARY")
    print(f"{'='*50}")
    
    passed = sum(1 for k, v in results.items() if k != "chunk_count" and v)
    total = len([k for k in results.keys() if k != "chunk_count"])
    
    for test_name, result in results.items():
        if test_name == "chunk_count":
            continue
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Dashboard should work correctly.")
        print("💡 Run: streamlit run src/dashboard/app.py")
    else:
        print(f"\n💥 {total - passed} test(s) failed. Check the errors above.")
    
    return passed == total


if __name__ == "__main__":
    success = run_full_test()
    sys.exit(0 if success else 1)
