#!/usr/bin/env python3
"""
사용자 비밀번호를 초기화합니다.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from core.database import SessionLocal
from models.user import User
from core.auth import get_password_hash

def reset_passwords():
    """주요 계정들의 비밀번호 초기화"""
    db = SessionLocal()

    try:
        print("=" * 60)
        print("사용자 비밀번호 초기화")
        print("=" * 60)

        # admin@aibio.kr 초기화
        admin_user = db.query(User).filter(User.email == "admin@aibio.kr").first()
        if admin_user:
            admin_user.password_hash = get_password_hash("admin123")
            admin_user.is_active = True
            print("✅ admin@aibio.kr → admin123")
        else:
            # 계정 생성
            new_admin = User(
                email="admin@aibio.kr",
                name="관리자",
                password_hash=get_password_hash("admin123"),
                role="admin",
                is_active=True
            )
            db.add(new_admin)
            print("✅ admin@aibio.kr 계정 생성 (admin123)")

        # taejun@biocom.kr 초기화
        master_user = db.query(User).filter(User.email == "taejun@biocom.kr").first()
        if master_user:
            master_user.password_hash = get_password_hash("admin1234")
            master_user.is_active = True
            master_user.role = "master"  # 권한도 확실히 master로
            print("✅ taejun@biocom.kr → admin1234 (master)")
        else:
            # 계정 생성
            new_master = User(
                email="taejun@biocom.kr",
                name="TaeJun",
                password_hash=get_password_hash("admin1234"),
                role="master",
                is_active=True
            )
            db.add(new_master)
            print("✅ taejun@biocom.kr 계정 생성 (admin1234, master)")

        # manager@aibio.kr 확인
        manager_user = db.query(User).filter(User.email == "manager@aibio.kr").first()
        if manager_user:
            manager_user.password_hash = get_password_hash("manager123")
            manager_user.is_active = True
            print("✅ manager@aibio.kr → manager123")

        db.commit()
        print("\n✅ 모든 비밀번호가 초기화되었습니다!")

        # 업데이트된 계정 목록 표시
        print("\n" + "-" * 60)
        print("업데이트된 계정 정보:")
        print("-" * 60)

        accounts = [
            ("admin@aibio.kr", "admin123", "admin"),
            ("taejun@biocom.kr", "admin1234", "master"),
            ("manager@aibio.kr", "manager123", "manager")
        ]

        for email, password, expected_role in accounts:
            user = db.query(User).filter(User.email == email).first()
            if user:
                print(f"\n📧 {email}")
                print(f"   비밀번호: {password}")
                print(f"   권한: {user.role}")
                print(f"   활성: {user.is_active}")

    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("⚠️  이 스크립트는 사용자 비밀번호를 초기화합니다.")
    print("계속하시겠습니까? (y/n): ", end="")

    # 자동으로 y 입력
    print("y")
    reset_passwords()
