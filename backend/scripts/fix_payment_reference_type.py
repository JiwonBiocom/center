#!/usr/bin/env python3
"""
결제 데이터의 reference_type(구매 항목) 수정 스크립트
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

    # reference_type 종류와 개수
    ref_types = db.query(
        Payment.reference_type,
        func.count(Payment.payment_id).label('count')
    ).group_by(Payment.reference_type).all()

    print("\nreference_type 분포:")
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

    # 중복 상세 정보 출력 (처음 5개만)
    if duplicates:
        print("\n중복 예시 (처음 5개):")
        for i, (customer_id, payment_date, amount, count) in enumerate(duplicates[:5]):
            customer = db.query(Customer).filter(Customer.customer_id == customer_id).first()
            print(f"  {i+1}. {customer.name if customer else 'Unknown'} - "
                  f"{payment_date} - {amount:,}원 ({count}건)")

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

def load_excel_data():
    """엑셀 파일에서 원본 데이터 로드"""
    print("\n=== 4. 엑셀 데이터 로드 ===")

    excel_path = Path(__file__).parent.parent / "data" / "payments_data.xlsx"

    if not excel_path.exists():
        print(f"엑셀 파일을 찾을 수 없습니다: {excel_path}")
        return None

    df = pd.read_excel(excel_path)
    print(f"엑셀 데이터 로드 완료: {len(df)}건")

    # 컬럼명 확인
    print(f"엑셀 컬럼: {df.columns.tolist()}")

    # 결제 프로그램 컬럼 확인
    if '결제 프로그램' in df.columns:
        program_counts = df['결제 프로그램'].value_counts()
        print("\n결제 프로그램 분포:")
        for program, count in program_counts.items():
            print(f"  {program}: {count}건")

    return df

def update_reference_types(db: Session, df):
    """엑셀 데이터를 기반으로 reference_type 업데이트"""
    print("\n=== 5. reference_type 업데이트 ===")

    if df is None or '결제 프로그램' not in df.columns:
        print("엑셀 데이터가 없거나 '결제 프로그램' 컬럼이 없습니다.")
        return 0

    updated_count = 0

    # 고객명으로 매칭
    for _, row in df.iterrows():
        customer_name = row.get('회원명') or row.get('이름')
        payment_date_str = row.get('결제일') or row.get('결제 날짜')
        amount = row.get('결제 금액') or row.get('금액')
        program = row.get('결제 프로그램')

        if not all([customer_name, payment_date_str, amount, program]):
            continue

        # 날짜 파싱
        try:
            if isinstance(payment_date_str, str):
                payment_date = datetime.strptime(payment_date_str, '%Y-%m-%d').date()
            else:
                payment_date = payment_date_str.date() if hasattr(payment_date_str, 'date') else payment_date_str
        except:
            continue

        # 고객 찾기
        customer = db.query(Customer).filter(Customer.name == customer_name).first()
        if not customer:
            continue

        # 해당 결제 찾기
        payment = db.query(Payment).filter(
            and_(
                Payment.customer_id == customer.customer_id,
                Payment.payment_date == payment_date,
                Payment.amount == amount
            )
        ).first()

        if payment and not payment.reference_type:
            payment.reference_type = program
            updated_count += 1

    db.commit()
    print(f"업데이트된 레코드 수: {updated_count}")

    return updated_count

def verify_update(db: Session):
    """업데이트 결과 검증"""
    print("\n=== 6. 업데이트 결과 검증 ===")

    # 전체 결제 수
    total_payments = db.query(Payment).count()
    print(f"전체 결제 수: {total_payments}")

    # reference_type이 NULL인 레코드 수
    null_ref_count = db.query(Payment).filter(Payment.reference_type == None).count()
    print(f"reference_type이 NULL인 레코드 수: {null_ref_count}")

    # reference_type 종류와 개수
    ref_types = db.query(
        Payment.reference_type,
        func.count(Payment.payment_id).label('count')
    ).group_by(Payment.reference_type).all()

    print("\nreference_type 분포:")
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
            response = input("\n중복 데이터를 제거하시겠습니까? (y/N): ")
            if response.lower() == 'y':
                remove_duplicates(db, duplicates)

        # 4. 엑셀 데이터 로드
        df = load_excel_data()

        # 5. reference_type 업데이트
        if null_count > 0 and df is not None:
            response = input("\nreference_type을 업데이트하시겠습니까? (y/N): ")
            if response.lower() == 'y':
                update_reference_types(db, df)

        # 6. 결과 검증
        verify_update(db)

    except Exception as e:
        print(f"\n오류 발생: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    main()
