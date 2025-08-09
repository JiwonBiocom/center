#!/usr/bin/env python
"""
고객 데이터베이스 쿼리 직접 테스트
"""

import sys
import os
from pathlib import Path

# 프로젝트 루트 경로 추가
sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy.orm import Session
from sqlalchemy import select, text
from core.database import get_db
from models.customer import Customer
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_basic_query():
    """기본 쿼리 테스트"""
    print("🔍 기본 고객 쿼리 테스트")
    print("-" * 50)
    
    db = next(get_db())
    
    try:
        # 1. Raw SQL로 테스트
        print("1️⃣ Raw SQL 테스트")
        result = db.execute(text("SELECT COUNT(*) FROM customers"))
        count = result.scalar()
        print(f"   총 고객 수: {count}")
        
        # 2. 기본 ORM 쿼리
        print("\n2️⃣ 기본 ORM 쿼리 테스트")
        result = db.execute(select(Customer).limit(3))
        customers = result.scalars().all()
        print(f"   조회된 고객 수: {len(customers)}")
        
        for customer in customers:
            print(f"   • {customer.name} (ID: {customer.customer_id})")
        
        # 3. JSON 직렬화 테스트
        print("\n3️⃣ 고객 데이터 직렬화 테스트")
        if customers:
            customer = customers[0]
            customer_dict = {
                'customer_id': customer.customer_id,
                'name': customer.name,
                'phone': customer.phone,
                'first_visit_date': customer.first_visit_date.isoformat() if customer.first_visit_date else None,
                'region': customer.region,
                'referral_source': customer.referral_source
            }
            print(f"   첫 번째 고객 데이터: {customer_dict}")
        
        # 4. 스키마 검증
        print("\n4️⃣ Customer 테이블 스키마 확인")
        result = db.execute(text("""
            SELECT column_name, data_type, is_nullable 
            FROM information_schema.columns 
            WHERE table_name = 'customers' 
            ORDER BY ordinal_position
        """))
        columns = result.fetchall()
        
        print(f"   컬럼 수: {len(columns)}")
        for col in columns[:10]:  # 처음 10개만 표시
            print(f"   • {col[0]}: {col[1]} ({'NULL' if col[2] == 'YES' else 'NOT NULL'})")
        
        return True
        
    except Exception as e:
        print(f"❌ 쿼리 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()

def test_pydantic_serialization():
    """Pydantic 스키마 직렬화 테스트"""
    print("\n🔍 Pydantic 스키마 직렬화 테스트")
    print("-" * 50)
    
    try:
        from schemas.customer import Customer as CustomerSchema
        
        db = next(get_db())
        result = db.execute(select(Customer).limit(1))
        customer = result.scalars().first()
        
        if customer:
            # Pydantic 모델로 변환 시도
            customer_schema = CustomerSchema.from_orm(customer)
            print(f"✅ Pydantic 직렬화 성공: {customer_schema.name}")
            
            # JSON 직렬화 시도
            customer_json = customer_schema.json()
            print(f"✅ JSON 직렬화 성공 (길이: {len(customer_json)})")
            
            return True
        else:
            print("❌ 고객 데이터가 없습니다")
            return False
            
    except Exception as e:
        print(f"❌ Pydantic 직렬화 실패: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()

def main():
    """메인 실행 함수"""
    print("🧪 고객 데이터베이스 쿼리 테스트")
    print("=" * 70)
    
    success_count = 0
    
    # 1. 기본 쿼리 테스트
    if test_basic_query():
        success_count += 1
    
    # 2. Pydantic 직렬화 테스트
    if test_pydantic_serialization():
        success_count += 1
    
    print("\n" + "=" * 70)
    print(f"📊 테스트 결과: {success_count}/2 성공")
    
    if success_count == 2:
        print("✅ 모든 테스트 통과 - API 500 에러 원인이 다른 곳에 있을 수 있습니다")
    else:
        print("❌ 테스트 실패 - 스키마나 데이터베이스 연결에 문제가 있습니다")

if __name__ == "__main__":
    main()