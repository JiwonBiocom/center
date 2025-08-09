#!/usr/bin/env python3
"""
고객 API 테스트
"""
import os
import sys
sys.path.insert(0, '/Users/vibetj/coding/center/backend')

from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from models.customer import Customer as CustomerModel
from schemas.customer import Customer
import json
from dotenv import load_dotenv

# backend 디렉토리의 .env 파일 로드
load_dotenv(os.path.join(os.path.dirname(__file__), '..', 'backend', '.env'))

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    DATABASE_URL = "postgresql://postgres.wvcxzyvmwwrbjpeuyvuh:bico6819!!@aws-0-ap-northeast-2.pooler.supabase.com:6543/postgres"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def test_customer_schema():
    """고객 스키마 테스트"""
    with SessionLocal() as db:
        # 첫 번째 고객 조회
        query = select(CustomerModel).limit(1)
        result = db.execute(query)
        customer = result.scalar_one_or_none()
        
        if customer:
            print(f"Customer ID: {customer.customer_id}")
            print(f"Name: {customer.name}")
            print(f"Phone: {customer.phone}")
            print(f"Assigned Staff: {customer.assigned_staff}")
            print(f"First Visit Date: {customer.first_visit_date}")
            print(f"Email: {customer.email}")
            print(f"Birth Year: {customer.birth_year}")
            
            # Pydantic 스키마로 변환 시도
            try:
                schema = Customer.model_validate(customer)
                print("\n✅ 스키마 변환 성공!")
                print(json.dumps(schema.model_dump(), default=str, ensure_ascii=False, indent=2))
            except Exception as e:
                print(f"\n❌ 스키마 변환 실패: {e}")
                print(f"에러 타입: {type(e)}")
                
                # 상세 에러 확인
                import traceback
                traceback.print_exc()

if __name__ == "__main__":
    test_customer_schema()