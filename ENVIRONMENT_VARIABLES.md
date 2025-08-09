# 환경변수 설정 가이드

## 1. Supabase (데이터베이스)

Supabase 프로젝트 생성 후 다음 정보를 얻습니다:

### Connection String
- Settings → Database → Connection string
- `postgresql://postgres:[YOUR-PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres`

### API Keys
- Settings → API
- `SUPABASE_URL`: https://[PROJECT-REF].supabase.co
- `SUPABASE_ANON_KEY`: 공개 키
- `SUPABASE_SERVICE_ROLE_KEY`: 서비스 키 (백엔드용)

## 2. Railway (백엔드)

Railway 프로젝트에서 다음 환경변수를 설정합니다:

```env
# 데이터베이스
DATABASE_URL=postgresql://postgres:[YOUR-PASSWORD]@db.[PROJECT-REF].supabase.co:6543/postgres?pgbouncer=true

# JWT 인증
JWT_SECRET_KEY=your-super-secure-secret-key-at-least-32-chars
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS 설정
CORS_ORIGINS=https://center-frontend.vercel.app,https://your-custom-domain.com

# 환경 설정
PYTHON_ENV=production
LOG_LEVEL=INFO
LOG_FORMAT=json

# SMS 설정 (선택사항)
SMS_API_KEY=your-sms-api-key
SMS_API_SECRET=your-sms-api-secret
SMS_SENDER=AIBIO

# 이메일 설정 (선택사항)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

### Railway 특수 변수
- `PORT`: Railway가 자동으로 제공 (수정 불가)
- `RAILWAY_ENVIRONMENT`: 환경 이름 (production/staging)

## 3. Vercel (프론트엔드)

Vercel 프로젝트에서 다음 환경변수를 설정합니다:

```env
# API 연결
VITE_API_URL=https://your-app.up.railway.app

# Supabase 연결
VITE_SUPABASE_URL=https://[PROJECT-REF].supabase.co
VITE_SUPABASE_ANON_KEY=your-supabase-anon-key

# 앱 설정
VITE_APP_NAME=AIBIO 센터 관리 시스템
VITE_APP_VERSION=1.0.0
VITE_APP_ENV=production

# 모니터링 (선택사항)
VITE_SENTRY_DSN=https://xxx@xxx.ingest.sentry.io/xxx
VITE_GA_TRACKING_ID=G-XXXXXXXXXX
```

## 4. 로컬 개발 환경

### backend/.env
```env
# 데이터베이스
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/aibio_center

# JWT
JWT_SECRET_KEY=dev-secret-key-for-local-development-only
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# 환경
PYTHON_ENV=development
LOG_LEVEL=DEBUG

# CORS
CORS_ORIGINS=http://localhost:5173,http://localhost:5174
```

### frontend/.env.local
```env
# API
VITE_API_URL=http://localhost:8000

# Supabase (로컬 개발용)
VITE_SUPABASE_URL=http://localhost:54321
VITE_SUPABASE_ANON_KEY=local-development-key

# 환경
VITE_APP_ENV=development
```

## 5. 보안 주의사항

### 절대 하지 말아야 할 것
- ❌ 환경변수를 코드에 하드코딩
- ❌ .env 파일을 git에 커밋
- ❌ 프로덕션 키를 로컬에서 사용
- ❌ 민감한 정보를 로그에 출력

### 반드시 해야 할 것
- ✅ 강력한 JWT_SECRET_KEY 사용 (32자 이상)
- ✅ 환경별로 다른 키 사용
- ✅ 정기적으로 키 로테이션
- ✅ 최소 권한 원칙 적용

## 6. 환경변수 생성 도구

### JWT Secret 생성
```python
import secrets
print(secrets.token_urlsafe(32))
```

### 또는 OpenSSL 사용
```bash
openssl rand -base64 32
```

## 7. 문제 해결

### Railway에서 DATABASE_URL 연결 실패
- Supabase 연결 풀러 사용: `?pgbouncer=true` 추가
- SSL 모드 설정: `?sslmode=require` 추가

### Vercel에서 환경변수 인식 안됨
- 변수명이 `VITE_`로 시작하는지 확인
- 재배포 필요 (환경변수 변경 후)

### CORS 에러
- Railway의 `CORS_ORIGINS`에 Vercel URL 추가
- 쉼표로 구분하여 여러 도메인 추가 가능

---

*이 문서는 배포 시 필요한 모든 환경변수를 정리한 것입니다.*
*각 플랫폼의 대시보드에서 설정하세요.*