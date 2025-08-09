#!/usr/bin/env python3
"""
서비스 타입 미리보기
"""
import sqlite3
from pathlib import Path

def preview_service_types():
    """서비스 타입 미리보기"""
    
    local_db = Path("backend/aibio_center.db")
    conn = sqlite3.connect(local_db)
    cursor = conn.cursor()
    
    # 서비스 타입 조회
    cursor.execute("""
        SELECT service_type_id, service_name, description
        FROM service_types
        ORDER BY service_type_id
    """)
    
    service_types = cursor.fetchall()
    
    print("🏥 로컬 서비스 타입 (5개)")
    print("=" * 70)
    
    for st in service_types:
        print(f"ID: {st[0]} | {st[1]}")
        if st[2]:
            print(f"   설명: {st[2]}")
    
    # kit_types도 확인
    print("\n🧪 로컬 키트 타입 (5개)")
    print("=" * 70)
    
    cursor.execute("""
        SELECT kit_type_id, name, code, price
        FROM kit_types
        ORDER BY kit_type_id
    """)
    
    kit_types = cursor.fetchall()
    for kt in kit_types:
        print(f"ID: {kt[0]} | {kt[1]} ({kt[2]}) - ₩{kt[3]:,}")
    
    conn.close()

if __name__ == "__main__":
    preview_service_types()