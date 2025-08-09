"""
AIBIO 엑셀 데이터 마이그레이션 스크립트

이 스크립트는 기존 엑셀 파일들의 데이터를 정제하고 데이터베이스로 이관합니다.
- 고객 데이터 통합 및 중복 제거
- 결제 내역 이관
- 서비스 이용 내역 이관
- 마케팅 리드 데이터 이관
"""

import asyncio
import sys
import os
import pandas as pd
from datetime import datetime, date
from typing import Dict, List, Optional
import re

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from core.database import engine
from models.customer import Customer
from models.payment import Payment
from models.service import ServiceUsage, ServiceType
from models.package import Package, PackagePurchase
from models.lead import MarketingLead

# 엑셀 파일 경로
EXCEL_DIR = "/Users/vibetj/coding/center/docs/AIBIO 관리대장 파일모음"
CUSTOMER_FILE = os.path.join(EXCEL_DIR, "고객관리대장2025.xlsm")
PAYMENT_FILE = os.path.join(EXCEL_DIR, "★2025년 AIBIO 결제현황.xlsx")
LEAD_FILE = os.path.join(EXCEL_DIR, "유입 고객 DB 리스트.xlsx")

class ExcelDataMigrator:
    def __init__(self):
        self.session = None
        self.customer_map = {}  # 이름_전화번호 -> customer_id 매핑
        self.service_type_map = {}  # 서비스명 -> service_type_id 매핑
        self.package_map = {}  # 패키지명 -> package_id 매핑
        
    async def migrate_all(self):
        """전체 마이그레이션 프로세스"""
        async with AsyncSession(engine) as session:
            self.session = session
            
            print("=== AIBIO 데이터 마이그레이션 시작 ===")
            
            # 1. 기본 데이터 로드
            await self.load_base_data()
            
            # 2. 고객 데이터 마이그레이션
            print("\n1. 고객 데이터 마이그레이션...")
            await self.migrate_customers()
            
            # 3. 결제 데이터 마이그레이션
            print("\n2. 결제 데이터 마이그레이션...")
            await self.migrate_payments()
            
            # 4. 서비스 이용 데이터 마이그레이션
            print("\n3. 서비스 이용 데이터 마이그레이션...")
            await self.migrate_service_usage()
            
            # 5. 마케팅 리드 데이터 마이그레이션
            print("\n4. 마케팅 리드 데이터 마이그레이션...")
            await self.migrate_leads()
            
            print("\n=== 마이그레이션 완료 ===")
    
    async def load_base_data(self):
        """기본 데이터 로드 (서비스 타입, 패키지 등)"""
        # 서비스 타입 로드
        result = await self.session.execute(select(ServiceType))
        service_types = result.scalars().all()
        for st in service_types:
            self.service_type_map[st.service_name.lower()] = st.service_type_id
        
        # 패키지 로드
        result = await self.session.execute(select(Package))
        packages = result.scalars().all()
        for pkg in packages:
            self.package_map[pkg.package_name] = pkg.package_id
    
    def clean_phone(self, phone: str) -> Optional[str]:
        """전화번호 정제"""
        if pd.isna(phone) or not phone:
            return None
        
        # 숫자만 추출
        numbers = re.sub(r'[^0-9]', '', str(phone))
        
        # 한국 휴대폰 번호 형식으로 변환
        if len(numbers) == 10:  # 010xxxxxxxx
            return f"{numbers[:3]}-{numbers[3:6]}-{numbers[6:]}"
        elif len(numbers) == 11:  # 010xxxxxxxx
            return f"{numbers[:3]}-{numbers[3:7]}-{numbers[7:]}"
        
        return None
    
    def parse_date(self, date_str) -> Optional[date]:
        """날짜 파싱"""
        if pd.isna(date_str):
            return None
        
        if isinstance(date_str, datetime):
            return date_str.date()
        
        # 다양한 날짜 형식 처리
        date_formats = [
            "%Y-%m-%d",
            "%Y.%m.%d",
            "%Y/%m/%d",
            "%d-%m-%Y",
            "%d.%m.%Y",
            "%d/%m/%Y"
        ]
        
        for fmt in date_formats:
            try:
                return datetime.strptime(str(date_str), fmt).date()
            except:
                continue
        
        return None
    
    async def migrate_customers(self):
        """고객 데이터 마이그레이션"""
        try:
            # 엑셀 파일 읽기
            df = pd.read_excel(CUSTOMER_FILE, sheet_name="전체 고객관리대장")
            
            # 기존 고객 로드
            result = await self.session.execute(select(Customer))
            existing_customers = {f"{c.name}_{c.phone}": c for c in result.scalars().all()}
            
            new_customers = 0
            updated_customers = 0
            
            for _, row in df.iterrows():
                name = str(row.get('성함', '')).strip()
                if not name or pd.isna(name):
                    continue
                
                phone = self.clean_phone(row.get('연락처'))
                key = f"{name}_{phone}" if phone else f"{name}_"
                
                # 중복 확인
                if key in existing_customers:
                    # 기존 고객 업데이트
                    customer = existing_customers[key]
                    self.customer_map[key] = customer.customer_id
                    updated_customers += 1
                    continue
                
                # 신규 고객 생성
                customer = Customer(
                    name=name,
                    phone=phone,
                    first_visit_date=self.parse_date(row.get('첫방문일')),
                    region=str(row.get('거주지역', '')).strip() if not pd.isna(row.get('거주지역')) else None,
                    referral_source=str(row.get('방문경로', '')).strip() if not pd.isna(row.get('방문경로')) else None,
                    health_concerns=str(row.get('호소문제', '')).strip() if not pd.isna(row.get('호소문제')) else None,
                    notes=str(row.get('비고', '')).strip() if not pd.isna(row.get('비고')) else None,
                    assigned_staff=str(row.get('담당자', '직원')).strip() if not pd.isna(row.get('담당자')) else '직원'
                )
                
                self.session.add(customer)
                await self.session.flush()
                
                self.customer_map[key] = customer.customer_id
                new_customers += 1
            
            await self.session.commit()
            print(f"  - 신규 고객: {new_customers}명")
            print(f"  - 기존 고객: {updated_customers}명")
            
        except Exception as e:
            print(f"  ! 고객 데이터 마이그레이션 오류: {e}")
            await self.session.rollback()
    
    async def migrate_payments(self):
        """결제 데이터 마이그레이션"""
        try:
            # 엑셀 파일 읽기
            xl = pd.ExcelFile(PAYMENT_FILE)
            
            total_payments = 0
            
            # 월별 시트 처리
            for sheet_name in xl.sheet_names:
                if sheet_name == "전체매출":
                    continue
                
                df = pd.read_excel(xl, sheet_name=sheet_name)
                
                for _, row in df.iterrows():
                    customer_name = str(row.get('고객명', '')).strip()
                    if not customer_name or pd.isna(customer_name):
                        continue
                    
                    # 고객 찾기
                    customer_id = None
                    for key, cid in self.customer_map.items():
                        if customer_name in key:
                            customer_id = cid
                            break
                    
                    if not customer_id:
                        # 새 고객 생성
                        customer = Customer(name=customer_name, assigned_staff='직원')
                        self.session.add(customer)
                        await self.session.flush()
                        customer_id = customer.customer_id
                        self.customer_map[f"{customer_name}_"] = customer_id
                    
                    # 결제 금액 파싱
                    amount = 0
                    amount_str = str(row.get('결제 금액', 0))
                    try:
                        amount = float(re.sub(r'[^0-9.]', '', amount_str))
                    except:
                        continue
                    
                    if amount <= 0:
                        continue
                    
                    # 결제 생성
                    payment = Payment(
                        customer_id=customer_id,
                        payment_date=self.parse_date(row.get('결제일자')) or date.today(),
                        amount=amount,
                        payment_method=str(row.get('결제 방법', '카드')).strip() if not pd.isna(row.get('결제 방법')) else '카드',
                        card_holder_name=str(row.get('카드주', '')).strip() if not pd.isna(row.get('카드주')) else None,
                        approval_number=str(row.get('승인번호', '')).strip() if not pd.isna(row.get('승인번호')) else None,
                        payment_staff=str(row.get('결제 담당자', '직원')).strip() if not pd.isna(row.get('결제 담당자')) else '직원',
                        purchase_type=str(row.get('고객 등급', '')).strip() if not pd.isna(row.get('고객 등급')) else None,
                        purchase_order=int(row.get('구매 차수', 1)) if not pd.isna(row.get('구매 차수')) else 1
                    )
                    
                    self.session.add(payment)
                    total_payments += 1
                
                await self.session.commit()
            
            print(f"  - 총 결제 건수: {total_payments}건")
            
        except Exception as e:
            print(f"  ! 결제 데이터 마이그레이션 오류: {e}")
            await self.session.rollback()
    
    async def migrate_service_usage(self):
        """서비스 이용 데이터 마이그레이션"""
        try:
            # 엑셀 파일 읽기
            xl = pd.ExcelFile(CUSTOMER_FILE)
            
            total_usage = 0
            
            # 월별 이용현황 시트 처리
            for sheet_name in xl.sheet_names:
                if "이용현황" not in sheet_name:
                    continue
                
                df = pd.read_excel(xl, sheet_name=sheet_name)
                
                # 날짜 컬럼 찾기
                date_columns = [col for col in df.columns if any(x in str(col) for x in ['일', '날짜', 'Date'])]
                
                for date_col in date_columns:
                    # 각 날짜별 처리
                    for _, row in df.iterrows():
                        customer_name = str(row.get('고객명', '')).strip()
                        if not customer_name or pd.isna(customer_name):
                            continue
                        
                        service_info = row.get(date_col)
                        if pd.isna(service_info) or not service_info:
                            continue
                        
                        # 고객 찾기
                        customer_id = None
                        for key, cid in self.customer_map.items():
                            if customer_name in key:
                                customer_id = cid
                                break
                        
                        if not customer_id:
                            continue
                        
                        # 서비스 타입 추출
                        service_type_id = 1  # 기본값
                        service_info_lower = str(service_info).lower()
                        for service_name, st_id in self.service_type_map.items():
                            if service_name in service_info_lower:
                                service_type_id = st_id
                                break
                        
                        # 서비스 이용 생성
                        usage = ServiceUsage(
                            customer_id=customer_id,
                            service_date=self.parse_date(date_col) or date.today(),
                            service_type_id=service_type_id,
                            session_details=str(service_info),
                            created_by='직원'
                        )
                        
                        self.session.add(usage)
                        total_usage += 1
                
                if total_usage > 0 and total_usage % 100 == 0:
                    await self.session.commit()
            
            await self.session.commit()
            print(f"  - 총 서비스 이용: {total_usage}건")
            
        except Exception as e:
            print(f"  ! 서비스 이용 데이터 마이그레이션 오류: {e}")
            await self.session.rollback()
    
    async def migrate_leads(self):
        """마케팅 리드 데이터 마이그레이션"""
        try:
            # 엑셀 파일 읽기
            df = pd.read_excel(LEAD_FILE, sheet_name="신규")
            
            total_leads = 0
            
            for _, row in df.iterrows():
                name = str(row.get('이름', '')).strip()
                if not name or pd.isna(name):
                    continue
                
                # 리드 생성
                lead = MarketingLead(
                    name=name,
                    phone=self.clean_phone(row.get('전화번호')),
                    lead_date=self.parse_date(row.get('DB입력')) or date.today(),
                    channel=str(row.get('유입', '')).strip() if not pd.isna(row.get('유입')) else None,
                    db_entry_date=self.parse_date(row.get('DB입력')),
                    phone_consult_date=self.parse_date(row.get('전화상담')),
                    visit_consult_date=self.parse_date(row.get('방문상담')),
                    registration_date=self.parse_date(row.get('등록')),
                    status='new'
                )
                
                # 상태 업데이트
                if lead.registration_date:
                    lead.status = 'converted'
                elif lead.visit_consult_date:
                    lead.status = 'visit_consulted'
                elif lead.phone_consult_date:
                    lead.status = 'phone_consulted'
                elif lead.db_entry_date:
                    lead.status = 'db_entered'
                
                self.session.add(lead)
                total_leads += 1
            
            await self.session.commit()
            print(f"  - 총 리드: {total_leads}건")
            
        except Exception as e:
            print(f"  ! 리드 데이터 마이그레이션 오류: {e}")
            await self.session.rollback()

async def main():
    """메인 실행 함수"""
    migrator = ExcelDataMigrator()
    await migrator.migrate_all()

if __name__ == "__main__":
    print("주의: 이 스크립트는 실제 엑셀 데이터를 데이터베이스로 이관합니다.")
    response = input("계속하시겠습니까? (y/n): ")
    
    if response.lower() == 'y':
        asyncio.run(main())
    else:
        print("마이그레이션이 취소되었습니다.")