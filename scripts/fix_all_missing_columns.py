#!/usr/bin/env python3
"""
모든 누락된 컬럼 추가
"""
import psycopg2
from datetime import datetime

DATABASE_URL = "postgresql://postgres.wvcxzyvmwwrbjpeuyvuh:bico6819!!@aws-0-ap-northeast-2.pooler.supabase.com:6543/postgres"

def fix_all_missing_columns():
    """모든 누락된 컬럼 추가"""
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    print(f"🔧 모든 누락된 컬럼 추가")
    print(f"시간: {datetime.now()}")
    print("=" * 60)
    
    # 예약 테이블에 추가할 컬럼들
    reservation_columns = [
        ("created_by", "VARCHAR(50)", "생성자"),
        ("cancelled_at", "TIMESTAMP", "취소 일시"),
        ("cancelled_by", "VARCHAR(50)", "취소자"),
        ("cancel_reason", "TEXT", "취소 사유")
    ]
    
    print("\n📅 예약 테이블 수정:")
    for column_name, column_type, description in reservation_columns:
        try:
            cursor.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'reservations' 
                AND column_name = %s
            """, (column_name,))
            
            if cursor.fetchone():
                print(f"  ✓ {column_name} - 이미 존재")
            else:
                cursor.execute(f"""
                    ALTER TABLE reservations 
                    ADD COLUMN {column_name} {column_type}
                """)
                print(f"  ✅ {column_name} - 추가됨 ({description})")
                
        except Exception as e:
            print(f"  ❌ {column_name} - 실패: {e}")
            conn.rollback()
            conn = psycopg2.connect(DATABASE_URL)
            cursor = conn.cursor()
    
    conn.commit()
    cursor.close()
    conn.close()
    
    print(f"\n✅ 모든 테이블 수정 완료")

if __name__ == "__main__":
    fix_all_missing_columns()