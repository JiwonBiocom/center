#!/usr/bin/env python3
"""
notifications 테이블의 user_id 컬럼 수정
"""
import psycopg2
from datetime import datetime

DATABASE_URL = "postgresql://postgres.wvcxzyvmwwrbjpeuyvuh:bico6819!!@aws-0-ap-northeast-2.pooler.supabase.com:6543/postgres"

def fix_notifications_user_id():
    """notifications 테이블의 user_id 컬럼 수정"""
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    print(f"🔧 notifications 테이블 user_id 수정")
    print(f"시간: {datetime.now()}")
    print("=" * 60)
    
    try:
        # 1. NULL인 user_id를 기본값으로 업데이트
        cursor.execute("""
            UPDATE notifications 
            SET user_id = 1 
            WHERE user_id IS NULL
        """)
        updated_rows = cursor.rowcount
        print(f"  ✅ {updated_rows}개 행의 user_id를 1로 설정")
        
        # 2. NOT NULL 제약 조건 추가
        cursor.execute("""
            ALTER TABLE notifications 
            ALTER COLUMN user_id SET NOT NULL
        """)
        print(f"  ✅ user_id NOT NULL 제약 조건 추가")
        
        # 3. 외래 키 제약 조건 확인 및 추가
        cursor.execute("""
            SELECT constraint_name 
            FROM information_schema.table_constraints 
            WHERE table_name = 'notifications' 
            AND constraint_name = 'fk_notifications_user'
        """)
        
        if not cursor.fetchone():
            cursor.execute("""
                ALTER TABLE notifications 
                ADD CONSTRAINT fk_notifications_user 
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            """)
            print(f"  ✅ 외래 키 제약 조건 추가")
        else:
            print(f"  ✓ 외래 키 제약 조건이 이미 존재합니다")
        
        # 4. 인덱스 확인 및 추가
        cursor.execute("""
            SELECT indexname 
            FROM pg_indexes 
            WHERE tablename = 'notifications' 
            AND indexname = 'idx_notifications_user_id'
        """)
        
        if not cursor.fetchone():
            cursor.execute("""
                CREATE INDEX idx_notifications_user_id 
                ON notifications(user_id)
            """)
            print(f"  ✅ user_id 인덱스 추가")
        else:
            print(f"  ✓ user_id 인덱스가 이미 존재합니다")
        
        conn.commit()
        print(f"\n✅ notifications 테이블 수정 완료!")
        
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    fix_notifications_user_id()