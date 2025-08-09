#!/usr/bin/env python3
"""
Admin 비밀번호 재설정 스크립트
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from core.database import engine
from models.user import User
from core.auth import get_password_hash

def reset_admin_password():
    """admin@aibio.kr 계정의 비밀번호를 admin123으로 재설정"""
    
    new_password = "admin123"
    new_hash = get_password_hash(new_password)
    
    print(f"새로운 비밀번호 해시 생성됨:")
    print(f"Password: {new_password}")
    print(f"Hash: {new_hash}")
    print()
    
    with Session(engine) as db:
        # admin 계정 찾기
        admin = db.query(User).filter(User.email == "admin@aibio.kr").first()
        
        if not admin:
            print("❌ admin@aibio.kr 계정을 찾을 수 없습니다!")
            print("새로 생성하시겠습니까? (y/n): ", end="")
            if input().lower() == 'y':
                admin = User(
                    email="admin@aibio.kr",
                    password_hash=new_hash,
                    name="관리자",
                    role="admin",
                    is_active=True
                )
                db.add(admin)
                db.commit()
                print("✅ Admin 계정이 생성되었습니다!")
            return
        
        # 비밀번호 업데이트
        print(f"현재 계정 정보:")
        print(f"- ID: {admin.user_id}")
        print(f"- Email: {admin.email}")
        print(f"- Name: {admin.name}")
        print(f"- Role: {admin.role}")
        print(f"- Active: {admin.is_active}")
        print(f"- 현재 해시: {admin.password_hash[:20]}...")
        
        admin.password_hash = new_hash
        db.commit()
        
        print(f"\n✅ 비밀번호가 업데이트되었습니다!")
        print(f"- 새 해시: {new_hash[:20]}...")
        
    # SQL 쿼리도 제공
    print("\n또는 Supabase SQL Editor에서 다음 쿼리 실행:")
    print(f"""
UPDATE users 
SET password_hash = '{new_hash}'
WHERE email = 'admin@aibio.kr';
""")

if __name__ == "__main__":
    reset_admin_password()