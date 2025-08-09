#!/usr/bin/env python3
"""
DB와 엑셀 데이터 매칭 디버깅
"""
import pandas as pd
import psycopg2
from psycopg2.extras import RealDictCursor
import re
from datetime import datetime

# DB 연결
DB_CONFIG = {
    'host': 'aws-0-ap-northeast-2.pooler.supabase.com',
    'port': 6543,
    'database': 'postgres',
    'user': 'postgres.wvcxzyvmwwrbjpeuyvuh',
    'password': 'bico6819!!'
}

def parse_excel_date(date_value):
    """엑셀 날짜 파싱"""
    if pd.isna(date_value):
        return None

    try:
        if isinstance(date_value, (datetime, pd.Timestamp)):
            return date_value.date()

        date_str = str(date_value).strip()
        if not date_str or date_str.lower() in ['none', 'nan', '']:
            return None

        # 다양한 날짜 형식 시도
        for fmt in ['%Y-%m-%d', '%Y/%m/%d', '%Y.%m.%d', '%m/%d/%Y', '%d/%m/%Y']:
            try:
                return datetime.strptime(date_str, fmt).date()
            except ValueError:
                continue

        return None
    except:
        return None

def main():
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor(cursor_factory=RealDictCursor)

    # DB 샘플 데이터 (처음 10건)
    cur.execute('''
        SELECT p.payment_date, c.name as customer_name, p.amount
        FROM payments p
        JOIN customers c ON p.customer_id = c.customer_id
        ORDER BY p.payment_date, p.amount
        LIMIT 10
    ''')
    db_sample = cur.fetchall()

    print("=== DB 샘플 (처음 10건) ===")
    for i, payment in enumerate(db_sample, 1):
        print(f"{i:2d}. {payment['payment_date']} | {payment['customer_name']:15s} | {payment['amount']:>10,.0f}원")

    # 엑셀 샘플 데이터
    excel_path = '/Users/vibetj/coding/center/docs/AIBIO 관리대장 파일모음/★2025년 AIBIO 결제현황.xlsx'
    df = pd.read_excel(excel_path, sheet_name='전체 결제대장', skiprows=2)

    print(f"\n=== 엑셀 컬럼명 ===")
    print(list(df.columns))

    print(f"\n=== 엑셀 샘플 (처음 10건) ===")
    excel_sample = []
    count = 0

    for idx, row in df.iterrows():
        if count >= 10:
            break

        try:
            # 첫 번째 열이 숫자인지 확인
            no_value = row.iloc[0]
            if pd.isna(no_value):
                continue
            try:
                int(no_value)
            except:
                continue

            customer_name = str(row.get('고객명', '')).strip()
            if not customer_name or customer_name == 'nan':
                continue

            # 결제 금액 파싱
            amount_str = str(row.get('결제 금액', 0))
            amount = 0
            try:
                amount_str = re.sub(r'[^0-9.]', '', amount_str)
                if amount_str:
                    amount = float(amount_str)
            except:
                continue

            if amount <= 0:
                continue

            payment_date = parse_excel_date(row.get('결제일자'))
            if not payment_date:
                continue

            count += 1
            print(f"{count:2d}. {payment_date} | {customer_name:15s} | {amount:>10,.0f}원")

        except Exception as e:
            print(f"엑셀 행 {idx} 처리 오류: {e}")
            continue

    # 고객명 비교
    print(f"\n=== 고객명 비교 (DB vs 엑셀) ===")
    cur.execute("SELECT DISTINCT name FROM customers ORDER BY name LIMIT 20")
    db_customers = [row['name'] for row in cur.fetchall()]

    excel_customers = set()
    for idx, row in df.iterrows():
        try:
            no_value = row.iloc[0]
            if pd.isna(no_value):
                continue
            try:
                int(no_value)
            except:
                continue

            customer_name = str(row.get('고객명', '')).strip()
            if customer_name and customer_name != 'nan':
                excel_customers.add(customer_name)
                if len(excel_customers) >= 20:
                    break
        except:
            continue

    print("DB 고객명 (처음 20명):")
    for name in db_customers:
        print(f"  - '{name}'")

    print(f"\n엑셀 고객명 (처음 20명):")
    for name in sorted(list(excel_customers))[:20]:
        print(f"  - '{name}'")

    conn.close()

if __name__ == "__main__":
    main()
