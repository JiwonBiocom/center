"""
회원 등급 시스템 업데이트 스크립트
- membership_level enum을 4단계로 확장
- system_settings에 등급 기준 설정 추가
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from core.database import SessionLocal
from datetime import datetime
import json

def update_membership_system():
    db = SessionLocal()
    
    try:
        # 1. membership_level 타입 업데이트 (PostgreSQL)
        print("1. Updating membership_level enum type...")
        
        # 기존 enum 타입 확인
        result = db.execute(text("""
            SELECT EXISTS (
                SELECT 1 FROM pg_type WHERE typname = 'membership_level_enum'
            );
        """))
        
        if result.scalar():
            # 기존 enum 타입이 있으면 업데이트
            db.execute(text("ALTER TYPE membership_level_enum ADD VALUE IF NOT EXISTS 'bronze';"))
            db.execute(text("ALTER TYPE membership_level_enum ADD VALUE IF NOT EXISTS 'silver';"))
            db.execute(text("ALTER TYPE membership_level_enum ADD VALUE IF NOT EXISTS 'gold';"))
            db.execute(text("ALTER TYPE membership_level_enum ADD VALUE IF NOT EXISTS 'platinum';"))
        
        # 2. customers 테이블의 membership_level 컬럼 업데이트
        print("2. Updating customers table...")
        
        # 기존 'basic', 'premium', 'vip'를 새로운 체계로 매핑
        db.execute(text("""
            UPDATE customers 
            SET membership_level = 'bronze' 
            WHERE membership_level = 'basic';
        """))
        
        db.execute(text("""
            UPDATE customers 
            SET membership_level = 'silver' 
            WHERE membership_level = 'premium';
        """))
        
        db.execute(text("""
            UPDATE customers 
            SET membership_level = 'gold' 
            WHERE membership_level = 'vip';
        """))
        
        # 3. risk_level 컬럼 추가 (없는 경우)
        print("3. Adding risk_level column if not exists...")
        db.execute(text("""
            DO $$ 
            BEGIN
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='customers' AND column_name='risk_level'
                ) THEN
                    ALTER TABLE customers 
                    ADD COLUMN risk_level VARCHAR(20) DEFAULT 'stable';
                END IF;
            END $$;
        """))
        
        # 4. system_settings에 회원 등급 기준 추가
        print("4. Adding membership criteria to system_settings...")
        
        membership_criteria = {
            "bronze": {
                "name": "브론즈",
                "annual_revenue_min": 0,
                "annual_revenue_max": 5000000,
                "total_visits_min": 0,
                "total_visits_max": 10,
                "benefits": {
                    "discount_rate": 0,
                    "description": "기본 서비스"
                }
            },
            "silver": {
                "name": "실버",
                "annual_revenue_min": 5000000,
                "total_visits_min": 11,
                "total_visits_max": 30,
                "benefits": {
                    "discount_rate": 5,
                    "test_vouchers": 1,
                    "supplements": 2,
                    "sessions": 2,
                    "description": "5% 할인, 검사권 1개, 영양제 2개, 세션 2개"
                }
            },
            "gold": {
                "name": "골드",
                "annual_revenue_min": 10000000,
                "total_visits_min": 31,
                "total_visits_max": 99,
                "benefits": {
                    "discount_rate": 10,
                    "test_vouchers": 1,
                    "supplements": 2,
                    "sessions": 5,
                    "description": "10% 할인, 검사권 1개, 영양제 2개, 세션 5개"
                }
            },
            "platinum": {
                "name": "플래티넘",
                "annual_revenue_min": 20000000,
                "total_visits_min": 100,
                "benefits": {
                    "discount_rate": 15,
                    "test_vouchers": 1,
                    "supplements": 3,
                    "sessions": 10,
                    "dedicated_consultant": True,
                    "description": "15% 할인, 전담 상담사, 검사권 1개, 영양제 3개, 세션 10개"
                }
            }
        }
        
        # 기존 설정 확인
        existing = db.execute(text("""
            SELECT setting_id FROM system_settings 
            WHERE setting_key = 'membership_criteria'
        """)).fetchone()
        
        if existing:
            db.execute(text("""
                UPDATE system_settings 
                SET setting_value = :value,
                    updated_at = :updated_at
                WHERE setting_key = 'membership_criteria'
            """), {
                'value': json.dumps(membership_criteria, ensure_ascii=False),
                'updated_at': datetime.now()
            })
        else:
            db.execute(text("""
                INSERT INTO system_settings (setting_key, setting_value, created_at, updated_at)
                VALUES ('membership_criteria', :value, :created_at, :updated_at)
            """), {
                'value': json.dumps(membership_criteria, ensure_ascii=False),
                'created_at': datetime.now(),
                'updated_at': datetime.now()
            })
        
        # 5. 고객 상태 및 위험 수준 설명 추가
        status_descriptions = {
            "customer_status": {
                "active": {
                    "name": "활성",
                    "description": "최근 30일 이내 서비스 이용",
                    "color": "green"
                },
                "inactive": {
                    "name": "비활성",
                    "description": "30일~90일 동안 서비스 미이용",
                    "color": "yellow"
                },
                "dormant": {
                    "name": "휴면",
                    "description": "90일 이상 서비스 미이용",
                    "color": "red"
                }
            },
            "risk_level": {
                "stable": {
                    "name": "안정",
                    "description": "정기적 이용 패턴 유지",
                    "color": "green"
                },
                "at_risk": {
                    "name": "위험",
                    "description": "이용 빈도 감소 또는 불규칙한 패턴",
                    "color": "yellow"
                },
                "high_risk": {
                    "name": "고위험",
                    "description": "장기간 미이용 또는 불만 접수 이력",
                    "color": "red"
                }
            }
        }
        
        # 상태 설명 저장
        existing = db.execute(text("""
            SELECT setting_id FROM system_settings 
            WHERE setting_key = 'customer_status_descriptions'
        """)).fetchone()
        
        if existing:
            db.execute(text("""
                UPDATE system_settings 
                SET setting_value = :value,
                    updated_at = :updated_at
                WHERE setting_key = 'customer_status_descriptions'
            """), {
                'value': json.dumps(status_descriptions, ensure_ascii=False),
                'updated_at': datetime.now()
            })
        else:
            db.execute(text("""
                INSERT INTO system_settings (setting_key, setting_value, created_at, updated_at)
                VALUES ('customer_status_descriptions', :value, :created_at, :updated_at)
            """), {
                'value': json.dumps(status_descriptions, ensure_ascii=False),
                'created_at': datetime.now(),
                'updated_at': datetime.now()
            })
        
        db.commit()
        print("✅ Membership system updated successfully!")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error updating membership system: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    update_membership_system()