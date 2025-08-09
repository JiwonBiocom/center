"""
실제 엑셀 데이터 마이그레이션 스크립트 (동기 버전)
"""

import sys
import os
import pandas as pd
from datetime import datetime, date
import re

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, delete, create_engine
from models.customer import Customer
from models.payment import Payment
from models.service import ServiceUsage, ServiceType
from models.package import Package, PackagePurchase
from models.customer_extended import MarketingLead
from models.kit import KitManagement
from core.config import settings

# 엑셀 파일 경로
EXCEL_DIR = "/Users/vibetj/coding/center/docs/AIBIO 관리대장 파일모음"

# 동기 엔진 생성
DATABASE_URL = settings.DATABASE_URL or "postgresql://aibio_user:aibio_password@localhost:5432/aibio_center"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class DataMigrator:
    def __init__(self):
        self.session = SessionLocal()
        self.customer_map = {}  # 이름 -> customer_id
        self.service_type_map = {}
        
    def clean_phone(self, phone):
        """전화번호 정제"""
        if pd.isna(phone) or not phone:
            return None
        
        # 숫자만 추출
        phone_str = str(phone).replace('-', '').replace(' ', '')
        if not phone_str.isdigit():
            return None
        
        # 010으로 시작하는 11자리로 정규화
        if len(phone_str) == 10 and phone_str.startswith('10'):
            phone_str = '0' + phone_str
        
        if len(phone_str) == 11 and phone_str.startswith('010'):
            return f"{phone_str[:3]}-{phone_str[3:7]}-{phone_str[7:]}"
        
        return None
    
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
        # 숫자가 아닌 문자 제거
        amount_str = re.sub(r'[^0-9.-]', '', amount_str)
        
        try:
            return float(amount_str)
        except:
            return 0
    
    def clean_all_data(self):
        """모든 테이블의 데이터 삭제"""
        print("=== 기존 데이터 삭제 중 ===")
        
        # 의존성 순서대로 삭제
        tables = [
            (ServiceUsage, "서비스 이용"),
            (PackagePurchase, "패키지 구매"),
            (Payment, "결제"),
            (MarketingLead, "리드"),
            (KitManagement, "키트"),
            (Customer, "고객"),
        ]
        
        for model, name in tables:
            result = self.session.execute(delete(model))
            print(f"  - {name}: {result.rowcount}건 삭제")
        
        self.session.commit()
        print("기존 데이터 삭제 완료\n")
    
    def load_service_types(self):
        """서비스 타입 매핑 로드"""
        result = self.session.execute(select(ServiceType))
        for st in result.scalars().all():
            self.service_type_map[st.service_name.lower()] = st.service_type_id
            # 별칭 추가
            if st.service_name == 'brain':
                self.service_type_map['브레인'] = st.service_type_id
            elif st.service_name == 'pulse':
                self.service_type_map['펄스'] = st.service_type_id
            elif st.service_name == 'lymph':
                self.service_type_map['림프'] = st.service_type_id
            elif st.service_name == 'red':
                self.service_type_map['레드'] = st.service_type_id
    
    def migrate_customers(self):
        """고객 데이터 마이그레이션"""
        print("1. 고객 데이터 마이그레이션 중...")
        
        file_path = os.path.join(EXCEL_DIR, "고객관리대장2025.xlsm")
        df = pd.read_excel(file_path, sheet_name="전체 고객관리대장", header=2)
        
        # 중복 전화번호 체크를 위한 세트
        phone_set = set()
        
        count = 0
        for _, row in df.iterrows():
            # NO가 숫자인 경우만 처리
            if pd.isna(row.get('NO')) or not str(row.get('NO')).strip().isdigit():
                continue
            
            name = str(row.get('성함', '')).strip()
            if not name or name == 'nan':
                continue
            
            phone = self.clean_phone(row.get('연락처'))
            
            # 중복 전화번호 체크
            if phone and phone in phone_set:
                phone = None  # 중복 전화번호는 null로 처리
            elif phone:
                phone_set.add(phone)
            
            # 고객 생성
            customer = Customer(
                name=name,
                phone=phone,
                first_visit_date=self.parse_date(row.get('첫방문일')),
                region=str(row.get('거주지역', '')).strip() if not pd.isna(row.get('거주지역')) else None,
                referral_source=str(row.get('방문경로', '')).strip() if not pd.isna(row.get('방문경로')) else None,
                health_concerns=str(row.get('호소문제', '')).strip() if not pd.isna(row.get('호소문제')) else None,
                notes=str(row.get('비고', '')).strip() if not pd.isna(row.get('비고')) else None,
                assigned_staff='직원'
            )
            
            self.session.add(customer)
            self.session.flush()
            
            # 매핑 저장
            self.customer_map[name] = customer.customer_id
            
            count += 1
        
        self.session.commit()
        print(f"  - 고객 {count}명 등록 완료")
    
    def migrate_leads(self):
        """리드 데이터 마이그레이션"""
        print("\n2. 리드 데이터 마이그레이션 중...")
        
        file_path = os.path.join(EXCEL_DIR, "유입 고객 DB 리스트.xlsx")
        df = pd.read_excel(file_path, sheet_name="신규")
        
        count = 0
        for _, row in df.iterrows():
            name = str(row.get('이름', '')).strip()
            if not name or name == 'nan':
                continue
            
            lead = MarketingLead(
                name=name,
                phone=self.clean_phone(row.get('연락처')),
                lead_date=self.parse_date(row.get('DB입력일')) or date.today(),
                channel=str(row.get('유입경로', '')).strip() if not pd.isna(row.get('유입경로')) else None,
                db_entry_date=self.parse_date(row.get('DB입력일')),
                phone_consult_date=self.parse_date(row.get('전화상담일')),
                visit_consult_date=self.parse_date(row.get('방문상담일')),
                registration_date=self.parse_date(row.get('등록일')),
                status='new'
            )
            
            # 상태 업데이트
            if lead.registration_date:
                lead.status = 'converted'
                # 고객과 연결
                if name in self.customer_map:
                    lead.converted_customer_id = self.customer_map[name]
            elif lead.visit_consult_date:
                lead.status = 'visit_consulted'
            elif lead.phone_consult_date:
                lead.status = 'phone_consulted'
            elif lead.db_entry_date:
                lead.status = 'db_entered'
            
            self.session.add(lead)
            count += 1
        
        self.session.commit()
        print(f"  - 리드 {count}건 등록 완료")
    
    def migrate_payments(self):
        """결제 데이터 마이그레이션"""
        print("\n3. 결제 데이터 마이그레이션 중...")
        
        file_path = os.path.join(EXCEL_DIR, "★2025년 AIBIO 결제현황.xlsx")
        
        # 전체 결제대장 읽기
        try:
            # skiprows=2로 헤더 자동 인식
            df_all = pd.read_excel(file_path, sheet_name="전체 결제대장", skiprows=2)
            
            count = 0
            for idx, row in df_all.iterrows():
                # 첫 번째 열(Unnamed: 0)이 숫자인 경우만 처리
                no_value = row.iloc[0]
                if pd.isna(no_value):
                    continue
                    
                # 숫자로 변환 가능한지 확인
                try:
                    int(no_value)
                except:
                    continue
                
                customer_name = str(row.get('고객명', '')).strip()
                if not customer_name or customer_name == 'nan':
                    continue
                
                # 고객 찾기 또는 생성
                customer_id = self.customer_map.get(customer_name)
                if not customer_id:
                    # 새 고객 생성
                    customer = Customer(name=customer_name, assigned_staff='직원')
                    self.session.add(customer)
                    self.session.flush()
                    customer_id = customer.customer_id
                    self.customer_map[customer_name] = customer_id
                
                amount = self.parse_amount(row.get('결제 금액'))
                if amount == 0:
                    continue
                
                # 결제 방법 컬럼이 없으므로 기본값 사용
                payment_method = '카드'
                if '현금' in str(row.get('결제 프로그램', '')):
                    payment_method = '현금'
                elif '계좌' in str(row.get('결제 프로그램', '')):
                    payment_method = '계좌이체'
                
                payment = Payment(
                    customer_id=customer_id,
                    payment_date=self.parse_date(row.get('결제일자')) or date.today(),
                    amount=amount,
                    payment_method=payment_method,
                    payment_staff='직원',
                    purchase_type=str(row.get('결제 프로그램', '')).strip() if not pd.isna(row.get('결제 프로그램')) else None
                )
                
                self.session.add(payment)
                count += 1
            
            self.session.commit()
            print(f"  - 결제 {count}건 등록 완료")
            
        except Exception as e:
            print(f"  ! 결제 데이터 오류: {e}")
            import traceback
            traceback.print_exc()
            self.session.rollback()
    
    def migrate_all(self):
        """전체 마이그레이션"""
        try:
            self.load_service_types()
            self.migrate_customers()
            self.migrate_leads()
            self.migrate_payments()
            
            print("\n=== 마이그레이션 완료 ===")
            
            # 결과 확인
            result = self.session.execute(select(Customer))
            customer_count = len(result.scalars().all())
            
            result = self.session.execute(select(Payment))
            payment_count = len(result.scalars().all())
            
            result = self.session.execute(select(MarketingLead))
            lead_count = len(result.scalars().all())
            
            print(f"\n최종 데이터:")
            print(f"  - 고객: {customer_count}명")
            print(f"  - 결제: {payment_count}건")
            print(f"  - 리드: {lead_count}건")
            
        except Exception as e:
            print(f"마이그레이션 오류: {e}")
            self.session.rollback()
        finally:
            self.session.close()

def main():
    """메인 실행"""
    migrator = DataMigrator()
    
    # 기존 데이터 정리
    migrator.clean_all_data()
    
    # 실제 데이터 마이그레이션
    migrator.migrate_all()

if __name__ == "__main__":
    print("실제 엑셀 데이터를 마이그레이션합니다.")
    print("기존 샘플 데이터는 모두 삭제됩니다.")
    
    # Auto-run without confirmation for script execution
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == '--yes':
        main()
    else:
        response = input("\n계속하시겠습니까? (y/n): ")
        
        if response.lower() == 'y':
            main()
        else:
            print("취소되었습니다.")