# ADR-001: 기술 스택 선택

## 상태
승인됨 (2025-06-03)

## 컨텍스트
AIBIO 센터 관리 시스템을 구축하기 위해 적절한 기술 스택을 선택해야 합니다. 현재 엑셀로 관리되는 데이터를 웹 기반 시스템으로 전환하며, 다음 요구사항을 충족해야 합니다:

- 약 1,000명의 고객 데이터 관리
- 실시간 데이터 조회 및 업데이트
- 다중 사용자 동시 접속 (10명 이상)
- 빠른 개발 및 배포
- 확장 가능한 아키텍처

## 결정

다음 기술 스택을 채택합니다:

### 백엔드
- **FastAPI** (Python 3.12)
  - 이유: 높은 성능, 자동 API 문서화, 타입 안정성
  - 대안: Django, Flask, Express.js

### 데이터베이스
- **PostgreSQL 17** + **Supabase**
  - 이유: 엔터프라이즈급 안정성, 실시간 기능, 자동 백업
  - 대안: MySQL, MongoDB, Firebase

### 프론트엔드
- **React 19** + **TypeScript 5.4+**
  - 이유: 최신 기능, 타입 안정성, 큰 생태계
  - 대안: Vue.js, Angular, Svelte

### 스타일링
- **Tailwind CSS** + **shadcn/ui**
  - 이유: 빠른 개발, 일관된 디자인, 커스터마이징 용이
  - 대안: Material-UI, Ant Design, Bootstrap

### 상태 관리
- **Zustand** + **React Query**
  - 이유: 간단한 API, 적은 보일러플레이트, 서버 상태 관리
  - 대안: Redux, MobX, Recoil

### 배포
- **Vercel** (프론트엔드) + **Supabase** (백엔드)
  - 이유: 간편한 배포, 자동 스케일링, 통합 환경
  - 대안: AWS, Google Cloud, Netlify

## 결과

### 긍정적 결과
- 빠른 개발 속도 (2개월 내 MVP 가능)
- 낮은 운영 비용 (Supabase 무료 티어 활용)
- 실시간 기능 내장
- 자동 백업 및 복구
- 타입 안정성으로 버그 감소
- 우수한 개발자 경험

### 부정적 결과
- Python/JavaScript 두 언어 관리 필요
- Supabase 종속성
- 새로운 기술 학습 곡선

### 위험 완화
- Supabase는 오픈소스이므로 필요시 자체 호스팅 가능
- 데이터 정기 백업으로 벤더 종속성 완화
- 팀 교육 계획 수립

## 참고 자료
- [FastAPI 공식 문서](https://fastapi.tiangolo.com/)
- [Supabase 공식 문서](https://supabase.com/docs)
- [React 19 릴리즈 노트](https://react.dev/blog)
- [CLAUDE.md 기술 스택 요구사항](../../../CLAUDE.md)
