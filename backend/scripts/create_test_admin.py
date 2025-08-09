#!/usr/bin/env python3
"""
테스트용 admin 계정 생성 스크립트
Railway에서 직접 실행하거나 로컬에서 실행 가능
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from passlib.context import CryptContext

# bcrypt 설정 (backend의 auth.py와 동일하게)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def generate_password_hash():
    """admin123에 대한 해시 생성"""
    password = "admin123"
    hash_value = pwd_context.hash(password)
    
    print("=== 비밀번호 해시 생성 ===")
    print(f"비밀번호: {password}")
    print(f"해시: {hash_value}")
    print()
    
    # 검증
    is_valid = pwd_context.verify(password, hash_value)
    print(f"검증 결과: {is_valid}")
    print()
    
    # SQL 생성
    print("=== Supabase SQL ===")
    print(f"""
-- 기존 admin 삭제 (선택사항)
DELETE FROM users WHERE email = 'admin@aibio.kr';

-- 새 admin 생성
INSERT INTO users (email, password_hash, name, role, is_active, created_at, updated_at) 
VALUES (
    'admin@aibio.kr',
    '{hash_value}',
    '관리자',
    'admin',
    true,
    NOW(),
    NOW()
);

-- 확인
SELECT user_id, email, name, role, is_active, 
       LENGTH(password_hash) as hash_length,
       LEFT(password_hash, 20) as hash_prefix
FROM users 
WHERE email = 'admin@aibio.kr';
""")

if __name__ == "__main__":
    generate_password_hash()