#!/usr/bin/env python3
"""Test JSON access methods."""

from config import load_env
from google.cloud import bigquery

load_env()
client = bigquery.Client()

# Test different ways to access JSON fields
test_queries = [
    "SELECT JSON_VALUE(meta, '$.severity') as severity FROM `gleaming-bus-468914-a6.demo_ai.chunks` LIMIT 1",
    "SELECT meta.severity as severity FROM `gleaming-bus-468914-a6.demo_ai.chunks` LIMIT 1",
    "SELECT TO_JSON_STRING(meta) as meta_string FROM `gleaming-bus-468914-a6.demo_ai.chunks` LIMIT 1"
]

for i, query in enumerate(test_queries):
    print(f"Test {i+1}: {query}")
    try:
        result = list(client.query(query).result())
        if hasattr(result[0], 'severity'):
            print(f"  Result: {result[0].severity}")
        elif hasattr(result[0], 'meta_string'):
            print(f"  Result: {result[0].meta_string}")
        else:
            print(f"  Result: {result[0]}")
    except Exception as e:
        print(f"  Error: {e}")
    print()
