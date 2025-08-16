#!/usr/bin/env python3
"""Test which text models are available in us-east1."""

from config import load_env
from google.cloud import bigquery

load_env()

def test_models_in_east1():
    """Test different model endpoints in us-east1."""
    client = bigquery.Client()
    project_id = "gleaming-bus-468914-a6"
    
    # Models to test in us-east1
    models_to_test = [
        # Gemini models
        'gemini-pro',
        'gemini-1.0-pro', 
        'gemini-1.5-flash',
        'gemini-1.5-pro',
        
        # Bison models
        'text-bison',
        'text-bison@001',
        'text-bison@002',
        'chat-bison',
        'chat-bison@001',
        'chat-bison@002',
        
        # Other models
        'text-unicorn@001',
        'codechat-bison@001',
        'code-bison@001',
    ]
    
    working_models = []
    
    for model_name in models_to_test:
        try:
            print(f"Testing {model_name}...")
            
            sql = f"""
            CREATE OR REPLACE MODEL `{project_id}.demo_ai_east1.test_model`
            REMOTE WITH CONNECTION `{project_id}.us-east1.vertex-ai-east1`
            OPTIONS (
              ENDPOINT = '{model_name}'
            )
            """
            
            job = client.query(sql)
            job.result()
            
            print(f"✅ {model_name}: MODEL CREATED!")
            
            # Test text generation
            test_sql = f"""
            SELECT * FROM ML.GENERATE_TEXT(
                MODEL `{project_id}.demo_ai_east1.test_model`,
                (SELECT 'Hello' as prompt),
                STRUCT(20 as max_output_tokens)
            )
            """
            
            result = client.query(test_sql)
            for row in result:
                generated = row.ml_generate_text_result
                print(f"✅ {model_name}: GENERATION WORKS! '{generated}'")
                working_models.append(model_name)
                break
            
            # Clean up
            client.query(f"DROP MODEL `{project_id}.demo_ai_east1.test_model`").result()
            
        except Exception as e:
            error_msg = str(e)
            if "not found" in error_msg.lower():
                print(f"❌ {model_name}: Not available in us-east1")
            elif "unsupported" in error_msg.lower():
                print(f"❌ {model_name}: Unsupported for remote models")
            else:
                print(f"❌ {model_name}: {error_msg[:60]}...")
    
    return working_models

def main():
    print("🔍 Testing Text Models Available in us-east1")
    print("=" * 50)
    
    working_models = test_models_in_east1()
    
    print("\n" + "=" * 50)
    if working_models:
        print(f"🎉 Found {len(working_models)} working text models!")
        for model in working_models:
            print(f"✅ {model}")
        
        print(f"\n🚀 You can now use any of these models with:")
        print(f"   Connection: gleaming-bus-468914-a6.us-east1.vertex-ai-east1")
        print(f"   Dataset: gleaming-bus-468914-a6.demo_ai_east1")
        
    else:
        print("❌ No working text models found in us-east1")
        print("💡 Consider trying a different region or using embeddings only")

if __name__ == "__main__":
    main()
