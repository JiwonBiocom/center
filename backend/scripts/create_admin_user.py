import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from core.database import SessionLocal, engine
from core.auth import get_password_hash
from models.user import User
import getpass

def create_admin_user():
    db = SessionLocal()
    
    try:
        print("=== 관리자 계정 생성 ===")
        
        # 이메일 입력
        email = input("관리자 이메일 주소: ")
        
        # 기존 사용자 확인
        existing_user = db.query(User).filter(User.email == email).first()
        if existing_user:
            print(f"이미 존재하는 이메일입니다: {email}")
            return
        
        # 이름 입력
        name = input("관리자 이름: ")
        
        # 비밀번호 입력
        password = getpass.getpass("비밀번호: ")
        password_confirm = getpass.getpass("비밀번호 확인: ")
        
        if password != password_confirm:
            print("비밀번호가 일치하지 않습니다.")
            return
        
        if len(password) < 8:
            print("비밀번호는 최소 8자 이상이어야 합니다.")
            return
        
        # 관리자 계정 생성
        hashed_password = get_password_hash(password)
        admin_user = User(
            email=email,
            password_hash=hashed_password,
            name=name,
            role="admin",
            is_active=True
        )
        
        db.add(admin_user)
        db.commit()
        
        print(f"\n관리자 계정이 성공적으로 생성되었습니다!")
        print(f"이메일: {email}")
        print(f"이름: {name}")
        print(f"역할: admin")
        
    except Exception as e:
        print(f"오류 발생: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_admin_user()