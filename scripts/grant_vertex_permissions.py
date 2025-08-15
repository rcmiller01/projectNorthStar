"""Grant Vertex AI permissions to BigQuery connection service account."""
from __future__ import annotations
import os
import sys
from pathlib import Path

# Add parent directory to path for config import
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from google.cloud import resourcemanager_v1
    from google.iam.v1 import iam_policy_pb2, policy_pb2
    from config import load_env
except Exception as e:
    print(f"Import error: {e}")
    print("Install required packages:")
    print("pip install google-cloud-resource-manager google-cloud-iam")
    raise

# Load environment configuration
load_env()

PROJECT = os.getenv("PROJECT_ID") or "your-project-id"
# This is the service account from the error message
SERVICE_ACCOUNT = "bqcx-111337406730-7dcz@gcp-sa-bigquery-condel.iam.gserviceaccount.com"
ROLE = "roles/aiplatform.user"


def grant_vertex_ai_permission():
    """Grant Vertex AI User role to BigQuery connection service account."""
    print("🔐 Granting Vertex AI permissions to BigQuery connection...")
    print(f"Project: {PROJECT}")
    print(f"Service Account: {SERVICE_ACCOUNT}")
    print(f"Role: {ROLE}")
    
    try:
        # Create the Resource Manager client
        client = resourcemanager_v1.ProjectsClient()
        
        # Get current IAM policy
        request = iam_policy_pb2.GetIamPolicyRequest(
            resource=f"projects/{PROJECT}"
        )
        policy = client.get_iam_policy(request=request)
        
        # Check if the binding already exists
        member = f"serviceAccount:{SERVICE_ACCOUNT}"
        binding_exists = False
        
        for binding in policy.bindings:
            if binding.role == ROLE:
                if member in binding.members:
                    print(f"✅ Permission already exists: {ROLE}")
                    return True
                else:
                    binding.members.append(member)
                    binding_exists = True
                    break
        
        # If binding doesn't exist, create it
        if not binding_exists:
            new_binding = policy_pb2.Binding(
                role=ROLE,
                members=[member]
            )
            policy.bindings.append(new_binding)
        
        # Set the updated policy
        set_request = iam_policy_pb2.SetIamPolicyRequest(
            resource=f"projects/{PROJECT}",
            policy=policy
        )
        
        client.set_iam_policy(request=set_request)
        print(f"✅ Granted {ROLE} to {SERVICE_ACCOUNT}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to grant permission: {e}")
        print("\nManual steps:")
        print("1. Go to: https://console.cloud.google.com/iam-admin/iam")
        print(f"2. Add role 'Vertex AI User' to: {SERVICE_ACCOUNT}")
        return False


def main():
    """Main function."""
    print("🤖 BigQuery → Vertex AI Permission Setup")
    print("="*60)
    
    success = grant_vertex_ai_permission()
    
    if success:
        print("\n🎉 SUCCESS! BigQuery connection has Vertex AI permissions!")
        print("\nNow run: python scripts/create_remote_models.py")
    else:
        print("\n❌ Permission setup failed. Use manual steps above.")


if __name__ == "__main__":
    main()
