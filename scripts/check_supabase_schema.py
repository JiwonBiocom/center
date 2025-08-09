#!/usr/bin/env python3
"""
Supabase 테이블 스키마 확인
"""
import psycopg2

DATABASE_URL = "postgresql://postgres.wvcxzyvmwwrbjpeuyvuh:bico6819!!@aws-0-ap-northeast-2.pooler.supabase.com:6543/postgres"

def check_schema():
    """테이블 스키마 확인"""
    
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    tables = ['packages', 'service_types', 'kit_types', 'customers', 'payments', 'leads']
    
    for table in tables:
        print(f"\n📋 {table} 테이블 구조:")
        print("-" * 50)
        
        cursor.execute(f"""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_name = '{table}'
            ORDER BY ordinal_position
        """)
        
        columns = cursor.fetchall()
        if columns:
            for col in columns:
                nullable = "NULL" if col[2] == "YES" else "NOT NULL"
                print(f"   {col[0]:<20} {col[1]:<20} {nullable}")
        else:
            print("   테이블이 존재하지 않습니다.")
    
    cursor.close()
    conn.close()

if __name__ == "__main__":
    check_schema()