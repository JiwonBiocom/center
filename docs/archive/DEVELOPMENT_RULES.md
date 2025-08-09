# 개발 규칙 및 가이드라인

## 🚀 프로젝트 시작하기

### 1. 백엔드 서버 시작
```bash
cd backend
source venv/bin/activate  # 가상환경 활성화
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 2. 프론트엔드 서버 시작
```bash
cd frontend
npm run dev
```

### 3. 접속 URL
- 프론트엔드: http://localhost:5173
- 백엔드 API: http://localhost:8000
- API 문서: http://localhost:8000/docs

## 📌 필수 확인 사항

### 변경 작업 후 반드시 확인
1. **로컬 서버 접속 테스트**
   - 변경사항 적용 후 반드시 브라우저에서 직접 확인
   - 주요 페이지 네비게이션 테스트
   - API 응답 정상 여부 확인

2. **에러 로그 확인**
   - 브라우저 콘솔 (F12)
   - 백엔드 로그: `backend/logs/app.log`
   - Vite 서버 터미널 출력

3. **Git 커밋 전 체크리스트**
   - [ ] 로컬 서버에서 정상 작동 확인
   - [ ] 타입스크립트 에러 없음 (`npx tsc --noEmit`)
   - [ ] 린트 에러 없음 (`npm run lint`)
   - [ ] 테스트 통과 (있는 경우)

## 🛠️ 자주 발생하는 문제 해결

### 1. "사이트에 연결할 수 없음" 에러
```bash
# 프론트엔드 서버 재시작
cd frontend
pkill -f vite
npm run dev
```

### 2. 500 Internal Server Error
```bash
# 백엔드 서버 재시작
cd backend
pkill -f uvicorn
uvicorn main:app --reload
```

### 3. Import 에러 (모듈을 찾을 수 없음)
- 파일명과 import 경로 확인
- 파일 확장자 확인 (.ts, .tsx)
- 대소문자 구분 확인

### 4. 설정 컴포넌트가 표시되지 않음
```javascript
// 브라우저 콘솔에서 실행
diagnoseSettings()
```

## 🔍 디버깅 도구

### 1. 진단 스크립트
```bash
# 설정 페이지 진단
브라우저 콘솔: diagnoseSettings()

# API 연결 테스트
curl http://localhost:8000/api/v1/health
```

### 2. 로그 위치
- 백엔드: `backend/logs/app.log`
- 프론트엔드: 브라우저 콘솔
- 시스템: `backend/server.log`

## 📝 코드 작성 규칙

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

## ⚠️ 주의사항

1. **절대 하지 말아야 할 것**
   - `rm -rf` 명령어 사용
   - `.env` 파일 커밋
   - 실제 사용자 데이터로 테스트
   - 프로덕션 DB에 직접 접속

2. **항상 해야 할 것**
   - 변경 전 백업
   - 로컬에서 테스트
   - 에러 로그 확인
   - 코드 리뷰

## 🔄 백업 및 복구

### 1. 설정 컴포넌트 백업
```bash
./backup_settings.sh
```

### 2. Git에서 복구
```bash
# 특정 파일 복구
git checkout HEAD -- path/to/file

# 전체 폴더 복구
git checkout HEAD -- frontend/src/components/settings/
```

## 📊 성능 모니터링

### 1. 번들 크기 확인
```bash
cd frontend
npm run build
# dist 폴더 크기 확인
```

### 2. 로딩 시간 측정
- Chrome DevTools > Network 탭
- Lighthouse 성능 측정

## 🤝 협업 규칙

1. **커밋 메시지 형식**
   ```
   [타입] 간단한 설명
   
   - 상세 내용 1
   - 상세 내용 2
   ```
   타입: feat, fix, docs, style, refactor, test, chore

2. **브랜치 전략**
   - main: 안정된 코드만
   - feature/*: 새 기능 개발
   - fix/*: 버그 수정

3. **코드 리뷰 체크리스트**
   - [ ] 기능이 정상 작동하는가?
   - [ ] 에러 처리가 되어 있는가?
   - [ ] 타입이 올바른가?
   - [ ] 불필요한 console.log가 없는가?

---

이 문서는 지속적으로 업데이트됩니다. 
문제 발생 시 이 문서를 먼저 확인해주세요.