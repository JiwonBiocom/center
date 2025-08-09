#!/usr/bin/env python3
"""
고객 데이터 분석 스크립트
- DB의 실제 고객 수 확인
- 고객 데이터 출처 분석
- 중복/샘플 데이터 식별
"""
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import pandas as pd
from collections import Counter

# 데이터베이스 연결
DATABASE_URL = "sqlite:///./center.db"
if os.path.exists("/Users/vibetj/coding/center/backend/center.db"):
    DATABASE_URL = "sqlite:////Users/vibetj/coding/center/backend/center.db"

engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

def analyze_customers():
    print("🔍 고객 데이터 분석 시작")
    print("="*60)

    # 1. 전체 고객 수
    total_count = session.execute(text("SELECT COUNT(*) FROM customers")).scalar()
    print(f"\n📊 전체 고객 수: {total_count}명")

    # 2. 고객 데이터를 DataFrame으로 로드
    query = """
    SELECT id, name, phone, email, created_at, updated_at,
           registration_date, first_visit_date, memo
    FROM customers
    ORDER BY id
    """
    df = pd.read_sql_query(query, engine)

    # 3. 생성일자 기준 분석
    print("\n📅 생성일자 기준 분석:")
    df['created_date'] = pd.to_datetime(df['created_at']).dt.date
    creation_stats = df['created_date'].value_counts().sort_index()

    print("  생성일별 고객 수:")
    for date, count in creation_stats.items():
        print(f"    {date}: {count}명")

    # 4. 이름 패턴 분석 (샘플 데이터 식별)
    print("\n👤 이름 패턴 분석:")
    name_patterns = {
        '테스트': df['name'].str.contains('테스트|test|Test|TEST', na=False).sum(),
        '샘플': df['name'].str.contains('샘플|sample|Sample', na=False).sum(),
        '고객+숫자': df['name'].str.match(r'^고객\d+$', na=False).sum(),
        'Customer+숫자': df['name'].str.match(r'^Customer\s*\d+$', na=False).sum(),
        '숫자로만': df['name'].str.match(r'^\d+$', na=False).sum(),
    }

    for pattern, count in name_patterns.items():
        if count > 0:
            print(f"  {pattern} 패턴: {count}명")

    # 5. 전화번호 분석
    print("\n📞 전화번호 분석:")
    phone_null_count = df['phone'].isna().sum()
    print(f"  전화번호 없음: {phone_null_count}명")

    # 전화번호 중복 확인
    phone_duplicates = df[df['phone'].notna()]['phone'].value_counts()
    duplicate_phones = phone_duplicates[phone_duplicates > 1]
    if len(duplicate_phones) > 0:
        print(f"  중복 전화번호: {len(duplicate_phones)}개")
        for phone, count in duplicate_phones.head(5).items():
            print(f"    {phone}: {count}명")

    # 6. 메모 필드 분석 (데이터 출처 추적)
    print("\n📝 메모 필드 분석:")
    memo_not_null = df[df['memo'].notna()]
    print(f"  메모가 있는 고객: {len(memo_not_null)}명")

    # 메모에서 특정 패턴 찾기
    if len(memo_not_null) > 0:
        # 엑셀 관련 키워드
        excel_keywords = memo_not_null['memo'].str.contains('엑셀|Excel|excel|import|마이그레이션', na=False).sum()
        if excel_keywords > 0:
            print(f"  엑셀 관련 메모: {excel_keywords}명")

    # 7. 등록일/첫방문일 분석
    print("\n📆 날짜 데이터 분석:")
    reg_date_not_null = df['registration_date'].notna().sum()
    first_visit_not_null = df['first_visit_date'].notna().sum()
    print(f"  등록일 있음: {reg_date_not_null}명")
    print(f"  첫방문일 있음: {first_visit_not_null}명")

    # 8. 최근 추가된 고객 (최근 7일)
    recent_date = pd.Timestamp.now() - pd.Timedelta(days=7)
    recent_customers = df[pd.to_datetime(df['created_at']) > recent_date]
    if len(recent_customers) > 0:
        print(f"\n🆕 최근 7일 내 추가된 고객: {len(recent_customers)}명")
        print(recent_customers[['id', 'name', 'created_at']].head(10))

    # 9. 의심스러운 패턴 종합
    print("\n⚠️  의심스러운 데이터 패턴:")
    suspicious_count = 0

    # 샘플 데이터로 의심되는 조건들
    suspicious_conditions = [
        (df['name'].str.contains('테스트|test|샘플|sample', case=False, na=False), "테스트/샘플 이름"),
        (df['name'].str.match(r'^고객\d+$|^Customer\s*\d+$', na=False), "자동생성 이름"),
        (df['phone'].isna() & df['email'].isna(), "연락처 없음"),
        ((df['registration_date'].isna()) & (df['first_visit_date'].isna()), "방문 기록 없음"),
    ]

    for condition, description in suspicious_conditions:
        count = condition.sum()
        if count > 0:
            suspicious_count += count
            print(f"  {description}: {count}명")

    # 10. 데이터 출처 추정
    print("\n🔎 데이터 출처 추정:")

    # 같은 날짜에 대량으로 생성된 데이터 찾기
    bulk_created = creation_stats[creation_stats > 50]
    if len(bulk_created) > 0:
        print("  대량 생성일:")
        for date, count in bulk_created.items():
            print(f"    {date}: {count}명 (일괄 import 가능성)")
            # 해당 날짜의 샘플 데이터 확인
            sample_data = df[df['created_date'] == date].head(5)
            print("      샘플:")
            for _, row in sample_data.iterrows():
                print(f"        ID:{row['id']} - {row['name']} ({row['phone']})")

    print("\n" + "="*60)
    print(f"📊 분석 결과 요약:")
    print(f"  - 전체 고객: {total_count}명")
    print(f"  - 의심 데이터: 약 {suspicious_count}명")
    print(f"  - 실제 고객 추정: 약 {total_count - suspicious_count}명")

    # 상세 데이터를 CSV로 저장
    output_file = "/Users/vibetj/coding/center/customer_analysis.csv"
    df.to_csv(output_file, index=False, encoding='utf-8-sig')
    print(f"\n💾 상세 데이터 저장: {output_file}")

    session.close()
    return df

if __name__ == "__main__":
    analyze_customers()
