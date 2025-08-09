# AIBIO 센터 관리 시스템 배포 가이드

## 배포 아키텍처
- **데이터베이스**: Supabase (PostgreSQL)
- **백엔드 API**: Railway (FastAPI)
- **프론트엔드**: Vercel (React)

## 1. Supabase 설정 (데이터베이스)

### 1.1 프로젝트 생성
1. [Supabase](https://supabase.com) 접속
2. New Project 생성
3. 프로젝트 정보:
   - Name: `aibio-center`
   - Database Password: 안전한 비밀번호 설정
   - Region: `Northeast Asia (Seoul)`

### 1.2 데이터베이스 URL 획득
```
Settings → Database → Connection string → URI
postgresql://postgres:[YOUR-PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres
```

### 1.3 테이블 생성
```bash
# 로컬에서 스키마 확인
cd backend
python scripts/export_schema.py > schema.sql

# Supabase SQL Editor에서 실행
# 또는 scripts/migrate_to_supabase.py 사용
```

## 2. Railway 설정 (백엔드)

### 2.1 프로젝트 생성
1. [Railway](https://railway.app) 접속
2. New Project → Deploy from GitHub repo
3. `biocomvibe/center` 저장소 선택

### 2.2 환경 변수 설정
```env
# Database
DATABASE_URL=postgresql://... (Supabase URL)

# Security
JWT_SECRET_KEY=your-secure-secret-key
JWT_ALGORITHM=HS256

# CORS
CORS_ORIGINS=https://center-frontend.vercel.app

# Environment
PYTHON_ENV=production
```

### 2.3 배포 설정
```toml
# railway.toml 생성
[build]
builder = "NIXPACKS"

[deploy]
startCommand = "cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT"

[healthcheck]
path = "/health"
```

### 2.4 도메인 설정
- Railway가 자동으로 제공하는 도메인 사용
- 예: `aibio-center-api.up.railway.app`

## 3. Vercel 설정 (프론트엔드)

### 3.1 프로젝트 연결
1. [Vercel](https://vercel.com) 접속
2. Import Git Repository
3. `biocomvibe/center` 저장소 선택

### 3.2 빌드 설정
```json
{
  "buildCommand": "cd frontend && npm run build",
  "outputDirectory": "frontend/dist",
  "installCommand": "cd frontend && npm install"
}
```

### 3.3 환경 변수 설정
```env
VITE_API_URL=https://aibio-center-api.up.railway.app
VITE_SUPABASE_URL=https://[PROJECT-REF].supabase.co
VITE_SUPABASE_ANON_KEY=your-anon-key
```

### 3.4 도메인 설정
- 기본: `center-frontend.vercel.app`
- 커스텀 도메인 추가 가능

## 4. 배포 체크리스트

### 백엔드 (Railway)
- [ ] 환경 변수 모두 설정됨
- [ ] Health check 통과 (`/health`)
- [ ] API 문서 접근 가능 (`/docs`)
- [ ] CORS 설정 확인

### 프론트엔드 (Vercel)
- [ ] 빌드 성공
- [ ] 환경 변수 설정됨
- [ ] API 연결 테스트
- [ ] 로그인 기능 작동

### 데이터베이스 (Supabase)
- [ ] 테이블 생성 완료
- [ ] 초기 데이터 입력
- [ ] 백업 설정
- [ ] Row Level Security 검토

## 5. 배포 후 작업

### 5.1 초기 데이터 설정
```bash
# Admin 계정 생성
python backend/scripts/create_admin.py

# 기본 서비스 타입 생성
python backend/scripts/init_service_types.py
```

### 5.2 모니터링 설정
- Railway: Metrics 탭에서 CPU/Memory 모니터링
- Vercel: Analytics 활성화
- Supabase: Database 모니터링

### 5.3 백업 전략
- Supabase: 자동 백업 (매일)
- 추가 백업: `scripts/backup_database.py` 주기적 실행

## 6. 비용 예상 (월)

### 무료 티어
- **Supabase**: 500MB DB, 2GB 전송
- **Vercel**: 100GB 대역폭
- **Railway**: $5 크레딧

### 유료 전환 시점
- 고객 5,000명 이상
- 월간 방문자 10,000명 이상
- 데이터베이스 500MB 초과

### 예상 월 비용 (소규모)
- Supabase Pro: $25
- Railway: $5-20
- Vercel Pro: $20
- **총: $50-65/월**

## 7. 트러블슈팅

### CORS 에러
```python
# backend/main.py
CORS_ORIGINS 환경변수에 프론트엔드 URL 추가
```

### 데이터베이스 연결 실패
```bash
# Railway 로그 확인
railway logs

# SSL 설정 추가
DATABASE_URL에 ?sslmode=require 추가
```

### 빌드 실패
```bash
# package.json 버전 확인
"engines": {
  "node": ">=20.0.0"
}
```

## 8. 롤백 전략

### 긴급 롤백
1. Vercel: 이전 배포로 즉시 롤백
2. Railway: 이전 커밋으로 재배포
3. Supabase: Point-in-time 복구

### 안전한 배포
1. Staging 환경 먼저 배포
2. 프로덕션 배포는 업무 시간 외
3. 배포 전 데이터베이스 백업

---

*작성일: 2025-06-20*
*작성자: 헤파이스토스 (Claude Code)*