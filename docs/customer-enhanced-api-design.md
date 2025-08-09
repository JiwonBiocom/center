# 고객관리 시스템 확장 API 설계 문서

## 📋 문서 정보
- **작성일**: 2025-06-06
- **버전**: 1.0
- **관련 문서**: [PRD](./prd-customer-enhanced.md), [개발 계획서](./customer-enhanced-development-plan.md)

---

## 🌐 API 개요

### Base URL
```
Production: https://api.aibio-center.com/api/v1
Development: http://localhost:8000/api/v1
```

### 인증
- Bearer Token (JWT)
- 헤더: `Authorization: Bearer {token}`

### 공통 응답 형식
```json
{
  "success": true,
  "data": {},
  "message": "Success",
  "timestamp": "2025-06-06T12:00:00Z"
}
```

### 에러 응답
```json
{
  "success": false,
  "error": {
    "code": "CUSTOMER_NOT_FOUND",
    "message": "고객을 찾을 수 없습니다",
    "detail": {}
  },
  "timestamp": "2025-06-06T12:00:00Z"
}
```

---

## 📚 API 엔드포인트

### 1. 고객 상세 정보 API

#### 1.1 고객 상세 조회
```http
GET /customers/{customer_id}/detail
```

**응답 예시**:
```json
{
  "success": true,
  "data": {
    "customer": {
      "customer_id": 123,
      "name": "김영희",
      "phone": "010-1234-5678",
      "email": "kim@example.com",
      "birth_year": 1985,
      "gender": "female",
      "address": "서울시 강남구...",
      "emergency_contact": "010-8765-4321",
      "occupation": "회사원",
      "membership_level": "VIP",
      "customer_status": "active",
      "first_visit_date": "2024-01-15",
      "last_visit_date": "2024-05-30",
      "total_visits": 12,
      "average_visit_interval": 14,
      "total_revenue": 2500000,
      "average_satisfaction": 4.8,
      "risk_level": "stable",
      "health_goals": "스트레스 해소, 수면 개선",
      "preferred_time_slots": ["morning", "weekend"],
      "assigned_staff": "이직원",
      "created_at": "2024-01-15T10:00:00Z",
      "updated_at": "2024-05-30T15:30:00Z"
    },
    "serviceHistory": [
      {
        "session_id": 456,
        "service_date": "2024-05-30",
        "service_type": "brain",
        "service_name": "브레인 피드백",
        "duration_minutes": 40,
        "satisfaction_rating": 5,
        "session_notes": "컨디션 매우 좋음",
        "staff_name": "이직원",
        "package_name": "프리미엄 케어"
      }
    ],
    "activePackages": [
      {
        "package_usage_id": 789,
        "package_name": "프리미엄 케어 패키지",
        "purchase_date": "2024-04-01",
        "expiry_date": "2024-07-01",
        "total_sessions": 40,
        "used_sessions": 18,
        "remaining_sessions": 22,
        "usage_rate": 45.0,
        "days_remaining": 25,
        "service_breakdown": {
          "brain": {"total": 10, "used": 8, "remaining": 2},
          "pulse": {"total": 10, "used": 6, "remaining": 4},
          "lymph": {"total": 10, "used": 4, "remaining": 6},
          "red": {"total": 10, "used": 0, "remaining": 10}
        }
      }
    ],
    "preferences": {
      "preferred_services": ["brain", "pulse"],
      "preferred_time": "morning",
      "preferred_intensity": "medium",
      "health_interests": ["stress_management", "sleep_quality"],
      "communication_preference": "kakao",
      "marketing_consent": true
    }
  }
}
```

#### 1.2 고객 상세 정보 업데이트
```http
PUT /customers/{customer_id}/detail
```

**요청 본문**:
```json
{
  "email": "newemail@example.com",
  "occupation": "프리랜서",
  "health_goals": "체중 감량, 근력 향상",
  "preferred_time_slots": ["evening", "weekend"]
}
```

---

### 2. 고객 분석 API

#### 2.1 고객 분석 데이터 조회
```http
GET /customers/{customer_id}/analytics
```

**쿼리 파라미터**:
- `period`: 분석 기간 (30d, 90d, 180d, 1y)
- `metrics`: 포함할 메트릭 (comma-separated)

