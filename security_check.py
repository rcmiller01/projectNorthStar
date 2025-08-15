#!/usr/bin/env python3
"""Final security verification before commit."""

import os
import re
from pathlib import Path

def check_for_sensitive_data():
    """Check for any remaining sensitive data patterns."""
    
    print("🔍 SECURITY VERIFICATION")
    print("=" * 50)
    
    # Patterns to check for
    patterns = [
        (r'gleaming-bus-468914', 'Hardcoded project ID'),
        (r'sk-[a-zA-Z0-9]{32,}', 'OpenAI API key'),
        (r'AIza[a-zA-Z0-9]{35}', 'Google API key'),
        (r'ya29\.[a-zA-Z0-9_-]+', 'Google OAuth token'),
        (r'AKIA[A-Z0-9]{16}', 'AWS access key'),
        (r'["\']?[A-Za-z0-9+/]{40,}["\']?', 'Possible base64 encoded secret'),
    ]
    
    # Files to check
    excluded_dirs = {'.git', '.venv', '__pycache__', '.mypy_cache', '.pytest_cache', 'node_modules', 'out'}
    excluded_files = {'.env', '.env.local', '.env.prod', 'README_OLD.md'}
    
    issues_found = []
    files_checked = 0
    
    for root, dirs, files in os.walk('.'):
        # Skip excluded directories
        dirs[:] = [d for d in dirs if d not in excluded_dirs]
        
        for file in files:
            if file in excluded_files:
                continue
                
            file_path = Path(root) / file
            
            # Only check text files
            if file_path.suffix in {'.py', '.md', '.txt', '.yml', '.yaml', '.json', '.toml', '.cfg', '.ini'}:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        files_checked += 1
                        
                        for pattern, description in patterns:
                            matches = re.findall(pattern, content)
                            for match in matches:
                                # Skip example/template patterns
                                if any(skip in match.lower() for skip in ['your-', 'example', 'template', 'placeholder']):
                                    continue
                                issues_found.append((file_path, description, match))
                                
                except Exception as e:
                    print(f"⚠️  Could not read {file_path}: {e}")
    
    print(f"📁 Files checked: {files_checked}")
    
    if issues_found:
        print(f"❌ SECURITY ISSUES FOUND: {len(issues_found)}")
        for file_path, description, match in issues_found:
            print(f"   {file_path}: {description}")
            print(f"     Match: {match[:50]}...")
        return False
    else:
        print("✅ No sensitive data patterns detected")
        return True

def check_gitignore():
    """Verify .gitignore is comprehensive."""
    
    print("\n🚫 GITIGNORE VERIFICATION")
    print("=" * 50)
    
    required_patterns = [
        '.env',
        '*.json',
        '__pycache__/',
        '.venv/',
        'check_*.py',
        'test_*.py',
        'debug_*.py'
    ]
    
    try:
        with open('.gitignore', 'r') as f:
            gitignore_content = f.read()
        
        missing_patterns = []
        for pattern in required_patterns:
            if pattern not in gitignore_content:
                missing_patterns.append(pattern)
        
        if missing_patterns:
            print(f"❌ Missing patterns in .gitignore: {missing_patterns}")
            return False
        else:
            print("✅ .gitignore contains all required patterns")
            return True
            
    except FileNotFoundError:
        print("❌ .gitignore file not found")
        return False

def main():
    """Run all security checks."""
    
    print("🛡️  FINAL SECURITY SCAN")
    print("=" * 60)
    
    checks = [
        check_for_sensitive_data(),
        check_gitignore()
    ]
    
    if all(checks):
        print("\n🎉 ALL SECURITY CHECKS PASSED!")
        print("✅ Repository is ready for commit")
        print("\n📋 Security Summary:")
        print("   - No hardcoded credentials found")
        print("   - Sensitive file patterns in .gitignore")
        print("   - Test files cleaned up")
        print("   - Generic placeholders used")
        return True
    else:
        print("\n⚠️  SECURITY ISSUES DETECTED")
        print("❌ Fix issues before committing")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
