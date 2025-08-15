#!/usr/bin/env python3
"""Check meta field format."""

from config import load_env
from google.cloud import bigquery

load_env()
client = bigquery.Client()

query = """
SELECT chunk_id, meta 
FROM `gleaming-bus-468914-a6.demo_ai.chunks` 
LIMIT 1
"""

result = list(client.query(query).result())
print("Meta field:", repr(result[0].meta))
print("Meta type:", type(result[0].meta))

# Try to parse JSON
import json
try:
    parsed = json.loads(result[0].meta)
    print("Parsed JSON:", parsed)
except Exception as e:
    print("JSON parse error:", e)
