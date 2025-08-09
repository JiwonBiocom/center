#!/usr/bin/env python3
"""
API를 통해 원본 엑셀 950명 외 모든 고객을 미반영 고객 DB로 이동
"""
import pandas as pd
import requests
import json

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

def fetch_all_customers():
    """API를 통해 모든 고객 데이터 가져오기"""
    print("\n📊 전체 고객 데이터 가져오는 중...")

    all_customers = []
    page = 1

    while True:
        response = requests.get(
            f"http://localhost:8000/api/v1/customers",
            params={"skip": (page-1)*100, "limit": 100}
        )
        data = response.json()

        customers = data.get("data", [])
        if not customers:
            break

        all_customers.extend(customers)

        if len(all_customers) >= data.get("total", 0):
            break

        page += 1

    print(f"  ✅ 전체 고객: {len(all_customers)}명")
    return all_customers

def add_to_unreflected_db(customer):
    """미반영 고객 DB에 추가 (백엔드에서 직접)"""
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

    from core.database import SessionLocal
    from models.unreflected_customer import UnreflectedCustomer

    db = SessionLocal()
    try:
        # 데이터 소스 추정
        created_date = pd.to_datetime(customer['created_at']).date()
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
            UnreflectedCustomer.original_customer_id == customer['customer_id']
        ).first()

        if not existing:
            unreflected = UnreflectedCustomer(
                original_customer_id=customer['customer_id'],
                name=customer['name'],
                phone=customer.get('phone'),
                email=customer.get('email'),
                first_visit_date=pd.to_datetime(customer['first_visit_date']).date() if customer.get('first_visit_date') else None,
                region=customer.get('region'),
                referral_source=customer.get('referral_source'),
                health_concerns=customer.get('health_concerns'),
                notes=customer.get('notes'),
                assigned_staff=customer.get('assigned_staff'),
                birth_year=customer.get('birth_year'),
                gender=customer.get('gender'),
                address=customer.get('address'),
                emergency_contact=customer.get('emergency_contact'),
                occupation=customer.get('occupation'),
                data_source=data_source,
                status='pending'
            )
            db.add(unreflected)
            db.commit()
            return True
    except Exception as e:
        print(f"    ❌ 에러: {e}")
        db.rollback()
        return False
    finally:
        db.close()

    return False

def move_all_unreflected():
    """미반영 고객 이동 메인 함수"""
    # 1. 원본 고객 ID 가져오기
    original_ids = get_original_customer_ids()

    # 2. 전체 고객 가져오기
    all_customers = fetch_all_customers()

    # 3. 미반영 고객 찾기
    print("\n🔍 미반영 고객 식별 중...")
    unreflected_customers = []

    for customer in all_customers:
        if customer['customer_id'] not in original_ids:
            unreflected_customers.append(customer)

    print(f"  ✅ 미반영 고객: {len(unreflected_customers)}명")

    if not unreflected_customers:
        print("  ℹ️  이동할 미반영 고객이 없습니다.")
        return

    # 4. 미반영 고객 DB에 추가
    print("\n📤 미반영 고객 DB로 데이터 복사 중...")
    added_count = 0

    for customer in unreflected_customers:
        if add_to_unreflected_db(customer):
            added_count += 1
            if added_count % 10 == 0:
                print(f"    ... {added_count}명 추가 완료")

    print(f"  ✅ 총 {added_count}명을 미반영 고객 DB에 추가")

    # 5. 원본에서 삭제
    print("\n🗑️  원본 테이블에서 미반영 고객 삭제 중...")
    delete_count = 0
    failed_deletes = []

    for customer in unreflected_customers:
        try:
            response = requests.delete(
                f"http://localhost:8000/api/v1/customers/{customer['customer_id']}?cascade=true"
            )
            if response.status_code == 200:
                delete_count += 1
                if delete_count % 10 == 0:
                    print(f"    ... {delete_count}명 삭제 완료")
            else:
                failed_deletes.append({
                    'id': customer['customer_id'],
                    'name': customer['name'],
                    'status': response.status_code
                })
        except Exception as e:
            failed_deletes.append({
                'id': customer['customer_id'],
                'name': customer['name'],
                'error': str(e)
            })

    print(f"  ✅ 총 {delete_count}명 삭제 완료")

    if failed_deletes:
        print(f"  ⚠️  삭제 실패: {len(failed_deletes)}명")
        for fail in failed_deletes[:5]:  # 처음 5개만 표시
            print(f"    - ID {fail['id']} ({fail['name']})")

    # 6. 최종 확인
    print("\n📊 최종 결과:")

    # 남은 고객 수 확인
    response = requests.get("http://localhost:8000/api/v1/customers?limit=1")
    remaining = response.json().get('total', 0)

    # 미반영 고객 수 확인
    response = requests.get("http://localhost:8000/api/v1/unreflected-customers?limit=1")
    unreflected = response.json().get('total', 0)

    print(f"  - 정식 고객: {remaining}명")
    print(f"  - 미반영 고객: {unreflected}명")
    print(f"  - 원본 엑셀과 차이: {remaining - 950}명")

if __name__ == "__main__":
    print("🚀 원본 엑셀 950명 외 고객 이동 시작")
    print("="*60)
    move_all_unreflected()
    print("\n✅ 작업 완료!")
