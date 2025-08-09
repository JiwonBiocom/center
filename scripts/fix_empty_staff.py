#!/usr/bin/env python3
"""
빈 문자열 담당자 수정
"""
import psycopg2

DATABASE_URL = "postgresql://postgres.wvcxzyvmwwrbjpeuyvuh:bico6819!!@aws-0-ap-northeast-2.pooler.supabase.com:6543/postgres"

def fix_empty_staff():
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    # 빈 문자열로 된 고객 수 확인
    cursor.execute("""
        SELECT COUNT(*) 
        FROM customers 
        WHERE assigned_staff = ''
    """)
    
    count = cursor.fetchone()[0]
    print(f'빈 문자열 담당자 고객 수: {count}명')
    
    if count > 0:
        # 빈 문자열을 '직원'으로 업데이트
        cursor.execute("""
            UPDATE customers 
            SET assigned_staff = '직원' 
            WHERE assigned_staff = ''
        """)
        
        updated = cursor.rowcount
        print(f'✅ {updated}명의 담당자를 "직원"으로 업데이트')
        
        conn.commit()
    
    cursor.close()
    conn.close()

if __name__ == "__main__":
    fix_empty_staff()