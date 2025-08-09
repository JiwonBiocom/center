#!/usr/bin/env python3
"""
결제 데이터의 reference_type 상태 확인 스크립트
"""

import sys
import os
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from core.database import SessionLocal
from models import Payment, Customer
from sqlalchemy import func

def check_payment_status(db: Session):
    """결제 데이터 상태 확인"""
    print("=== 결제 데이터 reference_type 현황 ===\n")

    # 전체 결제 수
    total_payments = db.query(Payment).count()
    print(f"전체 결제 수: {total_payments:,}건")

    # reference_type이 NULL인 레코드 수
    null_ref_count = db.query(Payment).filter(Payment.reference_type == None).count()
    print(f"reference_type이 NULL인 레코드: {null_ref_count}건")

    # reference_type이 있는 레코드 수
    with_ref_count = db.query(Payment).filter(Payment.reference_type != None).count()
    print(f"reference_type이 있는 레코드: {with_ref_count:,}건")

    print(f"\n완료율: {(with_ref_count/total_payments*100):.1f}%")

    # reference_type 분포 (상위 20개)
    print("\n=== 구매 항목별 분포 (상위 20개) ===")
    ref_types = db.query(
        Payment.reference_type,
        func.count(Payment.payment_id).label('count')
    ).filter(
        Payment.reference_type != None
    ).group_by(
        Payment.reference_type
    ).order_by(
        func.count(Payment.payment_id).desc()
    ).limit(20).all()

    for i, (ref_type, count) in enumerate(ref_types):
        print(f"{i+1:2d}. {ref_type}: {count:,}건")

    # 최근 결제 샘플
    print("\n=== 최근 결제 샘플 (10건) ===")
    recent_payments = db.query(Payment).join(Customer).order_by(
        Payment.payment_date.desc(),
        Payment.created_at.desc()
    ).limit(10).all()

    for i, payment in enumerate(recent_payments):
        print(f"\n{i+1}. {payment.customer.name}")
        print(f"   날짜: {payment.payment_date}")
        print(f"   금액: {payment.amount:,}원")
        print(f"   구매 항목: {payment.reference_type or 'N/A'}")
        print(f"   결제 방법: {payment.payment_method}")
        print(f"   결제 유형: {payment.payment_type}")

def main():
    """메인 실행 함수"""
    db = SessionLocal()

    try:
        check_payment_status(db)
    except Exception as e:
        print(f"\n오류 발생: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    main()