**응답 예시**:
```json
{
  "success": true,
  "data": {
    "visitPattern": {
      "average_interval_days": 14,
      "visit_frequency": "bi-weekly",
      "preferred_days": ["Monday", "Friday"],
      "preferred_times": ["10:00-12:00"],
      "consistency_score": 85,
      "monthly_visits": [
        {"month": "2024-01", "visits": 2},
        {"month": "2024-02", "visits": 3},
        {"month": "2024-03", "visits": 2}
      ]
    },
    "serviceUsage": {
      "most_used_service": "brain",
      "service_distribution": {
        "brain": 42,
        "pulse": 33,
        "lymph": 17,
        "red": 8
      },
      "satisfaction_by_service": {
        "brain": 4.8,
        "pulse": 4.2,
        "lymph": 3.5,
        "red": 4.0
      },
      "growth_trend": {
        "brain": "+15%",
        "pulse": "+8%",
        "lymph": "-5%",
        "red": "0%"
      }
    },
    "revenueContribution": {
      "total_revenue": 2500000,
      "average_monthly_revenue": 416667,
      "revenue_trend": [
        {"month": "2024-01", "amount": 350000},
        {"month": "2024-02", "amount": 450000},
        {"month": "2024-03", "amount": 420000}
      ],
      "ltv_estimate": 5200000,
      "revenue_percentile": 85
    },
    "healthMetrics": {
      "reported_improvements": {
        "stress_level": {"before": 7, "after": 4, "change": -43},
        "sleep_quality": {"before": 6, "after": 8, "change": +33},
        "focus_level": {"before": 5, "after": 8, "change": +60}
      },
      "goal_achievement_rate": 75,
      "recommendation_compliance": 85
    },
    "riskAssessment": {
      "churn_risk": "low",
      "churn_probability": 15,
      "risk_factors": [],
      "retention_score": 85,
      "next_action_recommendation": "패키지 갱신 제안"
    }
  }
}
```

#### 2.2 고객 세그먼트 분석
```http
GET /customers/segments/{customer_id}
```

**응답**:
```json
{
  "success": true,
  "data": {
    "primary_segment": "health_enthusiast",
    "secondary_segments": ["high_value", "regular_visitor"],
    "characteristics": {
      "visit_frequency": "high",
      "spending_level": "premium",
      "service_diversity": "medium",
      "loyalty_level": "strong"
    },
    "peer_comparison": {
      "visit_frequency_percentile": 80,
      "spending_percentile": 75,
      "satisfaction_percentile": 90
    }
  }
}
```

---

### 3. 서비스 추천 API

#### 3.1 개인화 서비스 추천
```http
GET /customers/{customer_id}/recommendations
```

**쿼리 파라미터**:
- `type`: 추천 유형 (service, package, schedule)
- `count`: 추천 개수 (기본값: 5)

**응답 예시**:
```json
{
  "success": true,
  "data": {
    "recommendations": [
      {
        "type": "service",
        "recommendation_id": "rec_001",
        "service_type": "ai_bike",
        "service_name": "AI 바이크",
        "confidence_score": 0.92,
        "reason": "미이용 서비스 중 운동 목표와 부합",
        "expected_benefit": "유산소 운동을 통한 전반적 건강 개선",
        "suggested_schedule": {
          "frequency": "주 2회",
          "duration": "30분",
          "best_times": ["화요일 오전", "금요일 오후"]
        }
      },
      {
        "type": "package",
        "recommendation_id": "rec_002",
        "package_name": "웰니스 플러스",
        "confidence_score": 0.88,
        "reason": "현재 이용 패턴에 최적화된 구성",
        "package_details": {
          "brain": 15,
          "pulse": 12,
          "ai_bike": 8,
          "total_sessions": 35,
          "price": 1680000,
          "savings": 252000
        },
        "personalization": {
          "based_on": "최근 3개월 이용 패턴",
          "optimization": "비용 대비 만족도 최대화"
        }
      },
      {
        "type": "schedule",
        "recommendation_id": "rec_003",
        "schedule_name": "주간 최적 스케줄",
        "confidence_score": 0.85,
        "weekly_plan": [
          {
            "day": "Monday",
            "time": "10:00",
            "service": "brain",
            "duration": 40,
            "reason": "주 시작 집중력 향상"
          },
          {
            "day": "Wednesday",
            "time": "11:00",
            "service": "pulse",
            "duration": 30,
            "reason": "중간 피로 회복"
          },
          {
            "day": "Friday",
            "time": "14:00",
            "service": "ai_bike",
            "duration": 30,
            "reason": "주말 전 활력 충전"
          }
        ]
      }
    ],
    "recommendation_metadata": {
      "generated_at": "2025-06-06T12:00:00Z",
      "model_version": "2.1.0",
      "factors_considered": [
        "service_history",
        "satisfaction_ratings",
        "health_goals",
        "peer_patterns",
        "seasonal_trends"
      ]
    }
  }
}
```

