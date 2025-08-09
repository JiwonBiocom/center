#!/usr/bin/env python3
"""Test database connection and diagnose endpoint issues"""

import sys
import traceback
from sqlalchemy import text
from sqlalchemy.orm import Session
import asyncio

def test_database_connection():
    """Test database connection and table existence"""
    print("\n" + "=" * 80)
    print("DATABASE CONNECTION AND TABLE TEST")
    print("=" * 80)
    
    try:
        from core.database import SessionLocal, engine
        from core.config import settings
        
        print(f"Database URL pattern: postgresql://...")
        print(f"Database name: {settings.POSTGRES_DATABASE}")
        
        # Test basic connection
        with SessionLocal() as db:
            result = db.execute(text("SELECT 1")).scalar()
            print(f"✅ Database connection successful")
            
            # List all tables
            tables_query = text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name
            """)
            tables = db.execute(tables_query).fetchall()
            
            print(f"\nTables found in database ({len(tables)}):")
            for table in tables:
                print(f"  - {table[0]}")
            
            # Check for specific tables
            expected_tables = [
                'users', 'customers', 'services', 'payments', 
                'packages', 'leads', 'kits', 'audit_logs'
            ]
            
            existing_tables = [t[0] for t in tables]
            
            print("\nTable existence check:")
            for table in expected_tables:
                if table in existing_tables:
                    # Count rows
                    count = db.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar()
                    print(f"  ✅ {table}: {count} rows")
                else:
                    print(f"  ❌ {table}: NOT FOUND")
                    
        return True
    except Exception as e:
        print("❌ Database test failed")
        print(f"Error: {str(e)}")
        traceback.print_exc()
        return False

async def test_endpoint_with_details(endpoint_name, endpoint_func):
    """Test a specific endpoint function"""
    print(f"\nTesting endpoint: {endpoint_name}")
    try:
        # Import dependencies
        from core.database import SessionLocal
        from core.auth import get_current_user
        from models.user import User
        
        # Create a mock database session
        db = SessionLocal()
        
        # Create a mock user for authentication
        mock_user = User(
            id=1,
            email="admin@aibio.com",
            full_name="Test Admin",
            is_active=True,
            is_superuser=True
        )
        
        # Try to call the endpoint function
        # Most endpoints expect (skip, limit, db, current_user)
        try:
            if asyncio.iscoroutinefunction(endpoint_func):
                result = await endpoint_func(skip=0, limit=10, db=db, current_user=mock_user)
            else:
                result = endpoint_func(skip=0, limit=10, db=db, current_user=mock_user)
            print(f"✅ Endpoint executed successfully")
            print(f"   Result type: {type(result)}")
            if hasattr(result, '__len__'):
                print(f"   Result length: {len(result)}")
        except Exception as e:
            print(f"❌ Endpoint execution failed")
            print(f"   Error: {str(e)}")
            traceback.print_exc()
        finally:
            db.close()
            
    except Exception as e:
        print(f"❌ Failed to test endpoint")
        print(f"   Error: {str(e)}")

async def test_specific_endpoints():
    """Test specific problematic endpoints"""
    print("\n" + "=" * 80)
    print("ENDPOINT FUNCTION TEST")
    print("=" * 80)
    
    # Test each problematic endpoint
    endpoints_to_test = [
        ("customers", "get_customers"),
        ("services", "get_services"),
        ("payments", "get_payments"),
        ("packages", "get_packages"),
        ("leads", "get_leads"),
    ]
    
    for module_name, func_name in endpoints_to_test:
        try:
            module = __import__(f"api.v1.{module_name}", fromlist=[func_name])
            if hasattr(module, func_name):
                func = getattr(module, func_name)
                await test_endpoint_with_details(f"{module_name}.{func_name}", func)
            else:
                print(f"\n❌ Function {func_name} not found in {module_name}")
        except Exception as e:
            print(f"\n❌ Failed to import {module_name}.{func_name}")
            print(f"   Error: {str(e)}")

def check_router_registration():
    """Check if routers are properly registered"""
    print("\n" + "=" * 80)
    print("ROUTER REGISTRATION CHECK")
    print("=" * 80)
    
    try:
        from main import app
        
        # Get all routes
        routes = []
        for route in app.routes:
            if hasattr(route, 'path'):
                routes.append({
                    'path': route.path,
                    'methods': list(route.methods) if hasattr(route, 'methods') else [],
                    'name': route.name if hasattr(route, 'name') else 'unnamed'
                })
        
        # Group by API section
        api_sections = {}
        for route in routes:
            if route['path'].startswith('/api/v1/'):
                section = route['path'].split('/')[3] if len(route['path'].split('/')) > 3 else 'root'
                if section not in api_sections:
                    api_sections[section] = []
                api_sections[section].append(route)
        
        print(f"Total routes: {len(routes)}")
        print(f"API sections found: {len(api_sections)}")
        
        for section, section_routes in sorted(api_sections.items()):
            print(f"\n{section.upper()} ({len(section_routes)} routes):")
            for route in section_routes[:3]:  # Show first 3 routes
                print(f"  - {' '.join(route['methods'])}: {route['path']}")
            if len(section_routes) > 3:
                print(f"  ... and {len(section_routes) - 3} more")
                
    except Exception as e:
        print(f"❌ Failed to check router registration")
        print(f"   Error: {str(e)}")
        traceback.print_exc()

async def main():
    # Test database first
    db_ok = test_database_connection()
    
    # Check router registration
    check_router_registration()
    
    # Test specific endpoints
    await test_specific_endpoints()

if __name__ == "__main__":
    asyncio.run(main())