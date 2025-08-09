#!/usr/bin/env python3
"""
notifications 테이블 user_id 컬럼 추가
"""
import psycopg2

DATABASE_URL = "postgresql://postgres.wvcxzyvmwwrbjpeuyvuh:bico6819!!@aws-0-ap-northeast-2.pooler.supabase.com:6543/postgres"

def fix_notifications():
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    try:
        # user_id 컬럼 존재 확인
        cursor.execute("""
            SELECT COUNT(*) 
            FROM information_schema.columns 
            WHERE table_name = 'notifications' 
            AND column_name = 'user_id'
        """)
        
        if cursor.fetchone()[0] == 0:
            print("❌ notifications 테이블에 user_id 컬럼이 없습니다.")
            
            # 1. user_id 컬럼 추가
            cursor.execute("""
                ALTER TABLE notifications 
                ADD COLUMN user_id INTEGER
            """)
            print("✅ user_id 컬럼 추가 완료")
            
            # 2. 기본값 설정 (admin user = 1)
            cursor.execute("""
                UPDATE notifications 
                SET user_id = 1 
                WHERE user_id IS NULL
            """)
            print("✅ 기본값 설정 완료")
            
            # 3. NOT NULL 제약 조건 추가
            cursor.execute("""
                ALTER TABLE notifications 
                ALTER COLUMN user_id SET NOT NULL
            """)
            print("✅ NOT NULL 제약 조건 추가 완료")
            
            # 4. 외래 키 제약 조건 추가
            cursor.execute("""
                ALTER TABLE notifications 
                ADD CONSTRAINT fk_notifications_user 
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            """)
            print("✅ 외래 키 제약 조건 추가 완료")
            
            # 5. 인덱스 추가
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_notifications_user_id 
                ON notifications(user_id)
            """)
            print("✅ 인덱스 추가 완료")
            
            conn.commit()
            print("\n🎉 notifications 테이블 스키마 수정 완료!")
        else:
            print("✅ notifications 테이블에 user_id 컬럼이 이미 존재합니다.")
            
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    fix_notifications()