#!/usr/bin/env python3
"""
고객 데이터베이스 상세 분석
"""
import requests
import pandas as pd
from datetime import datetime
import json

# API 엔드포인트
BASE_URL = "http://localhost:8000"

def fetch_all_customers():
    """모든 고객 데이터를 가져옵니다."""
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

        # 전체 개수에 도달했는지 확인
        if len(all_customers) >= data.get("total", 0):
            break

    return all_customers

def analyze_customers():
    print("🔍 고객 데이터베이스 분석 시작")
    print("="*60)

    # 모든 고객 데이터 가져오기
    customers = fetch_all_customers()
    df = pd.DataFrame(customers)

    print(f"\n📊 전체 고객 수: {len(df)}명")

    # created_at 분석
    df['created_date'] = pd.to_datetime(df['created_at'], format='mixed').dt.date
    df['created_hour'] = pd.to_datetime(df['created_at'], format='mixed').dt.hour

    # 생성일별 분석
    print("\n📅 생성일별 고객 수:")
    creation_stats = df['created_date'].value_counts().sort_index()
    for date, count in creation_stats.items():
        if count > 10:  # 10명 이상인 날짜만 표시
            print(f"  {date}: {count}명")

    # 대량 생성 패턴 분석
    print("\n🔍 대량 생성 패턴 분석:")
    bulk_dates = creation_stats[creation_stats > 50]

    for date in bulk_dates.index:
        date_customers = df[df['created_date'] == date]

        # 같은 시간대에 생성되었는지 확인
        hour_dist = date_customers['created_hour'].value_counts()
        print(f"\n  📅 {date}: {len(date_customers)}명")
        print(f"    시간대 분포: {dict(hour_dist.head())}")

        # 이름 패턴 분석
        names = date_customers['name'].tolist()
        sample_names = names[:10] if len(names) > 10 else names
        print(f"    샘플 이름: {sample_names}")

        # 전화번호 유무
        phone_exists = date_customers['phone'].notna().sum()
        print(f"    전화번호 있음: {phone_exists}/{len(date_customers)}")

        # 첫방문일 유무
        visit_exists = date_customers['first_visit_date'].notna().sum()
        print(f"    첫방문일 있음: {visit_exists}/{len(date_customers)}")

    # 샘플 데이터 패턴 찾기
    print("\n⚠️  샘플/테스트 데이터 패턴:")

    # 패턴 1: 전화번호와 이메일이 모두 없는 경우
    no_contact = df[(df['phone'].isna()) & (df['email'].isna())]
    print(f"  연락처 없음: {len(no_contact)}명")

    # 패턴 2: 방문 기록이 없는 경우
    no_visit = df[df['first_visit_date'].isna()]
    print(f"  첫방문일 없음: {len(no_visit)}명")

    # 패턴 3: 이름이 특정 패턴인 경우
    test_patterns = df['name'].str.contains(r'테스트|test|샘플|sample|고객\d+|Customer', case=False, na=False)
    print(f"  테스트 패턴 이름: {test_patterns.sum()}명")

    # 패턴 4: customer_id가 특정 범위인 경우
    print(f"\n📊 Customer ID 분포:")
    print(f"  최소 ID: {df['customer_id'].min()}")
    print(f"  최대 ID: {df['customer_id'].max()}")
    id_gaps = []
    sorted_ids = sorted(df['customer_id'].tolist())
    for i in range(1, len(sorted_ids)):
        gap = sorted_ids[i] - sorted_ids[i-1]
        if gap > 10:
            id_gaps.append((sorted_ids[i-1], sorted_ids[i], gap))

    if id_gaps:
        print(f"  ID 갭 (10 이상):")
        for start, end, gap in id_gaps[:5]:
            print(f"    {start} → {end} (갭: {gap})")

    # 원본 엑셀과 비교할 수 있는 데이터 추출
    print("\n📊 원본 데이터로 추정되는 고객:")

    # 조건: 전화번호가 있고, 2025년 6월 27일 이전에 생성된 데이터
    original_cutoff = pd.to_datetime('2025-06-27')
    original_candidates = df[
        (df['phone'].notna()) &
        (pd.to_datetime(df['created_at'], format='mixed') < original_cutoff)
    ]
    print(f"  후보 고객 수: {len(original_candidates)}명")

    # 2025년 6월 27일에 대량 생성된 데이터
    june_27_customers = df[df['created_date'] == pd.to_datetime('2025-06-27').date()]
    print(f"\n📅 2025-06-27 생성 고객: {len(june_27_customers)}명")

    # 결과 저장
    output_file = "/Users/vibetj/coding/center/customer_analysis_detail.csv"
    df.to_csv(output_file, index=False, encoding='utf-8-sig')
    print(f"\n💾 상세 분석 결과 저장: {output_file}")

    # 제거 추천 데이터
    print("\n🗑️  제거 추천 데이터:")
    remove_candidates = df[
        (df['phone'].isna()) &
        (df['email'].isna()) &
        (df['first_visit_date'].isna()) &
        (pd.to_datetime(df['created_at'], format='mixed') >= original_cutoff)
    ]
    print(f"  제거 추천: {len(remove_candidates)}명")
    print(f"  ID 범위: {remove_candidates['customer_id'].min()} ~ {remove_candidates['customer_id'].max()}")

    return df

if __name__ == "__main__":
    analyze_customers()
