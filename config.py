"""Environment configuration loader for projectNorthStar.

Supports multiple authentication methods for BigQuery:
1. API Key (GOOGLE_API_KEY) - for testing only
2. Service Account (GOOGLE_APPLICATION_CREDENTIALS) - recommended
3. Default credentials - gcloud auth application-default login

Usage:
    from config import load_env
    load_env()  # Loads from .env file if present
"""

import os
from pathlib import Path
from typing import Optional


def load_env(env_file: Optional[str] = None) -> None:
    """Load environment variables from .env file if it exists."""
    if env_file is None:
        env_file = ".env"
    
    env_path = Path(env_file)
    if not env_path.exists():
        print(f"[config] No {env_file} file found - using system environment")
        return
    
    print(f"[config] Loading environment from {env_file}")
    
    with open(env_path, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            
            # Skip comments and empty lines
            if not line or line.startswith('#'):
                continue
                
            # Parse KEY=VALUE format
            if '=' in line:
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip()
                
                # Remove quotes if present
                if value.startswith('"') and value.endswith('"'):
                    value = value[1:-1]
                elif value.startswith("'") and value.endswith("'"):
                    value = value[1:-1]
                
                # Only set if not already in environment
                if key not in os.environ:
                    os.environ[key] = value
                    print(f"[config] Set {key}=***")
                else:
                    print(f"[config] Using existing {key} from environment")


def get_auth_method() -> str:
    """Determine which authentication method is being used."""
    if os.getenv("GOOGLE_API_KEY"):
        return "api_key"
    elif os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
        return "service_account"
    else:
        return "default_credentials"


def validate_config() -> bool:
    """Validate that required configuration is present."""
    required_vars = ["PROJECT_ID", "DATASET", "LOCATION"]
    missing = [var for var in required_vars if not os.getenv(var)]
    
    if missing:
        print(f"[config] ERROR: Missing required environment variables: "
              f"{missing}")
        print("[config] Create a .env file with:")
        for var in missing:
            print(f"[config]   {var}=your-value-here")
        return False
    
    auth_method = get_auth_method()
    print(f"[config] Authentication method: {auth_method}")
    
    if auth_method == "api_key":
        print("[config] WARNING: API keys have limited BigQuery support")
        print("[config] Consider using service account or default credentials")
    
    return True


if __name__ == "__main__":
    # Test the configuration
    load_env()
    if validate_config():
        print("[config] Configuration is valid!")
    else:
        print("[config] Configuration has errors!")
