#!/usr/bin/env python3
"""
패키지 데이터 미리보기
"""
import sqlite3
from pathlib import Path

def preview_packages():
    """패키지 데이터 미리보기"""
    
    local_db = Path("backend/aibio_center.db")
    conn = sqlite3.connect(local_db)
    cursor = conn.cursor()
    
    # 패키지 데이터 조회
    cursor.execute("""
        SELECT package_id, package_name, total_sessions, price, valid_days
        FROM packages
        ORDER BY price DESC
    """)
    
    packages = cursor.fetchall()
    
    print("📦 로컬 패키지 데이터 (12개)")
    print("=" * 80)
    print(f"{'ID':>3} | {'패키지명':<30} | {'횟수':>4} | {'가격':>12} | {'기간':>5}")
    print("-" * 80)
    
    for pkg in packages:
        print(f"{pkg[0]:>3} | {pkg[1]:<30} | {pkg[2]:>4}회 | ₩{pkg[3]:>11,.0f} | {pkg[4]:>4}일")
    
    print("\n💡 이 데이터를 온라인으로 마이그레이션하면:")
    print("   - 패키지 관리 페이지가 정상 작동")
    print("   - 결제와 패키지 연결 가능")
    print("   - 신규 패키지 구매 가능")
    
    conn.close()

if __name__ == "__main__":
    preview_packages()