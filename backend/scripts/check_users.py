#!/usr/bin/env python3
"""
현재 데이터베이스의 사용자 목록을 확인합니다.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from core.database import SessionLocal
from models.user import User
from core.auth import verify_password, get_password_hash

def check_users():
    """현재 사용자 목록 확인"""
    db = SessionLocal()

    try:
        # 모든 사용자 조회
        users = db.query(User).all()

        print("=" * 60)
        print("현재 등록된 사용자 목록")
        print("=" * 60)

        if not users:
            print("❌ 등록된 사용자가 없습니다!")
            return

        for user in users:
            print(f"\n사용자 ID: {user.user_id}")
            print(f"  - 이메일: {user.email}")
            print(f"  - 이름: {user.name}")
            print(f"  - 권한: {user.role}")
            print(f"  - 활성: {user.is_active}")
            print(f"  - 생성일: {user.created_at}")

        # admin 계정 확인
        print("\n" + "=" * 60)
        print("기본 계정 상태 확인")
        print("=" * 60)

        # admin@aibio.kr 확인
        admin_user = db.query(User).filter(User.email == "admin@aibio.kr").first()
        if admin_user:
            print("\n✅ admin@aibio.kr 계정 존재")
            # 비밀번호 테스트
            test_passwords = ["admin123", "admin", "password", "123456"]
            for pwd in test_passwords:
                if verify_password(pwd, admin_user.password_hash):
                    print(f"  - 현재 비밀번호: {pwd}")
                    break
            else:
                print("  - ⚠️  알려진 비밀번호와 일치하지 않음")
        else:
            print("\n❌ admin@aibio.kr 계정이 없습니다!")

        # taejun@biocom.kr 확인
        master_user = db.query(User).filter(User.email == "taejun@biocom.kr").first()
        if master_user:
            print("\n✅ taejun@biocom.kr 계정 존재")
            print(f"  - 권한: {master_user.role}")
            if verify_password("admin1234", master_user.password_hash):
                print("  - 비밀번호 확인됨: admin1234")
            else:
                print("  - ⚠️  비밀번호가 admin1234가 아님")
        else:
            print("\n❌ taejun@biocom.kr 계정이 없습니다!")

    except Exception as e:
        print(f"❌ 오류 발생: {e}")
    finally:
        db.close()

def reset_admin_password():
    """admin 계정 비밀번호 초기화"""
    db = SessionLocal()

    try:
        # admin 계정 찾기
        admin_user = db.query(User).filter(User.email == "admin@aibio.kr").first()

        if admin_user:
            # 비밀번호를 admin123으로 초기화
            admin_user.password_hash = get_password_hash("admin123")
            admin_user.is_active = True
            db.commit()
            print("\n✅ admin@aibio.kr 비밀번호를 admin123으로 초기화했습니다.")
        else:
            # admin 계정 생성
            new_admin = User(
                email="admin@aibio.kr",
                name="관리자",
                password_hash=get_password_hash("admin123"),
                role="admin",
                is_active=True
            )
            db.add(new_admin)
            db.commit()
            print("\n✅ admin@aibio.kr 계정을 생성했습니다. (비밀번호: admin123)")

    except Exception as e:
        print(f"❌ 비밀번호 초기화 실패: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    check_users()

    # admin 계정이 없거나 비밀번호가 맞지 않으면 초기화 제안
    print("\n" + "-" * 60)
    response = input("\nadmin 계정을 초기화하시겠습니까? (y/n): ")
    if response.lower() == 'y':
        reset_admin_password()
