# CLAUDE.md 확장 문서

> 📌 이 문서는 프로젝트별 상세 규칙입니다.
> 글로벌 개발 원칙은 [글로벌 CLAUDE.md](../CLAUDE.md)를 먼저 참조하세요.
> 프로젝트 핵심 원칙은 [CLAUDE.md](./CLAUDE.md)를 참조하세요.
> 적용 우선순위: 글로벌 → 프로젝트 → 상세 규칙
>
> 이 문서는 CLAUDE.md의 상세 내용을 담고 있습니다.
> CLAUDE.md는 핵심 원칙만 담고, 상세 내용은 이 문서를 참조하세요.

## 프로젝트 시작하기

### 1. 환경 설정 (최초 1회)
```bash
# 백엔드 환경 설정
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 프론트엔드 환경 설정
cd frontend
npm install
```

### 2. 서버 실행

#### 자동 실행 스크립트 (권장)
```bash
# 프로젝트 루트에서
./start-servers.sh
```

#### 수동 실행

**백엔드 서버 (터미널 1)**
```bash
cd backend
source venv/bin/activate  # 가상환경 활성화
python main.py
# 또는
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**프론트엔드 서버 (터미널 2)**
```bash
cd frontend
npm run dev
```

#### 백그라운드 실행 (Claude Code 환경)
```bash
# 백엔드
cd backend && python main.py > backend.log 2>&1 &

# 프론트엔드
cd frontend && npm run dev > frontend.log 2>&1 &
```

### 3. 접속 정보

#### URL
- 프론트엔드: http://localhost:5173
- 백엔드 API: http://localhost:8000
- API 문서: http://localhost:8000/docs
- API ReDoc: http://localhost:8000/redoc

#### 테스트 계정
- 이메일: admin@aibio.com
- 비밀번호: admin123

### 4. 서버 상태 확인
```bash
# 프로세스 확인
ps aux | grep -E "python.*main|node|vite" | grep -v grep

# 포트 사용 확인
lsof -i :8000  # 백엔드
lsof -i :5173  # 프론트엔드

# API 헬스체크
curl http://localhost:8000/api/v1/health
```

### 5. 서버 종료
```bash
# 프로세스 종료
pkill -f "python.*main.py"
pkill -f vite

# 포트 강제 해제
kill -9 $(lsof -t -i:8000)
kill -9 $(lsof -t -i:5173)
```

## Bash 명령어 실행 규칙

### 자동 실행 가능한 명령어 (확인 불필요)

#### 1. 프로세스 관리
- `ps aux | grep [process]` - 프로세스 확인
- `lsof -ti:[port]` - 포트 사용 확인
- `pkill -f [process]` - 프로세스 종료
- `kill -9 [pid]` - 특정 PID 종료
- `lsof -ti:[port] | xargs kill -9` - 포트 사용 프로세스 종료

#### 2. 서버 관리
- `python main.py > backend.log 2>&1 &` - 백엔드 서버 재시작
- `npm run dev > frontend.log 2>&1 &` - 프론트엔드 서버 재시작
- `tail -f [logfile]` - 로그 확인
- `cat [logfile] | tail -n [lines]` - 로그 마지막 부분 확인

#### 3. 파일 시스템 작업
- `ls -la` - 파일 목록 확인
- `pwd` - 현재 디렉토리 확인
- `cd [directory]` - 디렉토리 이동
- `cat [file]` - 파일 내용 확인
- `grep [pattern] [file]` - 파일 내 검색
- `find . -name "[pattern]"` - 파일 찾기

#### 4. Git 작업
- `git status` - 상태 확인
- `git diff` - 변경사항 확인
- `git log --oneline -n [count]` - 커밋 로그 확인
- `git add .` 또는 `git add [file]` - 스테이징
- `git commit -m "[message]"` - 커밋

#### 5. 스크립트 실행
- `python scripts/[script].py` - 파이썬 스크립트 실행
- `bash scripts/[script].sh` - 쉘 스크립트 실행

#### 6. 네트워크 및 API 테스트
- `curl` 명령어 전체 - API 테스트
- `netstat -an | grep [port]` - 네트워크 상태 확인

#### 7. 환경 확인
- `which [command]` - 명령어 위치 확인
- `echo $[VARIABLE]` - 환경변수 확인
- `env | grep [pattern]` - 환경변수 검색

### 확인이 필요한 명령어

#### 1. 위험한 작업
- `rm -rf` - 강제 삭제
- `drop database` - 데이터베이스 삭제
- `truncate` - 테이블 초기화
- 시스템 설정 변경 명령어

#### 2. 민감한 정보
- 비밀번호가 포함된 명령어
- API 키가 노출되는 명령어
- 개인정보가 포함된 명령어

#### 3. 대규모 변경
- 대량의 데이터 마이그레이션
- 전체 시스템 재시작
- 프로덕션 환경 변경

## 코드 작성 규칙

### 1. 파일 명명 규칙
- 컴포넌트: PascalCase (예: `CustomerModal.tsx`)
- 유틸리티: camelCase (예: `formatDate.ts`)
- 상수: UPPER_SNAKE_CASE (예: `API_BASE_URL`)

### 2. Import 순서
```typescript
// 1. React 관련
import { useState, useEffect } from 'react';

