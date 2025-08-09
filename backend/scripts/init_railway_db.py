"""
Railway PostgreSQL 초기화 스크립트
- 모든 테이블 생성
- 초기 관리자 계정 생성
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine
from core.database import Base, get_db
from core.auth import get_password_hash
from models.user import User
from models.customer import Customer
from models.service import Service, ServiceUsage, ServiceType
from models.payment import Payment
from models.package import Package, PackagePurchase
from models.lead_management import Lead, LeadManagement, Campaign, CampaignTarget
from models.notification import Notification, NotificationTemplate
from models.reservation import Reservation
from models.kit import Kit
from models.customer_extended import Consultation
from models.staff_schedule import StaffSchedule
from models.inbody import InBodyData
from models.system import SystemSetting, AuditLog

def init_database():
    """데이터베이스 초기화"""
    # DATABASE_URL from environment
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("ERROR: DATABASE_URL not found in environment variables")
        return False
    
    try:
        # Create engine
        engine = create_engine(database_url)
        
        # Create all tables
        print("Creating database tables...")
        Base.metadata.create_all(bind=engine)
        print("✓ All tables created successfully")
        
        # Create initial admin user
        from sqlalchemy.orm import Session
        with Session(engine) as db:
            # Check if admin already exists
            existing_admin = db.query(User).filter(User.email == "admin@aibio.kr").first()
            if not existing_admin:
                admin_user = User(
                    email="admin@aibio.kr",
                    password_hash=get_password_hash("admin123"),
                    name="관리자",
                    role="admin",
                    is_active=True
                )
                db.add(admin_user)
                db.commit()
                print("✓ Admin user created (admin@aibio.kr / admin123)")
            else:
                print("✓ Admin user already exists")
        
        return True
        
    except Exception as e:
        print(f"ERROR: Failed to initialize database: {e}")
        return False

if __name__ == "__main__":
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    success = init_database()
    if success:
        print("\n✅ Database initialization completed successfully!")
    else:
        print("\n❌ Database initialization failed!")
        sys.exit(1)