"""
유입고객 관리 테이블에 추가 필드 생성
- 상담자 정보
- 체중 관련 정보
- 운동/식단 계획
- 체험 서비스 기록
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from core.database import SessionLocal
from datetime import datetime

def add_lead_enhancement_fields():
    db = SessionLocal()
    
    try:
        print("유입고객 관리 테이블에 추가 필드를 생성합니다...")
        
        # 1. marketing_leads 테이블에 컬럼 추가
        columns_to_add = [
            ("consultant_name", "VARCHAR(50)", "상담자 이름"),
            ("current_weight", "DECIMAL(5,2)", "현재 체중"),
            ("target_weight", "DECIMAL(5,2)", "목표 체중"),
            ("exercise_plan", "TEXT", "운동 계획"),
            ("diet_plan", "TEXT", "식단 계획"),
            ("experience_services", "TEXT", "체험 서비스"),
            ("experience_result", "TEXT", "체험 결과"),
            ("rejection_reason", "TEXT", "미등록 사유"),
            ("past_diet_experience", "TEXT", "과거 다이어트 경험"),
            ("main_concerns", "TEXT", "주요 관심사/니즈"),
            ("referral_detail", "TEXT", "유입 경로 상세"),
            ("visit_purpose", "TEXT", "방문 목적")
        ]
        
        for column_name, column_type, comment in columns_to_add:
            try:
                db.execute(text(f"""
                    ALTER TABLE marketing_leads 
                    ADD COLUMN IF NOT EXISTS {column_name} {column_type}
                """))
                print(f"✅ {column_name} 컬럼 추가 완료 ({comment})")
            except Exception as e:
                print(f"⚠️ {column_name} 컬럼 추가 중 오류 (이미 존재할 수 있음): {e}")
        
        # 2. 체험 서비스 기록 테이블 생성
        print("\n체험 서비스 기록 테이블을 생성합니다...")
        
        db.execute(text("""
            CREATE TABLE IF NOT EXISTS lead_experience_services (
                experience_id SERIAL PRIMARY KEY,
                lead_id INTEGER REFERENCES marketing_leads(lead_id) ON DELETE CASCADE,
                service_date DATE NOT NULL,
                service_types TEXT NOT NULL,
                before_weight DECIMAL(5,2),
                after_weight DECIMAL(5,2),
                before_muscle_mass DECIMAL(5,2),
                after_muscle_mass DECIMAL(5,2),
                before_body_fat DECIMAL(5,2),
                after_body_fat DECIMAL(5,2),
                phase_angle_change DECIMAL(3,2),
                result_summary TEXT,
                staff_name VARCHAR(50),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))
        print("✅ lead_experience_services 테이블 생성 완료")
        
        # 3. 상담 이력에 추가 필드
        print("\n상담 이력 테이블에 추가 필드를 생성합니다...")
        
        consultation_columns = [
            ("visit_purpose", "TEXT", "방문 목적"),
            ("main_needs", "TEXT", "주요 니즈"),
            ("current_condition", "TEXT", "현재 상태"),
            ("consultation_type", "VARCHAR(20)", "상담 유형 (초기/재상담/팔로우업)"),
            ("next_action", "TEXT", "다음 액션"),
            ("estimated_revenue", "DECIMAL(10,2)", "예상 매출")
        ]
        
        for column_name, column_type, comment in consultation_columns:
            try:
                db.execute(text(f"""
                    ALTER TABLE consultation_history 
                    ADD COLUMN IF NOT EXISTS {column_name} {column_type}
                """))
                print(f"✅ consultation_history.{column_name} 컬럼 추가 완료 ({comment})")
            except Exception as e:
                print(f"⚠️ consultation_history.{column_name} 컬럼 추가 중 오류: {e}")
        
        # 4. 인덱스 추가
        print("\n인덱스를 추가합니다...")
        
        indexes = [
            ("idx_marketing_leads_consultant", "marketing_leads(consultant_name)"),
            ("idx_marketing_leads_visit_purpose", "marketing_leads(visit_purpose)"),
            ("idx_lead_experience_lead_id", "lead_experience_services(lead_id)"),
            ("idx_lead_experience_date", "lead_experience_services(service_date)")
        ]
        
        for index_name, index_def in indexes:
            try:
                db.execute(text(f"CREATE INDEX IF NOT EXISTS {index_name} ON {index_def}"))
                print(f"✅ {index_name} 인덱스 생성 완료")
            except Exception as e:
                print(f"⚠️ {index_name} 인덱스 생성 중 오류: {e}")
        
        db.commit()
        print("\n✨ 유입고객 관리 기능 강화 완료!")
        
    except Exception as e:
        db.rollback()
        print(f"\n❌ 오류 발생: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    add_lead_enhancement_fields()