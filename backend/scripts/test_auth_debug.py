#!/usr/bin/env python
"""
인증 시스템 디버깅 및 테스트 계정 패스워드 재설정
"""

import sys
import os
from pathlib import Path

# 프로젝트 루트 경로 추가
sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy.orm import Session
from core.database import get_db
from core.auth import get_password_hash, verify_password
from models.user import User
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_user_authentication(db: Session, email: str, test_password: str):
    """특정 사용자의 인증 테스트"""
    print(f"\n🔍 사용자 인증 테스트: {email}")
    print("-" * 50)
    
    user = db.query(User).filter(User.email == email).first()
    if not user:
        print(f"❌ 사용자를 찾을 수 없습니다: {email}")
        return False
    
    print(f"✅ 사용자 발견: {user.name} ({user.role})")
    print(f"   활성 상태: {user.is_active}")
    print(f"   패스워드 해시: {user.password_hash[:50]}...")
    
    # 패스워드 검증
    is_valid = verify_password(test_password, user.password_hash)
    print(f"   패스워드 검증: {'✅ 성공' if is_valid else '❌ 실패'}")
    
    return is_valid

def reset_user_password(db: Session, email: str, new_password: str):
    """사용자 패스워드 재설정"""
    print(f"\n🔧 패스워드 재설정: {email}")
    print("-" * 50)
    
    user = db.query(User).filter(User.email == email).first()
    if not user:
        print(f"❌ 사용자를 찾을 수 없습니다: {email}")
        return False
    
    # 새 패스워드 해시 생성
    new_hash = get_password_hash(new_password)
    print(f"새 패스워드 해시: {new_hash[:50]}...")
    
    # 데이터베이스 업데이트
    user.password_hash = new_hash
    user.updated_at = datetime.utcnow()
    db.commit()
    
    # 검증
    verification = verify_password(new_password, user.password_hash)
    print(f"패스워드 재설정: {'✅ 성공' if verification else '❌ 실패'}")
    
    return verification

def main():
    """메인 실행 함수"""
    db = next(get_db())
    
    try:
        print("🔐 인증 시스템 디버깅 시작")
        print("=" * 70)
        
        # 테스트 계정들
        test_accounts = [
            {"email": "test@aibio.kr", "password": "admin123"},
            {"email": "taejun@biocom.kr", "password": "admin123"},
            {"email": "admin@aibio.kr", "password": "admin123"},
            {"email": "seungwoo@biocom.kr", "password": "1111"}
        ]
        
        # 1. 현재 패스워드 검증
        print("\n1️⃣ 현재 패스워드 검증")
        working_accounts = []
        
        for account in test_accounts:
            if test_user_authentication(db, account["email"], account["password"]):
                working_accounts.append(account)
        
        if working_accounts:
            print(f"\n✅ 작동하는 계정 {len(working_accounts)}개 발견")
        else:
            print(f"\n❌ 작동하는 계정이 없습니다. 패스워드를 재설정합니다.")
            
            # 2. 첫 번째 계정 패스워드 재설정
            first_account = test_accounts[0]
            if reset_user_password(db, first_account["email"], "admin123"):
                print(f"✅ {first_account['email']} 패스워드 재설정 완료")
                working_accounts.append(first_account)
        
        # 3. 최종 테스트
        if working_accounts:
            print(f"\n3️⃣ 최종 로그인 테스트")
            account = working_accounts[0]
            print(f"테스트 계정: {account['email']} / {account['password']}")
            
            # API 테스트용 curl 명령어 생성
            curl_command = f'''curl -X POST "https://center-production-1421.up.railway.app/api/v1/auth/login" \\
  -H "Content-Type: application/json" \\
  -d '{{"email": "{account["email"]}", "password": "{account["password"]}"}}\''''
            
            print(f"\n📋 테스트 명령어:")
            print(curl_command)
            
        print(f"\n✅ 인증 시스템 디버깅 완료")
        
    except Exception as e:
        logger.error(f"오류 발생: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    main()