# AIBIO Center API Documentation

## 개요
AIBIO Center Management System의 RESTful API 문서입니다.

- **Base URL**: `https://api.aibio.center/api/v1`
- **인증 방식**: JWT Bearer Token
- **응답 형식**: JSON

## 인증 (Authentication)

### 로그인
```http
POST /auth/login
Content-Type: application/x-www-form-urlencoded

username=admin@aibio.com&password=your-password
```

**응답**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### 토큰 갱신
```http
POST /auth/refresh
Content-Type: application/json

{
  "refresh_token": "your-refresh-token"
}
```

## 고객 관리 (Customers)

### 고객 목록 조회
```http
GET /customers?skip=0&limit=20&search=김
Authorization: Bearer {access_token}
```

**쿼리 파라미터**:
- `skip`: 건너뛸 레코드 수 (기본값: 0)
- `limit`: 조회할 레코드 수 (기본값: 100, 최대: 1000)
- `search`: 검색어 (이름, 전화번호)
- `region`: 지역 필터
- `referral_source`: 유입 경로
- `membership_level`: 회원 등급
- `customer_status`: 고객 상태
- `risk_level`: 리스크 수준
- `age_min`, `age_max`: 나이 범위
- `revenue_min`, `revenue_max`: 매출 범위 (만원 단위)
- `visits_min`, `visits_max`: 방문 횟수 범위
- `first_visit_from`, `first_visit_to`: 첫 방문일 범위
- `last_visit_from`, `last_visit_to`: 마지막 방문일 범위

### 고객 생성
```http
POST /customers
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "name": "홍길동",
  "phone": "010-1234-5678",
  "email": "hong@example.com",
  "birth_year": 1990,
  "gender": "M",
  "region": "서울",
  "referral_source": "지인추천"
}
```

### 고객 상세 조회
```http
GET /customers/{customer_id}
Authorization: Bearer {access_token}
```

### 고객 정보 수정
```http
PUT /customers/{customer_id}
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "name": "홍길동",
  "phone": "010-1234-5678",
  "email": "hong@example.com",
  "memo": "VIP 고객"
}
```

### 고객 삭제
```http
DELETE /customers/{customer_id}
Authorization: Bearer {access_token}
```

## 예약 관리 (Reservations)

### 예약 목록 조회
```http
GET /reservations?date_from=2025-01-01&date_to=2025-01-31
Authorization: Bearer {access_token}
```

**쿼리 파라미터**:
- `date_from`, `date_to`: 날짜 범위
- `status`: 예약 상태 (pending, confirmed, cancelled, completed, no_show)
- `customer_id`: 고객 ID
- `staff_id`: 담당자 ID

### 예약 생성
```http
POST /reservations
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "customer_id": 1,
  "service_type_id": 2,
  "staff_id": 3,
  "reservation_date": "2025-01-15",
  "reservation_time": "14:00",
  "duration_minutes": 60,
  "customer_request": "첫 방문입니다"
}
```

### 예약 수정
```http
PUT /reservations/{reservation_id}
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "reservation_date": "2025-01-16",
  "reservation_time": "15:00",
  "status": "confirmed"
}
```

### 예약 취소
```http
POST /reservations/{reservation_id}/cancel
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "reason": "고객 요청"
}
```

### 예약 확정
```http
POST /reservations/{reservation_id}/confirm
Authorization: Bearer {access_token}
```

### 예약 완료 (서비스 이용 기록 자동 생성)
```http
POST /reservations/{reservation_id}/complete
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "package_id": 5,
  "session_details": "첫 세션 완료, 고객 만족도 높음"
}
```

## 서비스 관리 (Services)

### 서비스 타입 목록
```http
GET /services/types
Authorization: Bearer {access_token}
```

### 서비스 이용 내역 조회
```http
GET /services/usage?date_from=2025-01-01&date_to=2025-01-31
Authorization: Bearer {access_token}
```

### 서비스 통계
```http
GET /services/stats?year=2025&month=1
Authorization: Bearer {access_token}
```

**응답**:
```json
{
  "total_services": 150,
  "unique_customers": 45,
  "most_popular_service": "브레인",
  "total_revenue": 4500000,
  "average_daily_services": 5.0
}
```

