#!/usr/bin/env python3
"""
엑셀 파일과 데이터베이스의 데이터 일치성 검증 스크립트 (개선 버전)
"""
import os
import sys
import pandas as pd
from datetime import datetime
from decimal import Decimal
from collections import defaultdict
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
if not DATABASE_URL:
    print("❌ DATABASE_URL이 설정되지 않았습니다.")
    sys.exit(1)

engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

def find_header_row(df):
    """헤더 행 찾기"""
    keywords = ['날짜', '일자', '일수', '고객명', '이름', '성명', '금액', '결제금액']

    for idx in range(min(10, len(df))):
        row_values = df.iloc[idx].astype(str)
        if any(keyword in ' '.join(row_values) for keyword in keywords):
            return idx
    return None

def read_excel_data():
    """엑셀 파일에서 데이터 읽기 (개선 버전)"""
    excel_path = "/Users/vibetj/coding/center/docs/AIBIO 관리대장 파일모음/★2025년 AIBIO 결제현황.xlsx"

    if not os.path.exists(excel_path):
        print(f"❌ 엑셀 파일을 찾을 수 없습니다: {excel_path}")
        return None, None

    print(f"📊 엑셀 파일 읽기: {excel_path}")

    # 2025년 월별 시트 이름
    sheet_names_2025 = ['2025년 1월', '2025년 2월', '2025년 3월', '2025년 4월', '2025년 5월']

    all_data = []
    sheet_stats = {}

    for sheet_name in sheet_names_2025:
        try:
            print(f"\n  - {sheet_name} 시트 읽기...")

            # 먼저 헤더 없이 읽어서 구조 파악
            df_raw = pd.read_excel(excel_path, sheet_name=sheet_name, header=None)

            # 헤더 행 찾기
            header_row = find_header_row(df_raw)

            if header_row is not None:
                # 헤더 행을 기준으로 다시 읽기
                df = pd.read_excel(excel_path, sheet_name=sheet_name, header=header_row)

                # 컬럼명 정리
                df.columns = [str(col).strip() for col in df.columns]

                # 필요한 컬럼 찾기
                date_col = None
                name_col = None
                amount_col = None

                for col in df.columns:
                    if any(keyword in col for keyword in ['날짜', '일자', '일수']):
                        date_col = col
                    elif any(keyword in col for keyword in ['고객명', '이름', '성명']):
                        name_col = col
                    elif any(keyword in col for keyword in ['금액', '결제금액', '이용금액']) and '누적' not in col:
                        amount_col = col

                if name_col and amount_col:
                    print(f"    ✓ 컬럼 발견: {name_col}, {amount_col}")

                    # 데이터 추출
                    data_df = pd.DataFrame()
                    if date_col:
                        data_df['날짜'] = df[date_col]
                    data_df['고객명'] = df[name_col]
                    data_df['금액'] = pd.to_numeric(df[amount_col], errors='coerce')

                    # 유효한 데이터만 필터링
                    data_df = data_df.dropna(subset=['고객명', '금액'])
                    data_df = data_df[data_df['고객명'].str.strip() != '']
                    data_df = data_df[data_df['금액'] > 0]

                    # 월 정보 추가
                    month_num = int(sheet_name.split('년')[1].split('월')[0].strip())
                    data_df['월'] = month_num
                    data_df['시트명'] = sheet_name

                    # 통계 저장
                    sheet_stats[sheet_name] = {
                        'count': len(data_df),
                        'total_amount': data_df['금액'].sum(),
                        'month': month_num
                    }

                    all_data.append(data_df)
                    print(f"    ✓ {len(data_df)}개 유효한 레코드 발견")
                    print(f"    ✓ 총 금액: {data_df['금액'].sum():,.0f}원")
                else:
                    print(f"    ⚠️  필요한 컬럼을 찾을 수 없습니다")
                    print(f"       발견된 컬럼: {list(df.columns)[:10]}")
            else:
                print(f"    ⚠️  헤더를 찾을 수 없습니다")

        except Exception as e:
            print(f"    ❌ 오류 발생: {str(e)}")

    if all_data:
        combined_df = pd.concat(all_data, ignore_index=True)
        return combined_df, sheet_stats
    else:
        return pd.DataFrame(), {}

