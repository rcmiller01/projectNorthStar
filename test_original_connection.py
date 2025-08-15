#!/usr/bin/env python3
"""Test text models in us-central1 with corrected permissions."""

from config import load_env
from google.cloud import bigquery
from google.cloud.bigquery_connection_v1 import ConnectionServiceClient

load_env()

def check_connection_permissions():
    """Check what service account is used by us connection."""
    client = ConnectionServiceClient()
    
    # Check us-central1 - this is where models were being looked up originally
    try:
        connection_name = "projects/111337406730/locations/us-central1/connections/vertex-ai-central"
        connection = client.get_connection(name=connection_name)
        print(f"✅ us-central1 connection exists: {connection.name}")
        print(f"   Service Account: {connection.cloud_resource.service_account_id}")
        return connection.cloud_resource.service_account_id
    except Exception as e:
        print(f"❌ us-central1 connection check failed: {e}")
        return None

def test_original_connection():
    """Test with the original US connection but try to force us-central1 models."""
    bq_client = bigquery.Client()
    project_id = "gleaming-bus-468914-a6"
    
    # Use the original US connection - this had working permissions
    connection_name = f"{project_id}.us.vertex-ai"
    
    print(f"Testing with original connection: {connection_name}")
    
    # Try creating model in our US dataset
    sql = f"""
    CREATE OR REPLACE MODEL `{project_id}.demo_ai.text_model_test`
    REMOTE WITH CONNECTION `{connection_name}`
    OPTIONS (
      ENDPOINT = 'text-bison'
    )
    """
    
    try:
        print("Testing text-bison with original US connection...")
        job = bq_client.query(sql)
        job.result()
        print("✅ Model created with US connection!")
        
        # Test generation
        test_sql = f"""
        SELECT * FROM ML.GENERATE_TEXT(
            MODEL `{project_id}.demo_ai.text_model_test`,
            (SELECT 'Hello world' as prompt),
            STRUCT(30 as max_output_tokens)
        )
        """
        
        result = bq_client.query(test_sql)
        for row in result:
            generated = row.ml_generate_text_result
            print(f"✅ Generated with US connection: {generated}")
            break
        
        return True
        
    except Exception as e:
        print(f"❌ US connection test failed: {e}")
        return False

def main():
    print("🔍 Testing Text Models with Original US Connection")
    print("=" * 60)
    
    # First check permissions on existing connections
    sa = check_connection_permissions()
    
    # Test with original US connection
    success = test_original_connection()
    
    if success:
        print("\n🎉 SUCCESS! Text generation works with original US connection!")
        print("✅ Use: gleaming-bus-468914-a6.us.vertex-ai")
        print("✅ In dataset: gleaming-bus-468914-a6.demo_ai")
    else:
        print("\n❌ Text generation still not working")
        print("💡 This may be a fundamental regional limitation")
        print("💡 Your embedding models work perfectly for most AI tasks")

if __name__ == "__main__":
    main()
