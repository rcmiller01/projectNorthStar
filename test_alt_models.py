#!/usr/bin/env python3
"""Try alternative text generation model names."""

from config import load_env
from google.cloud import bigquery

load_env()
client = bigquery.Client()

# Try alternative model names that might be available
alternative_models = [
    'textembedding-gecko',  # This might work for text generation too
    'text-unicorn',
    'code-bison',
    'codechat-bison', 
    'chat-bison-32k',
    'gemini-1.0-pro-vision',
    'gemini-1.0-pro-002',
    'gemini-1.5-pro-preview-0409',
    'publishers/google/models/text-bison',  # Try full path
    'publishers/google/models/gemini-pro',  # Try full path
]

for model in alternative_models:
    try:
        print(f"Trying {model}...")
        query = f"""
        CREATE OR REPLACE MODEL `gleaming-bus-468914-a6.demo_ai.test_text_model`
        REMOTE WITH CONNECTION `gleaming-bus-468914-a6.us.vertex-ai`
        OPTIONS (
          ENDPOINT = '{model}'
        )
        """
        result = client.query(query)
        result.result()
        print(f"✅ SUCCESS: {model} works!")
        
        # Try to generate text to confirm it works
        test_query = """
        SELECT * FROM ML.GENERATE_TEXT(
            MODEL `gleaming-bus-468914-a6.demo_ai.test_text_model`,
            (SELECT 'Say hello' as prompt),
            STRUCT(100 as max_output_tokens, 0.8 as temperature)
        )
        """
        test_result = client.query(test_query)
        for row in test_result:
            generated_text = row.ml_generate_text_result
            print(f"✅ Generated text: {generated_text}")
            break
            
        # Clean up and keep this model
        print(f"✅ Keeping working model: {model}")
        break
        
    except Exception as e:
        error_msg = str(e)
        if "not found" in error_msg.lower() or "was not found" in error_msg.lower():
            print(f"❌ {model}: Not found")
        else:
            print(f"❌ {model}: {error_msg[:100]}...")
            
print("\nIf no models worked, you may need to enable additional APIs or use different regions.")
