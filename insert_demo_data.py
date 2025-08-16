#!/usr/bin/env python3
"""Simple BigQuery direct insertion for dashboard demo."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from bq.bigquery_client import make_client
from config import load_env
from datetime import datetime, timedelta
import random
import json
import uuid

# Sample incidents with proper severity
SAMPLE_INCIDENTS = [
    {"content": "Authentication service down - 100% error rate", "severity": "P0"},
    {"content": "Database primary failover triggered automatically", "severity": "P0"},
    {"content": "Payment processing API returning 500 errors", "severity": "P1"},
    {"content": "SSL certificate expiring in 2 days", "severity": "P1"},
    {"content": "Memory usage high on web servers (85%)", "severity": "P2"},
    {"content": "Slow query detected in user dashboard", "severity": "P2"},
    {"content": "Log rotation not working on staging server", "severity": "P3"},
    {"content": "Minor UI alignment issue in mobile view", "severity": "P3"},
    {"content": "API rate limiting triggered for user uploads", "severity": "P1"},
    {"content": "Cache miss rate increased to 40%", "severity": "P2"},
    {"content": "Backup job completed with warnings", "severity": "P3"},
    {"content": "Load balancer health check failing intermittently", "severity": "P1"},
    {"content": "Disk space low on analytics server (92% full)", "severity": "P0"},
    {"content": "User reported timeout during large file upload", "severity": "P2"},
    {"content": "Email notification service delayed by 5 minutes", "severity": "P3"},
]

def insert_sample_data():
    """Insert sample data directly via BigQuery SQL."""
    
    load_env()
    client = make_client()
    
    print("🚀 Inserting sample incidents directly into BigQuery...")
    
    # Generate data for the last 30 days
    base_date = datetime.now() - timedelta(days=30)
    
    values_list = []
    for i, incident in enumerate(SAMPLE_INCIDENTS * 3):  # Replicate for more data
        # Random date in the last 30 days
        random_days = random.randint(0, 30)
        random_hours = random.randint(0, 23)
        incident_date = base_date + timedelta(days=random_days, hours=random_hours)
        
        # Create chunk data
        chunk_id = f"demo_chunk_{i:03d}"
        doc_id = f"demo_doc_{i // 5:02d}"  # Group chunks into docs
        content = incident["content"]
        
        # Create meta JSON string (note: BigQuery expects JSON as string)
        meta_obj = {
            "severity": incident["severity"],
            "ingested_at": incident_date.isoformat() + "Z",
            "source": "demo_data",
            "category": "incident"
        }
        meta_json = json.dumps(meta_obj).replace("'", "\\'")  # Escape quotes
        
        # Add fake embedding (768 dimensions of 0.1)
        embedding_str = "[" + ",".join(["0.1"] * 768) + "]"
        
        values_list.append(f"""(
            '{chunk_id}',
            '{doc_id}', 
            '{content}',
            PARSE_JSON('{meta_json}'),
            {embedding_str}
        )""")
    
    # Build INSERT statement
    values_clause = ",\n    ".join(values_list)
    sql = f"""
    INSERT INTO `gleaming-bus-468914-a6.demo_ai.chunks` 
    (chunk_id, doc_id, content, meta, embedding)
    VALUES
    {values_clause}
    """
    
    try:
        result = client.run_sql_template('inline', {'raw_sql': sql})
        print(f"✅ Inserted {len(values_list)} sample incidents")
        
        # Check total count
        count_result = client.run_sql_template('inline', {
            'raw_sql': "SELECT COUNT(*) as total FROM `gleaming-bus-468914-a6.demo_ai.chunks`"
        })
        total = count_result[0]['total'] if count_result else 0
        print(f"📊 Total chunks in table: {total}")
        
        # Check severity distribution
        severity_result = client.run_sql_template('inline', {
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
        for row in severity_result:
            print(f"  {row['severity']}: {row['count']} incidents")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = insert_sample_data()
    if success:
        print("\n🎉 Sample data inserted successfully!")
        print("💡 Now restart the dashboard to see the data visualization")
    else:
        print("\n💥 Failed to insert sample data")
