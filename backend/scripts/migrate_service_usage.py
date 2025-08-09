#!/usr/bin/env python3
"""
서비스 이용 내역 마이그레이션
2025년 5월 데이터를 service_usage 테이블로 마이그레이션
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
from sqlalchemy import text
from sqlalchemy.orm import Session
from core.database import SessionLocal
from datetime import datetime
import re
import logging

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ServiceUsageMigration:
    def __init__(self):
        self.session = SessionLocal()
        
    def __del__(self):
        if hasattr(self, 'session'):
            self.session.close()
    
    def get_customer_id(self, name: str) -> int:
        """고객 ID 조회"""
        result = self.session.execute(
            text("SELECT customer_id FROM customers WHERE name = :name"),
            {"name": name}
        ).first()
        
        if result:
            return result[0]
        return None
    
    def get_service_type_id(self, service_name: str) -> int:
        """서비스 타입 ID 조회"""
        # 서비스명 매핑
        service_map = {
            '브레인': 1,
            '펄스': 2, 
            '림프': 3,
            '레드': 4,
            'AI바이크': 5,
            'ai바이크': 5
        }
        
        for key, value in service_map.items():
            if key in service_name:
                return value
        
        return None
    
    def parse_service_sessions(self, package_str: str, session_str: str):
        """실행패키지와 세션진행사항을 파싱하여 서비스별로 분리"""
        if pd.isna(package_str) or pd.isna(session_str):
            return []
        
        services = []
        
        # 실행패키지에서 서비스 타입 추출
        package_lines = str(package_str).strip().split('\n')
        session_lines = str(session_str).strip().split('\n')
        
        # 각 서비스별로 매칭
        service_types = []
        for line in package_lines:
            if '브레인' in line:
                service_types.append(('브레인', 1))
            elif '펄스' in line:
                service_types.append(('펄스', 2))
            elif '림프' in line:
                service_types.append(('림프', 3))
            elif '레드' in line:
                service_types.append(('레드', 4))
            elif 'AI바이크' in line or 'ai바이크' in line:
                service_types.append(('AI바이크', 5))
        
        # 세션 정보와 매칭
        for i, (service_name, service_type_id) in enumerate(service_types):
            session_detail = session_lines[i] if i < len(session_lines) else ''
            
            # 시간 추출 (예: (20'), (30'))
            time_match = re.search(r'\((\d+)\'?\)', session_detail)
            duration = int(time_match.group(1)) if time_match else 20  # 기본 20분
            
            # 회차 정보 추출 (예: 1/11, 2/11)
            session_match = re.search(r'(\d+)/(\d+)', line)
            session_num = int(session_match.group(1)) if session_match else None
            
            services.append({
                'service_type_id': service_type_id,
                'service_name': service_name,
                'duration': duration,
                'session_number': session_num,
                'session_detail': session_detail
            })
        
        return services
    
    def migrate_may_2025(self):
        """2025년 5월 서비스 이용 내역 마이그레이션"""
        logger.info("=== 2025년 5월 서비스 이용 내역 마이그레이션 시작 ===")
        
        # CSV 파일 읽기
        csv_path = '/Users/vibetj/coding/center/docs/AIBIO 관리대장 파일모음/2025년5월_서비스이용내역.csv'
        df = pd.read_csv(csv_path)
        
        success_count = 0
        error_count = 0
        
        for _, row in df.iterrows():
            try:
                # 고객 ID 조회
                customer_id = self.get_customer_id(row['성함'])
                if not customer_id:
                    logger.warning(f"고객을 찾을 수 없음: {row['성함']}")
                    continue
                
                # 서비스 세션 파싱
                services = self.parse_service_sessions(row['실행패키지'], row['세션진행사항'])
                
                if not services:
                    continue
                
                # 각 서비스별로 기록 생성
                for service in services:
                    # 중복 확인
                    existing = self.session.execute(
                        text("""
                            SELECT usage_id FROM service_usage 
                            WHERE customer_id = :customer_id 
                            AND service_date = CAST(:service_date AS date)
                            AND service_type_id = :service_type_id
                            LIMIT 1
                        """),
                        {
                            'customer_id': customer_id,
                            'service_date': row['날짜'],
                            'service_type_id': service['service_type_id']
                        }
                    ).first()
                    
                    if existing:
                        logger.info(f"이미 존재하는 기록 건너뛰기: {row['성함']} - {service['service_name']}")
                        continue
                    
                    # 서비스 이용 기록 추가
                    self.session.execute(
                        text("""
                            INSERT INTO service_usage (
                                customer_id,
                                service_type_id,
                                service_date,
                                session_number,
                                session_details,
                                created_at,
                                created_by
                            ) VALUES (
                                :customer_id,
                                :service_type_id,
                                CAST(:service_date AS date),
                                :session_number,
                                :session_details,
                                CURRENT_TIMESTAMP,
                                '1'
                            )
                        """),
                        {
                            'customer_id': customer_id,
                            'service_type_id': service['service_type_id'],
                            'service_date': row['날짜'],
                            'session_number': service['session_number'],
                            'session_details': service['session_detail']
                        }
                    )
                    
                    success_count += 1
                    logger.info(f"추가: {row['성함']} - {service['service_name']} ({row['날짜']})")
                
            except Exception as e:
                logger.error(f"마이그레이션 오류 ({row['성함']}): {str(e)}")
                error_count += 1
                self.session.rollback()
                continue
        
        self.session.commit()
        logger.info(f"마이그레이션 완료: 성공 {success_count}건, 실패 {error_count}건")
    
    def verify_migration(self):
        """마이그레이션 결과 검증"""
        logger.info("\n=== 마이그레이션 결과 검증 ===")
        
        # 전체 서비스 이용 기록 수
        result = self.session.execute(
            text("SELECT COUNT(*) FROM service_usage")
        ).scalar()
        logger.info(f"전체 서비스 이용 기록: {result}건")
        
        # 최미라 고객 서비스 이용 내역
        result = self.session.execute(
            text("""
                SELECT 
                    c.name,
                    su.service_date,
                    st.service_type_id,
                    st.service_name,
                    su.session_details
                FROM service_usage su
                JOIN customers c ON su.customer_id = c.customer_id
                JOIN service_types st ON su.service_type_id = st.service_type_id
                WHERE c.name = '최미라'
                ORDER BY su.service_date
            """)
        ).fetchall()
        
        logger.info(f"\n최미라 고객 서비스 이용 내역:")
        for row in result:
            logger.info(f"  {row[1]} - {row[3]}: {row[4]}")

def main():
    migration = ServiceUsageMigration()
    
    try:
        # 1. 2025년 5월 데이터 마이그레이션
        migration.migrate_may_2025()
        
        # 2. 결과 검증
        migration.verify_migration()
        
        logger.info("\n✅ 서비스 이용 내역 마이그레이션이 완료되었습니다!")
        
    except Exception as e:
        logger.error(f"마이그레이션 중 오류 발생: {str(e)}")
        raise

if __name__ == "__main__":
    main()