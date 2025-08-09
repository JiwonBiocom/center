#!/usr/bin/env python3
"""
2023년 데이터 불일치를 상세 분석하는 스크립트
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
from datetime import datetime
from sqlalchemy import create_engine, text
from tabulate import tabulate
from collections import defaultdict
import warnings
warnings.filterwarnings('ignore')

# 직접 DB 연결 설정
from dotenv import load_dotenv
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)

# 엑셀 파일 경로
EXCEL_PATH = "/Users/vibetj/coding/center/docs/AIBIO 관리대장 파일모음/★2025년 AIBIO 결제현황.xlsx"

def analyze_2023_excel():
    """엑셀에서 2023년 데이터 분석"""
    print("📊 엑셀 파일에서 2023년 데이터 분석")
    print("-" * 60)

    # 전체 시트 목록 확인
    xls = pd.ExcelFile(EXCEL_PATH)

    # 2023년 관련 시트 찾기
    sheets_2023 = []
    for sheet in xls.sheet_names:
        if '23년' in sheet or '2023' in sheet:
            sheets_2023.append(sheet)

    print(f"2023년 관련 시트: {sheets_2023}")

    # 각 시트의 데이터 확인
    total_count = 0
    total_amount = 0
    sheet_data = []

    for sheet_name in sheets_2023:
        try:
            # 시트 읽기 (헤더는 2번째 행)
            df = pd.read_excel(EXCEL_PATH, sheet_name=sheet_name, header=2)

            # 컬럼명 정규화
            df.columns = [str(col).strip() for col in df.columns]

            # 필수 컬럼 찾기
            date_col = None
            amount_col = None

            for col in df.columns:
                if '결제일자' in col or '일자' in col:
                    date_col = col
                elif '결제 금액' in col or '결제금액' in col or '금액' in col:
                    amount_col = col

            if date_col and amount_col:
                # 유효한 데이터만 카운트
                valid_data = df[df[amount_col].notna() & (df[amount_col] > 0)]
                count = len(valid_data)
                amount = valid_data[amount_col].sum()

                total_count += count
                total_amount += amount

                sheet_data.append({
                    'sheet': sheet_name,
                    'count': count,
                    'amount': amount
                })

                print(f"\n{sheet_name}:")
                print(f"  건수: {count}, 금액: {amount:,}원")

        except Exception as e:
            print(f"  오류: {e}")

    print(f"\n엑셀 총계: {total_count}건, {total_amount:,}원")

    return sheet_data, total_count, total_amount

def analyze_2023_db():
    """DB에서 2023년 데이터 분석"""
    print("\n\n💾 데이터베이스에서 2023년 데이터 분석")
    print("-" * 60)

    with engine.connect() as conn:
        # 월별 데이터 집계
        query = text("""
            SELECT
                EXTRACT(MONTH FROM payment_date) as month,
                COUNT(*) as count,
                SUM(amount) as total_amount
            FROM payments
            WHERE EXTRACT(YEAR FROM payment_date) = 2023
            GROUP BY EXTRACT(MONTH FROM payment_date)
            ORDER BY month
        """)

        result = conn.execute(query)

        monthly_data = []
        total_count = 0
        total_amount = 0

        for row in result:
            month = int(row.month)
            count = row.count
            amount = row.total_amount or 0

            monthly_data.append({
                'month': f"2023-{month:02d}",
                'count': count,
                'amount': amount
            })

            total_count += count
            total_amount += amount

        print("\nDB 월별 데이터:")
        for data in monthly_data:
            print(f"  {data['month']}: {data['count']}건, {data['amount']:,}원")

        print(f"\nDB 총계: {total_count}건, {total_amount:,}원")

        # 상위 10개 거래 확인
        print("\n\n상위 10개 거래:")
        query_top = text("""
            SELECT
                p.payment_date,
                c.name as customer_name,
                p.amount
            FROM payments p
            JOIN customers c ON p.customer_id = c.customer_id
            WHERE EXTRACT(YEAR FROM p.payment_date) = 2023
            ORDER BY p.amount DESC
            LIMIT 10
        """)

        result_top = conn.execute(query_top)

        print(tabulate(
            [(row.payment_date, row.customer_name, f"{row.amount:,}") for row in result_top],
            headers=['날짜', '고객명', '금액'],
            tablefmt='grid'
        ))

    return monthly_data, total_count, total_amount

def check_duplicate_entries():
    """중복 입력 가능성 체크"""
    print("\n\n🔍 중복 입력 가능성 체크")
    print("-" * 60)

    with engine.connect() as conn:
        query = text("""
            SELECT
                payment_date,
                customer_id,
                amount,
                COUNT(*) as duplicate_count
            FROM payments
            WHERE EXTRACT(YEAR FROM payment_date) = 2023
            GROUP BY payment_date, customer_id, amount
            HAVING COUNT(*) > 1
            ORDER BY duplicate_count DESC, payment_date
            LIMIT 10
        """)

        result = conn.execute(query)
        duplicates = list(result)

        if duplicates:
            print("동일한 날짜/고객/금액의 중복 거래:")
            for row in duplicates:
                print(f"  {row.payment_date}: 고객ID {row.customer_id}, {row.amount:,}원 - {row.duplicate_count}건")
        else:
            print("중복된 거래가 없습니다.")

def main():
    print("🚀 2023년 데이터 불일치 상세 분석")
    print("=" * 80)

    # 엑셀 분석
    excel_sheets, excel_count, excel_amount = analyze_2023_excel()

    # DB 분석
    db_monthly, db_count, db_amount = analyze_2023_db()

    # 차이 분석
    print("\n\n📊 분석 결과")
    print("=" * 80)
    print(f"엑셀: {excel_count}건, {excel_amount:,}원")
    print(f"DB: {db_count}건, {db_amount:,}원")
    print(f"차이: {db_count - excel_count}건, {db_amount - excel_amount:,}원")

    print("\n\n💡 분석 결론:")
    print("-" * 60)

    if db_count > excel_count:
        print(f"1. DB에 {db_count - excel_count}건의 추가 데이터가 있습니다.")
        print("   → 엑셀에 2023년 1-8월 시트가 누락되었을 가능성")
        print("   → 또는 DB에 중복 입력된 데이터가 있을 가능성")

    if abs(db_amount - excel_amount) > 0:
        print(f"\n2. 금액 차이: {abs(db_amount - excel_amount):,}원")
        print("   → 개별 거래 금액 확인 필요")

    # 중복 체크
    check_duplicate_entries()

    print("\n\n📋 권장 조치:")
    print("-" * 60)
    print("1. 2023년 1-8월 엑셀 시트 존재 여부 확인")
    print("2. DB의 2023년 데이터 출처 확인")
    print("3. 중복 입력된 데이터 정리")
    print("4. 개별 거래 금액 대조 확인")

if __name__ == "__main__":
    main()
