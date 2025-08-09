"""
결제 데이터 마이그레이션 수정 스크립트
"""

import sys
import os
import pandas as pd
from datetime import datetime, date
import re

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, create_engine
from models.customer import Customer
from models.payment import Payment
from core.config import settings

# 엑셀 파일 경로
EXCEL_DIR = "/Users/vibetj/coding/center/docs/AIBIO 관리대장 파일모음"

# 동기 엔진 생성
DATABASE_URL = settings.DATABASE_URL or "postgresql://aibio_user:aibio_password@localhost:5432/aibio_center"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def parse_amount(amount):
    """금액 파싱"""
    if pd.isna(amount):
        return 0
    
    amount_str = str(amount)
    # 숫자가 아닌 문자 제거
    amount_str = re.sub(r'[^0-9.-]', '', amount_str)
    
    try:
        return float(amount_str)
    except:
        return 0

def parse_date(date_value):
    """날짜 파싱"""
    if pd.isna(date_value):
        return None
    
    if isinstance(date_value, datetime):
        return date_value.date()
    
    if isinstance(date_value, date):
        return date_value
    
    return None

def migrate_payments():
    session = SessionLocal()
    
    try:
        # 고객 매핑 로드
        result = session.execute(select(Customer))
        customers = result.scalars().all()
        customer_map = {c.name: c.customer_id for c in customers}
        print(f"고객 {len(customers)}명 로드")
        
        file_path = os.path.join(EXCEL_DIR, "★2025년 AIBIO 결제현황.xlsx")
        
        # 전체 결제대장 읽기 - header=None으로 읽어서 수동으로 처리
        df = pd.read_excel(file_path, sheet_name="전체 결제대장", header=None)
        
        count = 0
        # 데이터는 3번째 행(index 2)부터 시작
        for i in range(2, len(df)):
            row = df.iloc[i]
            
            # 첫 번째 컬럼이 숫자인 경우만 처리
            if pd.isna(row[0]):
                continue
            
            # 숫자인지 확인
            try:
                int(row[0])
            except:
                continue
            
            # 데이터 추출
            payment_date = parse_date(row[1])
            customer_name = str(row[2]).strip() if not pd.isna(row[2]) else None
            program = str(row[3]).strip() if not pd.isna(row[3]) else None
            amount = parse_amount(row[4])
            
            if not customer_name or amount == 0:
                continue
            
            # 고객 찾기 또는 생성
            customer_id = customer_map.get(customer_name)
            if not customer_id:
                # 새 고객 생성
                customer = Customer(name=customer_name, assigned_staff='직원')
                session.add(customer)
                session.flush()
                customer_id = customer.customer_id
                customer_map[customer_name] = customer_id
            
            # 결제 생성
            payment = Payment(
                customer_id=customer_id,
                payment_date=payment_date or date.today(),
                amount=amount,
                payment_method='카드',
                payment_staff='직원'
            )
            
            session.add(payment)
            count += 1
            
            if count % 50 == 0:
                print(f"  {count}건 처리...")
                session.commit()
        
        session.commit()
        print(f"\n총 {count}건 마이그레이션 완료")
        
        # 확인
        result = session.execute(select(Payment))
        final_count = len(result.scalars().all())
        print(f"최종 결제 데이터: {final_count}건")
        
    except Exception as e:
        print(f"오류 발생: {e}")
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    print("결제 데이터를 마이그레이션합니다.")
    migrate_payments()