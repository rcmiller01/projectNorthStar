#!/usr/bin/env python3
"""Create dataset in us-east1 and test text models there."""

from config import load_env
from google.cloud import bigquery

load_env()

client = bigquery.Client()
project_id = "gleaming-bus-468914-a6"

# Create dataset in us-east1
dataset_id = f"{project_id}.demo_ai_east1"

print("Creating dataset in us-east1 region...")
try:
    dataset = bigquery.Dataset(dataset_id)
    dataset.location = "us-east1"
    dataset.description = "Demo AI dataset for text generation models (us-east1)"
    
    dataset = client.create_dataset(dataset, exists_ok=True)
    print(f"✅ Dataset created: {dataset.dataset_id}")
    print(f"   Location: {dataset.location}")
    
except Exception as e:
    print(f"Dataset creation: {e}")

# Test text model in us-east1 dataset
print("\nTesting text model in us-east1 dataset...")

sql = f"""
CREATE OR REPLACE MODEL `{project_id}.demo_ai_east1.text_model`
REMOTE WITH CONNECTION `{project_id}.us-east1.vertex-ai-east1`
OPTIONS (
  ENDPOINT = 'gemini-1.5-pro'
)
"""

try:
    print("Creating text model...")
    job = client.query(sql)
    job.result()
    print("✅ Text model created successfully!")
    
    # Test generation
    test_sql = f"""
    SELECT * FROM ML.GENERATE_TEXT(
        MODEL `{project_id}.demo_ai_east1.text_model`,
        (SELECT 'Write a short hello message' as prompt),
        STRUCT(50 as max_output_tokens, 0.8 as temperature)
    )
    """
    
    print("Testing text generation...")
    result = client.query(test_sql)
    for row in result:
        generated = row.ml_generate_text_result
        print(f"✅ Generated text: {generated}")
        break
    
    print("\n🎉 SUCCESS! Text generation working in us-east1!")
    print(f"✅ Dataset: {dataset_id}")
    print(f"✅ Connection: {project_id}.us-east1.vertex-ai-east1")
    print(f"✅ Model: {project_id}.demo_ai_east1.text_model")
    
except Exception as e:
    print(f"❌ Text model failed: {e}")
    
    if "not found" in str(e).lower():
        print("Model endpoint may not be available in us-east1")
        print("Try different models: text-bison, gemini-pro, etc.")
