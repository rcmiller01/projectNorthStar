"""Create BigQuery connection to Vertex AI programmatically.

This script creates the required BigQuery external connection to Vertex AI
that allows creating remote ML models.
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
LOCATION = os.getenv("LOCATION") or "US"
CONNECTION_ID = "vertex-ai"


def create_vertex_ai_connection():
    """Create BigQuery connection to Vertex AI."""
    print("Creating BigQuery connection to Vertex AI...")
    print(f"Project: {PROJECT}")
    print(f"Location: {LOCATION}")
    print(f"Connection ID: {CONNECTION_ID}")
    
    # Initialize the connection client
    client = ConnectionServiceClient()
    
    # Create the connection request
    parent = f"projects/{PROJECT}/locations/{LOCATION.lower()}"
    
    connection = Connection()
    connection.description = "Connection to Vertex AI for remote ML models"
    connection.cloud_resource = CloudResourceProperties()
    
    request = CreateConnectionRequest(
        parent=parent,
        connection_id=CONNECTION_ID,
        connection=connection,
    )
    
    try:
        # Check if connection already exists
        existing_connection_name = f"{parent}/connections/{CONNECTION_ID}"
        try:
            existing = client.get_connection(name=existing_connection_name)
            print(f"✅ Connection already exists: {existing.name}")
            print(f"   Description: {existing.description}")
            return existing
        except Exception:
            # Connection doesn't exist, create it
            pass
        
        # Create the connection
        connection = client.create_connection(request=request)
        print(f"✅ Created connection: {connection.name}")
        print(f"   Description: {connection.description}")
        if hasattr(connection, 'cloud_resource') and connection.cloud_resource:
            if hasattr(connection.cloud_resource, 'service_account_id'):
                service_account = connection.cloud_resource.service_account_id
                print(f"   Service account: {service_account}")
        
        return connection
        
    except Exception as e:
        print(f"❌ Failed to create connection: {e}")
        raise


def test_connection():
    """Test the connection by creating a simple remote model."""
    print("\n" + "="*60)
    print("Testing the connection with a simple remote model...")
    
    bq_client = bigquery.Client(project=PROJECT, location=LOCATION)
    
    test_model_id = f"`{PROJECT}`.`demo_ai`.test_vertex_model"
    connection_name = f"{PROJECT}.{LOCATION.lower()}.{CONNECTION_ID}"
    
    sql = f"""
    CREATE OR REPLACE MODEL {test_model_id}
    REMOTE WITH CONNECTION `{connection_name}`
    OPTIONS (
      REMOTE_SERVICE_TYPE = 'TEXT_EMBEDDING',
      ENDPOINT = 'text-embedding-004'
    );
    """
    
    print(f"Creating test model: {test_model_id}")
    print(f"Using connection: {connection_name}")
    print(f"SQL: {sql}")
    
    try:
        job = bq_client.query(sql)
        job.result()
        print("✅ Test model created successfully!")
        print("🎉 BigQuery ↔ Vertex AI connection is working!")
        
        # Clean up test model
        cleanup_sql = f"DROP MODEL IF EXISTS {test_model_id}"
        bq_client.query(cleanup_sql).result()
        print("🧹 Cleaned up test model")
        
        return True
        
    except Exception as e:
        print(f"❌ Test model creation failed: {e}")
        return False


def main():
    """Main function to create connection and test it."""
    print("🔗 BigQuery → Vertex AI Connection Setup")
    print("="*60)
    
    try:
        # Create the connection
        connection = create_vertex_ai_connection()
        
        # Test the connection
        success = test_connection()
        
        if success:
            print("\n" + "🎉 SUCCESS! BigQuery → Vertex AI connection is ready!")
            print(f"Connection name: {connection.name}")
            print("\nYou can now run: python scripts/create_remote_models.py")
        else:
            print("\n❌ Connection created but test failed. Check permissions.")
            
    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
