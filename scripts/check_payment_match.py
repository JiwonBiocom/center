#!/usr/bin/env python3
"""
결제 데이터 매칭 문제 진단 스크립트
"""

import pandas as pd
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime

def check_data_mismatch():
    # Excel 데이터 로드
    excel_path = 'docs/AIBIO 관리대장 파일모음/★2025년 AIBIO 결제현황.xlsx'
    df_excel = pd.read_excel(excel_path, sheet_name='전체 결제대장', skiprows=2)

    print("📊 Excel 데이터 분석:")
    print(f"- 전체 건수: {len(df_excel)}")
    print(f"- 날짜 범위: {df_excel['결제일자'].min()} ~ {df_excel['결제일자'].max()}")
    print(f"- 고유 고객: {df_excel['고객명'].nunique()}")

    # DB 연결
    conn = psycopg2.connect(
        host='aws-0-ap-northeast-2.pooler.supabase.com',
        port=6543,
        database='postgres',
        user='postgres.wvcxzyvmwwrbjpeuyvuh',
        password=r'bico6819!!'
    )
    cur = conn.cursor(cursor_factory=RealDictCursor)

    # DB 데이터 분석
    cur.execute("""
        SELECT
            MIN(payment_date) as min_date,
            MAX(payment_date) as max_date,
            COUNT(*) as total,
            COUNT(DISTINCT customer_id) as unique_customers
        FROM payments
    """)
    db_stats = cur.fetchone()

    print("\n📊 DB 데이터 분석:")
    print(f"- 전체 건수: {db_stats['total']}")
    print(f"- 날짜 범위: {db_stats['min_date']} ~ {db_stats['max_date']}")
    print(f"- 고유 고객: {db_stats['unique_customers']}")

    # 고객명 매칭 확인
    print("\n🔍 고객명 매칭 테스트:")

    # Excel의 처음 10명 고객
    excel_customers = df_excel['고객명'].unique()[:10]

    for customer in excel_customers:
        cur.execute("""
            SELECT COUNT(*) as count
            FROM customers
            WHERE name = %s
        """, (customer,))
        result = cur.fetchone()

        if result['count'] == 0:
            print(f"  ❌ '{customer}' - DB에 없음")
        else:
            # 해당 고객의 결제 확인
            cur.execute("""
                SELECT COUNT(*) as payment_count
                FROM payments p
                JOIN customers c ON p.customer_id = c.customer_id
                WHERE c.name = %s
            """, (customer,))
            payment_result = cur.fetchone()
            print(f"  ✅ '{customer}' - 고객 존재, 결제 {payment_result['payment_count']}건")

    # 날짜별 분포 확인
    print("\n📅 월별 데이터 분포:")

    # Excel 월별 분포
    df_excel['month'] = pd.to_datetime(df_excel['결제일자']).dt.to_period('M')
    excel_monthly = df_excel.groupby('month').size()

    print("\nExcel 월별:")
    for month, count in excel_monthly.head(6).items():
        print(f"  {month}: {count}건")

    # DB 월별 분포
    cur.execute("""
        SELECT
            DATE_TRUNC('month', payment_date) as month,
            COUNT(*) as count
        FROM payments
        WHERE payment_date >= '2024-01-01'
        GROUP BY DATE_TRUNC('month', payment_date)
        ORDER BY month
        LIMIT 6
    """)

    print("\nDB 월별:")
    for row in cur.fetchall():
        print(f"  {row['month'].strftime('%Y-%m')}: {row['count']}건")

    # 문제 진단
    print("\n🔍 문제 진단:")

    # 1. 날짜 범위 겹침 확인
    if db_stats['max_date'] < df_excel['결제일자'].min().date():
        print("❌ DB와 Excel의 날짜 범위가 전혀 겹치지 않음!")
        print(f"   DB 최신: {db_stats['max_date']}")
        print(f"   Excel 최초: {df_excel['결제일자'].min().date()}")

    # 2. 고객 이름 인코딩 문제 확인
    cur.execute("""
        SELECT DISTINCT name
        FROM customers
        WHERE name LIKE '%김%'
        LIMIT 5
    """)
    db_kim_customers = [row['name'] for row in cur.fetchall()]
    excel_kim_customers = [c for c in df_excel['고객명'].unique() if '김' in str(c)][:5]

    print("\n이름 인코딩 확인:")
    print(f"  DB 김씨: {db_kim_customers}")
    print(f"  Excel 김씨: {excel_kim_customers}")

    cur.close()
    conn.close()

if __name__ == "__main__":
    check_data_mismatch()
