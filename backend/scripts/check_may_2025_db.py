#!/usr/bin/env python3
"""
데이터베이스의 2025년 5월 결제 데이터 확인
"""

import os
import sys
from datetime import datetime
from decimal import Decimal
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# 프로젝트 루트 디렉토리를 Python 경로에 추가
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.config import settings
from core.database import Base, engine
from models.payment import Payment

def check_may_2025_payments():
    """2025년 5월 결제 데이터 확인"""
    
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # 2025년 5월 결제 데이터 조회
        query = text("""
            SELECT 
                p.payment_id,
                p.payment_date,
                c.name as customer_name,
                s.service_type as payment_program,
                p.amount as payment_amount,
                p.payment_staff,
                p.purchase_type as grade
            FROM payments p
            LEFT JOIN customers c ON p.customer_id = c.customer_id
            LEFT JOIN services s ON c.customer_id = s.customer_id
            WHERE EXTRACT(YEAR FROM p.payment_date) = 2025
            AND EXTRACT(MONTH FROM p.payment_date) = 5
            ORDER BY p.payment_date
        """)
        
        result = session.execute(query)
        payments = result.fetchall()
        
        print(f"\n{'='*50}")
        print("데이터베이스의 2025년 5월 결제 현황")
        print('='*50)
        print(f"총 결제 건수: {len(payments)}건")
        
        if payments:
            total_amount = sum(p.payment_amount for p in payments)
            print(f"총 결제 금액: {total_amount:,.0f}원")
            
            print("\n상세 내역:")
            print("-" * 100)
            print(f"{'ID':>5} {'날짜':^12} {'고객명':^10} {'프로그램':^35} {'금액':>12}")
            print("-" * 100)
            
            for p in payments[:10]:  # 처음 10건만 출력
                date_str = p.payment_date.strftime('%Y-%m-%d')
                program = str(p.payment_program)[:35] if p.payment_program else 'N/A'
                print(f"{p.payment_id:>5} {date_str:^12} {p.customer_name:^10} {program:^35} {p.payment_amount:>12,.0f}")
            
            if len(payments) > 10:
                print(f"... 그 외 {len(payments) - 10}건")
                
            print("-" * 100)
            print(f"{'합계':>63} {total_amount:>12,.0f}원")
            
            # 예상 금액과 비교
            expected_total = 11933310
            print(f"\n예상 총액: {expected_total:,.0f}원")
            print(f"차이: {total_amount - expected_total:,.0f}원")
            
            if total_amount == expected_total:
                print("✅ 이미 모든 데이터가 마이그레이션되어 있습니다.")
                return True
            else:
                print("⚠️ 데이터가 불완전합니다. 마이그레이션이 필요합니다.")
                return False
        else:
            print("데이터베이스에 2025년 5월 결제 데이터가 없습니다.")
            print("마이그레이션이 필요합니다.")
            return False
            
    except Exception as e:
        print(f"오류 발생: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        session.close()

if __name__ == "__main__":
    check_may_2025_payments()