# 🚀 빠른 시작 가이드 - Claude Code 재시작 시

> 이 문서는 Claude Code를 재시작했을 때 빠르게 환경을 설정하는 가이드입니다.

## 1️⃣ 환경 설정 (1분)

```bash
# Playwright 설치 (테스트 도구)
pip install playwright aiohttp
playwright install chromium
```

## 2️⃣ 현재 시스템 확인 (30초)

```bash
# 백엔드 상태 확인
curl https://center-production-1421.up.railway.app/health

# 프론트엔드 콘솔 체크
python scripts/quick_console_check.py https://center-ten.vercel.app
```

## 3️⃣ 로그인 테스트 (1분)

```bash
# 자동 로그인 테스트
python scripts/test_login_flow.py
```

### 테스트 계정
- Email: `admin@aibio.com`
- Password: `admin123`

## 4️⃣ 주요 URL

| 서비스 | URL | 용도 |
|-------|-----|------|
| 프론트엔드 | https://center-ten.vercel.app | 메인 사이트 |
| 백엔드 API | https://center-production-1421.up.railway.app | API 서버 |
| API 문서 | https://center-production-1421.up.railway.app/docs | Swagger UI |
| Supabase | Supabase Dashboard | 데이터베이스 관리 |

## 5️⃣ 문제 발생 시 체크리스트

### API 500 에러
1. 스키마 확인: `scripts/quick_fix_schema.py`
2. Railway 로그: `railway logs -f`

### 로그인 안 됨
1. 환경 변수 확인 (Vercel Dashboard)
2. CORS 설정 확인 (backend/main.py)

### 콘솔 에러
```bash
python scripts/check_railway_console.py https://center-ten.vercel.app
```

## 6️⃣ 자주 사용하는 스크립트

```bash
# 스키마 수정 SQL 생성
python scripts/quick_fix_schema.py

# 전체 시스템 진단
python scripts/check_full_system.py

# API 호출 패턴 확인
python scripts/check_frontend_api.py
```

## 📌 중요 파일 위치

- 진행 상황: `PROGRESS_REPORT_20250621.md`
- 배포 가이드: `docs/deployment-checklist.md`
- 자동화 가이드: `docs/schema-sync-automation.md`
- 백엔드 설정: `backend/main.py`
- 프론트엔드 API: `frontend/src/lib/api.ts`

---

*빠른 참조를 위한 가이드입니다. 상세 내용은 PROGRESS_REPORT를 참조하세요.*