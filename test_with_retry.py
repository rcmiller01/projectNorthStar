#!/usr/bin/env python3
"""Test text models with retry logic for IAM propagation delays."""

import time
from config import load_env
from google.cloud import bigquery

load_env()

def test_text_generation_with_retry(max_retries=3, delay_seconds=30):
    """Test text generation with retry logic for IAM delays."""
    client = bigquery.Client()
    project_id = "gleaming-bus-468914-a6"
    
    sql = f"""
    CREATE OR REPLACE MODEL `{project_id}.demo_ai_east1.text_model`
    REMOTE WITH CONNECTION `{project_id}.us-east1.vertex-ai-east1`
    OPTIONS (
      ENDPOINT = 'gemini-1.5-pro'
    )
    """
    
    for attempt in range(max_retries):
        try:
            print(f"🔄 Attempt {attempt + 1}/{max_retries}: Creating text model...")
            job = client.query(sql)
            job.result()
            print("✅ Text model created successfully!")
            
            # Test generation
            test_sql = f"""
            SELECT * FROM ML.GENERATE_TEXT(
                MODEL `{project_id}.demo_ai_east1.text_model`,
                (SELECT 'Write a short hello message' as prompt),
                STRUCT(50 as max_output_tokens, 0.8 as temperature)
            )
            """
            
            print("Testing text generation...")
            result = client.query(test_sql)
            for row in result:
                generated = row.ml_generate_text_result
                print(f"✅ Generated text: {generated}")
                break
            
            print("\n🎉 SUCCESS! Text generation is working!")
            return True
            
        except Exception as e:
            error_msg = str(e)
            print(f"❌ Attempt {attempt + 1} failed: {error_msg[:100]}...")
            
            if "permission" in error_msg.lower() and attempt < max_retries - 1:
                print(f"⏳ IAM may still be propagating. Waiting {delay_seconds} seconds...")
                time.sleep(delay_seconds)
            elif "not found" in error_msg.lower() and "model" in error_msg.lower():
                print("🔍 Trying alternative model endpoints...")
                # Try different models
                alternatives = ['gemini-pro', 'text-bison', 'gemini-1.0-pro']
                for alt_model in alternatives:
                    if test_alternative_model(client, project_id, alt_model):
                        return True
                break
            else:
                if attempt == max_retries - 1:
                    print(f"\n❌ All attempts failed. Final error: {error_msg}")
                break
    
    return False

def test_alternative_model(client, project_id, model_endpoint):
    """Test alternative model endpoints."""
    try:
        print(f"🔄 Trying alternative model: {model_endpoint}")
        sql = f"""
        CREATE OR REPLACE MODEL `{project_id}.demo_ai_east1.text_model_alt`
        REMOTE WITH CONNECTION `{project_id}.us-east1.vertex-ai-east1`
        OPTIONS (
          ENDPOINT = '{model_endpoint}'
        )
        """
        
        job = client.query(sql)
        job.result()
        print(f"✅ Alternative model {model_endpoint} created!")
        
        # Test generation
        test_sql = f"""
        SELECT * FROM ML.GENERATE_TEXT(
            MODEL `{project_id}.demo_ai_east1.text_model_alt`,
            (SELECT 'Hello' as prompt),
            STRUCT(30 as max_output_tokens)
        )
        """
        
        result = client.query(test_sql)
        for row in result:
            generated = row.ml_generate_text_result
            print(f"✅ {model_endpoint} generated: {generated}")
            break
        
        return True
        
    except Exception as e:
        print(f"❌ {model_endpoint} failed: {str(e)[:80]}...")
        return False

def main():
    print("🧪 Testing Text Generation in us-east1")
    print("=" * 50)
    print("Service Account: bqcx-111337406730-4igi@gcp-sa-bigquery-condel.iam.gserviceaccount.com")
    print("Expected Role: Vertex AI User")
    print("Region: us-east1")
    print()
    
    success = test_text_generation_with_retry()
    
    if success:
        print("\n🎉 FINAL SUCCESS!")
        print("✅ Text generation models are now working in us-east1!")
        print("✅ You now have both:")
        print("   • Embeddings in US region (demo_ai dataset)")
        print("   • Text generation in us-east1 region (demo_ai_east1 dataset)")
    else:
        print("\n❌ Text generation setup incomplete")
        print("💡 You still have working embeddings in the US region")
        print("💡 Consider using embedding-only features for now")

if __name__ == "__main__":
    main()
