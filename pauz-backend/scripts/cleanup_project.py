#!/usr/bin/env python3
"""
Project cleanup and validation script
Ensures the backend is properly structured and organized
"""

import os
import sys
import shutil
from pathlib import Path

def validate_structure():
    """Validate the project structure"""
    print("🔍 Validating project structure...")
    
    required_dirs = [
        "app",
        "app/models", 
        "app/routes",
        "app/services",
        "app/utils",
        "tests",
        "scripts", 
        "docs",
        "config"
    ]
    
    missing = []
    for dir_path in required_dirs:
        if not os.path.exists(dir_path):
            missing.append(dir_path)
    
    if missing:
        print(f"❌ Missing directories: {missing}")
        return False
    
    print("✅ All required directories present")
    return True

def clean_python_cache():
    """Clean Python cache files"""
    print("🧹 Cleaning Python cache files...")
    
    cache_dirs = ["__pycache__", ".pytest_cache", ".ruff_cache"]
    
    for cache_dir in cache_dirs:
        if os.path.exists(cache_dir):
            shutil.rmtree(cache_dir)
            print(f"  Removed {cache_dir}")
    
    # Clean __pycache__ in subdirectories
    for root, dirs, files in os.walk("."):
        if "__pycache__" in dirs:
            cache_path = os.path.join(root, "__pycache__")
            shutil.rmtree(cache_path)
            print(f"  Removed {cache_path}")

def validate_imports():
    """Check if main imports work (basic validation)"""
    print("🔍 Validating Python imports...")
    
    try:
        # Add current directory to Python path
        sys.path.insert(0, ".")
        
        # Check if we can import basic modules
        from app import models, routes, services
        print("✅ Basic app modules import successfully")
        
        # Check if main.py exists and has the right structure
        main_path = "app/main.py"
        if os.path.exists(main_path):
            with open(main_path, 'r') as f:
                content = f.read()
                if "FastAPI" in content and "app = FastAPI" in content:
                    print("✅ Main application structure looks correct")
                    return True
                else:
                    print("❌ Main application structure issue")
                    return False
        else:
            print("❌ Main application file not found")
            return False
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def main():
    """Main cleanup function"""
    print("🚀 PAUZ Backend Cleanup & Validation")
    print("=" * 50)
    
    # Change to backend directory
    os.chdir(os.path.dirname(os.path.dirname(__file__)))
    print(f"Working directory: {os.getcwd()}")
    
    # Validate structure
    if not validate_structure():
        print("❌ Project structure validation failed")
        return False
    
    # Clean cache
    clean_python_cache()
    
    # Validate imports
    if not validate_imports():
        print("❌ Import validation failed")
        return False
    
    print("\n✅ Project cleanup completed successfully!")
    print("\n📁 Final Structure:")
    print("pauz-backend/")
    print("├── README.md")
    print("├── backend/")
    print("│   ├── app/          # Main application")
    print("│   ├── tests/        # Test suite")
    print("│   ├── scripts/      # Utility scripts")
    print("│   ├── docs/         # Documentation")
    print("│   ├── config/       # Configuration")
    print("│   └── *.db          # Database files")
    print("└── .git/             # Git repository")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)