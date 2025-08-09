"""
risk_level 필드 제거 스크립트
"""
import os
import sys
from datetime import datetime
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

load_dotenv()

def remove_risk_level():
    """customers 테이블에서 risk_level 컬럼 제거"""
    
    # 데이터베이스 연결
    engine = create_engine(os.getenv("DATABASE_URL"))
    
    try:
        with engine.begin() as conn:
            # 1. 백업을 위한 현재 데이터 확인
            result = conn.execute(text("""
                SELECT COUNT(*) as total,
                       COUNT(CASE WHEN risk_level = 'stable' THEN 1 END) as stable,
                       COUNT(CASE WHEN risk_level = 'at_risk' THEN 1 END) as at_risk,
                       COUNT(CASE WHEN risk_level = 'high_risk' THEN 1 END) as high_risk
                FROM customers
            """))
            
            stats = result.fetchone()
            logger.info(f"현재 위험 수준 통계:")
            logger.info(f"  - 전체: {stats.total}명")
            logger.info(f"  - stable: {stats.stable}명")
            logger.info(f"  - at_risk: {stats.at_risk}명")
            logger.info(f"  - high_risk: {stats.high_risk}명")
            
            # 2. 컬럼 존재 확인
            check_column = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'customers' 
                AND column_name = 'risk_level'
            """))
            
            if not check_column.fetchone():
                logger.info("risk_level 컬럼이 이미 존재하지 않습니다.")
                return
            
            # 3. 컬럼 제거
            logger.info("risk_level 컬럼을 제거합니다...")
            conn.execute(text("ALTER TABLE customers DROP COLUMN risk_level"))
            logger.info("risk_level 컬럼이 성공적으로 제거되었습니다.")
            
            # 4. system_settings 테이블 확인 (존재하는 경우에만 업데이트)
            check_table = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_name = 'system_settings'
            """))
            
            if check_table.fetchone():
                # 컬럼 이름 확인
                check_columns = conn.execute(text("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = 'system_settings'
                """))
                columns = [row[0] for row in check_columns]
                logger.info(f"system_settings 테이블 컬럼: {columns}")
                
                # 적절한 컬럼 이름 사용
                if 'key' in columns:
                    conn.execute(text("""
                        UPDATE system_settings 
                        SET value = value::jsonb - 'risk_level'
                        WHERE key = 'membership_settings'
                        AND value::jsonb ? 'risk_level'
                    """))
                elif 'setting_key' in columns:
                    conn.execute(text("""
                        UPDATE system_settings 
                        SET setting_value = setting_value::jsonb - 'risk_level'
                        WHERE setting_key = 'membership_settings'
                        AND setting_value::jsonb ? 'risk_level'
                    """))
                    
                logger.info("시스템 설정에서 risk_level 관련 데이터를 제거했습니다.")
            else:
                logger.info("system_settings 테이블이 존재하지 않습니다.")
            
    except Exception as e:
        logger.error(f"오류 발생: {str(e)}")
        raise
    
    logger.info("risk_level 제거 작업이 완료되었습니다.")

if __name__ == "__main__":
    remove_risk_level()