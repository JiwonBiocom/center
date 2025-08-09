#!/usr/bin/env python3
"""
notifications 테이블 구조 확인
"""
import psycopg2
from datetime import datetime

DATABASE_URL = "postgresql://postgres.wvcxzyvmwwrbjpeuyvuh:bico6819!!@aws-0-ap-northeast-2.pooler.supabase.com:6543/postgres"

def check_notifications_table():
    """notifications 테이블 구조 확인"""
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    print(f"🔍 notifications 테이블 구조 확인")
    print(f"시간: {datetime.now()}")
    print("=" * 60)
    
    # 테이블 컬럼 확인
    cursor.execute("""
        SELECT 
            column_name, 
            data_type, 
            is_nullable,
            column_default
        FROM information_schema.columns 
        WHERE table_name = 'notifications'
        ORDER BY ordinal_position
    """)
    
    columns = cursor.fetchall()
    
    print(f"\n📋 notifications 테이블 컬럼 ({len(columns)}개):")
    for col in columns:
        nullable = "NULL" if col[2] == 'YES' else "NOT NULL"
        default = f" DEFAULT {col[3]}" if col[3] else ""
        print(f"  • {col[0]}: {col[1]} ({nullable}){default}")
    
    # user_id 컬럼 특별히 확인
    print("\n🔍 user_id 컬럼 확인:")
    cursor.execute("""
        SELECT 
            column_name,
            data_type,
            is_nullable
        FROM information_schema.columns 
        WHERE table_name = 'notifications' 
        AND column_name = 'user_id'
    """)
    
    user_id_col = cursor.fetchone()
    if user_id_col:
        print(f"  ✅ user_id 컬럼 존재: {user_id_col[1]} ({user_id_col[2]})")
    else:
        print(f"  ❌ user_id 컬럼이 없습니다!")
    
    # 외래 키 확인
    cursor.execute("""
        SELECT 
            constraint_name,
            column_name,
            foreign_table_name,
            foreign_column_name
        FROM information_schema.key_column_usage kcu
        JOIN information_schema.table_constraints tc 
            ON kcu.constraint_name = tc.constraint_name
        JOIN information_schema.constraint_column_usage ccu
            ON kcu.constraint_name = ccu.constraint_name
        WHERE kcu.table_name = 'notifications'
        AND tc.constraint_type = 'FOREIGN KEY'
    """)
    
    fks = cursor.fetchall()
    print(f"\n🔗 외래 키 제약 조건:")
    for fk in fks:
        print(f"  • {fk[1]} → {fk[2]}({fk[3]})")
    
    cursor.close()
    conn.close()

if __name__ == "__main__":
    check_notifications_table()