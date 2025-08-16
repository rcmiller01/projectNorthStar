#!/usr/bin/env python3
"""Ingest JSONL sample data directly into BigQuery."""

import json
import sys
import os
from pathlib import Path
from datetime import datetime
import uuid

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from bq.load import upsert_documents, upsert_chunks
from bq.bigquery_client import make_client
from config import load_env


def ingest_jsonl_files():
    """Ingest all JSONL files from samples directory."""
    
    # Load configuration
    load_env()  # This loads env vars into os.environ
    is_real = os.getenv('BIGQUERY_REAL', 'False').lower() != 'false'
    print(f"[config] BIGQUERY_REAL: {is_real}")
    
    # Initialize BigQuery client
    client = make_client()
    
    # Find all JSONL files
    samples_dir = Path("samples")
    jsonl_files = list(samples_dir.glob("*.jsonl"))
    
    if not jsonl_files:
        print("❌ No JSONL files found in samples directory")
        return
    
    print(f"🔍 Found {len(jsonl_files)} JSONL files")
    
    all_chunks = []
    all_docs = []
    doc_count = 0
    
    for jsonl_file in jsonl_files:
        print(f"\n📄 Processing {jsonl_file}")
        
        with open(jsonl_file, 'r') as f:
            chunks_in_file = []
            for line_num, line in enumerate(f, 1):
                try:
                    chunk_data = json.loads(line.strip())
                    
                    # Create a chunk record
                    chunk = {
                        "chunk_id": chunk_data.get("chunk_id", f"{jsonl_file.stem}_{line_num:03d}"),
                        "doc_id": f"doc_{jsonl_file.stem}",
                        "text": chunk_data["text"],
                        "meta": chunk_data.get("meta", {}),
                        "type": chunk_data.get("meta", {}).get("type", "incident_report")
                    }
                    
                    chunks_in_file.append(chunk)
                    all_chunks.append(chunk)
                    
                except json.JSONDecodeError as e:
                    print(f"⚠️  Skipping invalid JSON on line {line_num}: {e}")
                    continue
            
            if chunks_in_file:
                # Create a document record for this file
                doc = {
                    "doc_id": f"doc_{jsonl_file.stem}",
                    "type": "incident_collection",
                    "meta": {
                        "filename": jsonl_file.name,
                        "records": len(chunks_in_file),
                        "ingested_at": datetime.now().isoformat() + "Z"
                    }
                }
                all_docs.append(doc)
                doc_count += 1
                
                print(f"  ✅ Loaded {len(chunks_in_file)} chunks")
    
    if not all_chunks:
        print("❌ No chunks to ingest")
        return
    
    print(f"\n📊 Summary:")
    print(f"  Documents: {len(all_docs)}")
    print(f"  Chunks: {len(all_chunks)}")
    
    # Load into BigQuery
    try:
        print(f"\n🚀 Loading data into BigQuery...")
        
        # Load documents first
        if all_docs:
            result = upsert_documents(client, all_docs)
            if result:
                print(f"  ✅ Documents loaded: {len(all_docs)}")
            else:
                print(f"  ⚠️  Document loading skipped (mock mode)")
        
        # Load chunks
        if all_chunks:
            result = upsert_chunks(client, all_chunks)
            if result:
                print(f"  ✅ Chunks loaded: {len(all_chunks)}")
            else:
                print(f"  ⚠️  Chunk loading skipped (mock mode)")
        
        print(f"\n🎉 Ingestion complete!")
        
    except Exception as e:
        print(f"❌ Error loading data: {e}")
        raise


if __name__ == "__main__":
    ingest_jsonl_files()
