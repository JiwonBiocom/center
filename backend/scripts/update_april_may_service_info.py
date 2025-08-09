"""
4월과 5월 결제 데이터의 service_type 정보 업데이트
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

# Excel 파일 읽기
EXCEL_DIR = "/Users/vibetj/coding/center/docs/AIBIO 관리대장 파일모음"
file_path = os.path.join(EXCEL_DIR, "★2025년 AIBIO 결제현황.xlsx")

print("=== 4월과 5월 결제 데이터 service_type 업데이트 ===")

# 전체 결제대장에서 데이터 읽기
df = pd.read_excel(file_path, sheet_name="전체 결제대장", header=2)

# 날짜 형식으로 변환
df['결제일자'] = pd.to_datetime(df['결제일자'], errors='coerce')

# 2024년 4월과 5월 데이터 필터링
april_may_data = df[
    (df['결제일자'].dt.year == 2024) & 
    (df['결제일자'].dt.month.isin([4, 5]))
]

print(f"\n업데이트할 데이터: {len(april_may_data)}건")

with engine.begin() as conn:
    updated_count = 0
    
    for idx, row in april_may_data.iterrows():
        if pd.notna(row['결제일자']) and pd.notna(row['고객명']) and pd.notna(row['결제 금액']):
            # 해당 날짜와 고객명, 금액으로 결제 찾기
            query = """
            UPDATE payments p
            SET service_type = :service_type,
                memo = :memo
            FROM customers c
            WHERE p.customer_id = c.customer_id
            AND c.name = :customer_name
            AND p.payment_date = :payment_date
            AND p.amount = :amount
            AND (p.service_type IS NULL OR p.service_type = '')
            """
            
            params = {
                'customer_name': row['고객명'],
                'payment_date': row['결제일자'].date(),
                'amount': float(row['결제 금액']),
                'service_type': row['결제 프로그램'] if pd.notna(row['결제 프로그램']) else '',
                'memo': row['메모'] if '메모' in df.columns and pd.notna(row.get('메모')) else ''
            }
            
            result = conn.execute(text(query), params)
            
            if result.rowcount > 0:
                updated_count += result.rowcount
                print(f"업데이트: {row['결제일자'].strftime('%Y-%m-%d')} {row['고객명']} - {row['결제 프로그램']}")
    
    print(f"\n총 {updated_count}건 업데이트 완료")

# 업데이트 결과 확인
print("\n=== 업데이트 결과 확인 ===")
with engine.connect() as conn:
    query = """
    SELECT 
        p.payment_date,
        c.name as customer_name,
        p.amount,
        p.service_type,
        p.memo
    FROM payments p
    JOIN customers c ON p.customer_id = c.customer_id
    WHERE p.payment_date >= '2024-04-01' AND p.payment_date < '2024-06-01'
    AND p.service_type IS NOT NULL AND p.service_type != ''
    ORDER BY p.payment_date
    LIMIT 20
    """
    
    result = conn.execute(text(query))
    updated_data = result.fetchall()
    
    print(f"\nservice_type이 업데이트된 데이터 샘플:")
    for row in updated_data:
        print(f"{row.payment_date.strftime('%Y-%m-%d')}: {row.customer_name} - {row.service_type} - {row.amount:,}원")

# 월별 통계 확인
print("\n=== 월별 결제 통계 (2024년) ===")
with engine.connect() as conn:
    query = """
    SELECT 
        EXTRACT(MONTH FROM payment_date) as month,
        COUNT(*) as count,
        SUM(amount) as total_amount
    FROM payments
    WHERE payment_date >= '2024-01-01' AND payment_date < '2025-01-01'
    GROUP BY EXTRACT(MONTH FROM payment_date)
    ORDER BY month
    """
    
    result = conn.execute(text(query))
    stats = result.fetchall()
    
    for row in stats:
        print(f"{int(row.month)}월: {row.count}건, 총액: {row.total_amount:,.0f}원")