#!/usr/bin/env python3
"""
notifications 테이블에 user_id 외래 키 추가
"""
import psycopg2

DATABASE_URL = "postgresql://postgres.wvcxzyvmwwrbjpeuyvuh:bico6819!!@aws-0-ap-northeast-2.pooler.supabase.com:6543/postgres"

def add_user_foreign_key():
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    try:
        # 외래 키 제약 조건이 있는지 확인
        cursor.execute("""
            SELECT COUNT(*) 
            FROM information_schema.table_constraints 
            WHERE table_name = 'notifications' 
            AND constraint_name = 'fk_notifications_user'
        """)
        
        if cursor.fetchone()[0] == 0:
            print("🔧 user_id 외래 키 제약 조건 추가 중...")
            
            # 외래 키 추가
            cursor.execute("""
                ALTER TABLE notifications 
                ADD CONSTRAINT fk_notifications_user 
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            """)
            
            conn.commit()
            print("✅ 외래 키 제약 조건 추가 완료!")
        else:
            print("✅ 외래 키 제약 조건이 이미 존재합니다.")
            
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    add_user_foreign_key()