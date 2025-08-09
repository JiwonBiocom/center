#!/usr/bin/env python3
"""Test synchronous database operations to verify the issue"""

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import os

# Get database URL from environment or use default
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./aibio_center.db")

print(f"Testing with database: {DATABASE_URL}")

# Create engine and session
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Test basic operations
try:
    with SessionLocal() as db:
        # Test connection
        result = db.execute(text("SELECT 1")).scalar()
        print(f"✅ Database connection successful")
        
        # Check if customers table exists
        if DATABASE_URL.startswith("sqlite"):
            tables_query = text("SELECT name FROM sqlite_master WHERE type='table'")
        else:
            tables_query = text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
            """)
        
        tables = db.execute(tables_query).fetchall()
        print(f"\nTables found: {len(tables)}")
        for table in tables:
            print(f"  - {table[0]}")
            
        # Try to query customers table
        if any('customers' in str(t[0]) for t in tables):
            count = db.execute(text("SELECT COUNT(*) FROM customers")).scalar()
            print(f"\n✅ Customers table exists with {count} records")
            
            # Get sample data
            customers = db.execute(text("SELECT id, name, phone FROM customers LIMIT 5")).fetchall()
            if customers:
                print("\nSample customers:")
                for c in customers:
                    print(f"  - ID: {c[0]}, Name: {c[1]}, Phone: {c[2]}")
        else:
            print("\n❌ Customers table not found")
            
except Exception as e:
    print(f"\n❌ Error: {str(e)}")
    import traceback
    traceback.print_exc()