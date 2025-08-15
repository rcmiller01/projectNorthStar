#!/usr/bin/env python3
"""Simple test for text generation models."""

from config import load_env
from google.cloud import bigquery

load_env()
client = bigquery.Client()

# Test text-bison
print("Trying text-bison...")
try:
    query = """
    CREATE OR REPLACE MODEL `gleaming-bus-468914-a6.demo_ai.text_model`
    REMOTE WITH CONNECTION `gleaming-bus-468914-a6.us.vertex-ai`
    OPTIONS (
      ENDPOINT = 'text-bison'
    )
    """
    result = client.query(query)
    result.result()
    print("✅ text-bison model created!")
except Exception as e:
    print(f"❌ text-bison failed: {e}")

# Test gemini-pro  
print("\nTrying gemini-pro...")
try:
    query = """
    CREATE OR REPLACE MODEL `gleaming-bus-468914-a6.demo_ai.text_model2`
    REMOTE WITH CONNECTION `gleaming-bus-468914-a6.us.vertex-ai`
    OPTIONS (
      ENDPOINT = 'gemini-pro'
    )
    """
    result = client.query(query)
    result.result()
    print("✅ gemini-pro model created!")
except Exception as e:
    print(f"❌ gemini-pro failed: {e}")
