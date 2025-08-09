#!/usr/bin/env python3
"""
102건 차이의 최종 분석 - 날짜+금액 기준 매칭
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

            excel_payments.append({
                'payment_date': payment_date,
                'customer_name': customer_name,
                'amount': amount,
                'excel_row': idx + 3
            })
        except:
            continue

    print(f'엑셀 파싱된 결제: {len(excel_payments)}건')

    # 3. 날짜 + 금액만으로 매칭 (고객명 무시)
    db_date_amount = set()
    excel_date_amount = set()

    for payment in db_payments:
        key = (payment['payment_date'], float(payment['amount']))
        db_date_amount.add(key)

    for payment in excel_payments:
        key = (payment['payment_date'], float(payment['amount']))
        excel_date_amount.add(key)

    # 매칭되지 않는 DB 데이터
    unmatched_db_keys = db_date_amount - excel_date_amount

    # 매칭되지 않는 DB 결제들
    db_only_payments = []
    for payment in db_payments:
        key = (payment['payment_date'], float(payment['amount']))
        if key in unmatched_db_keys:
            db_only_payments.append(payment)

    print(f'\n날짜+금액 기준 분석:')
    print(f'  - DB 고유 (날짜+금액): {len(db_date_amount)}건')
    print(f'  - 엑셀 고유 (날짜+금액): {len(excel_date_amount)}건')
    print(f'  - 공통: {len(db_date_amount & excel_date_amount)}건')
    print(f'  - DB에만 있음: {len(unmatched_db_keys)}건')
    print(f'  - 엑셀에만 있음: {len(excel_date_amount - db_date_amount)}건')

    # 4. 월별 분석
    monthly_stats = {}
    for payment in db_only_payments:
        month_key = payment['payment_date'].strftime('%Y-%m')
        if month_key not in monthly_stats:
            monthly_stats[month_key] = {'count': 0, 'amount': 0, 'payments': []}
        monthly_stats[month_key]['count'] += 1
        monthly_stats[month_key]['amount'] += payment['amount']
        monthly_stats[month_key]['payments'].append(payment)

    # 5. 결과 파일 저장
    output_file = 'final_102_analysis.txt'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('# 최종 분석: DB에만 있는 결제 데이터 (날짜+금액 기준)\n')
        f.write('# 엑셀 파일에는 없고 데이터베이스에만 존재하는 결제\n\n')
        f.write(f'분석 일시: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n\n')

        f.write(f'## 핵심 발견사항\n')
        f.write(f'- 마이그레이션 시 고객 데이터와 결제 데이터가 **다른 소스**에서 임포트됨\n')
        f.write(f'- 고객명이 다르더라도 날짜+금액 조합으로 실제 차이를 분석\n')
        f.write(f'- **실제 차이: {len(unmatched_db_keys)}건**\n\n')

        f.write(f'## 요약 통계\n')
        f.write(f'- DB 총 결제: {len(db_payments)}건\n')
        f.write(f'- 엑셀 총 결제: {len(excel_payments)}건\n')
        f.write(f'- 공통 결제 (날짜+금액): {len(db_date_amount & excel_date_amount)}건\n')
        f.write(f'- **DB에만 있는 결제: {len(unmatched_db_keys)}건** ⭐\n\n')

        # 월별 요약
        f.write('## 월별 분석 (DB에만 있는 데이터)\n')
        total_amount = 0
        total_count = 0
        for month, stats in sorted(monthly_stats.items()):
            total_amount += stats['amount']
            total_count += stats['count']
            f.write(f'{month}: {stats["count"]:2d}건, 총 {stats["amount"]:>12,.0f}원\n')
        f.write(f'합계:     {total_count:2d}건, 총 {total_amount:>12,.0f}원\n\n')

        # 2025년 데이터만 분석
        f.write('## 2025년 데이터 분석\n')
        year_2025_count = sum(1 for month in monthly_stats.keys() if month.startswith('2025'))
        year_2025_payments = sum(stats['count'] for month, stats in monthly_stats.items() if month.startswith('2025'))
        year_2024_payments = sum(stats['count'] for month, stats in monthly_stats.items() if month.startswith('2024'))

        f.write(f'- 2024년 차이: {year_2024_payments}건\n')
        f.write(f'- 2025년 차이: {year_2025_payments}건\n')
        f.write(f'- **결론: {year_2025_payments}건이 2025년 신규 결제로 추정됨**\n\n')

        f.write('='*120 + '\n\n')

        # 상세 목록
        f.write('## 상세 목록 (DB에만 있는 결제)\n')
        f.write('번호 | 결제일     | 고객명           | 결제금액      | 담당자       | 결제방법 | 생성일시      | Payment ID\n')
        f.write('-'*120 + '\n')

        for i, payment in enumerate(sorted(db_only_payments, key=lambda x: x['payment_date']), 1):
            created_at = payment['created_at'].strftime('%m-%d %H:%M') if payment['created_at'] else 'N/A'
            f.write(f'{i:3d}  | {payment["payment_date"]} | {payment["customer_name"]:15s} | {payment["amount"]:>10,.0f}원 | {payment["payment_staff"] or "미지정":10s} | {payment["payment_method"] or "":8s} | {created_at:10s} | {payment["payment_id"]}\n')

    print(f'\n✅ {output_file} 파일에 최종 분석 결과 저장 완료')
    print(f'\n🎯 **최종 결론**: {len(unmatched_db_keys)}건이 엑셀에는 없고 DB에만 있는 실제 차이입니다.')

    conn.close()

if __name__ == "__main__":
    main()
