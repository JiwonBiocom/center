#!/usr/bin/env python3
"""
2025년 전체 매출 현황 확인
"""

import os
import sys
from datetime import date
from sqlalchemy import create_engine, text, and_, extract
from sqlalchemy.orm import sessionmaker

# 프로젝트 루트 디렉토리를 Python 경로에 추가
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.config import settings
from models.payment import Payment

# 데이터베이스 설정
DATABASE_URL = settings.DATABASE_URL or "postgresql://aibio_user:aibio_password@localhost:5432/aibio_center"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def check_2025_revenue():
    """2025년 전체 매출 확인"""
    
    session = SessionLocal()
    
    try:
        # 월별 매출 집계
        monthly_query = text("""
            SELECT 
                EXTRACT(MONTH FROM payment_date) as month,
                COUNT(*) as count,
                SUM(amount) as total
            FROM payments
            WHERE EXTRACT(YEAR FROM payment_date) = 2025
            GROUP BY EXTRACT(MONTH FROM payment_date)
            ORDER BY month
        """)
        
        result = session.execute(monthly_query)
        monthly_data = result.fetchall()
        
        print(f"\n{'='*60}")
        print("2025년 월별 매출 현황")
        print('='*60)
        print(f"{'월':>5} {'건수':>10} {'매출액':>20}")
        print('-'*60)
        
        total_count = 0
        total_revenue = 0
        
        for row in monthly_data:
            month = int(row.month)
            count = row.count
            revenue = float(row.total)
            total_count += count
            total_revenue += revenue
            
            print(f"{month:>4}월 {count:>10}건 {revenue:>20,.0f}원")
        
        print('-'*60)
        print(f"{'합계':>5} {total_count:>10}건 {total_revenue:>20,.0f}원")
        
        # 5월 상세 확인
        may_query = text("""
            SELECT 
                payment_date,
                COUNT(*) as count,
                SUM(CASE WHEN amount > 0 THEN amount ELSE 0 END) as revenue,
                SUM(CASE WHEN amount < 0 THEN amount ELSE 0 END) as refund,
                SUM(amount) as net_total
            FROM payments
            WHERE EXTRACT(YEAR FROM payment_date) = 2025
            AND EXTRACT(MONTH FROM payment_date) = 5
            GROUP BY payment_date
            ORDER BY payment_date
        """)
        
        may_result = session.execute(may_query)
        may_data = may_result.fetchall()
        
        print(f"\n{'='*80}")
        print("2025년 5월 일별 매출 상세")
        print('='*80)
        print(f"{'날짜':^12} {'건수':>6} {'수입':>15} {'환불':>15} {'순매출':>15}")
        print('-'*80)
        
        for row in may_data:
            date_str = row.payment_date.strftime('%Y-%m-%d')
            print(f"{date_str:^12} {row.count:>6}건 {float(row.revenue):>15,.0f} {float(row.refund):>15,.0f} {float(row.net_total):>15,.0f}")
        
        print('-'*80)
        
        # 5월 전체 합계
        may_total_query = text("""
            SELECT 
                COUNT(*) as count,
                SUM(CASE WHEN amount > 0 THEN amount ELSE 0 END) as revenue,
                SUM(CASE WHEN amount < 0 THEN amount ELSE 0 END) as refund,
                SUM(amount) as net_total
            FROM payments
            WHERE EXTRACT(YEAR FROM payment_date) = 2025
            AND EXTRACT(MONTH FROM payment_date) = 5
        """)
        
        may_total_result = session.execute(may_total_query)
        may_total = may_total_result.fetchone()
        
        print(f"\n5월 총계:")
        print(f"- 총 건수: {may_total.count}건")
        print(f"- 총 수입: {float(may_total.revenue):,.0f}원")
        print(f"- 총 환불: {float(may_total.refund):,.0f}원")
        print(f"- 순 매출: {float(may_total.net_total):,.0f}원")
        
        if float(may_total.net_total) == 11933310:
            print("\n✅ 5월 매출액이 Excel과 정확히 일치합니다!")
        
    except Exception as e:
        print(f"오류 발생: {e}")
        import traceback
        traceback.print_exc()
    finally:
        session.close()

if __name__ == "__main__":
    check_2025_revenue()