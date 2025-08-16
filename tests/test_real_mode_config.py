#!/usr/bin/env python3
"""Test BigQuery real mode configuration without enabling it."""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / 'src'))

def test_real_mode_config():
    """Test that real BigQuery mode configuration is valid."""
    
    print("🔍 Testing BigQuery Real Mode Configuration")
    print("=" * 50)
    
    # Import config to load environment
    from config import load_env
    load_env()  # Actually load the .env file
    
    # Check required environment variables
    required_vars = [
        'PROJECT_ID',
        'BQ_PROJECT_ID', 
        'BQ_LOCATION',
        'BQ_DATASET',
        'GOOGLE_APPLICATION_CREDENTIALS'
    ]
    
    missing_vars = []
    print("\n📋 Environment Variables:")
    for var in required_vars:
        value = os.getenv(var)
        if value:
            if 'CREDENTIALS' in var:
                print(f"  ✅ {var}: {value[:50]}...") 
            else:
                print(f"  ✅ {var}: {value}")
        else:
            missing_vars.append(var)
            print(f"  ❌ {var}: Not set")
    
    # Check service account file exists
    service_account_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
    if service_account_path:
        if os.path.exists(service_account_path):
            print(f"  ✅ Service account file exists: {service_account_path}")
        else:
            print(f"  ❌ Service account file not found: {service_account_path}")
            missing_vars.append('SERVICE_ACCOUNT_FILE')
    
    # Check BigQuery dependencies
    print("\n📦 Dependencies:")
    try:
        import google.cloud.bigquery
        print("  ✅ google-cloud-bigquery: Available")
    except ImportError:
        print("  ❌ google-cloud-bigquery: Missing (run: pip install google-cloud-bigquery)")
        missing_vars.append('BIGQUERY_DEPENDENCY')
    
    try:
        import google.auth
        print("  ✅ google-auth: Available")
    except ImportError:
        print("  ❌ google-auth: Missing (run: pip install google-auth)")
        missing_vars.append('AUTH_DEPENDENCY')
    
    # Test client creation (without enabling real mode)
    print("\n🔧 Client Configuration:")
    from bq.bigquery_client import make_client
    
    # Current mode (should be stub)
    current_client = make_client()
    print(f"  📊 Current mode: {type(current_client).__name__}")
    
    # Simulate real mode configuration
    print("\n🔧 Real Mode Simulation:")
    try:
        from bq.bigquery_client import RealClient
        
        # Check if we can create a RealClient instance (without connecting)
        project_id = os.getenv('BQ_PROJECT_ID')
        location = os.getenv('BQ_LOCATION')
        
        if project_id and location:
            print(f"  ✅ RealClient configuration: project={project_id}, location={location}")
        else:
            print("  ❌ Missing project_id or location for RealClient")
            missing_vars.append('CLIENT_CONFIG')
            
    except Exception as e:
        print(f"  ❌ RealClient creation failed: {e}")
        missing_vars.append('CLIENT_CREATION')
    
    # Summary
    print("\n" + "=" * 50)
    if missing_vars:
        print("❌ Real BigQuery mode is NOT ready")
        print("   Missing requirements:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\n💡 To enable real mode:")
        print("   1. Fix missing requirements above")
        print("   2. Uncomment BIGQUERY_REAL=1 in .env file")
        return False
    else:
        print("✅ Real BigQuery mode is READY!")
        print("\n💡 To enable real mode:")
        print("   Uncomment BIGQUERY_REAL=1 in .env file")
        print("\n⚠️  Note: Ensure BigQuery dataset and views exist first")
        print("   Run: python run_util.py create_views")
        return True

if __name__ == "__main__":
    success = test_real_mode_config()
    sys.exit(0 if success else 1)
