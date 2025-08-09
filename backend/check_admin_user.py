import os
import sys
from pathlib import Path

# Add parent directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from core.database import SessionLocal
from models.user import User
from core.auth import verify_password, get_password_hash
from sqlalchemy import select

def check_admin_user():
    """Check if admin user exists and verify password"""
    db = SessionLocal()
    
    try:
        # Check all users
        print("=== Checking all users in database ===")
        users = db.query(User).all()
        
        if not users:
            print("No users found in database!")
        else:
            print(f"Found {len(users)} users:")
            for user in users:
                print(f"  - Name: {user.name}, Email: {user.email}, Role: {user.role}, Active: {user.is_active}")
        
        # Check specifically for admin user
        print("\n=== Checking for admin user ===")
        admin = db.query(User).filter(User.email == "admin@aibio.com").first()
        
        if admin:
            print(f"Admin user found:")
            print(f"  - ID: {admin.user_id}")
            print(f"  - Name: {admin.name}")
            print(f"  - Email: {admin.email}")
            print(f"  - Role: {admin.role}")
            print(f"  - Active: {admin.is_active}")
            print(f"  - Password hash: {admin.password_hash[:20]}...")
            
            # Test password verification
            test_password = "admin123"
            is_valid = verify_password(test_password, admin.password_hash)
            print(f"\n  - Password 'admin123' verification: {is_valid}")
            
            # Show what the correct hash should be
            correct_hash = get_password_hash(test_password)
            print(f"  - Expected hash for 'admin123': {correct_hash[:20]}...")
            
        else:
            print("Admin user NOT found!")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    check_admin_user()