from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import date, datetime
from core.config import settings
from models.service import ServiceUsage, ServiceType
from models.customer import Customer
from models.package import PackagePurchase

# 데이터베이스 연결
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def add_sample_service_usage():
    """샘플 서비스 이용 데이터 추가"""
    db = SessionLocal()
    
    try:
        # 기존 고객 조회
        customers = db.query(Customer).limit(3).all()
        if not customers:
            print("No customers found. Please add customers first.")
            return
        
        # 기존 서비스 타입 조회
        service_types = db.query(ServiceType).all()
        if not service_types:
            print("No service types found. Please add service types first.")
            return
        
        print(f"Found {len(customers)} customers and {len(service_types)} service types")
        
        # 2025년 1월 샘플 데이터 추가
        sample_usages = [
            {
                "customer_id": customers[0].customer_id,
                "service_date": date(2025, 1, 2),
                "service_type_id": service_types[0].service_type_id,
                "session_details": "초기 상담 및 영양 분석",
                "session_number": 1,
                "created_by": "admin"
            },
            {
                "customer_id": customers[0].customer_id,
                "service_date": date(2025, 1, 5),
                "service_type_id": service_types[1].service_type_id if len(service_types) > 1 else service_types[0].service_type_id,
                "session_details": "첫 번째 IV 테라피 세션",
                "session_number": 1,
                "created_by": "admin"
            },
            {
                "customer_id": customers[1].customer_id if len(customers) > 1 else customers[0].customer_id,
                "service_date": date(2025, 1, 3),
                "service_type_id": service_types[0].service_type_id,
                "session_details": "영양 상담",
                "session_number": 1,
                "created_by": "admin"
            },
            {
                "customer_id": customers[1].customer_id if len(customers) > 1 else customers[0].customer_id,
                "service_date": date(2025, 1, 7),
                "service_type_id": service_types[2].service_type_id if len(service_types) > 2 else service_types[0].service_type_id,
                "session_details": "크라이오 테라피 체험",
                "session_number": 1,
                "created_by": "admin"
            },
            {
                "customer_id": customers[2].customer_id if len(customers) > 2 else customers[0].customer_id,
                "service_date": date(2025, 1, 4),
                "service_type_id": service_types[0].service_type_id,
                "session_details": "건강 검진 상담",
                "session_number": 1,
                "created_by": "admin"
            }
        ]
        
        # 데이터 추가
        for usage_data in sample_usages:
            usage = ServiceUsage(**usage_data)
            db.add(usage)
        
        db.commit()
        print(f"Successfully added {len(sample_usages)} service usage records for January 2025")
        
        # 추가된 데이터 확인
        january_count = db.query(ServiceUsage).filter(
            ServiceUsage.service_date >= date(2025, 1, 1),
            ServiceUsage.service_date < date(2025, 2, 1)
        ).count()
        
        print(f"Total service usage records in January 2025: {january_count}")
        
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    add_sample_service_usage()