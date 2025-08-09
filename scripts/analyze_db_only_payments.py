#!/usr/bin/env python3
"""
DB에만 있는 102건 결제 데이터 상세 분석
"""
import pandas as pd
import psycopg2
from psycopg2.extras import RealDictCursor
import os
import re

# DB 연결
DB_CONFIG = {
    'host': 'aws-0-ap-northeast-2.pooler.supabase.com',
    'port': 6543,
    'database': 'postgres',
    'user': 'postgres.wvcxzyvmwwrbjpeuyvuh',
    'password': 'bico6819!!'
}

def main():
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor(cursor_factory=RealDictCursor)

    # 1. DB에서 모든 결제 데이터 가져오기
    cur.execute('''
        SELECT p.payment_date, c.name as customer_name, p.amount, p.payment_staff,
               p.payment_method, p.notes, p.created_at
        FROM payments p
        JOIN customers c ON p.customer_id = c.customer_id
        ORDER BY p.payment_date, p.amount
    ''')
    db_payments = cur.fetchall()
    print(f'DB 총 결제: {len(db_payments)}건')

    # 2. 엑셀에서 결제 데이터 가져오기
    excel_path = '/Users/vibetj/coding/center/docs/AIBIO 관리대장 파일모음/★2025년 AIBIO 결제현황.xlsx'
    df = pd.read_excel(excel_path, sheet_name='전체 결제대장', skiprows=2)

    excel_payments = []
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

            payment_date = pd.to_datetime(row.get('결제일자')).date() if pd.notna(row.get('결제일자')) else None
            staff = str(row.get('결제 담당자', '')).strip()

            excel_payments.append({
                'payment_date': payment_date,
                'customer_name': customer_name,
                'amount': amount,
                'payment_staff': staff if staff and staff != 'nan' else None
            })
        except:
            continue

    print(f'엑셀 총 결제: {len(excel_payments)}건')

    # 3. DB에만 있는 데이터 찾기 (날짜+금액+고객명 기준)
    db_only = []
    for db_payment in db_payments:
        matched = False
        for excel_payment in excel_payments:
            if (db_payment['payment_date'] == excel_payment['payment_date'] and
                abs(float(db_payment['amount']) - float(excel_payment['amount'])) < 0.01 and
                db_payment['customer_name'] == excel_payment['customer_name']):
                matched = True
                break

        if not matched:
            db_only.append(db_payment)

    print(f'DB에만 있는 데이터: {len(db_only)}건')

    # 월별 분석
    monthly_stats = {}
    for payment in db_only:
        month_key = payment['payment_date'].strftime('%Y-%m')
        if month_key not in monthly_stats:
            monthly_stats[month_key] = []
        monthly_stats[month_key].append(payment)

    # 결과를 파일에 저장
    with open('db_only_payments_102.txt', 'w', encoding='utf-8') as f:
        f.write('# DB에만 있는 결제 데이터 상세 목록\n')
        f.write('# (엑셀 파일에는 없고 데이터베이스에만 존재하는 결제)\n\n')
        f.write(f'총 {len(db_only)}건\n\n')

        # 월별 요약
        f.write('## 월별 요약\n')
        for month, payments in sorted(monthly_stats.items()):
            total_amount = sum(p['amount'] for p in payments)
            f.write(f'{month}: {len(payments):2d}건, 총 {total_amount:>12,.0f}원\n')
        f.write('\n' + '='*80 + '\n\n')

        # 상세 목록
        f.write('## 상세 목록\n')
        f.write('번호 | 결제일     | 고객명       | 결제금액      | 담당자   | 결제방법              | 생성일시\n')
        f.write('-'*100 + '\n')

        for i, payment in enumerate(db_only, 1):
            created_at = payment['created_at'].strftime('%m-%d %H:%M') if payment['created_at'] else 'N/A'
            f.write(f'{i:3d}  | {payment["payment_date"]} | {payment["customer_name"]:12s} | {payment["amount"]:>10,.0f}원 | {payment["payment_staff"] or "미지정":8s} | {payment["payment_method"] or "":20s} | {created_at}\n')

    conn.close()
    print('\n✅ db_only_payments_102.txt 파일에 상세 목록 저장 완료')

if __name__ == "__main__":
    main()
