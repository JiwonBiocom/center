#!/usr/bin/env python3
"""
2025년 5월 결제 데이터 삭제 스크립트
"""

import os
import sys
from datetime import date
from sqlalchemy import create_engine, and_
from sqlalchemy.orm import sessionmaker

# 프로젝트 루트 디렉토리를 Python 경로에 추가
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.config import settings
from models.payment import Payment

# 데이터베이스 설정
DATABASE_URL = settings.DATABASE_URL or "postgresql://aibio_user:aibio_password@localhost:5432/aibio_center"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def delete_may_2025_payments():
    """2025년 5월 결제 데이터 삭제"""
    
    session = SessionLocal()
    
    try:
        # 2025년 5월 결제 데이터 조회
        may_payments = session.query(Payment).filter(
            and_(
                Payment.payment_date >= date(2025, 5, 1),
                Payment.payment_date < date(2025, 6, 1)
            )
        ).all()
        
        print(f"삭제할 결제 건수: {len(may_payments)}건")
        
        if may_payments:
            total_amount = sum(float(p.amount) for p in may_payments)
            print(f"삭제할 결제 총액: {total_amount:,.0f}원")
            
            # 삭제 확인
            confirm = input("\n정말로 삭제하시겠습니까? (yes/no): ")
            if confirm.lower() == 'yes':
                for payment in may_payments:
                    session.delete(payment)
                
                session.commit()
                print("✅ 삭제 완료!")
            else:
                print("삭제 취소됨")
        else:
            print("삭제할 데이터가 없습니다.")
            
    except Exception as e:
        print(f"오류 발생: {e}")
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    delete_may_2025_payments()