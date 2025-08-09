import asyncio
import os
import sys
from pathlib import Path

# Add backend directory to path
sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import AsyncSession
from core.database import engine, Base, AsyncSessionLocal
from models import *  # Import all models to register them

async def init_db():
    """Initialize database with tables"""
    import os
    
    # Safety check - prevent dropping tables in production
    environment = os.getenv('ENVIRONMENT', 'development')
    
    async with engine.begin() as conn:
        if environment == 'production':
            print("WARNING: Cannot drop tables in production environment!")
            print("Only creating new tables if they don't exist...")
        else:
            # Require explicit confirmation for dropping tables
            confirm = input("\n⚠️  WARNING: This will DROP ALL TABLES and DELETE ALL DATA! ⚠️\nType 'yes' to confirm: ")
            if confirm.lower() == 'yes':
                # Drop all tables (for development only)
                await conn.run_sync(Base.metadata.drop_all)
                print("All tables dropped.")
            else:
                print("Operation cancelled. Tables not dropped.")
        
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)
        print("Database tables created successfully!")
        
    # Add initial service types
    async with AsyncSessionLocal() as db:
        from models.service import ServiceType
        
        service_types = [
            ServiceType(service_name="brain", description="브레인 서비스"),
            ServiceType(service_name="pulse", description="펄스 서비스"),
            ServiceType(service_name="lymph", description="림프 서비스"),
            ServiceType(service_name="red", description="레드 서비스"),
        ]
        
        for service_type in service_types:
            db.add(service_type)
        
        await db.commit()
        print("Initial data inserted successfully!")

if __name__ == "__main__":
    asyncio.run(init_db())