# 리팩토링 체크리스트

> 각 작업 전후로 확인해야 할 사항들

## 🚀 작업 시작 전

### 환경 준비
- [ ] 최신 main 브랜치에서 새 브랜치 생성
  ```bash
  git checkout main
  git pull origin main
  git checkout -b refactor/phase-1-utilities
  ```

- [ ] 현재 상태 백업
  ```bash
  git add .
  git commit -m "refactor: Phase 1 시작 전 상태"
  ```

- [ ] 서버 정상 작동 확인
  ```bash
  cd backend && python main.py
  cd frontend && npm run dev
  ```

- [ ] 테스트 실행 및 통과 확인
  ```bash
  cd backend && pytest
  cd frontend && npm test
  ```

## 💻 작업 중

### 코드 수정 시
- [ ] 한 번에 하나의 파일만 수정
- [ ] 수정 후 즉시 빌드 확인
- [ ] import 경로 정확성 확인
- [ ] 타입 에러 없음 확인

### 커밋 규칙
- [ ] 의미 있는 단위로 커밋
  ```bash
  git commit -m "refactor: 전화번호 포맷팅 유틸리티 함수 추출"
  git commit -m "refactor: CustomerModal에서 포맷팅 함수 import로 변경"
  ```

## 🧪 작업 후 검증

### 로컬 테스트
- [ ] Backend 서버 재시작 및 정상 작동
- [ ] Frontend 빌드 성공
  ```bash
  npm run build
  ```
- [ ] 주요 기능 수동 테스트
  - [ ] 로그인
  - [ ] 고객 등록/수정
  - [ ] 서비스 이용 등록
  - [ ] 결제 처리

### API 테스트
- [ ] 모든 엔드포인트 응답 확인
  ```bash
  python test_all_endpoints.py
  ```

### UI/UX 불변 확인
- [ ] 스크린샷 비교 (변경 전/후)
- [ ] 스타일 변경 없음
- [ ] 기능 동작 동일

## 📦 배포 전 확인

### Vercel (Frontend)
- [ ] 환경 변수 설정 확인
  ```
  VITE_API_URL=https://api.aibio.com
  ```
- [ ] Preview 배포 테스트
- [ ] 빌드 크기 확인 (기존 대비)

### Railway (Backend)
- [ ] requirements.txt 변경사항 확인
- [ ] 환경 변수 확인
  ```
  DATABASE_URL
  JWT_SECRET
  ENVIRONMENT=production
  ```
- [ ] 헬스체크 엔드포인트 응답

### Supabase
- [ ] 데이터베이스 연결 테스트
- [ ] 마이그레이션 필요 여부 확인

## 🚨 문제 발생 시

### 즉시 확인
- [ ] 에러 로그 확인
- [ ] 최근 변경사항 검토
- [ ] 환경 변수 설정 확인

### 롤백 절차
```bash
# 로컬 롤백
git checkout HEAD~1

# 배포 롤백
# Vercel: 이전 배포로 롤백
# Railway: 이전 커밋으로 재배포
```

## 📊 완료 기준

### Phase별 완료 조건
- [ ] 모든 테스트 통과
- [ ] 빌드 성공
- [ ] 배포 환경 정상 작동
- [ ] 성능 저하 없음
- [ ] UI/UX 변경 없음

### 문서화
- [ ] 변경사항 README 업데이트
- [ ] API 문서 업데이트 (필요시)
- [ ] 팀 공유 및 리뷰

## 🎯 Quick Commands

```bash
# 서버 시작
cd backend && python main.py > backend.log 2>&1 &
cd frontend && npm run dev > frontend.log 2>&1 &

# 프로세스 확인
ps aux | grep -E "python.*main|vite" | grep -v grep

# 로그 확인
tail -f backend/backend.log
tail -f frontend/frontend.log

# 테스트 실행
cd backend && python test_all_endpoints.py
cd frontend && npm run build

# 서버 종료
pkill -f "python.*main.py"
pkill -f vite
```

---

*이 체크리스트를 각 Phase 작업 시 참조하여 안전한 리팩토링을 진행하세요.*