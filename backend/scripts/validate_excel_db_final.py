#!/usr/bin/env python3
"""
엑셀 파일과 데이터베이스 간의 데이터 일치성을 검증하는 스크립트
2025년 3월 이전의 모든 데이터를 검사합니다.
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
from datetime import datetime
import datetime as dt
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session
from tabulate import tabulate
from collections import defaultdict
import warnings
warnings.filterwarnings('ignore')

# 직접 DB 연결 설정
from dotenv import load_dotenv
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    print("❌ DATABASE_URL 환경 변수가 설정되지 않았습니다.")
    sys.exit(1)

engine = create_engine(DATABASE_URL)

# 엑셀 파일 경로
EXCEL_PATH = "/Users/vibetj/coding/center/docs/AIBIO 관리대장 파일모음/★2025년 AIBIO 결제현황.xlsx"

def parse_date_safely(date_value):
    """날짜를 안전하게 파싱"""
    if pd.isna(date_value):
        return None

    if isinstance(date_value, datetime):
        return date_value

    if isinstance(date_value, pd.Timestamp):
        return date_value.to_pydatetime()

    if isinstance(date_value, str):
        # 다양한 날짜 형식 시도
        formats = ['%Y-%m-%d', '%Y.%m.%d', '%Y/%m/%d', '%d-%m-%Y', '%d.%m.%Y', '%d/%m/%Y']
        for fmt in formats:
            try:
                return datetime.strptime(date_value.strip(), fmt)
            except:
                continue

    return None

def parse_amount_safely(amount_value):
    """금액을 안전하게 파싱"""
    if pd.isna(amount_value):
        return 0

    if isinstance(amount_value, (int, float)):
        return int(amount_value)

    if isinstance(amount_value, str):
        # 숫자가 아닌 문자 제거
        amount_str = amount_value.replace(',', '').replace('원', '').replace(' ', '')
        try:
            return int(float(amount_str))
        except:
            return 0

    return 0

def extract_year_month_from_sheet_name(sheet_name):
    """시트 이름에서 연도와 월 추출"""
    import re

    # 패턴 1: "2025년 5월"
    match = re.search(r'(\d{4})년\s*(\d{1,2})월', sheet_name)
    if match:
        return int(match.group(1)), int(match.group(2))

    # 패턴 2: "23년 5월" 또는 "23년5월"
    match = re.search(r'(\d{2})년\s*(\d{1,2})월', sheet_name)
    if match:
        year = 2000 + int(match.group(1))
        return year, int(match.group(2))

    # 패턴 3: "23 3월"
    match = re.search(r'(\d{2})\s+(\d{1,2})월', sheet_name)
    if match:
        year = 2000 + int(match.group(1))
        return year, int(match.group(2))

    # 패턴 4: 단순 월 이름 (1월, 2월 등) - 2022년으로 가정
    match = re.search(r'^(\d{1,2})월$', sheet_name)
    if match:
        return 2022, int(match.group(1))

    return None, None

def read_excel_data():
    """엑셀 파일에서 모든 시트의 데이터를 읽기"""
    print(f"\n📊 엑셀 파일 읽기: {EXCEL_PATH}")

    all_data = []
    sheet_summary = {}

    try:
        # 모든 시트 이름 가져오기
        xls = pd.ExcelFile(EXCEL_PATH)
        sheet_names = xls.sheet_names

        print(f"\n시트 목록: {len(sheet_names)}개")

        # 월별 시트만 처리 (전체매출, 전체 결제대장, 2022합계 제외)
        skip_sheets = ['전체매출', '전체 결제대장', '2022합계']

        for sheet_name in sheet_names:
            if sheet_name in skip_sheets:
                continue

            # 시트에서 연도/월 추출
            year, month = extract_year_month_from_sheet_name(sheet_name)
            if not year or not month:
                continue

            # 헤더 위치 결정 (2022년은 3, 나머지는 2)
            header_row = 3 if year == 2022 else 2

            try:
                # 시트 읽기
                df = pd.read_excel(EXCEL_PATH, sheet_name=sheet_name, header=header_row)

                # 빈 시트 건너뛰기
                if df.empty:
                    continue

                # 컬럼명 정규화
                df.columns = [str(col).strip() for col in df.columns]

                # 필수 컬럼 찾기
                date_col = None
                amount_col = None
                customer_col = None

                for col in df.columns:
                    if '결제일자' in col or '일자' in col:
                        date_col = col
                    elif '결제 금액' in col or '결제금액' in col or '금액' in col:
                        amount_col = col
                    elif '고객명' in col or '고객' in col:
                        customer_col = col

                if not date_col or not amount_col:
                    continue

                valid_count = 0
                total_amount = 0

                # 데이터 처리
                for idx, row in df.iterrows():
                    # 날짜 파싱
                    date_value = parse_date_safely(row[date_col])
                    if not date_value:
                        continue

                    # 2025년 3월 이전 데이터만
                    if date_value >= datetime(2025, 3, 1):
                        continue

                    # 금액 파싱
                    amount = parse_amount_safely(row[amount_col])
                    if amount <= 0:
                        continue

                    # 고객명
                    customer_name = str(row[customer_col]).strip() if customer_col and pd.notna(row[customer_col]) else 'Unknown'

                    all_data.append({
                        'sheet_name': sheet_name,
                        'date': date_value,
                        'amount': amount,
                        'customer_name': customer_name,
                        'year': date_value.year,
                        'month': date_value.month,
                        'sheet_year': year,
                        'sheet_month': month
                    })

                    valid_count += 1
                    total_amount += amount

                if valid_count > 0:
                    sheet_summary[sheet_name] = {
                        'count': valid_count,
                        'total_amount': total_amount,
                        'year': year,
                        'month': month
                    }
                    print(f"✅ {sheet_name}: {valid_count}건, {total_amount:,}원")

            except Exception as e:
                print(f"❌ {sheet_name} 시트 처리 중 오류: {e}")
                continue

    except Exception as e:
        print(f"❌ 엑셀 파일 읽기 오류: {e}")
        import traceback
        traceback.print_exc()
        return [], {}

    return all_data, sheet_summary

def get_db_data():
    """데이터베이스에서 2025년 3월 이전의 모든 결제 데이터 가져오기"""
    print("\n💾 데이터베이스 데이터 읽기...")

    with engine.connect() as conn:
        query = text("""
            SELECT
                p.payment_date,
                p.amount,
                c.name as customer_name,
                p.payment_id,
                EXTRACT(YEAR FROM p.payment_date) as year,
                EXTRACT(MONTH FROM p.payment_date) as month
            FROM payments p
            JOIN customers c ON p.customer_id = c.customer_id
            WHERE p.payment_date < '2025-03-01'
            ORDER BY p.payment_date
        """)

        result = conn.execute(query)
        db_data = []

        for row in result:
            db_data.append({
                'date': row.payment_date,
                'amount': row.amount,
                'customer_name': row.customer_name,
                'payment_id': row.payment_id,
                'year': int(row.year),
                'month': int(row.month)
            })

    print(f"✅ DB에서 {len(db_data)}건의 데이터를 읽었습니다.")
    return db_data

def compare_data(excel_data, db_data):
    """엑셀과 DB 데이터 비교"""
    print("\n🔍 데이터 비교 분석 중...")

    # 연도별 집계
    excel_by_year = defaultdict(lambda: {'count': 0, 'amount': 0})
    db_by_year = defaultdict(lambda: {'count': 0, 'amount': 0})

    # 월별 집계
    excel_by_month = defaultdict(lambda: {'count': 0, 'amount': 0})
    db_by_month = defaultdict(lambda: {'count': 0, 'amount': 0})

    # 엑셀 데이터 집계
    for item in excel_data:
        year = item['year']
        month = f"{year}-{item['month']:02d}"

        excel_by_year[year]['count'] += 1
        excel_by_year[year]['amount'] += item['amount']

        excel_by_month[month]['count'] += 1
        excel_by_month[month]['amount'] += item['amount']

    # DB 데이터 집계
    for item in db_data:
        year = item['year']
        month = f"{year}-{item['month']:02d}"

        db_by_year[year]['count'] += 1
        db_by_year[year]['amount'] += item['amount']

        db_by_month[month]['count'] += 1
        db_by_month[month]['amount'] += item['amount']

    return {
        'excel_by_year': dict(excel_by_year),
        'db_by_year': dict(db_by_year),
        'excel_by_month': dict(excel_by_month),
        'db_by_month': dict(db_by_month)
    }

def find_missing_data(excel_data, db_data):
    """누락된 데이터 찾기"""
    # DB 데이터를 날짜/고객/금액으로 인덱싱
    db_index = set()
    for item in db_data:
        date_val = item['date'] if isinstance(item['date'], dt.date) else item['date'].date()
        key = (date_val, item['customer_name'], item['amount'])
        db_index.add(key)

    # 엑셀에만 있는 데이터 찾기
    missing_in_db = []
    for item in excel_data:
        date_val = item['date'] if isinstance(item['date'], dt.date) else item['date'].date()
        key = (date_val, item['customer_name'], item['amount'])
        if key not in db_index:
            missing_in_db.append(item)

    return missing_in_db

def generate_report(excel_data, db_data, sheet_summary, comparison):
    """상세 보고서 생성"""
    print("\n" + "="*80)
    print("📊 데이터 일치성 검증 보고서")
    print("="*80)

    # 1. 전체 데이터 요약
    print("\n1. 전체 데이터 요약 (2025년 3월 이전)")
    print("-"*60)
    total_excel = len(excel_data)
    total_excel_amount = sum(item['amount'] for item in excel_data)
    total_db = len(db_data)
    total_db_amount = sum(item['amount'] for item in db_data)

    summary_table = [
        ['엑셀 데이터', total_excel, f"{total_excel_amount:,}"],
        ['DB 데이터', total_db, f"{total_db_amount:,}"],
        ['차이', total_excel - total_db, f"{total_excel_amount - total_db_amount:,}"]
    ]

    print(tabulate(summary_table, headers=['구분', '건수', '총액(원)'], tablefmt='grid'))

    # 2. 연도별 비교
    print("\n2. 연도별 데이터 비교")
    print("-"*60)

    all_years = sorted(set(list(comparison['excel_by_year'].keys()) + list(comparison['db_by_year'].keys())))
    year_table = []

    for year in all_years:
        excel_info = comparison['excel_by_year'].get(year, {'count': 0, 'amount': 0})
        db_info = comparison['db_by_year'].get(year, {'count': 0, 'amount': 0})

        status = "✅" if excel_info['count'] == db_info['count'] and excel_info['amount'] == db_info['amount'] else "⚠️"

        year_table.append([
            f"{status} {year}",
            excel_info['count'],
            f"{excel_info['amount']:,}",
            db_info['count'],
            f"{db_info['amount']:,}",
            excel_info['count'] - db_info['count'],
            f"{excel_info['amount'] - db_info['amount']:,}"
        ])

    print(tabulate(year_table,
                   headers=['연도', '엑셀 건수', '엑셀 금액', 'DB 건수', 'DB 금액', '건수 차이', '금액 차이'],
                   tablefmt='grid'))

    # 3. 월별 불일치 항목
    print("\n3. 월별 불일치 항목 (상위 10개)")
    print("-"*60)

    mismatch_months = []
    for month in sorted(set(list(comparison['excel_by_month'].keys()) + list(comparison['db_by_month'].keys()))):
        excel_info = comparison['excel_by_month'].get(month, {'count': 0, 'amount': 0})
        db_info = comparison['db_by_month'].get(month, {'count': 0, 'amount': 0})

        if excel_info['count'] != db_info['count'] or excel_info['amount'] != db_info['amount']:
            mismatch_months.append([
                month,
                excel_info['count'],
                f"{excel_info['amount']:,}",
                db_info['count'],
                f"{db_info['amount']:,}",
                excel_info['count'] - db_info['count'],
                f"{excel_info['amount'] - db_info['amount']:,}"
            ])

    if mismatch_months:
        print(tabulate(mismatch_months[:10],
                       headers=['월', '엑셀 건수', '엑셀 금액', 'DB 건수', 'DB 금액', '건수 차이', '금액 차이'],
                       tablefmt='grid'))
        if len(mismatch_months) > 10:
            print(f"\n... 외 {len(mismatch_months) - 10}개월의 불일치가 더 있습니다.")
    else:
        print("✅ 모든 월별 데이터가 일치합니다!")

    # 4. 누락된 데이터 샘플
    missing_data = find_missing_data(excel_data, db_data)
    if missing_data:
        print(f"\n4. 엑셀에만 있는 데이터 (총 {len(missing_data)}건 중 10건)")
        print("-"*60)
        sample_table = []
        for item in missing_data[:10]:
            sample_table.append([
                item['date'].strftime('%Y-%m-%d'),
                item['customer_name'],
                f"{item['amount']:,}",
                item['sheet_name']
            ])
        print(tabulate(sample_table, headers=['날짜', '고객명', '금액', '시트'], tablefmt='grid'))

    # 5. 권장 조치사항
    print("\n5. 검증 결과 및 권장 조치사항")
    print("-"*60)

    # 주요 발견사항
    print("\n📌 주요 발견사항:")

    # 2022-2024년 데이터 상세
    for year in [2022, 2023, 2024]:
        excel_count = comparison['excel_by_year'].get(year, {'count': 0})['count']
        db_count = comparison['db_by_year'].get(year, {'count': 0})['count']
        excel_amount = comparison['excel_by_year'].get(year, {'amount': 0})['amount']
        db_amount = comparison['db_by_year'].get(year, {'amount': 0})['amount']

        if excel_count > 0 or db_count > 0:
            status = "✅ 일치" if excel_count == db_count else "⚠️ 불일치"
            print(f"  • {year}년: {status}")
            print(f"    - 엑셀: {excel_count}건, {excel_amount:,}원")
            print(f"    - DB: {db_count}건, {db_amount:,}원")
            if excel_count != db_count:
                print(f"    - 차이: {excel_count - db_count}건, {excel_amount - db_amount:,}원")

    # 권장 조치
    print("\n📋 권장 조치사항:")

    if total_excel > total_db:
        print(f"\n1. 데이터 누락")
        print(f"   - 엑셀에 {total_excel - total_db}건의 추가 데이터가 있습니다.")
        print(f"   - 금액 차이: {total_excel_amount - total_db_amount:,}원")
        print(f"   - 조치: scripts/migrate_missing_payments.py 실행 권장")
    elif total_db > total_excel:
        print(f"\n1. DB 추가 데이터")
        print(f"   - DB에 {total_db - total_excel}건의 추가 데이터가 있습니다.")
        print(f"   - 조치: DB의 추가 데이터 검토 필요")
    else:
        print("\n1. 데이터 건수 일치 ✅")

    if total_excel_amount != total_db_amount:
        print(f"\n2. 금액 불일치")
        print(f"   - 차이: {abs(total_excel_amount - total_db_amount):,}원")
        print(f"   - 조치: 개별 거래 금액 상세 검토 필요")
    else:
        print("\n2. 금액 일치 ✅")

    # 데이터 품질
    print(f"\n3. 데이터 품질")
    print(f"   - 엑셀 시트 수: {len(sheet_summary)}개")
    print(f"   - 처리된 데이터: {total_excel}건")
    print(f"   - 평균 거래 금액: {total_excel_amount // total_excel if total_excel > 0 else 0:,}원")

def main():
    """메인 실행 함수"""
    print("🚀 엑셀-DB 데이터 일치성 검증 시작")
    print(f"대상 기간: 2025년 3월 이전 모든 데이터")
    print(f"검증 시각: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # 엑셀 데이터 읽기
    excel_data, sheet_summary = read_excel_data()

    if not excel_data:
        print("❌ 엑셀 데이터를 읽을 수 없습니다.")
        return

    print(f"\n✅ 엑셀에서 총 {len(excel_data)}건의 데이터를 읽었습니다.")

    # DB 데이터 읽기
    db_data = get_db_data()

    # 데이터 비교
    comparison = compare_data(excel_data, db_data)

    # 보고서 생성
    generate_report(excel_data, db_data, sheet_summary, comparison)

    print("\n" + "="*80)
    print("✅ 검증 완료")
    print("="*80)

if __name__ == "__main__":
    main()
