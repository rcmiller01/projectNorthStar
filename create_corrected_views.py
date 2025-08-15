#!/usr/bin/env python3
"""Create views with corrected JSON parsing."""

from config import load_env
from google.cloud import bigquery

load_env()
client = bigquery.Client()

print("🏗️ Creating dashboard views with corrected JSON parsing...")

# Since meta is stored as STRING containing JSON, we need to parse it first
view_common_issues = """
CREATE OR REPLACE VIEW `gleaming-bus-468914-a6.demo_ai.view_common_issues` AS
SELECT 
    JSON_EXTRACT_SCALAR(PARSE_JSON(meta), '$.category') as issue_type,
    JSON_EXTRACT_SCALAR(PARSE_JSON(meta), '$.severity') as severity,
    COUNT(*) as occurrence_count,
    ARRAY_AGG(DISTINCT chunk_id LIMIT 5) as sample_chunk_ids
FROM `gleaming-bus-468914-a6.demo_ai.chunks`
WHERE meta IS NOT NULL
GROUP BY issue_type, severity
ORDER BY occurrence_count DESC
"""

view_issues_by_severity = """
CREATE OR REPLACE VIEW `gleaming-bus-468914-a6.demo_ai.view_issues_by_severity` AS
SELECT 
    JSON_EXTRACT_SCALAR(PARSE_JSON(meta), '$.severity') as severity,
    COUNT(*) as count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) as percentage
FROM `gleaming-bus-468914-a6.demo_ai.chunks`
WHERE meta IS NOT NULL
GROUP BY severity
ORDER BY 
    CASE severity
        WHEN 'critical' THEN 1
        WHEN 'high' THEN 2  
        WHEN 'medium' THEN 3
        WHEN 'low' THEN 4
        WHEN 'info' THEN 5
        ELSE 6
    END
"""

view_duplicate_chunks = """
CREATE OR REPLACE VIEW `gleaming-bus-468914-a6.demo_ai.view_duplicate_chunks` AS
WITH content_counts AS (
    SELECT 
        content,
        COUNT(*) as occurrence_count,
        ARRAY_AGG(chunk_id) as chunk_ids,
        ARRAY_AGG(JSON_EXTRACT_SCALAR(PARSE_JSON(meta), '$.severity')) as severities
    FROM `gleaming-bus-468914-a6.demo_ai.chunks`
    WHERE meta IS NOT NULL
    GROUP BY content
    HAVING COUNT(*) > 1
)
SELECT 
    content,
    occurrence_count,
    chunk_ids,
    severities
FROM content_counts
ORDER BY occurrence_count DESC
"""

views = [
    ("view_common_issues", view_common_issues),
    ("view_issues_by_severity", view_issues_by_severity), 
    ("view_duplicate_chunks", view_duplicate_chunks)
]

for view_name, view_sql in views:
    print(f"Creating {view_name}...")
    try:
        client.query(view_sql).result()
        print(f"✅ {view_name} created successfully")
    except Exception as e:
        print(f"❌ Error creating {view_name}: {e}")

print("\n🧪 Testing views...")

test_queries = [
    ("Common Issues", "SELECT * FROM `gleaming-bus-468914-a6.demo_ai.view_common_issues` LIMIT 3"),
    ("Issues by Severity", "SELECT * FROM `gleaming-bus-468914-a6.demo_ai.view_issues_by_severity`"),
    ("Duplicate Chunks", "SELECT content, occurrence_count FROM `gleaming-bus-468914-a6.demo_ai.view_duplicate_chunks`")
]

for test_name, test_query in test_queries:
    print(f"\n📊 {test_name}:")
    try:
        results = list(client.query(test_query).result())
        if results:
            for row in results:
                print(f"  {dict(row)}")
        else:
            print("  No data found")
    except Exception as e:
        print(f"  Error: {e}")

print("\n🎯 Views updated! Dashboard should now show data.")
