#!/usr/bin/env python3
"""Create sample data for dashboard testing."""

from config import load_env
from google.cloud import bigquery
import json
from datetime import datetime, timedelta
import uuid

load_env()
client = bigquery.Client()

print("🏗️ Creating sample data for dashboard...")

# Create chunks table
chunks_table_sql = """
CREATE OR REPLACE TABLE `gleaming-bus-468914-a6.demo_ai.chunks` (
    chunk_id STRING,
    doc_id STRING,
    content STRING,
    meta JSON,
    embedding ARRAY<FLOAT64>
)
"""

print("Creating chunks table...")
client.query(chunks_table_sql).result()

# Create sample data with proper meta structure for dashboard
sample_chunks = []
base_time = datetime.now() - timedelta(days=30)

issues = [
    {
        "content": "System failed to authenticate user due to expired JWT token. Error: Token validation failed at 2024-01-15 14:32:21",
        "severity": "critical",
        "category": "authentication"
    },
    {
        "content": "Database connection timeout after 30 seconds. Connection pool exhausted, max connections: 100",
        "severity": "high", 
        "category": "database"
    },
    {
        "content": "Memory usage exceeded 85% threshold. Current usage: 87.2GB/100GB. Garbage collection triggered",
        "severity": "medium",
        "category": "performance"
    },
    {
        "content": "API rate limit exceeded for client 192.168.1.100. Requests throttled for 60 seconds",
        "severity": "low",
        "category": "api"
    },
    {
        "content": "SSL certificate expires in 7 days. Certificate CN: api.example.com, expires: 2024-02-01",
        "severity": "medium",
        "category": "security"
    },
    {
        "content": "Disk space warning: /var/log partition 78% full (15.6GB/20GB). Log rotation recommended",
        "severity": "medium",
        "category": "storage"
    },
    {
        "content": "Failed login attempt from IP 203.0.113.45. Username: admin, failed attempts: 5",
        "severity": "high",
        "category": "security"
    },
    {
        "content": "Service health check failed. HTTP 500 response from internal-api.service:8080/health",
        "severity": "critical",
        "category": "service"
    },
    {
        "content": "Backup operation completed successfully. Duration: 45 minutes, size: 2.3TB",
        "severity": "info",
        "category": "backup"
    },
    {
        "content": "User session expired due to inactivity. Session ID: sess_abc123, duration: 2 hours",
        "severity": "low",
        "category": "session"
    }
]

# Create chunks with duplicate content to test duplicate detection
for i, issue in enumerate(issues):
    chunk_id = str(uuid.uuid4())
    doc_id = f"doc_{i // 3}"  # Group chunks into documents
    
    # Create meta with required fields for dashboard
    meta = {
        "severity": issue["severity"],
        "category": issue["category"],
        "ingested_at": (base_time + timedelta(days=i*3)).isoformat(),
        "source": f"log_file_{i}.txt"
    }
    
    # Create simple embedding (dashboard doesn't use it)
    embedding = [0.1] * 768  # Simple embedding for embedding column
    
    sample_chunks.append({
        "chunk_id": chunk_id,
        "doc_id": doc_id, 
        "content": issue["content"],
        "meta": json.dumps(meta),
        "embedding": embedding
    })

# Add some duplicate content for duplicate detection
duplicate_chunk = sample_chunks[0].copy()
duplicate_chunk["chunk_id"] = str(uuid.uuid4())
duplicate_chunk["doc_id"] = "doc_duplicate"
sample_chunks.append(duplicate_chunk)

# Insert data
print(f"Inserting {len(sample_chunks)} chunks...")
table = client.get_table("gleaming-bus-468914-a6.demo_ai.chunks")
errors = client.insert_rows(table, sample_chunks)

if errors:
    print(f"❌ Insert errors: {errors}")
else:
    print("✅ Sample data inserted successfully!")

# Verify insertion
count_query = "SELECT COUNT(*) as count FROM `gleaming-bus-468914-a6.demo_ai.chunks`"
result = client.query(count_query).result()
count = list(result)[0].count
print(f"📊 Total chunks in table: {count}")

# Test meta field parsing
meta_query = """
SELECT 
    chunk_id,
    JSON_EXTRACT_SCALAR(meta, '$.severity') as severity,
    JSON_EXTRACT_SCALAR(meta, '$.category') as category,
    JSON_EXTRACT_SCALAR(meta, '$.ingested_at') as ingested_at
FROM `gleaming-bus-468914-a6.demo_ai.chunks`
LIMIT 3
"""
print("\n📝 Sample meta field data:")
result = client.query(meta_query).result()
for row in result:
    print(f"  ID: {row.chunk_id}")
    print(f"  Severity: {row.severity}")
    print(f"  Category: {row.category}")
    print(f"  Ingested: {row.ingested_at}")
    print()

print("🎯 Ready to test dashboard!")
