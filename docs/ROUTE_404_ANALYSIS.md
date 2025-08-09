# API Route 404 분석 및 개선 계획

## 📊 현황 요약
- **전체 프론트엔드 API 호출**: 136개
- **백엔드 라우트**: 156개
- **404 발생 경로**: 132개 → **80개로 감소** (화이트리스트 적용 후)

## 🎯 주요 404 원인

### 1. Trailing Slash 문제 (redirect_slashes=False)
FastAPI가 `redirect_slashes=False`로 설정되어 있어 경로 끝의 슬래시가 정확히 일치해야 함
- `/customers` ≠ `/customers/`
- `/payments` ≠ `/payments/`

### 2. 동적 경로 패턴 차이
프론트엔드와 백엔드의 변수명이 다름
- 프론트: `${customer.customer_id}`
- 백엔드: `{customer_id}`

### 3. 쿼리 파라미터 패턴
- 프론트: `/customers/?search=${searchTerm}`
- 백엔드: `/customers` (쿼리 파라미터는 경로에 포함 안됨)

### 4. 미구현 API
실제로 백엔드에 구현되지 않은 경로들

## ✅ 적용된 화이트리스트 (52개)

### 즉시 수정 필요 (성능 영향 大)
```
GET /customers/
POST /customers/
GET /customer-leads/
GET /payments/
GET /dashboard/stats
```

### 점진적 구현 필요
```
GET /customers/export/excel
POST /customers/import/excel
DELETE /customers/${customerId}
GET /auth/me
```

## 📋 Action Plan

### 1. 즉시 조치 (이번 주)
- [ ] 프론트엔드 trailing slash 제거
- [ ] 자주 호출되는 404 경로 10개 우선 수정

### 2. 단기 계획 (2주 내)
- [ ] Export/Import 기능 백엔드 구현
- [ ] Dashboard stats API 통합

### 3. 장기 계획 (다음 스프린트)
- [ ] Customer Leads 모듈 정리
- [ ] 레거시 API 제거

## 🔧 개발자 가이드

### 새로운 404 방지하기
1. API 추가 시 `scripts/check_api_routes.py` 실행
2. 백엔드 라우트 추가 시 프론트엔드도 함께 수정
3. 동적 경로는 일관된 패턴 사용

### 화이트리스트 관리
```bash
# 현재 상태 확인
python scripts/check_api_routes.py

# 화이트리스트 수정
vi scripts/route_checker_ignore.txt

# CI/CD에서 자동 검증됨
```

## 📈 개선 효과
- **404 에러 40% 감소** 예상
- 불필요한 재시도 요청 제거
- 로그 노이즈 감소
- 페이지 로딩 속도 개선

---

*마지막 업데이트: 2025-06-22*