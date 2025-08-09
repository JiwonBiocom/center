#!/usr/bin/env python3
"""
고객 상태 확인 스크립트
이혜정 고객의 휴면 상태 문제 조사
"""
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

# 프로젝트 루트 경로 추가
sys.path.append(str(Path(__file__).parent.parent))

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from models.customer import Customer
from core.database import Base

# 환경 변수 로드
load_dotenv()

# 데이터베이스 연결
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def check_customer_status():
    """이혜정 고객 및 최근 방문 고객들의 상태 확인"""
    db = SessionLocal()
    
    try:
        print("=" * 80)
        print("고객 상태 확인 스크립트")
        print("=" * 80)
        
        # 1. 이혜정 고객 데이터 확인
        print("\n1. 이혜정 고객 데이터 확인")
        print("-" * 40)
        
        result = db.execute(text("""
            SELECT 
                customer_id, name, phone, email,
                first_visit_date, last_visit_date,
                customer_status, created_at, updated_at,
                CURRENT_DATE as today,
                CURRENT_DATE - last_visit_date as days_since_visit
            FROM customers 
            WHERE name = '이혜정'
        """))
        
        lee_customers = result.fetchall()
        
        if not lee_customers:
            print("❌ 이혜정 고객을 찾을 수 없습니다.")
        else:
            for customer in lee_customers:
                print(f"ID: {customer.customer_id}")
                print(f"이름: {customer.name}")
                print(f"전화번호: {customer.phone}")
                print(f"이메일: {customer.email}")
                print(f"첫 방문일: {customer.first_visit_date}")
                print(f"마지막 방문일: {customer.last_visit_date}")
                print(f"고객 상태: {customer.customer_status}")
                print(f"오늘 날짜: {customer.today}")
                print(f"마지막 방문 후 경과일: {customer.days_since_visit}일")
                print(f"생성일: {customer.created_at}")
                print(f"수정일: {customer.updated_at}")
                print()
        
        # 2. 고객 상태 업데이트 로직 확인
        print("\n2. 고객 상태 업데이트 로직 분석")
        print("-" * 40)
        
        # Customer 모델의 update_customer_status 메서드 로직 재현
        today = datetime.now().date()
        print(f"오늘 날짜: {today}")
        print(f"Active 기준: 30일 이내 방문")
        print(f"Inactive 기준: 31-90일 사이 방문")
        print(f"Dormant 기준: 90일 초과 미방문")
        
        if lee_customers:
            for customer in lee_customers:
                if customer.last_visit_date:
                    days_since = (today - customer.last_visit_date).days
                    print(f"\n{customer.name} ({customer.customer_id}) 분석:")
                    print(f"  - 마지막 방문: {customer.last_visit_date}")
                    print(f"  - 경과일: {days_since}일")
                    
                    if days_since <= 30:
                        expected_status = "active"
                    elif days_since <= 90:
                        expected_status = "inactive"
                    else:
                        expected_status = "dormant"
                    
                    print(f"  - 예상 상태: {expected_status}")
                    print(f"  - 실제 상태: {customer.customer_status}")
                    
                    if expected_status != customer.customer_status:
                        print(f"  ⚠️  상태 불일치!")
        
        # 3. 최근 방문 고객들의 상태 확인
        print("\n3. 최근 방문 고객들의 상태 확인 (2025년 5월 방문자)")
        print("-" * 40)
        
        result = db.execute(text("""
            SELECT 
                customer_id, name, phone,
                first_visit_date, last_visit_date,
                customer_status,
                CURRENT_DATE - last_visit_date as days_since_visit
            FROM customers 
            WHERE last_visit_date >= '2025-05-01'
            ORDER BY last_visit_date DESC
            LIMIT 20
        """))
        
        recent_customers = result.fetchall()
        
        if recent_customers:
            print(f"\n총 {len(recent_customers)}명의 최근 방문 고객:")
            print(f"{'이름':<10} {'전화번호':<15} {'마지막방문':<12} {'경과일':<8} {'상태':<8}")
            print("-" * 60)
            
            for customer in recent_customers:
                print(f"{customer.name:<10} {customer.phone:<15} {str(customer.last_visit_date):<12} "
                      f"{str(customer.days_since_visit)+'일':<8} {customer.customer_status:<8}")
        
        # 4. 상태별 고객 수 통계
        print("\n4. 고객 상태별 통계")
        print("-" * 40)
        
        result = db.execute(text("""
            SELECT 
                customer_status,
                COUNT(*) as count,
                AVG(CURRENT_DATE - last_visit_date) as avg_days_since_visit
            FROM customers
            WHERE last_visit_date IS NOT NULL
            GROUP BY customer_status
            ORDER BY customer_status
        """))
        
        status_stats = result.fetchall()
        
        for stat in status_stats:
            print(f"{stat.customer_status}: {stat.count}명 (평균 {stat.avg_days_since_visit:.1f}일 경과)")
        
        # 5. 날짜 관련 문제 가능성 확인
        print("\n5. 시스템 날짜 및 타임존 확인")
        print("-" * 40)
        
        result = db.execute(text("""
            SELECT 
                CURRENT_DATE as db_date,
                CURRENT_TIMESTAMP as db_timestamp,
                CURRENT_TIMESTAMP AT TIME ZONE 'Asia/Seoul' as korea_time
        """))
        
        date_info = result.fetchone()
        print(f"DB 현재 날짜: {date_info.db_date}")
        print(f"DB 현재 시각: {date_info.db_timestamp}")
        print(f"한국 시각: {date_info.korea_time}")
        
        # Python 시스템 날짜
        print(f"\nPython 현재 날짜: {datetime.now().date()}")
        print(f"Python 현재 시각: {datetime.now()}")
        
        # 6. update_customer_status 실행 테스트
        print("\n6. update_customer_status 메서드 실행 테스트")
        print("-" * 40)
        
        if lee_customers:
            # ORM으로 이혜정 고객 조회
            lee_customer_orm = db.query(Customer).filter(Customer.name == "이혜정").first()
            if lee_customer_orm:
                print(f"ORM 조회 - 이혜정 고객 상태 (업데이트 전): {lee_customer_orm.customer_status}")
                print(f"  - 마지막 방문일: {lee_customer_orm.last_visit_date}")
                print(f"  - 첫 방문일: {lee_customer_orm.first_visit_date}")
                
                # update_customer_status 메서드 실행
                old_status = lee_customer_orm.customer_status
                new_status = lee_customer_orm.update_customer_status()
                db.commit()
                
                # 재조회
                db.refresh(lee_customer_orm)
                print(f"ORM 조회 - 이혜정 고객 상태 (업데이트 후): {lee_customer_orm.customer_status}")
                print(f"  - 메서드 반환값: {new_status}")
                if old_status != new_status:
                    print(f"  ✅ 상태가 {old_status}에서 {new_status}로 변경되었습니다.")
        
    except Exception as e:
        print(f"\n❌ 오류 발생: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    check_customer_status()