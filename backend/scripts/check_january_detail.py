"""
1월 데이터 상세 비교
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
from sqlalchemy import create_engine, text
from core.config import settings

# Excel 파일 경로
EXCEL_PATH = "/Users/vibetj/coding/center/docs/AIBIO 관리대장 파일모음/★2025년 AIBIO 결제현황.xlsx"

def check_january_detail():
    """1월 데이터 상세 비교"""
    engine = create_engine(settings.DATABASE_URL)
    
    # Excel 데이터 읽기
    df = pd.read_excel(EXCEL_PATH, sheet_name="2025년 1월", header=2)
    excel_data = df.dropna(subset=['결제일자', '고객명', '결제 금액'])
    
    print("Excel 1월 데이터 상세:")
    for idx, row in excel_data.iterrows():
        try:
            date = pd.to_datetime(row['결제일자']).strftime('%Y-%m-%d')
        except:
            date = str(row['결제일자'])
        print(f"{idx+1}. {date} {row['고객명']} {row['결제 금액']:,.0f}원")
    
    print(f"\nExcel 합계: {len(excel_data)}건, {excel_data['결제 금액'].sum():,.0f}원")
    
    # DB 데이터 조회
    query = text("""
        SELECT p.payment_date, c.name, p.amount
        FROM payments p
        JOIN customers c ON p.customer_id = c.customer_id
        WHERE p.payment_date >= '2025-01-01' AND p.payment_date < '2025-02-01'
        ORDER BY p.payment_date, c.name
    """)
    
    print("\n\nDB 1월 데이터 상세:")
    with engine.connect() as conn:
        result = conn.execute(query)
        db_rows = result.fetchall()
        db_total = 0
        for idx, row in enumerate(db_rows):
            print(f"{idx+1}. {row[0]} {row[1]} {float(row[2]):,.0f}원")
            db_total += float(row[2])
    
    print(f"\nDB 합계: {len(db_rows)}건, {db_total:,.0f}원")
    
    # Excel 데이터를 set으로 변환
    excel_set = set()
    for _, row in excel_data.iterrows():
        try:
            date = pd.to_datetime(row['결제일자']).strftime('%Y-%m-%d')
        except:
            date = str(row['결제일자'])
        excel_set.add((date, row['고객명'], float(row['결제 금액'])))
    
    # DB 데이터를 set으로 변환
    db_set = set()
    for row in db_rows:
        db_set.add((row[0].strftime('%Y-%m-%d'), row[1], float(row[2])))
    
    # 차이 찾기
    print("\n\nExcel에만 있는 데이터:")
    excel_only = excel_set - db_set
    for item in sorted(excel_only):
        print(f"  {item[0]} {item[1]} {item[2]:,.0f}원")
    
    print("\n\nDB에만 있는 데이터:")
    db_only = db_set - excel_set
    for item in sorted(db_only):
        print(f"  {item[0]} {item[1]} {item[2]:,.0f}원")

def add_missing_january_data():
    """누락된 1월 데이터 추가"""
    engine = create_engine(settings.DATABASE_URL)
    
    # 장재미 취소 예정 건과 김보경 추가 건 처리
    with engine.begin() as conn:
        # 장재미 고객 ID 조회
        query = text("SELECT customer_id FROM customers WHERE name = :name")
        result = conn.execute(query, {"name": "장재미"}).fetchone()
        
        if result:
            customer_id = result[0]
            
            # 취소 예정 건 추가 (-4,000,000원)
            insert_query = text("""
                INSERT INTO payments (
                    customer_id, payment_date, amount, 
                    payment_method, card_holder_name, 
                    payment_staff, service_type, created_at
                ) VALUES (
                    :customer_id, '2025-01-23', -4000000,
                    '카드', '장재미', 
                    '미입력', '취소 예정', NOW()
                )
            """)
            conn.execute(insert_query, {"customer_id": customer_id})
            print("장재미 취소 예정 건 추가: -4,000,000원")
        
        # 김보경 추가 건
        query = text("SELECT customer_id FROM customers WHERE name = :name")
        result = conn.execute(query, {"name": "김보경"}).fetchone()
        
        if result:
            customer_id = result[0]
            
            # 19,800원 건 추가
            insert_query = text("""
                INSERT INTO payments (
                    customer_id, payment_date, amount, 
                    payment_method, card_holder_name, 
                    payment_staff, service_type, created_at
                ) VALUES (
                    :customer_id, '2025-01-13', 19800,
                    '카드', '김보경', 
                    '미입력', '미입력', NOW()
                )
            """)
            conn.execute(insert_query, {"customer_id": customer_id})
            print("김보경 추가 건: 19,800원")

def main():
    print("1월 데이터 상세 분석")
    print("="*60)
    
    check_january_detail()
    
    print("\n\n누락된 데이터 추가")
    print("="*60)
    add_missing_january_data()

if __name__ == "__main__":
    main()