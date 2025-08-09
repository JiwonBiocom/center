# AIBIO 센터 관리 시스템 - 핵심 개발 가이드

> 📌 이 문서는 프로젝트별 규칙입니다.
> 글로벌 개발 원칙은 [글로벌 CLAUDE.md](../CLAUDE.md)를 먼저 참조하세요.
> 적용 우선순위: 글로벌 → 프로젝트 → 기술별 규칙
>
> 이 문서는 Claude Code가 참조하는 핵심 개발 원칙입니다.
> 상세 내용은 [CLAUDE_EXTENDED.md](./CLAUDE_EXTENDED.md)를 참조하세요.

## 📋 빠른 참조
- **상세 가이드**: [CLAUDE_EXTENDED.md](./CLAUDE_EXTENDED.md)
- **인프라 구성**: [docs/INFRASTRUCTURE.md](./docs/INFRASTRUCTURE.md) 🔥 **필수 확인**
- **데이터베이스**: [docs/database-schema.md](./docs/database-schema.md)
- **API 문서**: [docs/API_DOCUMENTATION.md](./docs/API_DOCUMENTATION.md)
- **시스템 구조**: [docs/system-overview.md](./docs/system-overview.md)

## 프로젝트 개요
이 문서는 AIBIO 센터 관리 시스템 개발 시 준수해야 할 모든 원칙과 규칙을 정의합니다.

## 핵심 개발 원칙

### 1. 구현 작업 원칙
- **테스트 우선 개발**: 비즈니스 로직 구현 시 반드시 테스트를 먼저 작성
- **아키텍처 원칙**: SOLID 원칙과 Clean Architecture 준수
- **문서화 우선**: 코딩 시작 전 PRD(설계 문서) 작성 및 합의 필수
- **언어 규칙**: AWS 리소스 Description은 영문으로 작성

### 2. 코드 품질 원칙
- **단순성**: 복잡한 솔루션보다 가장 단순한 솔루션 우선
- **DRY 원칙**: 코드 중복 방지, 기존 기능 재사용
- **가드레일**: 테스트 외 환경에서 모의 데이터 사용 금지
- **효율성**: 명확성을 유지하면서 토큰 사용 최적화

### 3. 개발 프로세스

#### 문제 발생 시 대응 프로세스
1. **문제 감지**: 개발 규칙 위반, 예상치 못한 에러, 기대와 다른 결과
2. **해결 시도**: 5-10분 내 즉시 해결 시도
3. **원인 분석**: 근본 원인 파악, 영향 범위 분석
4. **문제 분석 레포트 작성**: 문제 설명, 시도한 방법, 근본 원인, 영향 범위, 권장 조치
5. **사용자 확인 요청**: 해결 또는 우회 방안 결정

#### 작업 자율성 가이드라인
**확인 없이 진행할 작업**:
- 일반적인 bash 명령어 (ls, cat, grep, curl 등)
- 테스트 스크립트 실행
- 서버 시작/재시작
- 프로세스 관리
- 로그 확인 및 디버깅
- API 테스트 (curl)

**반드시 확인이 필요한 작업**:
- 데이터베이스 스키마 변경
- 프로덕션 데이터 삭제/수정
- 환경 변수나 설정 파일 변경
- 대규모 리팩토링 (10개 이상 파일)
- git push 또는 배포 관련 작업

## 기술 스택 요구사항

### 핵심 기술
- **백엔드**: FastAPI (Python 3.12)
- **프론트엔드**: React 19, TypeScript 5.4+
- **데이터베이스**: PostgreSQL 17
- **런타임**: Node.js 20 LTS

### 배포 및 플랫폼
- **테스트 배포**: Vercel
- **메인 플랫폼**: Supabase
- **개발 환경**: Cursor with MCP 도구, Claude Code 이용

## 절대 규칙
1. 기존 작동 코드는 수정 전 백업
2. 한 번에 하나의 파일만 수정
3. 수정 후 반드시 테스트 실행
4. 에러 발생 시 즉시 롤백

## 프로젝트 구조 규칙
- /components: UI 컴포넌트만
- /lib: 비즈니스 로직
- /api: API 라우트만
- 폴더 간 의존성은 단방향

## 금지 사항
- 테스트 없는 비즈니스 로직 구현
- 하드코딩된 에러 fallback
- `--no-verify` 옵션 사용
- 문서화 없는 아키텍처 변경
- 프로덕션 환경에서의 모의 데이터 사용
- 전체 리팩토링 금지
- 미사용 라이브러리 추가 금지
- 복잡한 추상화 금지

## 데이터베이스 보호 원칙

### 위험한 작업 방지
- **절대 금지**: `drop_all()`, `TRUNCATE`, `DROP TABLE` 명령
- **init_db.py 사용 금지**: 모든 데이터를 삭제할 수 있음
- **대안 사용**: 테이블 생성만 필요한 경우 `create_all()` 사용