def get_db_data():
    """데이터베이스에서 2025년 1-5월 데이터 조회"""
    session = Session()

    try:
        # 먼저 전체 2025년 데이터 개수 확인
        count_query = text("""
            SELECT COUNT(*) as total_count
            FROM payments p
            WHERE p.payment_date >= '2025-01-01'
            AND p.payment_date < '2025-06-01'
        """)
        total_count = session.execute(count_query).scalar()
        print(f"\n📊 DB에서 2025년 1-5월 전체 결제 데이터: {total_count}건")

        # 엑셀 업로드 데이터만 조회
        query = text("""
            SELECT
                p.payment_id,
                p.customer_id,
                c.name as customer_name,
                p.payment_date,
                p.amount,
                p.notes,
                EXTRACT(MONTH FROM p.payment_date) as month
            FROM payments p
            JOIN customers c ON p.customer_id = c.customer_id
            WHERE p.payment_date >= '2025-01-01'
            AND p.payment_date < '2025-06-01'
            AND p.notes LIKE '%엑셀 업로드%'
            ORDER BY p.payment_date
        """)

        result = session.execute(query)
        db_data = []

        for row in result:
            db_data.append({
                'payment_id': row.payment_id,
                'customer_id': row.customer_id,
                'customer_name': row.customer_name,
                'payment_date': row.payment_date,
                'amount': float(row.amount),
                'notes': row.notes,
                'month': int(row.month)
            })

        print(f"  - 엑셀 업로드 데이터: {len(db_data)}건")

        # 월별 분포 확인
        monthly_query = text("""
            SELECT
                EXTRACT(MONTH FROM payment_date) as month,
                COUNT(*) as count,
                SUM(amount) as total_amount
            FROM payments
            WHERE payment_date >= '2025-01-01'
            AND payment_date < '2025-06-01'
            AND notes LIKE '%엑셀 업로드%'
            GROUP BY EXTRACT(MONTH FROM payment_date)
            ORDER BY month
        """)

        print("\n  월별 분포:")
        for row in session.execute(monthly_query):
            print(f"    - {int(row.month)}월: {row.count}건, {row.total_amount:,.0f}원")

        return pd.DataFrame(db_data)

    finally:
        session.close()

