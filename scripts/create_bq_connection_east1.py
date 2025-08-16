#!/usr/bin/env python3
"""Create BigQuery connection to Vertex AI in us-east1 region for text models.

This script creates a new BigQuery external connection to Vertex AI
in the us-east1 region where text generation models should be available.
"""
from __future__ import annotations
import os
import sys
from pathlib import Path

# Add parent directory to path for config import
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
    print("Install required packages:")
    print("pip install google-cloud-bigquery-connection")
    raise

# Load environment configuration
load_env()

PROJECT = os.getenv("PROJECT_ID") or "gleaming-bus-468914-a6"
# Use us-east1 region for text models
VERTEX_REGION = "us-east1"
CONNECTION_ID = "vertex-ai-east1"


def create_vertex_ai_connection_east():
    """Create BigQuery connection to Vertex AI in us-east1."""
    print("Creating BigQuery connection to Vertex AI in us-east1...")
    print(f"Project: {PROJECT}")
    print(f"Region: {VERTEX_REGION}")
    print(f"Connection ID: {CONNECTION_ID}")
    
    # Initialize the connection client
    client = ConnectionServiceClient()
    
    # Create the connection request
    parent = f"projects/{PROJECT}/locations/{VERTEX_REGION}"
    
    connection = Connection()
    connection.description = "Connection to Vertex AI for text generation models (us-east1)"
    connection.cloud_resource = CloudResourceProperties()
    
    request = CreateConnectionRequest(
        parent=parent,
        connection_id=CONNECTION_ID,
        connection=connection
    )
    
    try:
        # Check if connection already exists
        existing_name = f"{parent}/connections/{CONNECTION_ID}"
        try:
            existing = client.get_connection(name=existing_name)
            print(f"✅ Connection already exists: {existing.name}")
            print(f"   Service Account: {existing.cloud_resource.service_account_id}")
            return existing
        except Exception:
            # Connection doesn't exist, create it
            pass
        
        # Create new connection
        print("Creating new connection...")
        connection = client.create_connection(request=request)
        print(f"✅ Connection created: {connection.name}")
        print(f"   Service Account: {connection.cloud_resource.service_account_id}")
        
        print("\n⚠️  IMPORTANT: Grant Vertex AI User role to this service account:")
        print(f"   gcloud projects add-iam-policy-binding {PROJECT} \\")
        print(f"     --member='serviceAccount:{connection.cloud_resource.service_account_id}' \\")
        print(f"     --role='roles/aiplatform.user'")
        
        return connection
        
    except Exception as e:
        print(f"❌ Failed to create connection: {e}")
        raise


def test_text_model():
    """Test creating a text generation model in us-east1."""
    print("\n🧪 Testing text model creation in us-east1...")
    
    # Initialize BigQuery client
    bq_client = bigquery.Client()
    
    connection_name = f"{PROJECT}.{VERTEX_REGION}.{CONNECTION_ID}"
    test_model_id = f"`{PROJECT}.demo_ai.test_text_model_east1`"
    
    # Try gemini-1.5-pro in us-east1
    sql = f"""
    CREATE OR REPLACE MODEL {test_model_id}
    REMOTE WITH CONNECTION `{connection_name}`
    OPTIONS (
      ENDPOINT = 'gemini-1.5-pro'
    )
    """
    
    print(f"Creating test text model: {test_model_id}")
    print(f"Using connection: {connection_name}")
    print(f"Endpoint: gemini-1.5-pro")
    
    try:
        job = bq_client.query(sql)
        job.result()
        print("✅ Text model created successfully in us-east1!")
        
        # Test text generation
        test_query = f"""
        SELECT * FROM ML.GENERATE_TEXT(
            MODEL {test_model_id},
            (SELECT 'Say hello in a friendly way' as prompt),
            STRUCT(50 as max_output_tokens, 0.8 as temperature)
        )
        """
        
        print("Testing text generation...")
        result = bq_client.query(test_query)
        for row in result:
            generated_text = row.ml_generate_text_result
            print(f"✅ Generated text: {generated_text}")
            break
        
        # Clean up test model
        cleanup_sql = f"DROP MODEL IF EXISTS {test_model_id}"
        bq_client.query(cleanup_sql).result()
        print("🧹 Cleaned up test model")
        
        return True
        
    except Exception as e:
        print(f"❌ Text model creation failed: {e}")
        return False


def main():
    """Main function to create us-east1 connection and test text models."""
    print("🔗 BigQuery → Vertex AI Connection Setup (us-east1)")
    print("="*60)
    
    try:
        # Create the connection
        connection = create_vertex_ai_connection_east()
        
        print("\n" + "⚠️" * 20)
        print("IMPORTANT: You need to grant permissions to the service account!")
        print("Run this command in Google Cloud Shell or gcloud CLI:")
        print(f"gcloud projects add-iam-policy-binding {PROJECT} \\")
        print(f"  --member='serviceAccount:{connection.cloud_resource.service_account_id}' \\")
        print(f"  --role='roles/aiplatform.user'")
        print("⚠️" * 20)
        
        input("\nPress Enter after granting permissions to continue with testing...")
        
        # Test the connection
        success = test_text_model()
        
        if success:
            print("\n🎉 SUCCESS! Text generation models work in us-east1!")
            print(f"Connection name: {connection.name}")
            print("\nYou can now create text models using:")
            print(f"REMOTE WITH CONNECTION `{PROJECT}.{VERTEX_REGION}.{CONNECTION_ID}`")
        else:
            print("\n❌ Connection created but text model test failed.")
            print("Check permissions and model availability.")
            
    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
