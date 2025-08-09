import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.database import SessionLocal
from models.service import ServiceType
from datetime import datetime

def add_service_types():
    db = SessionLocal()
    
    service_types = [
        {
            "service_name": "IV 치료",
            "default_duration": 60,
            "default_price": 150000,
            "service_color": "#3B82F6",  # Blue
            "description": "정맥 주사를 통한 영양소 공급"
        },
        {
            "service_name": "수액 치료",
            "default_duration": 90,
            "default_price": 200000,
            "service_color": "#10B981",  # Green
            "description": "맞춤형 수액 치료"
        },
        {
            "service_name": "킬레이션",
            "default_duration": 120,
            "default_price": 300000,
            "service_color": "#F59E0B",  # Yellow
            "description": "중금속 해독 치료"
        },
        {
            "service_name": "줄기세포",
            "default_duration": 60,
            "default_price": 500000,
            "service_color": "#EF4444",  # Red
            "description": "줄기세포 치료"
        },
        {
            "service_name": "상담",
            "default_duration": 30,
            "default_price": 50000,
            "service_color": "#8B5CF6",  # Purple
            "description": "건강 상담"
        }
    ]
    
    try:
        for service_data in service_types:
            # Check if service type already exists
            existing = db.query(ServiceType).filter_by(service_name=service_data["service_name"]).first()
            if not existing:
                service_type = ServiceType(**service_data)
                db.add(service_type)
                print(f"Added service type: {service_data['service_name']}")
            else:
                print(f"Service type already exists: {service_data['service_name']}")
        
        db.commit()
        print("Service types added successfully!")
        
    except Exception as e:
        db.rollback()
        print(f"Error adding service types: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    add_service_types()