#!/usr/bin/env python3
"""Test embedding generation."""

from config import load_env
from google.cloud import bigquery

load_env()
client = bigquery.Client()

# Test embedding generation
try:
    query = """
    SELECT * FROM ML.GENERATE_EMBEDDING(
        MODEL `gleaming-bus-468914-a6.demo_ai.embed_model`,
        (SELECT 'test text' as content)
    )
    """
    print('Testing embedding generation...')
    result = client.query(query)
    for row in result:
        embeddings = row.ml_generate_embedding_result
        print(f'✅ Embedding generated! Length: {len(embeddings)}')
        print(f'First few values: {embeddings[:5]}')
        break
except Exception as e:
    print(f'❌ Embedding test failed: {e}')

# Also try to show the models in our dataset
try:
    query = """
    SELECT 
        table_name as model_name,
        table_type
    FROM `gleaming-bus-468914-a6.demo_ai.INFORMATION_SCHEMA.TABLES`
    WHERE table_type = 'MODEL'
    """
    print('\nListing models in dataset...')
    result = client.query(query)
    for row in result:
        print(f'Found model: {row.model_name} (type: {row.table_type})')
except Exception as e:
    print(f'❌ Error listing models: {e}')