def compare_data(excel_df, excel_stats, db_df):
    """엑셀과 DB 데이터 비교"""
    print("\n" + "="*80)
    print("📊 데이터 일치성 검증 결과")
    print("="*80)

    # 1. 전체 레코드 수 비교
    print("\n1️⃣ 전체 레코드 수 비교")
    excel_total = len(excel_df)
    db_total = len(db_df)
    match_icon = "✅" if excel_total == db_total else "❌"
    print(f"  - 엑셀 전체 레코드: {excel_total:,}개")
    print(f"  - DB 전체 레코드: {db_total:,}개")
    print(f"  - 일치 여부: {match_icon} (차이: {abs(excel_total - db_total)}개)")

    # 2. 월별 레코드 수 비교
    print("\n2️⃣ 월별 레코드 수 비교")
    excel_monthly = excel_df.groupby('월').size() if not excel_df.empty else pd.Series()
    db_monthly = db_df.groupby('month').size() if not db_df.empty else pd.Series()

    print(f"  {'월':>3} | {'엑셀':>8} | {'DB':>8} | {'차이':>8} | 상태")
    print("  " + "-"*50)

    for month in range(1, 6):
        excel_count = int(excel_monthly.get(month, 0))
        db_count = int(db_monthly.get(month, 0))
        diff = abs(excel_count - db_count)
        status = "✅" if excel_count == db_count else "❌"
        print(f"  {month:>3}월 | {excel_count:>8,} | {db_count:>8,} | {diff:>8,} | {status}")

    # 3. 금액 합계 비교
    print("\n3️⃣ 금액 합계 비교")
    excel_total_amount = excel_df['금액'].sum() if not excel_df.empty else 0
    db_total_amount = db_df['amount'].sum() if not db_df.empty else 0
    amount_diff = abs(excel_total_amount - db_total_amount)
    amount_match = "✅" if amount_diff < 1 else "❌"

    print(f"  - 엑셀 총 금액: {excel_total_amount:,.0f}원")
    print(f"  - DB 총 금액: {db_total_amount:,.0f}원")
    print(f"  - 차이: {amount_diff:,.0f}원 {amount_match}")

    # 4. 고객별 결제 건수 비교 (상위 10명)
    if not excel_df.empty and not db_df.empty:
        print("\n4️⃣ 고객별 결제 건수 TOP 10")
        excel_customer_counts = excel_df['고객명'].value_counts().head(10)
        db_customer_counts = db_df['customer_name'].value_counts().head(10)

        print(f"  {'순위':>3} | {'고객명':^20} | {'엑셀':>6} | {'DB':>6}")
        print("  " + "-"*50)

        for i, (customer, count) in enumerate(excel_customer_counts.items(), 1):
            db_count = db_customer_counts.get(customer, 0)
            print(f"  {i:>3}위 | {customer:^20} | {count:>6} | {db_count:>6}")

    # 5. 시트별 상세 정보
    if excel_stats:
        print("\n5️⃣ 엑셀 시트별 상세 정보")
        for sheet_name, stats in sorted(excel_stats.items(), key=lambda x: x[1]['month']):
            print(f"  - {sheet_name}: {stats['count']:,}개 레코드, 총 {stats['total_amount']:,.0f}원")

    # 6. 불일치 데이터 분석 (개선)
    if excel_total != db_total and not excel_df.empty and not db_df.empty:
        print("\n6️⃣ 불일치 데이터 상세 분석")

        # 고객명 표준화 (공백 제거)
        excel_df['고객명_표준'] = excel_df['고객명'].str.strip()
        db_df['customer_name_표준'] = db_df['customer_name'].str.strip()

        # 월별 불일치 분석
        for month in range(1, 6):
            excel_month = excel_df[excel_df['월'] == month]
            db_month = db_df[db_df['month'] == month]

            if len(excel_month) != len(db_month):
                print(f"\n  📌 {month}월 불일치 분석:")
                print(f"     엑셀: {len(excel_month)}건, DB: {len(db_month)}건")

                # 해당 월의 고객 목록 비교
                excel_customers = set(excel_month['고객명_표준'].unique())
                db_customers = set(db_month['customer_name_표준'].unique())

                only_excel = excel_customers - db_customers
                only_db = db_customers - excel_customers

                if only_excel:
                    print(f"     엑셀에만 있는 고객: {', '.join(list(only_excel)[:5])}")
                if only_db:
                    print(f"     DB에만 있는 고객: {', '.join(list(only_db)[:5])}")

def main():
    """메인 실행 함수"""
    print("🔍 엑셀-DB 데이터 일치성 검증 시작\n")

    # 1. 엑셀 데이터 읽기
    excel_data, excel_stats = read_excel_data()

    if excel_data.empty:
        print("\n❌ 엑셀에서 유효한 데이터를 찾을 수 없습니다.")
        return

    print(f"\n✅ 엑셀에서 총 {len(excel_data):,}개 레코드를 읽었습니다.")

    # 2. DB 데이터 조회
    print("\n📊 데이터베이스에서 데이터 조회 중...")
    db_data = get_db_data()

    # 3. 데이터 비교
    compare_data(excel_data, excel_stats, db_data)

    print("\n✅ 검증 완료!")

if __name__ == "__main__":
    main()
