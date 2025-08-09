#!/usr/bin/env python3
"""
notifications 테이블 상세 확인
"""
import psycopg2
from datetime import datetime

DATABASE_URL = "postgresql://postgres.wvcxzyvmwwrbjpeuyvuh:bico6819!!@aws-0-ap-northeast-2.pooler.supabase.com:6543/postgres"

def check_notifications():
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    print(f"🔍 notifications 테이블 상세 확인")
    print(f"시간: {datetime.now()}")
    print("=" * 60)
    
    # 1. 테이블 구조 확인
    cursor.execute("""
        SELECT 
            column_name,
            data_type,
            is_nullable,
            column_default
        FROM information_schema.columns
        WHERE table_name = 'notifications'
        AND table_schema = 'public'
        ORDER BY ordinal_position
    """)
    
    columns = cursor.fetchall()
    print("\n📊 notifications 테이블 구조:")
    print("-" * 60)
    for col in columns:
        print(f"  {col[0]:20} {col[1]:20} {col[2]:10} {col[3] or ''}")
    
    # 2. 제약 조건 확인
    cursor.execute("""
        SELECT 
            tc.constraint_name,
            tc.constraint_type,
            kcu.column_name
        FROM information_schema.table_constraints tc
        JOIN information_schema.key_column_usage kcu
            ON tc.constraint_name = kcu.constraint_name
            AND tc.table_schema = kcu.table_schema
        WHERE tc.table_name = 'notifications'
        AND tc.table_schema = 'public'
        ORDER BY tc.constraint_type, tc.constraint_name
    """)
    
    constraints = cursor.fetchall()
    print(f"\n🔗 제약 조건:")
    print("-" * 60)
    for con in constraints:
        print(f"  {con[0]:30} {con[1]:20} ({con[2]})")
    
    # 3. 인덱스 확인
    cursor.execute("""
        SELECT 
            indexname,
            indexdef
        FROM pg_indexes
        WHERE tablename = 'notifications'
        AND schemaname = 'public'
    """)
    
    indexes = cursor.fetchall()
    print(f"\n📑 인덱스:")
    print("-" * 60)
    for idx in indexes:
        print(f"  {idx[0]}")
        print(f"    {idx[1]}")
    
    # 4. 데이터 통계
    cursor.execute("SELECT COUNT(*) FROM notifications")
    count = cursor.fetchone()[0]
    print(f"\n📊 데이터 통계:")
    print(f"  전체 레코드 수: {count}")
    
    if count > 0:
        cursor.execute("""
            SELECT 
                type, 
                COUNT(*) as cnt 
            FROM notifications 
            GROUP BY type 
            ORDER BY cnt DESC
        """)
        types = cursor.fetchall()
        print(f"\n  타입별 분포:")
        for t in types:
            print(f"    - {t[0]}: {t[1]}건")
    
    cursor.close()
    conn.close()

if __name__ == "__main__":
    check_notifications()