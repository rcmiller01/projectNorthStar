#!/usr/bin/env python3
"""Test text models with us-east1 connection directly."""

from config import load_env
from google.cloud import bigquery

load_env()

client = bigquery.Client()

# Try creating text model using us-east1 connection
print("Testing text model creation with us-east1 connection...")

sql = """
CREATE OR REPLACE MODEL `gleaming-bus-468914-a6.demo_ai.text_model`
REMOTE WITH CONNECTION `gleaming-bus-468914-a6.us-east1.vertex-ai-east1`
OPTIONS (
  ENDPOINT = 'gemini-1.5-pro'
)
"""

try:
    print("Creating text model...")
    job = client.query(sql)
    job.result()
    print("✅ Text model created successfully!")
    
    # Test generation
    test_sql = """
    SELECT * FROM ML.GENERATE_TEXT(
        MODEL `gleaming-bus-468914-a6.demo_ai.text_model`,
        (SELECT 'Say hello in a friendly way' as prompt),
        STRUCT(50 as max_output_tokens, 0.8 as temperature)
    )
    """
    
    print("Testing text generation...")
    result = client.query(test_sql)
    for row in result:
        print(f"✅ Generated text: {row.ml_generate_text_result}")
        break
    
    print("\n🎉 SUCCESS! Text generation is now working!")
    
except Exception as e:
    print(f"❌ Failed: {e}")
    
    if "not found" in str(e).lower() and "location" in str(e).lower():
        print("\n💡 This appears to be a cross-region limitation.")
        print("Solutions:")
        print("1. Create dataset in us-east1")
        print("2. Use different connection region") 
        print("3. Use only embeddings (which work fine)")
