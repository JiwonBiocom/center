#!/usr/bin/env python3
"""
고객 상세 데이터 확인
"""
import psycopg2

DATABASE_URL = "postgresql://postgres.wvcxzyvmwwrbjpeuyvuh:bico6819!!@aws-0-ap-northeast-2.pooler.supabase.com:6543/postgres"

def check_details():
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    # 첫방문 날짜가 있는 고객 확인
    cursor.execute("""
        SELECT customer_id, name, assigned_staff, first_visit_date
        FROM customers 
        WHERE first_visit_date IS NOT NULL
        ORDER BY customer_id DESC
        LIMIT 5
    """)
    
    print('최근 고객 5명:')
    for row in cursor.fetchall():
        print(f'  ID: {row[0]}, 이름: {row[1]}, 담당자: {repr(row[2])}, 첫방문: {row[3]}')
    
    # ID 4783 확인
    cursor.execute("""
        SELECT customer_id, name, assigned_staff, first_visit_date
        FROM customers 
        WHERE customer_id = 4783
    """)
    
    row = cursor.fetchone()
    if row:
        print(f'\n고객 ID 4783 상세:')
        print(f'  이름: {row[1]}')
        print(f'  담당자: {repr(row[2])}')
        print(f'  첫방문: {row[3]}')
    
    cursor.close()
    conn.close()

if __name__ == "__main__":
    check_details()