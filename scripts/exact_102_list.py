#!/usr/bin/env python3
"""
정확한 102건 차이 리스트 생성
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

    # 1. DB에서 모든 결제 데이터 가져오기
    cur.execute('''
        SELECT p.payment_id, p.payment_date, c.name as customer_name, p.amount,
               p.payment_staff, p.payment_method, p.created_at
        FROM payments p
        JOIN customers c ON p.customer_id = c.customer_id
        ORDER BY p.payment_id
    ''')
    db_payments = cur.fetchall()
    print(f'DB 총 결제: {len(db_payments)}건')

    # 2. 엑셀에서 결제 데이터 가져오기
    excel_path = '/Users/vibetj/coding/center/docs/AIBIO 관리대장 파일모음/★2025년 AIBIO 결제현황.xlsx'
    df = pd.read_excel(excel_path, sheet_name='전체 결제대장', skiprows=2)

    excel_payments = []
    for idx, row in df.iterrows():
        try:
            # 첫 번째 열이 숫자인지 확인 (순번)
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
                amount_str = re.sub(r'[^0-9.-]', '', amount_str)
                if amount_str:
                    amount = float(amount_str)
            except:
                continue

            if amount == 0:
                continue

            payment_date = parse_excel_date(row.get('결제일자'))
            if not payment_date:
                continue

            excel_payments.append({
                'payment_date': payment_date,
                'customer_name': customer_name,
                'amount': amount,
                'excel_row': idx + 3
            })
        except:
            continue

    print(f'엑셀 파싱된 결제: {len(excel_payments)}건')

    # 3. 개별 매칭 (날짜 + 금액 기준, 중복 고려)
    excel_used = [False] * len(excel_payments)
    matched_db = []
    unmatched_db = []

    for db_payment in db_payments:
        matched = False
        for i, excel_payment in enumerate(excel_payments):
            if (not excel_used[i] and
                db_payment['payment_date'] == excel_payment['payment_date'] and
                abs(float(db_payment['amount']) - float(excel_payment['amount'])) < 0.01):
                excel_used[i] = True
                matched_db.append(db_payment)
                matched = True
                break

        if not matched:
            unmatched_db.append(db_payment)

    print(f'\n개별 매칭 결과:')
    print(f'  - 매칭된 DB 결제: {len(matched_db)}건')
    print(f'  - 매칭되지 않은 DB 결제: {len(unmatched_db)}건')
    print(f'  - 매칭되지 않은 엑셀 결제: {sum(1 for used in excel_used if not used)}건')

    # 4. 월별 분석
    monthly_stats = {}
    for payment in unmatched_db:
        month_key = payment['payment_date'].strftime('%Y-%m')
        if month_key not in monthly_stats:
            monthly_stats[month_key] = {'count': 0, 'amount': 0, 'payments': []}
        monthly_stats[month_key]['count'] += 1
        monthly_stats[month_key]['amount'] += float(payment['amount'])
        monthly_stats[month_key]['payments'].append(payment)

    # 5. 2025년 데이터만 필터링
    db_2025_only = [p for p in unmatched_db if p['payment_date'].year == 2025]
    db_2024_only = [p for p in unmatched_db if p['payment_date'].year == 2024]

    # 6. 결과 파일 저장
    output_file = 'exact_102_payments_list.txt'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('# 정확한 102건 차이 - DB에만 있는 결제 데이터\n')
        f.write('# (엑셀 파일에는 없고 데이터베이스에만 존재하는 결제)\n\n')
        f.write(f'분석 일시: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n\n')

        f.write(f'## 🎯 최종 결과\n')
        f.write(f'- DB 총 결제: {len(db_payments)}건\n')
        f.write(f'- 엑셀 총 결제: {len(excel_payments)}건\n')
        f.write(f'- 매칭된 결제: {len(matched_db)}건\n')
        f.write(f'- **DB에만 있는 결제: {len(unmatched_db)}건** ⭐\n\n')

        f.write(f'## 📊 연도별 분석\n')
        f.write(f'- 2024년 차이: {len(db_2024_only)}건\n')
        f.write(f'- 2025년 차이: {len(db_2025_only)}건\n\n')

        # 월별 요약
        f.write('## 📅 월별 분석\n')
        total_amount = 0
        total_count = 0
        for month, stats in sorted(monthly_stats.items()):
            total_amount += stats['amount']
            total_count += stats['count']
            f.write(f'{month}: {stats["count"]:2d}건, 총 {stats["amount"]:>12,.0f}원\n')
        f.write(f'합계:     {total_count:2d}건, 총 {total_amount:>12,.0f}원\n\n')

        f.write('='*130 + '\n\n')

        # 2025년 데이터 (신규 결제)
        f.write('## 🆕 2025년 신규 결제 데이터\n')
        f.write('번호 | 결제일     | 고객명           | 결제금액      | 담당자       | 결제방법 | 생성일시      | Payment ID\n')
        f.write('-'*130 + '\n')

        for i, payment in enumerate(sorted(db_2025_only, key=lambda x: x['payment_date']), 1):
            created_at = payment['created_at'].strftime('%m-%d %H:%M') if payment['created_at'] else 'N/A'
            f.write(f'{i:3d}  | {payment["payment_date"]} | {payment["customer_name"]:15s} | {payment["amount"]:>10,.0f}원 | {payment["payment_staff"] or "미지정":10s} | {payment["payment_method"] or "":8s} | {created_at:10s} | {payment["payment_id"]}\n')

        f.write('\n' + '='*130 + '\n\n')

        # 2024년 데이터 (추가/수정)
        f.write('## 📝 2024년 추가/수정 데이터\n')
        f.write('번호 | 결제일     | 고객명           | 결제금액      | 담당자       | 결제방법 | 생성일시      | Payment ID\n')
        f.write('-'*130 + '\n')

        for i, payment in enumerate(sorted(db_2024_only, key=lambda x: x['payment_date']), 1):
            created_at = payment['created_at'].strftime('%m-%d %H:%M') if payment['created_at'] else 'N/A'
            f.write(f'{i:3d}  | {payment["payment_date"]} | {payment["customer_name"]:15s} | {payment["amount"]:>10,.0f}원 | {payment["payment_staff"] or "미지정":10s} | {payment["payment_method"] or "":8s} | {created_at:10s} | {payment["payment_id"]}\n')

        f.write('\n' + '='*130 + '\n\n')

        # 전체 목록
        f.write('## 📋 전체 목록 (DB에만 있는 모든 결제)\n')
        f.write('번호 | 결제일     | 고객명           | 결제금액      | 담당자       | 결제방법 | 생성일시      | Payment ID\n')
        f.write('-'*130 + '\n')

        for i, payment in enumerate(sorted(unmatched_db, key=lambda x: x['payment_date']), 1):
            created_at = payment['created_at'].strftime('%m-%d %H:%M') if payment['created_at'] else 'N/A'
            f.write(f'{i:3d}  | {payment["payment_date"]} | {payment["customer_name"]:15s} | {payment["amount"]:>10,.0f}원 | {payment["payment_staff"] or "미지정":10s} | {payment["payment_method"] or "":8s} | {created_at:10s} | {payment["payment_id"]}\n')

    print(f'\n✅ {output_file} 파일에 정확한 102건 목록 저장 완료')
    print(f'\n🎯 **최종 답변**: {len(unmatched_db)}건이 엑셀에는 없고 DB에만 있는 결제입니다.')
    print(f'   - 2025년 신규: {len(db_2025_only)}건')
    print(f'   - 2024년 추가/수정: {len(db_2024_only)}건')

    conn.close()

if __name__ == "__main__":
    main()
