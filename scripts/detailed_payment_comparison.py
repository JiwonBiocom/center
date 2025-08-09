#!/usr/bin/env python3
"""
DB와 엑셀 결제 데이터 정교한 비교 분석
"""
import pandas as pd
import psycopg2
from psycopg2.extras import RealDictCursor
import os
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

    # 1. DB에서 모든 결제 데이터 가져오기
    cur.execute('''
        SELECT p.payment_id, p.payment_date, c.name as customer_name, p.amount,
               p.payment_staff, p.payment_method, p.created_at
        FROM payments p
        JOIN customers c ON p.customer_id = c.customer_id
        ORDER BY p.payment_date, p.amount
    ''')
    db_payments = cur.fetchall()
    print(f'DB 총 결제: {len(db_payments)}건')

    # 2. 엑셀에서 결제 데이터 가져오기
    excel_path = '/Users/vibetj/coding/center/docs/AIBIO 관리대장 파일모음/★2025년 AIBIO 결제현황.xlsx'
    df = pd.read_excel(excel_path, sheet_name='전체 결제대장', skiprows=2)
    print(f'엑셀 원본 행 수: {len(df)}')

    excel_payments = []
    excel_valid_count = 0

    for idx, row in df.iterrows():
        try:
            # 첫 번째 열이 숫자인지 확인 (순번)
            no_value = row.iloc[0]
            if pd.isna(no_value):
                continue
            try:
                int(no_value)
                excel_valid_count += 1
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

            staff = str(row.get('결제 담당자', '')).strip()

            excel_payments.append({
                'excel_row': idx + 3,  # skiprows=2이므로 +3
                'payment_date': payment_date,
                'customer_name': customer_name,
                'amount': amount,
                'payment_staff': staff if staff and staff != 'nan' else None
            })
        except Exception as e:
            print(f"엑셀 행 {idx} 처리 오류: {e}")
            continue

    print(f'엑셀 유효 행: {excel_valid_count}개')
    print(f'엑셀 파싱된 결제: {len(excel_payments)}건')

    # 3. 정확한 매칭 (날짜 + 금액 + 고객명)
    matched_db = set()
    matched_excel = set()

    for i, db_payment in enumerate(db_payments):
        for j, excel_payment in enumerate(excel_payments):
            if (db_payment['payment_date'] == excel_payment['payment_date'] and
                abs(float(db_payment['amount']) - float(excel_payment['amount'])) < 0.01 and
                db_payment['customer_name'].strip() == excel_payment['customer_name'].strip()):
                matched_db.add(i)
                matched_excel.add(j)
                break

    # 4. DB에만 있는 데이터
    db_only = [db_payments[i] for i in range(len(db_payments)) if i not in matched_db]
    excel_only = [excel_payments[j] for j in range(len(excel_payments)) if j not in matched_excel]

    print(f'\n매칭 결과:')
    print(f'  - 매칭된 결제: {len(matched_db)}건')
    print(f'  - DB에만 있음: {len(db_only)}건')
    print(f'  - 엑셀에만 있음: {len(excel_only)}건')

    # 5. 월별 분석
    monthly_db_only = {}
    for payment in db_only:
        month_key = payment['payment_date'].strftime('%Y-%m')
        if month_key not in monthly_db_only:
            monthly_db_only[month_key] = []
        monthly_db_only[month_key].append(payment)

    # 6. 결과 파일 저장
    output_file = 'db_only_payments_detailed.txt'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('# DB에만 있는 결제 데이터 상세 분석\n')
        f.write('# (엑셀 파일에는 없고 데이터베이스에만 존재하는 결제)\n\n')
        f.write(f'분석 일시: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n\n')

        f.write(f'## 요약\n')
        f.write(f'- DB 총 결제: {len(db_payments)}건\n')
        f.write(f'- 엑셀 총 결제: {len(excel_payments)}건\n')
        f.write(f'- 매칭된 결제: {len(matched_db)}건\n')
        f.write(f'- **DB에만 있는 결제: {len(db_only)}건** ⭐\n')
        f.write(f'- 엑셀에만 있는 결제: {len(excel_only)}건\n\n')

        # 월별 요약
        f.write('## 월별 분석 (DB에만 있는 데이터)\n')
        total_amount = 0
        for month, payments in sorted(monthly_db_only.items()):
            month_amount = sum(p['amount'] for p in payments)
            total_amount += month_amount
            f.write(f'{month}: {len(payments):2d}건, 총 {month_amount:>12,.0f}원\n')
        f.write(f'합계:     {len(db_only):2d}건, 총 {total_amount:>12,.0f}원\n\n')

        f.write('='*120 + '\n\n')

        # 상세 목록
        f.write('## 상세 목록 (DB에만 있는 결제)\n')
        f.write('번호 | 결제일     | 고객명           | 결제금액      | 담당자       | 결제방법 | 생성일시      | Payment ID\n')
        f.write('-'*120 + '\n')

        for i, payment in enumerate(sorted(db_only, key=lambda x: x['payment_date']), 1):
            created_at = payment['created_at'].strftime('%m-%d %H:%M') if payment['created_at'] else 'N/A'
            f.write(f'{i:3d}  | {payment["payment_date"]} | {payment["customer_name"]:15s} | {payment["amount"]:>10,.0f}원 | {payment["payment_staff"] or "미지정":10s} | {payment["payment_method"] or "":8s} | {created_at:10s} | {payment["payment_id"]}\n')

    print(f'\n✅ {output_file} 파일에 상세 분석 결과 저장 완료')

    # 간단한 통계
    print(f'\n📊 주요 통계:')
    print(f'   매칭률: {len(matched_db)/len(db_payments)*100:.1f}%')
    print(f'   DB 초과분: {len(db_only)}건 ({len(db_only)/len(db_payments)*100:.1f}%)')

    conn.close()

if __name__ == "__main__":
    main()
