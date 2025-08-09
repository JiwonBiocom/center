#!/usr/bin/env python3
"""
원본 엑셀과 DB의 정확한 차이 분석
"""
import pandas as pd
import requests
from datetime import datetime

def load_original_customers():
    """원본 엑셀 데이터 로드"""
    excel_path = "/Users/vibetj/coding/center/docs/AIBIO 관리대장 파일모음/고객관리대장_전체고객.csv"

    print("📋 원본 엑셀 데이터 로드 중...")
    df = pd.read_csv(excel_path, encoding='utf-8-sig')

    # 컬럼명 정리
    df.columns = df.columns.str.strip()

    # 이름과 전화번호 정리
    df['이름'] = df['이름'].str.strip()
    if '연락처' in df.columns:
        df['연락처'] = df['연락처'].astype(str).str.strip()
        # 전화번호 형식 통일 (하이픈 제거)
        df['연락처_정리'] = df['연락처'].str.replace('-', '').str.replace(' ', '')

    # nan이 아닌 경우에만 필터링
    df = df[df['이름'].notna()]

    print(f"  ✅ 원본 고객 수: {len(df)}명")
    return df

def fetch_all_db_customers():
    """DB의 모든 고객 데이터 가져오기"""
    print("\n📊 DB 고객 데이터 가져오는 중...")

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

    print(f"  ✅ DB 고객 수: {len(all_customers)}명")
    return all_customers

def analyze_differences():
    """차이 분석"""
    print("\n🔍 차이 분석 시작")
    print("="*60)

    # 1. 데이터 로드
    original_df = load_original_customers()
    db_customers = fetch_all_db_customers()

    # 2. DB 데이터를 DataFrame으로 변환
    db_df = pd.DataFrame(db_customers)

    # 전화번호 정리
    db_df['phone_cleaned'] = db_df['phone'].fillna('').str.replace('-', '').str.replace(' ', '')

    # 3. 매칭 방법 1: 이름으로 매칭
    original_names = set(original_df['이름'].tolist())
    db_names = set(db_df['name'].tolist())

    print(f"\n📊 이름 기준 분석:")
    print(f"  - 원본에만 있는 이름: {len(original_names - db_names)}명")
    print(f"  - DB에만 있는 이름: {len(db_names - original_names)}명")
    print(f"  - 공통 이름: {len(original_names & db_names)}명")

    # 4. 매칭 방법 2: 전화번호로 매칭 (빈 문자열 제외)
    original_phones = set(original_df[original_df['연락처_정리'].notna() & (original_df['연락처_정리'] != 'nan')]['연락처_정리'].tolist())
    db_phones = set(db_df[db_df['phone_cleaned'] != '']['phone_cleaned'].tolist())

    print(f"\n📊 전화번호 기준 분석:")
    print(f"  - 원본에만 있는 번호: {len(original_phones - db_phones)}개")
    print(f"  - DB에만 있는 번호: {len(db_phones - original_phones)}개")
    print(f"  - 공통 번호: {len(original_phones & db_phones)}개")

    # 5. DB에만 있는 고객 상세 분석
    db_only_names = db_names - original_names
    db_only_customers = db_df[db_df['name'].isin(db_only_names)]

    print(f"\n📊 DB에만 있는 고객 {len(db_only_customers)}명 분석:")

    # 생성일자별 분석
    db_only_customers['created_date'] = pd.to_datetime(db_only_customers['created_at'], format='mixed').dt.date
    date_counts = db_only_customers['created_date'].value_counts().sort_index()

    print("\n  생성일자별 분포:")
    for date, count in date_counts.items():
        print(f"    - {date}: {count}명")

    # 유입경로별 분석
    source_counts = db_only_customers['referral_source'].fillna('미입력').value_counts()

    print("\n  유입경로별 분포:")
    for source, count in source_counts.items():
        print(f"    - {source}: {count}명")

    # 6. 중복 가능성 체크
    print("\n🔍 중복 가능성 체크:")

    # 원본에서 이름이 중복된 경우
    original_name_counts = original_df['이름'].value_counts()
    original_duplicates = original_name_counts[original_name_counts > 1]

    if len(original_duplicates) > 0:
        print(f"  원본 엑셀의 중복 이름: {len(original_duplicates)}개")
        for name, count in original_duplicates.head(5).items():
            print(f"    - {name}: {count}명")

    # DB에서 이름이 중복된 경우
    db_name_counts = db_df['name'].value_counts()
    db_duplicates = db_name_counts[db_name_counts > 1]

    if len(db_duplicates) > 0:
        print(f"\n  DB의 중복 이름: {len(db_duplicates)}개")
        for name, count in db_duplicates.head(5).items():
            print(f"    - {name}: {count}명")

    # 7. DB에만 있는 고객 리스트 저장
    output_file = "/Users/vibetj/coding/center/db_only_customers.csv"
    db_only_customers.to_csv(output_file, index=False, encoding='utf-8-sig')
    print(f"\n💾 DB에만 있는 고객 목록 저장: {output_file}")

    return db_only_customers

if __name__ == "__main__":
    db_only = analyze_differences()