### 캘린더 데이터
```http
GET /services/calendar?year=2025&month=1
Authorization: Bearer {access_token}
```

## 패키지 관리 (Packages)

### 패키지 목록
```http
GET /packages
Authorization: Bearer {access_token}
```

### 패키지 구매
```http
POST /packages/purchases
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "customer_id": 1,
  "package_id": 2,
  "purchase_date": "2025-01-10",
  "payment_amount": 500000,
  "payment_method": "card"
}
```

### 고객별 활성 패키지
```http
GET /packages/customer/{customer_id}/active
Authorization: Bearer {access_token}
```

## 결제 관리 (Payments)

### 결제 내역 조회
```http
GET /payments?date_from=2025-01-01&date_to=2025-01-31
Authorization: Bearer {access_token}
```

### 결제 등록
```http
POST /payments
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "customer_id": 1,
  "payment_date": "2025-01-10",
  "amount": 150000,
  "payment_method": "card",
  "service_info": "브레인 케어",
  "memo": "첫 결제"
}
```

### 결제 통계
```http
GET /payments/stats?year=2025&month=1
Authorization: Bearer {access_token}
```

## 리포트 (Reports)

### 일일 매출 리포트
```http
GET /reports/daily-revenue?date=2025-01-10
Authorization: Bearer {access_token}
```

### 월간 요약 리포트
```http
GET /reports/monthly-summary?year=2025&month=1
Authorization: Bearer {access_token}
```

### 고객별 리포트
```http
GET /reports/customer/{customer_id}?start_date=2025-01-01&end_date=2025-01-31
Authorization: Bearer {access_token}
```

### 서비스별 리포트
```http
GET /reports/service?service_type_id=1&start_date=2025-01-01&end_date=2025-01-31
Authorization: Bearer {access_token}
```

## 대시보드 (Dashboard)

### 대시보드 통계
```http
GET /dashboard/stats
Authorization: Bearer {access_token}
```

**응답**:
```json
{
  "stats": {
    "total_customers": 250,
    "today_reservations": 12,
    "monthly_revenue": 15000000,
    "active_packages": 45
  },
  "monthly_revenue": [...],
  "daily_revenue": [...],
  "service_usage": [...],
  "top_services": [...]
}
```

## 설정 (Settings)

### 사용자 관리
```http
GET /settings/users
Authorization: Bearer {access_token}
```

### 알림 설정
```http
GET /settings/notifications
PUT /settings/notifications
Authorization: Bearer {access_token}
```

### 백업
```http
POST /settings/backup
Authorization: Bearer {access_token}
```

## 에러 응답

모든 API는 다음과 같은 표준 에러 응답을 반환합니다:

```json
{
  "detail": "에러 메시지",
  "status_code": 400,
  "type": "validation_error"
}
```

**HTTP 상태 코드**:
- `200 OK`: 성공
- `201 Created`: 생성 성공
- `400 Bad Request`: 잘못된 요청
- `401 Unauthorized`: 인증 실패
- `403 Forbidden`: 권한 없음
- `404 Not Found`: 리소스를 찾을 수 없음
- `409 Conflict`: 충돌 (중복 등)
- `422 Unprocessable Entity`: 유효성 검증 실패
- `500 Internal Server Error`: 서버 오류

## Rate Limiting

- 분당 60회 요청
- 시간당 1000회 요청
- 초과 시 `429 Too Many Requests` 응답

## 페이지네이션

목록 조회 API는 다음과 같은 페이지네이션 파라미터를 지원합니다:

- `skip`: 건너뛸 레코드 수 (기본값: 0)
- `limit`: 페이지당 레코드 수 (기본값: 20, 최대: 100)

## 날짜 형식

- 날짜: `YYYY-MM-DD` (예: 2025-01-15)
- 시간: `HH:MM` (예: 14:30)
- 날짜시간: ISO 8601 형식 (예: 2025-01-15T14:30:00)

## 보안 권장사항

1. HTTPS를 통해서만 API 호출
2. 액세스 토큰은 안전하게 저장
3. 토큰 만료 시 리프레시 토큰으로 갱신
4. API 키나 토큰을 코드에 하드코딩하지 않음
5. CORS 설정을 통해 허용된 도메인만 접근 가능