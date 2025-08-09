#!/usr/bin/env python3
"""
스키마 드리프트 수정 스크립트
GitHub Actions에서 감지된 스키마 차이를 수정합니다.
"""
import psycopg2
from datetime import datetime

DATABASE_URL = "postgresql://postgres.wvcxzyvmwwrbjpeuyvuh:bico6819!!@aws-0-ap-northeast-2.pooler.supabase.com:6543/postgres"

def fix_schema_drift():
    """스키마 드리프트 수정"""
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    print(f"🔧 스키마 드리프트 수정")
    print(f"시간: {datetime.now()}")
    print("=" * 60)
    
    try:
        # 1. notifications 테이블에 user_id 추가
        print("\n📋 notifications 테이블 수정:")
        
        # user_id 컬럼 확인
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'notifications' 
            AND column_name = 'user_id'
        """)
        
        if not cursor.fetchone():
            # user_id 컬럼 추가
            cursor.execute("""
                ALTER TABLE notifications 
                ADD COLUMN user_id INTEGER
            """)
            print("  ✅ user_id 컬럼 추가됨")
            
            # 기본값 설정 (admin 사용자)
            cursor.execute("""
                UPDATE notifications 
                SET user_id = 1 
                WHERE user_id IS NULL
            """)
            print("  ✅ 기존 데이터에 기본값 설정")
            
            # NOT NULL 제약 조건 추가
            cursor.execute("""
                ALTER TABLE notifications 
                ALTER COLUMN user_id SET NOT NULL
            """)
            print("  ✅ NOT NULL 제약 조건 추가")
            
            # 외래 키 제약 조건 추가
            cursor.execute("""
                ALTER TABLE notifications 
                ADD CONSTRAINT fk_notifications_user 
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            """)
            print("  ✅ 외래 키 제약 조건 추가")
            
            # 인덱스 추가
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_notifications_user_id 
                ON notifications(user_id)
            """)
            print("  ✅ 인덱스 추가")
        else:
            print("  ✓ user_id 컬럼이 이미 존재합니다")
        
        conn.commit()
        print(f"\n✅ 스키마 드리프트 수정 완료!")
        
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    fix_schema_drift()