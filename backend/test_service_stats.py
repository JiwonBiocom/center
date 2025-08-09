import asyncio
import sys
from datetime import date
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from core.config import settings
from api.v1.services import get_service_stats
from models.user import User

# 데이터베이스 연결
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def test_service_stats():
    """서비스 통계 API 테스트"""
    db = SessionLocal()
    
    try:
        # 임시 사용자 객체 생성 (테스트용)
        current_user = User(user_id=1, name="test", email="test@test.com", password_hash="dummy")
        
        # 2025년 1월 통계 조회
        stats = get_service_stats(
            year=2025,
            month=1,
            db=db,
            current_user=current_user
        )
        
        print("Service Stats for 2025-01:")
        print(f"Total Services: {stats['total_services']}")
        print(f"Unique Customers: {stats['unique_customers']}")
        print(f"Most Popular Service: {stats['most_popular_service']}")
        print(f"Total Revenue: {stats['total_revenue']:,}원")
        print(f"Average Daily Services: {stats['average_daily_services']}")
        
        return True
        
    except Exception as e:
        print(f"Error occurred: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        db.close()

if __name__ == "__main__":
    success = test_service_stats()
    sys.exit(0 if success else 1)