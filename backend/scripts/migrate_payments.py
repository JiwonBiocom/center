"""
결제 데이터만 마이그레이션하는 스크립트
엑셀 파일 구조에 맞춰 수정
"""

import asyncio
import sys
import os
import pandas as pd
from datetime import datetime, date
import re

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from core.database import engine
from models.customer import Customer
from models.payment import Payment

# 엑셀 파일 경로
EXCEL_DIR = "/Users/vibetj/coding/center/docs/AIBIO 관리대장 파일모음"

class PaymentMigrator:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.customer_map = {}
        
    async def load_customers(self):
        """기존 고객 정보 로드"""
        result = await self.session.execute(select(Customer))
        customers = result.scalars().all()
        
        for customer in customers:
            self.customer_map[customer.name] = customer.customer_id
            # 이름 변형도 추가 (공백 제거 등)
            clean_name = customer.name.replace(' ', '').strip()
            self.customer_map[clean_name] = customer.customer_id
        
        print(f"고객 {len(customers)}명 로드 완료")
    
    def parse_date(self, date_value):
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
    
    def parse_amount(self, amount):
        """금액 파싱"""
        if pd.isna(amount):
            return 0
        
        amount_str = str(amount)
        # 숫자가 아닌 문자 제거 (쉼표, 원 등)
        amount_str = re.sub(r'[^0-9.]', '', amount_str)
        
        try:
            return float(amount_str)
        except:
            return 0
    
    async def migrate_from_sheet(self, file_path, sheet_name):
        """특정 시트에서 결제 데이터 마이그레이션"""
        print(f"\n  - {sheet_name} 시트 처리 중...")
        
        try:
            # 엑셀 읽기 - header=1 (2번째 행이 헤더)
            df = pd.read_excel(file_path, sheet_name=sheet_name, header=1)
            
            # 컬럼명 정리
            df.columns = df.columns.str.strip()
            
            count = 0
            for idx, row in df.iterrows():
                # 첫 번째 컬럼이 숫자인 경우만 처리
                first_col = df.columns[0] if len(df.columns) > 0 else None
                if first_col and (pd.isna(row[first_col]) or not str(row[first_col]).strip().replace('-', '').isdigit()):
                    continue
                
                # 고객명 찾기
                customer_name = None
                for col in ['고객명', '성함', '이름']:
                    if col in row and not pd.isna(row[col]):
                        customer_name = str(row[col]).strip()
                        break
                
                if not customer_name or customer_name == 'nan':
                    continue
                
                # 금액 찾기
                amount = 0
                for col in ['결제 금액', '결제금액', '금액']:
                    if col in row:
                        amount = self.parse_amount(row[col])
                        if amount > 0:
                            break
                
                if amount <= 0:
                    continue
                
                # 날짜 찾기
                payment_date = None
                for col in ['결제일자', '결제일', '날짜']:
                    if col in row:
                        payment_date = self.parse_date(row[col])
                        if payment_date:
                            break
                
                if not payment_date:
                    payment_date = date.today()
                
                # 고객 ID 찾기
                customer_id = self.customer_map.get(customer_name)
                if not customer_id:
                    # 새 고객 생성
                    customer = Customer(name=customer_name, assigned_staff='직원')
                    self.session.add(customer)
                    await self.session.flush()
                    customer_id = customer.customer_id
                    self.customer_map[customer_name] = customer_id
                
                # 결제 방법
                payment_method = '카드'  # 기본값
                for col in ['결제 방법', '결제방법']:
                    if col in row and not pd.isna(row[col]):
                        payment_method = str(row[col]).strip()
                        break
                
                # 결제 정보 생성
                payment = Payment(
                    customer_id=customer_id,
                    payment_date=payment_date,
                    amount=amount,
                    payment_method=payment_method,
                    payment_staff='직원'
                )
                
                self.session.add(payment)
                count += 1
                
                if count % 100 == 0:
                    await self.session.commit()
                    print(f"    {count}건 처리...")
            
            await self.session.commit()
            print(f"    → {count}건 완료")
            return count
            
        except Exception as e:
            print(f"    ! 오류 발생: {e}")
            return 0
    
    async def migrate_all_payments(self):
        """모든 결제 데이터 마이그레이션"""
        print("\n=== 결제 데이터 마이그레이션 시작 ===")
        
        file_path = os.path.join(EXCEL_DIR, "★2025년 AIBIO 결제현황.xlsx")
        
        # 엑셀 파일의 모든 시트 확인
        xl = pd.ExcelFile(file_path)
        
        total_count = 0
        
        # 전체 결제대장 먼저 처리
        if '전체 결제대장' in xl.sheet_names:
            count = await self.migrate_from_sheet(file_path, '전체 결제대장')
            total_count += count
        
        # 월별 시트 처리 (2025년, 2024년, 2023년)
        for sheet_name in xl.sheet_names:
            # 연도와 월이 포함된 시트만 처리
            if any(year in sheet_name for year in ['2025년', '2024년', '2023년', '23년']):
                count = await self.migrate_from_sheet(file_path, sheet_name)
                total_count += count
        
        print(f"\n=== 총 {total_count}건 마이그레이션 완료 ===")

async def main():
    """메인 실행"""
    async with AsyncSession(engine) as session:
        # 기존 결제 데이터 확인
        result = await session.execute(select(Payment))
        existing = len(result.scalars().all())
        
        if existing > 0:
            print(f"기존 결제 데이터 {existing}건이 있습니다.")
            response = input("계속하시겠습니까? (y/n): ")
            if response.lower() != 'y':
                print("취소되었습니다.")
                return
        
        migrator = PaymentMigrator(session)
        await migrator.load_customers()
        await migrator.migrate_all_payments()
        
        # 결과 확인
        result = await session.execute(select(Payment))
        final_count = len(result.scalars().all())
        print(f"\n최종 결제 데이터: {final_count}건")

if __name__ == "__main__":
    asyncio.run(main())