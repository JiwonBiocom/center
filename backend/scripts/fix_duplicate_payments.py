"""
2025년 1-4월 중복 결제 데이터 확인 및 수정
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from datetime import datetime
from core.config import settings
import pandas as pd

def check_duplicates():
    """중복 결제 데이터 확인"""
    engine = create_engine(settings.DATABASE_URL)
    
    query = text("""
        WITH duplicate_payments AS (
            SELECT 
                customer_id,
                payment_date,
                amount,
                COUNT(*) as duplicate_count
            FROM payments
            WHERE payment_date >= '2025-01-01' 
            AND payment_date < '2025-05-01'
            GROUP BY customer_id, payment_date, amount
            HAVING COUNT(*) > 1
        )
        SELECT 
            p.payment_id,
            c.name as customer_name,
            p.payment_date,
            p.amount,
            p.payment_method,
            p.created_at,
            dp.duplicate_count
        FROM payments p
        JOIN customers c ON p.customer_id = c.customer_id
        JOIN duplicate_payments dp ON 
            p.customer_id = dp.customer_id 
            AND p.payment_date = dp.payment_date 
            AND p.amount = dp.amount
        ORDER BY p.payment_date, c.name, p.created_at
    """)
    
    with engine.connect() as conn:
        result = conn.execute(query)
        duplicates = result.fetchall()
        
    if duplicates:
        print(f"총 {len(duplicates)}개의 중복 결제 발견")
        print("\n중복 결제 상세:")
        
        # 데이터프레임으로 변환하여 보기 좋게 출력
        df = pd.DataFrame(duplicates, columns=['payment_id', 'customer_name', 'payment_date', 
                                              'amount', 'payment_method', 'created_at', 'duplicate_count'])
        
        # 고객별로 그룹화하여 출력
        for customer in df['customer_name'].unique():
            customer_df = df[df['customer_name'] == customer]
            print(f"\n{customer}:")
            for _, row in customer_df.iterrows():
                print(f"  ID: {row['payment_id']}, 날짜: {row['payment_date']}, "
                      f"금액: {row['amount']:,.0f}원, 생성시간: {row['created_at']}")
    else:
        print("중복 결제가 없습니다.")
    
    return duplicates

def remove_duplicates():
    """중복 결제 제거 (각 그룹에서 가장 먼저 생성된 것만 남김)"""
    engine = create_engine(settings.DATABASE_URL)
    
    # 삭제할 중복 결제 ID 찾기
    query = text("""
        WITH duplicate_groups AS (
            SELECT 
                payment_id,
                customer_id,
                payment_date,
                amount,
                created_at,
                ROW_NUMBER() OVER (
                    PARTITION BY customer_id, payment_date, amount 
                    ORDER BY created_at
                ) as rn
            FROM payments
            WHERE payment_date >= '2025-01-01' 
            AND payment_date < '2025-05-01'
        )
        SELECT payment_id
        FROM duplicate_groups
        WHERE rn > 1
    """)
    
    with engine.connect() as conn:
        result = conn.execute(query)
        duplicate_ids = [row[0] for row in result.fetchall()]
        
    if duplicate_ids:
        print(f"\n삭제할 중복 결제 ID: {duplicate_ids}")
        
        # 자동으로 중복 제거 실행
        print("\n중복 결제를 제거합니다...")
        if True:
            delete_query = text("""
                DELETE FROM payments 
                WHERE payment_id = ANY(:ids)
            """)
            
            with engine.begin() as conn:
                result = conn.execute(delete_query, {"ids": duplicate_ids})
                print(f"\n{len(duplicate_ids)}개의 중복 결제를 삭제했습니다.")
        else:
            print("\n삭제를 취소했습니다.")
    else:
        print("\n삭제할 중복 결제가 없습니다.")

def check_missing_data():
    """Excel에는 있지만 DB에 없는 데이터 확인"""
    print("\n" + "="*60)
    print("누락된 데이터 확인")
    print("="*60)
    
    # Excel 파일 경로
    EXCEL_PATH = "/Users/vibetj/coding/center/docs/AIBIO 관리대장 파일모음/★2025년 AIBIO 결제현황.xlsx"
    
    # 3월과 4월 데이터만 확인 (건수 차이가 큰 월)
    for month in [3, 4]:
        sheet_name = f"2025년 {month}월"
        
        # Excel 데이터 읽기
        df = pd.read_excel(EXCEL_PATH, sheet_name=sheet_name, header=2)
        excel_data = df[['결제일자', '고객명', '결제 금액']].dropna()
        
        print(f"\n{sheet_name}:")
        print(f"Excel 총 {len(excel_data)}건")
        
        # DB에서 해당 월 데이터 조회
        engine = create_engine(settings.DATABASE_URL)
        start_date = f"2025-{month:02d}-01"
        end_date = f"2025-{month+1:02d}-01" if month < 4 else "2025-05-01"
        
        query = text("""
            SELECT c.name, p.payment_date, p.amount
            FROM payments p
            JOIN customers c ON p.customer_id = c.customer_id
            WHERE p.payment_date >= :start_date 
            AND p.payment_date < :end_date
        """)
        
        with engine.connect() as conn:
            result = conn.execute(query, {"start_date": start_date, "end_date": end_date})
            db_data = pd.DataFrame(result.fetchall(), columns=['name', 'payment_date', 'amount'])
        
        print(f"DB 총 {len(db_data)}건")
        
        if len(excel_data) > len(db_data):
            print(f"\n누락된 데이터가 있을 수 있습니다. (차이: {len(excel_data) - len(db_data)}건)")

def main():
    print("2025년 1-4월 결제 데이터 중복 확인 및 정리")
    print("="*60)
    
    # 1. 중복 확인
    print("\n[1] 중복 결제 확인")
    duplicates = check_duplicates()
    
    # 2. 중복 제거
    if duplicates:
        print("\n[2] 중복 결제 제거")
        remove_duplicates()
    
    # 3. 누락 데이터 확인
    print("\n[3] 누락 데이터 확인")
    check_missing_data()

if __name__ == "__main__":
    main()