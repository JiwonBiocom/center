#!/usr/bin/env python3
"""
서비스 타입 추가 스크립트 (Simple version)
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from core.config import settings

# Create engine directly
engine = create_engine(settings.DATABASE_URL)

def add_service_types():
    """서비스 타입 추가"""
    
    service_types = [
        {
            'service_type_id': 1,
            'service_name': '브레인',
            'description': '뇌 최적화 서비스',
            'default_duration': 30,
            'default_price': 0,
            'service_color': '#8B5CF6'  # Purple
        },
        {
            'service_type_id': 2,
            'service_name': '펄스',
            'description': '펄스 전자기장 서비스',
            'default_duration': 30,
            'default_price': 0,
            'service_color': '#3B82F6'  # Blue
        },
        {
            'service_type_id': 3,
            'service_name': '림프',
            'description': '림프 순환 개선 서비스',
            'default_duration': 30,
            'default_price': 0,
            'service_color': '#10B981'  # Green
        },
        {
            'service_type_id': 4,
            'service_name': '레드',
            'description': '레드라이트 테라피',
            'default_duration': 30,
            'default_price': 0,
            'service_color': '#EF4444'  # Red
        },
        {
            'service_type_id': 5,
            'service_name': 'AI바이크',
            'description': 'AI 바이크 운동 서비스',
            'default_duration': 20,
            'default_price': 0,
            'service_color': '#F59E0B'  # Amber
        }
    ]
    
    with engine.connect() as conn:
        # Create transaction
        trans = conn.begin()
        
        try:
            for service in service_types:
                # Check if exists
                result = conn.execute(
                    text("SELECT service_type_id FROM service_types WHERE service_type_id = :id"),
                    {'id': service['service_type_id']}
                ).first()
                
                if result:
                    print(f"Service type {service['service_name']} already exists")
                else:
                    conn.execute(
                        text("""
                            INSERT INTO service_types (
                                service_type_id, 
                                service_name, 
                                description,
                                default_duration,
                                default_price,
                                service_color
                            ) VALUES (
                                :service_type_id, 
                                :service_name, 
                                :description,
                                :default_duration,
                                :default_price,
                                :service_color
                            )
                        """),
                        service
                    )
                    print(f"Added service type: {service['service_name']}")
            
            trans.commit()
            print("All service types added successfully!")
            
        except Exception as e:
            trans.rollback()
            print(f"Error adding service types: {e}")
            raise

if __name__ == "__main__":
    add_service_types()