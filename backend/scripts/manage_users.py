#!/usr/bin/env python
"""
사용자 계정 관리 스크립트
- 기존 admin 계정 수정
- 새로운 담당자 계정 생성
"""

import sys
import os
from pathlib import Path

# 프로젝트 루트 경로 추가
sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy.orm import Session
from sqlalchemy import text
from core.database import engine, get_db
from core.auth import get_password_hash
from models.user import User
from datetime import datetime
import logging
from enum import Enum

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# UserRole 정의
class UserRole(str, Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    STAFF = "staff"

def check_existing_users(db: Session):
    """현재 사용자 목록 확인"""
    logger.info("현재 사용자 목록 확인...")
    users = db.query(User).all()
    
    if users:
        print("\n현재 등록된 사용자:")
        print("-" * 50)
        for user in users:
            print(f"ID: {user.user_id}, 이름: {user.name}, 이메일: {user.email}, 권한: {user.role}")
        print("-" * 50)
    else:
        print("등록된 사용자가 없습니다.")
    
    return users

def update_admin_user(db: Session):
    """기존 admin@aibio.com을 clv@biocom.kr로 변경"""
    logger.info("기존 admin 계정 수정 중...")
    
    admin_user = db.query(User).filter(User.email == "admin@aibio.com").first()
    if admin_user:
        admin_user.email = "clv@biocom.kr"
        admin_user.updated_at = datetime.utcnow()
        db.commit()
        logger.info(f"✓ admin@aibio.com을 clv@biocom.kr로 변경 완료")
        return True
    else:
        logger.warning("admin@aibio.com 계정을 찾을 수 없습니다.")
        return False

def create_user(db: Session, name: str, email: str, password: str, role: UserRole):
    """새로운 사용자 생성"""
    # 이미 존재하는지 확인
    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user:
        logger.info(f"이미 존재하는 사용자: {email}")
        return existing_user
    
    # 새 사용자 생성
    new_user = User(
        name=name,
        email=email,
        password_hash=get_password_hash(password),  # password가 아닌 password_hash
        role=role.value,  # Enum value를 문자열로
        is_active=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    logger.info(f"✓ 새 사용자 생성 완료: {name} ({email}) - {role.value}")
    return new_user

def main():
    """메인 실행 함수"""
    db = next(get_db())
    
    try:
        # 1. 현재 사용자 확인
        check_existing_users(db)
        
        # 2. 기존 admin 계정 수정
        print("\n1. 기존 admin 계정 수정")
        update_admin_user(db)
        
        # 3. 새로운 사용자들 생성
        print("\n2. 새로운 담당자 계정 생성")
        
        users_to_create = [
            {
                "name": "이수경",
                "email": "sookyeong@biocom.kr",
                "password": "1111",
                "role": UserRole.MANAGER
            },
            {
                "name": "유승우",
                "email": "seungwoo@biocom.kr",
                "password": "1111",
                "role": UserRole.ADMIN
            },
            {
                "name": "김예림",
                "email": "yerim@biocom.kr",
                "password": "1111",
                "role": UserRole.MANAGER
            },
            {
                "name": "전태준",
                "email": "taejun@biocom.kr",
                "password": "admin123",
                "role": UserRole.ADMIN
            }
        ]
        
        for user_data in users_to_create:
            create_user(
                db,
                name=user_data["name"],
                email=user_data["email"],
                password=user_data["password"],
                role=user_data["role"]
            )
        
        # 4. 최종 사용자 목록 확인
        print("\n3. 최종 사용자 목록")
        check_existing_users(db)
        
        print("\n✅ 모든 작업이 완료되었습니다.")
        
    except Exception as e:
        logger.error(f"오류 발생: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    main()