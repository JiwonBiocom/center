import os
import sys
from pathlib import Path

# Add parent directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from core.database import SessionLocal
from sqlalchemy import text

def check_lead_consultation_history_table():
    """Check lead_consultation_history table structure"""
    db = SessionLocal()
    
    try:
        # Check if table exists
        result = db.execute(text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name = 'lead_consultation_history'
        """))
        
        table_exists = result.fetchone()
        print(f"Table 'lead_consultation_history' exists: {table_exists is not None}")
        
        if table_exists:
            # Get column information
            result = db.execute(text("""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns 
                WHERE table_schema = 'public' 
                AND table_name = 'lead_consultation_history'
                ORDER BY ordinal_position
            """))
            
            columns = result.fetchall()
            print("\nTable structure:")
            for col in columns:
                print(f"  - {col[0]}: {col[1]} ({'NULL' if col[2] == 'YES' else 'NOT NULL'})")
        else:
            print("Table does not exist, need to create it")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    check_lead_consultation_history_table()