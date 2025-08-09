# AIBIO 센터 관리 시스템

엑셀 기반 고객 관리를 웹 기반 데이터베이스 시스템으로 전환하는 프로젝트입니다.

## 프로젝트 구조

```
center/
├── docs/               # 프로젝트 문서
│   ├── prd.md         # 제품 요구사항 정의서
│   ├── features.md    # 기능 명세서
│   └── adr/           # 아키텍처 결정 기록
├── backend/           # FastAPI 백엔드
├── frontend/          # React 프론트엔드
├── scripts/           # 유틸리티 스크립트
└── README.md          # 프로젝트 개요
```

## 기술 스택

- **백엔드**: FastAPI (Python 3.12)
- **프론트엔드**: React 19, TypeScript 5.4+
- **데이터베이스**: PostgreSQL 17 (Supabase)
- **스타일링**: Tailwind CSS, shadcn/ui
- **배포**: Vercel, Supabase

## 시작하기

### 사전 요구사항

- Node.js 20 LTS
- Python 3.12+
- Git

### 환경 설정

1. 환경 변수 설정
```bash
cp .env.example .env
# .env 파일을 열어 Supabase 정보 입력
```

2. 백엔드 설정
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. 프론트엔드 설정
```bash
cd frontend
npm install
```

### 개발 서버 실행

백엔드:
```bash
cd backend
uvicorn main:app --reload
```

프론트엔드:
```bash
cd frontend
npm run dev
```

## 프로젝트 문서

- [제품 요구사항 정의서 (PRD)](./docs/prd.md)
- [기능 명세서](./docs/features.md)
- [기술 스택 상세](./docs/tech-stack.md)
- [시스템 구조](./docs/system-overview.md)
- [데이터 플로우](./docs/data-flow.md)

## 개발 가이드라인

[CLAUDE.md](../CLAUDE.md) 파일의 가이드라인을 준수합니다.

## 라이선스

Private
