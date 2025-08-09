# AIBIO 센터 관리 시스템 - 기술 스택 선택 및 설명

## 1. 개요

본 문서는 AIBIO 센터 관리 시스템 구축에 사용될 기술 스택의 선택 근거와 상세 설명을 담고 있습니다.

## 2. 핵심 기술 스택

### 2.1 백엔드

#### FastAPI (Python 3.12)
**선택 이유:**
- 높은 성능과 비동기 처리 지원
- 자동 API 문서화 (Swagger/OpenAPI)
- 타입 힌트를 통한 안정성
- Pydantic을 통한 데이터 검증
- 빠른 개발 속도

**주요 라이브러리:**
```python
fastapi==0.115.0
uvicorn==0.32.0
pydantic==2.10.0
sqlalchemy==2.0.36
alembic==1.14.0
python-jose==3.3.0
passlib==1.7.4
python-multipart==0.0.15
```

### 2.2 데이터베이스

#### PostgreSQL 17 + Supabase
**선택 이유:**
- 엔터프라이즈급 안정성
- JSON 지원으로 유연한 스키마
- 풀텍스트 검색 기능
- Supabase의 실시간 구독 기능
- 자동 백업 및 복구
- Row Level Security (RLS)

**Supabase 추가 기능:**
- 인증 시스템 내장
- 실시간 데이터 동기화
- 스토리지 서비스
- Edge Functions

### 2.3 프론트엔드

#### React 19 + TypeScript 5.4+
**선택 이유:**
- 최신 React 기능 활용 (Suspense, Error Boundaries)
- TypeScript를 통한 타입 안정성
- 대규모 커뮤니티와 생태계
- 컴포넌트 기반 아키텍처

**주요 라이브러리:**
```json
{
  "react": "^19.0.0",
  "typescript": "^5.4.0",
  "@tanstack/react-query": "^5.62.0",
  "react-router-dom": "^7.0.0",
  "zustand": "^4.5.0",
  "@supabase/supabase-js": "^2.47.0",
  "react-hook-form": "^7.54.0",
  "zod": "^3.24.0"
}
```

### 2.4 스타일링

#### Tailwind CSS + shadcn/ui
**선택 이유:**
- 유틸리티 퍼스트 접근법
- 빠른 프로토타이핑
- 일관된 디자인 시스템
- shadcn/ui의 고품질 컴포넌트
- 다크 모드 지원

### 2.5 상태 관리

#### Zustand + React Query
**선택 이유:**
- Zustand: 간단한 전역 상태 관리
- React Query: 서버 상태 관리 및 캐싱
- 보일러플레이트 최소화
- DevTools 지원

## 3. 개발 도구

### 3.1 개발 환경
- **IDE**: Cursor with Claude Code
- **버전 관리**: Git + GitHub
- **패키지 매니저**: pnpm (프론트엔드), pip (백엔드)
- **코드 포맷터**: Prettier, Black
- **린터**: ESLint, Ruff

### 3.2 테스트 도구
- **백엔드**: pytest, pytest-asyncio
- **프론트엔드**: Vitest, React Testing Library
- **E2E 테스트**: Playwright

### 3.3 CI/CD
- **GitHub Actions**: 자동 테스트 및 배포
- **Vercel**: 프론트엔드 배포
- **Supabase**: 백엔드 및 데이터베이스

## 4. 아키텍처 패턴

### 4.1 백엔드 아키텍처
```
src/
├── api/              # API 엔드포인트
│   ├── v1/
│   │   ├── customers.py
│   │   ├── services.py
│   │   └── payments.py
├── core/             # 핵심 설정
│   ├── config.py
│   ├── security.py
│   └── database.py
├── models/           # 데이터베이스 모델
├── schemas/          # Pydantic 스키마
├── services/         # 비즈니스 로직
└── utils/            # 유틸리티 함수
```

### 4.2 프론트엔드 아키텍처
```
src/
├── components/       # 재사용 가능한 컴포넌트
│   ├── ui/          # shadcn/ui 컴포넌트
│   └── features/    # 기능별 컴포넌트
├── pages/           # 페이지 컴포넌트
├── hooks/           # 커스텀 훅
├── services/        # API 서비스
├── stores/          # Zustand 스토어
├── types/           # TypeScript 타입
└── utils/           # 유틸리티 함수
```

## 5. 보안 고려사항

### 5.1 인증 및 권한
- **JWT 토큰 기반 인증**
- **역할 기반 접근 제어 (RBAC)**
- **Supabase Row Level Security**
- **API Rate Limiting**

### 5.2 데이터 보안
- **HTTPS 통신**
- **민감 정보 암호화**
- **SQL Injection 방지**
- **XSS/CSRF 방지**

## 6. 성능 최적화

### 6.1 백엔드
- **비동기 처리**
- **데이터베이스 인덱싱**
- **쿼리 최적화**
- **Redis 캐싱 (필요시)**

### 6.2 프론트엔드
- **코드 스플리팅**
- **이미지 최적화**
- **React Query 캐싱**
- **가상 스크롤링**

## 7. 모니터링 및 로깅

### 7.1 모니터링
- **Supabase Dashboard**
- **Vercel Analytics**
- **Sentry (에러 트래킹)**

### 7.2 로깅
- **구조화된 로깅**
- **로그 레벨 관리**
- **감사 로그**

## 8. 확장성 고려사항

### 8.1 수평적 확장
- **Supabase Edge Functions**
- **CDN 활용**
- **로드 밸런싱**

### 8.2 수직적 확장
- **데이터베이스 파티셔닝**
- **읽기 전용 복제본**
- **캐싱 레이어**

## 9. 개발 로드맵과의 연계

### Phase 1: 기반 구축
- Supabase 프로젝트 설정
- 데이터베이스 스키마 구현
- FastAPI 기본 구조
- React 프로젝트 초기화

### Phase 2: 핵심 기능
- CRUD API 구현
- 인증 시스템 구축
- 기본 UI 컴포넌트
- 데이터 마이그레이션

### Phase 3: 고급 기능
- 실시간 기능 구현
- 대시보드 개발
- 성능 최적화
- 모니터링 설정

### Phase 4: 배포 및 운영
- 프로덕션 배포
- 사용자 교육
- 피드백 반영
- 지속적 개선