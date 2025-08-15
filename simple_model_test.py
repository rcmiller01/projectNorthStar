#!/usr/bin/env python3
"""Simple test for text generation models."""

import os
from config import load_env
from google.cloud import bigquery

load_env()
client = bigquery.Client()

project_id = os.getenv("PROJECT_ID", "your-project-id")
dataset = os.getenv("DATASET", "demo_ai")
location = os.getenv("LOCATION", "US")

# Test text-bison
print("Trying text-bison...")
try:
    query = f"""
    CREATE OR REPLACE MODEL `{project_id}.{dataset}.text_model`
    REMOTE WITH CONNECTION `{project_id}.{location.lower()}.vertex-ai`
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
    query = f"""
    CREATE OR REPLACE MODEL `{project_id}.{dataset}.text_model2`
    REMOTE WITH CONNECTION `{project_id}.{location.lower()}.vertex-ai`
    OPTIONS (
      ENDPOINT = 'gemini-pro'
    )
    """
    result = client.query(query)
    result.result()
    print("✅ gemini-pro model created!")
except Exception as e:
    print(f"❌ gemini-pro failed: {e}")
