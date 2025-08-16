#!/usr/bin/env python3
"""Generate realistic sample data for the dashboard demo."""

import json
import random
from datetime import datetime, timedelta
from pathlib import Path

# Sample issue templates
ISSUE_TEMPLATES = [
    {
        "template": "Login timeout error after {duration} seconds on {browser}",
        "severity_weights": {"P0": 0.1, "P1": 0.3, "P2": 0.4, "P3": 0.2},
        "details": [
            "User authentication failed",
            "Session expired unexpectedly",
            "Network timeout during login",
            "Server response delayed"
        ]
    },
    {
        "template": "Database connection pool exhausted - max connections: {max_conn}",
        "severity_weights": {"P0": 0.4, "P1": 0.4, "P2": 0.2, "P3": 0.0},
        "details": [
            "Connection pool at capacity",
            "Query timeout after 30 seconds",
            "Database server overloaded",
            "Too many concurrent users"
        ]
    },
    {
        "template": "Memory leak detected in {service} service - heap size: {memory}MB",
        "severity_weights": {"P0": 0.2, "P1": 0.5, "P2": 0.3, "P3": 0.0},
        "details": [
            "Garbage collection frequency increased",
            "Application performance degraded",
            "Out of memory error imminent",
            "Heap dump analysis required"
        ]
    },
    {
        "template": "File upload failed for {file_type} files larger than {size}MB",
        "severity_weights": {"P0": 0.0, "P1": 0.2, "P2": 0.5, "P3": 0.3},
        "details": [
            "Upload progress stuck at 0%",
            "Request entity too large error",
            "Temporary directory full",
            "File processing timeout"
        ]
    },
    {
        "template": "API rate limit exceeded for endpoint /api/{endpoint}",
        "severity_weights": {"P0": 0.1, "P1": 0.3, "P2": 0.4, "P3": 0.2},
        "details": [
            "429 Too Many Requests returned",
            "Client exceeded 1000 requests/hour",
            "Backoff strategy not implemented",
            "Rate limiting headers missing"
        ]
    },
    {
        "template": "SSL certificate expiring in {days} days for {domain}",
        "severity_weights": {"P0": 0.3, "P1": 0.4, "P2": 0.2, "P3": 0.1},
        "details": [
            "Certificate renewal required",
            "HTTPS connections will fail",
            "Browser security warnings",
            "Automated renewal failed"
        ]
    },
    {
        "template": "Disk space critical on {server} - {percent}% full",
        "severity_weights": {"P0": 0.5, "P1": 0.3, "P2": 0.2, "P3": 0.0},
        "details": [
            "Log rotation not working",
            "Temporary files accumulating",
            "Database growth unexpected",
            "Backup cleanup required"
        ]
    }
]

# Sample data values
BROWSERS = ["Chrome", "Firefox", "Safari", "Edge", "Mobile"]
SERVICES = ["auth-service", "payment-service", "user-service", "notification-service"]
ENDPOINTS = ["users", "orders", "payments", "search", "upload"]
DOMAINS = ["api.example.com", "secure.example.com", "app.example.com"]
SERVERS = ["web-01", "web-02", "db-01", "cache-01", "worker-01"]
FILE_TYPES = ["PDF", "image", "video", "document", "archive"]

def weighted_choice(weights):
    """Choose item based on weights dictionary."""
    items = list(weights.keys())
    probs = list(weights.values())
    return random.choices(items, weights=probs)[0]

def generate_issue_text(template_info):
    """Generate issue text from template."""
    template = template_info["template"]
    
    # Fill in template variables
    variables = {
        "duration": random.randint(5, 60),
        "browser": random.choice(BROWSERS),
        "max_conn": random.choice([50, 100, 200, 500]),
        "service": random.choice(SERVICES),
        "memory": random.randint(512, 8192),
        "file_type": random.choice(FILE_TYPES),
        "size": random.choice([10, 25, 50, 100]),
        "endpoint": random.choice(ENDPOINTS),
        "days": random.choice([1, 3, 7, 14, 30]),
        "domain": random.choice(DOMAINS),
        "server": random.choice(SERVERS),
        "percent": random.randint(85, 99)
    }
    
    try:
        title = template.format(**variables)
    except KeyError:
        title = template
    
    # Add a detail
    detail = random.choice(template_info["details"])
    
    # Create text without newlines for BigQuery compatibility
    return f"{title}. {detail}", template_info["severity_weights"]

def generate_sample_chunks(num_chunks=100):
    """Generate sample chunks for the dashboard."""
    chunks = []
    
    # Generate data over the last 30 days
    start_date = datetime.now() - timedelta(days=30)
    
    for i in range(num_chunks):
        # Pick random template
        template_info = random.choice(ISSUE_TEMPLATES)
        
        # Generate issue text and get severity weights
        text, severity_weights = generate_issue_text(template_info)
        
        # Choose severity based on weights
        severity = weighted_choice(severity_weights)
        
        # Random timestamp in the last 30 days
        random_offset = random.randint(0, 30 * 24 * 60 * 60)  # 30 days in seconds
        timestamp = start_date + timedelta(seconds=random_offset)
        
        # Create chunk
        chunk = {
            "chunk_id": f"chunk_{i:04d}",
            "text": text,
            "meta": {
                "severity": severity,
                "ingested_at": timestamp.isoformat() + "Z",
                "source": "synthetic_issues",
                "type": "incident_report"
            }
        }
        
        chunks.append(chunk)
    
    return chunks

def create_sample_files():
    """Create sample issue files in the samples directory."""
    
    # Create more sample data
    samples_dir = Path("samples")
    samples_dir.mkdir(exist_ok=True)
    
    # Generate chunks
    chunks = generate_sample_chunks(150)  # More data for better visualization
    
    # Group by severity for separate files
    by_severity = {}
    for chunk in chunks:
        severity = chunk["meta"]["severity"]
        if severity not in by_severity:
            by_severity[severity] = []
        by_severity[severity].append(chunk)
    
    print(f"Generated {len(chunks)} sample issues:")
    for severity, severity_chunks in by_severity.items():
        print(f"  {severity}: {len(severity_chunks)} issues")
        
        # Create a file for each severity
        filename = samples_dir / f"issues_{severity.lower()}.jsonl"
        with open(filename, 'w') as f:
            for chunk in severity_chunks:
                f.write(json.dumps(chunk) + "\n")
        
        print(f"  Created: {filename}")
    
    # Also create a mixed file with recent critical issues
    recent_critical = [
        chunk for chunk in chunks 
        if chunk["meta"]["severity"] in ["P0", "P1"] 
        and (datetime.now() - datetime.fromisoformat(chunk["meta"]["ingested_at"].replace("Z", ""))) < timedelta(days=7)
    ]
    
    if recent_critical:
        critical_file = samples_dir / "recent_critical_issues.jsonl"
        with open(critical_file, 'w') as f:
            for chunk in recent_critical:
                f.write(json.dumps(chunk) + "\n")
        print(f"  Created: {critical_file} ({len(recent_critical)} critical issues)")
    
    return len(chunks)

if __name__ == "__main__":
    print("🔨 Generating realistic sample data for dashboard...")
    total_issues = create_sample_files()
    
    print(f"\n✅ Generated {total_issues} sample issues!")
    print("\nNext steps:")
    print("1. Run: python -m core.cli ingest --path samples --type auto --max-tokens 512")
    print("2. Run: python scripts/create_views.py")
    print("3. Restart dashboard to see the data")
