#!/usr/bin/env python3
"""
유영상 고객 데이터 확인
"""
import psycopg2

DATABASE_URL = "postgresql://postgres.wvcxzyvmwwrbjpeuyvuh:bico6819!!@aws-0-ap-northeast-2.pooler.supabase.com:6543/postgres"

def check_customer():
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT customer_id, name, first_visit_date, assigned_staff
        FROM customers 
        WHERE name = '유영상'
    """)
    
    for row in cursor.fetchall():
        print(f'ID: {row[0]}, 이름: {row[1]}, 첫방문: {row[2]}, 담당자: {row[3]}')
    
    cursor.close()
    conn.close()

if __name__ == "__main__":
    check_customer()