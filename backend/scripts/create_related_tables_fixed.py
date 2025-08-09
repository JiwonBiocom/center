#!/usr/bin/env python3
"""
고객 관련 새로운 테이블 생성 스크립트 (수정 버전)
- 각 테이블을 개별 트랜잭션으로 처리
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

def create_customer_preferences():
    """customer_preferences 테이블 생성"""
    with engine.begin() as conn:
        try:
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
            
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_preferences_customer 
                ON customer_preferences(customer_id)
            """))
            
            logger.info("✅ customer_preferences 테이블 생성 완료")
            return True
        except Exception as e:
            logger.error(f"❌ customer_preferences 생성 실패: {str(e)}")
            return False

def create_customer_analytics():
    """customer_analytics 테이블 생성"""
    with engine.begin() as conn:
        try:
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
            
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_analytics_customer 
                ON customer_analytics(customer_id)
            """))
            
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_analytics_date 
                ON customer_analytics(analysis_date)
            """))
            
            logger.info("✅ customer_analytics 테이블 생성 완료")
            return True
        except Exception as e:
            logger.error(f"❌ customer_analytics 생성 실패: {str(e)}")
            return False

def extend_marketing_leads():
    """marketing_leads 테이블 확장"""
    with engine.begin() as conn:
        try:
            # 컬럼 이름 변경 (channel -> lead_channel)
            inspector = inspect(engine)
            columns = [col['name'] for col in inspector.get_columns('marketing_leads')]
            
            if 'channel' in columns and 'lead_channel' not in columns:
                conn.execute(text("ALTER TABLE marketing_leads RENAME COLUMN channel TO lead_channel"))
                logger.info("  ✅ channel을 lead_channel로 변경")
            
            # 새로운 컬럼 추가
            columns_to_add = [
                ("age", "INTEGER"),
                ("region", "VARCHAR(50)"),
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
            
            current_columns = [col['name'] for col in inspector.get_columns('marketing_leads')]
            
            for column_name, column_type in columns_to_add:
                if column_name not in current_columns:
                    conn.execute(text(f"""
                        ALTER TABLE marketing_leads 
                        ADD COLUMN {column_name} {column_type}
                    """))
                    logger.info(f"  ✅ {column_name} 컬럼 추가")
            
            # 인덱스 추가
            existing_indexes = [idx['name'] for idx in inspector.get_indexes('marketing_leads')]
            
            if 'idx_leads_phone' not in existing_indexes:
                conn.execute(text("CREATE INDEX idx_leads_phone ON marketing_leads(phone)"))
            
            if 'idx_leads_status' not in existing_indexes:
                conn.execute(text("CREATE INDEX idx_leads_status ON marketing_leads(status)"))
            
            if 'idx_leads_channel' not in existing_indexes:
                conn.execute(text("CREATE INDEX idx_leads_channel ON marketing_leads(lead_channel)"))
            
            logger.info("✅ marketing_leads 테이블 확장 완료")
            return True
        except Exception as e:
            logger.error(f"❌ marketing_leads 확장 실패: {str(e)}")
            return False

def create_kit_receipts():
    """kit_receipts 테이블 생성"""
    with engine.begin() as conn:
        try:
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
            
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_kits_customer 
                ON kit_receipts(customer_id)
            """))
            
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_kits_serial 
                ON kit_receipts(serial_number)
            """))
            
            logger.info("✅ kit_receipts 테이블 생성 완료")
            return True
        except Exception as e:
            logger.error(f"❌ kit_receipts 생성 실패: {str(e)}")
            return False

def verify_tables():
    """생성된 테이블 확인"""
    with engine.connect() as conn:
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        logger.info("\n=== 테이블 상태 확인 ===")
        
        required_tables = ['customer_preferences', 'customer_analytics', 'marketing_leads', 'kit_receipts']
        
        for table in required_tables:
            if table in tables:
                result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
                count = result.scalar()
                
                columns = inspector.get_columns(table)
                logger.info(f"✅ {table}: {len(columns)}개 컬럼, {count}개 레코드")
            else:
                logger.error(f"❌ {table} 테이블이 없습니다")

if __name__ == "__main__":
    try:
        logger.info("고객 관련 테이블 생성을 시작합니다...")
        logger.info(f"실행 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 각 테이블을 개별적으로 생성
        results = []
        
        logger.info("\n1. customer_preferences 테이블 생성")
        results.append(create_customer_preferences())
        
        logger.info("\n2. customer_analytics 테이블 생성")
        results.append(create_customer_analytics())
        
        logger.info("\n3. marketing_leads 테이블 확장")
        results.append(extend_marketing_leads())
        
        logger.info("\n4. kit_receipts 테이블 생성")
        results.append(create_kit_receipts())
        
        # 결과 확인
        if all(results):
            verify_tables()
            logger.info("\n🎉 모든 테이블이 성공적으로 생성/확장되었습니다!")
        else:
            logger.error("\n⚠️  일부 테이블 생성/확장에 실패했습니다")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"\n❌ 예상치 못한 오류: {str(e)}")
        sys.exit(1)