#!/usr/bin/env python3
"""
최미라 고객 서비스 이용 내역 확인
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from core.database import SessionLocal

def verify_choi_service():
    db = SessionLocal()
    
    # 최미라 고객 ID 조회
    customer = db.execute(
        text("SELECT customer_id FROM customers WHERE name = '최미라'")
    ).first()
    
    if not customer:
        print("최미라 고객을 찾을 수 없습니다.")
        return
    
    customer_id = customer[0]
    print(f"최미라 고객 ID: {customer_id}")
    
    # 서비스 이용 내역 조회
    result = db.execute(text("""
        SELECT su.*, st.service_name
        FROM service_usage su
        JOIN service_types st ON su.service_type_id = st.service_type_id
        WHERE su.customer_id = :customer_id
        ORDER BY su.service_date
    """), {'customer_id': customer_id}).fetchall()
    
    print(f"\n최미라 서비스 이용 내역: {len(result)}건")
    for row in result:
        print(f"  - {row.service_date}: {row.service_name} - {row.session_details}")
    
    db.close()

if __name__ == "__main__":
    verify_choi_service()