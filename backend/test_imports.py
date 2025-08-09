#!/usr/bin/env python3
"""Test imports and basic module loading"""

import sys
import traceback

def test_import(module_path, module_name):
    """Test importing a module"""
    print(f"\nTesting import: {module_name}")
    try:
        exec(f"from {module_path} import {module_name}")
        print(f"✅ Success: {module_name} imported successfully")
        return True
    except Exception as e:
        print(f"❌ Failed: {module_name}")
        print(f"   Error type: {type(e).__name__}")
        print(f"   Error message: {str(e)}")
        traceback.print_exc()
        return False

def test_database_connection():
    """Test database connection"""
    print("\nTesting database connection...")
    try:
        from core.database import SessionLocal
        db = SessionLocal()
        # Try a simple query
        result = db.execute("SELECT 1")
        db.close()
        print("✅ Database connection successful")
        return True
    except Exception as e:
        print("❌ Database connection failed")
        print(f"   Error: {str(e)}")
        traceback.print_exc()
        return False

def main():
    print("=" * 80)
    print("Import and Database Connection Test")
    print("=" * 80)
    
    # Test core imports
    print("\n--- Testing Core Imports ---")
    core_imports = [
        ("core", "config"),
        ("core", "database"),
        ("core", "auth"),
    ]
    
    for module_path, module_name in core_imports:
        test_import(module_path, module_name)
    
    # Test API module imports
    print("\n--- Testing API Module Imports ---")
    api_modules = [
        "auth", "customers", "dashboard", "kits", 
        "leads", "packages", "payments", "reports", "services"
    ]
    
    for module in api_modules:
        test_import("api.v1", module)
    
    # Test database connection
    test_database_connection()
    
    # Test if we can actually create the FastAPI app
    print("\n--- Testing FastAPI App Creation ---")
    try:
        from main import app
        print("✅ FastAPI app created successfully")
        print(f"   App title: {app.title}")
        print(f"   Routes registered: {len(app.routes)}")
    except Exception as e:
        print("❌ Failed to create FastAPI app")
        print(f"   Error: {str(e)}")
        traceback.print_exc()

if __name__ == "__main__":
    main()