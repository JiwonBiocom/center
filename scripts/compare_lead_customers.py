#!/usr/bin/env python3
"""
유입 고객 DB 리스트와 6/25 import 데이터 비교
"""
import pandas as pd
import requests
from datetime import datetime

def load_lead_customers():
    """유입 고객 DB 리스트 로드"""
    lead_df = pd.read_csv('/Users/vibetj/coding/center/docs/AIBIO 관리대장 파일모음/유입고객_DB리스트.csv')
    print(f"📋 유입 고객 DB 리스트: {len(lead_df)}명")

    # 이름과 연락처 정리
    lead_df['이름'] = lead_df['이름'].str.strip()
    lead_df['연락처'] = lead_df['연락처'].astype(str).str.strip()

    # 전화번호 형식 통일 (숫자만 추출)
    lead_df['연락처_숫자'] = lead_df['연락처'].str.replace('-', '').str.replace(' ', '')

    return lead_df

def fetch_june25_customers():
    """6/25에 생성된 고객 데이터 가져오기"""
    all_customers = []
    skip = 0
    limit = 100

    while True:
        response = requests.get(f"http://localhost:8000/api/v1/customers",
                               params={"skip": skip, "limit": limit})
        data = response.json()

        customers = data.get("data", [])
        if not customers:
            break

        all_customers.extend(customers)
        skip += limit

        if len(all_customers) >= data.get("total", 0):
            break

    # DataFrame 변환 및 6/25 데이터 필터링
    df = pd.DataFrame(all_customers)
    df['created_date'] = pd.to_datetime(df['created_at'], format='mixed').dt.date
    june25_df = df[df['created_date'] == pd.to_datetime('2025-06-25').date()].copy()

    print(f"📅 6/25 생성 고객: {len(june25_df)}명")

    # 전화번호 형식 통일
    june25_df['phone_숫자'] = june25_df['phone'].astype(str).str.replace('-', '').str.replace(' ', '')

    return june25_df

def compare_data():
    """데이터 비교 분석"""
    print("🔍 유입 고객 DB와 6/25 import 데이터 비교")
    print("="*60)

    # 데이터 로드
    lead_df = load_lead_customers()
    june25_df = fetch_june25_customers()

    # 샘플 데이터 출력
    print("\n📊 유입 고객 DB 샘플 (처음 5명):")
    print(lead_df[['이름', '연락처', '유입경로', 'DB입력일']].head())

    print("\n📊 6/25 생성 고객 샘플 (처음 5명):")
    print(june25_df[['name', 'phone', 'referral_source', 'customer_id']].head())

    # 이름으로 매칭
    print("\n🔍 이름 매칭 결과:")
    name_matches = []
    for _, lead in lead_df.iterrows():
        match = june25_df[june25_df['name'] == lead['이름']]
        if not match.empty:
            name_matches.append({
                '이름': lead['이름'],
                '유입DB_연락처': lead['연락처'],
                '6/25_연락처': match.iloc[0]['phone'],
                '유입경로': lead['유입경로'],
                'customer_id': match.iloc[0]['customer_id']
            })

    print(f"  이름 일치: {len(name_matches)}명")
    if name_matches:
        match_df = pd.DataFrame(name_matches)
        print(match_df.head(10))

    # 전화번호로 매칭
    print("\n🔍 전화번호 매칭 결과:")
    phone_matches = []
    for _, lead in lead_df.iterrows():
        lead_phone = str(lead['연락처_숫자'])
        if lead_phone and lead_phone != 'nan':
            # 전화번호로 매칭 시도
            for _, june in june25_df.iterrows():
                june_phone = str(june['phone_숫자'])
                if june_phone and june_phone != 'nan' and lead_phone in june_phone or june_phone in lead_phone:
                    phone_matches.append({
                        '유입DB_이름': lead['이름'],
                        '6/25_이름': june['name'],
                        '전화번호': june['phone'],
                        '유입경로': lead['유입경로'],
                        'customer_id': june['customer_id']
                    })
                    break

    print(f"  전화번호 일치: {len(phone_matches)}명")
    if phone_matches:
        phone_match_df = pd.DataFrame(phone_matches)
        print(phone_match_df.head(10))

    # 6/25 고객의 특징 분석
    print("\n📊 6/25 고객 특징:")
    print(f"  첫방문일 있음: {june25_df['first_visit_date'].notna().sum()}명")
    print(f"  전화번호 있음: {june25_df['phone'].notna().sum()}명")
    print(f"  지역 정보 있음: {june25_df['region'].notna().sum()}명")

    # referral_source 분석
    print("\n📊 6/25 고객 방문경로 분포:")
    referral_counts = june25_df['referral_source'].value_counts()
    for source, count in referral_counts.head(10).items():
        print(f"  {source}: {count}명")

    # 결론
    print("\n" + "="*60)
    print("📊 분석 결과:")
    total_matches = len(set([m['customer_id'] for m in name_matches] +
                           [m['customer_id'] for m in phone_matches]))
    print(f"  - 6/25 import 고객: {len(june25_df)}명")
    print(f"  - 유입 고객 DB 리스트: {len(lead_df)}명")
    print(f"  - 매칭된 고객: 약 {total_matches}명")
    print(f"  - 매칭률: {total_matches/len(june25_df)*100:.1f}%")

    if total_matches > len(june25_df) * 0.7:
        print("\n✅ 결론: 6/25 import 데이터는 '유입 고객 DB 리스트'의 데이터로 확인됩니다.")
    else:
        print("\n❓ 결론: 6/25 import 데이터와 '유입 고객 DB 리스트'의 연관성이 낮습니다.")

if __name__ == "__main__":
    compare_data()
