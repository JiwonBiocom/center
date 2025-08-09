#!/usr/bin/env python3
"""
비밀번호 해시 생성 스크립트
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.auth import get_password_hash

def generate_hashes():
    """주요 계정들의 비밀번호 해시 생성"""

    passwords = [
        ("admin@aibio.kr", "admin123"),
        ("taejun@biocom.kr", "admin1234"),
        ("manager@aibio.kr", "manager123"),
    ]

    print("=" * 80)
    print("비밀번호 해시 생성")
    print("=" * 80)

    for email, password in passwords:
        hash_value = get_password_hash(password)
        print(f"\n계정: {email}")
        print(f"비밀번호: {password}")
        print(f"해시: {hash_value}")

    print("\n" + "=" * 80)
    print("SQL 업데이트 쿼리:")
    print("=" * 80)

    for email, password in passwords:
        hash_value = get_password_hash(password)
        print(f"\n-- {email} ({password})")
        print(f"UPDATE users SET password_hash = '{hash_value}' WHERE email = '{email}';")

if __name__ == "__main__":
    generate_hashes()