// 2. 외부 라이브러리
import { api } from '../lib/api';

// 3. 컴포넌트
import CustomerModal from '../components/CustomerModal';

// 4. 타입
import type { Customer } from '../types';

// 5. 스타일/기타
import '../styles/customer.css';
```

### 3. 에러 처리
```typescript
try {
  const response = await api.get('/endpoint');
  // 성공 처리
} catch (error) {
  console.error('Error details:', error);
  // 사용자에게 에러 표시
  alert('작업 중 오류가 발생했습니다.');
}
```

### 4. 주석 사용
- 주석은 최소화하고 코드로 의도를 표현
- 복잡한 비즈니스 로직의 경우에만 주석 사용
- TODO 주석은 반드시 담당자와 예정일 명시

## 디버깅 및 문제 해결

### 1. 자주 발생하는 문제

#### "사이트에 연결할 수 없음" 에러
```bash
# 프론트엔드 서버 재시작
cd frontend
pkill -f vite
npm run dev
```

#### 500 Internal Server Error
```bash
# 백엔드 서버 재시작
cd backend
pkill -f "python main.py"
python main.py
```

#### Import 에러 (모듈을 찾을 수 없음)
- 파일명과 import 경로 확인
- 파일 확장자 확인 (.ts, .tsx)
- 대소문자 구분 확인

### 2. 진단 도구
```bash
# API 연결 테스트
curl http://localhost:8000/api/v1/health

# 데이터베이스 스키마 확인
python scripts/check_schema.py --list

# 로그 확인
tail -f backend/logs/app.log
tail -f backend/server.log
```

### 3. 로그 위치
- 백엔드: `backend/logs/app.log`
- 프론트엔드: 브라우저 콘솔
- 시스템: `backend/server.log`

## 협업 규칙

### 1. 커밋 메시지 형식
```
[타입] 간단한 설명

- 상세 내용 1
- 상세 내용 2
```
타입: feat, fix, docs, style, refactor, test, chore

### 2. 브랜치 전략
- main: 안정된 코드만
- feature/*: 새 기능 개발
- fix/*: 버그 수정

### 3. 코드 리뷰 체크리스트
- [ ] 기능이 정상 작동하는가?
- [ ] 에러 처리가 되어 있는가?
- [ ] 타입이 올바른가?
- [ ] 불필요한 console.log가 없는가?
- [ ] 데이터베이스 스키마와 일치하는가?

### 4. Pull Request 규칙
- PR 템플릿 사용
- 스크린샷 첨부 (UI 변경 시)
- 테스트 결과 포함
- 최소 1명 이상의 리뷰 필수

## 성능 모니터링

### 1. 번들 크기 확인
```bash
cd frontend
npm run build
# dist 폴더 크기 확인
```

### 2. 로딩 시간 측정
- Chrome DevTools > Network 탭
- Lighthouse 성능 측정

### 3. 데이터베이스 쿼리 최적화
- 느린 쿼리 로그 확인
- 인덱스 활용 확인
- N+1 쿼리 문제 방지

## 백업 및 복구

### 1. 코드 백업
```bash
# 특정 파일 복구
git checkout HEAD -- path/to/file

# 전체 폴더 복구
git checkout HEAD -- frontend/src/components/
```

### 2. 데이터베이스 백업
```bash
# 백업 스크립트 실행
python scripts/backup_database.py

# 특정 테이블 백업
pg_dump -t table_name > backup.sql
```

## 코드 리팩토링 프로세스 🆕

### 1. 리팩토링 가이드
대규모 리팩토링이 필요할 때는 체계적인 접근이 필요합니다.
상세한 리팩토링 절차와 모범 사례는 다음 문서를 참조하세요:

👉 **[리팩토링 가이드](./docs/refactoring-guide.md)**

### 2. 주요 리팩토링 원칙
- **점진적 개선**: 한 번에 하나의 파일만 수정
- **테스트 우선**: 리팩토링 전후 테스트 실행
- **백업 필수**: 변경 전 git commit으로 체크포인트 생성

## 문서 규칙 승격 프로세스 🆕

### Hidden → Official Rule 승격 절차
`.claude` 폴더의 숨겨진 규칙이 팀 표준이 되는 과정:

1. **실험 단계** (.claude/)
   - 새로운 규칙이나 패턴을 `.claude/` 폴더에서 테스트
   - 최소 2주간 실제 개발에 적용

2. **검증 단계**
   - 팀 리뷰에서 효과성 검증
   - 실수 사례(mistakes.md)에서 패턴 추출

3. **승격 단계**
   - 검증된 규칙을 공식 문서로 이동:
     - 프로젝트 전체: `CLAUDE.md` 또는 `CLAUDE_EXTENDED.md`
     - 기술별: `backend/CLAUDE.md`, `frontend/CLAUDE.md`
     - 특화 가이드: `docs/` 폴더의 해당 문서

4. **통합 단계**
   - 상위 문서에 링크 추가
   - 기존 `.claude/` 문서에서 중복 내용 제거
   - 팀 공지 및 교육
