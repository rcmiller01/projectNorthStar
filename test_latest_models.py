#!/usr/bin/env python3
"""Try latest model naming conventions."""

from config import load_env
from google.cloud import bigquery

load_env()
client = bigquery.Client()

# Try latest model names from current Google Cloud docs
latest_models = [
    'text-bison@002',
    'text-bison-32k',
    'gemini-1.0-pro',
    'gemini-1.5-pro-002',
    'gemini-1.5-flash-002', 
    'text-bison-001',
    'chat-bison@002',
    'claude-3-sonnet@20240229',  # Anthropic models
    'claude-3-haiku@20240307',
]

for model in latest_models:
    try:
        print(f"Trying {model}...")
        query = f"""
        CREATE OR REPLACE MODEL `gleaming-bus-468914-a6.demo_ai.test_gen_model`
        REMOTE WITH CONNECTION `gleaming-bus-468914-a6.us.vertex-ai`
        OPTIONS (
          ENDPOINT = '{model}'
        )
        """
        result = client.query(query)
        result.result()
        print(f"✅ SUCCESS: {model} works!")
        
        # Update our main script to use this model
        print(f"✅ Found working text generation model: {model}")
        break
        
    except Exception as e:
        error_msg = str(e)
        if "not found" in error_msg.lower() or "was not found" in error_msg.lower():
            print(f"❌ {model}: Not found")
        elif "unsupported" in error_msg.lower():
            print(f"❌ {model}: Unsupported for remote models")
        elif "retired" in error_msg.lower():
            print(f"❌ {model}: Retired/deprecated")
        else:
            print(f"❌ {model}: {error_msg[:80]}...")
else:
    print("\n❌ No working text generation models found.")
    print("This might be due to:")
    print("1. Region limitations (models not available in us-central1)")
    print("2. Project permissions/quotas")
    print("3. Model naming changes")
    print("\nYour embedding model works, so consider:")
    print("- Using only embeddings for now")
    print("- Trying a different region for the connection")
    print("- Checking Google Cloud console for available models")
