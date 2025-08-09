#!/usr/bin/env python3
"""
서비스 타입 테이블에 누락된 컬럼 추가
"""
import psycopg2
from datetime import datetime

DATABASE_URL = "postgresql://postgres.wvcxzyvmwwrbjpeuyvuh:bico6819!!@aws-0-ap-northeast-2.pooler.supabase.com:6543/postgres"

def fix_service_types_columns():
    """서비스 타입 테이블에 누락된 컬럼 추가"""
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    print(f"🔧 서비스 타입 테이블 컬럼 추가")
    print(f"시간: {datetime.now()}")
    print("=" * 60)
    
    # 추가할 컬럼들
    columns_to_add = [
        ("description", "TEXT", "서비스 설명"),
        ("default_duration", "INTEGER DEFAULT 60", "기본 소요 시간(분)"),
        ("default_price", "INTEGER DEFAULT 0", "기본 가격"),
        ("service_color", "VARCHAR(7) DEFAULT '#3B82F6'", "서비스 색상 코드")
    ]
    
    for column_name, column_type, description in columns_to_add:
        try:
            # 컬럼 존재 여부 확인
            cursor.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'service_types' 
                AND column_name = %s
            """, (column_name,))
            
            if cursor.fetchone():
                print(f"✓ {column_name} - 이미 존재")
            else:
                # 컬럼 추가
                cursor.execute(f"""
                    ALTER TABLE service_types 
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
    
    print(f"\n✅ 서비스 타입 테이블 수정 완료")

if __name__ == "__main__":
    fix_service_types_columns()