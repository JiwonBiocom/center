# Supabase 설정 가이드

## 1. 연결 정보 획득

### Database Password
프로젝트 생성 시 설정한 비밀번호를 기억하고 계신가요?

### Connection String 위치
1. Supabase 대시보드에서 **Settings** (왼쪽 메뉴 하단)
2. **Database** 클릭
3. **Connection string** 섹션에서:
   - URI 탭 선택
   - `postgresql://postgres:[YOUR-PASSWORD]@db.wvcxzyvmwwrbjpeuyvuh.supabase.co:5432/postgres` 형태

### API 정보 위치
1. **Settings** → **API**
2. 다음 정보 복사:
   - **Project URL**: `https://wvcxzyvmwwrbjpeuyvuh.supabase.co`
   - **anon public**: `eyJ...` (긴 문자열)
   - **service_role**: `eyJ...` (더 긴 문자열, 백엔드용)

## 2. 데이터베이스 스키마 생성

### SQL Editor 접근
1. 왼쪽 메뉴에서 **SQL Editor** 클릭
2. **New query** 버튼 클릭

### 스키마 실행
1. `/backend/supabase_schema.sql` 파일 내용을 복사
2. SQL Editor에 붙여넣기
3. **Run** 버튼 클릭 (또는 Ctrl/Cmd + Enter)

## 3. 실행 순서

### Step 1: 기존 테이블 확인 (선택사항)
```sql
-- 기존 테이블 목록 확인
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public';
```

### Step 2: 스키마 생성
supabase_schema.sql 내용 전체 실행

### Step 3: 결과 확인
```sql
-- 생성된 테이블 확인
SELECT table_name, 
       (SELECT COUNT(*) FROM information_schema.columns WHERE table_name = t.table_name) as column_count
FROM information_schema.tables t
WHERE table_schema = 'public'
ORDER BY table_name;
```

## 4. Railway 환경변수용 정보

```env
# Supabase Connection (Railway에서 사용)
DATABASE_URL=postgresql://postgres:[YOUR-PASSWORD]@db.wvcxzyvmwwrbjpeuyvuh.supabase.co:6543/postgres?pgbouncer=true&sslmode=require

# Supabase API (프론트엔드에서 사용)
VITE_SUPABASE_URL=https://wvcxzyvmwwrbjpeuyvuh.supabase.co
VITE_SUPABASE_ANON_KEY=[anon key from dashboard]
```

## 5. 주의사항

### Connection Pooling
- Railway에서는 포트 6543 사용 (PgBouncer)
- 직접 연결은 포트 5432 사용

### SSL Mode
- 프로덕션에서는 `sslmode=require` 필수

### Row Level Security
- 현재는 비활성화 상태
- 나중에 필요시 활성화 가능

## 6. 테스트 쿼리

스키마 생성 후 테스트:
```sql
-- 관리자 계정 확인
SELECT * FROM users WHERE email = 'admin@aibio.kr';

-- 서비스 타입 확인
SELECT * FROM service_types;

-- 테이블 개수 확인
SELECT COUNT(*) as table_count 
FROM information_schema.tables 
WHERE table_schema = 'public';
```

예상 결과:
- 관리자 계정 1개
- 서비스 타입 7개
- 전체 테이블 약 20개