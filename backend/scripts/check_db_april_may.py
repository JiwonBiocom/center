"""
데이터베이스에서 4월과 5월 결제 데이터 확인
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from core.config import settings
from datetime import datetime

# 데이터베이스 연결
engine = create_engine(settings.DATABASE_URL)

print("=== 데이터베이스 4월과 5월 결제 데이터 확인 ===")

with engine.connect() as conn:
    # 2024년 4월과 5월 데이터 확인
    query = """
    SELECT 
        EXTRACT(YEAR FROM payment_date) as year,
        EXTRACT(MONTH FROM payment_date) as month,
        COUNT(*) as count,
        SUM(amount) as total_amount
    FROM payments
    WHERE payment_date >= '2024-04-01' AND payment_date < '2024-06-01'
    GROUP BY EXTRACT(YEAR FROM payment_date), EXTRACT(MONTH FROM payment_date)
    ORDER BY year, month
    """
    
    result = conn.execute(text(query))
    rows = result.fetchall()
    
    print("\n2024년 4-5월 결제 현황:")
    for row in rows:
        print(f"{int(row.year)}년 {int(row.month)}월: {row.count}건, 총액: {row.total_amount:,.0f}원")
    
    # payments 테이블 구조 확인
    print("\n=== payments 테이블 구조 확인 ===")
    query_columns = """
    SELECT column_name, data_type
    FROM information_schema.columns
    WHERE table_name = 'payments'
    ORDER BY ordinal_position
    """
    
    result = conn.execute(text(query_columns))
    columns = result.fetchall()
    print("Columns:", [col.column_name for col in columns])
    
    # customers 테이블 연결하여 상세 데이터 확인
    print("\n=== 2024년 4월 결제 상세 (처음 10건) ===")
    query_april = """
    SELECT p.payment_date, c.name as customer_name, p.service_type, p.amount, p.memo
    FROM payments p
    JOIN customers c ON p.customer_id = c.id
    WHERE p.payment_date >= '2024-04-01' AND p.payment_date < '2024-05-01'
    ORDER BY p.payment_date
    LIMIT 10
    """
    
    result = conn.execute(text(query_april))
    april_data = result.fetchall()
    
    for row in april_data:
        print(f"{row.payment_date.strftime('%Y-%m-%d')}: {row.customer_name} - {row.service_type} - {row.amount:,}원")
    
    print("\n=== 2024년 5월 결제 상세 (처음 10건) ===")
    query_may = """
    SELECT p.payment_date, c.name as customer_name, p.service_type, p.amount, p.memo
    FROM payments p
    JOIN customers c ON p.customer_id = c.id
    WHERE p.payment_date >= '2024-05-01' AND p.payment_date < '2024-06-01'
    ORDER BY p.payment_date
    LIMIT 10
    """
    
    result = conn.execute(text(query_may))
    may_data = result.fetchall()
    
    for row in may_data:
        print(f"{row.payment_date.strftime('%Y-%m-%d')}: {row.customer_name} - {row.service_type} - {row.amount:,}원")
    
    # 전체 월별 통계
    print("\n=== 전체 월별 결제 통계 ===")
    query_all = """
    SELECT 
        EXTRACT(YEAR FROM payment_date) as year,
        EXTRACT(MONTH FROM payment_date) as month,
        COUNT(*) as count,
        SUM(amount) as total_amount
    FROM payments
    WHERE payment_date >= '2024-01-01'
    GROUP BY EXTRACT(YEAR FROM payment_date), EXTRACT(MONTH FROM payment_date)
    ORDER BY year, month
    """
    
    result = conn.execute(text(query_all))
    all_data = result.fetchall()
    
    for row in all_data:
        print(f"{int(row.year)}년 {int(row.month)}월: {row.count}건, 총액: {row.total_amount:,.0f}원")