### 안전한 개발 방법
1. **테이블 생성**: `scripts/safe_create_tables.py` 사용
2. **마이그레이션**: Alembic 같은 마이그레이션 도구 사용
3. **환경 변수 설정**: `.env`에 `ENVIRONMENT=production` 추가
4. **백업 우선**: 중요한 작업 전 반드시 백업 실행

## 데이터베이스 스키마 작업 규칙

### 필수 확인 사항
1. **스키마 확인 우선**: DB 작업 전 반드시 실제 테이블 구조 확인
2. **가정 금지**: 테이블명, 컬럼명을 추측하지 말고 반드시 확인
3. **스키마 문서화**: 변경 시 즉시 `/docs/database-schema.md` 업데이트

### 스키마 확인 도구
```bash
# 모든 테이블 목록 보기
python scripts/check_schema.py --list

# 특정 테이블 구조 확인
python scripts/check_schema.py --table payments

# 특정 컬럼 존재 여부 확인
python scripts/check_schema.py --column payments.payment_status
```

### 에러 예방 체크리스트
- [ ] 사용할 테이블이 실제로 존재하는가?
- [ ] 사용할 컬럼명이 정확한가?
- [ ] 컬럼 타입이 예상과 일치하는가?
- [ ] Foreign Key 관계가 올바른가?

## 🆕 배포 전 스키마 검증 (필수!)

### Enum 타입 검증
```bash
# 배포 전 반드시 실행
python scripts/check_enum_values.py
```
- **membership_level**: `basic`, `silver`, `gold`, `platinum`, `vip`
- **customer_status**: `active`, `inactive`, `dormant`
- DB와 코드의 enum 값이 하나라도 다르면 **500 에러 발생!**

### API 경로 검증
```bash
python scripts/check_api_routes.py
```
- FastAPI `redirect_slashes=False` 설정 확인
- 프론트엔드와 백엔드 경로 일치 확인

## 데이터 관리 원칙
- **실제 데이터 우선**: 실제 데이터로 테스트
- **샘플 데이터 생성 규칙**: 사용자 동의 필수
- **데이터 추가 후 검증**: API 테스트로 정상 작동 확인

## 우선순위 가이드
1. **코드 동작의 정확성**
2. **테스트 커버리지**
3. **코드 단순성**
4. **성능 최적화**

## CLAUDE.md 파일 구조

### 프로젝트 내 CLAUDE.md 배치
```
center/
├── CLAUDE.md                 # 전체 프로젝트 공통 원칙 (이 파일)
├── backend/
│   └── CLAUDE.md            # 백엔드 특화 규칙 (FastAPI, Python)
└── frontend/
    └── CLAUDE.md            # 프론트엔드 특화 규칙 (React, TypeScript)
```

### 참조 방식
- 루트에서 작업: 루트 CLAUDE.md만 참조
- `/backend`에서 작업: 루트 + backend/CLAUDE.md 모두 참조
- `/frontend`에서 작업: 루트 + frontend/CLAUDE.md 모두 참조

### 작성 원칙
- **루트 CLAUDE.md**: 프로젝트 전체 공통 원칙, 금지사항
- **서브폴더 CLAUDE.md**: 해당 기술 스택 특화 규칙만 작성
- 중복 내용은 루트에만 작성하고 서브폴더에서는 참조

## 관련 문서

### 필수 참조 문서
- [CLAUDE_EXTENDED.md](./CLAUDE_EXTENDED.md) - 서버 실행, Bash 규칙, 코드 작성 상세 가이드
- [데이터베이스 스키마](./docs/database-schema.md) - 최신 DB 구조
- [API 문서](./docs/API_DOCUMENTATION.md) - API 엔드포인트 명세
- [시스템 구조](./docs/system-overview.md) - 전체 아키텍처

### 추가 참조 문서
- [개발자 가이드](./DEVELOPER_GUIDE.md) - 신규 개발자용 안내서
- [backend/CLAUDE.md](./backend/CLAUDE.md) - 백엔드 특화 규칙
- [frontend/CLAUDE.md](./frontend/CLAUDE.md) - 프론트엔드 특화 규칙
- [테스트 규칙](./docs/TEST_RULES.md) - 🧪 테스트 및 콘솔 체크 가이드라인
- [배포 체크리스트](./docs/deployment-checklist.md) - 🚨 스키마 드리프트 방지 가이드
- [스키마 동기화 자동화](./docs/schema-sync-automation.md) - 🤖 AI 기반 자동화 솔루션

## MCP (Model Context Protocol) 설정

MCP 설정 및 사용법에 대한 자세한 내용은 다음 문서를 참조하세요:

📖 **[MCP 가이드](./coding/mcp.md)** - Browser MCP, Notion MCP 등 모든 MCP 서버 설정 및 사용법

---

*이 문서는 프로젝트의 핵심 개발 원칙입니다. 300줄 이내로 유지됩니다.*
*상세 내용은 CLAUDE_EXTENDED.md를 참조하세요.*
*최종 업데이트: 2025-06-08*
