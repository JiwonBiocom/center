#!/usr/bin/env python3
"""
예약 테이블에 누락된 컬럼 추가
"""
import psycopg2
from datetime import datetime

DATABASE_URL = "postgresql://postgres.wvcxzyvmwwrbjpeuyvuh:bico6819!!@aws-0-ap-northeast-2.pooler.supabase.com:6543/postgres"

def fix_reservation_columns():
    """예약 테이블에 누락된 컬럼 추가"""
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    print(f"🔧 예약 테이블 컬럼 추가")
    print(f"시간: {datetime.now()}")
    print("=" * 60)
    
    # 추가할 컬럼들
    columns_to_add = [
        ("reminder_sent", "BOOLEAN DEFAULT FALSE", "알림 발송 여부"),
        ("confirmation_sent", "BOOLEAN DEFAULT FALSE", "확인 메시지 발송 여부")
    ]
    
    for column_name, column_type, description in columns_to_add:
        try:
            # 컬럼 존재 여부 확인
            cursor.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'reservations' 
                AND column_name = %s
            """, (column_name,))
            
            if cursor.fetchone():
                print(f"✓ {column_name} - 이미 존재")
            else:
                # 컬럼 추가
                cursor.execute(f"""
                    ALTER TABLE reservations 
                    ADD COLUMN {column_name} {column_type}
                """)
                print(f"✅ {column_name} - 추가됨 ({description})")
                
        except Exception as e:
            print(f"❌ {column_name} - 실패: {e}")
            conn.rollback()
            conn = psycopg2.connect(DATABASE_URL)
            cursor = conn.cursor()
    
    conn.commit()
    cursor.close()
    conn.close()
    
    print(f"\n✅ 예약 테이블 수정 완료")

if __name__ == "__main__":
    fix_reservation_columns()