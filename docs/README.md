# 📚 AIBIO Center Documentation

> 이 디렉토리는 AIBIO 센터 관리 시스템의 상세 문서를 담고 있습니다.
> 핵심 개발 원칙은 [프로젝트 CLAUDE.md](../CLAUDE.md)를 참조하세요.

## 🚀 신규 개발자가 먼저 읽을 문서
1. **[개발자 가이드](../DEVELOPER_GUIDE.md)** - 프로젝트 시작하기
2. **[개발 규칙](development-rules.md)** - 코딩 표준과 규칙 🆕
3. **[Vibe 코딩 가이드](vibe-coding-guide.md)** - 팀 문화와 협업 스타일 ✨
4. **[시스템 구조](system-overview.md)** - 전체 아키텍처 이해

## 📋 문서 목록

### 🏗️ 시스템 아키텍처
- [시스템 개요](./system-overview.md) - 전체 시스템 구조 및 컴포넌트
- [데이터베이스 스키마](./database-schema.md) - 테이블 구조 및 관계
- [API 문서](./API_DOCUMENTATION.md) - REST API 엔드포인트 명세
- [인프라 구성](./INFRASTRUCTURE.md) - 배포 환경 및 서비스 구성

### 🛠️ 개발 가이드
- [개발 규칙](./development-rules.md) 🆕 - 프로젝트 전체 개발 규칙
- [Vibe 코딩 가이드](./vibe-coding-guide.md) ✨ - 팀 문화와 커밋 스타일
- [테스트 전략](./test-strategy.md) 🆕 - 테스트 피라미드 및 전략
- [API Routing Style Guide](./api-routing-style.md) - FastAPI trailing slash 정책
<!-- - [리팩토링 가이드](./refactoring-guide.md) - 코드 리팩토링 모범 사례 - 파일 없음 -->
- [테스트 규칙](./TEST_RULES.md) - 테스트 작성 및 실행 가이드
<!-- - [Git Workflow](./git-workflow.md) 🆕 - 브랜치 전략 및 커밋 규칙 - 파일 없음 -->

### 🚀 배포 및 운영
- [배포 체크리스트](./deployment-checklist.md) - 프로덕션 배포 전 확인사항
- [스키마 동기화 자동화](./schema-sync-automation.md) - DB 스키마 드리프트 방지

### 🔗 통합 가이드
- [카카오 알림톡 연동](./kakao-integration-guide.md) - 카카오 비즈니스 API 설정
- [SMS 연동 가이드](./sms-integration-guide.md) - 알리고 SMS API 설정
- [Gmail 설정 가이드](./gmail-setup-guide.md) - 이메일 발송 설정
- [MCP Gmail 설정](./mcp-gmail-setup-guide.md) - MCP 서버 Gmail 연동

### 📱 프론트엔드
- [모바일 구현 가이드](./mobile-implementation-guide.md) - 반응형 UI 구현

### 📊 데이터 관리
- [데이터 시딩 가이드](./data-seeding-guide.md) - 초기 데이터 설정

## 🔍 빠른 참조

### 최근 업데이트 (2025-06)
1. **Trailing Slash 정책** - POST/PUT/PATCH 엔드포인트 처리 ([api-routing-style.md](./api-routing-style.md))
2. **Enum 동기화** - DB와 코드의 enum 값 일치 ([deployment-checklist.md](./deployment-checklist.md))
3. **스키마 드리프트 방지** - 자동화된 검증 프로세스 ([schema-sync-automation.md](./schema-sync-automation.md))

### 자주 참조하는 문서
- 새로운 API 엔드포인트 추가 시 → [api-routing-style.md](./api-routing-style.md)
- 배포 전 체크 → [deployment-checklist.md](./deployment-checklist.md)
- 테스트 작성 → [TEST_RULES.md](./TEST_RULES.md)
- DB 스키마 변경 → [database-schema.md](./database-schema.md)

## 📝 문서 작성 규칙

1. **파일명**: 소문자와 하이픈 사용 (예: `api-routing-style.md`)
2. **구조**: 목차, 개요, 상세 내용, 예시, 참조 순서
3. **업데이트**: 변경 시 날짜와 버전 명시
4. **링크**: 상대 경로 사용, 외부 링크는 명확히 표시

## 🤝 기여 방법

1. 새 문서 추가 시 이 README.md 업데이트
2. 기존 문서 수정 시 버전과 날짜 갱신
3. 중복 내용은 링크로 대체
4. 300줄 이상의 문서는 섹션 분할 고려

---

*이 문서는 2025-06-22 업데이트되었습니다.*
