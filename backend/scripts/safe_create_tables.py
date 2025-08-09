"""안전한 테이블 생성 스크립트 - 기존 데이터를 삭제하지 않음"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.database import engine, Base
from models import user, customer, service, payment, package, lead, kit, audit, notification, reservation, system

# Create tables without dropping existing ones
Base.metadata.create_all(bind=engine)
print("✅ Database tables created successfully (existing data preserved)!")