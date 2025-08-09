#!/usr/bin/env python3
"""
보안 키 생성 도구
배포에 필요한 각종 시크릿 키를 생성합니다.
"""
import secrets
import string
import random

def generate_jwt_secret():
    """JWT용 강력한 시크릿 키 생성"""
    return secrets.token_urlsafe(32)

def generate_db_password():
    """데이터베이스용 안전한 비밀번호 생성"""
    chars = string.ascii_letters + string.digits + "!@#$%^&*"
    # 특수문자 중 URL에 문제될 수 있는 것 제외
    safe_chars = chars.replace('@', '').replace('#', '').replace('&', '')
    return ''.join(secrets.choice(safe_chars) for _ in range(24))

def generate_api_key():
    """API 키 생성"""
    return f"sk-{secrets.token_urlsafe(32)}"

def main():
    print("=" * 60)
    print("🔐 AIBIO 센터 배포용 보안 키 생성기")
    print("=" * 60)
    print()
    
    # JWT Secret
    jwt_secret = generate_jwt_secret()
    print("1️⃣ JWT_SECRET_KEY (Railway에서 사용)")
    print(f"   {jwt_secret}")
    print()
    
    # DB Password
    db_password = generate_db_password()
    print("2️⃣ 데이터베이스 비밀번호 추천 (Supabase에서 사용)")
    print(f"   {db_password}")
    print()
    
    # API Key
    api_key = generate_api_key()
    print("3️⃣ API 키 예시 (향후 외부 API 연동 시)")
    print(f"   {api_key}")
    print()
    
    print("⚠️  주의사항:")
    print("   - 이 키들을 안전한 곳에 저장하세요")
    print("   - 절대 코드에 직접 입력하지 마세요")
    print("   - 환경변수로만 사용하세요")
    print("   - 한번 설정하면 변경이 어려우니 잘 보관하세요")
    print()
    
    # 환경변수 예시 생성
    print("=" * 60)
    print("📋 Railway 환경변수 설정 예시:")
    print("=" * 60)
    print(f"""
DATABASE_URL=postgresql://postgres:{db_password}@db.xxxx.supabase.co:5432/postgres
JWT_SECRET_KEY={jwt_secret}
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
CORS_ORIGINS=https://center-frontend.vercel.app
PYTHON_ENV=production
LOG_LEVEL=INFO
""")

if __name__ == "__main__":
    main()