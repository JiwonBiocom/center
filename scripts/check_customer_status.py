#!/usr/bin/env python3
"""
고객 상태 확인 및 업데이트
"""
import psycopg2
from datetime import datetime, date

DATABASE_URL = "postgresql://postgres.wvcxzyvmwwrbjpeuyvuh:bico6819!!@aws-0-ap-northeast-2.pooler.supabase.com:6543/postgres"

def check_customer_status():
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    # 고객 상태별 통계
    cursor.execute("""
        SELECT customer_status, COUNT(*) 
        FROM customers 
        GROUP BY customer_status
        ORDER BY COUNT(*) DESC
    """)
    
    print("🔍 고객 상태 분포:")
    print("-" * 40)
    for row in cursor.fetchall():
        status = row[0] or "(없음)"
        count = row[1]
        print(f"  {status}: {count}명")
    
    # last_visit_date가 있는 고객 확인
    cursor.execute("""
        SELECT COUNT(*) FROM customers WHERE last_visit_date IS NOT NULL
    """)
    with_visit = cursor.fetchone()[0]
    
    cursor.execute("""
        SELECT COUNT(*) FROM customers WHERE last_visit_date IS NULL
    """)
    without_visit = cursor.fetchone()[0]
    
    print(f"\n📅 방문 날짜 현황:")
    print(f"  방문 기록 있음: {with_visit}명")
    print(f"  방문 기록 없음: {without_visit}명")
    
    # 최근 활성 고객 확인 (first_visit_date 기준)
    cursor.execute("""
        SELECT customer_id, name, first_visit_date, last_visit_date, customer_status
        FROM customers 
        WHERE first_visit_date IS NOT NULL 
          AND first_visit_date >= CURRENT_DATE - INTERVAL '30 days'
        ORDER BY first_visit_date DESC
        LIMIT 10
    """)
    
    recent_customers = cursor.fetchall()
    if recent_customers:
        print(f"\n🆕 최근 30일 내 첫방문 고객:")
        print("-" * 80)
        for row in recent_customers:
            print(f"  ID: {row[0]}, 이름: {row[1]}, 첫방문: {row[2]}, 최근방문: {row[3]}, 상태: {row[4]}")
    
    # 잘못된 상태 확인
    cursor.execute("""
        SELECT COUNT(*) 
        FROM customers 
        WHERE customer_status = 'active' 
          AND (last_visit_date IS NULL OR last_visit_date < CURRENT_DATE - INTERVAL '30 days')
    """)
    wrong_active = cursor.fetchone()[0]
    
    if wrong_active > 0:
        print(f"\n⚠️  잘못된 활성 상태: {wrong_active}명")
        print("  (30일 이상 방문하지 않았는데 active 상태인 고객)")
    
    cursor.close()
    conn.close()

if __name__ == "__main__":
    check_customer_status()