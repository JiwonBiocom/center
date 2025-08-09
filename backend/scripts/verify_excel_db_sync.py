#!/usr/bin/env python3
"""
엑셀 파일과 데이터베이스의 데이터 일치성 검증 스크립트
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

def read_excel_data():
    """엑셀 파일에서 데이터 읽기"""
    excel_path = "/Users/vibetj/coding/center/docs/AIBIO 관리대장 파일모음/★2025년 AIBIO 결제현황.xlsx"

    if not os.path.exists(excel_path):
        print(f"❌ 엑셀 파일을 찾을 수 없습니다: {excel_path}")
        return None

    print(f"📊 엑셀 파일 읽기: {excel_path}")

    # 엑셀 파일 열기
    xl_file = pd.ExcelFile(excel_path)

    # 월별 시트 이름 패턴
    months = ['1월', '2월', '3월', '4월', '5월']

    all_data = []
    sheet_stats = {}

    for sheet_name in xl_file.sheet_names:
        # 월별 시트만 처리
        if any(month in sheet_name for month in months):
            print(f"\n  - {sheet_name} 시트 읽기...")
            df = pd.read_excel(excel_path, sheet_name=sheet_name)

            # 헤더 행 찾기 (일반적으로 특정 키워드가 있는 행)
            header_row = None
            for idx, row in df.iterrows():
                if any(str(cell).strip() in ['날짜', '일자', '일수', '고객명', '이름'] for cell in row):
                    header_row = idx
                    break

            if header_row is not None:
                # 헤더 행부터 다시 읽기
                df = pd.read_excel(excel_path, sheet_name=sheet_name, header=header_row)

                # 빈 행 제거
                df = df.dropna(how='all')

                # 날짜/일자/일수 컬럼 찾기
                date_cols = [col for col in df.columns if any(keyword in str(col) for keyword in ['날짜', '일자', '일수'])]
                name_cols = [col for col in df.columns if any(keyword in str(col) for keyword in ['고객명', '이름', '성명'])]
                amount_cols = [col for col in df.columns if any(keyword in str(col) for keyword in ['금액', '결제금액', '이용금액'])]

                if date_cols and name_cols and amount_cols:
                    # 필요한 컬럼만 선택
                    selected_df = df[[date_cols[0], name_cols[0], amount_cols[0]]].copy()
                    selected_df.columns = ['날짜', '고객명', '금액']

                    # 유효한 데이터만 필터링
                    selected_df = selected_df.dropna(subset=['고객명'])
                    selected_df = selected_df[selected_df['고객명'].str.strip() != '']

                    # 월 정보 추가
                    month_num = None
                    for i, month in enumerate(months, 1):
                        if month in sheet_name:
                            month_num = i
                            break

                    if month_num:
                        selected_df['월'] = month_num
                        selected_df['시트명'] = sheet_name

                        # 통계 저장
                        sheet_stats[sheet_name] = {
                            'count': len(selected_df),
                            'total_amount': selected_df['금액'].sum(),
                            'month': month_num
                        }

                        all_data.append(selected_df)
                        print(f"    ✓ {len(selected_df)}개 레코드 발견")

    if all_data:
        combined_df = pd.concat(all_data, ignore_index=True)
        return combined_df, sheet_stats
    else:
        return None, None

def get_db_data():
    """데이터베이스에서 2025년 1-5월 데이터 조회"""
    session = Session()

    try:
        # 2025년 1-5월 결제 데이터 조회
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
    excel_monthly = excel_df.groupby('월').size()
    db_monthly = db_df.groupby('month').size() if not db_df.empty else pd.Series()

    print(f"  {'월':>3} | {'엑셀':>8} | {'DB':>8} | {'차이':>8} | 상태")
    print("  " + "-"*50)

    for month in range(1, 6):
        excel_count = excel_monthly.get(month, 0)
        db_count = db_monthly.get(month, 0)
        diff = abs(excel_count - db_count)
        status = "✅" if excel_count == db_count else "❌"
        print(f"  {month:>3}월 | {excel_count:>8,} | {db_count:>8,} | {diff:>8,} | {status}")

    # 3. 금액 합계 비교
    print("\n3️⃣ 금액 합계 비교")
    excel_total_amount = excel_df['금액'].sum()
    db_total_amount = db_df['amount'].sum() if not db_df.empty else 0
    amount_diff = abs(excel_total_amount - db_total_amount)
    amount_match = "✅" if amount_diff < 1 else "❌"

    print(f"  - 엑셀 총 금액: {excel_total_amount:,.0f}원")
    print(f"  - DB 총 금액: {db_total_amount:,.0f}원")
    print(f"  - 차이: {amount_diff:,.0f}원 {amount_match}")

    # 4. 고객별 결제 건수 비교 (상위 10명)
    print("\n4️⃣ 고객별 결제 건수 TOP 10")
    excel_customer_counts = excel_df['고객명'].value_counts().head(10)
    db_customer_counts = db_df['customer_name'].value_counts().head(10) if not db_df.empty else pd.Series()

    print(f"  {'순위':>3} | {'고객명':^20} | {'엑셀':>6} | {'DB':>6}")
    print("  " + "-"*50)

    for i, (customer, count) in enumerate(excel_customer_counts.items(), 1):
        db_count = db_customer_counts.get(customer, 0)
        print(f"  {i:>3}위 | {customer:^20} | {count:>6} | {db_count:>6}")

    # 5. 시트별 상세 정보
    print("\n5️⃣ 엑셀 시트별 상세 정보")
    for sheet_name, stats in sorted(excel_stats.items(), key=lambda x: x[1]['month']):
        print(f"  - {sheet_name}: {stats['count']:,}개 레코드, 총 {stats['total_amount']:,.0f}원")

    # 6. 불일치 데이터 분석
    if excel_total != db_total:
        print("\n6️⃣ 불일치 데이터 분석")

        # 엑셀 데이터를 고객명과 금액으로 그룹화
        excel_grouped = excel_df.groupby(['고객명', '금액']).size().reset_index(name='count')

        # DB 데이터를 고객명과 금액으로 그룹화
        if not db_df.empty:
            db_grouped = db_df.groupby(['customer_name', 'amount']).size().reset_index(name='count')
            db_grouped.columns = ['고객명', '금액', 'count']
        else:
            db_grouped = pd.DataFrame(columns=['고객명', '금액', 'count'])

        # 엑셀에만 있는 데이터
        excel_only = excel_grouped.merge(db_grouped, on=['고객명', '금액'], how='left', suffixes=('_excel', '_db'))
        excel_only = excel_only[excel_only['count_db'].isna()]

        if not excel_only.empty:
            print("\n  📌 엑셀에만 있는 데이터 (샘플 10개)")
            for _, row in excel_only.head(10).iterrows():
                print(f"    - {row['고객명']}: {row['금액']:,.0f}원 ({int(row['count_excel'])}건)")

        # DB에만 있는 데이터
        if not db_grouped.empty:
            db_only = db_grouped.merge(excel_grouped, on=['고객명', '금액'], how='left', suffixes=('_db', '_excel'))
            db_only = db_only[db_only['count_excel'].isna()]

            if not db_only.empty:
                print("\n  📌 DB에만 있는 데이터 (샘플 10개)")
                for _, row in db_only.head(10).iterrows():
                    print(f"    - {row['고객명']}: {row['금액']:,.0f}원 ({int(row['count_db'])}건)")

def main():
    """메인 실행 함수"""
    print("🔍 엑셀-DB 데이터 일치성 검증 시작\n")

    # 1. 엑셀 데이터 읽기
    excel_data, excel_stats = read_excel_data()
    if excel_data is None:
        print("❌ 엑셀 데이터를 읽을 수 없습니다.")
        return

    print(f"\n✅ 엑셀에서 총 {len(excel_data):,}개 레코드를 읽었습니다.")

    # 2. DB 데이터 조회
    print("\n📊 데이터베이스에서 데이터 조회 중...")
    db_data = get_db_data()
    print(f"✅ DB에서 총 {len(db_data):,}개 레코드를 조회했습니다.")

    # 3. 데이터 비교
    compare_data(excel_data, excel_stats, db_data)

    print("\n✅ 검증 완료!")

if __name__ == "__main__":
    main()
