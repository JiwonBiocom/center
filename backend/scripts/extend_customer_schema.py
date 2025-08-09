#!/usr/bin/env python3
"""
고객 테이블 스키마 확장 스크립트
- 기존 데이터를 유지하면서 새로운 컬럼 추가
- 안전한 마이그레이션을 위한 트랜잭션 처리
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

def check_column_exists(inspector, table_name, column_name):
    """컬럼 존재 여부 확인"""
    columns = [col['name'] for col in inspector.get_columns(table_name)]
    return column_name in columns

def extend_customer_schema():
    """customers 테이블에 새로운 컬럼 추가"""
    
    # 추가할 컬럼 정의
    columns_to_add = [
        ("birth_year", "INTEGER"),
        ("gender", "VARCHAR(10)"),
        ("email", "VARCHAR(100)"),
        ("address", "TEXT"),
        ("emergency_contact", "VARCHAR(100)"),
        ("occupation", "VARCHAR(50)"),
        ("membership_level", "VARCHAR(20) DEFAULT 'basic'"),
        ("customer_status", "VARCHAR(20) DEFAULT 'active'"),
        ("preferred_time_slots", "JSONB"),
        ("health_goals", "TEXT"),
        ("last_visit_date", "DATE"),
        ("total_visits", "INTEGER DEFAULT 0"),
        ("average_visit_interval", "INTEGER"),
        ("total_revenue", "DECIMAL(10,2) DEFAULT 0"),
        ("average_satisfaction", "DECIMAL(3,2)"),
        ("risk_level", "VARCHAR(20) DEFAULT 'stable'")
    ]
    
    # 인덱스 정의
    indexes_to_add = [
        ("idx_customers_phone", "phone"),
        ("idx_customers_membership_level", "membership_level"),
        ("idx_customers_last_visit", "last_visit_date"),
        ("idx_customers_risk_level", "risk_level")
    ]
    
    with engine.begin() as conn:
        inspector = inspect(engine)
        
        # customers 테이블 존재 확인
        if 'customers' not in inspector.get_table_names():
            logger.error("customers 테이블이 존재하지 않습니다.")
            return False
        
        try:
            # 1. 컬럼 추가
            logger.info("=== customers 테이블 컬럼 추가 시작 ===")
            
            for column_name, column_type in columns_to_add:
                if not check_column_exists(inspector, 'customers', column_name):
                    query = f"ALTER TABLE customers ADD COLUMN IF NOT EXISTS {column_name} {column_type}"
                    conn.execute(text(query))
                    logger.info(f"✅ {column_name} 컬럼 추가 완료")
                else:
                    logger.info(f"ℹ️  {column_name} 컬럼은 이미 존재합니다")
            
            # 2. 인덱스 추가
            logger.info("\n=== 인덱스 추가 시작 ===")
            
            # 기존 인덱스 목록 조회
            existing_indexes = [idx['name'] for idx in inspector.get_indexes('customers')]
            
            for index_name, column_name in indexes_to_add:
                if index_name not in existing_indexes:
                    query = f"CREATE INDEX IF NOT EXISTS {index_name} ON customers({column_name})"
                    conn.execute(text(query))
                    logger.info(f"✅ {index_name} 인덱스 추가 완료")
                else:
                    logger.info(f"ℹ️  {index_name} 인덱스는 이미 존재합니다")
            
            # 3. 통계 업데이트
            logger.info("\n=== 테이블 통계 업데이트 ===")
            conn.execute(text("ANALYZE customers"))
            logger.info("✅ customers 테이블 통계 업데이트 완료")
            
            # 4. 확장된 테이블 정보 확인
            logger.info("\n=== 확장된 테이블 구조 ===")
            result = conn.execute(text("""
                SELECT 
                    column_name, 
                    data_type, 
                    is_nullable,
                    column_default
                FROM information_schema.columns 
                WHERE table_name = 'customers'
                ORDER BY ordinal_position
            """))
            
            for row in result:
                logger.info(f"  - {row[0]}: {row[1]} (nullable: {row[2]}, default: {row[3]})")
            
            # 5. 데이터 건수 확인
            result = conn.execute(text("SELECT COUNT(*) FROM customers"))
            count = result.scalar()
            logger.info(f"\n✅ 스키마 확장 완료! 현재 고객 수: {count}명")
            
            return True
            
        except SQLAlchemyError as e:
            logger.error(f"❌ 스키마 확장 중 오류 발생: {str(e)}")
            raise

def verify_schema():
    """스키마 확장 검증"""
    with engine.connect() as conn:
        # 필수 컬럼 확인
        required_columns = [
            'birth_year', 'gender', 'email', 'membership_level', 
            'customer_status', 'last_visit_date', 'total_visits', 
            'total_revenue', 'risk_level'
        ]
        
        inspector = inspect(engine)
        existing_columns = [col['name'] for col in inspector.get_columns('customers')]
        
        missing_columns = [col for col in required_columns if col not in existing_columns]
        
        if missing_columns:
            logger.error(f"❌ 누락된 컬럼: {missing_columns}")
            return False
        
        logger.info("✅ 모든 필수 컬럼이 존재합니다")
        return True

if __name__ == "__main__":
    try:
        logger.info("고객 테이블 스키마 확장을 시작합니다...")
        logger.info(f"실행 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 스키마 확장 실행
        if extend_customer_schema():
            # 검증
            if verify_schema():
                logger.info("\n🎉 고객 테이블 스키마 확장이 성공적으로 완료되었습니다!")
            else:
                logger.error("\n❌ 스키마 검증 실패")
                sys.exit(1)
        else:
            logger.error("\n❌ 스키마 확장 실패")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"\n❌ 예상치 못한 오류: {str(e)}")
        sys.exit(1)