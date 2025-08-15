#!/usr/bin/env python3
"""Quick data check for dashboard troubleshooting."""

from config import load_env
from google.cloud import bigquery

load_env()
client = bigquery.Client()

print("📊 Current Data Status:")
print("=" * 40)

# Check chunks count
chunks_count = 0
try:
    query = "SELECT COUNT(*) as count FROM `gleaming-bus-468914-a6.demo_ai.chunks`"
    result = client.query(query)
    chunks_count = list(result)[0].count
    print(f"✅ Chunks table: {chunks_count} records")
except Exception as e:
    print(f"❌ Chunks table error: {e}")

# Check sample chunk data
try:
    result = client.query("""
        SELECT chunk_id, SUBSTR(content, 1, 100) as content_preview, meta
        FROM `gleaming-bus-468914-a6.demo_ai.chunks`
        LIMIT 2
    """)
    print("\n📝 Sample chunk data:")
    for row in result:
        print(f"  ID: {row.chunk_id}")
        print(f"  Content: {row.content_preview}...")
        print(f"  Meta: {row.meta}")
        print()
except Exception as e:
    print(f"❌ Sample data error: {e}")

# Check if views have data
views = ["view_common_issues", "view_issues_by_severity",
         "view_duplicate_chunks"]
for view in views:
    try:
        query = f"SELECT COUNT(*) as count FROM `gleaming-bus-468914-a6.demo_ai.{view}`"
        result = client.query(query)
        count = list(result)[0].count
        print(f"✅ {view}: {count} records")
    except Exception as e:
        print(f"❌ {view}: {e}")

print("\n💡 Next steps:")
if chunks_count == 0:
    print("- No data found. Need to populate with sample data")
    print("- Download Kaggle competition data")
    print("- Or create synthetic issue data")
else:
    print("- Data exists but may not match dashboard schema")
    print("- Check meta field format and severity values")
