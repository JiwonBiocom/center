#!/usr/bin/env python3
"""
고객의 last_visit_date 수정 스크립트
first_visit_date는 있지만 last_visit_date가 없는 고객들을 찾아서 수정
"""
import os
import sys
from datetime import datetime
from pathlib import Path

# 프로젝트 루트 경로 추가
sys.path.append(str(Path(__file__).parent.parent))

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from models.customer import Customer

# 환경 변수 로드
load_dotenv()

# 데이터베이스 연결
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def fix_last_visit_dates():
    """last_visit_date가 없는 고객들 수정"""
    db = SessionLocal()
    
    try:
        print("=" * 80)
        print("고객 last_visit_date 수정 스크립트")
        print("=" * 80)
        
        # 1. last_visit_date가 없는 고객 찾기
        print("\n1. first_visit_date는 있지만 last_visit_date가 없는 고객 찾기")
        print("-" * 40)
        
        result = db.execute(text("""
            SELECT 
                customer_id, name, phone,
                first_visit_date, last_visit_date, customer_status,
                created_at, updated_at
            FROM customers 
            WHERE first_visit_date IS NOT NULL 
            AND last_visit_date IS NULL
            ORDER BY first_visit_date DESC
        """))
        
        customers_to_fix = result.fetchall()
        
        if not customers_to_fix:
            print("✅ last_visit_date가 없는 고객이 없습니다.")
            return
        
        print(f"\n총 {len(customers_to_fix)}명의 고객이 발견되었습니다:")
        print(f"{'ID':<10} {'이름':<10} {'전화번호':<15} {'첫방문일':<12} {'상태':<10}")
        print("-" * 60)
        
        for customer in customers_to_fix[:50]:  # 처음 50개만 표시
            phone = customer.phone or "없음"
            print(f"{customer.customer_id:<10} {customer.name:<10} {phone:<15} "
                  f"{str(customer.first_visit_date):<12} {customer.customer_status:<10}")
        
        # 2. 자동으로 업데이트 진행
        print("\n2. last_visit_date를 first_visit_date와 동일하게 설정합니다.")
        print("(첫 방문이 마지막 방문이라고 가정)")
        
        # 3. last_visit_date 업데이트
        print("\n3. last_visit_date 업데이트 중...")
        print("-" * 40)
        
        updated_count = 0
        for customer in customers_to_fix:
            # ORM으로 고객 조회 및 업데이트
            cust_obj = db.query(Customer).filter(
                Customer.customer_id == customer.customer_id
            ).first()
            
            if cust_obj:
                # last_visit_date를 first_visit_date로 설정
                cust_obj.last_visit_date = cust_obj.first_visit_date
                
                # 상태 업데이트
                old_status = cust_obj.customer_status
                new_status = cust_obj.update_customer_status()
                
                updated_count += 1
                print(f"✅ {cust_obj.name} - last_visit_date: {cust_obj.last_visit_date}, "
                      f"상태: {old_status} -> {new_status}")
        
        # 변경사항 커밋
        db.commit()
        print(f"\n✅ 총 {updated_count}명의 고객 정보가 업데이트되었습니다.")
        
        # 4. 업데이트 결과 확인
        print("\n4. 업데이트 결과 확인")
        print("-" * 40)
        
        # 이혜정 고객 재확인
        lee_customer = db.query(Customer).filter(Customer.name == "이혜정").first()
        if lee_customer:
            print(f"\n이혜정 고객 최종 상태:")
            print(f"  - 첫 방문일: {lee_customer.first_visit_date}")
            print(f"  - 마지막 방문일: {lee_customer.last_visit_date}")
            print(f"  - 고객 상태: {lee_customer.customer_status}")
            
            # 경과일 계산
            if lee_customer.last_visit_date:
                days_since = (datetime.now().date() - lee_customer.last_visit_date).days
                print(f"  - 마지막 방문 후 경과일: {days_since}일")
        
        # 전체 상태 통계
        result = db.execute(text("""
            SELECT 
                customer_status,
                COUNT(*) as count
            FROM customers
            WHERE last_visit_date IS NOT NULL
            GROUP BY customer_status
            ORDER BY customer_status
        """))
        
        status_stats = result.fetchall()
        
        print("\n전체 고객 상태 통계:")
        for stat in status_stats:
            print(f"  - {stat.customer_status}: {stat.count}명")
        
    except Exception as e:
        print(f"\n❌ 오류 발생: {str(e)}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    fix_last_visit_dates()