#### 3.2 추천 피드백
```http
POST /customers/{customer_id}/recommendations/{recommendation_id}/feedback
```

**요청 본문**:
```json
{
  "action": "accepted",
  "feedback_score": 5,
  "comment": "추천이 매우 도움이 되었습니다"
}
```

---

### 4. 고객 목록 확장 API

#### 4.1 고객 검색 (확장)
```http
GET /customers/search
```

**쿼리 파라미터**:
- `q`: 검색어
- `service_filter`: 서비스 필터 (brain,pulse,lymph,red,ai_bike)
- `package_status`: 패키지 상태 (active,expiring,expired)
- `membership_level`: 멤버십 레벨 (basic,premium,vip)
- `risk_level`: 위험도 (stable,warning,danger)
- `last_visit_from`: 최근 방문 시작일
- `last_visit_to`: 최근 방문 종료일
- `sort_by`: 정렬 기준 (name,last_visit,total_visits,revenue)
- `page`: 페이지 번호
- `size`: 페이지 크기

**응답 예시**:
```json
{
  "success": true,
  "data": {
    "customers": [
      {
        "customer_id": 123,
        "name": "김영희",
        "phone": "010-1234-5678",
        "first_visit_date": "2024-01-15",
        "last_visit_date": "2024-05-30",
        "total_visits": 12,
        "active_package": "프리미엄 케어",
        "package_usage_summary": "브5/10 펄3/10",
        "membership_level": "VIP",
        "risk_level": "stable",
        "total_revenue": 2500000
      }
    ],
    "pagination": {
      "total": 892,
      "page": 1,
      "size": 20,
      "total_pages": 45
    },
    "filters_applied": {
      "service_filter": ["brain", "pulse"],
      "package_status": "active"
    }
  }
}
```

---

## 🔐 권한 및 보안

### 권한 레벨
1. **ADMIN**: 모든 API 접근 가능
2. **MANAGER**: 분석 및 추천 API 접근 가능
3. **STAFF**: 조회 API만 접근 가능

### 민감 정보 처리
- 개인정보는 권한에 따라 마스킹
- 건강 정보는 별도 권한 필요
- 모든 조회는 감사 로그 기록

---

## 📊 성능 고려사항

### 캐싱 전략
- 고객 상세 정보: 5분 캐시
- 분석 데이터: 1시간 캐시
- 추천 데이터: 24시간 캐시

### 응답 시간 목표
- 고객 상세 조회: < 200ms
- 분석 데이터: < 500ms
- 추천 생성: < 1000ms

### Rate Limiting
- 일반 API: 1000 req/hour
- 분석 API: 100 req/hour
- 추천 API: 50 req/hour

---

## 🧪 테스트 시나리오

### 1. 고객 상세 조회
```bash
curl -X GET "http://localhost:8000/api/v1/customers/123/detail" \
  -H "Authorization: Bearer {token}"
```

### 2. 고객 분석 조회
```bash
curl -X GET "http://localhost:8000/api/v1/customers/123/analytics?period=90d" \
  -H "Authorization: Bearer {token}"
```

### 3. 서비스 추천 조회
```bash
curl -X GET "http://localhost:8000/api/v1/customers/123/recommendations?type=service&count=3" \
  -H "Authorization: Bearer {token}"
```

---

## 📝 에러 코드

| 코드 | 설명 | HTTP 상태 |
|------|------|-----------|
| CUSTOMER_NOT_FOUND | 고객을 찾을 수 없음 | 404 |
| INSUFFICIENT_DATA | 분석을 위한 데이터 부족 | 400 |
| UNAUTHORIZED_ACCESS | 권한 없음 | 403 |
| RATE_LIMIT_EXCEEDED | 요청 한도 초과 | 429 |
| INTERNAL_ERROR | 서버 내부 오류 | 500 |

---

*이 문서는 고객관리 시스템 확장 API의 상세 설계 문서입니다. 구현 시 참조하세요.*