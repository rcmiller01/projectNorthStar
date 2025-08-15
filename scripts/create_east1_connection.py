#!/usr/bin/env python3
"""Create BigQuery connection to Vertex AI in us-east1 region (non-interactive)."""

from __future__ import annotations
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from google.cloud.bigquery_connection_v1 import ConnectionServiceClient
    from google.cloud.bigquery_connection_v1 import Connection
    from google.cloud.bigquery_connection_v1 import CreateConnectionRequest
    from google.cloud.bigquery_connection_v1 import CloudResourceProperties
    from google.cloud import bigquery
    from config import load_env
except Exception as e:
    print(f"Import error: {e}")
    raise

load_env()

PROJECT = os.getenv("PROJECT_ID") or "your-project-id"
VERTEX_REGION = "us-east1"
CONNECTION_ID = "vertex-ai-east1"

def create_connection():
    """Create or get existing connection."""
    client = ConnectionServiceClient()
    parent = f"projects/{PROJECT}/locations/{VERTEX_REGION}"
    
    # Check if exists first
    try:
        existing_name = f"{parent}/connections/{CONNECTION_ID}"
        existing = client.get_connection(name=existing_name)
        print(f"✅ Using existing connection: {existing.name}")
        return existing
    except Exception:
        pass
    
    # Create new connection
    connection = Connection()
    connection.description = "Connection to Vertex AI for text models (us-east1)"
    connection.cloud_resource = CloudResourceProperties()
    
    request = CreateConnectionRequest(
        parent=parent,
        connection_id=CONNECTION_ID,
        connection=connection
    )
    
    connection = client.create_connection(request=request)
    print(f"✅ Created connection: {connection.name}")
    return connection

def test_text_model():
    """Test text model creation using us-east1 connection with US dataset."""
    bq_client = bigquery.Client()
    connection_name = f"{PROJECT}.{VERTEX_REGION}.{CONNECTION_ID}"
    test_model_id = f"`{PROJECT}.demo_ai.test_text_east1`"
    
    # Force the job to run in US region where our dataset exists
    job_config = bigquery.QueryJobConfig()
    # Note: We can't force job location, so let's try without it
    
    sql = f"""
    CREATE OR REPLACE MODEL {test_model_id}
    REMOTE WITH CONNECTION `{connection_name}`
    OPTIONS (
      ENDPOINT = 'gemini-1.5-pro'
    )
    """
    
    try:
        print("Testing text model with us-east1 connection...")
        print(f"Connection: {connection_name}")
        print(f"Job location: Auto-detected")
        job = bq_client.query(sql, job_config=job_config)
        job.result()
        print("✅ Text model created successfully!")
        
        # Test generation
        test_query = f"""
        SELECT * FROM ML.GENERATE_TEXT(
            MODEL {test_model_id},
            (SELECT 'Hello world' as prompt),
            STRUCT(30 as max_output_tokens)
        )
        """
        
        result = bq_client.query(test_query, job_config=job_config)
        for row in result:
            print(f"✅ Generated: {row.ml_generate_text_result}")
            break
        
        # Cleanup
        bq_client.query(f"DROP MODEL {test_model_id}").result()
        return True
        
    except Exception as e:
        print(f"❌ Text model failed: {e}")
        return False

def main():
    print("🔗 Creating us-east1 connection...")
    
    try:
        connection = create_connection()
        success = test_text_model()
        
        if success:
            print("\n🎉 SUCCESS! Text models work in us-east1!")
            print(f"Use: REMOTE WITH CONNECTION `{PROJECT}.{VERTEX_REGION}.{CONNECTION_ID}`")
        else:
            print("\n⚠️ Connection created but text test failed")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
