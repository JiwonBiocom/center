"""
테이블 구조 확인 및 4월, 5월 데이터 복원
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from core.config import settings
import pandas as pd
from datetime import datetime

# 데이터베이스 연결
engine = create_engine(settings.DATABASE_URL)

print("=== 데이터베이스 테이블 구조 확인 ===")

with engine.connect() as conn:
    # customers 테이블 구조
    query_customers = """
    SELECT column_name, data_type
    FROM information_schema.columns
    WHERE table_name = 'customers'
    ORDER BY ordinal_position
    """
    
    result = conn.execute(text(query_customers))
    customers_columns = result.fetchall()
    print("\ncustomers 테이블 컬럼:")
    for col in customers_columns:
        print(f"  - {col.column_name}: {col.data_type}")
    
    # payments 테이블의 service_type 컬럼 확인
    query_check = """
    SELECT column_name
    FROM information_schema.columns
    WHERE table_name = 'payments' AND column_name = 'service_type'
    """
    
    result = conn.execute(text(query_check))
    has_service_type = len(result.fetchall()) > 0
    
    if not has_service_type:
        print("\n'service_type' 컬럼이 없습니다. 컬럼 추가중...")
        # service_type 컬럼 추가
        conn.execute(text("ALTER TABLE payments ADD COLUMN IF NOT EXISTS service_type VARCHAR(255)"))
        conn.execute(text("ALTER TABLE payments ADD COLUMN IF NOT EXISTS memo TEXT"))
        conn.commit()
        print("컬럼 추가 완료")
    
    # 현재 데이터베이스의 4월, 5월 데이터 확인
    print("\n=== 현재 DB의 4월, 5월 데이터 ===")
    query_existing = """
    SELECT 
        p.payment_date,
        c.name as customer_name,
        p.amount,
        p.service_type,
        p.memo
    FROM payments p
    JOIN customers c ON p.customer_id = c.customer_id
    WHERE p.payment_date >= '2024-04-01' AND p.payment_date < '2024-06-01'
    ORDER BY p.payment_date
    LIMIT 20
    """
    
    result = conn.execute(text(query_existing))
    existing_data = result.fetchall()
    
    print(f"\n현재 DB에 있는 4-5월 데이터 샘플:")
    for row in existing_data:
        print(f"{row.payment_date.strftime('%Y-%m-%d')}: {row.customer_name} - {row.amount:,}원 - {row.service_type or 'N/A'}")

# Excel 파일에서 4월, 5월 데이터 읽기
EXCEL_DIR = "/Users/vibetj/coding/center/docs/AIBIO 관리대장 파일모음"
file_path = os.path.join(EXCEL_DIR, "★2025년 AIBIO 결제현황.xlsx")

print("\n\n=== Excel 파일에서 4월, 5월 데이터 확인 ===")

# 전체 결제대장에서 데이터 읽기
df = pd.read_excel(file_path, sheet_name="전체 결제대장", header=2)

# 날짜 형식으로 변환
df['결제일자'] = pd.to_datetime(df['결제일자'], errors='coerce')

# 2024년 4월과 5월 데이터 필터링
april_data = df[(df['결제일자'].dt.year == 2024) & (df['결제일자'].dt.month == 4)]
may_data = df[(df['결제일자'].dt.year == 2024) & (df['결제일자'].dt.month == 5)]

print(f"\nExcel 파일의 4월 데이터: {len(april_data)}건")
print("처음 5건:")
for idx, row in april_data.head(5).iterrows():
    print(f"  {row['결제일자'].strftime('%Y-%m-%d')}: {row['고객명']} - {row['결제 프로그램']} - {row['결제 금액']:,}원")

print(f"\nExcel 파일의 5월 데이터: {len(may_data)}건")
print("처음 5건:")
for idx, row in may_data.head(5).iterrows():
    print(f"  {row['결제일자'].strftime('%Y-%m-%d')}: {row['고객명']} - {row['결제 프로그램']} - {row['결제 금액']:,}원")