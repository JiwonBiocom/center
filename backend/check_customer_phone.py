#!/usr/bin/env python
"""전태준 고객 정보 및 전화번호 확인"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from sqlalchemy.orm import Session
from core.database import get_db
from models.customer import Customer

def check_customer_phone():
    db = next(get_db())
    
    # 전태준 고객 찾기
    customer = db.query(Customer).filter(Customer.name == "전태준").first()
    
    if customer:
        print(f"고객 정보:")
        print(f"  - ID: {customer.customer_id}")
        print(f"  - 이름: {customer.name}")
        print(f"  - 전화번호: {customer.phone}")
        print(f"  - 이메일: {customer.email}")
        print(f"  - 주소: {customer.address}")
        
        if not customer.phone:
            print("\n❌ 전화번호가 없습니다!")
        else:
            print(f"\n전화번호 형식: '{customer.phone}'")
            print(f"전화번호 길이: {len(customer.phone) if customer.phone else 0}")
    else:
        print("전태준 고객을 찾을 수 없습니다.")
    
    db.close()

if __name__ == "__main__":
    check_customer_phone()