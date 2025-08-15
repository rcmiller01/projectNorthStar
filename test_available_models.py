#!/usr/bin/env python3
"""Test different model endpoints to find what's available."""

from config import load_env
from google.cloud import bigquery

load_env()
client = bigquery.Client()

# Test different model endpoints
models_to_try = [
    'gemini-pro',
    'gemini-1.0-pro',
    'text-bison',
    'text-bison@001',
    'chat-bison',
    'chat-bison@001',
    'gemini-1.5-pro-001',
    'gemini-1.5-flash-001'
]

for model in models_to_try:
    try:
        query = f"""
        CREATE OR REPLACE MODEL `gleaming-bus-468914-a6.demo_ai.test_model`
        REMOTE WITH CONNECTION `gleaming-bus-468914-a6.us.vertex-ai`
        OPTIONS (
          ENDPOINT = '{model}'
        )
        """
        print(f'Trying {model}...')
        result = client.query(query)
        result.result()
        print(f'✅ SUCCESS: {model} works!')
        
        # Clean up the test model
        client.query("DROP MODEL `gleaming-bus-468914-a6.demo_ai.test_model`").result()
        break
        
    except Exception as e:
        error_msg = str(e)
        if "not found" in error_msg.lower():
            print(f'❌ {model}: Not found')
        else:
            print(f'❌ {model}: {error_msg[:100]}...')
