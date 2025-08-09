#!/usr/bin/env python3
"""
안전한 실제 데이터 마이그레이션 (기존 데이터 유지)
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
from models.service import ServiceUsage, ServiceType
from models.package import Package, PackagePurchase
from core.config import settings

# 엑셀 파일 경로
EXCEL_DIR = "/Users/vibetj/coding/center/docs/AIBIO 관리대장 파일모음"

# Supabase 연결
DATABASE_URL = "postgresql://postgres.wvcxzyvmwwrbjpeuyvuh:bico6819!!@aws-0-ap-northeast-2.pooler.supabase.com:6543/postgres"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class SafeDataMigrator:
    def __init__(self):
        self.session = SessionLocal()
        self.customer_map = {}
        self.service_type_map = {}
        
    def clean_phone(self, phone):
        """전화번호 정제"""
        if pd.isna(phone) or not phone:
            return None
        
        phone_str = str(phone).replace('-', '').replace(' ', '')
        if not phone_str.isdigit():
            return None
        
        if len(phone_str) == 10 and phone_str.startswith('10'):
            phone_str = '0' + phone_str
        elif len(phone_str) == 11 and phone_str.startswith('010'):
            pass
        else:
            return None
            
        return f"{phone_str[:3]}-{phone_str[3:7]}-{phone_str[7:]}"
    
    def load_customers_excel(self):
        """실제 고객 데이터 로드"""
        try:
            file_path = f"{EXCEL_DIR}/고객리스트.xlsx"
            if not os.path.exists(file_path):
                print(f"파일을 찾을 수 없습니다: {file_path}")
                return pd.DataFrame()
            
            df = pd.read_excel(file_path)
            print(f"✅ 고객 데이터 로드: {len(df)}건")
            return df
        except Exception as e:
            print(f"❌ 고객 데이터 로드 실패: {e}")
            return pd.DataFrame()
    
    def migrate_customers(self, df):
        """고객 데이터 마이그레이션"""
        success_count = 0
        
        for _, row in df.iterrows():
            try:
                # 필수 필드 확인
                name = row.get('이름') or row.get('고객명')
                if pd.isna(name):
                    continue
                
                phone = self.clean_phone(row.get('전화번호') or row.get('핸드폰'))
                if not phone:
                    continue
                
                # 중복 확인
                existing = self.session.query(Customer).filter(Customer.phone == phone).first()
                if existing:
                    continue
                
                # 고객 생성
                customer = Customer(
                    name=str(name).strip(),
                    phone=phone,
                    email=str(row.get('이메일', '')).strip() or None,
                    birth_date=self.parse_date(row.get('생년월일')),
                    gender=self.parse_gender(row.get('성별')),
                    address=str(row.get('주소', '')).strip() or None,
                    emergency_contact=str(row.get('비상연락처', '')).strip() or None,
                    emergency_phone=self.clean_phone(row.get('비상연락처전화')),
                    status='active',
                    membership_level='bronze',
                    notes=str(row.get('메모', '')).strip() or None,
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )
                
                self.session.add(customer)
                self.session.flush()
                
                self.customer_map[name] = customer.customer_id
                success_count += 1
                
            except Exception as e:
                print(f"고객 추가 실패 ({name}): {e}")
                continue
        
        try:
            self.session.commit()
            print(f"✅ 고객 데이터 마이그레이션 완료: {success_count}명")
        except Exception as e:
            self.session.rollback()
            print(f"❌ 고객 데이터 커밋 실패: {e}")
    
    def parse_date(self, date_str):
        """날짜 파싱"""
        if pd.isna(date_str):
            return None
        
        try:
            if isinstance(date_str, datetime):
                return date_str.date()
            elif isinstance(date_str, date):
                return date_str
            
            date_str = str(date_str).strip()
            if not date_str:
                return None
            
            # 다양한 날짜 형식 시도
            for fmt in ['%Y-%m-%d', '%Y/%m/%d', '%Y.%m.%d']:
                try:
                    return datetime.strptime(date_str, fmt).date()
                except ValueError:
                    continue
            
            return None
        except:
            return None
    
    def parse_gender(self, gender_str):
        """성별 파싱"""
        if pd.isna(gender_str):
            return None
        
        gender_str = str(gender_str).strip().lower()
        if gender_str in ['남', 'male', 'm', '남성']:
            return 'male'
        elif gender_str in ['여', 'female', 'f', '여성']:
            return 'female'
        return None
    
    def create_sample_service_types(self):
        """기본 서비스 타입 생성"""
        service_types = [
            ('InBody 측정', 'InBody 체성분 분석', 10000, 30, 'measurement'),
            ('개인 운동', '1:1 개인 트레이닝', 50000, 60, 'training'),
            ('그룹 운동', '소그룹 운동 클래스', 30000, 60, 'training'),
            ('영양 상담', '영양사 상담', 20000, 30, 'consultation'),
        ]
        
        for name, desc, price, duration, category in service_types:
            existing = self.session.query(ServiceType).filter(ServiceType.service_name == name).first()
            if not existing:
                service_type = ServiceType(
                    service_name=name,
                    description=desc,
                    default_price=price,
                    default_duration=duration
                )
                self.session.add(service_type)
        
        try:
            self.session.commit()
            print("✅ 기본 서비스 타입 생성 완료")
        except Exception as e:
            self.session.rollback()
            print(f"❌ 서비스 타입 생성 실패: {e}")

def main():
    print("=== 안전한 실제 데이터 마이그레이션 ===")
    print("기존 데이터는 유지하면서 새 데이터를 추가합니다.")
    
    migrator = SafeDataMigrator()
    
    # 기본 서비스 타입 생성
    migrator.create_sample_service_types()
    
    # 고객 데이터 마이그레이션
    df = migrator.load_customers_excel()
    if not df.empty:
        migrator.migrate_customers(df)
    else:
        print("⚠️  고객 데이터 파일이 없거나 비어있습니다.")
        print("임시로 샘플 데이터를 생성합니다...")
        
        # 샘플 데이터 생성
        sample_customers = [
            ('김철수', '010-1234-5678', 'kim@example.com'),
            ('박미영', '010-2345-6789', 'park@example.com'),
            ('이준호', '010-3456-7890', 'lee@example.com'),
            ('최유진', '010-4567-8901', 'choi@example.com'),
            ('정민수', '010-5678-9012', 'jung@example.com'),
        ]
        
        for name, phone, email in sample_customers:
            existing = migrator.session.query(Customer).filter(Customer.phone == phone).first()
            if not existing:
                customer = Customer(
                    name=name,
                    phone=phone,
                    email=email,
                    status='active',
                    membership_level='bronze',
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )
                migrator.session.add(customer)
        
        try:
            migrator.session.commit()
            print("✅ 샘플 고객 데이터 생성 완료")
        except Exception as e:
            migrator.session.rollback()
            print(f"❌ 샘플 데이터 생성 실패: {e}")
    
    # 결과 확인
    total_customers = migrator.session.query(Customer).count()
    print(f"\n📊 마이그레이션 완료!")
    print(f"총 고객 수: {total_customers}명")
    
    migrator.session.close()

if __name__ == "__main__":
    main()