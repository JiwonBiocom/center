#!/usr/bin/env python3
"""
엑셀과 DB 불일치 데이터 상세 분석 스크립트
"""
import os
import sys
import pandas as pd
from datetime import datetime
from decimal import Decimal
import warnings
warnings.filterwarnings('ignore')

# 프로젝트 루트 경로 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

# 데이터베이스 연결
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

def get_detailed_db_data():
    """DB에서 상세 데이터 조회"""
    session = Session()

    try:
        # 2025년 1-5월 모든 결제 데이터 조회 (엑셀 업로드 아닌 것도 포함)
        query = text("""
            SELECT
                p.payment_id,
                p.customer_id,
                c.name as customer_name,
                p.payment_date,
                p.amount,
                p.notes,
                p.created_at,
                EXTRACT(MONTH FROM p.payment_date) as month,
                CASE
                    WHEN p.notes LIKE '%엑셀 업로드%' THEN '엑셀 업로드'
                    ELSE '수동 입력'
                END as data_source
            FROM payments p
            JOIN customers c ON p.customer_id = c.customer_id
            WHERE p.payment_date >= '2025-01-01'
            AND p.payment_date < '2025-06-01'
            ORDER BY p.payment_date, c.name
        """)

        result = session.execute(query)
        data = []

        for row in result:
            data.append({
                'payment_id': row.payment_id,
                'customer_id': row.customer_id,
                'customer_name': row.customer_name,
                'payment_date': row.payment_date,
                'amount': float(row.amount),
                'notes': row.notes,
                'created_at': row.created_at,
                'month': int(row.month),
                'data_source': row.data_source
            })

        return pd.DataFrame(data)

    finally:
        session.close()

def analyze_duplicate_payments():
    """중복 결제 분석"""
    session = Session()

    try:
        # 같은 고객, 같은 날짜에 여러 결제가 있는 경우 찾기
        query = text("""
            SELECT
                c.name as customer_name,
                p.payment_date,
                COUNT(*) as payment_count,
                SUM(p.amount) as total_amount,
                STRING_AGG(p.payment_id::text, ', ') as payment_ids,
                STRING_AGG(p.notes, ' | ') as all_notes
            FROM payments p
            JOIN customers c ON p.customer_id = c.customer_id
            WHERE p.payment_date >= '2025-01-01'
            AND p.payment_date < '2025-06-01'
            GROUP BY c.name, p.payment_date
            HAVING COUNT(*) > 1
            ORDER BY p.payment_date, c.name
        """)

        result = session.execute(query)
        duplicates = []

        for row in result:
            duplicates.append({
                'customer_name': row.customer_name,
                'payment_date': row.payment_date,
                'payment_count': row.payment_count,
                'total_amount': float(row.total_amount),
                'payment_ids': row.payment_ids,
                'all_notes': row.all_notes
            })

        return pd.DataFrame(duplicates)

    finally:
        session.close()

def main():
    """메인 실행 함수"""
    print("🔍 불일치 데이터 상세 분석\n")

    # 1. 전체 DB 데이터 조회
    print("📊 DB 데이터 상세 조회...")
    db_data = get_detailed_db_data()

    # 데이터 소스별 통계
    print("\n1️⃣ 데이터 소스별 통계")
    source_stats = db_data.groupby('data_source').agg({
        'payment_id': 'count',
        'amount': 'sum'
    }).rename(columns={'payment_id': 'count'})

    for source, stats in source_stats.iterrows():
        print(f"  - {source}: {int(stats['count'])}건, {stats['amount']:,.0f}원")

    # 월별 데이터 소스 분포
    print("\n2️⃣ 월별 데이터 소스 분포")
    monthly_source = db_data.groupby(['month', 'data_source']).size().unstack(fill_value=0)
    print(monthly_source.to_string())

    # 수동 입력 데이터 상세
    manual_data = db_data[db_data['data_source'] == '수동 입력']
    if not manual_data.empty:
        print("\n3️⃣ 수동 입력 데이터 상세")
        print(f"  총 {len(manual_data)}건의 수동 입력 데이터:")

        for month in range(1, 6):
            month_manual = manual_data[manual_data['month'] == month]
            if not month_manual.empty:
                print(f"\n  📌 {month}월 수동 입력 ({len(month_manual)}건):")
                for _, row in month_manual.iterrows():
                    print(f"    - {row['payment_date'].strftime('%Y-%m-%d')} {row['customer_name']}: {row['amount']:,.0f}원")
                    if row['notes']:
                        print(f"      메모: {row['notes']}")

    # 4. 중복 결제 분석
    print("\n4️⃣ 중복 결제 분석")
    duplicates = analyze_duplicate_payments()

    if not duplicates.empty:
        print(f"  ⚠️  같은 날짜에 같은 고객의 중복 결제 발견: {len(duplicates)}건")
        for _, dup in duplicates.iterrows():
            print(f"\n  - {dup['payment_date'].strftime('%Y-%m-%d')} {dup['customer_name']}")
            print(f"    결제 {dup['payment_count']}건, 총 {dup['total_amount']:,.0f}원")
            print(f"    Payment IDs: {dup['payment_ids']}")
            print(f"    메모: {dup['all_notes']}")
    else:
        print("  ✅ 중복 결제 없음")

    # 5. 금액 차이 분석
    print("\n5️⃣ 엑셀과 DB 금액 차이 분석")
    excel_total = 100_360_710  # 엑셀 총액
    db_excel_total = db_data[db_data['data_source'] == '엑셀 업로드']['amount'].sum()
    db_manual_total = db_data[db_data['data_source'] == '수동 입력']['amount'].sum()

    print(f"  - 엑셀 파일 총액: {excel_total:,.0f}원")
    print(f"  - DB 엑셀 업로드 총액: {db_excel_total:,.0f}원")
    print(f"  - DB 수동 입력 총액: {db_manual_total:,.0f}원")
    print(f"  - 엑셀과 DB 엑셀업로드 차이: {excel_total - db_excel_total:,.0f}원")

    # 6. 특정 고객 분석 (불일치가 있던 고객들)
    print("\n6️⃣ 불일치 고객 상세 분석")
    mismatch_customers = ['김수현', '송선경', '김준호', '국지은', '김수현(남)']

    for customer in mismatch_customers:
        customer_data = db_data[db_data['customer_name'].str.contains(customer, na=False)]
        if not customer_data.empty:
            print(f"\n  📌 {customer} 결제 내역:")
            for _, row in customer_data.iterrows():
                print(f"    - {row['payment_date'].strftime('%Y-%m-%d')}: {row['amount']:,.0f}원 ({row['data_source']})")

if __name__ == "__main__":
    main()
