#!/usr/bin/env python3
"""
사용자 계정 확인
"""
import psycopg2

DATABASE_URL = "postgresql://postgres.wvcxzyvmwwrbjpeuyvuh:bico6819!!@aws-0-ap-northeast-2.pooler.supabase.com:6543/postgres"

def check_users():
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    print("👥 사용자 계정 확인")
    print("=" * 50)
    
    cursor.execute("""
        SELECT user_id, email, name, role, is_active
        FROM users
        ORDER BY user_id
    """)
    
    users = cursor.fetchall()
    print(f"\n등록된 사용자: {len(users)}명")
    print("-" * 50)
    for user in users:
        status = "✅" if user[4] else "❌"
        print(f"{status} {user[0]:2d} | {user[1]:25} | {user[2]:15} | {user[3]}")
    
    print(f"\n💡 테스트 로그인 정보:")
    if users:
        first_user = users[0]
        print(f"이메일: {first_user[1]}")
        print(f"비밀번호: admin123 (기본값)")
    
    cursor.close()
    conn.close()

if __name__ == "__main__":
    check_users()