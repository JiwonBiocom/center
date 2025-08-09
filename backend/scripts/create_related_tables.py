#!/usr/bin/env python3
"""
고객 관련 새로운 테이블 생성 스크립트
- customer_preferences: 고객 선호도 정보
- customer_analytics: 고객 분석 데이터
- marketing_leads: 마케팅 리드 (유입 고객)
- kit_receipts: 키트 수령 정보
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text, inspect
from sqlalchemy.exc import SQLAlchemyError
from core.database import engine
from datetime import datetime
import logging

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_related_tables():
    """고객 관련 새로운 테이블 생성"""
    
    with engine.begin() as conn:
        try:
            # 1. customer_preferences 테이블
            logger.info("\n=== customer_preferences 테이블 생성 ===")
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS customer_preferences (
                    preference_id SERIAL PRIMARY KEY,
                    customer_id INTEGER REFERENCES customers(customer_id) ON DELETE CASCADE,
                    preferred_services TEXT[],
                    preferred_time VARCHAR(20),
                    preferred_intensity VARCHAR(20),
                    health_interests TEXT[],
                    communication_preference VARCHAR(20),
                    marketing_consent BOOLEAN DEFAULT false,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(customer_id)
                )
            """))
            logger.info("✅ customer_preferences 테이블 생성 완료")
            
            # 인덱스 추가
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_preferences_customer 
                ON customer_preferences(customer_id)
            """))
            
            # 2. customer_analytics 테이블
            logger.info("\n=== customer_analytics 테이블 생성 ===")
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS customer_analytics (
                    analytics_id SERIAL PRIMARY KEY,
                    customer_id INTEGER REFERENCES customers(customer_id) ON DELETE CASCADE,
                    analysis_date DATE NOT NULL,
                    visit_frequency VARCHAR(20),
                    consistency_score INTEGER CHECK (consistency_score >= 0 AND consistency_score <= 100),
                    most_used_service VARCHAR(20),
                    ltv_estimate DECIMAL(10,2),
                    churn_risk VARCHAR(20),
                    churn_probability INTEGER CHECK (churn_probability >= 0 AND churn_probability <= 100),
                    retention_score INTEGER CHECK (retention_score >= 0 AND retention_score <= 100),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(customer_id, analysis_date)
                )
            """))
            logger.info("✅ customer_analytics 테이블 생성 완료")
            
            # 인덱스 추가
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_analytics_customer 
                ON customer_analytics(customer_id)
            """))
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_analytics_date 
                ON customer_analytics(analysis_date)
            """))
            
            # 3. marketing_leads 테이블 (기존 테이블 확장)
            logger.info("\n=== marketing_leads 테이블 확장 ===")
            
            # 기존 테이블에 새로운 컬럼 추가
            columns_to_add = [
                ("age", "INTEGER"),
                ("region", "VARCHAR(50)"),
                ("lead_channel", "VARCHAR(50)"),
                ("carrot_id", "VARCHAR(100)"),
                ("ad_watched", "VARCHAR(100)"),
                ("price_informed", "BOOLEAN DEFAULT false"),
                ("ab_test_group", "VARCHAR(20)"),
                ("purchased_product", "VARCHAR(200)"),
                ("no_registration_reason", "TEXT"),
                ("notes", "TEXT"),
                ("revenue", "DECIMAL(10,2)"),
                ("updated_at", "TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
            ]
            
            for column_name, column_type in columns_to_add:
                try:
                    conn.execute(text(f"""
                        ALTER TABLE marketing_leads 
                        ADD COLUMN IF NOT EXISTS {column_name} {column_type}
                    """))
                    logger.info(f"  ✅ {column_name} 컬럼 추가")
                except Exception as e:
                    logger.warning(f"  ℹ️  {column_name} 컬럼 추가 중 오류 (이미 존재할 수 있음): {str(e)}")
            
            # channel 컬럼을 lead_channel로 이름 변경 (필요한 경우)
            try:
                conn.execute(text("""
                    ALTER TABLE marketing_leads 
                    RENAME COLUMN channel TO lead_channel
                """))
                logger.info("  ✅ channel 컬럼을 lead_channel로 변경")
            except Exception:
                logger.info("  ℹ️  lead_channel 컬럼이 이미 존재하거나 channel 컬럼이 없습니다")
            
            logger.info("✅ marketing_leads 테이블 확장 완료")
            
            # 인덱스 추가
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_leads_phone 
                ON marketing_leads(phone)
            """))
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_leads_status 
                ON marketing_leads(status)
            """))
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_leads_channel 
                ON marketing_leads(lead_channel)
            """))
            
            # 4. kit_receipts 테이블
            logger.info("\n=== kit_receipts 테이블 생성 ===")
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS kit_receipts (
                    kit_id SERIAL PRIMARY KEY,
                    customer_id INTEGER REFERENCES customers(customer_id) ON DELETE CASCADE,
                    kit_type VARCHAR(100),
                    serial_number VARCHAR(100) UNIQUE,
                    receipt_date DATE,
                    result_received_date DATE,
                    result_delivered_date DATE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            logger.info("✅ kit_receipts 테이블 생성 완료")
            
            # 인덱스 추가
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_kits_customer 
                ON kit_receipts(customer_id)
            """))
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_kits_serial 
                ON kit_receipts(serial_number)
            """))
            
            # 5. 테이블 생성 확인
            logger.info("\n=== 생성된 테이블 확인 ===")
            inspector = inspect(engine)
            tables = inspector.get_table_names()
            
            new_tables = ['customer_preferences', 'customer_analytics', 'marketing_leads', 'kit_receipts']
            for table in new_tables:
                if table in tables:
                    # 테이블 정보 조회
                    result = conn.execute(text(f"""
                        SELECT COUNT(*) as column_count
                        FROM information_schema.columns
                        WHERE table_name = '{table}'
                    """))
                    column_count = result.scalar()
                    
                    result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
                    row_count = result.scalar()
                    
                    logger.info(f"  ✅ {table}: {column_count}개 컬럼, {row_count}개 레코드")
                else:
                    logger.error(f"  ❌ {table} 테이블이 생성되지 않았습니다")
            
            return True
            
        except SQLAlchemyError as e:
            logger.error(f"❌ 테이블 생성 중 오류 발생: {str(e)}")
            raise

def verify_foreign_keys():
    """외래 키 제약 조건 확인"""
    with engine.connect() as conn:
        logger.info("\n=== 외래 키 제약 조건 확인 ===")
        
        result = conn.execute(text("""
            SELECT
                tc.table_name,
                kcu.column_name,
                ccu.table_name AS foreign_table_name,
                ccu.column_name AS foreign_column_name
            FROM
                information_schema.table_constraints AS tc
                JOIN information_schema.key_column_usage AS kcu
                  ON tc.constraint_name = kcu.constraint_name
                  AND tc.table_schema = kcu.table_schema
                JOIN information_schema.constraint_column_usage AS ccu
                  ON ccu.constraint_name = tc.constraint_name
                  AND ccu.table_schema = tc.table_schema
            WHERE tc.constraint_type = 'FOREIGN KEY' 
                AND tc.table_name IN ('customer_preferences', 'customer_analytics', 'marketing_leads', 'kit_receipts')
        """))
        
        for row in result:
            logger.info(f"  ✅ {row[0]}.{row[1]} → {row[2]}.{row[3]}")
        
        return True

if __name__ == "__main__":
    try:
        logger.info("고객 관련 테이블 생성을 시작합니다...")
        logger.info(f"실행 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 테이블 생성
        if create_related_tables():
            # 외래 키 확인
            verify_foreign_keys()
            logger.info("\n🎉 모든 관련 테이블이 성공적으로 생성되었습니다!")
        else:
            logger.error("\n❌ 테이블 생성 실패")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"\n❌ 예상치 못한 오류: {str(e)}")
        sys.exit(1)