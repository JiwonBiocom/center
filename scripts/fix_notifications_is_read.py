#!/usr/bin/env python3
"""
notifications 테이블 is_read 컬럼 추가
"""
import psycopg2

DATABASE_URL = "postgresql://postgres.wvcxzyvmwwrbjpeuyvuh:bico6819!!@aws-0-ap-northeast-2.pooler.supabase.com:6543/postgres"

def fix_is_read():
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    try:
        # is_read 컬럼 존재 확인
        cursor.execute("""
            SELECT COUNT(*) 
            FROM information_schema.columns 
            WHERE table_name = 'notifications' 
            AND column_name = 'is_read'
        """)
        
        if cursor.fetchone()[0] == 0:
            print("❌ notifications 테이블에 is_read 컬럼이 없습니다.")
            
            # is_read 컬럼 추가
            cursor.execute("""
                ALTER TABLE notifications 
                ADD COLUMN is_read BOOLEAN DEFAULT false
            """)
            print("✅ is_read 컬럼 추가 완료")
            
            conn.commit()
            print("\n🎉 notifications 테이블에 is_read 컬럼 추가 완료!")
        else:
            print("✅ notifications 테이블에 is_read 컬럼이 이미 존재합니다.")
            
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    fix_is_read()