#!/usr/bin/env python3
"""
API를 통한 중복/테스트 고객 데이터 정리
"""
import requests
import json
from datetime import datetime
import os
import pandas as pd

BASE_URL = "http://localhost:8000"

def fetch_all_customers():
    """모든 고객 데이터 가져오기"""
    all_customers = []
    skip = 0
    limit = 100

    while True:
        response = requests.get(f"{BASE_URL}/api/v1/customers", params={"skip": skip, "limit": limit})
        data = response.json()

        customers = data.get("data", [])
        if not customers:
            break

        all_customers.extend(customers)
        skip += limit

        if len(all_customers) >= data.get("total", 0):
            break

    return all_customers

def backup_data():
    """삭제 전 데이터 백업"""
    print("📦 데이터 백업 시작...")

    # 백업 디렉토리 생성
    backup_dir = "/Users/vibetj/coding/center/backup"
    os.makedirs(backup_dir, exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    # 전체 고객 데이터 가져오기
    customers = fetch_all_customers()
    df = pd.DataFrame(customers)

    # 백업 저장
    backup_file = f"{backup_dir}/customers_backup_{timestamp}.csv"
    df.to_csv(backup_file, index=False, encoding='utf-8-sig')
    print(f"  ✅ 전체 고객 백업 완료: {backup_file} ({len(df)}명)")

    # 삭제 대상 식별
    # 1. 6/25 생성 데이터
    df['created_date'] = pd.to_datetime(df['created_at'], format='mixed').dt.date
    june25_df = df[df['created_date'] == pd.to_datetime('2025-06-25').date()]

    # 2. 6/27 이후 생성된 테스트 데이터
    test_df = df[
        (df['created_date'] >= pd.to_datetime('2025-06-27').date()) &
        (df['phone'].isna() | (df['phone'] == '')) &
        (df['email'].isna() | (df['email'] == '')) &
        (df['first_visit_date'].isna())
    ]

    delete_info = {
        'timestamp': timestamp,
        'june25_count': len(june25_df),
        'june25_ids': june25_df['customer_id'].tolist(),
        'test_data_count': len(test_df),
        'test_data_ids': test_df['customer_id'].tolist(),
        'total_to_delete': len(june25_df) + len(test_df)
    }

    # 삭제 대상 정보 저장
    delete_info_file = f"{backup_dir}/delete_info_{timestamp}.json"
    with open(delete_info_file, 'w', encoding='utf-8') as f:
        json.dump(delete_info, f, ensure_ascii=False, indent=2)

    print(f"\n📊 삭제 대상 데이터:")
    print(f"  - 6/25 import 데이터: {len(june25_df)}명")
    print(f"    ID 범위: {min(june25_df['customer_id'])} ~ {max(june25_df['customer_id'])}")
    print(f"  - 6/27 이후 테스트 데이터: {len(test_df)}명")
    if len(test_df) > 0:
        print(f"    ID 범위: {min(test_df['customer_id'])} ~ {max(test_df['customer_id'])}")
    print(f"  - 총 삭제 예정: {delete_info['total_to_delete']}명")

    return delete_info

def delete_customers(delete_info):
    """고객 데이터 삭제"""
    print("\n🗑️  데이터 삭제 시작...")

    all_ids = delete_info['june25_ids'] + delete_info['test_data_ids']

    success_count = 0
    failed_ids = []

    for customer_id in all_ids:
        try:
            response = requests.delete(f"{BASE_URL}/api/v1/customers/{customer_id}")
            if response.status_code == 200:
                success_count += 1
            else:
                failed_ids.append(customer_id)
                print(f"  ⚠️  삭제 실패 ID {customer_id}: {response.status_code}")
        except Exception as e:
            failed_ids.append(customer_id)
            print(f"  ❌ 삭제 에러 ID {customer_id}: {e}")

    print(f"\n  ✅ 삭제 완료: {success_count}명")
    if failed_ids:
        print(f"  ❌ 삭제 실패: {len(failed_ids)}명")
        print(f"     실패 ID: {failed_ids[:10]}...")

def verify_cleanup():
    """정리 후 검증"""
    print("\n🔍 데이터 검증...")

    # 현재 고객 수 확인
    response = requests.get(f"{BASE_URL}/api/v1/customers?limit=1")
    data = response.json()
    total_count = data.get('total', 0)

    print(f"  현재 전체 고객 수: {total_count}명")
    print(f"  원본 엑셀 고객 수: 950명")
    print(f"  차이: {total_count - 950}명")

    # 남은 데이터 품질 확인
    customers = fetch_all_customers()
    df = pd.DataFrame(customers)

    with_phone = df['phone'].notna().sum()
    with_email = df['email'].notna().sum()
    with_visit = df['first_visit_date'].notna().sum()

    print("\n📊 데이터 품질:")
    print(f"  전화번호 있음: {with_phone}/{len(df)} ({with_phone/len(df)*100:.1f}%)")
    print(f"  이메일 있음: {with_email}/{len(df)} ({with_email/len(df)*100:.1f}%)")
    print(f"  첫방문일 있음: {with_visit}/{len(df)} ({with_visit/len(df)*100:.1f}%)")

    # 날짜별 분포
    df['created_date'] = pd.to_datetime(df['created_at'], format='mixed').dt.date
    date_dist = df['created_date'].value_counts().sort_index()

    print("\n📅 생성일별 고객 수:")
    for date, count in date_dist.items():
        if count > 10:
            print(f"  {date}: {count}명")

def main():
    print("🧹 고객 데이터 정리 시작")
    print("="*60)

    # 1. 백업
    delete_info = backup_data()

    # 2. 확인
    print("\n⚠️  정말로 삭제하시겠습니까?")
    print(f"삭제될 데이터: {delete_info['total_to_delete']}명")
    response = input("계속하려면 'yes'를 입력하세요: ")

    if response.lower() == 'yes':
        # 3. 삭제
        delete_customers(delete_info)

        # 4. 검증
        verify_cleanup()

        print("\n✅ 데이터 정리 완료!")
        print("📌 백업 파일은 /backup 폴더에 저장되었습니다.")
    else:
        print("\n❌ 취소되었습니다.")

if __name__ == "__main__":
    main()
