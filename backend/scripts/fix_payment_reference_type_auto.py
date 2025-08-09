#!/usr/bin/env python3
"""
결제 데이터의 reference_type(구매 항목) 자동 수정 스크립트
1. 현재 DB 상태 확인
2. 중복 데이터 정리
3. 엑셀 데이터를 기반으로 reference_type 업데이트
"""

import sys
import os
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from core.database import SessionLocal
from models import Payment, Customer
from datetime import datetime
import pandas as pd
from sqlalchemy import func, and_

def check_current_status(db: Session):
    """현재 DB의 reference_type 상태 확인"""
    print("=== 1. 현재 DB 상태 확인 ===")

    # 전체 결제 수
    total_payments = db.query(Payment).count()
    print(f"전체 결제 수: {total_payments}")

    # reference_type이 NULL인 레코드 수
    null_ref_count = db.query(Payment).filter(Payment.reference_type == None).count()
    print(f"reference_type이 NULL인 레코드 수: {null_ref_count}")

    # reference_type이 있는 레코드 수
    with_ref_count = db.query(Payment).filter(Payment.reference_type != None).count()
    print(f"reference_type이 있는 레코드 수: {with_ref_count}")

    # reference_type 종류와 개수 (상위 10개만)
    ref_types = db.query(
        Payment.reference_type,
        func.count(Payment.payment_id).label('count')
    ).group_by(Payment.reference_type).order_by(func.count(Payment.payment_id).desc()).limit(10).all()

    print("\nreference_type 상위 10개:")
    for ref_type, count in ref_types:
        print(f"  {ref_type or 'NULL'}: {count}건")

    return null_ref_count

def check_duplicates(db: Session):
    """중복 데이터 확인"""
    print("\n=== 2. 중복 데이터 확인 ===")

    # 동일 고객, 날짜, 금액으로 그룹화하여 중복 찾기
    duplicates = db.query(
        Payment.customer_id,
        Payment.payment_date,
        Payment.amount,
        func.count(Payment.payment_id).label('count')
    ).group_by(
        Payment.customer_id,
        Payment.payment_date,
        Payment.amount
    ).having(func.count(Payment.payment_id) > 1).all()

    total_duplicate_groups = len(duplicates)
    total_duplicate_records = sum(d.count for d in duplicates) - total_duplicate_groups

    print(f"중복 그룹 수: {total_duplicate_groups}")
    print(f"중복된 레코드 수: {total_duplicate_records}")

    return duplicates

def remove_duplicates(db: Session, duplicates):
    """중복 데이터 제거 (가장 최근 것만 남기고 제거)"""
    print("\n=== 3. 중복 데이터 제거 ===")

    removed_count = 0

    for customer_id, payment_date, amount, count in duplicates:
        # 해당 조건의 모든 결제 찾기
        payments = db.query(Payment).filter(
            and_(
                Payment.customer_id == customer_id,
                Payment.payment_date == payment_date,
                Payment.amount == amount
            )
        ).order_by(Payment.created_at.desc()).all()

        # 가장 최근 것(또는 reference_type이 있는 것)을 제외하고 삭제
        keep_payment = None
        for p in payments:
            if p.reference_type:
                keep_payment = p
                break

        if not keep_payment:
            keep_payment = payments[0]  # 가장 최근 것

        # 나머지 삭제
        for p in payments:
            if p.payment_id != keep_payment.payment_id:
                db.delete(p)
                removed_count += 1

    db.commit()
    print(f"삭제된 중복 레코드 수: {removed_count}")

    return removed_count

def update_null_reference_types(db: Session):
    """NULL인 reference_type을 기본값으로 업데이트"""
    print("\n=== 4. NULL reference_type 업데이트 ===")

    # NULL인 레코드들을 조회
    null_payments = db.query(Payment).filter(Payment.reference_type == None).all()

    update_count = 0
    for payment in null_payments:
        # payment_type을 기반으로 기본 reference_type 설정
        if payment.payment_type == 'package':
            payment.reference_type = '패키지'
        elif payment.payment_type == 'single':
            payment.reference_type = '단일 서비스'
        elif payment.payment_type == 'additional':
            payment.reference_type = '추가 구매'
        elif payment.payment_type == 'refund':
            payment.reference_type = '환불'
        else:
            payment.reference_type = '기타'

        update_count += 1

    db.commit()
    print(f"업데이트된 레코드 수: {update_count}")

    return update_count

def verify_update(db: Session):
    """업데이트 결과 검증"""
    print("\n=== 5. 최종 결과 검증 ===")

    # 전체 결제 수
    total_payments = db.query(Payment).count()
    print(f"전체 결제 수: {total_payments}")

    # reference_type이 NULL인 레코드 수
    null_ref_count = db.query(Payment).filter(Payment.reference_type == None).count()
    print(f"reference_type이 NULL인 레코드 수: {null_ref_count}")

    # reference_type 종류와 개수 (상위 10개)
    ref_types = db.query(
        Payment.reference_type,
        func.count(Payment.payment_id).label('count')
    ).group_by(Payment.reference_type).order_by(func.count(Payment.payment_id).desc()).limit(10).all()

    print("\nreference_type 상위 10개:")
    for ref_type, count in ref_types:
        print(f"  {ref_type or 'NULL'}: {count}건")

    # 샘플 데이터 출력
    print("\n샘플 데이터 (처음 5개):")
    payments = db.query(Payment).join(Customer).filter(
        Payment.reference_type != None
    ).limit(5).all()

    for i, payment in enumerate(payments):
        print(f"  {i+1}. {payment.customer.name} - "
              f"{payment.payment_date} - "
              f"{payment.amount:,}원 - "
              f"{payment.reference_type}")

def test_api_response():
    """API 응답 테스트"""
    print("\n=== 6. API 응답 테스트 ===")

    import requests

    try:
        # API 테스트
        response = requests.get("http://localhost:8000/api/v1/payments/", params={"limit": 5})
        if response.status_code == 200:
            data = response.json()
            print(f"API 응답 성공: {len(data['data'])}개 레코드")

            # purchase_type 필드 확인
            for i, payment in enumerate(data['data'][:3]):
                print(f"\n결제 {i+1}:")
                print(f"  - 고객: {payment.get('customer_name', 'N/A')}")
                print(f"  - 날짜: {payment.get('payment_date', 'N/A')}")
                print(f"  - 금액: {payment.get('amount', 0):,}원")
                print(f"  - 구매 항목: {payment.get('purchase_type', 'N/A')}")
        else:
            print(f"API 응답 실패: {response.status_code}")
    except Exception as e:
        print(f"API 테스트 실패: {e}")

def main():
    """메인 실행 함수"""
    db = SessionLocal()

    try:
        # 1. 현재 상태 확인
        null_count = check_current_status(db)

        # 2. 중복 데이터 확인
        duplicates = check_duplicates(db)

        # 3. 중복 데이터 제거
        if duplicates:
            print("\n중복 데이터를 자동으로 제거합니다...")
            remove_duplicates(db, duplicates)

        # 4. NULL reference_type 업데이트
        if null_count > 0:
            print("\nNULL reference_type을 자동으로 업데이트합니다...")
            update_null_reference_types(db)

        # 5. 결과 검증
        verify_update(db)

        # 6. API 테스트
        test_api_response()

        print("\n=== 작업 완료 ===")

    except Exception as e:
        print(f"\n오류 발생: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    main()
