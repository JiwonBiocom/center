"""
삭제 후 데이터 검증 스크립트
"""

import sys
import os
from datetime import datetime, date
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, func, create_engine
from decimal import Decimal

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.payment import Payment
from models.customer import Customer
from core.config import settings

# 데이터베이스 연결
DATABASE_URL = settings.DATABASE_URL or "postgresql://aibio_user:aibio_password@localhost:5432/aibio_center"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def main():
    session = SessionLocal()
    
    print("=== 데이터 정리 후 검증 ===\n")
    
    # 1. 전체 결제 건수
    total_payments = session.query(func.count(Payment.payment_id)).scalar()
    print(f"1. 전체 결제 건수: {total_payments}건")
    
    # 2. 전체 매출액
    total_revenue = session.query(func.sum(Payment.amount)).scalar() or 0
    print(f"2. 전체 매출액: {float(total_revenue):,.0f}원")
    
    # 3. 2025년 월별 매출
    print("\n3. 2025년 월별 매출:")
    for month in range(1, 7):  # 1월부터 6월까지
        start_date = date(2025, month, 1)
        if month == 12:
            end_date = date(2026, 1, 1)
        else:
            end_date = date(2025, month + 1, 1)
        
        monthly_revenue = session.query(func.sum(Payment.amount)).filter(
            Payment.payment_date >= start_date,
            Payment.payment_date < end_date
        ).scalar() or 0
        
        monthly_count = session.query(func.count(Payment.payment_id)).filter(
            Payment.payment_date >= start_date,
            Payment.payment_date < end_date
        ).scalar() or 0
        
        print(f"  - {month}월: {float(monthly_revenue):,.0f}원 ({monthly_count}건)")
    
    # 4. 특정 고객의 결제 확인 (장재미님 확인)
    print("\n4. 특정 고객 결제 확인:")
    result = session.execute(
        select(Customer, Payment)
        .join(Payment)
        .filter(Customer.name == '장재미')
        .order_by(Payment.payment_date)
    )
    
    jang_payments = list(result)
    if jang_payments:
        print(f"  - 장재미님 결제 내역:")
        for customer, payment in jang_payments:
            print(f"    · {payment.payment_date}: {float(payment.amount):,.0f}원")
    else:
        print("  - 장재미님 결제 내역 없음")
    
    # 5. 음수 금액 결제 확인
    print("\n5. 음수 금액 결제 확인:")
    negative_payments = session.query(Payment).filter(Payment.amount < 0).all()
    if negative_payments:
        print(f"  ! 음수 금액 결제 {len(negative_payments)}건 발견:")
        for payment in negative_payments:
            customer = session.get(Customer, payment.customer_id)
            print(f"    - {customer.name}: {float(payment.amount):,.0f}원 ({payment.payment_date})")
    else:
        print("  ✓ 음수 금액 결제 없음")
    
    # 6. 최근 결제 5건
    print("\n6. 최근 결제 5건:")
    recent_payments = session.query(Payment, Customer)\
        .join(Customer)\
        .order_by(Payment.payment_date.desc())\
        .limit(5)\
        .all()
    
    for payment, customer in recent_payments:
        print(f"  - {payment.payment_date}: {customer.name} - {float(payment.amount):,.0f}원")
    
    session.close()

if __name__ == "__main__":
    main()