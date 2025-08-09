"""
테스트 마이그레이션 스크립트
실제 엑셀 데이터의 일부를 테스트로 마이그레이션합니다.
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
from models.lead import MarketingLead

EXCEL_DIR = "/Users/vibetj/coding/center/docs/AIBIO 관리대장 파일모음"

async def test_customer_migration():
    """고객 데이터 테스트 마이그레이션"""
    async with AsyncSession(engine) as session:
        try:
            # 고객관리대장 읽기 (header를 수동으로 지정)
            file_path = os.path.join(EXCEL_DIR, "고객관리대장2025.xlsm")
            df = pd.read_excel(file_path, sheet_name="전체 고객관리대장", header=2)
            
            print("컬럼 확인:", list(df.columns)[:10])
            
            # 첫 5명의 고객만 테스트
            count = 0
            for _, row in df.head(5).iterrows():
                # NO가 숫자인 경우만 처리
                if pd.isna(row.get('NO')) or not str(row.get('NO')).isdigit():
                    continue
                
                name = str(row.get('성함', '')).strip()
                if not name or name == 'nan':
                    continue
                
                print(f"\n고객 {count+1}:")
                print(f"  이름: {name}")
                print(f"  연락처: {row.get('연락처')}")
                print(f"  첫방문일: {row.get('첫방문일')}")
                print(f"  거주지역: {row.get('거주지역')}")
                
                count += 1
                
        except Exception as e:
            print(f"오류: {e}")
            import traceback
            traceback.print_exc()

async def test_lead_migration():
    """리드 데이터 테스트 마이그레이션"""
    async with AsyncSession(engine) as session:
        try:
            # 리드 데이터 읽기
            file_path = os.path.join(EXCEL_DIR, "유입 고객 DB 리스트.xlsx")
            df = pd.read_excel(file_path, sheet_name="신규")
            
            print("\n\n리드 데이터 컬럼:", list(df.columns)[:10])
            
            # 첫 5명의 리드만 테스트
            count = 0
            for _, row in df.head(5).iterrows():
                name = str(row.get('이름', '')).strip()
                if not name or name == 'nan':
                    continue
                
                print(f"\n리드 {count+1}:")
                print(f"  이름: {name}")
                print(f"  유입경로: {row.get('유입경로')}")
                print(f"  연락처: {row.get('연락처')}")
                print(f"  DB입력일: {row.get('DB입력일')}")
                
                count += 1
                
        except Exception as e:
            print(f"오류: {e}")
            import traceback
            traceback.print_exc()

async def test_payment_migration():
    """결제 데이터 테스트 마이그레이션"""
    async with AsyncSession(engine) as session:
        try:
            # 결제 데이터 읽기
            file_path = os.path.join(EXCEL_DIR, "★2025년 AIBIO 결제현황.xlsx")
            
            # 전체 결제대장 시트 읽기
            df = pd.read_excel(file_path, sheet_name="전체 결제대장", header=1)
            
            print("\n\n결제 데이터 컬럼:", list(df.columns)[:10])
            
            # 첫 5개 결제만 테스트
            count = 0
            for _, row in df.head(5).iterrows():
                if pd.isna(row.get('NO')) or not str(row.get('NO')).isdigit():
                    continue
                
                print(f"\n결제 {count+1}:")
                print(f"  결제일자: {row.get('결제일자')}")
                print(f"  고객명: {row.get('고객명')}")
                print(f"  결제 프로그램: {row.get('결제 프로그램')}")
                print(f"  결제 금액: {row.get('결제 금액')}")
                
                count += 1
                
        except Exception as e:
            print(f"오류: {e}")
            import traceback
            traceback.print_exc()

async def main():
    """메인 실행 함수"""
    print("=== 엑셀 데이터 테스트 마이그레이션 ===")
    
    await test_customer_migration()
    await test_lead_migration()
    await test_payment_migration()

if __name__ == "__main__":
    asyncio.run(main())