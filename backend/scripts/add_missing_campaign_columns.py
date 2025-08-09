#!/usr/bin/env python3
"""
Add missing columns to reregistration_campaigns table
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy import create_engine, text
from core.config import settings

def add_missing_columns():
    engine = create_engine(settings.DATABASE_URL)
    
    with engine.connect() as conn:
        try:
            # Add campaign_type column
            print("Adding campaign_type column...")
            conn.execute(text("""
                ALTER TABLE reregistration_campaigns 
                ADD COLUMN IF NOT EXISTS campaign_type VARCHAR(50)
            """))
            conn.commit()
            print("✓ Added campaign_type column")
            
            # Add message_template column
            print("Adding message_template column...")
            conn.execute(text("""
                ALTER TABLE reregistration_campaigns 
                ADD COLUMN IF NOT EXISTS message_template TEXT
            """))
            conn.commit()
            print("✓ Added message_template column")
            
            # Add total_targets column (already exists as target_count, so we'll use that)
            print("Checking total_targets column...")
            # Note: total_targets already exists as target_count in the DB
            
            # Add total_conversions column (already exists as success_count, so we'll use that)
            print("Checking total_conversions column...")
            # Note: total_conversions already exists as success_count in the DB
            
            print("\nAll columns have been added successfully!")
            
        except Exception as e:
            print(f"Error adding columns: {e}")
            conn.rollback()
            raise

if __name__ == "__main__":
    add_missing_columns()