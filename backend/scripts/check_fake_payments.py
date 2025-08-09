"""
가짜 결제 데이터 확인 및 삭제 스크립트
"""

import sys
import os
import pandas as pd
from datetime import datetime, date
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, delete, create_engine
from decimal import Decimal

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.payment import Payment
from models.customer import Customer
from core.config import settings

# 엑셀 파일 경로
EXCEL_PATH = "/Users/vibetj/coding/center/docs/AIBIO 관리대장 파일모음/★2025년 AIBIO 결제현황.xlsx"

# 데이터베이스 연결
DATABASE_URL = settings.DATABASE_URL or "postgresql://aibio_user:aibio_password@localhost:5432/aibio_center"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def parse_amount(amount):
    """금액 파싱"""
    if pd.isna(amount):
        return 0
    
    amount_str = str(amount)
    # 숫자가 아닌 문자 제거
    import re
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
    
    # 문자열 날짜 파싱
    date_str = str(date_value).strip()
    for fmt in ['%Y-%m-%d', '%Y.%m.%d', '%Y/%m/%d', '%d.%m.%Y']:
        try:
            return datetime.strptime(date_str, fmt).date()
        except:
            continue
    
    return None

def main():
    session = SessionLocal()
    
    print("=== 가짜 결제 데이터 확인 ===\n")
    
    # 1. Excel 파일에서 실제 결제 데이터 읽기
    print("1. Excel 파일에서 실제 결제 데이터 읽기...")
    df = pd.read_excel(EXCEL_PATH, sheet_name="전체 결제대장", skiprows=2)
    
    excel_payments = []
    for idx, row in df.iterrows():
        # 첫 번째 열이 숫자인 경우만 처리
        no_value = row.iloc[0]
        if pd.isna(no_value):
            continue
            
        try:
            int(no_value)
        except:
            continue
        
        customer_name = str(row.get('고객명', '')).strip()
        if not customer_name or customer_name == 'nan':
            continue
        
        amount = parse_amount(row.get('결제 금액'))
        if amount == 0:
            continue
        
        payment_date = parse_date(row.get('결제일자'))
        
        excel_payments.append({
            'customer_name': customer_name,
            'amount': amount,
            'date': payment_date,
            'program': str(row.get('결제 프로그램', '')).strip()
        })
    
    print(f"  - Excel 파일에서 {len(excel_payments)}건의 결제 데이터 발견")
    
    # 2. 데이터베이스에서 모든 결제 데이터 조회
    print("\n2. 데이터베이스에서 모든 결제 데이터 조회...")
    result = session.execute(
        select(Payment, Customer)
        .join(Customer)
        .order_by(Payment.payment_date.desc())
    )
    
    db_payments = []
    for payment, customer in result:
        db_payments.append({
            'payment_id': payment.payment_id,
            'customer_name': customer.name,
            'amount': float(payment.amount),
            'date': payment.payment_date,
            'purchase_type': payment.purchase_type
        })
    
    print(f"  - 데이터베이스에서 {len(db_payments)}건의 결제 데이터 발견")
    
    # 3. Excel에 없는 결제 데이터 찾기
    print("\n3. Excel 파일에 없는 가짜 결제 데이터 찾기...")
    fake_payments = []
    
    for db_payment in db_payments:
        found = False
        for excel_payment in excel_payments:
            # 고객명과 금액이 일치하는지 확인
            if (db_payment['customer_name'] == excel_payment['customer_name'] and
                abs(db_payment['amount'] - excel_payment['amount']) < 0.01):
                found = True
                break
        
        if not found:
            fake_payments.append(db_payment)
    
    # 4. 가짜 데이터 출력
    if fake_payments:
        print(f"\n  ! 가짜 결제 데이터 {len(fake_payments)}건 발견:")
        for fp in fake_payments:
            print(f"    - ID: {fp['payment_id']}, 고객: {fp['customer_name']}, "
                  f"금액: {fp['amount']:,.0f}원, 날짜: {fp['date']}")
        
        # 5. 자동으로 삭제 진행
        print("\n가짜 데이터를 삭제합니다...")
        
        if True:  # 자동 삭제
            # 가짜 데이터 삭제
            deleted_count = 0
            for fp in fake_payments:
                result = session.execute(
                    delete(Payment).where(Payment.payment_id == fp['payment_id'])
                )
                deleted_count += result.rowcount
            
            session.commit()
            print(f"\n  ✓ {deleted_count}건의 가짜 결제 데이터를 삭제했습니다.")
            
            # 6. 삭제 후 통계 확인
            print("\n4. 삭제 후 월별 매출 통계:")
            result = session.execute(
                select(Payment).order_by(Payment.payment_date)
            )
            
            monthly_stats = {}
            for payment in result.scalars().all():
                month_key = f"{payment.payment_date.year}-{payment.payment_date.month:02d}"
                if month_key not in monthly_stats:
                    monthly_stats[month_key] = 0
                monthly_stats[month_key] += float(payment.amount)
            
            for month, total in sorted(monthly_stats.items()):
                print(f"  - {month}: {total:,.0f}원")
            
        else:
            print("\n  - 삭제가 취소되었습니다.")
    else:
        print("  ✓ 가짜 결제 데이터가 없습니다. 모든 데이터가 Excel 파일과 일치합니다.")
    
    session.close()

if __name__ == "__main__":
    main()