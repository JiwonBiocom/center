# Claude Code 팀 온보딩 가이드

## 1. Claude Code 설치
```bash
npm install -g @anthropic-ai/claude-code
```

## 2. 필수 CLAUDE.md 위치
- `~/.claude/CLAUDE.md` - 글로벌 설정 (아래 내용 복사)
- `./CLAUDE.md` - 프로젝트 규칙 (이미 있음)
- `./backend/CLAUDE.md` - 백엔드 규칙 (이미 있음)
- `./frontend/CLAUDE.md` - 프론트엔드 규칙 (이미 있음)

## 3. 글로벌 CLAUDE.md 내용
```markdown
# 🤖 Claude Code 프로젝트 가이드라인 v1.1
[~/coding/CLAUDE.md 내용을 여기에 복사]
```

## 4. 프로젝트 설정
```bash
# 1. 프로젝트 클론
git clone [repository-url] ~/coding/center
cd ~/coding/center

# 2. Backend 설정
cd backend
cp .env.example .env
# .env 파일 수정 필요
pip install -r requirements.txt

# 3. Frontend 설정  
cd ../frontend
npm install

# 4. 데이터베이스 설정
# PostgreSQL 설치 후 다음 정보로 DB 생성
# DB명: aibio_center
# 사용자: aibio_user
# 비밀번호: aibio_password
```

## 5. Claude Code 실행
```bash
# 프로젝트 루트에서
cd ~/coding/center
claude-code

# 첫 명령어
"center 프로젝트 로컬 서버 띄워줘"
```

## 6. 주요 파일 구조
```
center/
├── CLAUDE.md                 # 프로젝트 공통 규칙
├── backend/
│   ├── CLAUDE.md            # 백엔드 규칙
│   ├── main.py              # FastAPI 앱
│   └── .env.example         # 환경변수 템플릿
└── frontend/
    ├── CLAUDE.md            # 프론트엔드 규칙
    └── package.json         # 의존성
```

## 7. 필수 문서 위치
- 시스템 구조: `docs/system-overview.md`
- DB 스키마: `docs/database-schema.md`
- API 문서: `docs/API_DOCUMENTATION.md`

## 8. 테스트 계정
- 이메일: test@aibio.kr
- 비밀번호: test1234

---
*이 문서 하나로 Claude Code 개발을 시작할 수 있습니다.*