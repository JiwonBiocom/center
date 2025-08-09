#!/usr/bin/env python3
"""
원본 엑셀 950명 외 모든 고객을 미반영 고객 DB로 이동
"""
import pandas as pd
import requests
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from sqlalchemy import create_engine, text
from core.database import SessionLocal, engine
from models.customer import Customer as CustomerModel
from models.unreflected_customer import UnreflectedCustomer

def get_original_customer_ids():
    """원본 엑셀에서 customer_id 목록 추출"""
    print("📋 원본 엑셀 데이터에서 customer_id 추출 중...")

    # 원본 CSV 읽기
    excel_path = "/Users/vibetj/coding/center/docs/AIBIO 관리대장 파일모음/고객관리대장_전체고객.csv"
    df = pd.read_csv(excel_path, encoding='utf-8-sig')

    # 번호 컬럼이 customer_id
    original_ids = df['번호'].tolist()
    print(f"  ✅ 원본 고객 ID: {len(original_ids)}개")

    return original_ids

def move_unreflected_customers():
    """미반영 고객을 unreflected_customers 테이블로 이동"""
    db = SessionLocal()

    try:
        # 1. 원본 고객 ID 가져오기
        original_ids = get_original_customer_ids()

        # 2. 원본에 없는 고객 조회
        print("\n🔍 미반영 고객 조회 중...")
        unreflected_customers = db.query(CustomerModel).filter(
            ~CustomerModel.customer_id.in_(original_ids)
        ).all()

        print(f"  ✅ 미반영 고객: {len(unreflected_customers)}명")

        if not unreflected_customers:
            print("  ℹ️  이동할 미반영 고객이 없습니다.")
            return

        # 3. 미반영 고객 테이블로 데이터 복사
        print("\n📤 미반영 고객 테이블로 데이터 이동 중...")
        moved_count = 0

        for customer in unreflected_customers:
            # 데이터 소스 추정
            created_date = customer.created_at.date()
            data_source = "Unknown"

            if created_date.strftime('%Y-%m-%d') == '2025-06-05':
                data_source = "초기 마이그레이션 (6/5)"
            elif created_date.strftime('%Y-%m-%d') == '2025-06-20':
                data_source = "2차 마이그레이션 (6/20)"
            elif created_date.strftime('%Y-%m-%d') == '2025-06-25':
                data_source = "월별 이용현황 import (6/25)"
            elif created_date >= pd.to_datetime('2025-06-26').date():
                data_source = "수동 입력 또는 테스트 데이터"

            # 이미 존재하는지 확인
            existing = db.query(UnreflectedCustomer).filter(
                UnreflectedCustomer.original_customer_id == customer.customer_id
            ).first()

            if not existing:
                unreflected = UnreflectedCustomer(
                    original_customer_id=customer.customer_id,
                    name=customer.name,
                    phone=customer.phone,
                    email=customer.email,
                    first_visit_date=customer.first_visit_date,
                    region=customer.region,
                    referral_source=customer.referral_source,
                    health_concerns=customer.health_concerns,
                    notes=customer.notes,
                    assigned_staff=customer.assigned_staff,
                    birth_year=customer.birth_year,
                    gender=customer.gender,
                    address=customer.address,
                    emergency_contact=customer.emergency_contact,
                    occupation=customer.occupation,
                    data_source=data_source,
                    status='pending'
                )
                db.add(unreflected)
                moved_count += 1

                if moved_count % 10 == 0:
                    print(f"    ... {moved_count}명 이동 완료")

        db.commit()
        print(f"  ✅ 총 {moved_count}명을 미반영 고객 테이블로 이동 완료")

        # 4. 원본 테이블에서 삭제
        print("\n🗑️  원본 테이블에서 미반영 고객 삭제 중...")
        delete_count = 0

        for customer in unreflected_customers:
            try:
                # API를 통한 cascade 삭제
                response = requests.delete(
                    f"http://localhost:8000/api/v1/customers/{customer.customer_id}?cascade=true"
                )
                if response.status_code == 200:
                    delete_count += 1
                    if delete_count % 10 == 0:
                        print(f"    ... {delete_count}명 삭제 완료")
                else:
                    print(f"  ⚠️  ID {customer.customer_id} 삭제 실패: {response.status_code}")
            except Exception as e:
                print(f"  ❌ ID {customer.customer_id} 삭제 중 에러: {e}")

        print(f"  ✅ 총 {delete_count}명 삭제 완료")

        # 5. 최종 확인
        print("\n📊 최종 결과:")
        remaining_count = db.query(CustomerModel).count()
        unreflected_count = db.query(UnreflectedCustomer).count()

        print(f"  - 정식 고객: {remaining_count}명")
        print(f"  - 미반영 고객: {unreflected_count}명")
        print(f"  - 원본 엑셀과 차이: {remaining_count - 950}명")

    except Exception as e:
        print(f"\n❌ 에러 발생: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("🚀 원본 엑셀 950명 외 고객 이동 시작")
    print("="*60)
    move_unreflected_customers()
    print("\n✅ 작업 완료!")
