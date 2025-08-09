# 개발 중 발생한 에러 및 해결 방법

이 문서는 AIBIO Center Management System 개발 중 발생한 에러와 해결 방법을 기록합니다.

## 상태 표시
- ✅ **해결 완료**: 해결 방법이 적용되고 테스트까지 완료됨
- 🔄 **해결 시도 중**: 해결 방법을 찾았으나 아직 완전히 해결되지 않음

## 목차
- [백엔드 에러](#백엔드-에러)
- [프론트엔드 에러](#프론트엔드-에러)
- [데이터베이스 에러](#데이터베이스-에러)
- [배포 관련 에러](#배포-관련-에러)

---

## 백엔드 에러

### 1. AsyncSession vs Session 타입 에러
**발생일시**: 2025-06-04 02:00
**증상**: reports.py에서 500 Internal Server Error 발생
**원인**: SQLAlchemy에서 동기 Session 대신 AsyncSession을 사용해야 함
**상태**: ✅ 해결 완료
**해결**:
```python
# 변경 전
from sqlalchemy.orm import Session
db: Session = Depends(get_db)

# 변경 후
from sqlalchemy.ext.asyncio import AsyncSession
db: AsyncSession = Depends(get_db)
```

### 2. SQLAlchemy 쿼리 구문 에러
**발생일시**: 2025-06-04 02:05
**증상**: 고객 목록 API에서 정렬 시 에러
**원인**: SQLite에서 `nullslast()` 미지원
**상태**: ✅ 해결 완료
**해결**:
```python
# 변경 전
query.order_by(CustomerModel.first_visit_date.desc().nullslast())

# 변경 후
query.order_by(desc(CustomerModel.first_visit_date))
```

### 3. 중복 전화번호 제약 조건 위반
**발생일시**: 2025-06-03 16:40
**증상**: 엑셀 데이터 마이그레이션 시 UNIQUE constraint failed
**원인**: 전화번호 필드에 unique=True 제약이 있는데 중복 데이터 존재
**상태**: ✅ 해결 완료
**해결**:
- 중복 전화번호는 null로 처리
- 고객명에 suffix 추가하여 구분

### 4. 결제 데이터 마이그레이션 실패
**발생일시**: 2025-06-04 08:57
**증상**: 대시보드 차트에 "데이터 없음" 표시, 결제 테이블이 비어있음
**원인**: 엑셀 파일의 복잡한 구조로 인해 마이그레이션 스크립트가 데이터를 제대로 읽지 못함
**상태**: ✅ 해결 완료
**해결**:
- 엑셀 파일 분석 결과 헤더가 row 2(header=1)에 위치
- 데이터는 row 3부터 시작
- 간단한 마이그레이션 스크립트(simple_payment_migrate.py)로 해결
- 295개 결제 데이터 성공적으로 마이그레이션

---

## 프론트엔드 에러

### 1. 빈 화면 표시 문제
**발생일시**: 2025-06-04 01:59
**증상**: 고객 관리 페이지가 빈 화면으로 표시됨
**원인**: API 응답 형식 변경 (페이지네이션 구조)
**상태**: ✅ 해결 완료
**해결**:
```typescript
// API 응답 형식에 맞춰 프론트엔드 코드 수정
const response = await api.get<Customer[]>('/api/v1/customers', {
  params: { skip, limit: pageSize }
})
```

### 2. 프론트엔드 폴더 위치 혼동
**발생일시**: 2025-06-04 02:20
**증상**: 잘못된 경로에 파일 생성
**원인**: `/backend/frontend`와 `/frontend` 두 개의 프론트엔드 폴더 존재
**상태**: ✅ 해결 완료
**해결**: 올바른 경로는 `/Users/vibetj/coding/center/frontend`

---

## 데이터베이스 에러

### 1. email-validator 의존성 누락
**발생일시**: 2025-06-03 15:30
**증상**: Pydantic 모델 import 시 에러
**원인**: pydantic[email] 설치 필요
**상태**: ✅ 해결 완료
**해결**: `pip install pydantic[email]`

### 2. greenlet 의존성 문제
**발생일시**: 2025-06-03 15:45
**증상**: SQLAlchemy async 사용 시 greenlet 필요
**원인**: AsyncSession 사용을 위한 의존성
**상태**: ✅ 해결 완료
**해결**: requirements.txt에 `greenlet==3.1.1` 추가

---

## 배포 관련 에러

### 1. CORS 에러
**발생일시**: 2025-06-03 16:00
**증상**: 프론트엔드에서 백엔드 API 호출 시 CORS 에러
**원인**: localhost:5173 (Vite 기본 포트) 미허용
**상태**: ✅ 해결 완료
**해결**: CORS 설정에 포트 추가
```python
allow_origins=["http://localhost:3000", "http://localhost:5173"]
```

---

## 자주 발생하는 문제 및 해결 팁

1. **API 엔드포인트 404 에러**
   - 라우터가 main.py에 등록되었는지 확인
   - URL 끝에 슬래시(/) 확인 (FastAPI는 자동 리다이렉트)

2. **타입 에러**
   - Pydantic 스키마와 SQLAlchemy 모델 타입 일치 확인
   - Optional 필드 처리 확인

3. **비동기 처리**
   - 모든 데이터베이스 작업에 await 사용
   - AsyncSession 사용 확인

---

### 3. 의존성 누락으로 인한 빈 화면
**발생일시**: 2025-06-04 08:34
**증상**: 프론트엔드 접속 시 빈 화면만 표시
**원인**: react-router-dom, @tanstack/react-query, lucide-react, axios 패키지 미설치
**상태**: ✅ 해결 완료
**해결**:
```bash
npm install react-router-dom @tanstack/react-query lucide-react axios
```

### 4. PostCSS/Tailwind CSS 설정 충돌로 인한 스타일 미적용
**발생일시**: 2025-06-28 10:00
**증상**: 웹페이지가 CSS 스타일 없이 깨져서 표시됨 (스크린샷 참조)
**원인**:
- PostCSS 설정에서 Tailwind CSS v4 방식의 import 사용 (`@tailwindcss/postcss`)
- index.css에서 잘못된 import 구문 사용 (`@import "tailwindcss"`)
- Tailwind CSS v3와 v4 설정 방식 혼용
**상태**: ✅ 해결 완료
**해결**:
1. `@tailwindcss/postcss` 패키지 설치
   ```bash
   npm install -D @tailwindcss/postcss
   ```
2. index.css를 표준 v3 방식으로 수정
   ```css
   /* 변경 전 */
   @import "tailwindcss";

   /* 변경 후 */
   @tailwind base;
   @tailwind components;
   @tailwind utilities;
   ```
3. Vite 캐시 삭제 및 서버 재시작
   ```bash
   rm -rf node_modules/.vite
   npm run dev
   ```

### 5. ViewModeProvider 제거로 인한 Context 에러
**발생일시**: 2025-06-28 10:10
**증상**: "Error: useViewMode must be used within a ViewModeProvider"
**원인**: main.tsx에서 ViewModeProvider가 제거되었지만 캐시에 이전 코드 잔존
**상태**: ✅ 해결 완료
**해결**: Vite 개발 서버 캐시 삭제로 해결

---

## 해결 상태 요약
- **전체 에러**: 12개
- **해결 완료**: 12개 (100%) ✅
- **해결 시도 중**: 0개 (0%)

### 모든 에러가 해결되었습니다! 🎉

---

*마지막 업데이트: 2025-06-28 10:25*
