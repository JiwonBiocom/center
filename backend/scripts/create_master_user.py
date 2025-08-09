import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from core.database import SessionLocal
from core.auth import get_password_hash
from models.user import User
import getpass

def create_master_user():
    """마스터 사용자 생성 스크립트"""
    db = SessionLocal()

    try:
        print("=== 마스터 사용자 생성 ===")

        # 이메일 입력
        email = input("이메일 주소: ").strip()

        # 기존 사용자 확인
        existing_user = db.query(User).filter(User.email == email).first()
        if existing_user:
            print(f"이미 존재하는 이메일입니다: {email}")
            confirm = input("기존 사용자를 마스터로 업그레이드하시겠습니까? (y/n): ")
            if confirm.lower() != 'y':
                return

            # 기존 사용자를 마스터로 업그레이드
            existing_user.role = "master"
            db.commit()
            print(f"사용자 {email}이(가) 마스터 권한으로 업그레이드되었습니다.")
            return

        # 신규 사용자 정보 입력
        name = input("이름: ").strip()
        password = getpass.getpass("비밀번호: ")
        password_confirm = getpass.getpass("비밀번호 확인: ")

        if password != password_confirm:
            print("비밀번호가 일치하지 않습니다.")
            return

        # 마스터 사용자 생성
        new_user = User(
            email=email,
            name=name,
            password_hash=get_password_hash(password),
            role="master",
            is_active=True
        )

        db.add(new_user)
        db.commit()

        print(f"\n마스터 사용자가 성공적으로 생성되었습니다!")
        print(f"이메일: {email}")
        print(f"이름: {name}")
        print(f"권한: master")

    except Exception as e:
        print(f"오류 발생: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_master_user()
