"""
marketing_leads 테이블 확장 스크립트
유입고객 관리 시스템 개편을 위한 새 컬럼 추가
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from core.database import engine
from datetime import datetime

def extend_marketing_leads_table():
    """marketing_leads 테이블에 새로운 컬럼 추가"""
    
    alterations = [
        # DB작성 채널 (기존 notes에서 추출)
        "ALTER TABLE marketing_leads ADD COLUMN IF NOT EXISTS db_channel VARCHAR(50)",
        
        # 상담 관련
        "ALTER TABLE marketing_leads ADD COLUMN IF NOT EXISTS phone_consult_result VARCHAR(100)",
        "ALTER TABLE marketing_leads ADD COLUMN IF NOT EXISTS remind_date DATE",
        "ALTER TABLE marketing_leads ADD COLUMN IF NOT EXISTS visit_cancelled BOOLEAN DEFAULT FALSE",
        "ALTER TABLE marketing_leads ADD COLUMN IF NOT EXISTS visit_cancel_reason TEXT",
        
        # 재등록 관련
        "ALTER TABLE marketing_leads ADD COLUMN IF NOT EXISTS is_reregistration_target BOOLEAN DEFAULT FALSE",
        "ALTER TABLE marketing_leads ADD COLUMN IF NOT EXISTS last_service_date DATE",
        "ALTER TABLE marketing_leads ADD COLUMN IF NOT EXISTS reregistration_proposal_date DATE",
        
        # 담당자
        "ALTER TABLE marketing_leads ADD COLUMN IF NOT EXISTS assigned_staff_id INTEGER REFERENCES users(user_id)",
        
        # 추가 인덱스
        "CREATE INDEX IF NOT EXISTS idx_leads_db_channel ON marketing_leads(db_channel)",
        "CREATE INDEX IF NOT EXISTS idx_leads_assigned_staff ON marketing_leads(assigned_staff_id)",
        "CREATE INDEX IF NOT EXISTS idx_leads_reregistration ON marketing_leads(is_reregistration_target)"
    ]
    
    with engine.connect() as conn:
        for alteration in alterations:
            try:
                conn.execute(text(alteration))
                conn.commit()
                print(f"✅ 실행 성공: {alteration[:60]}...")
            except Exception as e:
                print(f"❌ 실행 실패: {alteration[:60]}...")
                print(f"   오류: {str(e)}")

def create_consultation_history_table():
    """상담 이력 테이블 생성"""
    
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS lead_consultation_history (
        history_id SERIAL PRIMARY KEY,
        lead_id INTEGER REFERENCES marketing_leads(lead_id) ON DELETE CASCADE,
        consultation_type VARCHAR(20) NOT NULL CHECK (consultation_type IN ('phone', 'visit', 'message', 'other')),
        consultation_date TIMESTAMP NOT NULL,
        result VARCHAR(100),
        notes TEXT,
        next_action VARCHAR(100),
        created_by INTEGER REFERENCES users(user_id),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """
    
    # 인덱스는 별도로 생성
    create_indexes = [
        "CREATE INDEX IF NOT EXISTS idx_history_lead_id ON lead_consultation_history(lead_id)",
        "CREATE INDEX IF NOT EXISTS idx_history_date ON lead_consultation_history(consultation_date)"
    ]
    
    with engine.connect() as conn:
        try:
            conn.execute(text(create_table_sql))
            conn.commit()
            print("✅ 상담 이력 테이블 생성 완료")
            
            # 인덱스 생성
            for idx_sql in create_indexes:
                conn.execute(text(idx_sql))
                conn.commit()
            print("✅ 상담 이력 테이블 인덱스 생성 완료")
        except Exception as e:
            print(f"❌ 상담 이력 테이블 생성 실패: {str(e)}")

def create_reregistration_campaigns_table():
    """재등록 캠페인 테이블 생성"""
    
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS reregistration_campaigns (
        campaign_id SERIAL PRIMARY KEY,
        campaign_name VARCHAR(100) NOT NULL,
        start_date DATE NOT NULL,
        end_date DATE,
        target_criteria JSON,
        target_count INTEGER DEFAULT 0,
        success_count INTEGER DEFAULT 0,
        notes TEXT,
        is_active BOOLEAN DEFAULT TRUE,
        created_by INTEGER REFERENCES users(user_id),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """
    
    # 인덱스와 트리거는 별도로 생성
    create_indexes = [
        "CREATE INDEX IF NOT EXISTS idx_campaign_dates ON reregistration_campaigns(start_date, end_date)",
        "CREATE INDEX IF NOT EXISTS idx_campaign_active ON reregistration_campaigns(is_active)"
    ]
    
    with engine.connect() as conn:
        try:
            conn.execute(text(create_table_sql))
            conn.commit()
            print("✅ 재등록 캠페인 테이블 생성 완료")
            
            # 인덱스 생성
            for idx_sql in create_indexes:
                conn.execute(text(idx_sql))
                conn.commit()
            print("✅ 재등록 캠페인 테이블 인덱스 생성 완료")
        except Exception as e:
            print(f"❌ 재등록 캠페인 테이블 생성 실패: {str(e)}")

def create_campaign_targets_table():
    """캠페인 대상 고객 연결 테이블"""
    
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS campaign_targets (
        target_id SERIAL PRIMARY KEY,
        campaign_id INTEGER REFERENCES reregistration_campaigns(campaign_id) ON DELETE CASCADE,
        lead_id INTEGER REFERENCES marketing_leads(lead_id) ON DELETE CASCADE,
        contact_date DATE,
        contact_result VARCHAR(100),
        converted BOOLEAN DEFAULT FALSE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        
        UNIQUE(campaign_id, lead_id)
    )
    """
    
    # 인덱스는 별도로 생성
    create_indexes = [
        "CREATE INDEX IF NOT EXISTS idx_target_campaign ON campaign_targets(campaign_id)",
        "CREATE INDEX IF NOT EXISTS idx_target_lead ON campaign_targets(lead_id)"
    ]
    
    with engine.connect() as conn:
        try:
            conn.execute(text(create_table_sql))
            conn.commit()
            print("✅ 캠페인 대상 테이블 생성 완료")
            
            # 인덱스 생성
            for idx_sql in create_indexes:
                conn.execute(text(idx_sql))
                conn.commit()
            print("✅ 캠페인 대상 테이블 인덱스 생성 완료")
        except Exception as e:
            print(f"❌ 캠페인 대상 테이블 생성 실패: {str(e)}")

def main():
    print("=" * 60)
    print("유입고객 관리 시스템 - DB 스키마 확장")
    print("=" * 60)
    print(f"실행 시간: {datetime.now()}")
    print()
    
    print("1. marketing_leads 테이블 확장...")
    extend_marketing_leads_table()
    
    print("\n2. 상담 이력 테이블 생성...")
    create_consultation_history_table()
    
    print("\n3. 재등록 캠페인 테이블 생성...")
    create_reregistration_campaigns_table()
    
    print("\n4. 캠페인 대상 테이블 생성...")
    create_campaign_targets_table()
    
    print("\n✅ DB 스키마 확장 완료!")

if __name__ == "__main__":
    main()