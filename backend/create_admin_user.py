import os
import sys
from pathlib import Path

# Add parent directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from core.database import SessionLocal
from models.user import User
from core.auth import get_password_hash
from datetime import datetime

def create_admin_user():
    """Create admin user"""
    db = SessionLocal()
    
    try:
        # Check if admin already exists
        existing_admin = db.query(User).filter(User.email == "admin@aibio.com").first()
        
        if existing_admin:
            print("Admin user already exists!")
            print(f"  - Email: {existing_admin.email}")
            print(f"  - Name: {existing_admin.name}")
            return
        
        # Create new admin user
        admin_user = User(
            email="admin@aibio.com",
            password_hash=get_password_hash("admin123"),
            name="Admin",
            role="admin",
            is_active=True
        )
        
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        
        print("Admin user created successfully!")
        print(f"  - ID: {admin_user.user_id}")
        print(f"  - Email: {admin_user.email}")
        print(f"  - Name: {admin_user.name}")
        print(f"  - Role: {admin_user.role}")
        print(f"  - Password: admin123")
        
    except Exception as e:
        print(f"Error creating admin user: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_admin_user()