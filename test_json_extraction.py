#!/usr/bin/env python3
"""Test JSON extraction directly."""

from config import load_env
from google.cloud import bigquery

load_env()
client = bigquery.Client()

# Test different JSON extraction methods
queries = [
    "SELECT JSON_EXTRACT_SCALAR(meta, '$.severity') as severity FROM `gleaming-bus-468914-a6.demo_ai.chunks` LIMIT 1",
    "SELECT JSON_VALUE(meta, '$.severity') as severity FROM `gleaming-bus-468914-a6.demo_ai.chunks` LIMIT 1", 
    "SELECT meta.severity as severity FROM `gleaming-bus-468914-a6.demo_ai.chunks` LIMIT 1"
]

for i, query in enumerate(queries):
    try:
        print(f"Method {i+1}:")
        result = list(client.query(query).result())
        print(f"  Result: {result[0].severity}")
    except Exception as e:
        print(f"  Error: {e}")
    print()
