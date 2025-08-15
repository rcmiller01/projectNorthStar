#!/usr/bin/env python3
"""Test with more model endpoints."""

from config import load_env
from google.cloud import bigquery

load_env()
client = bigquery.Client()

# Try the most basic models that should definitely work
models_to_try = [
    'textembedding-gecko@003',
    'textembedding-gecko@001',
    'text-embedding-004',
    'text-embedding-preview-0409'
]

for model in models_to_try:
    try:
        query = f"""
        CREATE OR REPLACE MODEL `gleaming-bus-468914-a6.demo_ai.test_text_model`
        REMOTE WITH CONNECTION `gleaming-bus-468914-a6.us.vertex-ai`
        OPTIONS (
          ENDPOINT = '{model}'
        )
        """
        print(f'Trying text model {model}...')
        result = client.query(query)
        result.result()
        print(f'✅ SUCCESS: {model} works for text generation!')
        
        # Test if we can use it
        test_query = """
        SELECT * FROM ML.GENERATE_TEXT(
            MODEL `gleaming-bus-468914-a6.demo_ai.test_text_model`,
            (SELECT 'Write a short hello message' as prompt)
        )
        """
        test_result = client.query(test_query)
        for row in test_result:
            print(f'✅ Model generates text: {str(row)[:100]}...')
            break
        
        # Clean up
        client.query("DROP MODEL `gleaming-bus-468914-a6.demo_ai.test_text_model`").result()
        break
        
    except Exception as e:
        error_msg = str(e)
        if "not found" in error_msg.lower():
            print(f'❌ {model}: Not found')
        else:
            print(f'❌ {model}: {error_msg[:150]}...')
