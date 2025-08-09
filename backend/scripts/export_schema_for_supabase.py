"""
Supabase로 스키마를 내보내는 스크립트
SQLAlchemy 모델을 기반으로 CREATE TABLE 문을 생성합니다.
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, MetaData
from sqlalchemy.schema import CreateTable
from sqlalchemy.dialects import postgresql
from core.database import Base

# 모든 모델 import (테이블 생성을 위해 필요)
from models.user import User
from models.customer import Customer
from models.service import ServiceUsage, ServiceType
from models.payment import Payment
from models.package import Package, PackagePurchase
from models.lead_management import LeadConsultationHistory, ReregistrationCampaign, CampaignTarget
from models.notification import Notification, NotificationSettings
from models.reservation import Reservation
from models.kit import KitType, KitManagement
from models.customer_extended import CustomerPreference, CustomerAnalytics, MarketingLead, KitReceipt
from models.staff_schedule import StaffSchedule
from models.inbody import InBodyRecord
from models.system import SystemSettings, CompanyInfo, NotificationPreferences
from models.audit import AuditLog
from models.questionnaire import QuestionnaireTemplate, Question, QuestionnaireResponse, Answer, QuestionnaireAnalysis

def export_schema():
    """스키마를 SQL 파일로 내보내기"""
    
    # PostgreSQL dialect 사용하여 올바른 SQL 생성
    engine = create_engine("postgresql://user:pass@localhost/db")
    
    # 출력 파일 경로
    output_file = os.path.join(os.path.dirname(__file__), "..", "supabase_schema.sql")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        # 헤더 작성
        f.write("-- AIBIO Center Management System Database Schema\n")
        f.write("-- Generated for Supabase (PostgreSQL)\n")
        f.write("-- Note: Supabase 대시보드의 SQL Editor에서 실행하세요\n\n")
        
        # 기본 설정
        f.write("-- Enable UUID extension (Supabase에서 기본 제공)\n")
        f.write("CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";\n\n")
        
        # 각 테이블에 대해 CREATE TABLE 문 생성
        for table in Base.metadata.sorted_tables:
            # PostgreSQL dialect로 컴파일
            create_stmt = str(CreateTable(table).compile(dialect=postgresql.dialect()))
            
            f.write(f"-- {table.name} 테이블\n")
            f.write(create_stmt)
            f.write(";\n\n")
        
        # 인덱스 생성
        f.write("-- 인덱스 생성\n")
        for table in Base.metadata.sorted_tables:
            for index in table.indexes:
                columns = ", ".join([col.name for col in index.columns])
                f.write(f"CREATE INDEX IF NOT EXISTS idx_{table.name}_{index.name} ON {table.name} ({columns});\n")
        
        f.write("\n")
        
        # 초기 데이터
        f.write("-- 초기 데이터 삽입\n")
        f.write("-- 관리자 계정 (비밀번호: admin123)\n")
        f.write("""
INSERT INTO users (email, password_hash, name, role, is_active, created_at) 
VALUES (
    'admin@aibio.kr',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewYpfQeUjrktJrIa',
    '관리자',
    'admin',
    true,
    NOW()
) ON CONFLICT (email) DO NOTHING;
""")
        
        f.write("\n-- 기본 서비스 타입\n")
        service_types = [
            ('상담', '#FF6B6B', 30, 50000),
            ('발가락케어', '#4ECDC4', 60, 80000),
            ('종아리케어', '#45B7D1', 60, 70000),
            ('뱃살케어', '#F8961E', 90, 120000),
            ('등케어', '#90BE6D', 60, 90000),
            ('DNA검사', '#C77DFF', 30, 150000),
            ('인바디측정', '#7209B7', 15, 20000)
        ]
        
        for name, color, duration, price in service_types:
            f.write(f"""
INSERT INTO service_types (service_name, service_color, default_duration, default_price, is_active, created_at)
VALUES ('{name}', '{color}', {duration}, {price}, true, NOW())
ON CONFLICT (service_name) DO NOTHING;
""")
        
        # Row Level Security 정책 (Supabase 특화)
        f.write("\n\n-- Row Level Security 정책 (선택사항)\n")
        f.write("-- Supabase 대시보드에서 RLS를 활성화하고 정책을 설정할 수 있습니다.\n")
        f.write("-- 예시:\n")
        f.write("-- ALTER TABLE customers ENABLE ROW LEVEL SECURITY;\n")
        f.write("-- CREATE POLICY \"Users can view all customers\" ON customers FOR SELECT USING (true);\n")
        
    print(f"✅ Supabase 스키마가 생성되었습니다: {output_file}")
    print("\n사용 방법:")
    print("1. Supabase 대시보드에 로그인")
    print("2. SQL Editor 열기")
    print("3. supabase_schema.sql 내용을 복사하여 붙여넣기")
    print("4. Run 버튼 클릭")
    print("\n주의: 기존 테이블이 있는 경우 DROP TABLE 문을 먼저 실행해야 할 수 있습니다.")

if __name__ == "__main__":
    export_schema()