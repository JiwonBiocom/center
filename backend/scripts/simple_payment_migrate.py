"""
간단한 결제 데이터 마이그레이션
"""

import asyncio
import sys
import os
import pandas as pd
from datetime import datetime, date

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from core.database import engine
from models.customer import Customer
from models.payment import Payment

EXCEL_DIR = "/Users/vibetj/coding/center/docs/AIBIO 관리대장 파일모음"

async def migrate_payments():
    async with AsyncSession(engine) as session:
        # 고객 정보 로드
        result = await session.execute(select(Customer))
        customers = result.scalars().all()
        customer_map = {c.name: c.customer_id for c in customers}
        print(f"고객 {len(customers)}명 로드")
        
        file_path = os.path.join(EXCEL_DIR, "★2025년 AIBIO 결제현황.xlsx")
        
        # 전체 결제대장 시트 처리
        print("\n전체 결제대장 처리 중...")
        df = pd.read_excel(file_path, sheet_name="전체 결제대장", header=None)
        
        count = 0
        # 3번째 행부터 데이터 시작 (0-indexed이므로 2)
        for i in range(3, len(df)):
            row = df.iloc[i]
            
            # 첫 번째 컬럼이 숫자가 아니면 스킵
            if pd.isna(row[0]) or not str(row[0]).strip().replace('-', '').isdigit():
                continue
            
            # 데이터 추출
            payment_date = row[1] if not pd.isna(row[1]) else None
            customer_name = str(row[2]).strip() if not pd.isna(row[2]) else None
            amount = row[4] if not pd.isna(row[4]) else 0
            
            if not customer_name or amount <= 0:
                continue
            
            # 날짜 처리
            if isinstance(payment_date, datetime):
                payment_date = payment_date.date()
            elif not payment_date:
                payment_date = date.today()
            
            # 고객 찾기
            customer_id = customer_map.get(customer_name)
            if not customer_id:
                # 새 고객 생성
                customer = Customer(name=customer_name, assigned_staff='직원')
                session.add(customer)
                await session.flush()
                customer_id = customer.customer_id
                customer_map[customer_name] = customer_id
            
            # 결제 생성
            payment = Payment(
                customer_id=customer_id,
                payment_date=payment_date,
                amount=float(amount),
                payment_method='카드',
                payment_staff='직원'
            )
            session.add(payment)
            count += 1
            
            if count % 50 == 0:
                print(f"  {count}건 처리...")
                await session.commit()
        
        await session.commit()
        print(f"\n총 {count}건 마이그레이션 완료")
        
        # 확인
        result = await session.execute(select(Payment))
        final_count = len(result.scalars().all())
        print(f"최종 결제 데이터: {final_count}건")

if __name__ == "__main__":
    asyncio.run(migrate_payments())