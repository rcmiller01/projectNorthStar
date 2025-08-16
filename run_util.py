#!/usr/bin/env python3
"""Convenience script to run utilities from project root."""

import sys
import os
import subprocess
from pathlib import Path

def main():
    if len(sys.argv) < 2:
        print("Usage: python run_util.py <utility_name> [args...]")
        print("\nAvailable utilities:")
        
        # List utilities in each folder
        project_root = Path(__file__).parent
        
        print("\n📊 Tests (tests/):")
        test_dir = project_root / "tests"
        if test_dir.exists():
            for f in sorted(test_dir.glob("test_*.py")):
                print(f"  {f.stem}")
        
        print("\n🔍 Debug tools (debug/):")
        debug_dir = project_root / "debug"  
        if debug_dir.exists():
            for f in sorted(debug_dir.glob("debug_*.py")):
                print(f"  {f.stem}")
        
        print("\n🛠️  Utilities (utils/):")
        utils_dir = project_root / "utils"
        if utils_dir.exists():
            for f in sorted(utils_dir.glob("*.py")):
                if f.stem != "__init__":
                    print(f"  {f.stem}")
        
        print("\n📜 Scripts (scripts/):")
        scripts_dir = project_root / "scripts"
        if scripts_dir.exists():
            for f in sorted(scripts_dir.glob("*.py")):
                print(f"  {f.stem}")
        
        return
    
    util_name = sys.argv[1]
    util_args = sys.argv[2:]
    
    # Search for the utility in different folders
    project_root = Path(__file__).parent
    search_dirs = ["tests", "debug", "utils", "scripts"]
    
    util_path = None
    for dirname in search_dirs:
        search_dir = project_root / dirname
        if search_dir.exists():
            # Try exact match first
            exact_match = search_dir / f"{util_name}.py"
            if exact_match.exists():
                util_path = exact_match
                break
            
            # Try with prefix (for files that don't include their folder prefix)
            prefix_match = search_dir / f"{dirname.rstrip('s')}_{util_name}.py"
            if prefix_match.exists():
                util_path = prefix_match
                break
    
    if util_path is None:
        print(f"❌ Utility '{util_name}' not found in any folder")
        return 1
    
    print(f"🚀 Running: {util_path}")
    
    # Change to project root directory and run the utility
    os.chdir(project_root)
    
    # Run the utility with Python
    cmd = [sys.executable, str(util_path)] + util_args
    result = subprocess.run(cmd)
    
    return result.returncode

if __name__ == "__main__":
    sys.exit(main())
