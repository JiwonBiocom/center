#!/usr/bin/env python3
"""
첫방문 날짜 기준으로 고객 상태 업데이트
(last_visit_date가 없는 경우 first_visit_date 사용)
"""
import psycopg2
from datetime import datetime, date, timedelta

DATABASE_URL = "postgresql://postgres.wvcxzyvmwwrbjpeuyvuh:bico6819!!@aws-0-ap-northeast-2.pooler.supabase.com:6543/postgres"

def update_customer_status():
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    # 현재 날짜 확인 (2025년 1월로 가정)
    today = date(2025, 1, 21)  # 실제 오늘 날짜
    print(f"📅 기준 날짜: {today}")
    
    # 1. last_visit_date가 없는 경우 first_visit_date로 설정
    cursor.execute("""
        UPDATE customers
        SET last_visit_date = first_visit_date
        WHERE last_visit_date IS NULL AND first_visit_date IS NOT NULL
    """)
    updated_visits = cursor.rowcount
    print(f"\n✅ {updated_visits}명의 last_visit_date를 first_visit_date로 설정")
    
    # 2. 30일 이내 방문 고객을 active로 설정
    active_date = today - timedelta(days=30)
    cursor.execute("""
        UPDATE customers
        SET customer_status = 'active'
        WHERE last_visit_date >= %s
    """, (active_date,))
    active_count = cursor.rowcount
    print(f"✅ {active_count}명을 active 상태로 업데이트")
    
    # 3. 31-90일 사이 방문 고객을 inactive로 설정
    inactive_date = today - timedelta(days=90)
    cursor.execute("""
        UPDATE customers
        SET customer_status = 'inactive'
        WHERE last_visit_date < %s AND last_visit_date >= %s
    """, (active_date, inactive_date))
    inactive_count = cursor.rowcount
    print(f"✅ {inactive_count}명을 inactive 상태로 업데이트")
    
    # 4. 90일 초과 미방문 고객을 dormant로 설정
    cursor.execute("""
        UPDATE customers
        SET customer_status = 'dormant'
        WHERE last_visit_date < %s OR last_visit_date IS NULL
    """, (inactive_date,))
    dormant_count = cursor.rowcount
    print(f"✅ {dormant_count}명을 dormant 상태로 업데이트")
    
    # 최종 통계
    cursor.execute("""
        SELECT customer_status, COUNT(*) 
        FROM customers 
        GROUP BY customer_status
        ORDER BY customer_status
    """)
    
    print(f"\n📊 최종 고객 상태 분포:")
    print("-" * 40)
    for row in cursor.fetchall():
        status = row[0] or "(없음)"
        count = row[1]
        print(f"  {status}: {count}명")
    
    # 최근 active 고객 샘플
    cursor.execute("""
        SELECT name, last_visit_date, customer_status
        FROM customers 
        WHERE customer_status = 'active'
        ORDER BY last_visit_date DESC
        LIMIT 5
    """)
    
    active_samples = cursor.fetchall()
    if active_samples:
        print(f"\n👥 Active 고객 샘플:")
        for row in active_samples:
            print(f"  - {row[0]}: 마지막 방문 {row[1]}")
    
    conn.commit()
    cursor.close()
    conn.close()
    
    print(f"\n🎉 고객 상태 업데이트 완료!")

if __name__ == "__main__":
    update_customer_status()