#!/usr/bin/env python3
"""Debug JSON extraction issue."""

from config import load_env
from google.cloud import bigquery

load_env()
client = bigquery.Client()

print("🔍 Debugging JSON extraction...")

# First check what TO_JSON_STRING produces
query1 = """
SELECT 
    TO_JSON_STRING(meta) as json_string,
    meta
FROM `gleaming-bus-468914-a6.demo_ai.chunks` 
LIMIT 1
"""

print("Raw data:")
result = list(client.query(query1).result())
json_string = result[0].json_string
raw_meta = result[0].meta
print(f"  JSON String: {json_string}")
print(f"  Raw meta: {raw_meta}")
print(f"  Types: json_string={type(json_string)}, meta={type(raw_meta)}")

# Test JSON extraction on the string
query2 = f"""
SELECT 
    JSON_EXTRACT_SCALAR('{json_string}', '$.severity') as severity,
    JSON_EXTRACT_SCALAR('{json_string}', '$.category') as category
"""

print("\nJSON extraction from literal string:")
try:
    result2 = list(client.query(query2).result())
    print(f"  Severity: {result2[0].severity}")
    print(f"  Category: {result2[0].category}")
except Exception as e:
    print(f"  Error: {e}")

# Test double JSON wrapping issue
print(f"\nJSON analysis:")
import json
try:
    parsed = json.loads(json_string)
    print(f"  Parsed JSON: {parsed}")
    print(f"  Type of parsed: {type(parsed)}")
    if isinstance(parsed, str):
        # It's double-wrapped
        parsed2 = json.loads(parsed)
        print(f"  Double-parsed JSON: {parsed2}")
except Exception as e:
    print(f"  Parse error: {e}")

# Test the fix
if json_string.startswith('"') and json_string.endswith('"'):
    print("\nDetected double-wrapped JSON, testing fix...")
    query3 = """
    SELECT 
        JSON_EXTRACT_SCALAR(JSON_EXTRACT_SCALAR(TO_JSON_STRING(meta), '$'), '$.severity') as severity
    FROM `gleaming-bus-468914-a6.demo_ai.chunks` 
    LIMIT 1
    """
    try:
        result3 = list(client.query(query3).result())
        print(f"  Fixed extraction: {result3[0].severity}")
    except Exception as e:
        print(f"  Fix error: {e}")
