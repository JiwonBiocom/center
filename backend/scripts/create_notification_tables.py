"""알림 테이블 생성 스크립트"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine
from core.config import settings
from core.database import Base
from models.notification import Notification, NotificationSettings

def create_notification_tables():
    """알림 관련 테이블 생성"""
    print("알림 테이블 생성 중...")
    
    # 엔진 생성
    engine = create_engine(settings.DATABASE_URL)
    
    # 테이블 생성
    Base.metadata.create_all(bind=engine, tables=[
        Notification.__table__,
        NotificationSettings.__table__
    ])
    
    print("✅ 알림 테이블 생성 완료!")
    print("  - notifications")
    print("  - notification_settings")

if __name__ == "__main__":
    create_notification_tables()