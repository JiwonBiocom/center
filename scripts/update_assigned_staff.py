#!/usr/bin/env python3
"""
담당자 필드 업데이트
"""
import psycopg2

DATABASE_URL = "postgresql://postgres.wvcxzyvmwwrbjpeuyvuh:bico6819!!@aws-0-ap-northeast-2.pooler.supabase.com:6543/postgres"

def update_staff():
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    # assigned_staff 상태 확인
    cursor.execute("""
        SELECT assigned_staff, COUNT(*) 
        FROM customers 
        GROUP BY assigned_staff 
        ORDER BY COUNT(*) DESC
        LIMIT 10
    """)
    
    print('담당자별 고객 수:')
    for row in cursor.fetchall():
        staff = row[0] if row[0] else "(빈값)"
        print(f'  {staff}: {row[1]}명')
    
    # 빈 문자열, NULL, 'nan'을 '직원'으로 업데이트
    cursor.execute("""
        UPDATE customers 
        SET assigned_staff = '직원' 
        WHERE assigned_staff = '' 
           OR assigned_staff IS NULL 
           OR assigned_staff = 'nan'
           OR assigned_staff = 'NaN'
    """)
    
    updated = cursor.rowcount
    print(f'\n✅ {updated}명의 담당자를 "직원"으로 업데이트')
    
    conn.commit()
    cursor.close()
    conn.close()

if __name__ == "__main__":
    update_staff()