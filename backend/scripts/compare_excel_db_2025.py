"""
Excel 파일과 데이터베이스의 2025년 1월~4월 결제 데이터를 비교하는 스크립트
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
from datetime import datetime
from sqlalchemy import create_engine, text
from tabulate import tabulate
from core.config import settings
from core.database import get_db

# Excel 파일 경로
EXCEL_PATH = "/Users/vibetj/coding/center/docs/AIBIO 관리대장 파일모음/★2025년 AIBIO 결제현황.xlsx"

def read_excel_data():
    """Excel 파일에서 각 월별 데이터 읽기"""
    excel_data = {}
    
    # 각 월별 시트 읽기
    sheet_names = ["2025년 1월", "2025년 2월", "2025년 3월", "2025년 4월"]
    
    for sheet_name in sheet_names:
        try:
            # 시트 읽기 (header=2는 3행째가 헤더)
            df = pd.read_excel(EXCEL_PATH, sheet_name=sheet_name, header=2)
            
            # 필요한 컬럼 선택: 결제일자, 고객명, 결제금액
            df_clean = df[['결제일자', '고객명', '결제 금액']].copy()
            
            # 유효한 데이터만 필터링
            df_clean = df_clean.dropna(subset=['결제일자', '고객명', '결제 금액'])
            
            # 날짜 형식 정리
            df_clean['결제일자'] = pd.to_datetime(df_clean['결제일자'], errors='coerce')
            df_clean = df_clean.dropna(subset=['결제일자'])
            
            # 결제금액 숫자로 변환
            df_clean['결제 금액'] = pd.to_numeric(df_clean['결제 금액'], errors='coerce')
            df_clean = df_clean.dropna(subset=['결제 금액'])
            
            # 컬럼명 통일
            df_clean.columns = ['날짜', '이름', '결제금액']
            
            # 월 추출
            month = int(sheet_name.split('월')[0].split()[-1])
            
            excel_data[month] = {
                'count': len(df_clean),
                'total_amount': int(df_clean['결제금액'].sum()),
                'details': df_clean
            }
            
            print(f"\n{sheet_name} 시트:")
            print(f"  건수: {excel_data[month]['count']}건")
            print(f"  총액: {excel_data[month]['total_amount']:,}원")
            
        except Exception as e:
            print(f"{sheet_name} 시트 읽기 실패: {e}")
    
    return excel_data

def get_db_data():
    """데이터베이스에서 2025년 1월~4월 결제 데이터 조회"""
    db_data = {}
    
    # 데이터베이스 연결
    engine = create_engine(settings.DATABASE_URL)
    
    # 각 월별 데이터 조회
    for month in range(1, 5):
        start_date = f"2025-{month:02d}-01"
        if month == 4:
            end_date = "2025-05-01"
        else:
            end_date = f"2025-{month+1:02d}-01"
        
        query = text("""
            SELECT 
                payment_date,
                c.name as customer_name,
                amount
            FROM payments p
            JOIN customers c ON p.customer_id = c.customer_id
            WHERE payment_date >= :start_date 
            AND payment_date < :end_date
            ORDER BY payment_date
        """)
        
        with engine.connect() as conn:
            result = conn.execute(query, {"start_date": start_date, "end_date": end_date})
            rows = result.fetchall()
            
            total_amount = sum(row[2] for row in rows)
            
            db_data[month] = {
                'count': len(rows),
                'total_amount': total_amount,
                'details': pd.DataFrame(rows, columns=['날짜', '이름', '결제금액'])
            }
            
            print(f"\n데이터베이스 2025년 {month}월:")
            print(f"  건수: {db_data[month]['count']}건")
            print(f"  총액: {db_data[month]['total_amount']:,}원")
    
    return db_data

def compare_data(excel_data, db_data):
    """Excel과 DB 데이터 비교"""
    print("\n" + "="*60)
    print("Excel vs DB 데이터 비교 결과")
    print("="*60)
    
    comparison_table = []
    
    for month in range(1, 5):
        excel_count = excel_data.get(month, {}).get('count', 0)
        excel_amount = excel_data.get(month, {}).get('total_amount', 0)
        db_count = db_data.get(month, {}).get('count', 0)
        db_amount = db_data.get(month, {}).get('total_amount', 0)
        
        count_diff = db_count - excel_count
        amount_diff = db_amount - excel_amount
        
        comparison_table.append([
            f"2025년 {month}월",
            f"{excel_count}건",
            f"{db_count}건",
            f"{count_diff:+d}건",
            f"{excel_amount:,}원",
            f"{db_amount:,}원",
            f"{amount_diff:+,}원"
        ])
    
    # 합계
    total_excel_count = sum(excel_data.get(m, {}).get('count', 0) for m in range(1, 5))
    total_excel_amount = sum(excel_data.get(m, {}).get('total_amount', 0) for m in range(1, 5))
    total_db_count = sum(db_data.get(m, {}).get('count', 0) for m in range(1, 5))
    total_db_amount = sum(db_data.get(m, {}).get('total_amount', 0) for m in range(1, 5))
    
    comparison_table.append([
        "합계",
        f"{total_excel_count}건",
        f"{total_db_count}건",
        f"{total_db_count - total_excel_count:+d}건",
        f"{total_excel_amount:,}원",
        f"{total_db_amount:,}원",
        f"{total_db_amount - total_excel_amount:+,}원"
    ])
    
    headers = ["월", "Excel 건수", "DB 건수", "건수 차이", "Excel 금액", "DB 금액", "금액 차이"]
    print(tabulate(comparison_table, headers=headers, tablefmt="grid"))
    
    # 불일치 상세 분석
    print("\n" + "="*60)
    print("불일치 상세 분석")
    print("="*60)
    
    for month in range(1, 5):
        if month not in excel_data or month not in db_data:
            continue
            
        excel_details = excel_data[month]['details']
        db_details = db_data[month]['details']
        
        if excel_data[month]['count'] != db_data[month]['count'] or \
           excel_data[month]['total_amount'] != db_data[month]['total_amount']:
            
            print(f"\n2025년 {month}월 불일치 상세:")
            
            # Excel에만 있는 데이터 찾기
            excel_names = set(excel_details['이름'].unique())
            db_names = set(db_details['이름'].unique())
            
            only_in_excel = excel_names - db_names
            only_in_db = db_names - excel_names
            
            if only_in_excel:
                print(f"\n  Excel에만 있는 고객:")
                for name in only_in_excel:
                    customer_data = excel_details[excel_details['이름'] == name]
                    for _, row in customer_data.iterrows():
                        print(f"    - {row['날짜'].strftime('%Y-%m-%d')} {name}: {row['결제금액']:,}원")
            
            if only_in_db:
                print(f"\n  DB에만 있는 고객:")
                for name in only_in_db:
                    customer_data = db_details[db_details['이름'] == name]
                    for _, row in customer_data.iterrows():
                        print(f"    - {row['날짜'].strftime('%Y-%m-%d')} {name}: {row['결제금액']:,}원")
            
            # 같은 고객이지만 금액이 다른 경우
            common_names = excel_names & db_names
            for name in common_names:
                excel_customer = excel_details[excel_details['이름'] == name]
                db_customer = db_details[db_details['이름'] == name]
                
                excel_total = excel_customer['결제금액'].sum()
                db_total = db_customer['결제금액'].sum()
                
                if abs(excel_total - db_total) > 1:  # 1원 이상 차이
                    print(f"\n  금액 불일치 - {name}:")
                    print(f"    Excel: {excel_total:,}원 ({len(excel_customer)}건)")
                    print(f"    DB: {db_total:,}원 ({len(db_customer)}건)")

def main():
    print("2025년 1월~4월 Excel vs DB 결제 데이터 비교")
    print("="*60)
    
    # Excel 데이터 읽기
    print("\n[1] Excel 파일 읽기")
    excel_data = read_excel_data()
    
    # DB 데이터 읽기
    print("\n[2] 데이터베이스 조회")
    db_data = get_db_data()
    
    # 데이터 비교
    print("\n[3] 데이터 비교")
    compare_data(excel_data, db_data)

if __name__ == "__main__":
    main()