# 인프라 구성 정보

> **중요**: 이 문서는 시스템의 실제 인프라 구성을 명시합니다.
> 개발/배포 시 반드시 참조하세요.

## 현재 인프라 구성 (2025-06-21 기준)

### 🗃️ 데이터베이스
- **운영 환경**: Supabase PostgreSQL
  - 프로젝트 URL: https://supabase.com/dashboard/project/wvcxzyvmwwrbjpeuyvuh
  - PostgreSQL 17
  - 918명의 고객 데이터 보유
  
- **개발 환경**: 로컬 PostgreSQL
  - `DATABASE_URL=postgresql://aibio_user:aibio_password@localhost:5432/aibio_center`

### 🚀 배포 환경
- **프론트엔드**: Vercel
  - URL: https://center-ten.vercel.app
  - 자동 배포: GitHub main 브랜치
  
- **백엔드**: Railway
  - URL: https://center-production-1421.up.railway.app
  - 자동 배포: GitHub main 브랜치
  - DATABASE_URL은 Supabase 연결 문자열 사용

### 🔧 환경 변수 관리
```
개발 환경 (.env):
- DATABASE_URL: localhost PostgreSQL
- SUPABASE_*: 설정되어 있지만 미사용

운영 환경 (Railway):
- DATABASE_URL: Supabase PostgreSQL 연결 문자열
- 기타 프로덕션 환경 변수들
```

### 📊 데이터 마이그레이션 방법

#### Supabase SQL Editor 사용 (권장)
1. https://supabase.com/dashboard/project/wvcxzyvmwwrbjpeuyvuh
2. SQL Editor → New query
3. 마이그레이션 SQL 실행

#### Python 스크립트 사용
```bash
# Supabase DATABASE_URL로 실행
python scripts/apply_migration.py "postgresql://[supabase-connection-string]"
```

### ⚠️ 주의사항
1. **개발과 운영 DB가 분리되어 있음**
   - 로컬 테스트는 localhost DB
   - 운영 데이터는 Supabase DB
   
2. **스키마 변경 시 두 곳 모두 적용 필요**
   - 개발: 로컬 PostgreSQL
   - 운영: Supabase PostgreSQL
   
3. **Railway는 백엔드 애플리케이션만 호스팅**
   - 데이터베이스 서비스는 제공하지 않음
   - Supabase가 DB 역할

### 🔍 인프라 확인 명령어
```bash
# API 응답 확인 (운영 환경)
curl https://center-production-1421.up.railway.app/api/v1/customers/count

# 로컬 환경 확인
python scripts/check_customer_nulls.py
```

---

**최종 업데이트**: 2025-06-21  
**확인된 이슈**: Customer NULL 값으로 인한 500 에러 → Pydantic 스키마 수정으로 해결