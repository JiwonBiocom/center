#!/usr/bin/env python3
"""
정제된 엑셀 데이터를 데이터베이스로 마이그레이션
- 고객 정보 업데이트
- 유입 고객 정보 마이그레이션
- 키트 수령 정보 마이그레이션
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
from sqlalchemy import text
from sqlalchemy.orm import Session
from core.database import engine, SessionLocal
from datetime import datetime
import logging

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class CustomerDataMigration:
    """고객 데이터 마이그레이션 클래스"""
    
    def __init__(self):
        self.base_path = 'docs/AIBIO 관리대장 파일모음'
        self.session = SessionLocal()
        
    def __del__(self):
        if hasattr(self, 'session'):
            self.session.close()
    
    def get_or_create_customer(self, name: str, phone: str = None) -> int:
        """고객 찾기 또는 생성"""
        # 전화번호로 먼저 찾기
        if phone and pd.notna(phone) and phone != '':
            result = self.session.execute(
                text("SELECT customer_id FROM customers WHERE phone = :phone"),
                {"phone": phone}
            ).first()
            if result:
                return result[0]
        
        # 이름으로 찾기
        result = self.session.execute(
            text("SELECT customer_id FROM customers WHERE name = :name"),
            {"name": name}
        ).first()
        if result:
            return result[0]
        
        # 새로 생성
        result = self.session.execute(
            text("""
                INSERT INTO customers (name, phone, created_at, updated_at)
                VALUES (:name, :phone, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                RETURNING customer_id
            """),
            {"name": name, "phone": phone}
        )
        self.session.commit()
        return result.scalar()
    
    def migrate_customers(self):
        """고객 데이터 마이그레이션"""
        logger.info("=== 고객 데이터 마이그레이션 시작 ===")
        
        # 정제된 데이터 읽기
        df = pd.read_csv(f'{self.base_path}/고객관리대장_정제됨.csv')
        
        success_count = 0
        error_count = 0
        
        for _, row in df.iterrows():
            try:
                # 고객 ID 찾기
                customer_id = self.get_or_create_customer(
                    name=row['이름'],
                    phone=row.get('phone_clean')
                )
                
                # 업데이트할 데이터 준비
                update_data = {
                    'customer_id': customer_id,
                    'first_visit_date': row.get('first_visit_date'),
                    'region': row.get('거주지역'),
                    'referral_source': row.get('방문경로'),
                    'health_concerns': row.get('호소문제'),
                    'notes': row.get('비고'),
                    'assigned_staff': row.get('담당자'),
                    'birth_year': row.get('birth_year'),
                    'gender': row.get('gender')
                }
                
                # NULL 값 제거
                update_data = {k: v for k, v in update_data.items() 
                             if pd.notna(v) and v is not None}
                
                # 업데이트 쿼리 생성
                if len(update_data) > 1:  # customer_id 외에 업데이트할 데이터가 있는 경우
                    set_clause = ', '.join([f"{k} = :{k}" for k in update_data.keys() if k != 'customer_id'])
                    query = f"""
                        UPDATE customers 
                        SET {set_clause}, updated_at = CURRENT_TIMESTAMP
                        WHERE customer_id = :customer_id
                    """
                    
                    self.session.execute(text(query), update_data)
                
                success_count += 1
                
            except Exception as e:
                logger.error(f"고객 마이그레이션 오류 ({row['이름']}): {str(e)}")
                error_count += 1
                self.session.rollback()
        
        self.session.commit()
        logger.info(f"고객 마이그레이션 완료: 성공 {success_count}건, 실패 {error_count}건")
    
    def migrate_leads(self):
        """유입 고객 데이터 마이그레이션"""
        logger.info("\n=== 유입 고객 마이그레이션 시작 ===")
        
        # 정제된 데이터 읽기
        df = pd.read_csv(f'{self.base_path}/유입고객_정제됨.csv')
        
        success_count = 0
        error_count = 0
        
        for _, row in df.iterrows():
            try:
                # 전환된 고객 ID 찾기
                converted_customer_id = None
                if pd.notna(row.get('등록일_clean')):
                    converted_customer_id = self.get_or_create_customer(
                        name=row['이름'],
                        phone=row.get('phone_clean')
                    )
                
                # 유입 고객 데이터 준비
                lead_data = {
                    'name': row['이름'],
                    'phone': row.get('phone_clean'),
                    'age': row.get('나이'),
                    'region': row.get('거주지역'),
                    'lead_channel': row.get('유입경로'),
                    'carrot_id': row.get('당근아이디'),
                    'ad_watched': row.get('시청 광고'),
                    'price_informed': row.get('price_informed_clean', False),
                    'ab_test_group': row.get('A/B 테스트'),
                    'db_entry_date': row.get('DB입력일_clean'),
                    'phone_consult_date': row.get('전화상담일_clean'),
                    'visit_consult_date': row.get('방문상담일_clean'),
                    'registration_date': row.get('등록일_clean'),
                    'purchased_product': row.get('구매상품'),
                    'no_registration_reason': row.get('미등록사유'),
                    'notes': row.get('비고'),
                    'revenue': row.get('revenue_clean', 0),
                    'status': row.get('status_inferred', 'new'),
                    'converted_customer_id': converted_customer_id
                }
                
                # NULL 값 제거
                lead_data = {k: v for k, v in lead_data.items() 
                           if pd.notna(v) and v is not None}
                
                # 중복 확인 (이름 + 전화번호)
                existing = self.session.execute(
                    text("""
                        SELECT lead_id FROM marketing_leads 
                        WHERE name = :name AND 
                              (phone = :phone OR (phone IS NULL AND :phone IS NULL))
                    """),
                    {'name': lead_data['name'], 'phone': lead_data.get('phone')}
                ).first()
                
                if existing:
                    # 업데이트
                    lead_data['lead_id'] = existing[0]
                    set_clause = ', '.join([f"{k} = :{k}" for k in lead_data.keys() if k != 'lead_id'])
                    query = f"""
                        UPDATE marketing_leads 
                        SET {set_clause}, updated_at = CURRENT_TIMESTAMP
                        WHERE lead_id = :lead_id
                    """
                else:
                    # 새로 삽입
                    columns = ', '.join(lead_data.keys())
                    values = ', '.join([f":{k}" for k in lead_data.keys()])
                    query = f"""
                        INSERT INTO marketing_leads ({columns}, created_at, updated_at)
                        VALUES ({values}, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                    """
                
                self.session.execute(text(query), lead_data)
                success_count += 1
                
            except Exception as e:
                logger.error(f"유입 고객 마이그레이션 오류 ({row['이름']}): {str(e)}")
                error_count += 1
                self.session.rollback()
        
        self.session.commit()
        logger.info(f"유입 고객 마이그레이션 완료: 성공 {success_count}건, 실패 {error_count}건")
    
    def migrate_kits(self):
        """키트 수령 데이터 마이그레이션"""
        logger.info("\n=== 키트 수령 마이그레이션 시작 ===")
        
        # 정제된 데이터 읽기
        df = pd.read_csv(f'{self.base_path}/키트고객_정제됨.csv')
        
        success_count = 0
        error_count = 0
        
        for _, row in df.iterrows():
            try:
                # 고객 ID 찾기
                customer_id = self.get_or_create_customer(
                    name=row['고객명']
                )
                
                # 키트 데이터 준비
                kit_data = {
                    'customer_id': customer_id,
                    'kit_type': row.get('키트'),
                    'serial_number': row.get('serial_clean'),
                    'receipt_date': row.get('키트수령일_clean'),
                    'result_received_date': row.get('결과지 수령일_clean'),
                    'result_delivered_date': row.get('결과지 전달일_clean')
                }
                
                # NULL 값 제거
                kit_data = {k: v for k, v in kit_data.items() 
                           if pd.notna(v) and v is not None}
                
                # 중복 확인 (시리얼 번호)
                if 'serial_number' in kit_data:
                    existing = self.session.execute(
                        text("SELECT kit_id FROM kit_receipts WHERE serial_number = :serial"),
                        {'serial': kit_data['serial_number']}
                    ).first()
                    
                    if existing:
                        logger.warning(f"중복 시리얼 번호 건너뛰기: {kit_data['serial_number']}")
                        continue
                
                # 삽입
                columns = ', '.join(kit_data.keys())
                values = ', '.join([f":{k}" for k in kit_data.keys()])
                query = f"""
                    INSERT INTO kit_receipts ({columns}, created_at, updated_at)
                    VALUES ({values}, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                """
                
                self.session.execute(text(query), kit_data)
                success_count += 1
                
            except Exception as e:
                logger.error(f"키트 마이그레이션 오류 ({row['고객명']}): {str(e)}")
                error_count += 1
                self.session.rollback()
        
        self.session.commit()
        logger.info(f"키트 마이그레이션 완료: 성공 {success_count}건, 실패 {error_count}건")
    
    def update_customer_statistics(self):
        """고객 통계 정보 업데이트"""
        logger.info("\n=== 고객 통계 업데이트 시작 ===")
        
        # 서비스 이용 통계 업데이트
        self.session.execute(text("""
            UPDATE customers c
            SET 
                total_visits = COALESCE(stats.visit_count, 0),
                last_visit_date = stats.last_visit,
                total_revenue = COALESCE(stats.total_revenue, 0)
            FROM (
                SELECT 
                    su.customer_id,
                    COUNT(DISTINCT su.service_date) as visit_count,
                    MAX(su.service_date) as last_visit,
                    SUM(p.amount) as total_revenue
                FROM service_usage su
                LEFT JOIN payments p ON su.customer_id = p.customer_id
                GROUP BY su.customer_id
            ) stats
            WHERE c.customer_id = stats.customer_id
        """))
        
        # 리스크 레벨 업데이트 (3개월 이상 미방문 시 warning)
        self.session.execute(text("""
            UPDATE customers
            SET risk_level = CASE
                WHEN last_visit_date < CURRENT_DATE - INTERVAL '3 months' THEN 'warning'
                WHEN last_visit_date < CURRENT_DATE - INTERVAL '6 months' THEN 'danger'
                ELSE 'stable'
            END
            WHERE last_visit_date IS NOT NULL
        """))
        
        self.session.commit()
        logger.info("고객 통계 업데이트 완료")
    
    def verify_migration(self):
        """마이그레이션 결과 검증"""
        logger.info("\n=== 마이그레이션 결과 검증 ===")
        
        # 고객 수 확인
        result = self.session.execute(text("SELECT COUNT(*) FROM customers")).scalar()
        logger.info(f"전체 고객 수: {result}")
        
        # 확장 정보가 있는 고객 수
        result = self.session.execute(text("""
            SELECT 
                COUNT(CASE WHEN birth_year IS NOT NULL THEN 1 END) as with_birth_year,
                COUNT(CASE WHEN gender IS NOT NULL THEN 1 END) as with_gender,
                COUNT(CASE WHEN phone IS NOT NULL THEN 1 END) as with_phone
            FROM customers
        """)).first()
        logger.info(f"생년 정보: {result[0]}명, 성별 정보: {result[1]}명, 전화번호: {result[2]}명")
        
        # 유입 고객 수
        result = self.session.execute(text("SELECT COUNT(*) FROM marketing_leads")).scalar()
        logger.info(f"유입 고객 수: {result}")
        
        # 키트 수령 정보
        result = self.session.execute(text("SELECT COUNT(*) FROM kit_receipts")).scalar()
        logger.info(f"키트 수령 기록: {result}")

def main():
    """메인 실행 함수"""
    migration = CustomerDataMigration()
    
    try:
        # 1. 고객 데이터 마이그레이션
        migration.migrate_customers()
        
        # 2. 유입 고객 마이그레이션
        migration.migrate_leads()
        
        # 3. 키트 수령 마이그레이션
        migration.migrate_kits()
        
        # 4. 통계 업데이트
        migration.update_customer_statistics()
        
        # 5. 결과 검증
        migration.verify_migration()
        
        logger.info("\n✅ 모든 데이터 마이그레이션이 완료되었습니다!")
        
    except Exception as e:
        logger.error(f"마이그레이션 중 오류 발생: {str(e)}")
        raise

if __name__ == "__main__":
    main()