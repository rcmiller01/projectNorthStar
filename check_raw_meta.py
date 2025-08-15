#!/usr/bin/env python3
"""Check raw meta value."""

from config import load_env
from google.cloud import bigquery

load_env()
client = bigquery.Client()

result = list(client.query("SELECT meta FROM `gleaming-bus-468914-a6.demo_ai.chunks` LIMIT 1").result())
meta_value = result[0].meta
print("Raw meta:", repr(meta_value))
print("Type:", type(meta_value))

# If it's JSON type in BigQuery, we might need to handle it differently
print("Direct access attempt:")
try:
    query = "SELECT meta FROM `gleaming-bus-468914-a6.demo_ai.chunks` LIMIT 1"
    for row in client.query(query).result():
        print("Row meta:", row.meta)
        if hasattr(row.meta, 'severity'):
            print("Has severity attr:", row.meta.severity)
        else:
            print("No severity attr")
except Exception as e:
    print("Error:", e)
