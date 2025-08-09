import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.database import engine
from sqlalchemy import text

def update_service_types_table():
    """Add missing columns to service_types table"""
    
    with engine.connect() as conn:
        # Check if columns exist first
        result = conn.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'service_types'
        """))
        existing_columns = [row[0] for row in result]
        
        # Add missing columns
        if 'default_duration' not in existing_columns:
            conn.execute(text("""
                ALTER TABLE service_types 
                ADD COLUMN default_duration INTEGER DEFAULT 60
            """))
            print("Added default_duration column")
            
        if 'default_price' not in existing_columns:
            conn.execute(text("""
                ALTER TABLE service_types 
                ADD COLUMN default_price INTEGER DEFAULT 0
            """))
            print("Added default_price column")
            
        if 'service_color' not in existing_columns:
            conn.execute(text("""
                ALTER TABLE service_types 
                ADD COLUMN service_color VARCHAR(10) DEFAULT '#3B82F6'
            """))
            print("Added service_color column")
            
        conn.commit()
        print("Service types table updated successfully!")

if __name__ == "__main__":
    update_service_types_table()