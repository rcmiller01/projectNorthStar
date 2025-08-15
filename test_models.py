#!/usr/bin/env python3
"""Test if our models work."""

from config import load_env
from google.cloud import bigquery
import os

load_env()

client = bigquery.Client()

# Test embedding model
try:
    query = """
    SELECT * FROM ML.PREDICT(
        MODEL `gleaming-bus-468914-a6.demo_ai.embed_model`,
        (SELECT 'test text' as content)
    )
    """
    print('Testing embedding model...')
    result = client.query(query)
    for row in result:
        print('✅ Embedding model works!')
        break
except Exception as e:
    print(f'❌ Embedding model failed: {e}')

# Try to create text model with a different endpoint
try:
    query = """
    CREATE OR REPLACE MODEL `gleaming-bus-468914-a6.demo_ai.text_model`
    REMOTE WITH CONNECTION `gleaming-bus-468914-a6.us.vertex-ai`
    OPTIONS (
      ENDPOINT = 'gemini-1.5-flash'
    )
    """
    print('Trying to create text model with gemini-1.5-flash...')
    result = client.query(query)
    result.result()
    print('✅ Text model created with gemini-1.5-flash!')
except Exception as e:
    print(f'❌ Text model creation failed: {e}')
