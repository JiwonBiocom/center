#!/usr/bin/env python3
"""Check the actual structure of database tables"""

from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import sessionmaker
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./aibio_center.db")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

# Use SQLAlchemy inspector
inspector = inspect(engine)

print("=" * 80)
print("DATABASE TABLE STRUCTURE")
print("=" * 80)

# Get all table names
tables = inspector.get_table_names()
print(f"\nTables found: {len(tables)}")

# For each table, show its columns
for table_name in sorted(tables):
    print(f"\n{table_name.upper()}:")
    columns = inspector.get_columns(table_name)
    
    for col in columns:
        col_type = str(col['type'])
        nullable = "NULL" if col['nullable'] else "NOT NULL"
        primary = " PRIMARY KEY" if col.get('primary_key') else ""
        print(f"  - {col['name']}: {col_type} {nullable}{primary}")
    
    # Show sample data if table has records
    with SessionLocal() as db:
        count = db.execute(text(f"SELECT COUNT(*) FROM {table_name}")).scalar()
        if count > 0:
            print(f"  Records: {count}")
            
            # Get column names for this table
            col_names = [col['name'] for col in columns]
            
            # Show first record
            if col_names:
                cols_str = ", ".join(f'"{c}"' for c in col_names[:5])  # Quote column names
                try:
                    first_record = db.execute(text(f"SELECT {cols_str} FROM {table_name} LIMIT 1")).fetchone()
                    if first_record:
                        print(f"  Sample: {dict(zip(col_names[:5], first_record))}")
                except Exception as e:
                    print(f"  Sample: Error reading - {str(e)}")

print("\n" + "=" * 80)